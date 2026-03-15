#!/usr/bin/env python3
"""
Database management: reset, clear, seed from CSV, status.

Usage:
    python db_manager.py reset-db
    python db_manager.py reset-and-seed   # Full reset + migrations + seed
    python db_manager.py clear-all
    python db_manager.py clear-table cards
    python db_manager.py seed
    python db_manager.py status
"""

import argparse
import os
import subprocess
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

SCRIPT_DIR = Path(__file__).parent


def get_connection():
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        conn.autocommit = True
        return conn
    except psycopg2.Error as exc:
        print(f"[ERROR] Unable to connect to database: {exc}", file=sys.stderr)
        sys.exit(1)


def reset_database():
    """Drop and recreate the public schema."""
    conn = get_connection()
    with conn, conn.cursor() as cur:
        cur.execute("DROP SCHEMA public CASCADE;")
        cur.execute("CREATE SCHEMA public;")
        cur.execute("GRANT ALL ON SCHEMA public TO public;")
        cur.execute(f"GRANT ALL ON SCHEMA public TO {DB_SETTINGS['user']};")
    print("[OK] Schema reset. Run migrations: python run_migrations.py")


def clear_all_tables():
    """Clear all data but keep the schema."""
    conn = get_connection()
    with conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('cards', 'decks', 'deck_cards')
            """
        )
        existing = [r[0] for r in cur.fetchall()]
        if not existing:
            print("[ERROR] Tables do not exist. Run migrations first.", file=sys.stderr)
            sys.exit(1)
        cur.execute(f"TRUNCATE TABLE {', '.join(existing)} RESTART IDENTITY CASCADE;")
    print(f"[OK] Cleared {', '.join(existing)}")


def clear_table(table_name: str):
    """Clear a single table."""
    if table_name not in {"cards", "decks", "deck_cards"}:
        print(f"[ERROR] Unsupported table '{table_name}'", file=sys.stderr)
        sys.exit(1)
    conn = get_connection()
    with conn, conn.cursor() as cur:
        cur.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s);",
            (table_name,),
        )
        if not cur.fetchone()[0]:
            print(f"[ERROR] Table '{table_name}' does not exist. Run migrations first.", file=sys.stderr)
            sys.exit(1)
        cur.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
    print(f"[OK] Cleared {table_name}")


def seed():
    """Seed from data/*.csv."""
    subprocess.run([sys.executable, str(SCRIPT_DIR / "seed_from_csv.py")], check=True)


def reset_and_seed():
    """Full reset: drop schema, run migrations, seed from data/*.csv."""
    print("Resetting database...")
    reset_database()
    print("Running migrations...")
    subprocess.run([sys.executable, str(SCRIPT_DIR / "run_migrations.py")], check=True)
    print("Seeding from data/*.csv...")
    seed()
    print("[OK] Database reset and seeded successfully")


def show_status():
    """Show database counts."""
    conn = get_connection()
    with conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('cards', 'decks', 'deck_cards')
            """
        )
        existing = [r[0] for r in cur.fetchall()]
        if not existing:
            print("[INFO] Tables do not exist. Run migrations first.")
            return

        print("[Database Status]")
        for table in existing:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            print(f"  {table}: {count}")
        if "cards" in existing:
            cur.execute("SELECT COUNT(*) FROM cards;")
            if cur.fetchone()[0] > 0:
                cur.execute("SELECT MIN(id), MAX(id) FROM cards;")
                min_id, max_id = cur.fetchone()
                print(f"  Card ID range: {min_id} - {max_id}")


def main():
    parser = argparse.ArgumentParser(description="Database utilities")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("reset-db", help="Drop and recreate schema")
    subparsers.add_parser("reset-and-seed", help="Full reset + migrations + seed from data/*.csv")
    subparsers.add_parser("clear-all", help="Clear all tables")
    subparsers.add_parser("status", help="Show counts")
    subparsers.add_parser("seed", help="Seed from data/*.csv")
    clear_parser = subparsers.add_parser("clear-table", help="Clear one table")
    clear_parser.add_argument("table", choices=["cards", "decks", "deck_cards"])

    args = parser.parse_args()

    if args.command == "reset-db":
        reset_database()
    elif args.command == "reset-and-seed":
        reset_and_seed()
    elif args.command == "clear-all":
        clear_all_tables()
    elif args.command == "clear-table":
        clear_table(args.table)
    elif args.command == "status":
        show_status()
    elif args.command == "seed":
        seed()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
