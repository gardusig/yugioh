#!/usr/bin/env python3
"""
Generate data/cards.csv from data/card_list.csv.

By default uses built-in data for known cards and defaults for others.
Use --fetch-images to fetch images and full data from YGOPRODECK API (requires network).

Run from project root: python3 scripts/src/generate_cards_csv.py
"""

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
CARD_LIST = PROJECT_ROOT / "data" / "card_list.csv"
CARDS_OUT = PROJECT_ROOT / "data" / "cards.csv"

API_BASE = "https://db.ygoprodeck.com/api/v7/cardinfo.php"
RATE_LIMIT_DELAY = 0.06  # ~16 req/sec to stay under 20/sec

# Full data for known cards (keyed by exact name - fixes wrong image for cards at wrong IDs)
# Image URLs use YGOPRODECK passcode format
CARD_DATA_BY_NAME = {
    "Blue-Eyes White Dragon": {"type": "Normal Monster", "attribute": "LIGHT", "race": "Dragon", "level": 8,
        "attack_points": 3000, "defense_points": 2500, "cost": 8, "rarity": "Ultra Rare",
        "description": "This legendary dragon is a powerful engine of destruction.", "image": "https://images.ygoprodeck.com/images/cards/89631139.jpg"},
    "Mystical Elf": {"type": "Normal Monster", "attribute": "LIGHT", "race": "Spellcaster", "level": 4,
        "attack_points": 800, "defense_points": 2000, "cost": 4, "rarity": "Super Rare",
        "description": "A delicate elf that lacks offense, but has a terrific defense backed by mystical power.", "image": "https://images.ygoprodeck.com/images/cards/15025844.jpg"},
    "Dark Magician": {"type": "Normal Monster", "attribute": "DARK", "race": "Spellcaster", "level": 7,
        "attack_points": 2500, "defense_points": 2100, "cost": 7, "rarity": "Ultra Rare",
        "description": "The ultimate wizard in terms of attack and defense.", "image": "https://images.ygoprodeck.com/images/cards/46986414.jpg"},
    "Exodia the Forbidden One": {"type": "Effect Monster", "attribute": "DARK", "race": "Spellcaster", "level": 3,
        "attack_points": 1000, "defense_points": 1000, "cost": 3, "rarity": "Ultra Rare",
        "description": "If you have all five Exodia pieces in your hand, you win the Duel.", "image": "https://images.ygoprodeck.com/images/cards/33396948.jpg"},
    "Obelisk the Tormentor": {"type": "Effect Monster", "attribute": "DIVINE", "race": "Divine-Beast", "level": 10,
        "attack_points": 4000, "defense_points": 4000, "cost": 10, "rarity": "Secret Rare",
        "description": "One of the three Egyptian God cards.", "image": "https://images.ygoprodeck.com/images/cards/10000000.jpg"},
    "Slifer the Sky Dragon": {"type": "Effect Monster", "attribute": "DIVINE", "race": "Divine-Beast", "level": 10,
        "attack_points": 0, "defense_points": 0, "cost": 10, "rarity": "Secret Rare",
        "description": "One of the three Egyptian God cards.", "image": "https://images.ygoprodeck.com/images/cards/10000020.jpg"},
    "The Winged Dragon of Ra": {"type": "Effect Monster", "attribute": "DIVINE", "race": "Divine-Beast", "level": 10,
        "attack_points": 0, "defense_points": 0, "cost": 10, "rarity": "Secret Rare",
        "description": "One of the three Egyptian God cards.", "image": "https://images.ygoprodeck.com/images/cards/10000010.jpg"},
    "Red-Eyes B. Dragon": {"type": "Normal Monster", "attribute": "DARK", "race": "Dragon", "level": 7,
        "attack_points": 2400, "defense_points": 2000, "cost": 7, "rarity": "Ultra Rare",
        "description": "A ferocious dragon with a deadly attack.", "image": "https://images.ygoprodeck.com/images/cards/74677422.jpg"},
    "Red-Eyes Black Dragon": {"type": "Normal Monster", "attribute": "DARK", "race": "Dragon", "level": 7,
        "attack_points": 2400, "defense_points": 2000, "cost": 7, "rarity": "Ultra Rare",
        "description": "A ferocious dragon with a deadly attack.", "image": "https://images.ygoprodeck.com/images/cards/74677422.jpg"},
    "Summoned Skull": {"type": "Normal Monster", "attribute": "DARK", "race": "Fiend", "level": 6,
        "attack_points": 2500, "defense_points": 1200, "cost": 6, "rarity": "Super Rare",
        "description": "A fiend with dark powers for confusing the enemy.", "image": "https://images.ygoprodeck.com/images/cards/70781052.jpg"},
    "Dark Magician Girl": {"type": "Effect Monster", "attribute": "DARK", "race": "Spellcaster", "level": 6,
        "attack_points": 2000, "defense_points": 1700, "cost": 6, "rarity": "Ultra Rare",
        "description": "Gains 300 ATK for every Dark Magician in the GY.", "image": "https://images.ygoprodeck.com/images/cards/38033121.jpg"},
    "Kuriboh": {"type": "Effect Monster", "attribute": "DARK", "race": "Fiend", "level": 1,
        "attack_points": 300, "defense_points": 200, "cost": 1, "rarity": "Common",
        "description": "Discard this card to take no battle damage from one attack.", "image": "https://images.ygoprodeck.com/images/cards/40640057.jpg"},
    "Right Leg of the Forbidden One": {"type": "Normal Monster", "attribute": "DARK", "race": "Spellcaster", "level": 1,
        "attack_points": 200, "defense_points": 300, "cost": 1, "rarity": "Rare",
        "description": "A forbidden right leg sealed by magic.", "image": "https://images.ygoprodeck.com/images/cards/8124921.jpg"},
    "Left Leg of the Forbidden One": {"type": "Normal Monster", "attribute": "DARK", "race": "Spellcaster", "level": 1,
        "attack_points": 200, "defense_points": 300, "cost": 1, "rarity": "Rare",
        "description": "A forbidden left leg sealed by magic.", "image": "https://images.ygoprodeck.com/images/cards/44519536.jpg"},
    "Right Arm of the Forbidden One": {"type": "Normal Monster", "attribute": "DARK", "race": "Spellcaster", "level": 1,
        "attack_points": 200, "defense_points": 300, "cost": 1, "rarity": "Rare",
        "description": "A forbidden right arm sealed by magic.", "image": "https://images.ygoprodeck.com/images/cards/70903634.jpg"},
    "Left Arm of the Forbidden One": {"type": "Normal Monster", "attribute": "DARK", "race": "Spellcaster", "level": 1,
        "attack_points": 200, "defense_points": 300, "cost": 1, "rarity": "Rare",
        "description": "A forbidden left arm sealed by magic.", "image": "https://images.ygoprodeck.com/images/cards/7902349.jpg"},
    "Mushroom Man": {"type": "Normal Monster", "attribute": "EARTH", "race": "Plant", "level": 2,
        "attack_points": 800, "defense_points": 600, "cost": 2, "rarity": "Common",
        "description": "Found in humid regions, this creature attacks enemies with a lethal rain of poison spores.", "image": "https://images.ygoprodeck.com/images/cards/14181608.jpg"},
    "Winged Dragon Guardian of the Fortress #1": {"type": "Normal Monster", "attribute": "LIGHT", "race": "Spellcaster", "level": 6,
        "attack_points": 1900, "defense_points": 1700, "cost": 6, "rarity": "Common",
        "description": "A dragon commonly found guarding mountain fortresses. Its signature attack is a sweeping dive from out of the blue.", "image": "https://images.ygoprodeck.com/images/cards/87796900.jpg"},
    "Winged Dragon Guardian of the Fortress #2": {"type": "Normal Monster", "attribute": "DARK", "race": "Dragon", "level": 3,
        "attack_points": 1400, "defense_points": 1000, "cost": 3, "rarity": "Common",
        "description": "This monster's wings are capable of generating tornadoes.", "image": "https://images.ygoprodeck.com/images/cards/57405307.jpg"},
}

# Passcodes for cards that fail API lookup (image-only override when not in CARD_DATA_BY_NAME)
CARD_IMAGE_PASSCODES = {}


def default_card(card_id: int, name: str) -> dict:
    """Generate default stats. Uses CARD_DATA_BY_NAME when available."""
    known = CARD_DATA_BY_NAME.get(name)
    if known:
        return {"id": card_id, "name": name, **known}
    level = 3 + (card_id % 4)
    base_atk = 1200 + (card_id % 10) * 100
    base_def = 1000 + (card_id % 8) * 100
    image = ""
    if name in CARD_IMAGE_PASSCODES:
        image = f"https://images.ygoprodeck.com/images/cards/{CARD_IMAGE_PASSCODES[name]}.jpg"
    return {
        "id": card_id,
        "name": name,
        "type": "Normal Monster",
        "attribute": ["DARK", "LIGHT", "EARTH", "WATER", "FIRE", "WIND"][card_id % 6],
        "race": ["Dragon", "Spellcaster", "Warrior", "Fiend", "Beast", "Machine"][card_id % 6],
        "level": level,
        "attack_points": base_atk,
        "defense_points": base_def,
        "cost": level,
        "rarity": "Common",
        "description": "",
        "image": image,
    }


def name_variations_for_api(name: str) -> list[str]:
    """Return name variations to try when API lookup fails (card_list vs YGOPRODECK naming)."""
    variations = [name]
    # YGOPRODECK uses "Winged Dragon, Guardian of the Fortress #1" (comma after Dragon)
    if "Winged Dragon Guardian of the Fortress #1" in name:
        variations.append("Winged Dragon, Guardian of the Fortress #1")
    if "Winged Dragon Guardian of the Fortress #2" in name:
        variations.append("Winged Dragon, Guardian of the Fortress #2")
    # Generic: try without # for numbered cards
    if " #" in name:
        variations.append(name.replace(" #", " "))
    return variations


def fetch_card_from_api(name: str) -> dict | None:
    """Fetch card data from YGOPRODECK API. Returns dict or None if not found."""
    for try_name in name_variations_for_api(name):
        for param in ["name", "fname"]:
            url = f"{API_BASE}?{param}={urllib.parse.quote(try_name)}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "YuGiOh-DeckEditor/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
            except (urllib.error.HTTPError, urllib.error.URLError, json.JSONDecodeError, OSError):
                continue
            if not data.get("data"):
                continue
            card = data["data"][0]
            imgs = card.get("card_images", [])
            img_url = imgs[0]["image_url"] if imgs else ""
            return {
                "type": card.get("type", "Normal Monster"),
                "attribute": card.get("attribute", ""),
                "race": card.get("race", ""),
                "level": int(card.get("level", 0)),
                "attack_points": int(card.get("atk", 0)),
                "defense_points": int(card.get("def", 0)),
                "cost": int(card.get("level", 0)),
                "rarity": "Common",
                "description": card.get("desc", ""),
                "image": img_url,
            }
    return None


def fill_missing_images(cards: list[dict]) -> int:
    """Fetch images from API for cards with empty image. Returns count of filled."""
    filled = 0
    for i, card in enumerate(cards):
        if card.get("image", "").strip():
            continue
        name = card.get("name", "")
        api_data = fetch_card_from_api(name)
        if api_data and api_data.get("image"):
            card["image"] = api_data["image"]
            filled += 1
            print(f"  Fetched image for: {name}", file=sys.stderr)
        time.sleep(RATE_LIMIT_DELAY)
    return filled


def verify_image_url(url: str) -> bool:
    """Check if image URL returns 200. Returns True if valid."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "YuGiOh-DeckEditor/1.0")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 400
    except Exception:
        return False


def verify_and_fix_images(cards: list[dict]) -> tuple[int, int]:
    """Verify each card's image URL. Re-fetch from API if invalid. Returns (verified_ok, re_fetched)."""
    verified_ok = 0
    re_fetched = 0
    for card in cards:
        url = (card.get("image") or "").strip()
        if not url:
            # Missing - try to fetch
            api_data = fetch_card_from_api(card.get("name", ""))
            if api_data and api_data.get("image"):
                card["image"] = api_data["image"]
                re_fetched += 1
                print(f"  Fetched missing: {card['name']}", file=sys.stderr)
            time.sleep(RATE_LIMIT_DELAY)
            continue
        if verify_image_url(url):
            verified_ok += 1
        else:
            # Invalid URL - try to re-fetch
            api_data = fetch_card_from_api(card.get("name", ""))
            if api_data and api_data.get("image"):
                card["image"] = api_data["image"]
                re_fetched += 1
                print(f"  Re-fetched invalid URL: {card['name']}", file=sys.stderr)
            time.sleep(RATE_LIMIT_DELAY)
    return verified_ok, re_fetched


def main():
    parser = argparse.ArgumentParser(description="Generate cards.csv from card_list.csv")
    parser.add_argument("--fetch-images", action="store_true",
        help="Fetch images and full data from YGOPRODECK API (requires network, ~1 min for 900 cards)")
    parser.add_argument("--fill-missing-images", action="store_true",
        help="Read existing cards.csv and fetch images only for cards with empty image")
    parser.add_argument("--verify-images", action="store_true",
        help="Verify each image URL and re-fetch from API if missing or invalid")
    args = parser.parse_args()

    if args.verify_images:
        if not CARDS_OUT.exists():
            print(f"[ERROR] {CARDS_OUT} not found.", file=sys.stderr)
            sys.exit(1)
        with open(CARDS_OUT, encoding="utf-8") as f:
            cards = list(csv.DictReader(f))
        for c in cards:
            c["id"] = int(c["id"])
            c["level"] = int(c.get("level", 0))
            c["attack_points"] = int(c.get("attack_points", 0))
            c["defense_points"] = int(c.get("defense_points", 0))
            c["cost"] = int(c.get("cost", 0))
        print("[INFO] Verifying image URLs and re-fetching invalid/missing...")
        verified, refetched = verify_and_fix_images(cards)
        with open(CARDS_OUT, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "id", "name", "type", "attribute", "race", "level", "attack_points", "defense_points",
                "cost", "rarity", "description", "image"
            ], extrasaction="ignore")
            writer.writeheader()
            writer.writerows(cards)
        with_img = sum(1 for c in cards if c.get("image", "").strip())
        print(f"[OK] Verified {verified} URLs, re-fetched {refetched}. Total with image: {with_img}/{len(cards)}")
        return

    if args.fill_missing_images:
        if not CARDS_OUT.exists():
            print(f"[ERROR] {CARDS_OUT} not found. Run without --fill-missing-images first.", file=sys.stderr)
            sys.exit(1)
        with open(CARDS_OUT, encoding="utf-8") as f:
            cards = list(csv.DictReader(f))
        for c in cards:
            c["id"] = int(c["id"])
            c["level"] = int(c.get("level", 0))
            c["attack_points"] = int(c.get("attack_points", 0))
            c["defense_points"] = int(c.get("defense_points", 0))
            c["cost"] = int(c.get("cost", 0))
        print(f"[INFO] Filling missing images for {len([c for c in cards if not c.get('image', '').strip()])} cards...")
        filled = fill_missing_images(cards)
        with open(CARDS_OUT, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "id", "name", "type", "attribute", "race", "level", "attack_points", "defense_points",
                "cost", "rarity", "description", "image"
            ], extrasaction="ignore")
            writer.writeheader()
            writer.writerows(cards)
        print(f"[OK] Filled {filled} images → {CARDS_OUT}")
        return

    if not CARD_LIST.exists():
        print(f"[ERROR] {CARD_LIST} not found. Run from project root.", file=sys.stderr)
        sys.exit(1)

    cards = []
    with open(CARD_LIST, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for i, row in enumerate(rows):
        try:
            card_id = int(row["id"])
        except (ValueError, KeyError):
            continue
        name = row.get("name", "").strip()
        if not name or len(name) < 2:
            continue

        if args.fetch_images:
            api_data = fetch_card_from_api(name)
            if api_data:
                cards.append({"id": card_id, "name": name, **api_data})
            else:
                cards.append(default_card(card_id, name))
            time.sleep(RATE_LIMIT_DELAY)
        else:
            cards.append(default_card(card_id, name))

    CARDS_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(CARDS_OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "name", "type", "attribute", "race", "level", "attack_points", "defense_points",
            "cost", "rarity", "description", "image"
        ], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(cards)

    with_img = sum(1 for c in cards if c.get("image"))
    print(f"[OK] Generated {len(cards)} cards → {CARDS_OUT} ({with_img} with images)")


if __name__ == "__main__":
    main()
