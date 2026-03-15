# Python 3.11 for data management scripts (migrations, CSV seed)
# Build from repo root: docker build -f scripts/Dockerfile .
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY scripts/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts, migrations, and data (preserves repo structure for path resolution)
COPY scripts ./scripts
COPY data ./data

# Run from project root so PROJECT_ROOT = /app, data = /app/data
ENTRYPOINT ["python3"]
CMD ["scripts/src/setup.py"]
