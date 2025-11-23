# API Endpoints

All endpoints are publicly accessible - no authentication required.

## Cards

- `GET /cards` - List all cards with pagination
  - Query params: `page` (default: 1), `limit` (default: 24, max: 100)
  - Returns: `{ "cards": [...], "pagination": {...} }`
- `GET /cards/{id}` - Get card by ID with full details

## Decks

- `GET /decks` - List all decks with pagination
  - Query params: `page` (default: 1), `limit` (default: 20, max: 100), `archetype`, `preset` (true/false)
  - Returns: Deck summaries with name, description, character_name, archetype, card_count, total_cost, max_cost
- `GET /decks/{id}` - Get deck by ID with full card details

## Health

- `GET /healthcheck` - Health check endpoint

## Swagger/OpenAPI

- `GET /swagger-ui.html` - Swagger UI for interactive API documentation
- `GET /api-docs` - OpenAPI 3.0 JSON specification

## Example API Calls

### Using cURL

```bash
# Get all cards (first page)
curl http://localhost:8080/cards

# Get cards with pagination
curl http://localhost:8080/cards?page=2&limit=50

# Get specific card
curl http://localhost:8080/cards/1

# Get all decks
curl http://localhost:8080/decks

# Get decks filtered by archetype
curl http://localhost:8080/decks?archetype=Insect

# Get preset decks only
curl http://localhost:8080/decks?preset=true

# Get specific deck with cards
curl http://localhost:8080/decks/1

# Health check
curl http://localhost:8080/healthcheck
```

### Using Swagger UI

1. Open http://localhost:8080/swagger-ui.html
2. Click on any endpoint (e.g., `GET /cards`)
3. Click "Try it out"
4. Modify parameters if needed
5. Click "Execute"
6. View the response

