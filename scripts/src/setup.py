#!/usr/bin/env python3
"""
Smart database setup: Check database state and only run migrations/seeding if needed.

Usage:
    python setup.py
    python setup.py --seed-range 1 100
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SCRIPTS_ROOT = SCRIPT_DIR.parent  # Go up from src/ to scripts/


def main():
    parser = argparse.ArgumentParser(description="Smart database setup")
    parser.add_argument(
        "--seed-range",
        type=int,
        nargs=2,
        metavar=("START", "END"),
        default=[1, 100],
        help="Range of cards to seed (default: 1 100)",
    )
    args = parser.parse_args()

    # Check database state
    print("Checking database state...")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "check_db.py")], capture_output=True, text=True
    )
    db_state = result.returncode

    if db_state == 0:
        # Database is empty - run migrations
        print("Database is empty - running migrations...")
        subprocess.run([sys.executable, str(SCRIPT_DIR / "run_migrations.py")], check=True)
        print("✓ Migrations completed")

        # Seed cards
        print(f"Seeding cards {args.seed_range[0]}-{args.seed_range[1]}...")
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "crawl_cards.py"),
                "--start",
                str(args.seed_range[0]),
                "--end",
                str(args.seed_range[1]),
                "--workers",
                "10",
            ],
            check=True,
        )
        print("✓ Database setup complete")

    elif db_state == 1:
        # Database has tables but no cards - seed data
        print("Database has tables but no cards - seeding data...")
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "crawl_cards.py"),
                "--start",
                str(args.seed_range[0]),
                "--end",
                str(args.seed_range[1]),
                "--workers",
                "10",
            ],
            check=True,
        )
        print("✓ Database seeded")

    elif db_state == 2:
        # Database is already populated
        print("Database is already populated - skipping setup")

    elif db_state == 3:
        print("Error: Cannot connect to database", file=sys.stderr)
        sys.exit(1)

    elif db_state == 4:
        print("Error: Failed to check database state", file=sys.stderr)
        sys.exit(1)

    else:
        print(f"Error: Unknown database state (exit code: {db_state})", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
