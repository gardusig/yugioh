# Frontend — Yu-Gi-Oh! Card Browser

Web UI for browsing cards and decks. **Stack:** React 18, Vite 5, Tailwind CSS.

## Focus

Browse cards, view decks, search by archetype, and inspect deck details.

## First-Time Setup

### Option A: Docker (recommended)

From the **project root**:

```bash
docker-compose up --build
```

Frontend: http://localhost:8082

### Option B: Local development

1. **Prerequisites:** Node.js 20+, npm
2. **Backend:** Ensure API is running at http://localhost:8080
3. **Run:**

```bash
cd frontend
npm install
npm run dev
```

Dev server: http://localhost:3000 (proxies `/api` to backend).

## Run Container Standalone

```bash
# From project root
docker build -f frontend/Dockerfile -t yugioh-frontend ./frontend
docker run -p 8082:80 \
  -e API_URL=http://localhost:8080 \
  yugioh-frontend
```

Note: The built image proxies `/api/` to `backend:8080`. For standalone use, you may need to adjust nginx config or run behind a reverse proxy.

## Build & Test

```bash
npm install
npm run build
npm run test
```

## URLs

- **Production (Docker):** http://localhost:8082
- **Dev:** http://localhost:3000
