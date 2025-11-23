# Yu-Gi-Oh! The Sacred Cards

![Java 21](https://img.shields.io/badge/Java%2021-ED8B00?logo=openjdk&logoColor=white)    ![Backend Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen)

![React 18.2](https://img.shields.io/badge/React%2018.2-61DAFB?logo=react&logoColor=black)  ![Frontend Coverage](https://img.shields.io/badge/Coverage-99%25-brightgreen)

![Python 3.9](https://img.shields.io/badge/Python%203.9-3776AB?logo=python&logoColor=white) ![Scripts Coverage](https://img.shields.io/badge/Coverage-99%25-brightgreen)







A full-stack web application for browsing all 900 cards and character decks from **Yu-Gi-Oh! The Sacred Cards**. Built with **Java Spring Boot** backend, **PostgreSQL** database, a modern **React + Tailwind CSS** frontend, and **Python scripts** for data management, all containerized with **Docker**.

## Features

- **Card Browsing**: Browse Yu-Gi-Oh! The Sacred Cards data with pagination
- **Deck Viewing**: View character decks with detailed information
- **Card Details**: View complete card information
- **Deck Details**: View full deck compositions with all 40 cards
- **Pagination**: Efficient pagination for both cards and decks
- **Swagger/OpenAPI**: Interactive API documentation with Swagger UI
- **Scriptable Data Management**: Reset, clear, and reseed the database

## Prerequisites

- **Docker Desktop** - Required for running the application (all services are containerized)
- **OpenJDK 21+** (optional) - For local backend development (Eclipse Temurin recommended)
- **Node.js 20+** (optional) - For local frontend development
- **npm** (optional) - For local frontend development

**Note**: The backend uses Gradle wrapper (`gradlew`), so Gradle doesn't need to be installed separately. The wrapper will download Gradle automatically on first use.

## Quick Start

### 1. Start the Application (all services)

```bash
# Start all services (database, API, frontend)
docker-compose up --build

# Stop services
docker-compose down
```

### 2. Start only the Database (for maintenance)

```bash
# Launch PostgreSQL alone (useful for running scripts)
docker-compose up -d database
```

### 3. Access the Application

Once the services are running, you can access:

#### **Frontend Web UI** 🌐
- **URL**: http://localhost:8082
- **Description**: React + Tailwind CSS web interface for browsing cards and decks
- **Features**:
  - Browse all 900 cards with pagination
  - View character decks
  - Search and filter decks by archetype
  - View detailed deck compositions
  - Modern, responsive UI built with Tailwind CSS
  - Client-side routing with React Router

#### **Swagger UI** 📚
- **URL**: http://localhost:8080/swagger-ui.html
- **Description**: Interactive API documentation
- **Features**:
  - Browse all available API endpoints
  - Test API calls directly from the browser
  - View request/response schemas
  - See example requests and responses

#### **API Documentation (JSON)** 📄
- **URL**: http://localhost:8080/api-docs
- **Description**: OpenAPI 3.0 JSON specification
- **Use Case**: Import into API testing tools like Postman or Insomnia

#### **Backend API** 🔌
- **URL**: http://localhost:8080
- **Description**: REST API endpoint
- **Health Check**: http://localhost:8080/healthcheck

## Database Maintenance & Sample Data

Flyway now creates only the schema (`V1__initial_schema.sql`). All data management happens through `scripts/src/db_manager.py`. This keeps migrations fast and lets you decide when/how to populate the database.

### Step-by-step: clear DB and load the first 10 cards (001-010)

```bash
# 1. Start PostgreSQL only (if it is not already running)
docker-compose up -d database

# 2. Clear all data but keep the tables
docker-compose run --rm scripts python3 src/db_manager.py clear-all

# 3. Seed the first 10 iconic cards
docker-compose run --rm scripts python3 src/db_manager.py seed --cards
```

### Other useful commands

> ℹ️ Run `docker-compose up -d database` first so the scripts can connect to Postgres.

| Goal | Command |
|------|---------|
| Drop & recreate entire schema (removes everything) | `docker-compose run --rm scripts python3 src/db_manager.py reset-db` |
| Clear all rows but keep tables | `docker-compose run --rm scripts python3 src/db_manager.py clear-all` |
| Clear a single table | `docker-compose run --rm scripts python3 src/db_manager.py clear-table cards` (or `decks`, `deck_cards`) |
| Seed the sample 10 iconic cards + 2 decks | `docker-compose run --rm scripts python3 src/db_manager.py seed` |
| Seed only cards | `docker-compose run --rm scripts python3 src/db_manager.py seed --cards` |
| Seed only decks (expects matching card IDs to exist) | `docker-compose run --rm scripts python3 src/db_manager.py seed --decks` |

To generate larger SQL imports (e.g., all 900 cards), run `crawl_cards.py` to produce an export, then pipe it into `psql` or adapt the output inside `db_manager.py`. See `scripts/README.md` for details.

## Services Overview

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8082 | Web interface for card browsing and deck viewing |
| **Backend API** | http://localhost:8080 | REST API endpoint (Spring Boot) |
| **Swagger UI** | http://localhost:8080/swagger-ui.html | Interactive API documentation |
| **API Docs** | http://localhost:8080/api-docs | OpenAPI 3.0 JSON specification |
| **Database** | localhost:5432 | PostgreSQL database |
| **Scripts** | N/A | Utility scripts container (run on-demand via `docker-compose run`) |

## How to Use Swagger UI

1. **Start the application**: `docker-compose up --build`
2. **Open Swagger UI**: Navigate to http://localhost:8080/swagger-ui.html in your browser
3. **Explore Endpoints**: 
   - Click on any endpoint (e.g., `GET /cards`) to expand it
   - View the endpoint description, parameters, and response schema
4. **Test API Calls**:
   - Click "Try it out" button on any endpoint
   - Modify parameters if needed (e.g., `page`, `limit`)
   - Click "Execute" to make the API call
   - View the response in the UI
5. **View Schemas**: Scroll down to see all data models (Card, Deck, etc.)

## How to Use the Frontend UI

1. **Start the application**: `docker-compose up --build`
2. **Open the Frontend**: Navigate to http://localhost:8082 in your browser
3. **Browse Cards**:
   - Click "Browse All Cards (001-900)" from the home page
   - Use pagination to navigate through cards
   - View card details including attack, defense, and cost
4. **Browse Decks**:
   - Click "View Decks & Search" from the home page
   - Use filters to find decks by archetype (Insect, Dragon, etc.)
   - Search for specific decks by name
   - Click on any deck to view full details with all cards

## Project Structure

```
.
├── backend/                          # Java Spring Boot backend (web server only)
│   ├── src/main/java/com/yugioh/
│   │   ├── YugiohApplication.java   # Main application class
│   │   ├── config/                  # Configuration classes
│   │   ├── controller/             # REST controllers
│   │   ├── service/                 # Business logic services
│   │   ├── repository/              # JPA repositories
│   │   ├── model/                   # Entity models
│   │   └── dto/                     # Data transfer objects
│   ├── src/main/resources/
│   │   ├── application.properties    # Application configuration
│   │   └── db/migration/             # Flyway database migrations
│   ├── build.gradle.kts              # Gradle build configuration
│   ├── settings.gradle.kts           # Gradle settings
│   └── Dockerfile                   # Backend container definition
├── frontend/                        # React + Tailwind CSS frontend
│   ├── src/                         # React source code
│   │   ├── pages/                   # Page components
│   │   ├── components/              # Reusable components
│   │   └── api/                     # API integration layer
│   ├── public/                      # Static assets
│   ├── package.json                 # Node.js dependencies
│   ├── vite.config.js               # Vite build configuration
│   ├── tailwind.config.js           # Tailwind CSS configuration
│   └── Dockerfile                   # Frontend container definition
├── scripts/                         # Utility scripts and tools (Python)
│   ├── src/                         # Source scripts
│   │   ├── crawl_cards.py           # Card data crawler
│   │   ├── db_manager.py            # Reset/clear/seed helper
│   │   ├── gather_card_data.py      # Gather card data to CSV
│   │   └── ...                      # Other utility scripts
│   ├── tests/                       # Unit tests
│   ├── Dockerfile                   # Scripts container definition
│   └── README.md                    # Scripts documentation
├── data/                            # Data files (CSV files)
│   ├── card_list.csv                # Card names list
│   └── cards_data.csv               # Complete card data (generated)
└── docker-compose.yml               # Service orchestration
```

## API Endpoints

All endpoints are publicly accessible - no authentication required.

### Cards
- `GET /cards` - List all cards with pagination
  - Query params: `page` (default: 1), `limit` (default: 24, max: 100)
  - Returns: `{ "cards": [...], "pagination": {...} }`
- `GET /cards/{id}` - Get card by ID with full details

### Decks
- `GET /decks` - List all decks with pagination
  - Query params: `page` (default: 1), `limit` (default: 20, max: 100), `archetype`, `preset` (true/false)
  - Returns: Deck summaries with name, description, character_name, archetype, card_count, total_cost, max_cost
- `GET /decks/{id}` - Get deck by ID with full card details

### Health
- `GET /healthcheck` - Health check endpoint

### Swagger/OpenAPI
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

Flyway automatically runs SQL files inside `backend/src/main/resources/db/migration/`. At the moment only the schema migration is maintained in Git:

- `V1__initial_schema.sql` — creates `cards`, `decks`, and `deck_cards`

All data seeding is handled manually through `scripts/src/db_manager.py` to avoid long Flyway runtimes and to keep business data outside of migrations.

### Generating / Importing Card Data

If you need a large batch of card inserts:

1. Run the crawler to generate SQL (see `scripts/README.md` for options).
2. Pipe the output directly into `psql`, or copy the rows you want into `db_manager.py` and re-run the `seed` command.

Example (Docker + psql):

```bash
docker-compose run --rm scripts python3 src/crawl_cards.py --start 1 --end 50 > cards.sql
cat cards.sql | docker exec -i yugioh-database psql -U yugioh_user -d yugioh_db
rm cards.sql
```

## Development

### Local CI Checks

Before pushing code, you can run the same checks that GitHub Actions will run:

```bash
# Run all CI checks locally and update README badges
./ci-local.sh
```

This script will:
- **Backend**: Check for unused imports (Spotless Gradle plugin) and run unit tests (using Mockito mocks, no database required)
- **Frontend**: Install dependencies, build check (Vite), run unit tests (Vitest), and check for unused dependencies
- **Scripts**: Run Python unit tests with coverage
- **Badges**: Automatically update README badges with current test status and coverage percentages (green if tests pass, red if they fail)

**Note**: All tests use mocks and don't require a running database. The README badges will be updated with the actual coverage percentages from test results (e.g., 60% shown as green if tests pass).

### Run Backend Locally

```bash
cd backend
./gradlew bootRun
```

The API will be available at http://localhost:8080

**Note**: Make sure PostgreSQL is running and accessible. Update `application.properties` with your database credentials if needed.

### Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000 (Vite default port)

**Note**: The frontend will proxy API requests to `http://localhost:8080` as configured in `vite.config.js`.

### Build Backend

```bash
cd backend
./gradlew clean build
```

The JAR file will be created in `build/libs/yugioh-api-1.0.0.jar`

### Build Frontend

```bash
cd frontend
npm install
npm run build
```

The production build will be created in `frontend/dist/` directory, ready to be served by a web server or Docker container.

### Database Migrations

Migrations are automatically run on backend startup via Flyway. The migration system reads all SQL files in `backend/src/main/resources/db/migration/` and executes them in version order (V1, V2, V3, etc.).

## Troubleshooting

### Common Issues

- **Docker not running**: Start Docker Desktop application
- **Port conflicts**: Modify ports in `docker-compose.yml` if 8080 or 8082 are in use
- **View logs**: `docker-compose logs -f [service-name]`
  - Backend logs: `docker-compose logs -f backend`
  - Database logs: `docker-compose logs -f database`
  - Frontend logs: `docker-compose logs -f frontend`
- **Rebuild containers**: `docker-compose up --build --force-recreate`
- **Clean restart**: `docker-compose down && docker-compose up --build`
- **Database connection issues**: Check that the database service is healthy before the backend starts
- **Migration errors**: Check Flyway logs in backend container output

### Backend Connection Issues

If the frontend cannot connect to the backend:

1. Verify backend is running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Test API directly: `curl http://localhost:8080/healthcheck`
4. Verify CORS is enabled (it should be with `@CrossOrigin` annotations)

### Swagger UI Not Loading

If Swagger UI doesn't load:

1. Verify backend is running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Try accessing: http://localhost:8080/api-docs (should return JSON)
4. Clear browser cache and try again

## Technology Stack

### Backend
- **OpenJDK 21** - Programming language (latest LTS, Eclipse Temurin distribution)
- **Spring Boot 3.3.0** - Application framework
- **Spring Data JPA** - Database access layer
- **Springdoc OpenAPI** - API documentation (Swagger)
- **Gradle 8.5** - Build tool and dependency management
- **Flyway** - Database migrations

### Frontend
- **React 18** - UI library
- **React Router 6** - Client-side routing
- **Tailwind CSS 3** - Utility-first CSS framework
- **Vite 5** - Build tool and development server
- **Vitest** - Unit testing framework
- **React Testing Library** - Component testing utilities

### Database
- **PostgreSQL 16** - Relational database

### DevOps & Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **GitHub Actions** - CI/CD pipeline

### Testing
- **JUnit 5** - Backend unit testing
- **Mockito** - Backend mocking framework
- **Vitest** - Frontend unit testing
- **JaCoCo** - Backend code coverage
- **Vitest Coverage** - Frontend code coverage

## License

This project is provided as-is for demonstration purposes.
