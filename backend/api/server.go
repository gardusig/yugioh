package api

import (
	"encoding/json"
	"net/http"
)

// Server holds the API server and its dependencies
type Server struct {
	router        *http.ServeMux
	cardHandler   *CardHandler
	deckHandler   *DeckHandler
	swaggerHandler *SwaggerHandler
}

// NewServer creates a new server instance
func NewServer() *Server {
	s := &Server{
		router:        http.NewServeMux(),
		cardHandler:   NewCardHandler(),
		deckHandler:   NewDeckHandler(),
		swaggerHandler: NewSwaggerHandler(),
	}
	s.setupRoutes()
	return s
}

// setupRoutes configures all HTTP routes
func (s *Server) setupRoutes() {
	// Health check
	s.router.HandleFunc("GET /healthcheck", s.handleCORS(s.handleHealthCheck))

	// Swagger UI
	s.router.HandleFunc("GET /swagger", s.handleCORS(s.swaggerHandler.ServeSwaggerUI))
	s.router.HandleFunc("GET /swagger.json", s.handleCORS(s.swaggerHandler.ServeSwaggerJSON))

	// Card routes (public)
	s.router.HandleFunc("GET /cards", s.handleCORS(s.cardHandler.GetAll))
	s.router.HandleFunc("GET /cards/{id}", s.handleCORS(s.cardHandler.GetByID))

	// Deck routes (public)
	s.router.HandleFunc("GET /decks", s.handleCORS(s.deckHandler.GetAll))
	s.router.HandleFunc("GET /decks/{id}", s.handleCORS(s.deckHandler.GetByID))
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

// enableCORS adds CORS headers to the response
func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
}

// handleHealthCheck handles the /healthcheck endpoint
func (s *Server) handleHealthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	response := map[string]string{
		"status": "healthy",
	}
	json.NewEncoder(w).Encode(response)
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

