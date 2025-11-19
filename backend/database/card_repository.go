package database

import (
	"database/sql"
	"fmt"
	"strings"

	"yugioh-api/models"
)

// CardRepository handles card database operations
type CardRepository struct{}

// NewCardRepository creates a new card repository
func NewCardRepository() *CardRepository {
	return &CardRepository{}
}

// GetAll retrieves all cards with pagination
func (r *CardRepository) GetAll(page, limit int) ([]models.Card, int, error) {
	offset := (page - 1) * limit

	// Get total count
	var total int
	err := DB.QueryRow("SELECT COUNT(*) FROM cards").Scan(&total)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to count cards: %w", err)
	}

	// Get paginated cards
	query := `
		SELECT id, name, description, image, type, attribute, race, level, attack_points, defense_points, cost, rarity
		FROM cards
		ORDER BY id
		LIMIT $1 OFFSET $2
	`
	rows, err := DB.Query(query, limit, offset)
	if err != nil {
		return nil, 0, fmt.Errorf("failed to query cards: %w", err)
	}
	defer rows.Close()

	cards := make([]models.Card, 0)
	for rows.Next() {
		var card models.Card
		err := rows.Scan(
			&card.ID,
			&card.Name,
			&card.Description,
			&card.Image,
			&card.Type,
			&card.Attribute,
			&card.Race,
			&card.Level,
			&card.AttackPoints,
			&card.DefensePoints,
			&card.Cost,
			&card.Rarity,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("failed to scan card: %w", err)
		}
		cards = append(cards, card)
	}

	return cards, total, nil
}

// GetByID retrieves a card by ID
func (r *CardRepository) GetByID(id int) (*models.Card, error) {
	query := `
		SELECT id, name, description, image, type, attribute, race, level, attack_points, defense_points, cost, rarity
		FROM cards
		WHERE id = $1
	`
	var card models.Card
	err := DB.QueryRow(query, id).Scan(
		&card.ID,
		&card.Name,
		&card.Description,
		&card.Image,
		&card.Type,
		&card.Attribute,
		&card.Race,
		&card.Level,
		&card.AttackPoints,
		&card.DefensePoints,
		&card.Cost,
	)
	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("card with ID %d not found", id)
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get card: %w", err)
	}
	return &card, nil
}

// GetByIDs retrieves multiple cards by their IDs
func (r *CardRepository) GetByIDs(ids []int) ([]models.Card, error) {
	if len(ids) == 0 {
		return []models.Card{}, nil
	}

	// Build query with placeholders
	placeholders := make([]string, len(ids))
	args := make([]interface{}, len(ids))
	for i, id := range ids {
		placeholders[i] = fmt.Sprintf("$%d", i+1)
		args[i] = id
	}

	query := fmt.Sprintf(`
		SELECT id, name, description, image, type, attribute, race, level, attack_points, defense_points, cost, rarity
		FROM cards
		WHERE id IN (%s)
		ORDER BY id
	`, strings.Join(placeholders, ","))

	rows, err := DB.Query(query, args...)
	if err != nil {
		return nil, fmt.Errorf("failed to query cards: %w", err)
	}
	defer rows.Close()

	cards := make([]models.Card, 0)
	for rows.Next() {
		var card models.Card
		err := rows.Scan(
			&card.ID,
			&card.Name,
			&card.Description,
			&card.Image,
			&card.Type,
			&card.Attribute,
			&card.Race,
			&card.Level,
			&card.AttackPoints,
			&card.DefensePoints,
			&card.Cost,
			&card.Rarity,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan card: %w", err)
		}
		cards = append(cards, card)
	}

	return cards, nil
}
