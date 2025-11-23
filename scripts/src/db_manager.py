#!/usr/bin/env python3
"""
Database management utilities for the Yu-Gi-Oh! project.

This script provides helper commands to:
  - Reset or clear database tables
  - Seed sample cards and decks

Usage examples (Local):
    python db_manager.py reset-db
    python db_manager.py clear-all
    python db_manager.py clear-table cards
    python db_manager.py seed --cards
    python db_manager.py seed --decks
    python db_manager.py seed
"""

import argparse
import os
import sys
from typing import List

import psycopg2

DB_SETTINGS = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "dbname": os.environ.get("DB_NAME", "yugioh_db"),
    "user": os.environ.get("DB_USER", "yugioh_user"),
    "password": os.environ.get("DB_PASSWORD", "yugioh_password"),
}


CARDS_DATA = [
    {
        "id": 1,
        "name": "Blue-Eyes White Dragon",
        "type": "Normal Monster",
        "level": 8,
        "attack_points": 3000,
        "defense_points": 2500,
        "cost": 8,
        "description": "This legendary dragon is a powerful engine of destruction. "
        "Virtually invincible, very few have faced this awesome creature and lived to tell the tale.",
        "image": "https://images.ygoprodeck.com/images/cards/89631139.jpg",
        "attribute": "LIGHT",
        "race": "Dragon",
        "rarity": "Ultra Rare",
    },
    {
        "id": 2,
        "name": "Dark Magician",
        "type": "Normal Monster",
        "level": 7,
        "attack_points": 2500,
        "defense_points": 2100,
        "cost": 7,
        "description": "The ultimate wizard in terms of attack and defense.",
        "image": "https://images.ygoprodeck.com/images/cards/46986414.jpg",
        "attribute": "DARK",
        "race": "Spellcaster",
        "rarity": "Ultra Rare",
    },
    {
        "id": 3,
        "name": "Exodia the Forbidden One",
        "type": "Effect Monster",
        "level": 3,
        "attack_points": 1000,
        "defense_points": 1000,
        "cost": 3,
        "description": 'If you have "Right Leg of the Forbidden One", "Left Leg of the Forbidden One", '
        '"Right Arm of the Forbidden One" and "Left Arm of the Forbidden One" in addition to this card '
        "in your hand, you win the Duel.",
        "image": "https://images.ygoprodeck.com/images/cards/33396948.jpg",
        "attribute": "DARK",
        "race": "Spellcaster",
        "rarity": "Ultra Rare",
    },
    {
        "id": 4,
        "name": "Obelisk the Tormentor",
        "type": "Effect Monster",
        "level": 10,
        "attack_points": 4000,
        "defense_points": 4000,
        "cost": 10,
        "description": "Requires 3 Tributes to Normal Summon (cannot be Normal Set). This card's Normal "
        "Summon cannot be negated. When Normal Summoned, cards and effects cannot be activated. "
        "Neither player can target this card with card effects. Once per turn, during the End Phase, "
        "if this card was Special Summoned: Send it to the GY. You can Tribute 2 monsters; destroy all "
        "monsters your opponent controls. This card cannot declare an attack the turn this effect is activated.",
        "image": "https://images.ygoprodeck.com/images/cards/10000000.jpg",
        "attribute": "DIVINE",
        "race": "Divine-Beast",
        "rarity": "Secret Rare",
    },
    {
        "id": 5,
        "name": "Slifer the Sky Dragon",
        "type": "Effect Monster",
        "level": 10,
        "attack_points": -1,
        "defense_points": -1,
        "cost": 10,
        "description": "Requires 3 Tributes to Normal Summon (cannot be Normal Set). This card's Normal "
        "Summon cannot be negated. When Normal Summoned, cards and effects cannot be activated. "
        "Once per turn, during the End Phase, if this card was Special Summoned: Send it to the GY. "
        "Gains 1000 ATK/DEF for each card in your hand. If a monster(s) is Normal or Special Summoned "
        "to your opponent's field in Attack Position: That monster(s) loses 2000 ATK, then if its ATK "
        "has been reduced to 0 as a result, destroy it.",
        "image": "https://images.ygoprodeck.com/images/cards/10000020.jpg",
        "attribute": "DIVINE",
        "race": "Divine-Beast",
        "rarity": "Secret Rare",
    },
    {
        "id": 6,
        "name": "The Winged Dragon of Ra",
        "type": "Effect Monster",
        "level": 10,
        "attack_points": -1,
        "defense_points": -1,
        "cost": 10,
        "description": "Cannot be Special Summoned. Requires 3 Tributes to Normal Summon (cannot be Normal Set). "
        "This card's Normal Summon cannot be negated. When Normal Summoned, other cards and effects cannot "
        "be activated. When this card is Normal Summoned: You can pay LP so that you only have 100 left; "
        "this card gains ATK/DEF equal to the amount of LP paid. You can pay 1000 LP, then target 1 monster "
        "on the field; destroy that target.",
        "image": "https://images.ygoprodeck.com/images/cards/10000010.jpg",
        "attribute": "DIVINE",
        "race": "Divine-Beast",
        "rarity": "Secret Rare",
    },
    {
        "id": 7,
        "name": "Red-Eyes Black Dragon",
        "type": "Normal Monster",
        "level": 7,
        "attack_points": 2400,
        "defense_points": 2000,
        "cost": 7,
        "description": "A ferocious dragon with a deadly attack.",
        "image": "https://images.ygoprodeck.com/images/cards/74677422.jpg",
        "attribute": "DARK",
        "race": "Dragon",
        "rarity": "Ultra Rare",
    },
    {
        "id": 8,
        "name": "Summoned Skull",
        "type": "Normal Monster",
        "level": 6,
        "attack_points": 2500,
        "defense_points": 1200,
        "cost": 6,
        "description": "A fiend with dark powers for confusing the enemy. Among the Fiend-Type monsters, "
        'this monster boasts considerable force. (This card is always treated as an "Archfiend" card.)',
        "image": "https://images.ygoprodeck.com/images/cards/70781052.jpg",
        "attribute": "DARK",
        "race": "Fiend",
        "rarity": "Super Rare",
    },
    {
        "id": 9,
        "name": "Dark Magician Girl",
        "type": "Effect Monster",
        "level": 6,
        "attack_points": 2000,
        "defense_points": 1700,
        "cost": 6,
        "description": 'Gains 300 ATK for every "Dark Magician" or "Magician of Black Chaos" in the GY.',
        "image": "https://images.ygoprodeck.com/images/cards/38033121.jpg",
        "attribute": "DARK",
        "race": "Spellcaster",
        "rarity": "Ultra Rare",
    },
    {
        "id": 10,
        "name": "Kuriboh",
        "type": "Effect Monster",
        "level": 1,
        "attack_points": 300,
        "defense_points": 200,
        "cost": 1,
        "description": "During damage calculation, if your opponent's monster attacks (Quick Effect): "
        "You can discard this card; you take no battle damage from that battle.",
        "image": "https://images.ygoprodeck.com/images/cards/40640057.jpg",
        "attribute": "DARK",
        "race": "Fiend",
        "rarity": "Common",
    },
]


def generate_deck_cards(base_pattern: List[int]) -> List[int]:
    """Expand a shorter pattern to 40 positions."""
    repeated: List[int] = []
    idx = 0
    while len(repeated) < 40:
        repeated.append(base_pattern[idx % len(base_pattern)])
        idx += 1
    return repeated


DECKS_DATA = [
    {
        "name": "Legend of Blue Eyes",
        "description": "Seto Kaiba's dragon-heavy deck built around overwhelming attack power.",
        "character_name": "Seto Kaiba",
        "archetype": "Dragon",
        "max_cost": 250,
        "is_preset": True,
        "card_ids": generate_deck_cards([1, 2, 4, 5, 6, 7]),
    },
    {
        "name": "Heart of the Cards",
        "description": "Yugi's balanced line-up featuring spellcasters, guardians, and the Egyptian Gods.",
        "character_name": "Yugi Muto",
        "archetype": "Spellcaster",
        "max_cost": 230,
        "is_preset": True,
        "card_ids": generate_deck_cards([2, 3, 5, 6, 8, 9, 10]),
    },
]


def get_connection():
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        conn.autocommit = True
        return conn
    except psycopg2.Error as exc:
        print(f"[ERROR] Unable to connect to database: {exc}", file=sys.stderr)
        sys.exit(1)


def reset_database():
    """Drop and recreate the public schema (removes EVERYTHING)."""
    conn = get_connection()
    with conn, conn.cursor() as cur:
        cur.execute("DROP SCHEMA public CASCADE;")
        cur.execute("CREATE SCHEMA public;")
        cur.execute("GRANT ALL ON SCHEMA public TO public;")
        cur.execute(f"GRANT ALL ON SCHEMA public TO {DB_SETTINGS['user']};")
    print("[OK] Database schema reset. Run migrations to recreate tables:")
    print("  python run_migrations.py")


def clear_all_tables():
    """Clear all domain tables but keep the schema."""
    conn = get_connection()
    with conn, conn.cursor() as cur:
        # Check if tables exist
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            AND table_name IN ('cards', 'decks', 'deck_cards')
        """
        )
        existing_tables = [row[0] for row in cur.fetchall()]

        if not existing_tables:
            print("[ERROR] Tables do not exist. Run migrations first:", file=sys.stderr)
            print("  python run_migrations.py", file=sys.stderr)
            sys.exit(1)

        # Only clear tables that exist
        tables_to_clear = ", ".join(existing_tables)
        cur.execute(f"TRUNCATE TABLE {tables_to_clear} RESTART IDENTITY CASCADE;")
    print(f"[OK] Tables {', '.join(existing_tables)} cleared.")


def clear_table(table_name: str):
    """Clear a single table (cards, decks, or deck_cards)."""
    if table_name not in {"cards", "decks", "deck_cards"}:
        print(f"[ERROR] Unsupported table '{table_name}'.", file=sys.stderr)
        sys.exit(1)

    conn = get_connection()
    with conn, conn.cursor() as cur:
        # Check if table exists
        cur.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = %s
            );
        """,
            (table_name,),
        )
        table_exists = cur.fetchone()[0]

        if not table_exists:
            print(
                f"[ERROR] Table '{table_name}' does not exist. Run migrations first:",
                file=sys.stderr,
            )
            print("  python run_migrations.py", file=sys.stderr)
            sys.exit(1)

        cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
    print(f"[OK] Table '{table_name}' cleared.")


def seed_cards(start_id=None, end_id=None):
    """Seed cards from CARDS_DATA, optionally filtered by ID range."""
    # Filter cards by ID range if specified
    cards_to_seed = CARDS_DATA
    if start_id is not None or end_id is not None:
        cards_to_seed = [
            card
            for card in CARDS_DATA
            if (start_id is None or card["id"] >= start_id)
            and (end_id is None or card["id"] <= end_id)
        ]

    if not cards_to_seed:
        print("[WARN] No cards found in the specified range.", file=sys.stderr)
        return

    conn = get_connection()
    seeded_count = 0
    with conn, conn.cursor() as cur:
        for card in cards_to_seed:
            # Preview card being added
            card_preview = f"Card #{card['id']:03d}: {card['name']}"
            if card.get("type"):
                card_preview += f" ({card['type']})"
            if card.get("level", 0) > 0:
                card_preview += f" [Lv.{card['level']}]"
            if card.get("attribute"):
                card_preview += f" [{card['attribute']}]"
            if card.get("attack_points", 0) > 0 or card.get("defense_points", 0) > 0:
                card_preview += (
                    f" ATK:{card.get('attack_points', 0)}/DEF:{card.get('defense_points', 0)}"
                )
            print(f"  → {card_preview}")

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
                card,
            )
            seeded_count += 1

    print(f"[OK] Seeded {seeded_count} card(s).")


def show_status():
    """Show database status (counts of cards, decks, etc.)."""
    conn = get_connection()
    with conn, conn.cursor() as cur:
        # Check if tables exist
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            AND table_name IN ('cards', 'decks', 'deck_cards')
        """
        )
        existing_tables = [row[0] for row in cur.fetchall()]

        if not existing_tables:
            print("[INFO] Database tables do not exist. Run migrations first:")
            print("  python run_migrations.py")
            return

        stats = {}

        if "cards" in existing_tables:
            cur.execute("SELECT COUNT(*) FROM cards;")
            stats["cards"] = cur.fetchone()[0]

        if "decks" in existing_tables:
            cur.execute("SELECT COUNT(*) FROM decks;")
            stats["decks"] = cur.fetchone()[0]

        if "deck_cards" in existing_tables:
            cur.execute("SELECT COUNT(*) FROM deck_cards;")
            stats["deck_cards"] = cur.fetchone()[0]

        print("[Database Status]")
        for table, count in stats.items():
            print(f"  {table}: {count}")

        # Show card ID range if cards exist
        if "cards" in existing_tables and stats.get("cards", 0) > 0:
            cur.execute("SELECT MIN(id), MAX(id) FROM cards;")
            min_id, max_id = cur.fetchone()
            print(f"  Card ID range: {min_id} - {max_id}")


def seed_decks():
    conn = get_connection()
    with conn, conn.cursor() as cur:
        for deck in DECKS_DATA:
            cur.execute(
                """
                INSERT INTO decks (name, description, character_name, archetype, max_cost, is_preset)
                VALUES (%(name)s, %(description)s, %(character_name)s, %(archetype)s,
                        %(max_cost)s, %(is_preset)s)
                ON CONFLICT (name) DO UPDATE SET
                    description = EXCLUDED.description,
                    character_name = EXCLUDED.character_name,
                    archetype = EXCLUDED.archetype,
                    max_cost = EXCLUDED.max_cost,
                    is_preset = EXCLUDED.is_preset,
                    updated_at = NOW()
                RETURNING id;
                """,
                deck,
            )
            deck_id = cur.fetchone()[0]

            # Clear current deck list then repopulate
            cur.execute("DELETE FROM deck_cards WHERE deck_id = %s;", (deck_id,))

            for position, card_id in enumerate(deck["card_ids"], start=1):
                cur.execute(
                    """
                    INSERT INTO deck_cards (deck_id, card_id, position)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (deck_id, position) DO UPDATE SET
                        card_id = EXCLUDED.card_id;
                    """,
                    (deck_id, card_id, position),
                )
    print(f"[OK] Seeded {len(DECKS_DATA)} decks with deck_cards.")


def main():
    parser = argparse.ArgumentParser(description="Yu-Gi-Oh! database utilities.")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "reset-db",
        help="Drop and recreate the public schema. Requires rerunning Flyway migrations afterwards.",
    )
    subparsers.add_parser(
        "clear-all",
        help="Clear all data from cards, decks, and deck_cards tables but keep the schema.",
    )

    subparsers.add_parser(
        "status",
        help="Show database status (counts of cards, decks, etc.).",
    )

    clear_parser = subparsers.add_parser(
        "clear-table", help="Clear all data from a single table (cards, decks, deck_cards)."
    )
    clear_parser.add_argument("table", choices=["cards", "decks", "deck_cards"])

    seed_parser = subparsers.add_parser("seed", help="Seed cards and/or decks.")
    seed_parser.add_argument(
        "--cards", action="store_true", help="Seed only cards (default: seed cards and decks)."
    )
    seed_parser.add_argument(
        "--decks", action="store_true", help="Seed only decks (default: seed cards and decks)."
    )
    seed_parser.add_argument(
        "--start",
        type=int,
        metavar="ID",
        help="Start card ID (inclusive). Only seed cards with ID >= this value.",
    )
    seed_parser.add_argument(
        "--end",
        type=int,
        metavar="ID",
        help="End card ID (inclusive). Only seed cards with ID <= this value.",
    )

    args = parser.parse_args()

    if args.command == "reset-db":
        reset_database()
    elif args.command == "clear-all":
        clear_all_tables()
    elif args.command == "clear-table":
        clear_table(args.table)
    elif args.command == "status":
        show_status()
    elif args.command == "seed":
        seed_cards_flag = args.cards or not (args.cards or args.decks)
        seed_decks_flag = args.decks or not (args.cards or args.decks)

        if seed_cards_flag:
            seed_cards(start_id=args.start, end_id=args.end)
        if seed_decks_flag:
            seed_decks()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
