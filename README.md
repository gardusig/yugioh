# Yu-Gi-Oh! The Sacred Cards Database

A full-stack application for browsing all 900 cards and character decks from Yu-Gi-Oh! The Sacred Cards. Built with Go backend, PostgreSQL database, and a modern web interface.

## Features

- **Card Browsing**: Browse all 900 cards (001-900) from Yu-Gi-Oh! The Sacred Cards with pagination
- **Deck Viewing**: View all character decks with detailed information
- **Card Details**: View complete card information including attributes, race, level, attack/defense, cost, and rarity
- **Deck Details**: View full deck compositions with all 40 cards
- **Pagination**: Efficient pagination for both cards and decks

## Prerequisites

- **Docker Desktop** - Required for running the application
- **Go 1.23+** (optional) - For local development

## Quick Start

```bash
# Start all services (database, API, frontend)
docker-compose up --build

# Stop services
docker-compose down
```

## Services

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8082 | Web interface for card browsing and deck viewing |
| **API** | http://localhost:8080 | REST API endpoint |
| **Swagger UI** | http://localhost:8080/swagger | Interactive API documentation |
| **Database** | localhost:5432 | PostgreSQL database |

## Project Structure

```
.
├── backend/               # Go backend API
│   ├── api/              # HTTP handlers
│   ├── database/         # Database repositories and migrations
│   ├── models/           # Data models (Card, Deck)
│   ├── main.go          # Application entry point
│   └── Dockerfile       # Backend container definition
├── frontend/             # Frontend web interface
│   ├── public/          # HTML, CSS, JavaScript files
│   └── Dockerfile       # Frontend container definition
└── docker-compose.yml    # Service orchestration
```

## API Endpoints

All endpoints are publicly accessible - no authentication required.

### Cards
- `GET /cards` - List all cards with pagination
  - Query params: `page` (default: 1), `limit` (default: 24, max: 100)
  - Returns: `{ "cards": [...], "pagination": {...} }`
- `GET /cards/{id}` - Get card by ID with full details

### Swagger
- `GET /swagger` - Swagger UI for interactive API documentation
- `GET /swagger.json` - OpenAPI 3.0 specification

### Decks
- `GET /decks` - List all decks with pagination
  - Query params: `page` (default: 1), `limit` (default: 20, max: 100), `archetype`, `preset` (true/false)
  - Returns: Deck summaries with name, description, character_name, archetype, card_count, total_cost, max_cost
- `GET /decks/{id}` - Get deck by ID with full card details

## Database

The application uses PostgreSQL with the following tables:

### Cards Table
- `id` - Card number (001-900)
- `name` - Card name
- `description` - Card description
- `image` - Card image URL
- `type` - Monster, Spell, or Trap
- `attribute` - For monsters: Dark, Light, Earth, Water, Fire, Wind, Divine
- `race` - For monsters: Dragon, Spellcaster, Warrior, etc.
- `level` - Monster level (0 for Spell/Trap)
- `attack_points` - Attack points
- `defense_points` - Defense points
- `cost` - Card cost
- `rarity` - Common, Rare, Super Rare, Ultra Rare, etc.

### Decks Table
- `id` - Deck ID
- `name` - Deck name
- `description` - Deck description
- `character_name` - Character who uses this deck (e.g., "Weevil Underwood", "Mako Tsunami")
- `archetype` - Deck archetype/style (e.g., "Insect", "Fish", "Dragon")
- `max_cost` - Maximum total cost for the deck
- `is_preset` - Whether this is a preset character deck

### Deck Cards Table
- `deck_id` - Reference to deck
- `card_id` - Reference to card
- `position` - Position in deck (0-39)

## Database Migrations

Migrations are automatically run on backend startup. They are located in `backend/database/migrations/`:
- `001_initial_schema.sql` - Creates cards, decks, and deck_cards tables
- `002_seed_cards.sql` - Seeds all 900 cards (001-900) from The Sacred Cards
- `003_seed_decks.sql` - Seeds preset character decks (Weevil, Mako, Kaiba, Yugi, Joey, Rex, etc.)

## Frontend Pages

- **Home** (`index.html`) - Landing page with navigation to cards and decks
- **Cards** (`cards.html`) - Browse all 900 cards with pagination
- **Decks** (`decks.html`) - View and search decks, filter by archetype
- **Deck Detail** (`deck-detail.html`) - View full deck details with all cards

## Development

### Run Backend Locally

```bash
cd backend
go run main.go
```

The API will be available at http://localhost:8080

### Database Migrations

Migrations are automatically run on backend startup. The migration system reads all `.sql` files in `backend/database/migrations/` and executes them in numerical order (001, 002, 003, etc.).

## Troubleshooting

### Common Issues

- **Docker not running**: Start Docker Desktop application
- **Port conflicts**: Modify ports in `docker-compose.yml` if 8080 or 8082 are in use
- **View logs**: `docker-compose logs -f [service-name]`
- **Rebuild containers**: `docker-compose up --build --force-recreate`
- **Clean restart**: `docker-compose down && docker-compose up --build`

## License

This project is provided as-is for demonstration purposes.
