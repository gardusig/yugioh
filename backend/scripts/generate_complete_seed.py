#!/usr/bin/env python3
"""
Generate complete seed file for all 900 Yu-Gi-Oh! The Sacred Cards
This script creates a template with all 900 card IDs that can be populated with actual data.

Usage:
    python3 scripts/generate_complete_seed.py > database/migrations/003_seed_cards_complete.sql
"""

def escape_sql_string(s):
    """Escape single quotes for SQL"""
    if s is None:
        return "NULL"
    return "'" + s.replace("'", "''") + "'"

def generate_image_url(card_id):
    """Generate placeholder image URL - replace with actual YGOPRODeck card IDs when available"""
    # Using placeholder format - you'll need to map game IDs to actual YGOPRODeck card IDs
    return f"https://images.ygoprodeck.com/images/cards/{card_id}.jpg"

def main():
    print("-- Seed database with ALL Yu-Gi-Oh! The Sacred Cards (001-900)")
    print("-- Based on: https://yugioh.fandom.com/wiki/List_of_Yu-Gi-Oh!_The_Sacred_Cards_cards")
    print("--")
    print("-- This migration seeds all 900 cards from The Sacred Cards game")
    print("-- Each card has: id, name, type, level, attack_points, defense_points, cost, description, image")
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
    print("-- ============================================================================")
    print("-- CARDS 001-900")
    print("-- ============================================================================")
    print("")
    
    # Known cards with their exact data
    known_cards = {
        1: ("Blue-Eyes White Dragon", "Monster", 8, 3000, 2500, 8, 
            "A legendary dragon said to be invincible. Its destructive power is unmatched."),
        35: ("Dark Magician", "Monster", 7, 2500, 2100, 7,
             "The ultimate wizard in terms of attack and defense."),
        82: ("Red-Eyes B. Dragon", "Monster", 7, 2400, 2000, 7,
             "A ferocious dragon with a deadly attack."),
        380: ("Blue-Eyes Ultimate Dragon", "Monster", 12, 4500, 3800, 12,
              "3 \"Blue-Eyes White Dragon\""),
        742: ("Red-Eyes Black Metal Dragon", "Monster", 8, 2800, 2400, 8,
              "Cannot be Normal Summoned/Set. Must first be Special Summoned (from your Deck) by Tributing 1 \"Red-Eyes Black Dragon\" equipped with \"Metalmorph\"."),
    }
    
    # Generate all 900 cards
    for card_id in range(1, 901):
        if card_id in known_cards:
            name, card_type, level, atk, def_val, cost, description = known_cards[card_id]
            desc_str = escape_sql_string(description)
        else:
            # Placeholder for unknown cards - replace with actual data from wiki
            name = f"Card {card_id:03d}"
            card_type = "Monster"  # Default, update based on actual card type
            level = 4  # Default, update based on actual level
            atk = 1500  # Default, update based on actual ATK
            def_val = 1200  # Default, update based on actual DEF
            cost = 4  # Default, update based on actual cost
            desc_str = "NULL"  # Update with actual description
        
        image_url = generate_image_url(card_id)
        
        print(f"-- Card #{card_id:03d}")
        print(f"SELECT insert_sacred_card({card_id}, {escape_sql_string(name)}, {escape_sql_string(card_type)}, {level}, {atk}, {def_val}, {cost}, {desc_str}, {escape_sql_string(image_url)});")
        print("")
    
    print("-- Clean up the function after use")
    print("DROP FUNCTION IF EXISTS insert_sacred_card;")
    print("")
    print("-- NOTE: This file contains placeholders for cards 002-034, 036-081, 083-379, 381-741, 743-900")
    print("-- Please replace placeholder values with actual card data from the wiki page:")
    print("-- https://yugioh.fandom.com/wiki/List_of_Yu-Gi-Oh!_The_Sacred_Cards_cards")

if __name__ == "__main__":
    main()

