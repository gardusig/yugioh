package main

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"

	"neo-submission/back-end-api/models"
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
}
