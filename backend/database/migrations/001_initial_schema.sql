-- Yu-Gi-Oh! The Sacred Cards Database Schema
-- Simplified schema focusing on cards and decks only

-- Create cards table
-- All 900 cards from Yu-Gi-Oh! The Sacred Cards (001-900)
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY,  -- Card number from game (001-900)
    name VARCHAR(255) NOT NULL,
    description TEXT,
    image VARCHAR(500),
    type VARCHAR(50) NOT NULL,  -- Monster, Spell, Trap
    attribute VARCHAR(50),      -- For monsters: Dark, Light, Earth, Water, Fire, Wind, Divine
    race VARCHAR(50),          -- For monsters: Dragon, Spellcaster, Warrior, etc.
    level INTEGER DEFAULT 0,   -- Monster level (0 for Spell/Trap)
    attack_points INTEGER NOT NULL DEFAULT 0,
    defense_points INTEGER NOT NULL DEFAULT 0,
    cost INTEGER NOT NULL DEFAULT 0,
    rarity VARCHAR(50),        -- Common, Rare, Super Rare, Ultra Rare, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create decks table
-- Character decks and example decks from The Sacred Cards
CREATE TABLE IF NOT EXISTS decks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    character_name VARCHAR(255),  -- Character who uses this deck (e.g., "Weevil Underwood", "Mako Tsunami")
    archetype VARCHAR(100),       -- Deck archetype/style (e.g., "Insect", "Fish", "Dragon")
    max_cost INTEGER NOT NULL DEFAULT 0,
    is_preset BOOLEAN DEFAULT FALSE,  -- True for character preset decks
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create deck_cards junction table (many-to-many relationship)
-- Links decks to their 40 cards with position
CREATE TABLE IF NOT EXISTS deck_cards (
    deck_id INTEGER NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    PRIMARY KEY (deck_id, card_id, position),
    CONSTRAINT unique_deck_card_position UNIQUE (deck_id, position)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name);
CREATE INDEX IF NOT EXISTS idx_cards_type ON cards(type);
CREATE INDEX IF NOT EXISTS idx_cards_level ON cards(level);
CREATE INDEX IF NOT EXISTS idx_cards_attribute ON cards(attribute);
CREATE INDEX IF NOT EXISTS idx_cards_race ON cards(race);
CREATE INDEX IF NOT EXISTS idx_decks_character_name ON decks(character_name);
CREATE INDEX IF NOT EXISTS idx_decks_archetype ON decks(archetype);
CREATE INDEX IF NOT EXISTS idx_decks_is_preset ON decks(is_preset);
CREATE INDEX IF NOT EXISTS idx_deck_cards_deck_id ON deck_cards(deck_id);
CREATE INDEX IF NOT EXISTS idx_deck_cards_card_id ON deck_cards(card_id);
