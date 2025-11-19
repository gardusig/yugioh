package main

import (
	"fmt"
	"log"
	"net/http"

	"yugioh-api/api"
	"yugioh-api/database"
)

func main() {
	// Initialize database connection
	config := database.GetConfig()
	if err := database.Connect(config); err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer database.Close()

	// Run migrations
	if err := database.RunMigrations(); err != nil {
		log.Fatalf("Failed to run migrations: %v", err)
	}

	// Initialize server
	server := api.NewServer()

	fmt.Println("🚀 API running on :8080")
	if err := http.ListenAndServe(":8080", server); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
