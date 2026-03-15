# Database Migrations

Migrations are run by the **scripts** service using Flyway-style SQL files in `scripts/migrations/`:

- `V1__initial_schema.sql` — creates `cards`, `decks`, and `deck_cards`

The scripts service runs at startup (`./podman.sh up`) and executes migrations before the backend starts. All data seeding is from `data/*.csv` via `scripts/src/seed_from_csv.py`.

## Adding Card Data

Edit `data/card_list.csv` to add cards, then run:

```bash
python3 scripts/src/generate_cards_csv.py
python3 scripts/src/seed_from_csv.py
```

## Database Schema

The application uses PostgreSQL with the following tables:

### Cards Table
- `id` - Card ID
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
- `character_name` - Deck owner (optional)
- `archetype` - Deck archetype/style (e.g., "Insect", "Fish", "Dragon")
- `max_cost` - Maximum total cost for the deck
- `is_preset` - Whether this is a preset deck

### Deck Cards Table
- `deck_id` - Reference to deck
- `card_id` - Reference to card
- `position` - Position in deck (0-39)

