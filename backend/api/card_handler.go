package api

import (
	"encoding/json"
	"net/http"
	"strconv"

	"yugioh-api/database"
	"yugioh-api/models"
)

// CardHandler handles card-related HTTP requests
type CardHandler struct {
	cardRepo *database.CardRepository
}

// NewCardHandler creates a new card handler
func NewCardHandler() *CardHandler {
	return &CardHandler{
		cardRepo: database.NewCardRepository(),
	}
}

// GetAll handles GET /cards
func (h *CardHandler) GetAll(w http.ResponseWriter, r *http.Request) {
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
	typeFilter := r.URL.Query().Get("type")
	levelFilter := r.URL.Query().Get("level")

	cards, total, err := h.cardRepo.GetAll(page, limit)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	// Apply filters if provided
	filteredCards := cards
	if typeFilter != "" {
		filtered := make([]models.Card, 0)
		for _, card := range cards {
			if card.Type == typeFilter {
				filtered = append(filtered, card)
			}
		}
		filteredCards = filtered
	}
	if levelFilter != "" {
		level, err := strconv.Atoi(levelFilter)
		if err == nil {
			filtered := make([]models.Card, 0)
			for _, card := range filteredCards {
				if card.Level == level {
					filtered = append(filtered, card)
				}
			}
			filteredCards = filtered
		}
	}

	response := map[string]interface{}{
		"cards": filteredCards,
		"pagination": map[string]interface{}{
			"page":       page,
			"limit":      limit,
			"total":      total,
			"totalPages": (total + limit - 1) / limit,
		},
	}

	json.NewEncoder(w).Encode(response)
}

// GetByID handles GET /cards/{id}
func (h *CardHandler) GetByID(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	idStr := r.PathValue("id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(map[string]string{"error": "Invalid card ID"})
		return
	}

	card, err := h.cardRepo.GetByID(id)
	if err != nil {
		w.WriteHeader(http.StatusNotFound)
		json.NewEncoder(w).Encode(map[string]string{"error": err.Error()})
		return
	}

	json.NewEncoder(w).Encode(card)
}
