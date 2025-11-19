package database

import (
	"database/sql"
	"fmt"
	"strings"

	"yugioh-api/models"
)

// DeckRepository handles deck database operations
type DeckRepository struct {
	cardRepo *CardRepository
}

// NewDeckRepository creates a new deck repository
func NewDeckRepository() *DeckRepository {
	return &DeckRepository{
		cardRepo: NewCardRepository(),
	}
}

// GetAllPaginated retrieves all decks with pagination (public access)
func (r *DeckRepository) GetAllPaginated(page, limit int, archetypeFilter string, presetOnly bool) ([]models.DeckSummary, int, error) {
	offset := (page - 1) * limit

	// Build WHERE clause
	whereClause := "1=1"
	args := []interface{}{}
	argIndex := 1

	if archetypeFilter != "" {
		whereClause += fmt.Sprintf(" AND archetype = $%d", argIndex)
		args = append(args, archetypeFilter)
		argIndex++
	}

	if presetOnly {
		whereClause += fmt.Sprintf(" AND is_preset = $%d", argIndex)
		args = append(args, true)
		argIndex++
	}

	// Get total count
	countQuery := fmt.Sprintf("SELECT COUNT(*) FROM decks WHERE %s", whereClause)
	var total int
	err := DB.QueryRow(countQuery, args...).Scan(&total)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to count decks: %w", err)
	}

	// Get paginated decks
	query := fmt.Sprintf(`
		SELECT id, name, description, max_cost, archetype, is_preset, character_name
		FROM decks
		WHERE %s
		ORDER BY is_preset DESC, character_name, name
		LIMIT $%d OFFSET $%d
	`, whereClause, argIndex, argIndex+1)
	args = append(args, limit, offset)

	rows, err := DB.Query(query, args...)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query decks: %w", err)
	}
	defer rows.Close()

	decks := make([]models.DeckSummary, 0)
	for rows.Next() {
		var deck models.DeckSummary
		err := rows.Scan(
			&deck.ID,
			&deck.Name,
			&deck.Description,
			&deck.MaxCost,
			&deck.Archetype,
			&deck.IsPreset,
			&deck.CharacterName,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to scan deck: %w", err)
		}

		// Get card count and total cost
		cardIDs, err := r.getDeckCardIDs(deck.ID)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to get card IDs for deck %d: %w", deck.ID, err)
		}
		deck.CardCount = len(cardIDs)

		if len(cardIDs) > 0 {
			cards, err := r.cardRepo.GetByIDs(cardIDs)
			if err == nil {
				for _, card := range cards {
					deck.TotalCost += card.Cost
				}
			}
		}

		decks = append(decks, deck)
	}

	return decks, total, nil
}

// GetByID retrieves a deck by ID with full card details (public access)
func (r *DeckRepository) GetByID(id int) (*models.DeckWithCards, error) {
	// Get deck info
	query := `
		SELECT id, name, description, max_cost, archetype, is_preset, character_name
		FROM decks
		WHERE id = $1
	`
	var deck models.DeckWithCards
	err := DB.QueryRow(query, id).Scan(
		&deck.ID,
		&deck.Name,
		&deck.Description,
		&deck.MaxCost,
		&deck.Archetype,
		&deck.IsPreset,
		&deck.CharacterName,
	)
	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("deck with ID %d not found", id)
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get deck: %w", err)
	}

	// Get card IDs
	cardIDs, err := r.getDeckCardIDs(id)
	if err != nil {
		return nil, fmt.Errorf("failed to get card IDs: %w", err)
	}

	// Get full card details
	if len(cardIDs) > 0 {
		cards, err := r.cardRepo.GetByIDs(cardIDs)
		if err != nil {
			return nil, fmt.Errorf("failed to get cards: %w", err)
		}
		deck.Cards = cards

		// Calculate total cost
		for _, card := range cards {
			deck.TotalCost += card.Cost
		}
	}

	return &deck, nil
}

// getDeckCardIDs retrieves card IDs for a deck in order
func (r *DeckRepository) getDeckCardIDs(deckID int) ([]int, error) {
	query := `
		SELECT card_id
		FROM deck_cards
		WHERE deck_id = $1
		ORDER BY position
	`
	rows, err := DB.Query(query, deckID)
	if err != nil {
		return nil, fmt.Errorf("failed to query deck cards: %w", err)
	}
	defer rows.Close()

	cardIDs := make([]int, 0)
	for rows.Next() {
		var cardID int
		err := rows.Scan(&cardID)
		if err != nil {
			return nil, fmt.Errorf("failed to scan card ID: %w", err)
		}
		cardIDs = append(cardIDs, cardID)
	}

	return cardIDs, nil
}

// SearchDeckNames retrieves deck names for autocomplete (returns all decks, filtering done in handler)
func (r *DeckRepository) SearchDeckNames(query string) ([]models.DeckSummary, error) {
	queryLower := "%" + strings.ToLower(query) + "%"
	sqlQuery := `
		SELECT id, name, description, max_cost, archetype, is_preset, character_name
		FROM decks
		WHERE LOWER(name) LIKE $1 OR LOWER(character_name) LIKE $1
		ORDER BY name
		LIMIT 50
	`
	rows, err := DB.Query(sqlQuery, queryLower)
	if err != nil {
		return nil, fmt.Errorf("failed to search deck names: %w", err)
	}
	defer rows.Close()

	decks := make([]models.DeckSummary, 0)
	for rows.Next() {
		var deck models.DeckSummary
		err := rows.Scan(
			&deck.ID,
			&deck.Name,
			&deck.Description,
			&deck.MaxCost,
			&deck.Archetype,
			&deck.IsPreset,
			&deck.CharacterName,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan deck: %w", err)
		}
		decks = append(decks, deck)
	}

	return decks, nil
}
