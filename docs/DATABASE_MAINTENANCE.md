# Database Maintenance & Sample Data

Flyway now creates only the schema (`V1__initial_schema.sql`). All data management happens through `scripts/src/db_manager.py`. This keeps migrations fast and lets you decide when/how to populate the database.

## Step-by-step: Clear DB and Load the First 10 Cards (001-010)

```bash
# 1. Start PostgreSQL only (if it is not already running)
docker-compose up -d database

# 2. Clear all data but keep the tables
docker-compose run --rm scripts python3 src/db_manager.py clear-all

# 3. Seed the first 10 iconic cards
docker-compose run --rm scripts python3 src/db_manager.py seed --cards
```

## Useful Commands

> ℹ️ Run `docker-compose up -d database` first so the scripts can connect to Postgres.

| Goal | Command |
|------|---------|
| Drop & recreate entire schema (removes everything) | `docker-compose run --rm scripts python3 src/db_manager.py reset-db` |
| Clear all rows but keep tables | `docker-compose run --rm scripts python3 src/db_manager.py clear-all` |
| Clear a single table | `docker-compose run --rm scripts python3 src/db_manager.py clear-table cards` (or `decks`, `deck_cards`) |
| Seed the sample 10 iconic cards + 2 decks | `docker-compose run --rm scripts python3 src/db_manager.py seed` |
| Seed only cards | `docker-compose run --rm scripts python3 src/db_manager.py seed --cards` |
| Seed only decks (expects matching card IDs to exist) | `docker-compose run --rm scripts python3 src/db_manager.py seed --decks` |

To generate larger SQL imports (e.g., all 900 cards), run `crawl_cards.py` to produce an export, then pipe it into `psql` or adapt the output inside `db_manager.py`. See `scripts/README.md` for details.

