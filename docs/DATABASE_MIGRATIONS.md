# Database Migrations

Flyway automatically runs SQL files inside `backend/src/main/resources/db/migration/`. At the moment only the schema migration is maintained in Git:

- `V1__initial_schema.sql` — creates `cards`, `decks`, and `deck_cards`

All data seeding is handled manually through `scripts/src/db_manager.py` to avoid long Flyway runtimes and to keep business data outside of migrations.

## Generating / Importing Card Data

If you need a large batch of card inserts:

1. Run the crawler to generate SQL (see `scripts/README.md` for options).
2. Pipe the output directly into `psql`, or copy the rows you want into `db_manager.py` and re-run the `seed` command.

Example (Docker + psql):

```bash
docker-compose run --rm scripts python3 src/crawl_cards.py --start 1 --end 50 > cards.sql
cat cards.sql | docker exec -i yugioh-database psql -U yugioh_user -d yugioh_db
rm cards.sql
```

## Database Schema

The application uses PostgreSQL with the following tables:

### Cards Table
- `id` - Card number (001-900)
- `name` - Card name
- `description` - Card description
- `image` - Card image URL
- `type` - Monster, Spell, or Trap
- `attribute` - For monsters: Dark, Light, Earth, Water, Fire, Wind, Divine
- `race` - For monsters: Dragon, Spellcaster, Warrior, etc.
- `level` - Monster level (0 for Spell/Trap)
- `attack_points` - Attack points
- `defense_points` - Defense points
- `cost` - Card cost
- `rarity` - Common, Rare, Super Rare, Ultra Rare, etc.

### Decks Table
- `id` - Deck ID
- `name` - Deck name
- `description` - Deck description
- `character_name` - Character who uses this deck (e.g., "Weevil Underwood", "Mako Tsunami")
- `archetype` - Deck archetype/style (e.g., "Insect", "Fish", "Dragon")
- `max_cost` - Maximum total cost for the deck
- `is_preset` - Whether this is a preset character deck

### Deck Cards Table
- `deck_id` - Reference to deck
- `card_id` - Reference to card
- `position` - Position in deck (0-39)

