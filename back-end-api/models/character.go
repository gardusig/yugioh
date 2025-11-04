package models

import "math"

// Character represents a game character (stored in database)
type Character struct {
	ID           string `json:"id"`
	Name         string `json:"name"`
	Role         Role   `json:"role"`
	Level        int    `json:"level"`
	Experience   int    `json:"experience"`
	HP           int    `json:"hp"`
	MaxHP        int    `json:"max_hp"`
	Strength     int    `json:"strength"`
	Dexterity    int    `json:"dexterity"`
	Intelligence int    `json:"intelligence"`
}

// CharacterResponse represents a character with calculated modifiers for API responses
type CharacterResponse struct {
	ID                     string  `json:"id"`
	Name                   string  `json:"name"`
	Role                   Role    `json:"role"`
	Level                  int     `json:"level"`
	Experience             int     `json:"experience"`
	HP                     int     `json:"hp"`
	MaxHP                  int     `json:"max_hp"`
	Strength               int     `json:"strength"`
	Dexterity              int     `json:"dexterity"`
	Intelligence           int     `json:"intelligence"`
	Status                 string  `json:"status"` // "alive" or "dead"
	StrengthMultiplier     float64 `json:"strength_multiplier"`
	DexterityMultiplier    float64 `json:"dexterity_multiplier"`
	IntelligenceMultiplier float64 `json:"intelligence_multiplier"`
	SpeedModifier          float64 `json:"speed_modifier"`
}

// GetStatus returns "alive" if HP > 0, otherwise "dead"
func (c *Character) GetStatus() string {
	if c.HP > 0 {
		return "alive"
	}
	return "dead"
}

// ToResponse converts a Character to CharacterResponse with level-up multipliers
func (c *Character) ToResponse() *CharacterResponse {
	strMult, dexMult, intMult := GetLevelUpMultipliers(c.Role)
	speedMod := GetSpeedModifier(c.Role, c.Dexterity, c.Strength, c.Intelligence)
	return &CharacterResponse{
		ID:                     c.ID,
		Name:                   c.Name,
		Role:                   c.Role,
		Level:                  c.Level,
		Experience:             c.Experience,
		HP:                     c.HP,
		MaxHP:                  c.MaxHP,
		Strength:               c.Strength,
		Dexterity:              c.Dexterity,
		Intelligence:           c.Intelligence,
		Status:                 c.GetStatus(),
		StrengthMultiplier:     strMult,
		DexterityMultiplier:    dexMult,
		IntelligenceMultiplier: intMult,
		SpeedModifier:          speedMod,
	}
}

// GetExperienceRequired returns the experience needed to reach the next level
func GetExperienceRequired(level int) int {
	if level >= 100 {
		return 0 // Max level reached
	}
	// Exponential growth: base * (1.5 ^ (level - 1))
	// Base experience for level 1->2 is 100
	base := 100.0
	multiplier := 1.5
	exp := base * math.Pow(multiplier, float64(level-1))
	return int(exp)
}

// AddExperience adds experience and returns true if level up occurred
func (c *Character) AddExperience(amount int) bool {
	if c.Level >= 100 {
		return false // Max level reached
	}

	c.Experience += amount
	leveledUp := false

	for c.Level < 100 {
		expRequired := GetExperienceRequired(c.Level)
		if c.Experience >= expRequired {
			c.Experience -= expRequired
			c.Level++
			leveledUp = true
			// Restore HP to max on level up
			c.HP = c.MaxHP
			// Apply stat improvements based on role
			c.applyLevelUpStats()
		} else {
			break
		}
	}

	return leveledUp
}

// applyLevelUpStats applies stat improvements based on role
func (c *Character) applyLevelUpStats() {
	strMult, dexMult, intMult := GetLevelUpMultipliers(c.Role)

	// Apply multipliers to current stats
	c.Strength = int(float64(c.Strength) * (1.0 + strMult))
	c.Dexterity = int(float64(c.Dexterity) * (1.0 + dexMult))
	c.Intelligence = int(float64(c.Intelligence) * (1.0 + intMult))

	// Increase MaxHP on level up (10% increase)
	c.MaxHP = int(float64(c.MaxHP) * 1.1)
	c.HP = c.MaxHP // Restore to full
}
