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

## Additional Documentation

For detailed documentation, see the [`docs/`](./docs/) folder:
- **Project Structure** - Directory structure and file descriptions
- **API Endpoints** - Complete API documentation with examples
- **Database Migrations** - Schema, migrations, and data import instructions
- **Troubleshooting** - Common issues and solutions
- **Technology Stack** - Complete list of technologies used
- **License** - License information
