# CI and tests

## Running the same tests as CI

CI runs unit tests for **backend**, **frontend**, and **scripts** on every pull request. Run the same batch locally:

### One command (same as CI)

From repo root:

```bash
docker compose --profile test build
```

Each service builds that project's test image; the build runs the unit tests. No database required. With Podman: `podman compose --profile test build` (or use `podman build` per project below).

### Per project (Docker)

From repo root:

```bash
docker build -f backend/Dockerfile --target test ./backend
docker build -f frontend/Dockerfile --target test ./frontend
docker build -f scripts/Dockerfile --target test .
```

(Backend and frontend use context `./backend` and `./frontend`; scripts use context `.` so migrations and data are available for the default stage.)

**Run all three:** append with `&&` or use the compose command above. With Podman, use `podman build` instead of `docker build`.

### Native (optional)

If you have Java 21, Node 20, and Python 3.9+ on the host:

```bash
cd backend && ./gradlew test jacocoTestReport && cd ..
cd frontend && npm ci && npm run test && cd ..
cd scripts && pip install -r requirements.txt && python -m pytest tests/ --cov=src && cd ..
```

## What CI does

[`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs on **pull_request** and executes the same Docker builds:

| Project  | Command |
|----------|---------|
| backend  | `docker build -f backend/Dockerfile --target test ./backend` |
| frontend | `docker build -f frontend/Dockerfile --target test ./frontend` |
| scripts  | `docker build -f scripts/Dockerfile --target test .` |

All three jobs run in parallel. No database or secrets required.
