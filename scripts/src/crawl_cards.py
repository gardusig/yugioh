#!/usr/bin/env python3
"""
Yu-Gi-Oh! Card Data Crawler

Crawls yugioh.fandom.com to extract card data using card names from CSV
and directly inserts them into the database.

Usage:
    python crawl_cards.py --start 1 --end 10
    python crawl_cards.py --start 1 --end 900 --workers 15

This script:
1. Loads card IDs and names from card_list.csv
2. Fetches card data from yugioh.fandom.com using parallel requests
3. Extracts: name, type, level, ATK, DEF, cost, description, image, attribute, race, rarity
4. Calculates tribute requirements based on level
5. Inserts/updates cards directly in the database
"""

import argparse
import csv
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional, Tuple

import psycopg2
import requests
from bs4 import BeautifulSoup

# Base URLs
WIKI_BASE_URL = "https://yugioh.fandom.com/wiki"
DEFAULT_WORKERS = 10
# Path to card_list.csv in project root/data directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
CARDS_CSV = PROJECT_ROOT / "data" / "card_list.csv"

# Fallback card back image
CARD_BACK_IMAGE = "https://static.wikia.nocookie.net/yugioh/images/d/da/Back-JP.png/revision/latest?cb=20100726082049"

# Database settings (same as db_manager.py)
DB_SETTINGS = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "dbname": os.environ.get("DB_NAME", "yugioh_db"),
    "user": os.environ.get("DB_USER", "yugioh_user"),
    "password": os.environ.get("DB_PASSWORD", "yugioh_password"),
}


def get_db_connection():
    """Get a database connection."""
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        return conn
    except psycopg2.Error as exc:
        print(f"[ERROR] Unable to connect to database: {exc}", file=sys.stderr)
        sys.exit(1)


def load_cards_from_csv(csv_path: Path) -> Dict[int, str]:
    """
    Load card IDs and names from CSV file.

    Args:
        csv_path: Path to the CSV file

    Returns:
        Dictionary mapping card_id to card_name
    """
    cards = {}
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            card_id = int(row["id"])
            card_name = row["name"].strip()
            cards[card_id] = card_name
    return cards


def get_card_url_patterns(card_name: str) -> List[str]:
    """
    Get URL patterns to search for a card by name with multiple fallback variations.

    Handles special cases like:
    - "#1" -> "_1" (e.g., "Winged Dragon, Guardian of the Fortress #1" -> "Winged_Dragon,_Guardian_of_the_Fortress_1")
    - Spaces -> underscores
    - Multiple variations for better matching

    Args:
        card_name: Name of the card

    Returns:
        List of URL patterns to try in order of preference
    """
    pattern_set = set()  # Use set to avoid duplicates
    patterns = []

    # Pattern 1: Replace spaces first, then replace "#X" with "_X" (wiki converts #1 to _1) - most common case
    # "Winged Dragon, Guardian of the Fortress #1" -> "Winged_Dragon,_Guardian_of_the_Fortress_1"
    # The key is: space before # becomes _, then #1 -> _1, but we need to handle the space carefully
    pattern1 = card_name.replace(" ", "_")
    # Replace #X with _X, but collapse any double underscores that might form
    pattern1 = re.sub(r"_#(\d+)", r"_\1", pattern1)  # Handle _#1 -> _1 (space already replaced)
    pattern1 = re.sub(r"#(\d+)", r"_\1", pattern1)  # Handle #1 at start of string
    # Collapse double underscores
    pattern1 = re.sub(r"__+", "_", pattern1)
    if pattern1 not in pattern_set:
        pattern_set.add(pattern1)
        patterns.append(f"{WIKI_BASE_URL}/{pattern1}")

    # Pattern 2: Replace "#X" with "_X" first (no space before #), then spaces
    # "Winged Dragon, Guardian of the Fortress #1" -> "Winged_Dragon,_Guardian_of_the_Fortress_1"
    # This handles the case where there's no space before # (shouldn't happen but be safe)
    pattern2 = re.sub(r"#(\d+)", r"_\1", card_name)  # Replace #1 with _1 first
    pattern2 = pattern2.replace(" ", "_")  # Then replace spaces
    pattern2 = re.sub(r"__+", "_", pattern2)  # Collapse double underscores
    if pattern2 not in pattern_set:
        pattern_set.add(pattern2)
        patterns.append(f"{WIKI_BASE_URL}/{pattern2}")

    # Pattern 3: Replace spaces with underscores, keep special chars as-is (including #)
    # "Winged Dragon, Guardian of the Fortress #1" -> "Winged_Dragon,_Guardian_of_the_Fortress_#1"
    pattern3 = card_name.replace(" ", "_")
    if pattern3 not in pattern_set:
        pattern_set.add(pattern3)
        patterns.append(f"{WIKI_BASE_URL}/{pattern3}")

    # Pattern 4: Remove all special chars except underscores (no commas, no quotes)
    # "Winged Dragon, Guardian of the Fortress #1" -> "Winged_Dragon_Guardian_of_the_Fortress_1"
    pattern4 = card_name.replace(" ", "_")
    pattern4 = pattern4.replace(",", "").replace("'", "").replace('"', "")
    pattern4 = re.sub(r"_#(\d+)", r"_\1", pattern4)  # Handle _#1 -> _1
    pattern4 = re.sub(r"#(\d+)", r"_\1", pattern4)  # Handle #1 at start
    pattern4 = re.sub(r"__+", "_", pattern4)  # Collapse double underscores
    if pattern4 not in pattern_set:
        pattern_set.add(pattern4)
        patterns.append(f"{WIKI_BASE_URL}/{pattern4}")

    # Pattern 5: Remove quotes only, keep commas
    pattern5 = card_name.replace(" ", "_").replace("'", "").replace('"', "")
    pattern5 = re.sub(r"_#(\d+)", r"_\1", pattern5)  # Handle _#1 -> _1
    pattern5 = re.sub(r"#(\d+)", r"_\1", pattern5)  # Handle #1 at start
    pattern5 = re.sub(r"__+", "_", pattern5)  # Collapse double underscores
    if pattern5 not in pattern_set:
        pattern_set.add(pattern5)
        patterns.append(f"{WIKI_BASE_URL}/{pattern5}")

    # Pattern 6: Try with "#" removed entirely (last resort fallback)
    pattern6 = card_name.replace(" ", "_").replace("#", "")
    pattern6 = re.sub(r"__+", "_", pattern6)  # Collapse double underscores
    if pattern6 not in pattern_set:
        pattern_set.add(pattern6)
        patterns.append(f"{WIKI_BASE_URL}/{pattern6}")

    return patterns


def calculate_tributes(level: int, description: Optional[str] = None) -> int:
    """
    Calculate number of tributes needed to summon a monster based on level.

    Yu-Gi-Oh! Tribute Rules:
    - Level 1-4: 0 tributes
    - Level 5-6: 1 tribute
    - Level 7+: 2 tributes
    - Special cases may require 3 tributes (mentioned in description)

    Args:
        level: Monster level
        description: Card description (may contain special tribute requirements)

    Returns:
        Number of tributes required
    """
    if level <= 0:
        return 0
    if level <= 4:
        return 0
    if level <= 6:
        return 1
    if level <= 10:
        # Check for special 3-tribute requirements (e.g., Egyptian Gods)
        if description:
            desc_lower = description.lower()
            if "3 tribute" in desc_lower or "three tribute" in desc_lower:
                return 3
        return 2
    return 3  # Level 11+


def normalize_name(name: str) -> str:
    """
    Normalize card name for comparison by removing punctuation and extra spaces.

    Args:
        name: Card name to normalize

    Returns:
        Normalized name
    """
    # Remove punctuation except spaces
    normalized = re.sub(r"[^\w\s]", " ", name.lower())
    # Collapse multiple spaces
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def validate_card_match(html: str, expected_name: str) -> Tuple[bool, str]:
    """
    Validate that the fetched page matches the expected card name from CSV.

    Args:
        html: HTML content of the card page
        expected_name: Expected card name from CSV (authoritative)

    Returns:
        Tuple of (is_valid: bool, reason: str)
    """
    soup = BeautifulSoup(html, "html.parser")

    # Get page title
    title_elem = (
        soup.find("h1", class_="page-header__title")
        or soup.find("h1", {"id": "firstHeading"})
        or soup.find("h1")
    )
    if not title_elem:
        return False, "No page title found"

    page_name = title_elem.get_text(strip=True)
    if not page_name or len(page_name) < 2:
        return False, "Empty or invalid page title"

    # Normalize both names for comparison
    page_normalized = normalize_name(page_name)
    expected_normalized = normalize_name(expected_name)

    # Exact match after normalization
    if page_normalized == expected_normalized:
        return True, "Exact match"

    # Check if the expected name is contained in the page name (for cases with extra text)
    if expected_normalized in page_normalized or page_normalized in expected_normalized:
        return True, f"Partial match (page: '{page_name}')"

    # Check word overlap - require at least 75% overlap
    expected_words = set(expected_normalized.split())
    page_words = set(page_normalized.split())

    # Remove very short/common words
    common_words = {"the", "of", "a", "an", "and", "or"}
    expected_words = {w for w in expected_words if w not in common_words and len(w) > 2}
    page_words = {w for w in page_words if w not in common_words and len(w) > 2}

    if not expected_words:
        return True, "No significant words to compare"

    # Require at least 75% word overlap for a match
    overlap = len(expected_words.intersection(page_words))
    match_ratio = overlap / len(expected_words) if expected_words else 0

    if match_ratio >= 0.75:
        return True, f"High word overlap ({int(match_ratio * 100)}%, page: '{page_name}')"

    return (
        False,
        f"Low word overlap ({int(match_ratio * 100)}%, page: '{page_name}' vs expected: '{expected_name}')",
    )


def extract_value_from_infobox(soup, data_source: str) -> Optional[str]:
    """
    Extract value from portable-infobox using data-source attribute.

    Args:
        soup: BeautifulSoup object
        data_source: The data-source attribute value to search for

    Returns:
        Extracted value or None
    """
    # Try portable-infobox structure
    infobox = soup.find("aside", class_="portable-infobox")
    if infobox:
        # Find element with matching data-source (could be div, section, or h2)
        elem = infobox.find(attrs={"data-source": data_source})
        if elem:
            # Portable-infobox structure: data-source is on a div/section, value is in pi-data-value
            value_elem = elem.find(class_="pi-data-value")
            if not value_elem:
                # Try finding pi-data-value in children
                value_elem = elem.find(class_=re.compile(r"pi-data-value|pi-data", re.I))
            if not value_elem:
                # Try next sibling with pi-data-value class
                for sibling in elem.next_siblings:
                    if hasattr(sibling, "find"):
                        value_elem = sibling.find(class_="pi-data-value")
                        if value_elem:
                            break
            if not value_elem:
                # Try getting text from the element itself (sometimes value is direct child)
                # Skip the label (pi-data-label)
                for child in elem.find_all(recursive=True):
                    if child.get("class") and "pi-data-label" not in " ".join(
                        child.get("class", [])
                    ):
                        text = child.get_text(strip=True)
                        if text and text != data_source:
                            return text
            if value_elem:
                text = value_elem.get_text(strip=True)
                if text:
                    return text

    # Fallback: try finding by text content in table
    table = soup.find("table", class_="cardtable") or soup.find("aside", class_="portable-infobox")
    if table:
        # Try finding by text match in table cells
        for td in table.find_all(["td", "div"]):
            text = td.get_text(strip=True)
            if data_source.lower() in text.lower() and len(text) < 20:  # Label should be short
                # Get next sibling or parent
                value_elem = td.find_next_sibling() or td.parent
                if value_elem:
                    value_text = value_elem.get_text(strip=True)
                    if value_text and value_text != text and len(value_text) > 0:
                        return value_text

    return None


def extract_numeric_value(text: str) -> Optional[int]:
    """
    Extract numeric value from text, handling various formats.

    Args:
        text: Text containing a number

    Returns:
        Integer value or None
    """
    if not text:
        return None

    # Try to find number (including negative)
    match = re.search(r"(-?\d+)", str(text))
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return None


def parse_card_page(html: str, card_id: int, card_name: str) -> Dict:
    """
    Parse card data from HTML page with improved reliability.

    Always uses the CSV card_name as the authoritative name - never overrides it.

    Args:
        html: HTML content of the card page
        card_id: Card ID
        card_name: Card name from CSV (authoritative, never changed)

    Returns:
        Dictionary with card data
    """
    soup = BeautifulSoup(html, "html.parser")

    card_data = {
        "id": card_id,
        "name": card_name,  # Always use CSV name - never override
        "type": None,
        "level": 0,
        "attack_points": 0,
        "defense_points": 0,
        "cost": 0,
        "description": None,
        "image": None,
        "attribute": None,
        "race": None,
        "rarity": None,
    }

    # Find card data container (try multiple structures)
    infobox = soup.find("aside", class_="portable-infobox")
    card_table = (
        soup.find("table", class_="cardtable")
        or soup.find("table", {"class": re.compile(r"card.*table", re.I)})
        or soup.find("div", class_="cardtable")
    )

    container = infobox or card_table

    if container:
        # Method 1: Try portable-infobox data-source attributes
        if infobox:
            # ATK
            atk_text = extract_value_from_infobox(soup, "atk")
            if not atk_text:
                atk_text = extract_value_from_infobox(soup, "attack")
            if atk_text:
                atk_val = extract_numeric_value(atk_text)
                if atk_val is not None:
                    card_data["attack_points"] = atk_val

            # DEF
            def_text = extract_value_from_infobox(soup, "def")
            if not def_text:
                def_text = extract_value_from_infobox(soup, "defense")
            if def_text:
                def_val = extract_numeric_value(def_text)
                if def_val is not None:
                    card_data["defense_points"] = def_val

            # Level
            level_text = extract_value_from_infobox(soup, "level")
            if not level_text:
                level_text = extract_value_from_infobox(soup, "stars")
            if level_text:
                level_val = extract_numeric_value(level_text)
                if level_val is not None:
                    card_data["level"] = level_val

            # Type
            type_text = extract_value_from_infobox(soup, "type")
            if type_text:
                if "Monster" in type_text:
                    card_data["type"] = "Monster"
                elif "Spell" in type_text:
                    card_data["type"] = "Spell"
                elif "Trap" in type_text:
                    card_data["type"] = "Trap"

            # Attribute
            attr_text = extract_value_from_infobox(soup, "attribute")
            if attr_text:
                card_data["attribute"] = attr_text.strip()

            # Race/Property
            race_text = extract_value_from_infobox(soup, "property")
            if not race_text:
                race_text = extract_value_from_infobox(soup, "species")
            if race_text:
                card_data["race"] = race_text.strip()

        # Method 2: Fallback to table-based extraction (only if infobox didn't work)
        if card_table:
            # Extract ATK (only if not already found)
            if card_data["attack_points"] == 0:
                atk_elem = card_table.find("td", string=re.compile(r"ATK|Attack", re.I))
                if atk_elem:
                    atk_text = atk_elem.find_next_sibling("td")
                    if atk_text:
                        atk_val = extract_numeric_value(atk_text.get_text())
                        if atk_val is not None:
                            card_data["attack_points"] = atk_val
                else:
                    # Try finding by partial text match
                    for td in card_table.find_all("td"):
                        text = td.get_text(strip=True)
                        if re.search(r"ATK|Attack", text, re.I) and "?" not in text:
                            next_td = td.find_next_sibling("td")
                            if next_td:
                                atk_val = extract_numeric_value(next_td.get_text())
                                if atk_val is not None:
                                    card_data["attack_points"] = atk_val
                                    break

            # Extract DEF (only if not already found)
            if card_data["defense_points"] == 0:
                def_elem = card_table.find("td", string=re.compile(r"DEF|Defense", re.I))
                if def_elem:
                    def_text = def_elem.find_next_sibling("td")
                    if def_text:
                        def_val = extract_numeric_value(def_text.get_text())
                        if def_val is not None:
                            card_data["defense_points"] = def_val
                else:
                    # Try finding by partial text match
                    for td in card_table.find_all("td"):
                        text = td.get_text(strip=True)
                        if re.search(r"DEF|Defense", text, re.I) and "?" not in text:
                            next_td = td.find_next_sibling("td")
                            if next_td:
                                def_val = extract_numeric_value(next_td.get_text())
                                if def_val is not None:
                                    card_data["defense_points"] = def_val
                                    break

            # Extract Level/Stars (only if not already found)
            if card_data["level"] == 0:
                level_elem = card_table.find("td", string=re.compile(r"Level|Stars", re.I))
                if level_elem:
                    level_text = level_elem.find_next_sibling("td")
                    if level_text:
                        level_val = extract_numeric_value(level_text.get_text())
                        if level_val is not None:
                            card_data["level"] = level_val
                else:
                    # Try finding by partial text match
                    for td in card_table.find_all("td"):
                        text = td.get_text(strip=True)
                        if re.search(r"Level|Stars", text, re.I):
                            next_td = td.find_next_sibling("td")
                            if next_td:
                                level_val = extract_numeric_value(next_td.get_text())
                                if level_val is not None and 0 < level_val <= 12:
                                    card_data["level"] = level_val
                                    break

            # Extract Type (Card Type)
            if not card_data["type"]:
                type_elem = card_table.find("td", string=re.compile(r"Type|Card Type", re.I))
                if type_elem:
                    type_text = type_elem.find_next_sibling("td")
                    if type_text:
                        card_type = type_text.get_text(strip=True)
                        if "Monster" in card_type:
                            card_data["type"] = "Monster"
                        elif "Spell" in card_type:
                            card_data["type"] = "Spell"
                        elif "Trap" in card_type:
                            card_data["type"] = "Trap"

            # Extract Attribute
            if not card_data["attribute"]:
                attr_elem = card_table.find("td", string=re.compile(r"Attribute", re.I))
                if attr_elem:
                    attr_text = attr_elem.find_next_sibling("td")
                    if attr_text:
                        card_data["attribute"] = attr_text.get_text(strip=True)

            # Extract Race/Monster Type
            if not card_data["race"]:
                race_elem = card_table.find("td", string=re.compile(r"Property|Species", re.I))
                if not race_elem:
                    # Sometimes race is in the Type field
                    type_elem = card_table.find("td", string=re.compile(r"Type|Card Type", re.I))
                    if type_elem:
                        type_text = type_elem.find_next_sibling("td")
                        if type_text:
                            type_value = type_text.get_text(strip=True)
                            # Format: "Dragon / Normal" or "Dragon / Effect"
                            if "/" in type_value:
                                parts = type_value.split("/")
                                card_data["race"] = parts[0].strip()
                else:
                    race_text = race_elem.find_next_sibling("td")
                    if race_text:
                        card_data["race"] = race_text.get_text(strip=True)

        # Extract image (try multiple methods)
        img_elem = None
        if infobox:
            img_elem = infobox.find("img")
        if not img_elem and card_table:
            img_elem = card_table.find("img")
        if not img_elem:
            img_elem = soup.find("img", class_=re.compile(r"card.*image", re.I))
        if not img_elem:
            img_link = soup.find("a", class_="image")
            if img_link:
                img_elem = img_link.find("img")

        if img_elem:
            img_src = img_elem.get("src") or img_elem.get("data-src") or img_elem.get("data-image")
            if img_src:
                # Convert to full URL if relative
                if img_src.startswith("//"):
                    img_src = f"https:{img_src}"
                elif img_src.startswith("/"):
                    img_src = f"https://yugioh.fandom.com{img_src}"
                # Remove size parameters from wiki images but keep the revision
                if "/revision/" in img_src:
                    # Keep the revision part for proper image loading
                    pass
                card_data["image"] = img_src

        # Extract description/lore/card text
        if infobox:
            lore_text = extract_value_from_infobox(soup, "lore")
            if not lore_text:
                lore_text = extract_value_from_infobox(soup, "description")
            if not lore_text:
                lore_text = extract_value_from_infobox(soup, "effect")
            if lore_text:
                card_data["description"] = lore_text

        if not card_data["description"] and card_table:
            lore_elem = card_table.find(
                "td", string=re.compile(r"Lore|Description|Card Text|Effect", re.I)
            )
            if lore_elem:
                lore_text = lore_elem.find_next_sibling("td")
                if lore_text:
                    card_data["description"] = lore_text.get_text(strip=True)

    # If no description found, try to find it elsewhere
    if not card_data["description"]:
        lore_div = soup.find("div", class_=re.compile(r"lore|description|card.*text", re.I))
        if lore_div:
            card_data["description"] = lore_div.get_text(strip=True)

    # Calculate cost (in Yu-Gi-Oh! The Sacred Cards, cost = level for monsters)
    if card_data["type"] == "Monster":
        card_data["cost"] = card_data["level"] if card_data["level"] > 0 else 0
    else:
        # Spells and Traps typically have cost 0, but some might have a cost
        card_data["cost"] = 0

    # Set default values if missing
    if not card_data["type"]:
        card_data["type"] = "Monster"

    # Set fallback image if not found
    if not card_data["image"]:
        # Try YGOPRODeck first
        card_data["image"] = f"https://images.ygoprodeck.com/images/cards/{card_id}.jpg"
        # Note: Frontend should use CARD_BACK_IMAGE if image fails to load

    return card_data


def fetch_card_data(card_id: int, card_name: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Fetch card data from wiki by card name.

    Uses CSV card_name as the authoritative reference. Validates that the found
    page matches the expected card name.

    Search strategy:
    1. Try multiple URL pattern variations (wiki fandom direct URLs)
    2. Fallback to wiki search API if direct URLs fail
    3. Validate all matches against CSV name

    Args:
        card_id: Card ID
        card_name: Card name from CSV (authoritative)

    Returns:
        Tuple of (card_data dict or None, error_reason string or None)
    """
    # Attempt 1: Try multiple direct URL patterns (wiki fandom)
    patterns = get_card_url_patterns(card_name)
    tried_patterns = []
    validation_failures = []

    for url in patterns:
        tried_patterns.append(url.split("/")[-1])  # Store just the page name for logging
        try:
            response = requests.get(
                url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            if response.status_code == 200:
                # Validate we got the right card
                is_valid, validation_reason = validate_card_match(response.text, card_name)
                if is_valid:
                    card_data = parse_card_page(response.text, card_id, card_name)
                    if card_data:
                        return card_data, None
                else:
                    # Page found but didn't match - note the reason
                    validation_failures.append(validation_reason)
                    continue
            elif response.status_code == 404:
                continue  # URL pattern didn't match, try next
        except requests.exceptions.Timeout:
            continue  # Timeout on this pattern, try next
        except requests.exceptions.RequestException:
            continue  # Network error, try next pattern
        except Exception:
            continue

    # Attempt 2: If direct patterns fail, try wiki search API
    try:
        search_url = f"{WIKI_BASE_URL}/Special:Search?search={requests.utils.quote(card_name)}"
        response = requests.get(search_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("a", class_="unified-search__result__title")

            if not results:
                # No search results found
                tried_urls = ", ".join(tried_patterns[:3])  # Show first 3 for brevity
                error_msg = f"Not found: tried {len(tried_patterns)} URL pattern(s) (e.g., {tried_urls}) and search returned no results"
                if validation_failures:
                    error_msg += f" (validation failed: {validation_failures[0]})"
                return None, error_msg

            # Try each result and validate it matches our expected card name
            for result in results[:5]:  # Limit to first 5 results
                result_title = result.get_text(strip=True)

                # Quick check before fetching the full page
                result_normalized = normalize_name(result_title)
                expected_normalized = normalize_name(card_name)

                # Skip if clearly different
                if result_normalized != expected_normalized:
                    # Check word overlap
                    result_words = set(result_normalized.split())
                    expected_words = set(expected_normalized.split())
                    common_words = {"the", "of", "a", "an", "and", "or"}
                    result_words = {w for w in result_words if w not in common_words and len(w) > 2}
                    expected_words = {
                        w for w in expected_words if w not in common_words and len(w) > 2
                    }

                    if expected_words:
                        overlap = len(expected_words.intersection(result_words))
                        match_ratio = overlap / len(expected_words)
                        if match_ratio < 0.75:
                            continue  # Skip this result

                # Found a potential match, fetch and validate
                card_url = result.get("href")
                if card_url.startswith("/"):
                    card_url = f"https://yugioh.fandom.com{card_url}"

                try:
                    card_response = requests.get(
                        card_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    if card_response.status_code == 200:
                        is_valid, validation_reason = validate_card_match(
                            card_response.text, card_name
                        )
                        if is_valid:
                            card_data = parse_card_page(card_response.text, card_id, card_name)
                            if card_data:
                                return card_data, None
                        else:
                            validation_failures.append(
                                f"search result '{result_title}': {validation_reason}"
                            )
                except Exception:
                    continue

            # All search results tried but none matched
            tried_urls = ", ".join(tried_patterns[:3])
            error_msg = f"Not found: tried {len(tried_patterns)} URL pattern(s) (e.g., {tried_urls}) and {len(results)} search result(s), but none matched"
            if validation_failures:
                error_msg += f" (last validation: {validation_failures[-1]})"
            return None, error_msg
    except requests.exceptions.RequestException:
        # Search API failed
        tried_urls = ", ".join(tried_patterns[:3])
        return (
            None,
            f"Network error: tried {len(tried_patterns)} URL pattern(s) (e.g., {tried_urls}) and search API unavailable",
        )
    except Exception as exc:
        tried_urls = ", ".join(tried_patterns[:3])
        return (
            None,
            f"Search error: tried {len(tried_patterns)} URL pattern(s) (e.g., {tried_urls}), search failed ({type(exc).__name__})",
        )

    # All attempts exhausted
    tried_urls = ", ".join(tried_patterns[:3])
    error_msg = f"Not found: tried {len(tried_patterns)} URL pattern(s) (e.g., {tried_urls})"
    if validation_failures:
        error_msg += f" (validation failed: {validation_failures[0]})"
    return None, error_msg


def save_card_to_db(conn, card_data: Dict) -> bool:
    """
    Save or update card in the database.

    Args:
        conn: Database connection
        card_data: Dictionary with card data

    Returns:
        True if successful, False otherwise
    """
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cards (
                    id, name, description, image, type, attribute, race, level,
                    attack_points, defense_points, cost, rarity
                )
                VALUES (
                    %(id)s, %(name)s, %(description)s, %(image)s, %(type)s, %(attribute)s,
                    %(race)s, %(level)s, %(attack_points)s, %(defense_points)s, %(cost)s, %(rarity)s
                )
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    image = EXCLUDED.image,
                    type = EXCLUDED.type,
                    attribute = EXCLUDED.attribute,
                    race = EXCLUDED.race,
                    level = EXCLUDED.level,
                    attack_points = EXCLUDED.attack_points,
                    defense_points = EXCLUDED.defense_points,
                    cost = EXCLUDED.cost,
                    rarity = EXCLUDED.rarity,
                    updated_at = NOW();
                """,
                card_data,
            )
        conn.commit()
        return True
    except psycopg2.Error as exc:
        conn.rollback()
        print(f"[ERROR] Failed to save card {card_data['id']}: {exc}", file=sys.stderr)
        return False


def fetch_and_save_card(card_id: int, card_name: str) -> Tuple[Dict, bool]:
    """
    Fetch a single card and save it to database. Used for parallel execution.

    Skips cards that are not found or don't match the CSV name, with logging.

    Args:
        card_id: Card ID
        card_name: Card name from CSV (authoritative)

    Returns:
        Tuple of (result dict, success bool)
    """
    conn = get_db_connection()
    try:
        # Fetch card data - returns (card_data, error_reason)
        card_data, error_reason = fetch_card_data(card_id, card_name)

        if not card_data:
            # Card not found or doesn't match - skip it and log the reason
            reason = error_reason or "Unknown error"
            preview = f"Card #{card_id:03d}: '{card_name}' - SKIPPED ({reason})"
            return {
                "card_id": card_id,
                "data": None,
                "success": False,
                "preview": preview,
                "skip_reason": reason,
            }, False

        # Calculate tributes
        tributes = calculate_tributes(card_data.get("level", 0), card_data.get("description"))

        # Save to database
        success = save_card_to_db(conn, card_data)

        # Build preview string
        preview = f"Card #{card_id:03d}: {card_data['name']}"
        if card_data.get("type") == "Monster":
            preview += f" ({card_data.get('type', 'Monster')})"
            if card_data.get("level", 0) > 0:
                preview += f" [Lv.{card_data['level']}]"
            if card_data.get("attribute"):
                preview += f" [{card_data['attribute']}]"
            if card_data.get("attack_points", 0) > 0 or card_data.get("defense_points", 0) > 0:
                preview += f" ATK:{card_data.get('attack_points', 0)}/DEF:{card_data.get('defense_points', 0)}"
            if tributes > 0:
                preview += f" (Tributes: {tributes})"
        else:
            preview += f" ({card_data.get('type', 'Card')})"

        return {
            "card_id": card_id,
            "data": card_data,
            "success": success,
            "preview": preview,
        }, success

    except Exception as exc:
        preview = f"Card #{card_id:03d}: '{card_name}' - ERROR ({type(exc).__name__}: {exc})"
        return {
            "card_id": card_id,
            "data": None,
            "success": False,
            "preview": preview,
            "skip_reason": f"Exception: {exc}",
        }, False
    finally:
        conn.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Crawl Yu-Gi-Oh! card data from yugioh.fandom.com and save to database."
    )
    parser.add_argument("--start", type=int, default=1, help="Starting card ID (default: 1)")
    parser.add_argument("--end", type=int, default=10, help="Ending card ID (default: 10)")
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Number of parallel workers (default: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=str(CARDS_CSV),
        help=f"Path to CSV file with card names (default: {CARDS_CSV})",
    )
    args = parser.parse_args()

    # Load cards from CSV
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[ERROR] CSV file not found: {csv_path}", file=sys.stderr)
        print("Please create a CSV file with columns: id,name", file=sys.stderr)
        sys.exit(1)

    all_cards = load_cards_from_csv(csv_path)
    if not all_cards:
        print(f"[ERROR] No cards found in CSV file: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Filter cards by range
    start_id = max(min(all_cards.keys()), args.start)
    end_id = min(max(all_cards.keys()), args.end)
    if start_id > end_id:
        start_id, end_id = end_id, start_id

    cards_to_fetch = {
        card_id: card_name
        for card_id, card_name in all_cards.items()
        if start_id <= card_id <= end_id
    }

    if not cards_to_fetch:
        print(f"[ERROR] No cards found in range [{start_id}, {end_id}]", file=sys.stderr)
        sys.exit(1)

    workers = max(1, min(50, args.workers))

    # Check database connection
    print("Checking database connection...", file=sys.stderr)
    test_conn = get_db_connection()
    test_conn.close()
    print(
        f"[OK] Connected to database: {DB_SETTINGS['host']}:{DB_SETTINGS['port']}/{DB_SETTINGS['dbname']}",
        file=sys.stderr,
    )

    print("Starting Yu-Gi-Oh! Card Crawler...", file=sys.stderr)
    print(f"Loading cards from: {csv_path}", file=sys.stderr)
    print(f"This will crawl cards {start_id}-{end_id} from yugioh.fandom.com", file=sys.stderr)
    print(f"Using {workers} parallel workers", file=sys.stderr)
    print("This may take a while. Please be patient...", file=sys.stderr)
    print("", file=sys.stderr)

    successful = 0
    skipped = 0
    progress_lock = Lock()
    completed = 0

    # Use ThreadPoolExecutor for parallel fetching and saving
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        future_to_card_id = {
            executor.submit(fetch_and_save_card, card_id, card_name): card_id
            for card_id, card_name in cards_to_fetch.items()
        }

        # Process completed tasks as they finish
        for future in as_completed(future_to_card_id):
            result, success = future.result()
            card_id = result["card_id"]
            preview = result.get("preview", f"Card #{card_id:03d}")

            with progress_lock:
                completed += 1
                if success:
                    successful += 1
                    print(f"[{completed}/{len(cards_to_fetch)}] ✓ {preview}", file=sys.stderr)
                else:
                    skipped += 1
                    # Log skipped cards with their reason
                    skip_reason = result.get("skip_reason", "Unknown reason")
                    print(
                        f"[{completed}/{len(cards_to_fetch)}] ⊘ {preview} ({skip_reason})",
                        file=sys.stderr,
                    )

                # Progress update every 25 cards or at completion
                if completed % 25 == 0 or completed == len(cards_to_fetch):
                    print(
                        f"Progress: {completed}/{len(cards_to_fetch)} (Success: {successful}, Skipped: {skipped})",
                        file=sys.stderr,
                    )

    print("", file=sys.stderr)
    print(f"Crawling complete! Success: {successful}, Skipped: {skipped}", file=sys.stderr)
    if skipped > 0:
        print(
            f"Note: {skipped} card(s) were skipped because they were not found or didn't match the CSV name.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
