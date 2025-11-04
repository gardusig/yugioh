package main

import (
	"encoding/json"
	"net/http"
	"strconv"
	"strings"
	"time"

	"character-api/models"
)

// Server holds the API server and its dependencies
type Server struct {
	db     *Database
	router *http.ServeMux
}

// NewServer creates a new server instance
func NewServer(db *Database) *Server {
	s := &Server{
		db:     db,
		router: http.NewServeMux(),
	}
	s.setupRoutes()
	return s
}

// setupRoutes configures all HTTP routes
func (s *Server) setupRoutes() {
	// Read APIs
	s.router.HandleFunc("GET /healthcheck", s.handleCORS(s.handleHealthCheck))
	s.router.HandleFunc("GET /characters", s.handleCORS(s.handleGetAllCharacters))
	s.router.HandleFunc("GET /characters/{id}", s.handleCORS(s.handleGetCharacter))
	s.router.HandleFunc("GET /swagger.json", s.handleCORS(s.handleSwagger))

	// Write APIs
	s.router.HandleFunc("POST /characters", s.handleCORS(s.handleCreateCharacter))
	s.router.HandleFunc("PUT /characters/{id}", s.handleCORS(s.handleUpdateCharacter))
	s.router.HandleFunc("DELETE /characters/{id}", s.handleCORS(s.handleDeleteCharacter))
	s.router.HandleFunc("POST /characters/{id}/experience", s.handleCORS(s.handleAddExperience))
	s.router.HandleFunc("POST /characters/{id}/damage", s.handleCORS(s.handleDealDamage))

	// Battle APIs
	s.router.HandleFunc("POST /battles", s.handleCORS(s.handleRecordBattle))
	s.router.HandleFunc("GET /battles", s.handleCORS(s.handleGetBattles))
	s.router.HandleFunc("GET /characters/{id}/battles", s.handleCORS(s.handleGetCharacterBattles))
}

// handleCORS wraps handlers to add CORS headers and handle OPTIONS preflight
func (s *Server) handleCORS(handler http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		enableCORS(w)

		// Handle preflight OPTIONS request
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		handler(w, r)
	}
}

// Read API Handlers

// handleHealthCheck handles the /healthcheck endpoint
func (s *Server) handleHealthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	response := map[string]string{
		"status": "healthy",
	}
	json.NewEncoder(w).Encode(response)
}

// handleGetAllCharacters handles GET /characters with optional pagination
func (s *Server) handleGetAllCharacters(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	// Parse pagination parameters
	page := 1
	limit := 24
	if pageStr := r.URL.Query().Get("page"); pageStr != "" {
		if p, err := strconv.Atoi(pageStr); err == nil && p > 0 {
			page = p
		}
	}
	if limitStr := r.URL.Query().Get("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil && l > 0 && l <= 100 {
			limit = l
		}
	}

	// Parse filters
	roleFilter := r.URL.Query().Get("role")
	statusFilter := r.URL.Query().Get("status")

	var characters []*models.Character
	var total int

	if page > 0 && limit > 0 {
		// Use paginated version with filters
		characters, total = s.db.GetAllPaginatedWithFilters(page, limit, roleFilter, statusFilter)
	} else {
		// Return all characters (with filters if provided)
		if roleFilter != "" || statusFilter != "" {
			characters, total = s.db.GetAllPaginatedWithFilters(1, 1000, roleFilter, statusFilter)
		} else {
			characters = s.db.GetAll()
			total = len(characters)
		}
	}

	// Convert to response format with modifiers
	responses := make([]*models.CharacterResponse, len(characters))
	for i, char := range characters {
		responses[i] = char.ToResponse()
	}

	// Return paginated response
	response := map[string]interface{}{
		"characters": responses,
		"pagination": map[string]interface{}{
			"page":       page,
			"limit":      limit,
			"total":      total,
			"totalPages": (total + limit - 1) / limit,
		},
	}

	json.NewEncoder(w).Encode(response)
}

// handleGetCharacter handles GET /characters/{id}
func (s *Server) handleGetCharacter(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimPrefix(r.URL.Path, "/characters/")

	char, err := s.db.Get(id)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	// Convert to response format with modifiers
	json.NewEncoder(w).Encode(char.ToResponse())
}

// handleSwagger handles GET /swagger.json
func (s *Server) handleSwagger(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	http.ServeFile(w, r, "./docs/swagger.json")
}

// Write API Handlers

// handleCreateCharacter handles POST /characters
func (s *Server) handleCreateCharacter(w http.ResponseWriter, r *http.Request) {
	var char models.Character
	if err := json.NewDecoder(r.Body).Decode(&char); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Invalid request body"})
		return
	}

	// Validate role
	if !models.IsValidRole(char.Role) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Invalid role. Must be Warrior, Thief, or Mage"})
		return
	}

	// Initialize default values for new characters
	if char.Name == "" {
		char.Name = "Unnamed Character"
	}
	if char.Level == 0 {
		char.Level = 1
	}
	if char.Experience == 0 {
		char.Experience = 0
	}
	if char.MaxHP == 0 {
		char.MaxHP = char.HP
	}
	if char.HP == 0 {
		char.HP = char.MaxHP
	}

	created, err := s.db.Create(&char)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusConflict)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	// Convert to response format with modifiers
	json.NewEncoder(w).Encode(created.ToResponse())
}

// handleUpdateCharacter handles PUT /characters/{id}
func (s *Server) handleUpdateCharacter(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimPrefix(r.URL.Path, "/characters/")

	var char models.Character
	if err := json.NewDecoder(r.Body).Decode(&char); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Invalid request body"})
		return
	}

	// Validate role
	if !models.IsValidRole(char.Role) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Invalid role. Must be Warrior, Thief, or Mage"})
		return
	}

	updated, err := s.db.Update(id, &char)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.Header().Set("Content-Type", "application/json")
	// Convert to response format with modifiers
	json.NewEncoder(w).Encode(updated.ToResponse())
}

// handleDeleteCharacter handles DELETE /characters/{id}
func (s *Server) handleDeleteCharacter(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimPrefix(r.URL.Path, "/characters/")

	if err := s.db.Delete(id); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// handleAddExperience handles POST /characters/{id}/experience
func (s *Server) handleAddExperience(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimPrefix(r.URL.Path, "/characters/")
	id = strings.TrimSuffix(id, "/experience")

	var req struct {
		Amount int `json:"amount"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Invalid request body"})
		return
	}

	if req.Amount <= 0 {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Experience amount must be positive"})
		return
	}

	leveledUp, err := s.db.AddExperience(id, req.Amount)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	char, _ := s.db.Get(id)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"character":  char.ToResponse(),
		"leveled_up": leveledUp,
	})
}

// handleDealDamage handles POST /characters/{id}/damage
func (s *Server) handleDealDamage(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimPrefix(r.URL.Path, "/characters/")
	id = strings.TrimSuffix(id, "/damage")

	var req struct {
		Damage int `json:"damage"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Invalid request body"})
		return
	}

	if req.Damage <= 0 {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Damage must be positive"})
		return
	}

	died, err := s.db.DealDamage(id, req.Damage)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	char, _ := s.db.Get(id)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"character": char.ToResponse(),
		"died":      died,
	})
}

// Battle API Handlers

// handleRecordBattle handles POST /battles
func (s *Server) handleRecordBattle(w http.ResponseWriter, r *http.Request) {
	var battle models.Battle
	if err := json.NewDecoder(r.Body).Decode(&battle); err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Invalid request body"})
		return
	}

	// Set timestamp if not provided
	if battle.Timestamp.IsZero() {
		battle.Timestamp = time.Now()
	}

	// Get character names for response
	char1, err1 := s.db.Get(battle.Character1ID)
	char2, err2 := s.db.Get(battle.Character2ID)
	if err1 != nil || err2 != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Character not found"})
		return
	}

	recorded, err := s.db.RecordBattle(&battle)
	if err != nil {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	// Create response with character names
	response := &models.BattleResponse{
		ID:               recorded.ID,
		Character1ID:     recorded.Character1ID,
		Character1Name:   char1.Name,
		Character2ID:     recorded.Character2ID,
		Character2Name:   char2.Name,
		WinnerID:         recorded.WinnerID,
		WinnerName:       "",
		LoserID:          recorded.LoserID,
		LoserName:        "",
		BattleLog:        recorded.BattleLog,
		ExperienceGained: recorded.ExperienceGained,
		LeveledUp:        recorded.LeveledUp,
		Timestamp:        recorded.Timestamp,
	}

	// Set winner/loser names
	if recorded.WinnerID == char1.ID {
		response.WinnerName = char1.Name
		response.LoserName = char2.Name
	} else {
		response.WinnerName = char2.Name
		response.LoserName = char1.Name
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(response)
}

// handleGetBattles handles GET /battles with pagination
func (s *Server) handleGetBattles(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	page := 1
	limit := 20
	if pageStr := r.URL.Query().Get("page"); pageStr != "" {
		if p, err := strconv.Atoi(pageStr); err == nil && p > 0 {
			page = p
		}
	}
	if limitStr := r.URL.Query().Get("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil && l > 0 && l <= 100 {
			limit = l
		}
	}

	battles, total := s.db.GetBattlesPaginated(page, limit)

	// Convert to BattleResponse with character names
	responses := make([]*models.BattleResponse, len(battles))
	for i, battle := range battles {
		char1, _ := s.db.Get(battle.Character1ID)
		char2, _ := s.db.Get(battle.Character2ID)

		response := &models.BattleResponse{
			ID:               battle.ID,
			Character1ID:     battle.Character1ID,
			Character1Name:   char1.Name,
			Character2ID:     battle.Character2ID,
			Character2Name:   char2.Name,
			WinnerID:         battle.WinnerID,
			WinnerName:       "",
			LoserID:          battle.LoserID,
			LoserName:        "",
			BattleLog:        battle.BattleLog,
			ExperienceGained: battle.ExperienceGained,
			LeveledUp:        battle.LeveledUp,
			Timestamp:        battle.Timestamp,
		}

		if battle.WinnerID == char1.ID {
			response.WinnerName = char1.Name
			response.LoserName = char2.Name
		} else {
			response.WinnerName = char2.Name
			response.LoserName = char1.Name
		}

		responses[i] = response
	}

	json.NewEncoder(w).Encode(map[string]interface{}{
		"battles": responses,
		"pagination": map[string]interface{}{
			"page":       page,
			"limit":      limit,
			"total":      total,
			"totalPages": (total + limit - 1) / limit,
		},
	})
}

// handleGetCharacterBattles handles GET /characters/{id}/battles
func (s *Server) handleGetCharacterBattles(w http.ResponseWriter, r *http.Request) {
	id := strings.TrimPrefix(r.URL.Path, "/characters/")
	id = strings.TrimSuffix(id, "/battles")

	battles := s.db.GetBattlesForCharacter(id)

	// Convert to BattleResponse with character names
	responses := make([]*models.BattleResponse, len(battles))
	for i, battle := range battles {
		char1, _ := s.db.Get(battle.Character1ID)
		char2, _ := s.db.Get(battle.Character2ID)

		response := &models.BattleResponse{
			ID:               battle.ID,
			Character1ID:     battle.Character1ID,
			Character1Name:   char1.Name,
			Character2ID:     battle.Character2ID,
			Character2Name:   char2.Name,
			WinnerID:         battle.WinnerID,
			WinnerName:       "",
			LoserID:          battle.LoserID,
			LoserName:        "",
			BattleLog:        battle.BattleLog,
			ExperienceGained: battle.ExperienceGained,
			LeveledUp:        battle.LeveledUp,
			Timestamp:        battle.Timestamp,
		}

		if battle.WinnerID == char1.ID {
			response.WinnerName = char1.Name
			response.LoserName = char2.Name
		} else {
			response.WinnerName = char2.Name
			response.LoserName = char1.Name
		}

		responses[i] = response
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"battles": responses,
		"total":   len(responses),
	})
}

// ServeHTTP makes Server implement http.Handler
func (s *Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// Handle OPTIONS preflight requests globally
	if r.Method == "OPTIONS" {
		enableCORS(w)
		w.WriteHeader(http.StatusOK)
		return
	}

	s.router.ServeHTTP(w, r)
}
