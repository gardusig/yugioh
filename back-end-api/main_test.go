package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"
	"time"

	"character-api/models"
)

// TestEnableCORS tests the CORS headers are set correctly
func TestEnableCORS(t *testing.T) {
	w := httptest.NewRecorder()
	enableCORS(w)

	if w.Header().Get("Access-Control-Allow-Origin") != "*" {
		t.Errorf("Expected Access-Control-Allow-Origin to be '*', got '%s'", w.Header().Get("Access-Control-Allow-Origin"))
	}

	if w.Header().Get("Access-Control-Allow-Methods") != "GET, POST, PUT, DELETE, OPTIONS" {
		t.Errorf("Expected Access-Control-Allow-Methods to include all methods, got '%s'", w.Header().Get("Access-Control-Allow-Methods"))
	}

	if w.Header().Get("Access-Control-Allow-Headers") != "Content-Type" {
		t.Errorf("Expected Access-Control-Allow-Headers to be 'Content-Type', got '%s'", w.Header().Get("Access-Control-Allow-Headers"))
	}
}

// TestServerHealthCheck tests the /healthcheck endpoint
func TestServerHealthCheck(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	req := httptest.NewRequest("GET", "/healthcheck", nil)
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	// Check CORS headers
	if w.Header().Get("Access-Control-Allow-Origin") != "*" {
		t.Error("CORS headers not set")
	}

	// Check content type
	if w.Header().Get("Content-Type") != "application/json" {
		t.Errorf("Expected Content-Type to be 'application/json', got '%s'", w.Header().Get("Content-Type"))
	}

	// Check response body
	var response map[string]string
	if err := json.NewDecoder(w.Body).Decode(&response); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	if response["status"] != "healthy" {
		t.Errorf("Expected status 'healthy', got '%s'", response["status"])
	}
}

// TestServerCreateCharacter tests creating a character
func TestServerCreateCharacter(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	character := models.Character{
		Role:         models.RoleWarrior,
		Level:        1,
		Experience:   0,
		HP:           100,
		MaxHP:        100,
		Strength:     80,
		Dexterity:    60,
		Intelligence: 40,
	}

	body, _ := json.Marshal(character)
	req := httptest.NewRequest("POST", "/characters", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusCreated {
		t.Errorf("Expected status %d, got %d", http.StatusCreated, w.Code)
	}

	var created models.CharacterResponse
	if err := json.NewDecoder(w.Body).Decode(&created); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	if created.ID == "" {
		t.Error("Expected character to have an ID")
	}

	if created.Role != models.RoleWarrior {
		t.Errorf("Expected role %s, got %s", models.RoleWarrior, created.Role)
	}

	// Check level-up multipliers are calculated
	if created.StrengthMultiplier == 0 || created.DexterityMultiplier == 0 {
		t.Error("Expected level-up multipliers to be calculated")
	}

	// Check default level is set
	if created.Level != 1 {
		t.Errorf("Expected level 1, got %d", created.Level)
	}
}

// TestServerGetAllCharacters tests getting all characters
func TestServerGetAllCharacters(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	// Create a character
	char1 := &models.Character{
		Role:         models.RoleMage,
		Level:        1,
		Experience:   0,
		HP:           80,
		MaxHP:        80,
		Strength:     40,
		Dexterity:    60,
		Intelligence: 90,
	}
	db.Create(char1)

	req := httptest.NewRequest("GET", "/characters", nil)
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var characters []models.CharacterResponse
	if err := json.NewDecoder(w.Body).Decode(&characters); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	if len(characters) != 1 {
		t.Errorf("Expected 1 character, got %d", len(characters))
	}
}

// TestServerGetCharacter tests getting a single character
func TestServerGetCharacter(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	// Create a character
	char := &models.Character{
		Role:         models.RoleThief,
		Level:        1,
		Experience:   0,
		HP:           90,
		MaxHP:        90,
		Strength:     60,
		Dexterity:    85,
		Intelligence: 70,
	}
	created, _ := db.Create(char)

	req := httptest.NewRequest("GET", "/characters/"+created.ID, nil)
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var retrieved models.CharacterResponse
	if err := json.NewDecoder(w.Body).Decode(&retrieved); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	if retrieved.ID != created.ID {
		t.Errorf("Expected ID %s, got %s", created.ID, retrieved.ID)
	}
}

// TestServerUpdateCharacter tests updating a character
func TestServerUpdateCharacter(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	// Create a character
	char := &models.Character{
		Role:         models.RoleWarrior,
		Level:        1,
		Experience:   0,
		HP:           100,
		MaxHP:        100,
		Strength:     80,
		Dexterity:    60,
		Intelligence: 40,
	}
	created, _ := db.Create(char)

	// Update character
	updatedChar := models.Character{
		Role:         models.RoleMage,
		Level:        1,
		Experience:   0,
		HP:           120,
		MaxHP:        120,
		Strength:     50,
		Dexterity:    70,
		Intelligence: 100,
	}

	body, _ := json.Marshal(updatedChar)
	req := httptest.NewRequest("PUT", "/characters/"+created.ID, bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var updated models.CharacterResponse
	if err := json.NewDecoder(w.Body).Decode(&updated); err != nil {
		t.Fatalf("Failed to decode response: %v", err)
	}

	if updated.HP != 120 {
		t.Errorf("Expected HP 120, got %d", updated.HP)
	}

	if updated.Role != models.RoleMage {
		t.Errorf("Expected role %s, got %s", models.RoleMage, updated.Role)
	}
}

// TestServerDeleteCharacter tests deleting a character
func TestServerDeleteCharacter(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	// Create a character
	char := &models.Character{
		Role:         models.RoleThief,
		Level:        1,
		Experience:   0,
		HP:           90,
		MaxHP:        90,
		Strength:     60,
		Dexterity:    85,
		Intelligence: 70,
	}
	created, _ := db.Create(char)

	req := httptest.NewRequest("DELETE", "/characters/"+created.ID, nil)
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusNoContent {
		t.Errorf("Expected status %d, got %d", http.StatusNoContent, w.Code)
	}

	// Verify character is deleted
	_, err := db.Get(created.ID)
	if err == nil {
		t.Error("Expected character to be deleted")
	}
}

// TestServerSwaggerHandler tests the /swagger.json endpoint
func TestServerSwaggerHandler(t *testing.T) {
	// Create a temporary swagger.json file for testing
	testDir := t.TempDir()
	testFile := filepath.Join(testDir, "swagger.json")
	testContent := `{"openapi": "3.0.0", "info": {"title": "Test API"}}`

	if err := os.WriteFile(testFile, []byte(testContent), 0644); err != nil {
		t.Fatalf("Failed to create test swagger file: %v", err)
	}

	// Change to test directory temporarily
	originalDir, err := os.Getwd()
	if err != nil {
		t.Fatalf("Failed to get current directory: %v", err)
	}
	defer os.Chdir(originalDir)

	if err := os.Chdir(testDir); err != nil {
		t.Fatalf("Failed to change to test directory: %v", err)
	}

	// Create docs directory
	if err := os.MkdirAll("docs", 0755); err != nil {
		t.Fatalf("Failed to create docs directory: %v", err)
	}

	// Move swagger.json to docs directory
	docsFile := filepath.Join("docs", "swagger.json")
	if err := os.WriteFile(docsFile, []byte(testContent), 0644); err != nil {
		t.Fatalf("Failed to create docs swagger file: %v", err)
	}

	db := NewDatabase()
	server := NewServer(db)

	req := httptest.NewRequest("GET", "/swagger.json", nil)
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	// Check CORS headers
	if w.Header().Get("Access-Control-Allow-Origin") != "*" {
		t.Error("CORS headers not set")
	}

	// Check content type
	if w.Header().Get("Content-Type") != "application/json" {
		t.Errorf("Expected Content-Type to be 'application/json', got '%s'", w.Header().Get("Content-Type"))
	}
}

// TestDatabaseOperations tests database CRUD operations
func TestDatabaseOperations(t *testing.T) {
	db := NewDatabase()

	// Test Create
	char := &models.Character{
		Role:         models.RoleWarrior,
		Level:        1,
		Experience:   0,
		HP:           100,
		MaxHP:        100,
		Strength:     80,
		Dexterity:    60,
		Intelligence: 40,
	}

	created, err := db.Create(char)
	if err != nil {
		t.Fatalf("Failed to create character: %v", err)
	}

	if created.ID == "" {
		t.Error("Expected character to have an ID")
	}

	// Test Get
	retrieved, err := db.Get(created.ID)
	if err != nil {
		t.Fatalf("Failed to get character: %v", err)
	}

	if retrieved.ID != created.ID {
		t.Errorf("Expected ID %s, got %s", created.ID, retrieved.ID)
	}

	// Test GetAll
	allChars := db.GetAll()
	if len(allChars) != 1 {
		t.Errorf("Expected 1 character, got %d", len(allChars))
	}

	// Test Update
	char.HP = 120
	updated, err := db.Update(created.ID, char)
	if err != nil {
		t.Fatalf("Failed to update character: %v", err)
	}

	if updated.HP != 120 {
		t.Errorf("Expected HP 120, got %d", updated.HP)
	}

	// Test Delete
	err = db.Delete(created.ID)
	if err != nil {
		t.Fatalf("Failed to delete character: %v", err)
	}

	_, err = db.Get(created.ID)
	if err == nil {
		t.Error("Expected character to be deleted")
	}
}

// TestGetLevelUpMultipliers tests role-based level-up multiplier calculation
func TestGetLevelUpMultipliers(t *testing.T) {
	tests := []struct {
		role                 models.Role
		expectedStrength     float64
		expectedDexterity    float64
		expectedIntelligence float64
	}{
		{models.RoleWarrior, 0.80, 0.20, 0.00},
		{models.RoleThief, 0.25, 1.00, 0.25},
		{models.RoleMage, 0.20, 0.20, 1.20},
	}

	for _, tt := range tests {
		t.Run(string(tt.role), func(t *testing.T) {
			str, dex, int := models.GetLevelUpMultipliers(tt.role)
			if str != tt.expectedStrength {
				t.Errorf("Expected strength multiplier %f, got %f", tt.expectedStrength, str)
			}
			if dex != tt.expectedDexterity {
				t.Errorf("Expected dexterity multiplier %f, got %f", tt.expectedDexterity, dex)
			}
			if int != tt.expectedIntelligence {
				t.Errorf("Expected intelligence multiplier %f, got %f", tt.expectedIntelligence, int)
			}
		})
	}
}

// TestIsValidRole tests role validation
func TestIsValidRole(t *testing.T) {
	tests := []struct {
		role     models.Role
		expected bool
	}{
		{models.RoleWarrior, true},
		{models.RoleThief, true},
		{models.RoleMage, true},
		{models.Role("Invalid"), false},
		{models.Role(""), false},
	}

	for _, tt := range tests {
		t.Run(string(tt.role), func(t *testing.T) {
			result := models.IsValidRole(tt.role)
			if result != tt.expected {
				t.Errorf("Expected %v for role %s, got %v", tt.expected, tt.role, result)
			}
		})
	}
}

// TestCharacterToResponse tests character to response conversion
func TestCharacterToResponse(t *testing.T) {
	char := &models.Character{
		ID:           "1",
		Role:         models.RoleWarrior,
		Level:        1,
		Experience:   0,
		HP:           100,
		MaxHP:        100,
		Strength:     80,
		Dexterity:    60,
		Intelligence: 40,
	}

	response := char.ToResponse()

	if response.ID != char.ID {
		t.Errorf("Expected ID %s, got %s", char.ID, response.ID)
	}

	if response.StrengthMultiplier != 0.80 {
		t.Errorf("Expected strength multiplier 0.80, got %f", response.StrengthMultiplier)
	}

	if response.DexterityMultiplier != 0.20 {
		t.Errorf("Expected dexterity multiplier 0.20, got %f", response.DexterityMultiplier)
	}

	if response.IntelligenceMultiplier != 0.00 {
		t.Errorf("Expected intelligence multiplier 0.00, got %f", response.IntelligenceMultiplier)
	}

	if response.SpeedModifier == 0 {
		t.Error("Expected speed modifier to be calculated")
	}
}

// TestServerAddExperience tests adding experience endpoint
func TestServerAddExperience(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	char, _ := db.Create(&models.Character{
		Name:         "TestChar",
		Role:         models.RoleWarrior,
		Level:        1,
		Experience:   0,
		HP:           100,
		MaxHP:        100,
		Strength:     50,
		Dexterity:    30,
		Intelligence: 20,
	})

	reqBody := map[string]int{"amount": 100}
	reqJSON, _ := json.Marshal(reqBody)
	req := httptest.NewRequest("POST", "/characters/"+char.ID+"/experience", bytes.NewBuffer(reqJSON))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var response map[string]interface{}
	json.NewDecoder(w.Body).Decode(&response)

	character, _ := response["character"].(map[string]interface{})
	if character["experience"].(float64) != 100 {
		t.Errorf("Expected experience 100, got %f", character["experience"].(float64))
	}
}

// TestServerAddExperienceInvalid tests invalid experience amounts
func TestServerAddExperienceInvalid(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

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

	// Test negative experience
	reqBody := map[string]int{"amount": -10}
	reqJSON, _ := json.Marshal(reqBody)
	req := httptest.NewRequest("POST", "/characters/"+char.ID+"/experience", bytes.NewBuffer(reqJSON))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}

	// Test zero experience
	reqBody = map[string]int{"amount": 0}
	reqJSON, _ = json.Marshal(reqBody)
	req = httptest.NewRequest("POST", "/characters/"+char.ID+"/experience", bytes.NewBuffer(reqJSON))
	req.Header.Set("Content-Type", "application/json")
	w = httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

// TestServerDealDamage tests damage endpoint
func TestServerDealDamage(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

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

	reqBody := map[string]int{"damage": 30}
	reqJSON, _ := json.Marshal(reqBody)
	req := httptest.NewRequest("POST", "/characters/"+char.ID+"/damage", bytes.NewBuffer(reqJSON))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	var response map[string]interface{}
	json.NewDecoder(w.Body).Decode(&response)

	character, _ := response["character"].(map[string]interface{})
	if int(character["hp"].(float64)) != 70 {
		t.Errorf("Expected HP 70, got %f", character["hp"].(float64))
	}
}

// TestServerDealDamageInvalid tests invalid damage amounts
func TestServerDealDamageInvalid(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

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

	// Test negative damage
	reqBody := map[string]int{"damage": -10}
	reqJSON, _ := json.Marshal(reqBody)
	req := httptest.NewRequest("POST", "/characters/"+char.ID+"/damage", bytes.NewBuffer(reqJSON))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}

	// Test zero damage
	reqBody = map[string]int{"damage": 0}
	reqJSON, _ = json.Marshal(reqBody)
	req = httptest.NewRequest("POST", "/characters/"+char.ID+"/damage", bytes.NewBuffer(reqJSON))
	req.Header.Set("Content-Type", "application/json")
	w = httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

// TestGetAllPaginatedWithFiltersEmpty tests filtering with no matches
func TestGetAllPaginatedWithFiltersEmpty(t *testing.T) {
	db := NewDatabase()

	// Create characters that don't match filter
	db.Create(&models.Character{Name: "Warrior1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	db.Create(&models.Character{Name: "Thief1", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})

	// Filter for Mage (none exist)
	characters, total := db.GetAllPaginatedWithFilters(1, 10, "Mage", "")
	if total != 0 {
		t.Errorf("Expected 0 mages, got %d", total)
	}
	if len(characters) != 0 {
		t.Errorf("Expected 0 characters in result, got %d", len(characters))
	}
}

// TestDatabaseGetAllPaginated tests pagination with no filters
func TestDatabaseGetAllPaginated(t *testing.T) {
	db := NewDatabase()

	// Create 10 characters
	for i := 0; i < 10; i++ {
		db.Create(&models.Character{
			Name:         "Char" + string(rune(i+'0')),
			Role:         models.RoleWarrior,
			Level:        1,
			HP:           100,
			MaxHP:        100,
			Strength:     50,
			Dexterity:    30,
			Intelligence: 20,
		})
	}

	// Test first page
	characters, total := db.GetAllPaginated(1, 5)
	if total != 10 {
		t.Errorf("Expected total 10, got %d", total)
	}
	if len(characters) != 5 {
		t.Errorf("Expected 5 characters on first page, got %d", len(characters))
	}

	// Test second page
	characters, total = db.GetAllPaginated(2, 5)
	if len(characters) != 5 {
		t.Errorf("Expected 5 characters on second page, got %d", len(characters))
	}
}

// TestDatabaseGetAllPaginatedEdgeCases tests pagination edge cases
func TestDatabaseGetAllPaginatedEdgeCases(t *testing.T) {
	db := NewDatabase()

	// Create 3 characters
	for i := 0; i < 3; i++ {
		db.Create(&models.Character{
			Name:         "Char" + string(rune(i+'0')),
			Role:         models.RoleWarrior,
			Level:        1,
			HP:           100,
			MaxHP:        100,
			Strength:     50,
			Dexterity:    30,
			Intelligence: 20,
		})
	}

	// Test page beyond total
	characters, _ := db.GetAllPaginated(10, 5)
	if len(characters) != 0 {
		t.Errorf("Expected 0 characters for page 10, got %d", len(characters))
	}

	// Test page 0
	characters, _ = db.GetAllPaginated(0, 5)
	if len(characters) == 0 {
		t.Error("Expected characters even with page 0")
	}
}

// TestServerGetAllCharactersWithFilters tests character filtering via API
func TestServerGetAllCharactersWithFilters(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	// Create characters
	db.Create(&models.Character{Name: "Warrior1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	db.Create(&models.Character{Name: "Warrior2", Role: models.RoleWarrior, Level: 1, HP: 0, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	db.Create(&models.Character{Name: "Thief1", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})

	// Test role filter
	req := httptest.NewRequest("GET", "/characters?role=Warrior&page=1&limit=10", nil)
	w := httptest.NewRecorder()
	server.ServeHTTP(w, req)

	var response map[string]interface{}
	json.NewDecoder(w.Body).Decode(&response)

	characters, _ := response["characters"].([]interface{})
	if len(characters) != 2 {
		t.Errorf("Expected 2 warriors, got %d", len(characters))
	}

	// Test status filter
	req = httptest.NewRequest("GET", "/characters?status=alive&page=1&limit=10", nil)
	w = httptest.NewRecorder()
	server.ServeHTTP(w, req)

	json.NewDecoder(w.Body).Decode(&response)
	characters, _ = response["characters"].([]interface{})
	if len(characters) != 2 {
		t.Errorf("Expected 2 alive characters, got %d", len(characters))
	}
}

// TestServerGetAllCharactersPagination tests pagination via API
func TestServerGetAllCharactersPagination(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	// Create 30 characters
	for i := 0; i < 30; i++ {
		db.Create(&models.Character{
			Name:         "Char" + string(rune(i+'0')),
			Role:         models.RoleWarrior,
			Level:        1,
			HP:           100,
			MaxHP:        100,
			Strength:     50,
			Dexterity:    30,
			Intelligence: 20,
		})
	}

	req := httptest.NewRequest("GET", "/characters?page=1&limit=24", nil)
	w := httptest.NewRecorder()
	server.ServeHTTP(w, req)

	var response map[string]interface{}
	json.NewDecoder(w.Body).Decode(&response)

	characters, _ := response["characters"].([]interface{})
	if len(characters) != 24 {
		t.Errorf("Expected 24 characters, got %d", len(characters))
	}

	pagination, _ := response["pagination"].(map[string]interface{})
	if int(pagination["total"].(float64)) != 30 {
		t.Errorf("Expected total 30, got %f", pagination["total"].(float64))
	}
}

// TestServerOptionsRequest tests OPTIONS preflight handling
func TestServerOptionsRequest(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	req := httptest.NewRequest("OPTIONS", "/characters", nil)
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}

	if w.Header().Get("Access-Control-Allow-Origin") != "*" {
		t.Error("Expected CORS headers")
	}
}

// TestServerCreateCharacterDefaults tests default values in character creation
func TestServerCreateCharacterDefaults(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

	charJSON := map[string]interface{}{
		"role": "Warrior",
		"hp":   120,
		"strength": 100,
		"dexterity": 60,
		"intelligence": 40,
	}

	reqBody, _ := json.Marshal(charJSON)
	req := httptest.NewRequest("POST", "/characters", bytes.NewBuffer(reqBody))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusCreated {
		t.Errorf("Expected status %d, got %d", http.StatusCreated, w.Code)
	}

	var response models.CharacterResponse
	json.NewDecoder(w.Body).Decode(&response)

	if response.Name == "" {
		t.Error("Expected default name")
	}
	if response.Level != 1 {
		t.Errorf("Expected level 1, got %d", response.Level)
	}
	if response.MaxHP == 0 {
		t.Error("Expected MaxHP to be set")
	}
}

// TestServerUpdateCharacterValidation tests update character validation
func TestServerUpdateCharacterValidation(t *testing.T) {
	db := NewDatabase()
	server := NewServer(db)

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

	// Test invalid role
	charJSON := map[string]interface{}{
		"name": "Updated",
		"role": "InvalidRole",
		"hp":   100,
		"strength": 50,
		"dexterity": 30,
		"intelligence": 20,
	}

	reqBody, _ := json.Marshal(charJSON)
	req := httptest.NewRequest("PUT", "/characters/"+char.ID, bytes.NewBuffer(reqBody))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()

	server.ServeHTTP(w, req)

	if w.Code != http.StatusBadRequest {
		t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
	}
}

// TestGetBattlesForCharacterOrder tests battle order (newest first)
func TestGetBattlesForCharacterOrder(t *testing.T) {
	db := NewDatabase()

	char1, _ := db.Create(&models.Character{Name: "Char1", Role: models.RoleWarrior, Level: 1, HP: 100, MaxHP: 100, Strength: 50, Dexterity: 30, Intelligence: 20})
	char2, _ := db.Create(&models.Character{Name: "Char2", Role: models.RoleThief, Level: 1, HP: 80, MaxHP: 80, Strength: 30, Dexterity: 50, Intelligence: 40})

	// Create battles with different timestamps
	battle1 := &models.Battle{
		Character1ID:     char1.ID,
		Character2ID:     char2.ID,
		WinnerID:         char1.ID,
		LoserID:          char2.ID,
		BattleLog:        []string{"Battle 1"},
		ExperienceGained: 10,
		Timestamp:        time.Now().Add(-2 * time.Hour),
	}
	battle2 := &models.Battle{
		Character1ID:     char1.ID,
		Character2ID:     char2.ID,
		WinnerID:         char1.ID,
		LoserID:          char2.ID,
		BattleLog:        []string{"Battle 2"},
		ExperienceGained: 10,
		Timestamp:        time.Now(),
	}

	db.RecordBattle(battle1)
	db.RecordBattle(battle2)

	battles := db.GetBattlesForCharacter(char1.ID)
	if len(battles) != 2 {
		t.Fatalf("Expected 2 battles, got %d", len(battles))
	}

	// Newest should be first
	if battles[0].Timestamp.Before(battles[1].Timestamp) {
		t.Error("Expected newest battle first")
	}
}
