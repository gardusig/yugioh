#!/usr/bin/env python3
"""
Script to generate complete seed file for all 900 Yu-Gi-Oh! The Sacred Cards
Based on: https://yugioh.fandom.com/wiki/List_of_Yu-Gi-Oh!_The_Sacred_Cards_cards

Usage:
    python3 scripts/generate_all_cards.py > database/migrations/003_seed_cards_complete.sql

This script generates SQL INSERT statements for all 900 cards.
You can manually populate the cards list or scrape it from the wiki.
"""

import sys

# Card data structure: (id, name, type, level, atk, def, cost, description)
# Type: 'Monster', 'Spell', or 'Trap'
# For Spell/Trap: level=0, atk=0, def=0

cards = [
    # Known cards with their exact data
    (1, "Blue-Eyes White Dragon", "Monster", 8, 3000, 2500, 8, "A legendary dragon said to be invincible. Its destructive power is unmatched."),
    (35, "Dark Magician", "Monster", 7, 2500, 2100, 7, "The ultimate wizard in terms of attack and defense."),
    (82, "Red-Eyes B. Dragon", "Monster", 7, 2400, 2000, 7, "A ferocious dragon with a deadly attack."),
    (380, "Blue-Eyes Ultimate Dragon", "Monster", 12, 4500, 3800, 12, "3 \"Blue-Eyes White Dragon\""),
    (742, "Red-Eyes Black Metal Dragon", "Monster", 8, 2800, 2400, 8, "Cannot be Normal Summoned/Set. Must first be Special Summoned (from your Deck) by Tributing 1 \"Red-Eyes Black Dragon\" equipped with \"Metalmorph\"."),
    # Duplicates
    (865, "Dark Magician", "Monster", 7, 2500, 2100, 7, "The ultimate wizard in terms of attack and defense."),
    (866, "Blue-Eyes Ultimate Dragon", "Monster", 12, 4500, 3800, 12, "3 \"Blue-Eyes White Dragon\""),
    (884, "Red-Eyes Black Metal Dragon", "Monster", 8, 2800, 2400, 8, "Cannot be Normal Summoned/Set. Must first be Special Summoned (from your Deck) by Tributing 1 \"Red-Eyes Black Dragon\" equipped with \"Metalmorph\"."),
    (885, "Red-Eyes B. Dragon", "Monster", 7, 2400, 2000, 7, "A ferocious dragon with a deadly attack."),
    (887, "Blue-Eyes White Dragon", "Monster", 8, 3000, 2500, 8, "A legendary dragon said to be invincible. Its destructive power is unmatched."),
    # TODO: Add all remaining cards (002-034, 036-081, 083-379, 381-741, 743-863, 868-883, 886, 888-900)
    # Format: (id, name, type, level, atk, def, cost, description)
]

def escape_sql_string(s):
    """Escape single quotes for SQL"""
    return s.replace("'", "''")

def generate_image_url(card_id):
    """Generate image URL - using placeholder for now"""
    # In production, you'd map card IDs to actual YGOPRODeck card IDs
    return f"https://images.ygoprodeck.com/images/cards/{card_id}.jpg"

def main():
    print("-- Seed database with ALL Yu-Gi-Oh! The Sacred Cards (001-900)")
    print("-- Based on: https://yugioh.fandom.com/wiki/List_of_Yu-Gi-Oh!_The_Sacred_Cards_cards")
    print("--")
    print("-- Note: Five cards appear twice:")
    print("-- - Blue-Eyes White Dragon (#001 and #887)")
    print("-- - Dark Magician (#035 and #865)")
    print("-- - Red-Eyes B. Dragon (#082 and #885)")
    print("-- - Blue-Eyes Ultimate Dragon (#380 and #866)")
    print("-- - Red-Eyes Black Metal Dragon (#742 and #884)")
    print("")
    print("-- Function to safely insert a card")
    print("CREATE OR REPLACE FUNCTION insert_sacred_card(")
    print("    p_id INTEGER,")
    print("    p_name VARCHAR(255),")
    print("    p_type VARCHAR(50),")
    print("    p_level INTEGER,")
    print("    p_atk INTEGER,")
    print("    p_def INTEGER,")
    print("    p_cost INTEGER,")
    print("    p_description TEXT DEFAULT NULL,")
    print("    p_image VARCHAR(500) DEFAULT NULL")
    print(") RETURNS VOID AS $$")
    print("BEGIN")
    print("    INSERT INTO cards (id, name, type, level, attack_points, defense_points, cost, description, image)")
    print("    VALUES (p_id, p_name, p_type, p_level, p_atk, p_def, p_cost, p_description, p_image)")
    print("    ON CONFLICT (id) DO UPDATE SET")
    print("        name = EXCLUDED.name,")
    print("        type = EXCLUDED.type,")
    print("        level = EXCLUDED.level,")
    print("        attack_points = EXCLUDED.attack_points,")
    print("        defense_points = EXCLUDED.defense_points,")
    print("        cost = EXCLUDED.cost,")
    print("        description = EXCLUDED.description,")
    print("        image = EXCLUDED.image;")
    print("END;")
    print("$$ LANGUAGE plpgsql;")
    print("")
    print("-- Insert all cards")
    print("")
    
    for card_id, name, card_type, level, atk, def_val, cost, description in cards:
        desc = escape_sql_string(description) if description else "NULL"
        image_url = generate_image_url(card_id)
        
        if desc == "NULL":
            desc_str = "NULL"
        else:
            desc_str = f"'{desc}'"
        
        print(f"SELECT insert_sacred_card({card_id}, '{escape_sql_string(name)}', '{card_type}', {level}, {atk}, {def_val}, {cost}, {desc_str}, '{image_url}');")
    
    print("")
    print("-- Clean up the function after use")
    print("DROP FUNCTION IF EXISTS insert_sacred_card;")
    
    # Check if we have all 900 cards
    card_ids = {card[0] for card in cards}
    expected_ids = set(range(1, 901))
    missing = sorted(expected_ids - card_ids)
    
    if missing:
        print("", file=sys.stderr)
        print(f"WARNING: Only {len(cards)} cards defined. Missing {len(missing)} cards.", file=sys.stderr)
        print(f"Missing card IDs: {missing[:20]}{'...' if len(missing) > 20 else ''}", file=sys.stderr)
        print("Please add all remaining cards from the wiki page.", file=sys.stderr)

if __name__ == "__main__":
    main()

