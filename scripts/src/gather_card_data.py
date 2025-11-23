#!/usr/bin/env python3
"""
Yu-Gi-Oh! Card Data Gatherer

Gathers all card data from yugioh.fandom.com using card names from card_list.csv
and saves the complete card data to a CSV file for database insertion.

Usage:
    python gather_card_data.py
    python gather_card_data.py --start 1 --end 100
    python gather_card_data.py --workers 15

This script:
1. Loads card IDs and names from card_list.csv
2. Fetches card data from yugioh.fandom.com using parallel requests
3. Extracts: name, type, level, ATK, DEF, cost, description, image, attribute, race, rarity
4. Saves all card data to data/cards_data.csv
"""

import argparse
import csv
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Dict, List, Optional

import requests

# Import functions from crawl_cards module
from crawl_cards import (
    DEFAULT_WORKERS,
    fetch_card_data,
    load_cards_from_csv,
    calculate_tributes,
)

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
# Card list is in project root/data, output CSV also goes there
CARD_LIST_CSV = PROJECT_ROOT / "data" / "card_list.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "cards_data.csv"

# CSV field names matching database schema
CSV_FIELDS = [
    "id",
    "name",
    "description",
    "image",
    "type",
    "attribute",
    "race",
    "level",
    "attack_points",
    "defense_points",
    "cost",
    "rarity",
]


def save_card_to_csv(card_data: Dict, csv_path: Path, csv_lock: Lock, write_header: bool = False):
    """
    Save a single card to CSV file (thread-safe).

    Args:
        card_data: Dictionary with card data
        csv_path: Path to CSV file
        csv_lock: Lock for thread-safe file writing
        write_header: Whether to write CSV header
    """
    with csv_lock:
        file_exists = csv_path.exists()
        mode = "a" if file_exists and not write_header else "w"

        with open(csv_path, mode=mode, encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
            if write_header or not file_exists:
                writer.writeheader()
            writer.writerow(card_data)


def fetch_and_save_card(
    card_id: int, card_name: str, csv_path: Path, csv_lock: Lock, header_written: List[bool]
) -> tuple[Dict, bool]:
    """
    Fetch a single card and save it to CSV. Used for parallel execution.

    Args:
        card_id: Card ID
        card_name: Card name from CSV (authoritative)
        csv_path: Path to output CSV file
        csv_lock: Lock for thread-safe file writing
        header_written: List with single boolean to track if header was written

    Returns:
        Tuple of (result dict, success bool)
    """
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

        # Ensure all required fields are present with defaults
        card_data.setdefault("description", "")
        card_data.setdefault("image", "")
        card_data.setdefault("type", "Monster")
        card_data.setdefault("attribute", "")
        card_data.setdefault("race", "")
        card_data.setdefault("level", 0)
        card_data.setdefault("attack_points", 0)
        card_data.setdefault("defense_points", 0)
        card_data.setdefault("cost", 0)
        card_data.setdefault("rarity", "")

        # Save to CSV (thread-safe write with lock)
        # Only first successful card writes header
        write_header = not header_written[0]
        save_card_to_csv(card_data, csv_path, csv_lock, write_header=write_header)
        if write_header:
            header_written[0] = True

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
        else:
            preview += f" ({card_data.get('type', 'Card')})"

        return {
            "card_id": card_id,
            "data": card_data,
            "success": True,
            "preview": preview,
        }, True

    except Exception as exc:
        preview = f"Card #{card_id:03d}: '{card_name}' - ERROR ({type(exc).__name__}: {exc})"
        return {
            "card_id": card_id,
            "data": None,
            "success": False,
            "preview": preview,
            "skip_reason": f"Exception: {exc}",
        }, False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Gather Yu-Gi-Oh! card data from yugioh.fandom.com and save to CSV."
    )
    parser.add_argument("--start", type=int, default=None, help="Starting card ID (default: all)")
    parser.add_argument("--end", type=int, default=None, help="Ending card ID (default: all)")
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help=f"Number of parallel workers (default: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(OUTPUT_CSV),
        help=f"Path to output CSV file (default: {OUTPUT_CSV})",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=str(CARD_LIST_CSV),
        help=f"Path to input card list CSV (default: {CARD_LIST_CSV})",
    )
    args = parser.parse_args()

    # Load cards from CSV
    csv_path = Path(args.input)
    if not csv_path.exists():
        print(f"[ERROR] Card list CSV file not found: {csv_path}", file=sys.stderr)
        print("Please ensure card_list.csv exists in data/ directory at project root", file=sys.stderr)
        sys.exit(1)

    all_cards = load_cards_from_csv(csv_path)
    if not all_cards:
        print(f"[ERROR] No cards found in CSV file: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Filter cards by range if specified
    if args.start is not None or args.end is not None:
        start_id = args.start if args.start is not None else min(all_cards.keys())
        end_id = args.end if args.end is not None else max(all_cards.keys())
        if start_id > end_id:
            start_id, end_id = end_id, start_id

        cards_to_fetch = {
            card_id: card_name
            for card_id, card_name in all_cards.items()
            if start_id <= card_id <= end_id
        }
    else:
        cards_to_fetch = all_cards

    if not cards_to_fetch:
        print(f"[ERROR] No cards found in specified range", file=sys.stderr)
        sys.exit(1)

    workers = max(1, min(50, args.workers))
    output_path = Path(args.output)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing output file if it exists
    if output_path.exists():
        print(f"[INFO] Removing existing output file: {output_path}", file=sys.stderr)
        output_path.unlink()

    print("Starting Yu-Gi-Oh! Card Data Gatherer...", file=sys.stderr)
    print(f"Loading cards from: {csv_path}", file=sys.stderr)
    print(f"This will gather data for {len(cards_to_fetch)} card(s)", file=sys.stderr)
    print(f"Output will be saved to: {output_path}", file=sys.stderr)
    print(f"Using {workers} parallel workers", file=sys.stderr)
    print("This may take a while. Please be patient...", file=sys.stderr)
    print("", file=sys.stderr)

    successful = 0
    skipped = 0
    progress_lock = Lock()
    csv_lock = Lock()
    completed = 0
    header_written = [False]  # Use list to allow modification in nested function

    # Use ThreadPoolExecutor for parallel fetching and saving
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        future_to_card_id = {
            executor.submit(fetch_and_save_card, card_id, card_name, output_path, csv_lock, header_written): card_id
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
    print(f"Gathering complete! Success: {successful}, Skipped: {skipped}", file=sys.stderr)
    print(f"Card data saved to: {output_path}", file=sys.stderr)
    if skipped > 0:
        print(
            f"Note: {skipped} card(s) were skipped because they were not found or didn't match the CSV name.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()

