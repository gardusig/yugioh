# Development

**Run the app and tests in containers:** See [SETUP_AND_TESTS.md](SETUP_AND_TESTS.md) (setup, run app) and [TESTS.md](TESTS.md) (run tests, per-project, Podman, native).

The sections below are for **optional** local development — running backend or frontend on the host **without** Docker/Podman.

## Quick reference

| Task | Command | URL |
|------|---------|-----|
| **Run backend** | `cd backend && ./gradlew bootRun` | http://localhost:8080 |
| **Run frontend** | `cd frontend && npm run dev` | http://localhost:3000 |
| **Build backend** | `cd backend && ./gradlew clean build` | JAR in `build/libs/` |
| **Build frontend** | `cd frontend && npm run build` | Output in `frontend/dist/` |

*Prereqs:* PostgreSQL running for backend; Node/npm for frontend. Frontend proxies `/api` to backend.

---

## Run backend locally

```bash
cd backend
./gradlew bootRun
```

The API will be available at http://localhost:8080

**Note**: Make sure PostgreSQL is running and accessible. Update `application.properties` with your database credentials if needed.

## Run frontend locally

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000 (Vite default port)

**Note**: The frontend will proxy API requests to `http://localhost:8080` as configured in `vite.config.js`.

## Build backend

```bash
cd backend
./gradlew clean build
```

The JAR file will be created in `build/libs/yugioh-api-1.0.0.jar`

## Build frontend

```bash
cd frontend
npm install
npm run build
```

The production build will be created in `frontend/dist/` directory, ready to be served by a web server or Docker container.

