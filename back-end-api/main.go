package main

import (
	"fmt"
	"net/http"
)

// enableCORS adds CORS headers to the response
func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
}

func main() {
	// Initialize database
	db := NewDatabase()

	// Initialize server
	server := NewServer(db)

	fmt.Println("🚀 API running on :8080")
	http.ListenAndServe(":8080", server)
}
