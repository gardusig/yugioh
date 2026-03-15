#!/usr/bin/env python3
"""
Database setup: migrations + seed from data/*.csv (no network required).

Usage:
    python setup.py
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CARDS_CSV = PROJECT_ROOT / "data" / "cards.csv"


def main():
    print("Checking database state...")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "check_db.py")], capture_output=True, text=True
    )
    db_state = result.returncode

    if db_state == 0:
        print("Database is empty - running migrations...")
        subprocess.run([sys.executable, str(SCRIPT_DIR / "run_migrations.py")], check=True)
        print("✓ Migrations completed")

        if not CARDS_CSV.exists():
            print("Generating data/cards.csv from card_list.csv...")
            subprocess.run([sys.executable, str(SCRIPT_DIR / "generate_cards_csv.py")], check=True)
        print("Seeding from data/*.csv...")
        subprocess.run([sys.executable, str(SCRIPT_DIR / "seed_from_csv.py")], check=True)
        print("✓ Database setup complete")

    elif db_state == 1:
        if not CARDS_CSV.exists():
            subprocess.run([sys.executable, str(SCRIPT_DIR / "generate_cards_csv.py")], check=True)
        print("Seeding from data/*.csv...")
        subprocess.run([sys.executable, str(SCRIPT_DIR / "seed_from_csv.py")], check=True)
        print("✓ Database seeded")

    elif db_state == 2:
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
