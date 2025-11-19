-- Seed preset character decks from Yu-Gi-Oh! The Sacred Cards
-- These are example decks used by characters in the game

-- Function to create a preset deck
CREATE OR REPLACE FUNCTION create_preset_deck(
    p_name VARCHAR(255),
    p_description TEXT,
    p_archetype VARCHAR(100),
    p_character_name VARCHAR(255),
    p_max_cost INTEGER,
    p_card_ids INTEGER[]
) RETURNS INTEGER AS $$
DECLARE
    v_deck_id INTEGER;
    v_card_id INTEGER;
    v_position INTEGER := 1;
BEGIN
    -- Insert deck
    INSERT INTO decks (name, description, archetype, character_name, max_cost, is_preset)
    VALUES (p_name, p_description, p_archetype, p_character_name, p_max_cost, TRUE)
    RETURNING id INTO v_deck_id;
    
    -- Insert deck cards
    FOREACH v_card_id IN ARRAY p_card_ids
    LOOP
        INSERT INTO deck_cards (deck_id, card_id, position)
        VALUES (v_deck_id, v_card_id, v_position)
        ON CONFLICT (deck_id, position) DO NOTHING;
        v_position := v_position + 1;
    END LOOP;
    
    RETURN v_deck_id;
END;
$$ LANGUAGE plpgsql;

-- Weevil Underwood's Insect Deck
-- Note: Card IDs are placeholders - replace with actual IDs from the game
SELECT create_preset_deck(
    'Weevil''s Insect Swarm',
    'Weevil Underwood''s signature insect-themed deck focused on bug-type monsters and parasitic strategies. This deck emphasizes swarm tactics and using insect-type monsters to overwhelm opponents.',
    'Insect',
    'Weevil Underwood',
    200,
    ARRAY[
        -- Insect monsters (replace with actual card IDs)
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10,  -- Placeholder IDs
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
        -- Spell/Trap support cards
        31, 32, 33, 34, 35, 36, 37, 38, 39, 40
    ]
);

-- Mako Tsunami's Fish Deck
SELECT create_preset_deck(
    'Mako''s Oceanic Assault',
    'Mako Tsunami''s water-themed deck with fish and sea serpent monsters, utilizing field spells like Umi to boost aquatic creatures. This deck focuses on controlling the field with powerful water monsters.',
    'Fish',
    'Mako Tsunami',
    200,
    ARRAY[
        -- Fish and Sea Serpent monsters (replace with actual card IDs)
        41, 42, 43, 44, 45, 46, 47, 48, 49, 50,  -- Placeholder IDs
        51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
        61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
        -- Water support spells/traps
        71, 72, 73, 74, 75, 76, 77, 78, 79, 80
    ]
);

-- Seto Kaiba's Dragon Deck
SELECT create_preset_deck(
    'Kaiba''s Dragon Power',
    'Seto Kaiba''s powerful dragon deck centered around Blue-Eyes White Dragon and high-level dragons. This deck focuses on overwhelming opponents with massive attack power and fusion monsters.',
    'Dragon',
    'Seto Kaiba',
    250,
    ARRAY[
        -- Blue-Eyes White Dragon and other dragons (replace with actual card IDs)
        1,  -- Blue-Eyes White Dragon
        81, 82, 83, 84, 85, 86, 87, 88, 89, 90,  -- Placeholder IDs
        91, 92, 93, 94, 95, 96, 97, 98, 99, 100,
        101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
        -- Dragon support spells/traps
        111, 112, 113, 114, 115, 116, 117, 118, 119, 120
    ]
);

-- Yugi Muto's Spellcaster Deck
SELECT create_preset_deck(
    'Yugi''s Dark Magic',
    'Yugi Muto''s spellcaster deck featuring Dark Magician and powerful spell cards. This deck combines magical monsters with strategic spell support to control the duel.',
    'Spellcaster',
    'Yugi Muto',
    200,
    ARRAY[
        -- Dark Magician and spellcasters (replace with actual card IDs)
        35,  -- Dark Magician
        121, 122, 123, 124, 125, 126, 127, 128, 129, 130,  -- Placeholder IDs
        131, 132, 133, 134, 135, 136, 137, 138, 139, 140,
        141, 142, 143, 144, 145, 146, 147, 148, 149, 150,
        -- Spell support
        151, 152, 153, 154, 155, 156, 157, 158, 159, 160
    ]
);

-- Joey Wheeler's Warrior Deck
SELECT create_preset_deck(
    'Joey''s Warrior Rush',
    'Joey Wheeler''s warrior-themed deck with balanced monsters and combat support. This deck focuses on aggressive play with warrior-type monsters and equip spells.',
    'Warrior',
    'Joey Wheeler',
    180,
    ARRAY[
        -- Warrior monsters (replace with actual card IDs)
        161, 162, 163, 164, 165, 166, 167, 168, 169, 170,  -- Placeholder IDs
        171, 172, 173, 174, 175, 176, 177, 178, 179, 180,
        181, 182, 183, 184, 185, 186, 187, 188, 189, 190,
        -- Warrior support
        191, 192, 193, 194, 195, 196, 197, 198, 199, 200
    ]
);

-- Rex Raptor's Dinosaur Deck
SELECT create_preset_deck(
    'Rex''s Dinosaur Kingdom',
    'Rex Raptor''s dinosaur-themed deck with powerful prehistoric monsters. This deck uses high-attack dinosaur monsters to dominate the field.',
    'Dinosaur',
    'Rex Raptor',
    200,
    ARRAY[
        -- Dinosaur monsters (replace with actual card IDs)
        201, 202, 203, 204, 205, 206, 207, 208, 209, 210,  -- Placeholder IDs
        211, 212, 213, 214, 215, 216, 217, 218, 219, 220,
        221, 222, 223, 224, 225, 226, 227, 228, 229, 230,
        -- Dinosaur support
        231, 232, 233, 234, 235, 236, 237, 238, 239, 240
    ]
);

-- Clean up the function after use
DROP FUNCTION IF EXISTS create_preset_deck;

-- NOTE: All card IDs above are placeholders
-- Replace them with actual card IDs from the 900 cards in The Sacred Cards
-- You can find character-specific cards by searching the wiki or game data

