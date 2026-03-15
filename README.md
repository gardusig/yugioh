# Yu-Gi-Oh! Deck Editor

![Java 21](https://img.shields.io/badge/Java%2021-ED8B00?logo=openjdk&logoColor=white)    ![Backend Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen)

![React 18.2](https://img.shields.io/badge/React%2018.2-61DAFB?logo=react&logoColor=black)  ![Frontend Coverage](https://img.shields.io/badge/Coverage-99%25-brightgreen)

![Python 3.9](https://img.shields.io/badge/Python%203.9-3776AB?logo=python&logoColor=white) ![Scripts Coverage](https://img.shields.io/badge/Coverage-99%25-brightgreen)







A full-stack web application for browsing cards and building decks. Built with **Java Spring Boot** backend, **PostgreSQL** database, a modern **React + Tailwind CSS** frontend, and **Python scripts** for data management, all containerized with **Docker** or **Podman**.

## Features

- **Card Browsing**: Browse cards with pagination
- **Deck Viewing**: View and manage decks with detailed information
- **Card Details**: View complete card information
- **Deck Details**: View full deck compositions with all 40 cards
- **Pagination**: Efficient pagination for both cards and decks
- **Swagger/OpenAPI**: Interactive API documentation with Swagger UI
- **Scriptable Data Management**: Reset, clear, and reseed the database

## Prerequisites

- **Docker** or **Podman** - Required for running the application (all services are containerized). Use `./podman.sh` to run with either.
- **OpenJDK 21+** (optional) - For local backend development (Eclipse Temurin recommended)
- **Node.js 20+** (optional) - For local frontend development
- **npm** (optional) - For local frontend development

**Note**: The backend uses Gradle wrapper (`gradlew`), so Gradle doesn't need to be installed separately. The wrapper will download Gradle automatically on first use.

## Quick Start

### 1. First-Time Setup

```bash
# Start all services (database → scripts → backend → frontend)
# Uses Podman if available, otherwise Docker
./podman.sh up --build
```

On first run, the `scripts` service runs migrations and seeds the database from `data/*.csv` (no network required). The backend starts after that.

### 2. Start only the Database (for maintenance)

```bash
# Launch PostgreSQL alone (useful for running scripts locally)
./podman.sh up -d database
```

### 3. Per-Folder Setup

Each folder has its own README with first-time setup and runnable container instructions:

- **[backend/README.md](./backend/README.md)** — Java Spring Boot API
- **[frontend/README.md](./frontend/README.md)** — React + Vite UI
- **[scripts/README.md](./scripts/README.md)** — Python data management

### 4. Access the Application

- **Frontend**: http://localhost:8082
- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **API Docs**: http://localhost:8080/api-docs
- **Health Check**: http://localhost:8080/healthcheck

## Documentation

- **[Getting Started](./docs/GETTING_STARTED.md)** - Access URLs, services overview, and usage guides
- **[Database Maintenance](./docs/DATABASE_MAINTENANCE.md)** - Database commands and sample data setup
- **[Development](./docs/DEVELOPMENT.md)** - Local development setup and build instructions
- **[API Endpoints](./docs/API_ENDPOINTS.md)** - Complete API documentation with examples
- **[Project Structure](./docs/PROJECT_STRUCTURE.md)** - Directory structure and file descriptions
- **[Database Migrations](./docs/DATABASE_MIGRATIONS.md)** - Schema, migrations, and data import instructions
- **[Troubleshooting](./docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Technology Stack](./docs/TECHNOLOGY_STACK.md)** - Complete list of technologies used
- **[License](./docs/LICENSE.md)** - License information
