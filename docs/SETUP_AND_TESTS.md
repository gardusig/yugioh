# Setup and Running Tests

This project uses **Docker** (or **Podman**) with **docker-compose**. The snippets below use `docker compose` and `docker`; with Podman use `podman compose -f docker-compose.yml` and `podman` in place of `docker compose` and `docker`.

---

## Prerequisites

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/) (or Docker Desktop). Ensure `docker compose` works.
- **Podman** (optional): [Install Podman](https://podman.io/) and the [Compose plugin](https://github.com/containers/podman-compose); use `podman compose` and `podman` in the commands below if you prefer.

You only need one of the two. No need to install Java, Node, or Python on the host to run the app or tests in containers.

### What to install (by platform)

**macOS (Terminal):**

1. [Homebrew](https://brew.sh) (optional but useful):  
   `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. **Docker:** [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/) (includes `docker compose`).  
   **Podman:** `brew install podman` then [Compose](https://github.com/containers/podman-compose) (e.g. `pip install podman-compose`).
3. **Standalone compose only:** `brew install python` then `pip install docker-compose`; run `docker-compose -f docker-compose.yml up --build` from repo root.

**Other OS / native runtimes:** See [DEVELOPMENT.md](DEVELOPMENT.md) for running without containers (Java, Node, Python on the host).

---

## Setup from scratch

From the **repository root**:

```bash
# Start all services (database → scripts → backend → frontend)
docker compose up --build
```

*With Podman: `podman compose -f docker-compose.yml up --build`.*

- **First run**: The scripts service runs **migrations** (create tables) then **seed** from `data/*.csv`, then exits. The backend and frontend start after that.
- **Frontend**: http://localhost:8082  
- **Backend / Swagger**: http://localhost:8080 (e.g. http://localhost:8080/swagger-ui.html)  
- **Health**: http://localhost:8080/healthcheck  

To start only the database (e.g. for running scripts or backend locally):

```bash
docker compose up -d database
```

To tear everything down:

```bash
docker compose down
```

---

## Running tests

Tests run **inside containers**; no database is required. Use `docker` in the commands below; with Podman, use `podman` instead of `docker`.

### Backend (Java/Gradle)

From repo root:

```bash
docker build -f backend/Dockerfile --target test ./backend
```

### Frontend (Node/Vitest)

From repo root:

```bash
docker build -f frontend/Dockerfile --target test ./frontend
```

### Scripts (Python/pytest)

From repo root (context is repo root so the same Dockerfile can build the run image with migrations/data):

```bash
docker build -f scripts/Dockerfile --target test .
```

### Run all three test stages

From repo root (same as GitHub Actions CI):

```bash
docker build -f backend/Dockerfile --target test ./backend && \
docker build -f frontend/Dockerfile --target test ./frontend && \
docker build -f scripts/Dockerfile --target test .
```

Or use the test profile in the main compose file:

```bash
docker compose --profile test build
```
