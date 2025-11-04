package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"character-api/models"
)

// TestRecordBattle tests recording a battle
func TestRecordBattle(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	// Create two characters for battle
	char1 := &models.Character{
		Name:         "Warrior1",
		Role:         models.RoleWarrior,
		Level:        1,
		HP:           100,
		MaxHP:        100,
		Strength:     50,
		Dexterity:    30,
		Intelligence: 20,
	}
	char2 := &models.Character{
		Name:         "Thief1",
		Role:         models.RoleThief,
		Level:        1,
		HP:           80,
		MaxHP:        80,
		Strength:     30,
		Dexterity:    50,
		Intelligence: 40,
	}

	char1, _ = db.Create(char1)
	char2, _ = db.Create(char2)

	battle := models.Battle{
		Character1ID:     char1.ID,
		Character2ID:     char2.ID,
		WinnerID:         char1.ID,
		LoserID:          char2.ID,
		BattleLog:        []string{"Warrior1 attacks", "Thief1 is defeated"},
		ExperienceGained: 10,
		LeveledUp:        false,
		Timestamp:        time.Now(),
	}

	battleJSON, _ := json.Marshal(battle)
	req := httptest.NewRequest("POST", "/battles", bytes.NewBuffer(battleJSON))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusCreated {
		t.Errorf("Expected status %d, got %d", http.StatusCreated, w.Code)
	}

	var response models.BattleResponse
	json.NewDecoder(w.Body).Decode(&response)

	if response.Character1ID != char1.ID {
		t.Errorf("Expected Character1ID %s, got %s", char1.ID, response.Character1ID)
	}
	if response.WinnerID != char1.ID {
		t.Errorf("Expected WinnerID %s, got %s", char1.ID, response.WinnerID)
	}
}

// TestGetBattles tests getting battles with pagination
func TestGetBattles(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	// Create characters and battles
	char1, _ := db.Create(&models.Character{Name: "Char1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	char2, _ := db.Create(&models.Character{Name: "Char2", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})

	// Record multiple battles
	for i := 0; i < 5; i++ {
		battle := &models.Battle{
			Character1ID:     char1.ID,
			Character2ID:     char2.ID,
			WinnerID:         char1.ID,
			LoserID:          char2.ID,
			BattleLog:        []string{"Battle log"},
			ExperienceGained: 10,
			Timestamp:        time.Now(),
		}
		db.RecordBattle(battle)
	}

	req := httptest.NewRequest("GET", "/battles?page=1&limit=3", nil)
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var response map[string]interface{}
	json.NewDecoder(w.Body).Decode(&response)

	battles, ok := response["battles"].([]interface{})
	if !ok {
		t.Fatal("Expected battles array")
	}

	if len(battles) != 3 {
		t.Errorf("Expected 3 battles, got %d", len(battles))
	}
}

// TestGetCharacterBattles tests getting battles for a specific character
func TestGetCharacterBattles(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	char1, _ := db.Create(&models.Character{Name: "Char1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	char2, _ := db.Create(&models.Character{Name: "Char2", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})
	char3, _ := db.Create(&models.Character{Name: "Char3", Role: models.RoleMage, Level: 1, HP: 70, MaxHP: 70, Strength: 20, Dexterity: 30, Intelligence: 60})

	// Record battles involving char1
	battle1 := &models.Battle{
		Character1ID:     char1.ID,
		Character2ID:     char2.ID,
		WinnerID:         char1.ID,
		LoserID:          char2.ID,
		BattleLog:        []string{"Battle 1"},
		ExperienceGained: 10,
		Timestamp:        time.Now(),
	}
	battle2 := &models.Battle{
		Character1ID:     char3.ID,
		Character2ID:     char1.ID,
		WinnerID:         char3.ID,
		LoserID:          char1.ID,
		BattleLog:        []string{"Battle 2"},
		ExperienceGained: 10,
		Timestamp:        time.Now(),
	}
	// Battle not involving char1
	battle3 := &models.Battle{
		Character1ID:     char2.ID,
		Character2ID:     char3.ID,
		WinnerID:         char2.ID,
		LoserID:          char3.ID,
		BattleLog:        []string{"Battle 3"},
		ExperienceGained: 10,
		Timestamp:        time.Now(),
	}

	db.RecordBattle(battle1)
	db.RecordBattle(battle2)
	db.RecordBattle(battle3)

	req := httptest.NewRequest("GET", "/characters/"+char1.ID+"/battles", nil)
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var response map[string]interface{}
	json.NewDecoder(w.Body).Decode(&response)

	battles, ok := response["battles"].([]interface{})
	if !ok {
		t.Fatal("Expected battles array")
	}

	if len(battles) != 2 {
		t.Errorf("Expected 2 battles for char1, got %d", len(battles))
	}
}

// TestGetAllPaginatedWithFilters tests filtering characters by role and status
func TestGetAllPaginatedWithFilters(t *testing.T) {
	db := NewDatabase()

	// Create characters with different roles and statuses
	warrior1, _ := db.Create(&models.Character{Name: "Warrior1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	warrior2, _ := db.Create(&models.Character{Name: "Warrior2", Role: models.RoleWarrior, Level: 1, HP: 0, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	_, _ = db.Create(&models.Character{Name: "Thief1", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})
	_, _ = db.Create(&models.Character{Name: "Mage1", Role: models.RoleMage, Level: 1, HP: 70, MaxHP: 70, Strength: 20, Dexterity: 30, Intelligence: 60})

	// Test filter by role
	characters, total := db.GetAllPaginatedWithFilters(1, 10, "Warrior", "")
	if total != 2 {
		t.Errorf("Expected 2 warriors, got %d", total)
	}
	if len(characters) != 2 {
		t.Errorf("Expected 2 warriors in result, got %d", len(characters))
	}
	for _, char := range characters {
		if char.Role != models.RoleWarrior {
			t.Errorf("Expected Warrior role, got %s", char.Role)
		}
	}

	// Test filter by status
	characters, total = db.GetAllPaginatedWithFilters(1, 10, "", "alive")
	if total != 3 {
		t.Errorf("Expected 3 alive characters, got %d", total)
	}
	for _, char := range characters {
		if char.HP <= 0 {
			t.Errorf("Expected alive character, got HP %d", char.HP)
		}
	}

	characters, total = db.GetAllPaginatedWithFilters(1, 10, "", "dead")
	if total != 1 {
		t.Errorf("Expected 1 dead character, got %d", total)
	}
	if characters[0].ID != warrior2.ID {
		t.Errorf("Expected dead character to be warrior2")
	}

	// Test filter by both role and status
	characters, total = db.GetAllPaginatedWithFilters(1, 10, "Warrior", "alive")
	if total != 1 {
		t.Errorf("Expected 1 alive warrior, got %d", total)
	}
	if characters[0].ID != warrior1.ID {
		t.Errorf("Expected alive warrior to be warrior1")
	}
}

// TestGetSpeedModifier tests speed modifier calculation
func TestGetSpeedModifier(t *testing.T) {
	// Test Warrior: 60% dexterity + 20% intelligence
	dex := 60
	int := 40
	expected := float64(dex)*0.60 + float64(int)*0.20
	result := models.GetSpeedModifier(models.RoleWarrior, dex, 50, int)
	if result != expected {
		t.Errorf("Expected Warrior speed modifier %f, got %f", expected, result)
	}

	// Test Thief: 80% dexterity
	dex = 85
	expected = float64(dex) * 0.80
	result = models.GetSpeedModifier(models.RoleThief, dex, 60, 70)
	if result != expected {
		t.Errorf("Expected Thief speed modifier %f, got %f", expected, result)
	}

	// Test Mage: 40% dexterity + 10% strength
	dex = 60
	str := 40
	expected = float64(dex)*0.40 + float64(str)*0.10
	result = models.GetSpeedModifier(models.RoleMage, dex, str, 90)
	if result != expected {
		t.Errorf("Expected Mage speed modifier %f, got %f", expected, result)
	}
}

// TestDealDamage tests damage dealing
func TestDealDamage(t *testing.T) {
	db := NewDatabase()

	char, _ := db.Create(&models.Character{
		Name:         "TestChar",
		Role:         models.RoleWarrior,
		Level:        1,
		HP:           100,
		MaxHP:        100,
		Strength:     50,
		Dexterity:    30,
		Intelligence: 20,
	})

	// Deal damage
	died, err := db.DealDamage(char.ID, 30)
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if died {
		t.Error("Character should not be dead after 30 damage")
	}

	updated, _ := db.Get(char.ID)
	if updated.HP != 70 {
		t.Errorf("Expected HP 70, got %d", updated.HP)
	}

	// Deal more damage to kill
	died, err = db.DealDamage(char.ID, 80)
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if !died {
		t.Error("Character should be dead")
	}

	updated, _ = db.Get(char.ID)
	if updated.HP != 0 {
		t.Errorf("Expected HP 0, got %d", updated.HP)
	}
}

// TestDealDamageNotFound tests dealing damage to non-existent character
func TestDealDamageNotFound(t *testing.T) {
	db := NewDatabase()

	_, err := db.DealDamage("nonexistent", 10)
	if err == nil {
		t.Error("Expected error for non-existent character")
	}
}

// TestRecordBattleWithTimestamp tests battle recording with timestamp
func TestRecordBattleWithTimestamp(t *testing.T) {
	db := NewDatabase()

	char1, _ := db.Create(&models.Character{Name: "Char1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	char2, _ := db.Create(&models.Character{Name: "Char2", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})

	timestamp := time.Now()
	battle := &models.Battle{
		Character1ID:     char1.ID,
		Character2ID:     char2.ID,
		WinnerID:         char1.ID,
		LoserID:          char2.ID,
		BattleLog:        []string{"Test log"},
		ExperienceGained: 10,
		Timestamp:        timestamp,
	}

	recorded, err := db.RecordBattle(battle)
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}

	if recorded.ID == "" {
		t.Error("Expected battle to have an ID")
	}

	if recorded.Timestamp.IsZero() {
		t.Error("Expected battle to have a timestamp")
	}
}

// TestGetBattlesPaginated tests pagination of battles
func TestGetBattlesPaginated(t *testing.T) {
	db := NewDatabase()

	char1, _ := db.Create(&models.Character{Name: "Char1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	char2, _ := db.Create(&models.Character{Name: "Char2", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})

	// Create 10 battles
	for i := 0; i < 10; i++ {
		battle := &models.Battle{
			Character1ID:     char1.ID,
			Character2ID:     char2.ID,
			WinnerID:         char1.ID,
			LoserID:          char2.ID,
			BattleLog:        []string{"Battle"},
			ExperienceGained: 10,
			Timestamp:        time.Now(),
		}
		db.RecordBattle(battle)
	}

	// Test first page
	battles, total := db.GetBattlesPaginated(1, 5)
	if total != 10 {
		t.Errorf("Expected total 10 battles, got %d", total)
	}
	if len(battles) != 5 {
		t.Errorf("Expected 5 battles on first page, got %d", len(battles))
	}

	// Test second page
	battles, total = db.GetBattlesPaginated(2, 5)
	if len(battles) != 5 {
		t.Errorf("Expected 5 battles on second page, got %d", len(battles))
	}

	// Test empty page
	battles, total = db.GetBattlesPaginated(10, 5)
	if len(battles) != 0 {
		t.Errorf("Expected 0 battles on page 10, got %d", len(battles))
	}
}

// TestGetBattlesForCharacterEmpty tests getting battles for character with no battles
func TestGetBattlesForCharacterEmpty(t *testing.T) {
	db := NewDatabase()

	char, _ := db.Create(&models.Character{Name: "Char1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})

	battles := db.GetBattlesForCharacter(char.ID)
	if len(battles) != 0 {
		t.Errorf("Expected 0 battles, got %d", len(battles))
	}
}

// TestCharacterFilteringByRole tests character filtering endpoints
func TestCharacterFilteringByRole(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	// Create characters
	db.Create(&models.Character{Name: "Warrior1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	db.Create(&models.Character{Name: "Warrior2", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	db.Create(&models.Character{Name: "Thief1", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})

	req := httptest.NewRequest("GET", "/characters?role=Warrior", nil)
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var response map[string]interface{}
	json.NewDecoder(w.Body).Decode(&response)

	characters, _ := response["characters"].([]interface{})
	if len(characters) != 2 {
		t.Errorf("Expected 2 warriors, got %d", len(characters))
	}
}

// TestCharacterFilteringByStatus tests character filtering by status
func TestCharacterFilteringByStatus(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	// Create characters
	db.Create(&models.Character{Name: "Alive1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	db.Create(&models.Character{Name: "Alive2", Role: models.RoleThief, Level: 1, HP: 50, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})
	db.Create(&models.Character{Name: "Dead1", Role: models.RoleMage, Level: 1, HP: 0, MaxHP: 70, Strength: 20, Dexterity: 30, Intelligence: 60})

	req := httptest.NewRequest("GET", "/characters?status=alive", nil)
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var response map[string]interface{}
	json.NewDecoder(w.Body).Decode(&response)

	characters, _ := response["characters"].([]interface{})
	if len(characters) != 2 {
		t.Errorf("Expected 2 alive characters, got %d", len(characters))
	}

	// Test dead filter
	req = httptest.NewRequest("GET", "/characters?status=dead", nil)
	w = httptest.NewRecorder()

	server.ServeHTTP(w, req)

	json.NewDecoder(w.Body).Decode(&response)
	characters, _ = response["characters"].([]interface{})
	if len(characters) != 1 {
		t.Errorf("Expected 1 dead character, got %d", len(characters))
	}
}

// TestCharacterFilteringCombined tests combined role and status filtering
func TestCharacterFilteringCombined(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	// Create characters
	db.Create(&models.Character{Name: "WarriorAlive", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	db.Create(&models.Character{Name: "WarriorDead", Role: models.RoleWarrior, Level: 1, HP: 0, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	db.Create(&models.Character{Name: "ThiefAlive", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})

	req := httptest.NewRequest("GET", "/characters?role=Warrior&status=alive", nil)
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	var response map[string]interface{}
	json.NewDecoder(w.Body).Decode(&response)

	characters, _ := response["characters"].([]interface{})
	if len(characters) != 1 {
		t.Errorf("Expected 1 alive warrior, got %d", len(characters))
	}
}

// TestBattleRecordWithInvalidCharacter tests recording battle with invalid character
func TestBattleRecordWithInvalidCharacter(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	battle := models.Battle{
		Character1ID:     "nonexistent",
		Character2ID:     "nonexistent2",
		WinnerID:         "nonexistent",
		LoserID:          "nonexistent2",
		BattleLog:        []string{"Test"},
		ExperienceGained: 10,
		Timestamp:        time.Now(),
	}

	battleJSON, _ := json.Marshal(battle)
	req := httptest.NewRequest("POST", "/battles", bytes.NewBuffer(battleJSON))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

// TestGetBattlesPaginationEdgeCases tests pagination edge cases
func TestGetBattlesPaginationEdgeCases(t *testing.T) {
	db := NewDatabase()

	char1, _ := db.Create(&models.Character{Name: "Char1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	char2, _ := db.Create(&models.Character{Name: "Char2", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})

	// Create 3 battles
	for i := 0; i < 3; i++ {
		battle := &models.Battle{
			Character1ID:     char1.ID,
			Character2ID:     char2.ID,
			WinnerID:         char1.ID,
			LoserID:          char2.ID,
			BattleLog:        []string{"Battle"},
			ExperienceGained: 10,
			Timestamp:        time.Now(),
		}
		db.RecordBattle(battle)
	}

	// Test page 0 (should default to page 1)
	battles, _ := db.GetBattlesPaginated(0, 2)
	if len(battles) == 0 {
		t.Error("Expected battles even with page 0")
	}

	// Test negative page
	battles, _ = db.GetBattlesPaginated(-1, 2)
	if len(battles) != 0 {
		t.Errorf("Expected 0 battles for negative page, got %d", len(battles))
	}

	// Test page beyond total
	battles, _ = db.GetBattlesPaginated(10, 2)
	if len(battles) != 0 {
		t.Errorf("Expected 0 battles for page beyond total, got %d", len(battles))
	}
}

// TestDealDamageEdgeCases tests damage edge cases
func TestDealDamageEdgeCases(t *testing.T) {
	db := NewDatabase()

	char, _ := db.Create(&models.Character{
		Name:         "TestChar",
		Role:         models.RoleWarrior,
		Level:        1,
		HP:           100,
		MaxHP:        100,
		Strength:     50,
		Dexterity:    30,
		Intelligence: 20,
	})

	// Deal exact HP damage
	died, _ := db.DealDamage(char.ID, 100)
	if !died {
		t.Error("Character should be dead after exact HP damage")
	}

	// Deal more than HP damage
	char, _ = db.Create(&models.Character{
		Name:         "TestChar2",
		Role:         models.RoleWarrior,
		Level:        1,
		HP:           100,
		MaxHP:        100,
		Strength:     50,
		Dexterity:    30,
		Intelligence: 20,
	})

	died, _ = db.DealDamage(char.ID, 200)
	if !died {
		t.Error("Character should be dead after excessive damage")
	}

	updated, _ := db.Get(char.ID)
	if updated.HP != 0 {
		t.Errorf("Expected HP to be 0, got %d", updated.HP)
	}
}

// TestGetBattlesForCharacterMultiple tests getting battles when character appears in multiple battles
func TestGetBattlesForCharacterMultiple(t *testing.T) {
	db := NewDatabase()

	char1, _ := db.Create(&models.Character{Name: "Char1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	char2, _ := db.Create(&models.Character{Name: "Char2", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})
	char3, _ := db.Create(&models.Character{Name: "Char3", Role: models.RoleMage, Level: 1, HP: 70, MaxHP: 70, Strength: 20, Dexterity: 30, Intelligence: 60})

	// char1 vs char2
	battle1 := &models.Battle{
		Character1ID:     char1.ID,
		Character2ID:     char2.ID,
		WinnerID:         char1.ID,
		LoserID:          char2.ID,
		BattleLog:        []string{"Battle 1"},
		ExperienceGained: 10,
		Timestamp:        time.Now(),
	}
	// char1 vs char3 (char1 as character2)
	battle2 := &models.Battle{
		Character1ID:     char3.ID,
		Character2ID:     char1.ID,
		WinnerID:         char3.ID,
		LoserID:          char1.ID,
		BattleLog:        []string{"Battle 2"},
		ExperienceGained: 10,
		Timestamp:        time.Now(),
	}

	db.RecordBattle(battle1)
	db.RecordBattle(battle2)

	battles := db.GetBattlesForCharacter(char1.ID)
	if len(battles) != 2 {
		t.Errorf("Expected 2 battles for char1, got %d", len(battles))
	}
}

// TestCharacterResponseWithSpeedModifier tests that CharacterResponse includes speed modifier
func TestCharacterResponseWithSpeedModifier(t *testing.T) {
	char := &models.Character{
		Name:         "TestChar",
		Role:         models.RoleWarrior,
		Level:        1,
		HP:           100,
		MaxHP:        100,
		Strength:     50,
		Dexterity:    60,
		Intelligence: 40,
	}

	response := char.ToResponse()

	if response.SpeedModifier == 0 {
		t.Error("Expected speed modifier to be calculated")
	}

	expected := models.GetSpeedModifier(models.RoleWarrior, 60, 50, 40)
	if response.SpeedModifier != expected {
		t.Errorf("Expected speed modifier %f, got %f", expected, response.SpeedModifier)
	}
}
