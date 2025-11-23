#!/usr/bin/env python3
"""
Check if database is empty or needs migrations.

Returns:
    0 if database is empty (needs setup)
    1 if database has tables but no cards (needs seeding)
    2 if database is populated (ready)
"""

import os
import sys

import psycopg2

DB_SETTINGS = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 5432)),
    "dbname": os.environ.get("DB_NAME", "yugioh_db"),
    "user": os.environ.get("DB_USER", "yugioh_user"),
    "password": os.environ.get("DB_PASSWORD", "yugioh_password"),
}


def check_database():
    """Check database state."""
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        with conn.cursor() as cur:
            # Check if cards table exists
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'cards'
                );
            """
            )
            cards_table_exists = cur.fetchone()[0]

            if not cards_table_exists:
                # Database is empty - needs migrations
                return 0

            # Check if cards table has data
            cur.execute("SELECT COUNT(*) FROM cards;")
            card_count = cur.fetchone()[0]

            if card_count == 0:
                # Tables exist but no data - needs seeding
                return 1

            # Database is populated
            return 2

    except psycopg2.OperationalError as e:
        print(f"Database connection error: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Error checking database: {e}", file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    status = check_database()
    sys.exit(status)
