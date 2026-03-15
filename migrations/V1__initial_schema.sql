-- Yu-Gi-Oh! Deck Editor - Initial schema
-- Compatible with Flyway naming (V1__description.sql)

CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    image VARCHAR(500),
    type VARCHAR(50) NOT NULL,
    attribute VARCHAR(50),
    race VARCHAR(50),
    level INTEGER NOT NULL DEFAULT 0,
    attack_points INTEGER NOT NULL DEFAULT 0,
    defense_points INTEGER NOT NULL DEFAULT 0,
    cost INTEGER NOT NULL DEFAULT 0,
    rarity VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS decks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    character_name VARCHAR(255),
    archetype VARCHAR(100),
    most_common_type VARCHAR(50),
    max_cost INTEGER NOT NULL DEFAULT 0,
    is_preset BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS deck_cards (
    deck_id INTEGER NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    PRIMARY KEY (deck_id, card_id, position),
    UNIQUE (deck_id, position)
);

CREATE INDEX IF NOT EXISTS idx_deck_cards_deck_id ON deck_cards(deck_id);
CREATE INDEX IF NOT EXISTS idx_deck_cards_card_id ON deck_cards(card_id);
