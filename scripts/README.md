# Scripts — Data Management

Python tools for database setup and seeding. **Stack:** Python 3.11, psycopg2.

## Focus

- Run migrations (schema creation)
- Seed from `data/*.csv` (no network required)
- Database maintenance (reset, clear, status)

## First-Time Setup

From the **project root**:

```bash
./podman.sh up --build
```

The `scripts` service runs migrations and seeds from `data/*.csv` before the backend starts.

**Run on-demand:**

```bash
# Full setup (migrations + seed)
./podman.sh run --rm scripts

# Reset DB and reseed (ensures clean state from data/*.csv)
./podman.sh run --rm scripts scripts/src/db_manager.py reset-and-seed

# Migrations only
./podman.sh run --rm scripts scripts/src/run_migrations.py

# Seed from CSV
./podman.sh run --rm scripts scripts/src/seed_from_csv.py

# DB status
./podman.sh run --rm scripts scripts/src/check_db.py
```

## Main Scripts

| Script | Purpose |
|--------|---------|
| `src/setup.py` | Migrations + seed from CSV |
| `src/db_manager.py reset-and-seed` | **Reset DB + migrations + seed** (use to ensure seeds are correct) |
| `src/seed_from_csv.py` | Seed DB from `data/*.csv` |
| `src/generate_cards_csv.py` | Generate `data/cards.csv` (`--fetch-images` all, `--fill-missing-images` empty only, `--verify-images` validate URLs) |
| `src/run_migrations.py` | Run SQL migrations |
| `src/check_db.py` | Check DB state (empty / needs seed / ready) |
| `src/db_manager.py` | Reset, clear, seed, status |

## Environment Variables

| Variable | Default |
|----------|---------|
| `DB_HOST` | localhost |
| `DB_PORT` | 5432 |
| `DB_NAME` | yugioh_db |
| `DB_USER` | yugioh_user |
| `DB_PASSWORD` | yugioh_password |

## Data Files

- `data/card_list.csv` — Card IDs and names
- `data/cards.csv` — Full card data (from `generate_cards_csv.py`)
- `data/decks.csv` — Deck metadata
- `data/deck_cards.csv` — Deck contents

See [data/README.md](../data/README.md) for CSV formats.

## Tests

```bash
cd scripts
pytest
```
