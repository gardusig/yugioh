#!/usr/bin/env python3
"""
Check if database is empty, needs migrations, or needs seeding.
When populated, prints counts and runs validation queries; alerts on issues.

Exit codes:
    0  Database empty (no tables) — run migrations
    1  Tables exist but no cards — run seed
    2  Database populated (ready)
    3  Connection error
    4  Other error
"""

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


def get_connection():
    return psycopg2.connect(**DB_SETTINGS)


def check_database():
    """Check database state. Returns exit code 0, 1, or 2."""
    try:
        conn = get_connection()
        with conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = 'cards'
                );
                """
            )
            if not cur.fetchone()[0]:
                return 0

            cur.execute("SELECT COUNT(*) FROM cards;")
            if cur.fetchone()[0] == 0:
                return 1

            return 2

    except psycopg2.OperationalError as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Error checking database: {e}", file=sys.stderr)
        sys.exit(4)


def print_data_report():
    """Print table counts, key queries, and alert on data issues."""
    conn = get_connection()
    alerts = []

    try:
        with conn, conn.cursor() as cur:
            # ---- Counts ----
            cur.execute("SELECT COUNT(*) FROM cards;")
            card_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM decks;")
            deck_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM deck_cards;")
            deck_cards_count = cur.fetchone()[0]

            print("--- Counts ---")
            print(f"  cards:      {card_count}")
            print(f"  decks:      {deck_count}")
            print(f"  deck_cards: {deck_cards_count}")

            if card_count > 0:
                cur.execute("SELECT MIN(id), MAX(id) FROM cards;")
                min_id, max_id = cur.fetchone()
                print(f"  card ID range: {min_id} — {max_id}")

            # ---- Expected cards (from data/cards.csv if present) ----
            # Script is at scripts/src/check_db.py -> project root is parent.parent.parent
            project_root = Path(__file__).resolve().parent.parent.parent
            cards_csv = project_root / "data" / "cards.csv"
            if cards_csv.exists():
                with open(cards_csv, "r", encoding="utf-8", errors="ignore") as f:
                    expected_lines = sum(1 for _ in f) - 1  # subtract header
                if expected_lines > 0:
                    print(f"\n  data/cards.csv rows (expected): {expected_lines}")
                    if card_count != expected_lines:
                        alerts.append(
                            f"Card count mismatch: DB has {card_count}, CSV has {expected_lines} rows. Re-seed?"
                        )

            # ---- Validation queries ----
            print("\n--- Data checks ---")

            cur.execute("SELECT COUNT(*) FROM cards WHERE name IS NULL OR TRIM(name) = '';")
            n = cur.fetchone()[0]
            if n > 0:
                alerts.append(f"Cards with missing or empty name: {n}")
            else:
                print("  Cards with valid name: OK")

            cur.execute("SELECT COUNT(*) FROM cards WHERE type IS NULL OR TRIM(type) = '';")
            n = cur.fetchone()[0]
            if n > 0:
                alerts.append(f"Cards with missing or empty type: {n}")
            else:
                print("  Cards with valid type: OK")

            cur.execute("SELECT COUNT(*) FROM cards WHERE image IS NULL OR TRIM(image) = '';")
            n = cur.fetchone()[0]
            if n > 0:
                print(f"  Cards with no image URL: {n} (optional)")
            else:
                print("  Cards with image URL: OK")

            cur.execute(
                """
                SELECT COUNT(*) FROM deck_cards dc
                WHERE NOT EXISTS (SELECT 1 FROM cards c WHERE c.id = dc.card_id);
                """
            )
            n = cur.fetchone()[0]
            if n > 0:
                alerts.append(f"deck_cards referencing missing card_id: {n}")
            else:
                print("  deck_cards → cards: OK")

            cur.execute(
                """
                SELECT COUNT(*) FROM deck_cards dc
                WHERE NOT EXISTS (SELECT 1 FROM decks d WHERE d.id = dc.deck_id);
                """
            )
            n = cur.fetchone()[0]
            if n > 0:
                alerts.append(f"deck_cards referencing missing deck_id: {n}")
            else:
                print("  deck_cards → decks: OK")

            # ---- Alerts ----
            if alerts:
                print("\n--- Alerts ---")
                for msg in alerts:
                    print(f"  ⚠ {msg}")
            else:
                print("\n  No data issues found.")
    finally:
        conn.close()


if __name__ == "__main__":
    status = check_database()
    if status == 2:
        try:
            print_data_report()
        except Exception as e:
            print(f"Could not generate report: {e}", file=sys.stderr)
    elif status == 0:
        print("Database is empty (no tables). Run: db_manager.py migrate", file=sys.stderr)
    elif status == 1:
        print("Database has tables but no data. Run: db_manager.py seed", file=sys.stderr)
    sys.exit(status)
