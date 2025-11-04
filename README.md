A full-stack application with a Go back-end API, Swagger UI documentation, and a front-end web interface.

## Prerequisites

Before running this project, you need to install:

1. **Docker Desktop** - For containerization
2. **Go** (optional) - Only needed if you want to run the API locally without Docker

## Installation

### 1. Install Docker Desktop

On macOS, install Docker using Homebrew:

```bash
brew install --cask docker
```

After installation:
1. Open Docker Desktop from Applications
2. Wait for Docker to start (you'll see the Docker icon in your menu bar)
3. Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

### 2. Install Go (Optional)

If you want to run the back-end API locally without Docker:

```bash
brew install go
```

Verify installation:
```bash
go version
```

## Running the Project

### Option 1: Using Docker Compose (Recommended)

This is the easiest way to run the entire stack:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up --build -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Stop and remove containers, networks, and volumes
docker-compose down -v
```

### Option 2: Run Back-end Locally (Without Docker)

If you want to develop the Go API locally:

```bash
cd back-end-api
go run main.go
```

The API will be available at `http://localhost:8080`

**Note:** Running locally won't include the Swagger UI or front-end containers. You'll need to run those separately or use Docker Compose.

## Accessing the Services

Once all services are running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Front-end UI** | http://localhost:8082 | Main web interface to interact with the API |
| **Swagger UI** | http://localhost:8081 | Interactive API documentation |
| **Back-end API** | http://localhost:8080 | REST API endpoints |

