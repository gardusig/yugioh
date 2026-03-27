# Database Migrations

Flyway-style SQL migrations live here (project root). They are run by the **scripts** service, not the backend.

- **V1__initial_schema.sql** — Creates `cards`, `decks`, and `deck_cards`
- **V2__** / **V3__** — Schema updates

Run from project root or via the scripts container:

```bash
docker compose run --rm scripts scripts/src/run_migrations.py
```

*With Podman: `podman compose -f docker-compose.yml run --rm scripts ...`.*

See [docs/DATABASE_MIGRATIONS.md](../docs/DATABASE_MIGRATIONS.md) for details.
