# Scripts — Data Management

Python tools for database setup and seeding. **Stack:** Python 3.11, psycopg2.

## Focus

- **Migrations** (schema) then **seed** from `data/*.csv` (no network required)
- DB maintenance: reset, migrate, seed, check (counts + validation)

## First-Time Setup

From the **project root**:

```bash
docker compose up --build
```

*With Podman: `podman compose -f docker-compose.yml up --build`.*

The `scripts` service runs **migrations** then **seed** before the backend starts.

**Run on-demand (order: reset → migrate → seed):**

```bash
# Full clean setup (reset schema → migrations → seed)
docker compose run --rm scripts scripts/src/db_manager.py reset-and-seed

# Or step by step:
docker compose run --rm scripts scripts/src/db_manager.py reset-db   # clean schema
docker compose run --rm scripts scripts/src/db_manager.py migrate    # run migrations
docker compose run --rm scripts scripts/src/db_manager.py seed       # load data/*.csv

# Counts + validation (alerts if data missing or mismatched)
docker compose run --rm scripts scripts/src/check_db.py
```

*With Podman: `podman compose -f docker-compose.yml run --rm scripts ...`.*

**One-off setup (if DB empty):** `docker compose run --rm scripts` runs `setup.py` (migrate + seed when needed).

## Dockerfile

Single file, two stages (build from **repo root**):

| Stage | Purpose |
|-------|---------|
| `test` | Unit tests: `docker build -f scripts/Dockerfile --target test .` |
| default | Run scripts (migrations + seed): used by `docker compose` for the scripts service |

## Main Scripts

| Script | Purpose |
|--------|---------|
| `src/db_manager.py` | **reset-db** (clean schema), **migrate** (run SQL), **seed** (load CSV), **reset-and-seed** (all three), status, clear-all, clear-table |
| `src/setup.py` | If DB empty: run migrations then seed; if tables empty: seed only |
| `src/seed_from_csv.py` | Seed from `data/*.csv` (cards, decks, deck_cards) |
| `src/run_migrations.py` | Run SQL migrations from project root `migrations/` |
| `src/check_db.py` | Exit 0/1/2 (empty / needs seed / ready); when ready, prints counts and validation alerts |
| `src/generate_cards_csv.py` | Generate `data/cards.csv` (`--fetch-images`, `--fill-missing-images`, `--verify-images`) |

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
