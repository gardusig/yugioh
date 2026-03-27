# Backend — Yu-Gi-Oh! API

REST API for the Yu-Gi-Oh! deck editor. **Stack:** Java 21, Spring Boot 3, PostgreSQL, Gradle.

## Focus

Serves cards and decks via REST. Handles pagination, filtering, and OpenAPI/Swagger docs.

## First-Time Setup

### Option A: Docker (recommended)

From the **project root**:

```bash
docker compose up --build
```

The backend runs at http://localhost:8080. Database and migrations are handled by other services.

### Option B: Local development

1. **Prerequisites:** OpenJDK 21+, PostgreSQL 16
2. **Database:** Start PostgreSQL (or `docker compose up -d database`)
3. **Run:**

```bash
cd backend
./gradlew bootRun
```

Set env vars if needed: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.

## Run Container Standalone

```bash
# From project root
docker build -f backend/Dockerfile -t yugioh-backend ./backend
docker run -p 8080:8080 \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e DB_USER=yugioh_user \
  -e DB_PASSWORD=yugioh_password \
  -e DB_NAME=yugioh_db \
  yugioh-backend
```

## Build & Test

```bash
./gradlew clean build
./gradlew test
```

## Endpoints

- **Health:** `GET /healthcheck`
- **Swagger UI:** http://localhost:8080/swagger-ui.html
- **API docs:** http://localhost:8080/api-docs
