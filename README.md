# Yu-Gi-Oh! Deck Editor

![Java 21](https://img.shields.io/badge/Java%2021-ED8B00?logo=openjdk&logoColor=white) ![Backend Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen)  
![React 18.2](https://img.shields.io/badge/React%2018.2-61DAFB?logo=react&logoColor=black) ![Frontend Coverage](https://img.shields.io/badge/Coverage-99%25-brightgreen)  
![Python 3.9](https://img.shields.io/badge/Python%203.9-3776AB?logo=python&logoColor=white) ![Scripts Coverage](https://img.shields.io/badge/Coverage-99%25-brightgreen)

Full-stack app for browsing cards and building decks: **Spring Boot** API, **PostgreSQL**, **React** frontend, **Python** scripts for data. Everything runs with **Docker** (or Podman). You get card browsing with pagination, deck list and composition (40 cards), card details, and Swagger API docs; the DB can be reset, migrated, and seeded from CSV.

---

## Quick start

1. **Prereqs:** [Docker](https://docs.docker.com/get-docker/) (or [Podman](https://podman.io/) + Compose). On macOS you can use [Homebrew](https://brew.sh) and [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/).
2. **Run the app** (from repo root):
   ```bash
   docker compose up --build
   ```
3. **Open:** [Frontend](http://localhost:8082) · [Swagger UI](http://localhost:8080/swagger-ui.html) · [Health](http://localhost:8080/healthcheck)  
   First run runs migrations and seeds the DB from CSV automatically.
4. **Run tests** (same as CI, no DB):
   ```bash
   docker compose --profile test build
   ```

*(With Podman: `podman compose -f docker-compose.yml up --build` and `podman compose -f docker-compose.yml --profile test build`.)*

---

## Index

- [Quick start](#quick-start)
- [Setup (detailed)](#setup-detailed)
- [Run & links](#run--links)
- [Tests](#tests)
- [Per-project](#per-project)
- [Documentation guide](#documentation-guide)

---

## Setup (detailed)

Use **Docker** or **Podman**; no Java/Node/Python on the host required for the commands above.

**macOS (Terminal):**

1. [Homebrew](https://brew.sh):  
   `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. **Docker:** [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/) (includes `docker compose`).  
   **Podman:** `brew install podman` then [Compose](https://github.com/containers/podman-compose) (e.g. `pip install podman-compose`).
3. **Standalone compose only:** `brew install python` then `pip install docker-compose`; run `docker-compose -f docker-compose.yml up --build` from repo root.

More options (native runtimes, other OS): [docs/SETUP_AND_TESTS.md](docs/SETUP_AND_TESTS.md).

---

## Run & links

| Link | Description |
|------|-------------|
| [**Frontend**](http://localhost:8082) | Cards grid, decks list; click a card for details, a deck for composition. |
| [**Swagger UI**](http://localhost:8080/swagger-ui.html) | Interactive API docs; try `GET /cards`, `GET /decks`. |
| [**Health**](http://localhost:8080/healthcheck) | Backend health check. |

---

## Tests

Run all project tests the same way as GitHub Actions (no DB):

```bash
docker compose --profile test build
```

Per project (from repo root):  
`docker build -f backend/Dockerfile --target test ./backend` · same for `frontend` with `./frontend` · for scripts: `docker build -f scripts/Dockerfile --target test .`

Details and native runtimes: [.github/README.md](.github/README.md) and [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

---

## Per-project

| Project | Dockerfile | README |
|---------|------------|--------|
| Backend | [backend/Dockerfile](backend/Dockerfile) | [backend/README.md](backend/README.md) |
| Frontend | [frontend/Dockerfile](frontend/Dockerfile) | [frontend/README.md](frontend/README.md) |
| Scripts | [scripts/Dockerfile](scripts/Dockerfile) (stages: test, default; build from repo root) | [scripts/README.md](scripts/README.md) |

---

## Documentation guide

Use this to find the right doc. All live in **[docs/](docs/)** unless noted.

| When you want to… | Open |
|-------------------|------|
| **Get running** — setup, run app, run tests (Docker/Podman) | [SETUP_AND_TESTS](docs/SETUP_AND_TESTS.md) |
| **Use the app** — URLs, Swagger, frontend usage | [GETTING_STARTED](docs/GETTING_STARTED.md) |
| **Work on code** — run backend/frontend locally (no containers) | [DEVELOPMENT](docs/DEVELOPMENT.md) |
| **Database** — reset, migrate, seed, check data | [DATABASE_MAINTENANCE](docs/DATABASE_MAINTENANCE.md) |
| **Schema** — migrations, adding tables | [DATABASE_MIGRATIONS](docs/DATABASE_MIGRATIONS.md) |
| **API** — endpoints, request/response examples | [API_ENDPOINTS](docs/API_ENDPOINTS.md) |
| **Layout** — where things are in the repo | [PROJECT_STRUCTURE](docs/PROJECT_STRUCTURE.md) |
| **Problems** — common errors and fixes | [TROUBLESHOOTING](docs/TROUBLESHOOTING.md) |
| **Stack** — technologies and tools | [TECHNOLOGY_STACK](docs/TECHNOLOGY_STACK.md) |
| **CI / tests** — run tests like GitHub Actions | [.github/README](.github/README.md) |
| **Docs index** — list of all docs | [docs/README](docs/README.md) |
| **License** | [LICENSE](docs/LICENSE.md) |

---

## Website preview

Screenshots (add images under [docs/screenshots/](docs/screenshots/)):

| Page | Preview |
|------|---------|
| Cards | [cards-page.png](docs/screenshots/cards-page.png) |
| Card detail | [card-detail.png](docs/screenshots/card-detail.png) |
| Decks list | [decks-list.png](docs/screenshots/decks-list.png) |
| Deck detail | [deck-detail.png](docs/screenshots/deck-detail.png) |
| Swagger UI | [swagger-ui.png](docs/screenshots/swagger-ui.png) |

*(Links work once the image files exist in `docs/screenshots/`.)*
