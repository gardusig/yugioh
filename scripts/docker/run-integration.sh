#!/usr/bin/env bash
# Integration gate — production build smoke for backend and frontend images.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "==> backend builder image"
docker build -f backend/Dockerfile --target builder ./backend

echo "==> frontend builder image"
docker build -f frontend/Dockerfile --target builder ./frontend
