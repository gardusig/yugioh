#!/usr/bin/env python3
"""
Run database migrations independently from the backend.

This script reads SQL migration files from the migrations directory
and executes them against the database. This allows you to set up the schema
without starting the entire backend application.

Usage:
    python run_migrations.py
    python run_migrations.py --migration-dir migrations
"""

import argparse
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
    """Get a database connection."""
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        conn.autocommit = False
        return conn
    except psycopg2.Error as exc:
        print(f"[ERROR] Unable to connect to database: {exc}", file=sys.stderr)
        sys.exit(1)


def parse_migration_filename(filename):
    """Parse Flyway migration filename to extract version number.

    Expected format: V{version}__{description}.sql
    Example: V1__initial_schema.sql -> version 1
    """
    if not filename.endswith(".sql"):
        return None

    name = filename[:-4]  # Remove .sql
    if not name.startswith("V"):
        return None

    try:
        # Extract version number (everything between V and __)
        parts = name.split("__", 1)
        if len(parts) < 2:
            return None

        version_str = parts[0][1:]  # Remove 'V' prefix
        version = int(version_str)
        description = parts[1]
        return {"version": version, "description": description, "filename": filename}
    except (ValueError, IndexError):
        return None


def get_migration_files(migration_dir):
    """Get all migration files sorted by version."""
    migration_path = Path(migration_dir)
    if not migration_path.exists():
        print(f"[ERROR] Migration directory not found: {migration_dir}", file=sys.stderr)
        sys.exit(1)

    migrations = []
    for file_path in migration_path.glob("V*.sql"):
        migration_info = parse_migration_filename(file_path.name)
        if migration_info:
            migration_info["path"] = file_path
            migrations.append(migration_info)

    # Sort by version number
    migrations.sort(key=lambda x: x["version"])
    return migrations


def check_migration_applied(conn, version):
    """Check if a migration has already been applied."""
    with conn.cursor() as cur:
        # Check if flyway_schema_history table exists
        cur.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'flyway_schema_history'
            );
        """
        )
        table_exists = cur.fetchone()[0]

        if not table_exists:
            return False

        # Check if this version is already applied
        cur.execute(
            """
            SELECT COUNT(*) FROM flyway_schema_history
            WHERE version = %s AND success = true
        """,
            (str(version),),
        )
        count = cur.fetchone()[0]
        return count > 0


def record_migration(conn, version, description, checksum=None):
    """Record a migration in flyway_schema_history table."""
    with conn.cursor() as cur:
        # Create flyway_schema_history table if it doesn't exist
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS flyway_schema_history (
                installed_rank INTEGER PRIMARY KEY,
                version VARCHAR(50),
                description VARCHAR(200),
                type VARCHAR(20),
                script VARCHAR(1000),
                checksum INTEGER,
                installed_by VARCHAR(100),
                installed_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                execution_time INTEGER,
                success BOOLEAN
            );
        """
        )

        # Get next rank
        cur.execute("SELECT COALESCE(MAX(installed_rank), 0) + 1 FROM flyway_schema_history")
        rank = cur.fetchone()[0]

        # Insert migration record
        cur.execute(
            """
            INSERT INTO flyway_schema_history
            (installed_rank, version, description, type, script, checksum, installed_by, execution_time, success)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                rank,
                str(version),
                description,
                "SQL",
                f"V{version}__{description}.sql",
                checksum,
                DB_SETTINGS["user"],
                0,  # Execution time not tracked
                True,
            ),
        )


def run_migration(conn, migration_info, dry_run=False):
    """Run a single migration file."""
    version = migration_info["version"]
    description = migration_info["description"]
    file_path = migration_info["path"]

    # Check if already applied
    if check_migration_applied(conn, version):
        print(f"[SKIP] Migration V{version} ({description}) already applied")
        return True

    print(f"[RUN] Migration V{version}: {description}")

    if dry_run:
        print(f"  [DRY RUN] Would execute: {file_path}")
        return True

    try:
        # Read SQL file
        with open(file_path, encoding="utf-8") as f:
            sql_content = f.read()

        # Execute SQL
        with conn.cursor() as cur:
            cur.execute(sql_content)

        # Record migration
        record_migration(conn, version, description)
        conn.commit()

        print(f"[OK] Migration V{version} applied successfully")
        return True
    except Exception as exc:
        conn.rollback()
        print(f"[ERROR] Failed to apply migration V{version}: {exc}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run database migrations independently from the backend."
    )
    parser.add_argument(
        "--migration-dir",
        type=str,
        default="migrations",
        help="Path to migration directory (default: migrations)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without actually running migrations",
    )
    args = parser.parse_args()

    # Resolve migration directory path
    # Script is in src/, but migrations/ is in scripts root, so go up one level
    scripts_root = Path(__file__).parent.parent
    migration_dir = (scripts_root / args.migration_dir).resolve()

    if not migration_dir.exists():
        print(f"[ERROR] Migration directory not found: {migration_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Using migration directory: {migration_dir}")

    # Get connection
    conn = get_connection()
    print(
        f"[INFO] Connected to database: {DB_SETTINGS['host']}:{DB_SETTINGS['port']}/{DB_SETTINGS['dbname']}"
    )

    try:
        # Get migration files
        migrations = get_migration_files(migration_dir)

        if not migrations:
            print("[WARN] No migration files found", file=sys.stderr)
            return

        print(f"[INFO] Found {len(migrations)} migration(s)")

        # Run migrations
        success_count = 0
        for migration in migrations:
            if run_migration(conn, migration, dry_run=args.dry_run):
                success_count += 1
            else:
                print("[ERROR] Migration failed, stopping", file=sys.stderr)
                sys.exit(1)

        print(f"\n[OK] Successfully processed {success_count}/{len(migrations)} migration(s)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
