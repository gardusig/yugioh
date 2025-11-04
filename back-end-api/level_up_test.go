package main

import (
	"fmt"
	"testing"

	"character-api/models"
)

// TestWarriorLevelUp tests level up for Warrior role
func TestWarriorLevelUp(t *testing.T) {
	char := &models.Character{
		Role:         models.RoleWarrior,
		Level:        1,
		Experience:   0,
		HP:           100,
		MaxHP:        100,
		Strength:     100,
		Dexterity:    50,
		Intelligence: 30,
	}

	initialStrength := char.Strength
	initialDexterity := char.Dexterity
	initialIntelligence := char.Intelligence

	// Add enough experience to level up (100 exp for level 1->2)
	leveledUp := char.AddExperience(100)

	if !leveledUp {
		t.Error("Expected character to level up")
	}

	if char.Level != 2 {
		t.Errorf("Expected level 2, got %d", char.Level)
	}

	if char.HP != char.MaxHP {
		t.Errorf("Expected HP to be restored to max (%d), got %d", char.MaxHP, char.HP)
	}

	// Warrior: +80% strength, +20% dexterity
	expectedStrength := int(float64(initialStrength) * 1.80)
	expectedDexterity := int(float64(initialDexterity) * 1.20)
	expectedIntelligence := initialIntelligence // No intelligence boost for warrior

	if char.Strength != expectedStrength {
		t.Errorf("Expected strength %d, got %d", expectedStrength, char.Strength)
	}

	if char.Dexterity != expectedDexterity {
		t.Errorf("Expected dexterity %d, got %d", expectedDexterity, char.Dexterity)
	}

	if char.Intelligence != expectedIntelligence {
		t.Errorf("Expected intelligence %d, got %d (should not change for warrior)", expectedIntelligence, char.Intelligence)
	}
}

// TestThiefLevelUp tests level up for Thief role
func TestThiefLevelUp(t *testing.T) {
	char := &models.Character{
		Role:         models.RoleThief,
		Level:        1,
		Experience:   0,
		HP:           90,
		MaxHP:        90,
		Strength:     60,
		Dexterity:    80,
		Intelligence: 70,
	}

	initialStrength := char.Strength
	initialDexterity := char.Dexterity
	initialIntelligence := char.Intelligence

	// Add enough experience to level up
	leveledUp := char.AddExperience(100)

	if !leveledUp {
		t.Error("Expected character to level up")
	}

	if char.Level != 2 {
		t.Errorf("Expected level 2, got %d", char.Level)
	}

	// Thief: +25% strength, +100% dexterity, +25% intelligence
	expectedStrength := int(float64(initialStrength) * 1.25)
	expectedDexterity := int(float64(initialDexterity) * 2.00) // +100%
	expectedIntelligence := int(float64(initialIntelligence) * 1.25)

	if char.Strength != expectedStrength {
		t.Errorf("Expected strength %d, got %d", expectedStrength, char.Strength)
	}

	if char.Dexterity != expectedDexterity {
		t.Errorf("Expected dexterity %d, got %d", expectedDexterity, char.Dexterity)
	}

	if char.Intelligence != expectedIntelligence {
		t.Errorf("Expected intelligence %d, got %d", expectedIntelligence, char.Intelligence)
	}
}

// TestMageLevelUp tests level up for Mage role
func TestMageLevelUp(t *testing.T) {
	char := &models.Character{
		Role:         models.RoleMage,
		Level:        1,
		Experience:   0,
		HP:           80,
		MaxHP:        80,
		Strength:     40,
		Dexterity:    60,
		Intelligence: 90,
	}

	initialStrength := char.Strength
	initialDexterity := char.Dexterity
	initialIntelligence := char.Intelligence

	// Add enough experience to level up
	leveledUp := char.AddExperience(100)

	if !leveledUp {
		t.Error("Expected character to level up")
	}

	if char.Level != 2 {
		t.Errorf("Expected level 2, got %d", char.Level)
	}

	// Mage: +20% strength, +20% dexterity, +120% intelligence
	expectedStrength := int(float64(initialStrength) * 1.20)
	expectedDexterity := int(float64(initialDexterity) * 1.20)
	expectedIntelligence := int(float64(initialIntelligence) * 2.20) // +120%

	if char.Strength != expectedStrength {
		t.Errorf("Expected strength %d, got %d", expectedStrength, char.Strength)
	}

	if char.Dexterity != expectedDexterity {
		t.Errorf("Expected dexterity %d, got %d", expectedDexterity, char.Dexterity)
	}

	if char.Intelligence != expectedIntelligence {
		t.Errorf("Expected intelligence %d, got %d", expectedIntelligence, char.Intelligence)
	}
}

// TestMultipleLevelUps tests multiple level ups in sequence
func TestMultipleLevelUps(t *testing.T) {
	char := &models.Character{
		Role:         models.RoleWarrior,
		Level:        1,
		Experience:   0,
		HP:           100,
		MaxHP:        100,
		Strength:     100,
		Dexterity:    50,
		Intelligence: 30,
	}

	// Add enough experience for multiple level ups
	// Level 1->2: 100 exp
	// Level 2->3: 150 exp (100 * 1.5)
	// Total: 250 exp
	leveledUp := char.AddExperience(250)

	if !leveledUp {
		t.Error("Expected character to level up")
	}

	if char.Level != 3 {
		t.Errorf("Expected level 3, got %d", char.Level)
	}

	// Stats should have improved twice
	if char.Strength <= 100 {
		t.Errorf("Expected strength to increase from level ups, got %d", char.Strength)
	}

	// MaxHP should have increased (10% per level)
	if char.MaxHP <= 100 {
		t.Errorf("Expected MaxHP to increase, got %d", char.MaxHP)
	}

	if char.HP != char.MaxHP {
		t.Errorf("Expected HP to be at max (%d), got %d", char.MaxHP, char.HP)
	}
}

// TestMaxLevel tests that level cannot exceed 100
func TestMaxLevel(t *testing.T) {
	char := &models.Character{
		Role:         models.RoleWarrior,
		Level:        100,
		Experience:   0,
		HP:           1000,
		MaxHP:        1000,
		Strength:     500,
		Dexterity:    200,
		Intelligence: 100,
	}

	initialLevel := char.Level
	initialStrength := char.Strength

	// Try to add experience at max level
	leveledUp := char.AddExperience(10000)

	if leveledUp {
		t.Error("Expected no level up at max level")
	}

	if char.Level != initialLevel {
		t.Errorf("Expected level to remain %d, got %d", initialLevel, char.Level)
	}

	if char.Strength != initialStrength {
		t.Errorf("Expected strength to remain %d, got %d", initialStrength, char.Strength)
	}
}

// TestExperienceRequired tests exponential experience requirements
func TestExperienceRequired(t *testing.T) {
	tests := []struct {
		level    int
		expected int
	}{
		{1, 100},   // Level 1->2: 100 * 1.5^0 = 100
		{2, 150},   // Level 2->3: 100 * 1.5^1 = 150
		{3, 225},   // Level 3->4: 100 * 1.5^2 = 225
		{10, 5766}, // Level 10->11: 100 * 1.5^9 ≈ 5766
		{100, 0},   // Max level, no exp required
	}

	for _, tt := range tests {
		t.Run(fmt.Sprintf("Level_%d", tt.level), func(t *testing.T) {
			exp := models.GetExperienceRequired(tt.level)
			if tt.level == 100 {
				if exp != 0 {
					t.Errorf("Expected 0 exp for max level, got %d", exp)
				}
			} else {
				// Allow some tolerance for floating point calculations
				if exp < tt.expected-10 || exp > tt.expected+10 {
					t.Errorf("Expected approximately %d exp for level %d, got %d", tt.expected, tt.level, exp)
				}
			}
		})
	}
}

// TestLevelUpHPRestoration tests that HP is restored to max on level up
func TestLevelUpHPRestoration(t *testing.T) {
	char := &models.Character{
		Role:         models.RoleWarrior,
		Level:        1,
		Experience:   0,
		HP:           50, // Less than max
		MaxHP:        100,
		Strength:     100,
		Dexterity:    50,
		Intelligence: 30,
	}

	// Level up
	char.AddExperience(100)

	// HP should be restored to max
	if char.HP != char.MaxHP {
		t.Errorf("Expected HP to be restored to max (%d), got %d", char.MaxHP, char.HP)
	}
}

