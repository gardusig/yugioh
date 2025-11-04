# Character Management System

A full-stack character management application with battle mechanics, experience systems, and level progression. Built with Go backend, Swagger UI documentation, and a modern web interface.

## Features

- **Character Management**: Create, update, delete, and view characters with detailed stats
- **Role System**: Three unique character roles (Warrior, Thief, Mage) with role-specific stat growth
- **Experience & Leveling**: Exponential experience system with automatic level-ups
- **Battle System**: Turn-based combat with speed-based turn order
- **Battle History**: Track all battles with detailed logs and outcomes
- **Filtering & Pagination**: Filter characters by role/status with paginated views

## Prerequisites

- **Docker Desktop** - Install via Homebrew: `brew install --cask docker`
- **Go 1.23+** (optional) - For local development: `brew install go`

## Quick Start

```bash
# Start all services (backend API, Swagger UI, frontend)
docker-compose up --build

# Stop services
docker-compose down
```

## Services

| Service | URL | Description |
|---------|-----|-------------|
| **Front-end UI** | http://localhost:8082 | Web interface for character management and battles |
| **Swagger UI** | http://localhost:8081 | Interactive API documentation |
| **Back-end API** | http://localhost:8080 | REST API endpoint |

## Character System

### Character Creation

Characters can be created with:
- **Name**: Custom name or randomly generated
- **Role**: Warrior, Thief, or Mage
- **Initial Stats**: Automatically set based on role

### Experience & Leveling

- Characters start at **level 1** with **0 experience**
- Experience requirements grow exponentially (base: 100, multiplier: 1.5 per level)
- Maximum level: **100**
- On level up:
  - HP is restored to maximum
  - MaxHP increases by 10%
  - Stats improve based on role multipliers

### Character Roles & Level-Up Multipliers

Each role has unique stat growth when leveling up:

| Role | Strength | Dexterity | Intelligence |
|------|----------|-----------|--------------|
| **Warrior** | +80% | +20% | +0% |
| **Thief** | +25% | +100% | +25% |
| **Mage** | +20% | +20% | +120% |

### Battle System

- **Turn-based combat**: Each battle consists of a single turn
- **Speed-based turn order**: Character with higher speed modifier attacks first
- **Speed modifiers**:
  - Warrior: 60% dexterity + 20% intelligence
  - Thief: 80% dexterity
  - Mage: 40% dexterity + 10% strength
- **Experience rewards**: Winners gain experience based on opponent's level
- **Battle history**: All battles are recorded with detailed logs

## API Endpoints

### Read Operations

- `GET /healthcheck` - API health status
- `GET /characters` - List all characters (supports pagination and filters)
  - Query params: `page`, `limit`, `role`, `status`
- `GET /characters/{id}` - Get character by ID
- `GET /battles` - List all battles (supports pagination)
  - Query params: `page`, `limit`
- `GET /characters/{id}/battles` - Get battles for a specific character

### Write Operations

- `POST /characters` - Create new character
- `PUT /characters/{id}` - Update character
- `DELETE /characters/{id}` - Delete character
- `POST /characters/{id}/experience` - Add experience (may trigger level up)
- `POST /characters/{id}/damage` - Deal damage to character
- `POST /battles` - Record a battle outcome

### API Documentation

Visit http://localhost:8081 for interactive Swagger UI documentation with full endpoint details, request/response schemas, and the ability to test endpoints directly.

## Development

### Project Structure

```
.
├── back-end-api/          # Go backend API
│   ├── models/            # Data models (Character, Battle, Role, Modifiers)
│   ├── docs/              # Swagger/OpenAPI documentation
│   ├── main.go            # Application entry point
│   ├── server.go          # HTTP server and route handlers
│   ├── database.go        # In-memory database implementation
│   └── *_test.go          # Unit tests
├── front-end-ui/          # Frontend web interface
│   └── public/            # HTML, CSS, JavaScript files
└── docker-compose.yml     # Service orchestration
```

### Run API Locally

```bash
cd back-end-api
go run main.go
```

The API will be available at http://localhost:8080

### Run Tests

```bash
cd back-end-api

# Run all unit tests
go test -v

# Run tests with coverage
go test -v -cover

# Run specific test
go test -v -run TestServerHealthCheck

# Generate coverage report
go test -coverprofile=coverage.out
go tool cover -html=coverage.out
```

### Test Coverage

The project includes comprehensive unit tests covering:
- API endpoints and handlers
- Database operations (CRUD, pagination, filtering)
- Character level-up mechanics
- Experience system
- Battle recording and retrieval
- Speed modifier calculations
- Damage dealing
- Edge cases and error handling

## Architecture

### Backend

- **Language**: Go 1.23+
- **Database**: In-memory map with `sync.RWMutex` for thread safety
- **API**: RESTful HTTP API with JSON responses
- **CORS**: Enabled for cross-origin requests
- **Documentation**: OpenAPI 3.0 specification

### Frontend

- **Technology**: Vanilla HTML, CSS, JavaScript
- **Features**: 
  - Multi-page navigation
  - Character creation and management
  - Battle simulation
  - Battle history with pagination
  - Character filtering
  - Responsive design

## Troubleshooting

### Common Issues

- **Docker not running**: Start Docker Desktop application
- **Port conflicts**: Modify ports in `docker-compose.yml` if 8080, 8081, or 8082 are in use
- **View logs**: `docker-compose logs -f [service-name]`
- **Rebuild containers**: `docker-compose up --build --force-recreate`
- **Clean restart**: `docker-compose down && docker-compose up --build`

### API Errors

- **404 Not Found**: Check endpoint URL and HTTP method
- **400 Bad Request**: Verify request body format and required fields
- **CORS errors**: Ensure backend is running and CORS headers are set

## License

This project is provided as-is for demonstration purposes.
