# Database Maintenance & Sample Data

The scripts service runs **migrations** first (create/update tables), then **seed** from `data/*.csv`. All DB control is via `scripts/src/db_manager.py` or `scripts/src/setup.py`.

## Order: reset → migrate → seed

1. **reset-db** — Drop and recreate the schema (clean everything). No tables left.
2. **migrate** — Run SQL migrations (create/update tables). No data.
3. **seed** — Load data from `data/*.csv` (cards, decks, deck_cards).

Use **reset-and-seed** to do all three in one go.

## Step-by-step: full clean setup

```bash
# 1. Start PostgreSQL (if not already running)
docker compose up -d database

# 2. Reset, run migrations, and seed (one command)
docker compose run --rm scripts scripts/src/db_manager.py reset-and-seed

# 3. Check counts and data (numbers + validation queries, alerts if issues)
docker compose run --rm scripts scripts/src/check_db.py
```

*With Podman: use `podman compose -f docker-compose.yml` instead of `docker compose`.*

Or run the steps separately:

```bash
docker compose run --rm scripts scripts/src/db_manager.py reset-db
docker compose run --rm scripts scripts/src/db_manager.py migrate
docker compose run --rm scripts scripts/src/db_manager.py seed
```

## Commands

> Run `docker compose up -d database` first so scripts can connect to Postgres. With Podman, use `podman compose -f docker-compose.yml up -d database`.

| Goal | Command |
|------|---------|
| **Clean everything and reseed** (reset → migrate → seed) | `docker compose run --rm scripts scripts/src/db_manager.py reset-and-seed` |
| **Clean schema only** (drop schema; run migrate next) | `docker compose run --rm scripts scripts/src/db_manager.py reset-db` |
| **Run migrations only** (create/update tables) | `docker compose run --rm scripts scripts/src/db_manager.py migrate` |
| **Seed from CSV only** | `docker compose run --rm scripts scripts/src/db_manager.py seed` |
| **Counts + validation** (cards/decks numbers, missing data alerts) | `docker compose run --rm scripts scripts/src/check_db.py` |
| Table counts only | `docker compose run --rm scripts scripts/src/db_manager.py status` |
| Truncate all tables (keep schema) | `docker compose run --rm scripts scripts/src/db_manager.py clear-all` |
| Truncate one table | `docker compose run --rm scripts scripts/src/db_manager.py clear-table cards` |

**check_db** prints: card/deck/deck_cards counts, card ID range, expected rows from `data/cards.csv` (if present), and validation (missing name/type, missing image, broken deck_cards references). It alerts when counts or data don’t match expectations.

To add more cards, edit `data/card_list.csv`, run `generate_cards_csv.py`, then `seed`. See `data/README.md`.

