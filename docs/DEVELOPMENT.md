# Development

Tests and full app run via **Docker** (or **Podman**) and **docker-compose**. See **[Setup and Tests](./SETUP_AND_TESTS.md)** for setup and per-project test commands.

**Run all project tests (same as GitHub Actions CI):** from repo root, no DB required:

```bash
docker compose --profile test build
```

*(With Podman: `podman compose --profile test build`.)*

The following sections are for **optional** local development (running backend or frontend on the host without containers).

## Run Backend Locally

```bash
cd backend
./gradlew bootRun
```

The API will be available at http://localhost:8080

**Note**: Make sure PostgreSQL is running and accessible. Update `application.properties` with your database credentials if needed.

## Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000 (Vite default port)

**Note**: The frontend will proxy API requests to `http://localhost:8080` as configured in `vite.config.js`.

## Build Backend

```bash
cd backend
./gradlew clean build
```

The JAR file will be created in `build/libs/yugioh-api-1.0.0.jar`

## Build Frontend

```bash
cd frontend
npm install
npm run build
```

The production build will be created in `frontend/dist/` directory, ready to be served by a web server or Docker container.

