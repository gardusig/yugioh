#!/usr/bin/env bash
# Unit gate — component Docker test images (runs on host with Docker socket).
# See backend/Dockerfile, frontend/Dockerfile, scripts/Dockerfile (target: test).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "==> backend test image"
docker build -f backend/Dockerfile --target test ./backend

echo "==> frontend test image"
docker build -f frontend/Dockerfile --target test ./frontend

echo "==> scripts test image"
docker build -f scripts/Dockerfile --target test .
