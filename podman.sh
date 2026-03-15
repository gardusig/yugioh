#!/usr/bin/env bash
# Run compose with Podman if available, otherwise Docker.
# Usage: ./podman.sh [up|down|build|...]
# Examples:
#   ./podman.sh up --build
#   ./podman.sh run --rm scripts scripts/src/db_manager.py status

set -e

if command -v podman &>/dev/null; then
    if podman compose version &>/dev/null; then
        exec podman compose -f docker-compose.yml "$@"
    elif command -v podman-compose &>/dev/null; then
        exec podman-compose -f docker-compose.yml "$@"
    else
        echo "Podman found but no compose. Falling back to Docker..." >&2
    fi
fi

if command -v docker &>/dev/null; then
    if docker compose version &>/dev/null; then
        exec docker compose -f docker-compose.yml "$@"
    else
        exec docker-compose -f docker-compose.yml "$@"
    fi
else
    echo "Neither Podman (with compose) nor Docker found. Install:" >&2
    echo "  - Podman 4.1+ with compose plugin, or pip install podman-compose" >&2
    echo "  - Docker or Docker Desktop" >&2
    exit 1
fi
