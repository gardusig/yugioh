package main

import (
	"encoding/json"
	"fmt"
	"net/http"
)

// enableCORS adds CORS headers to the response
func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
}

type User struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

func main() {
	// Hello endpoint
	http.HandleFunc("/hello", func(w http.ResponseWriter, r *http.Request) {
		enableCORS(w)
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		response := map[string]string{
			"message": "Hello! Welcome to the Neo API",
		}
		json.NewEncoder(w).Encode(response)
	})

	http.HandleFunc("/users", func(w http.ResponseWriter, r *http.Request) {
		enableCORS(w)
		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}
		users := []User{
			{ID: "1", Name: "Gustavo"},
			{ID: "2", Name: "Alex"},
		}
		json.NewEncoder(w).Encode(users)
	})

	// Serve Swagger spec
	http.HandleFunc("/swagger.json", func(w http.ResponseWriter, r *http.Request) {
		enableCORS(w)
		w.Header().Set("Content-Type", "application/json")
		http.ServeFile(w, r, "./docs/swagger.json")
	})

	fmt.Println("🚀 API running on :8080")
	http.ListenAndServe(":8080", nil)
}
