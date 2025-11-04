package models

import "time"

// Battle represents a battle between two characters
type Battle struct {
	ID           string    `json:"id"`
	Character1ID string   `json:"character1_id"`
	Character2ID string   `json:"character2_id"`
	WinnerID     string    `json:"winner_id"`
	LoserID      string    `json:"loser_id"`
	BattleLog    []string  `json:"battle_log"`
	ExperienceGained int   `json:"experience_gained"`
	LeveledUp    bool      `json:"leveled_up"`
	Timestamp    time.Time `json:"timestamp"`
}

// BattleResponse represents a battle with character names for API responses
type BattleResponse struct {
	ID              string    `json:"id"`
	Character1ID    string    `json:"character1_id"`
	Character1Name  string    `json:"character1_name"`
	Character2ID    string    `json:"character2_id"`
	Character2Name  string    `json:"character2_name"`
	WinnerID        string    `json:"winner_id"`
	WinnerName      string    `json:"winner_name"`
	LoserID         string    `json:"loser_id"`
	LoserName       string    `json:"loser_name"`
	BattleLog       []string  `json:"battle_log"`
	ExperienceGained int      `json:"experience_gained"`
	LeveledUp       bool      `json:"leveled_up"`
	Timestamp       time.Time `json:"timestamp"`
}

