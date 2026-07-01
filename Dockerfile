# Yu-Gi-Oh! Deck Editor — Docker pipeline (local + GitHub Actions).
#
# Test:    ./scripts/test/all.sh
# Deploy:  ./scripts/deploy/deploy.sh
# Release: ./scripts/release/build.sh
#
# Targets: unit (2m) | integration (8m) | deploy | release
# Unit/integration/release orchestrate backend/, frontend/, scripts/ Dockerfiles via Docker socket.

FROM docker:27-cli AS base
RUN apk add --no-cache bash
WORKDIR /repo
COPY . .

FROM base AS unit
RUN chmod +x scripts/docker/run-unit.sh
CMD ["./scripts/docker/run-unit.sh"]

FROM base AS integration
RUN chmod +x scripts/docker/run-integration.sh
CMD ["./scripts/docker/run-integration.sh"]

FROM python:3.12-slim AS deploy
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY scripts/docker/run-deploy.sh /usr/local/bin/run-deploy.sh
RUN chmod +x /usr/local/bin/run-deploy.sh
WORKDIR /repo
CMD ["run-deploy.sh"]

FROM docker:27-cli AS release
RUN apk add --no-cache bash zip
WORKDIR /repo
COPY . .
RUN chmod +x scripts/docker/run-release.sh
CMD ["./scripts/docker/run-release.sh"]
