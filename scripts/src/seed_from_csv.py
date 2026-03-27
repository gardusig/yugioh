#!/usr/bin/env python3
"""
Seed the database from CSV files in data/.

Expects:
  - data/cards.csv    (id, name, type, attribute, race, level, attack_points, defense_points, cost, rarity, description, image)
  - data/decks.csv   (name, description, character_name, archetype, max_cost, is_preset)
  - data/deck_cards.csv  (deck_name, card_id, position)

Run from project root or scripts/:
  python3 scripts/src/seed_from_csv.py
  python3 scripts/src/seed_from_csv.py --data-dir /path/to/data

If data/cards.csv doesn't exist, run: python3 scripts/src/generate_cards_csv.py
"""

import argparse
import csv
import os
import sys
from pathlib import Path

import psycopg2

DB_SETTINGS = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "dbname": os.environ.get("DB_NAME", "yugioh_db"),
    "user": os.environ.get("DB_USER", "yugioh_user"),
    "password": os.environ.get("DB_PASSWORD", "yugioh_password"),
}


def get_data_dir() -> Path:
    """Resolve data directory: script is in scripts/src/, data is at project root."""
    script = Path(__file__).resolve()
    # scripts/src/seed_from_csv.py -> project root
    project_root = script.parent.parent.parent
    return project_root / "data"


def get_connection():
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        conn.autocommit = False
        return conn
    except psycopg2.Error as exc:
        print(f"[ERROR] Cannot connect to database: {exc}", file=sys.stderr)
        sys.exit(1)


def seed_cards(conn, data_dir: Path) -> int:
    cards_csv = data_dir / "cards.csv"
    if not cards_csv.exists():
        print(f"[ERROR] {cards_csv} not found. Run: python3 scripts/src/generate_cards_csv.py", file=sys.stderr)
        sys.exit(1)

    count = 0
    with open(cards_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                """
                INSERT INTO cards (id, name, description, image, type, attribute, race, level,
                                   attack_points, defense_points, cost, rarity)
                VALUES (%(id)s, %(name)s, %(description)s, %(image)s, %(type)s, %(attribute)s,
                        %(race)s, %(level)s, %(attack_points)s, %(defense_points)s, %(cost)s, %(rarity)s)
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
                {
                    "id": int(row["id"]),
                    "name": row["name"],
                    "description": row.get("description", "").strip() or None,
                    "image": row.get("image", "").strip() or None,
                    "type": row.get("type", "Normal Monster"),
                    "attribute": row.get("attribute", "").strip() or None,
                    "race": row.get("race", "").strip() or None,
                    "level": int(row.get("level") or 0),
                    "attack_points": int(row.get("attack_points") or 0),
                    "defense_points": int(row.get("defense_points") or 0),
                    "cost": int(row.get("cost") or 0),
                    "rarity": row.get("rarity", "").strip() or None,
                },
            )
            count += 1

    conn.commit()
    return count


def seed_decks(conn, data_dir: Path) -> dict:
    """Insert decks, return mapping deck_name -> deck_id."""
    decks_csv = data_dir / "decks.csv"
    if not decks_csv.exists():
        print(f"[WARN] {decks_csv} not found. Skipping decks.", file=sys.stderr)
        return {}

    name_to_id = {}
    with open(decks_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                """
                INSERT INTO decks (name, description, character_name, archetype, max_cost, is_preset)
                VALUES (%(name)s, %(description)s, %(character_name)s, %(archetype)s, %(max_cost)s, %(is_preset)s)
                ON CONFLICT (name) DO UPDATE SET
                    description = EXCLUDED.description,
                    character_name = EXCLUDED.character_name,
                    archetype = EXCLUDED.archetype,
                    max_cost = EXCLUDED.max_cost,
                    is_preset = EXCLUDED.is_preset,
                    updated_at = NOW()
                RETURNING id;
                """,
                {
                    "name": row["name"],
                    "description": row.get("description", "").strip() or None,
                    "character_name": row.get("character_name", "").strip() or None,
                    "archetype": row.get("archetype", "").strip() or None,
                    "max_cost": int(row.get("max_cost", 0)),
                    "is_preset": row.get("is_preset", "false").lower() in ("true", "1", "yes"),
                },
            )
            deck_id = cur.fetchone()[0]
            name_to_id[row["name"]] = deck_id

    conn.commit()
    return name_to_id


def seed_deck_cards(conn, data_dir: Path, name_to_id: dict) -> int:
    deck_cards_csv = data_dir / "deck_cards.csv"
    if not deck_cards_csv.exists():
        print(f"[WARN] {deck_cards_csv} not found. Skipping deck cards.", file=sys.stderr)
        return 0

    if not name_to_id:
        print("[WARN] No decks loaded. Skipping deck_cards.", file=sys.stderr)
        return 0

    count = 0
    with open(deck_cards_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with conn.cursor() as cur:
        for row in rows:
            deck_name = row["deck_name"]
            if deck_name not in name_to_id:
                print(f"[WARN] Unknown deck '{deck_name}' in deck_cards.csv, skipping.", file=sys.stderr)
                continue
            deck_id = name_to_id[deck_name]
            card_id = int(row["card_id"])
            position = int(row["position"])

            cur.execute(
                """
                INSERT INTO deck_cards (deck_id, card_id, position)
                VALUES (%s, %s, %s)
                ON CONFLICT (deck_id, card_id, position) DO UPDATE SET position = EXCLUDED.position;
                """,
                (deck_id, card_id, position),
            )
            count += 1

    conn.commit()
    return count


def main():
    parser = argparse.ArgumentParser(description="Seed database from data/*.csv")
    parser.add_argument("--data-dir", type=Path, default=None, help="Path to data directory")
    args = parser.parse_args()

    data_dir = args.data_dir or get_data_dir()
    if not data_dir.exists():
        print(f"[ERROR] Data directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Loading from {data_dir}")
    conn = get_connection()

    try:
        print("  → Seeding cards...")
        cards_count = seed_cards(conn, data_dir)
        print(f"  ✓ {cards_count} cards")

        print("  → Seeding decks...")
        name_to_id = seed_decks(conn, data_dir)
        print(f"  ✓ {len(name_to_id)} decks")

        print("  → Seeding deck_cards...")
        dc_count = seed_deck_cards(conn, data_dir, name_to_id)
        print(f"  ✓ {dc_count} deck_cards")

        print("[OK] Database seeded from CSV.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
