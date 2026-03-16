# 🚀 Setup and run the app

This project uses **Docker** (or **Podman**) with **docker-compose**. You only need one of the two. *No Java, Node, or Python on the host required* to run the app in containers.

**Running tests:** See [TESTS.md](TESTS.md) for per-project test commands, Podman, and native runtimes.

---

## ✅ Prerequisites

| Runtime | Install | Notes |
|---------|---------|--------|
| **Docker** | [Install Docker](https://docs.docker.com/get-docker/) (or Docker Desktop) | Ensure `docker compose` works |
| **Podman** | [Install Podman](https://podman.io/) + [Compose](https://github.com/containers/podman-compose) (e.g. `pip install podman-compose`) | Use `podman compose -f docker-compose.yml` and `podman` in place of `docker compose` and `docker` below |

---

## 📦 What to install (by platform)

### macOS (Terminal)

1. **[Homebrew](https://brew.sh)** (optional):  
   `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. **Docker:** [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/) (includes `docker compose`).  
   **Podman:** `brew install podman` then install [podman-compose](https://github.com/containers/podman-compose) (e.g. `pip install podman-compose`).
3. **Standalone compose only:** `brew install python` then `pip install docker-compose`; run `docker-compose -f docker-compose.yml up --build` from repo root.

### Other OS / native runtimes

See [DEVELOPMENT.md](DEVELOPMENT.md) for running **without containers** (Java, Node, Python on the host).

---

## 🏃 Run the app

From the **repository root**:

| Runtime | Command |
|---------|---------|
| **Docker** | `docker compose up --build` |
| **Podman** | `podman compose -f docker-compose.yml up --build` |

**First run:** The scripts service runs **migrations** (create tables) then **seed** from `data/*.csv`, then exits. Backend and frontend start after that.

### After startup — where to open

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:8082 |
| **Swagger UI** | http://localhost:8080/swagger-ui.html |
| **Health** | http://localhost:8080/healthcheck |

### Other useful commands

| Goal | Docker | Podman |
|------|--------|--------|
| **Start only DB** (e.g. for local backend) | `docker compose up -d database` | `podman compose -f docker-compose.yml up -d database` |
| **Tear down** | `docker compose down` | `podman compose -f docker-compose.yml down` |

---

## 📚 See also

- **Run tests (Docker / Podman / native):** [TESTS.md](TESTS.md)
- **Use the app (URLs, Swagger, frontend):** [GETTING_STARTED.md](GETTING_STARTED.md)
- **Local dev without containers:** [DEVELOPMENT.md](DEVELOPMENT.md)
