# Database Maintenance & Sample Data

The scripts service runs migrations (`scripts/migrations/V1__initial_schema.sql`) at startup. All data management happens through `scripts/src/db_manager.py` or `scripts/src/setup.py`. This keeps migrations fast and lets you decide when/how to populate the database.

## Step-by-step: Reset DB and Reseed

```bash
# 1. Start PostgreSQL only (if it is not already running)
./podman.sh up -d database

# 2. Reset DB and reseed from data/*.csv
./podman.sh run --rm scripts scripts/src/db_manager.py reset-and-seed

# 3. Verify
./podman.sh run --rm scripts scripts/src/db_manager.py status
```

## Useful Commands

> ℹ️ Run `./podman.sh up -d database` first so the scripts can connect to Postgres.

| Goal | Command |
|------|---------|
| **Reset DB and reseed** (full clean slate from `data/*.csv`) | `./podman.sh run --rm scripts scripts/src/db_manager.py reset-and-seed` |
| Drop & recreate entire schema (removes everything) | `./podman.sh run --rm scripts scripts/src/db_manager.py reset-db` |
| Clear all rows but keep tables | `./podman.sh run --rm scripts scripts/src/db_manager.py clear-all` |
| Clear a single table | `./podman.sh run --rm scripts scripts/src/db_manager.py clear-table cards` (or `decks`, `deck_cards`) |
| Seed from `data/*.csv` | `./podman.sh run --rm scripts scripts/src/db_manager.py seed` |

To add more cards, edit `data/card_list.csv` and run `generate_cards_csv.py` then `seed_from_csv.py`. See `data/README.md`.

