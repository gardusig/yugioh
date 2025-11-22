# Scripts Directory

Simple scripts for retrieving card data and inserting into the database.

## Directory Structure

```
scripts/
├── data/                    # Data crawling and CSV files
│   ├── crawl_cards.py      # Crawl card data from yugioh.fandom.com
│   └── sacred_cards.csv    # Card names CSV (001-900)
├── migrations/             # Database migration SQL files
│   └── V1__initial_schema.sql
├── check_db.py             # Check database state
├── run_migrations.py       # Run database migrations
└── setup.py                # Smart database setup (main entry point)
```

## Quick Start

### Setup Database

```bash
cd scripts
DB_HOST=localhost DB_PORT=5432 python3 setup.py
```

This will:
- Check if database is empty
- Run migrations if needed
- Seed first 100 cards if needed

## Main Scripts

### `setup.py`
Smart database setup that checks state and only runs what's needed.

```bash
python3 setup.py
python3 setup.py --seed-range 1 100
```

### `data/crawl_cards.py`
Crawl card data from yugioh.fandom.com and insert into database.

```bash
python3 data/crawl_cards.py --start 1 --end 100 --workers 10
```

### `run_migrations.py`
Run database migrations from `migrations/` directory.

```bash
python3 run_migrations.py
```

### `check_db.py`
Check database state:
- Exit 0: Database is empty (needs migrations)
- Exit 1: Database has tables but no cards (needs seeding)
- Exit 2: Database is populated (ready)

## Environment Variables

All scripts use these environment variables (with defaults):
- `DB_HOST` (default: localhost)
- `DB_PORT` (default: 5432)
- `DB_NAME` (default: yugioh_db)
- `DB_USER` (default: yugioh_user)
- `DB_PASSWORD` (default: yugioh_password)

## Data Files

- `data/sacred_cards.csv` - Contains all 900 card IDs and names from Yu-Gi-Oh! The Sacred Cards
