package main

import (
	"fmt"
	"sync"

	"neo-submission/back-end-api/models"
)

// Database represents the in-memory database for characters and battles
type Database struct {
	characters map[string]*models.Character
	battles    []*models.Battle
	mu         sync.RWMutex
	nextID     int
	battleID   int
}

// NewDatabase creates a new database instance
func NewDatabase() *Database {
	return &Database{
		characters: make(map[string]*models.Character),
		battles:    make([]*models.Battle, 0),
		nextID:     1,
		battleID:   1,
	}
}

// Create adds a new character to the database
func (db *Database) Create(char *models.Character) (*models.Character, error) {
	db.mu.Lock()
	defer db.mu.Unlock()

	// Generate ID if not provided
	if char.ID == "" {
		char.ID = fmt.Sprintf("%d", db.nextID)
		db.nextID++
	}

	// Check if ID already exists
	if _, exists := db.characters[char.ID]; exists {
		return nil, fmt.Errorf("character with ID %s already exists", char.ID)
	}

	// Store character (without modifiers)
	db.characters[char.ID] = char

	// Return a copy to avoid external mutations
	return db.copyCharacter(char), nil
}

// Get retrieves a character by ID
func (db *Database) Get(id string) (*models.Character, error) {
	db.mu.RLock()
	defer db.mu.RUnlock()

	char, exists := db.characters[id]
	if !exists {
		return nil, fmt.Errorf("character with ID %s not found", id)
	}

	return db.copyCharacter(char), nil
}

// GetAll retrieves all characters
func (db *Database) GetAll() []*models.Character {
	db.mu.RLock()
	defer db.mu.RUnlock()

	characters := make([]*models.Character, 0, len(db.characters))
	for _, char := range db.characters {
		characters = append(characters, db.copyCharacter(char))
	}

	return characters
}

// GetAllPaginated retrieves characters with pagination
func (db *Database) GetAllPaginated(page, limit int) ([]*models.Character, int) {
	db.mu.RLock()
	defer db.mu.RUnlock()

	allCharacters := make([]*models.Character, 0, len(db.characters))
	for _, char := range db.characters {
		allCharacters = append(allCharacters, db.copyCharacter(char))
	}

	total := len(allCharacters)

	// Calculate pagination
	start := (page - 1) * limit
	if start < 0 {
		start = 0
	}
	if start >= total {
		return []*models.Character{}, total
	}

	end := start + limit
	if end > total {
		end = total
	}

	return allCharacters[start:end], total
}

// Update updates an existing character
func (db *Database) Update(id string, char *models.Character) (*models.Character, error) {
	db.mu.Lock()
	defer db.mu.Unlock()

	if _, exists := db.characters[id]; !exists {
		return nil, fmt.Errorf("character with ID %s not found", id)
	}

	// Update fields (without modifiers)
	char.ID = id
	db.characters[id] = char

	return db.copyCharacter(char), nil
}

// Delete removes a character from the database
func (db *Database) Delete(id string) error {
	db.mu.Lock()
	defer db.mu.Unlock()

	if _, exists := db.characters[id]; !exists {
		return fmt.Errorf("character with ID %s not found", id)
	}

	delete(db.characters, id)
	return nil
}

// AddExperience adds experience to a character and handles level ups
func (db *Database) AddExperience(id string, amount int) (bool, error) {
	db.mu.Lock()
	defer db.mu.Unlock()

	char, exists := db.characters[id]
	if !exists {
		return false, fmt.Errorf("character with ID %s not found", id)
	}

	leveledUp := char.AddExperience(amount)
	return leveledUp, nil
}

// DealDamage deals damage to a character and returns if they died
func (db *Database) DealDamage(id string, damage int) (bool, error) {
	db.mu.Lock()
	defer db.mu.Unlock()

	char, exists := db.characters[id]
	if !exists {
		return false, fmt.Errorf("character with ID %s not found", id)
	}

	char.HP -= damage
	if char.HP < 0 {
		char.HP = 0
	}

	return char.HP == 0, nil
}

// RecordBattle records a battle in the history
func (db *Database) RecordBattle(battle *models.Battle) (*models.Battle, error) {
	db.mu.Lock()
	defer db.mu.Unlock()

	if battle.ID == "" {
		battle.ID = fmt.Sprintf("battle-%d", db.battleID)
		db.battleID++
	}

	// Create a copy
	battleCopy := *battle
	db.battles = append(db.battles, &battleCopy)

	return &battleCopy, nil
}

// GetBattlesPaginated retrieves battles with pagination
func (db *Database) GetBattlesPaginated(page, limit int) ([]*models.Battle, int) {
	db.mu.RLock()
	defer db.mu.RUnlock()

	total := len(db.battles)

	// Calculate pagination
	start := (page - 1) * limit
	if start < 0 {
		start = 0
	}
	if start >= total {
		return []*models.Battle{}, total
	}

	end := start + limit
	if end > total {
		end = total
	}

	// Return battles in reverse chronological order (newest first)
	battles := make([]*models.Battle, end-start)
	for i := start; i < end; i++ {
		battles[end-1-i] = db.battles[total-1-i]
	}

	return battles, total
}

// GetBattlesForCharacter retrieves all battles for a specific character
func (db *Database) GetBattlesForCharacter(characterID string) []*models.Battle {
	db.mu.RLock()
	defer db.mu.RUnlock()

	battles := make([]*models.Battle, 0)
	for _, battle := range db.battles {
		if battle.Character1ID == characterID || battle.Character2ID == characterID {
			battles = append(battles, battle)
		}
	}

	// Return in reverse chronological order
	result := make([]*models.Battle, len(battles))
	for i, battle := range battles {
		result[len(battles)-1-i] = battle
	}

	return result
}

// GetAllPaginatedWithFilters retrieves characters with pagination and filters
func (db *Database) GetAllPaginatedWithFilters(page, limit int, roleFilter, statusFilter string) ([]*models.Character, int) {
	db.mu.RLock()
	defer db.mu.RUnlock()

	allCharacters := make([]*models.Character, 0, len(db.characters))
	for _, char := range db.characters {
		// Apply filters
		if roleFilter != "" && string(char.Role) != roleFilter {
			continue
		}
		if statusFilter != "" {
			status := char.GetStatus()
			if status != statusFilter {
				continue
			}
		}
		allCharacters = append(allCharacters, db.copyCharacter(char))
	}

	total := len(allCharacters)

	// Calculate pagination
	start := (page - 1) * limit
	if start < 0 {
		start = 0
	}
	if start >= total {
		return []*models.Character{}, total
	}

	end := start + limit
	if end > total {
		end = total
	}

	return allCharacters[start:end], total
}

// copyCharacter creates a deep copy of a character
func (db *Database) copyCharacter(char *models.Character) *models.Character {
	return &models.Character{
		ID:           char.ID,
		Name:         char.Name,
		Role:         char.Role,
		Level:        char.Level,
		Experience:   char.Experience,
		HP:           char.HP,
		MaxHP:        char.MaxHP,
		Strength:     char.Strength,
		Dexterity:    char.Dexterity,
		Intelligence: char.Intelligence,
	}
}
