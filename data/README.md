# Data Directory

Static CSV files for seeding the database. **No network required** for first-time setup.

## Files

| File | Description |
|------|--------------|
| `card_list.csv` | Card IDs and names (source for `cards.csv`) |
| `cards.csv` | Full card data — generated from `card_list.csv` by `scripts/src/generate_cards_csv.py` |
| `decks.csv` | Deck metadata (name, description, archetype, etc.) |
| `deck_cards.csv` | Deck contents: `deck_name`, `card_id`, `position` |

## First-Time Setup

The setup runs automatically when you start the stack:

```bash
./podman.sh up --build
```

This will:
1. Run migrations
2. Generate `cards.csv` from `card_list.csv` if missing
3. Seed cards, decks, and deck_cards from the CSV files

## Regenerating cards.csv

If you add cards to `card_list.csv`:

```bash
python3 scripts/src/generate_cards_csv.py
```

To fetch images and full data from YGOPRODECK API for all cards (~1 min, requires network):

```bash
python3 scripts/src/generate_cards_csv.py --fetch-images
```

To fill only missing images in existing `cards.csv` (faster, fetches only for cards without image):

```bash
python3 scripts/src/generate_cards_csv.py --fill-missing-images
```

To verify all image URLs and re-fetch any that are missing or invalid:

```bash
python3 scripts/src/generate_cards_csv.py --verify-images
```

## Manual Seeding

```bash
# Seed from CSV (no network)
./podman.sh run --rm scripts scripts/src/seed_from_csv.py

# Or locally (with DB running):
DB_HOST=localhost python3 scripts/src/seed_from_csv.py
```

## CSV Formats

### cards.csv
```
id,name,type,attribute,race,level,attack_points,defense_points,cost,rarity,description,image
1,Blue-Eyes White Dragon,Normal Monster,LIGHT,Dragon,8,3000,2500,8,Ultra Rare,...
```

### decks.csv
```
name,description,character_name,archetype,max_cost,is_preset
Legend of Blue Eyes,Dragon deck...,Seto Kaiba,Dragon,250,true
```

### deck_cards.csv
```
deck_name,card_id,position
Legend of Blue Eyes,1,1
Legend of Blue Eyes,1,2
...
```
