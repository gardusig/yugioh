# 🧪 Tests

Dockerized unit and integration gates — same commands locally and in GitHub Actions.

---

## ⚡ Quick start

From **repo root**:

```bash
./scripts/test/unit.sh          # 2 minute timeout
./scripts/test/integration.sh     # 8 minute timeout
./scripts/test/all.sh             # both, in order
```

---

## What runs where

| Gate | Timeout | Command | What it does |
|------|---------|---------|--------------|
| **Unit** | 2 min | `./scripts/test/unit.sh` | `docker build --target test` for backend, frontend, scripts |
| **Integration** | 8 min | `./scripts/test/integration.sh` | `docker build --target builder` smoke for backend + frontend |

Orchestration lives in `scripts/docker/run-unit.sh` and `scripts/docker/run-integration.sh`.  
Per-component test steps are defined in each `Dockerfile` (`backend/`, `frontend/`, `scripts/`).

---

## Compose (alternative)

```bash
docker compose --profile test build
```

Builds all three test images in parallel (no hard timeout wrapper).

---

## CI

[`.github/workflows/test.yml`](../.github/workflows/test.yml) runs the same scripts:

1. **Unit tests (Docker)** — `./scripts/test/unit.sh` — 2 minute job timeout
2. **Integration tests (Docker)** — `./scripts/test/integration.sh` — 8 minute job timeout (after unit passes)

---

## See also

- **Setup & run app:** [SETUP_AND_TESTS.md](SETUP_AND_TESTS.md)
- **Local dev (no containers):** [DEVELOPMENT.md](DEVELOPMENT.md)
