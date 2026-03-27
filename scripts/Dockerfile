# Yu-Gi-Oh! Deck Editor — Scripts (Python 3.11)
# Build from repo root. Stages: test (unit tests), default (run migrations + seed).
#   Tests:  docker build -f scripts/Dockerfile --target test .
#   Run:    docker build -f scripts/Dockerfile .   (used by docker compose)

# Stage: test — run unit tests (no DB)
FROM python:3.11-slim AS test
WORKDIR /app
COPY scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY scripts ./scripts
WORKDIR /app/scripts
RUN python -m pytest tests -v

# Stage: default — run scripts (migrations, seed, or any script)
FROM python:3.11-slim
WORKDIR /app
COPY scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY scripts ./scripts
COPY migrations ./migrations
COPY data ./data
ENTRYPOINT ["python3"]
CMD ["scripts/src/setup.py"]
