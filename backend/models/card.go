package models

// Card represents a Yu-Gi-Oh card from The Sacred Cards
type Card struct {
	ID           int    `json:"id" db:"id"`
	Name         string `json:"name" db:"name"`
	Description  string `json:"description" db:"description"`
	Image        string `json:"image" db:"image"`
	Type         string `json:"type" db:"type"`         // Monster, Spell, Trap
	Attribute    string `json:"attribute,omitempty" db:"attribute"` // Dark, Light, Earth, Water, Fire, Wind, Divine
	Race         string `json:"race,omitempty" db:"race"`           // Dragon, Spellcaster, Warrior, etc.
	Level        int    `json:"level" db:"level"`       // Monster level (0 for Spell/Trap)
	AttackPoints int    `json:"attack_points" db:"attack_points"`
	DefensePoints int   `json:"defense_points" db:"defense_points"`
	Cost         int    `json:"cost" db:"cost"`
	Rarity       string `json:"rarity,omitempty" db:"rarity"` // Common, Rare, Super Rare, Ultra Rare
}

// DeckSummary represents a deck summary for listing (without full card details)
type DeckSummary struct {
	ID            int    `json:"id" db:"id"`
	Name          string `json:"name" db:"name"`
	Description   string `json:"description" db:"description"`
	CharacterName string `json:"character_name,omitempty" db:"character_name"` // Character who uses this deck
	Archetype     string `json:"archetype,omitempty" db:"archetype"`            // Deck archetype/style
	MaxCost       int    `json:"max_cost" db:"max_cost"`
	TotalCost     int    `json:"total_cost"`
	CardCount     int    `json:"card_count"`
	IsPreset      bool   `json:"is_preset,omitempty" db:"is_preset"`
}

// DeckWithCards represents a deck with full card details
type DeckWithCards struct {
	ID            int    `json:"id" db:"id"`
	Name          string `json:"name" db:"name"`
	Description   string `json:"description" db:"description"`
	CharacterName string `json:"character_name,omitempty" db:"character_name"` // Character who uses this deck
	Archetype     string `json:"archetype,omitempty" db:"archetype"`            // Deck archetype/style
	Cards         []Card `json:"cards"`
	MaxCost       int    `json:"max_cost" db:"max_cost"`
	TotalCost     int    `json:"total_cost"`
	IsPreset      bool   `json:"is_preset,omitempty" db:"is_preset"`
}
