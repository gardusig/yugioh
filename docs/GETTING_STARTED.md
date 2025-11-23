# Getting Started

## Access the Application

Once the services are running, you can access:

### Frontend Web UI 🌐
- **URL**: http://localhost:8082
- **Description**: React + Tailwind CSS web interface for browsing cards and decks
- **Features**:
  - Browse all 900 cards with pagination
  - View character decks
  - Search and filter decks by archetype
  - View detailed deck compositions
  - Modern, responsive UI built with Tailwind CSS
  - Client-side routing with React Router

### Swagger UI 📚
- **URL**: http://localhost:8080/swagger-ui.html
- **Description**: Interactive API documentation
- **Features**:
  - Browse all available API endpoints
  - Test API calls directly from the browser
  - View request/response schemas
  - See example requests and responses

### API Documentation (JSON) 📄
- **URL**: http://localhost:8080/api-docs
- **Description**: OpenAPI 3.0 JSON specification
- **Use Case**: Import into API testing tools like Postman or Insomnia

### Backend API 🔌
- **URL**: http://localhost:8080
- **Description**: REST API endpoint
- **Health Check**: http://localhost:8080/healthcheck

## Services Overview

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8082 | Web interface for card browsing and deck viewing |
| **Backend API** | http://localhost:8080 | REST API endpoint (Spring Boot) |
| **Swagger UI** | http://localhost:8080/swagger-ui.html | Interactive API documentation |
| **API Docs** | http://localhost:8080/api-docs | OpenAPI 3.0 JSON specification |
| **Database** | localhost:5432 | PostgreSQL database |
| **Scripts** | N/A | Utility scripts container (run on-demand via `docker-compose run`) |

## How to Use Swagger UI

1. **Start the application**: `docker-compose up --build`
2. **Open Swagger UI**: Navigate to http://localhost:8080/swagger-ui.html in your browser
3. **Explore Endpoints**: 
   - Click on any endpoint (e.g., `GET /cards`) to expand it
   - View the endpoint description, parameters, and response schema
4. **Test API Calls**:
   - Click "Try it out" button on any endpoint
   - Modify parameters if needed (e.g., `page`, `limit`)
   - Click "Execute" to make the API call
   - View the response in the UI
5. **View Schemas**: Scroll down to see all data models (Card, Deck, etc.)

## How to Use the Frontend UI

1. **Start the application**: `docker-compose up --build`
2. **Open the Frontend**: Navigate to http://localhost:8082 in your browser
3. **Browse Cards**:
   - Click "Browse All Cards (001-900)" from the home page
   - Use pagination to navigate through cards
   - View card details including attack, defense, and cost
4. **Browse Decks**:
   - Click "View Decks & Search" from the home page
   - Use filters to find decks by archetype (Insect, Dragon, etc.)
   - Search for specific decks by name
   - Click on any deck to view full details with all cards

