# 🧪 Tests

Run unit tests for **backend**, **frontend**, and **scripts** the same way as GitHub Actions. **No database required.**

---

## ⚡ One command (same as CI)

From **repo root**:

```bash
docker compose --profile test build
```

Builds each project’s test image and runs its tests. *Equivalent to the per-project commands below run in sequence.*

**With Podman:** `podman compose -f docker-compose.yml --profile test build`

---

## 📋 Per-project test commands

Run tests for a single project from **repo root**:

| Project | Dockerfile | Command | Context | Notes |
|---------|------------|---------|---------|-------|
| **Backend** | [backend/Dockerfile](../backend/Dockerfile) | `docker build -f backend/Dockerfile --target test ./backend` | `./backend` | Java 21, Gradle, JUnit |
| **Frontend** | [frontend/Dockerfile](../frontend/Dockerfile) | `docker build -f frontend/Dockerfile --target test ./frontend` | `./frontend` | Node, Vitest |
| **Scripts** | [scripts/Dockerfile](../scripts/Dockerfile) | `docker build -f scripts/Dockerfile --target test .` | `.` (repo root) | Python, pytest; context is root so default stage can use `migrations/` and `data/` |

**Run all three:** chain with `&&` or use the compose command above.

**With Podman:** use `podman build` instead of `docker build` in each command (e.g. `podman build -f backend/Dockerfile --target test ./backend`).

---

## 🖥️ Native (no containers)

If you have **Java 21**, **Node 20**, and **Python 3.9+** on the host:

| Project | Command |
|---------|---------|
| **Backend** | `cd backend && ./gradlew test jacocoTestReport && cd ..` |
| **Frontend** | `cd frontend && npm ci && npm run test && cd ..` |
| **Scripts** | `cd scripts && pip install -r requirements.txt && python -m pytest tests/ --cov=src && cd ..` |

Ensure the database is running if any test expects it (scripts may have DB-dependent tests). The Docker test stage does *not* require a DB.

---

## 🔄 What CI does

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs on **pull_request** and executes the same Docker builds:

| Job | Command |
|-----|---------|
| **backend** | `docker build -f backend/Dockerfile --target test ./backend` |
| **frontend** | `docker build -f frontend/Dockerfile --target test ./frontend` |
| **scripts** | `docker build -f scripts/Dockerfile --target test .` |

All three jobs run **in parallel**. No database or secrets required.

---

## 📚 See also

- **Setup & run app:** [SETUP_AND_TESTS.md](SETUP_AND_TESTS.md)
- **Local dev (no containers):** [DEVELOPMENT.md](DEVELOPMENT.md)
