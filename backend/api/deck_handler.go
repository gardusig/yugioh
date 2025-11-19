package api

import (
	"encoding/json"
	"net/http"
	"strconv"

	"yugioh-api/database"
)

// DeckHandler handles deck-related HTTP requests
type DeckHandler struct {
	deckRepo *database.DeckRepository
}

// NewDeckHandler creates a new deck handler
func NewDeckHandler() *DeckHandler {
	return &DeckHandler{
		deckRepo: database.NewDeckRepository(),
	}
}

// GetAll handles GET /decks - Returns paginated list of all decks (public)
func (h *DeckHandler) GetAll(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	// Parse pagination parameters
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

	// Parse optional filters
	archetypeFilter := r.URL.Query().Get("archetype")
	presetOnly := r.URL.Query().Get("preset") == "true"

	decks, total, err := h.deckRepo.GetAllPaginated(page, limit, archetypeFilter, presetOnly)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	response := map[string]interface{}{
		"decks": decks,
		"pagination": map[string]interface{}{
			"page":       page,
			"limit":      limit,
			"total":      total,
			"totalPages": (total + limit - 1) / limit,
		},
	}

	json.NewEncoder(w).Encode(response)
}

// GetByID handles GET /decks/{id} - Returns deck details with cards (public)
func (h *DeckHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	idStr := r.PathValue("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Invalid deck ID"})
		return
	}

	deck, err := h.deckRepo.GetByID(id)
	if err != nil {
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	json.NewEncoder(w).Encode(deck)
}
