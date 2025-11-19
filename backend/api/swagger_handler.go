package api

import (
	"net/http"
)

// SwaggerHandler serves Swagger UI
type SwaggerHandler struct{}

// NewSwaggerHandler creates a new swagger handler
func NewSwaggerHandler() *SwaggerHandler {
	return &SwaggerHandler{}
}

// ServeSwaggerUI serves the Swagger UI HTML
func (h *SwaggerHandler) ServeSwaggerUI(w http.ResponseWriter, r *http.Request) {
	swaggerHTML := `<!DOCTYPE html>
<html>
<head>
    <title>Yu-Gi-Oh! API - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui.css" />
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin:0;
            background: #fafafa;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: "/swagger.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            });
        };
    </script>
</body>
</html>`
	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte(swaggerHTML))
}

// ServeSwaggerJSON serves the Swagger JSON spec
func (h *SwaggerHandler) ServeSwaggerJSON(w http.ResponseWriter, r *http.Request) {
	swaggerJSON := `{
  "openapi": "3.0.0",
  "info": {
    "title": "Yu-Gi-Oh! The Sacred Cards API",
    "version": "1.0.0",
    "description": "API for browsing all 900 cards and character decks from Yu-Gi-Oh! The Sacred Cards"
  },
  "servers": [
    {
      "url": "http://localhost:8080",
      "description": "Local development server"
    }
  ],
  "paths": {
    "/cards": {
      "get": {
        "summary": "List all cards",
        "description": "Get a paginated list of all cards (001-900)",
        "parameters": [
          {
            "name": "page",
            "in": "query",
            "schema": {
              "type": "integer",
              "default": 1,
              "minimum": 1
            },
            "description": "Page number"
          },
          {
            "name": "limit",
            "in": "query",
            "schema": {
              "type": "integer",
              "default": 24,
              "minimum": 1,
              "maximum": 100
            },
            "description": "Number of cards per page"
          }
        ],
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/CardsResponse"
                }
              }
            }
          }
        }
      }
    },
    "/cards/{id}": {
      "get": {
        "summary": "Get card by ID",
        "description": "Get detailed information about a specific card",
        "parameters": [
          {
            "name": "id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "integer"
            },
            "description": "Card ID (001-900)"
          }
        ],
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Card"
                }
              }
            }
          },
          "404": {
            "description": "Card not found"
          }
        }
      }
    },
    "/decks": {
      "get": {
        "summary": "List all decks",
        "description": "Get a paginated list of all decks",
        "parameters": [
          {
            "name": "page",
            "in": "query",
            "schema": {
              "type": "integer",
              "default": 1,
              "minimum": 1
            },
            "description": "Page number"
          },
          {
            "name": "limit",
            "in": "query",
            "schema": {
              "type": "integer",
              "default": 20,
              "minimum": 1,
              "maximum": 100
            },
            "description": "Number of decks per page"
          },
          {
            "name": "archetype",
            "in": "query",
            "schema": {
              "type": "string"
            },
            "description": "Filter by deck archetype"
          },
          {
            "name": "preset",
            "in": "query",
            "schema": {
              "type": "boolean"
            },
            "description": "Filter preset decks only"
          }
        ],
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/DecksResponse"
                }
              }
            }
          }
        }
      }
    },
    "/decks/{id}": {
      "get": {
        "summary": "Get deck by ID",
        "description": "Get detailed information about a specific deck with all cards",
        "parameters": [
          {
            "name": "id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "integer"
            },
            "description": "Deck ID"
          }
        ],
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/DeckWithCards"
                }
              }
            }
          },
          "404": {
            "description": "Deck not found"
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "Card": {
        "type": "object",
        "properties": {
          "id": {
            "type": "integer",
            "description": "Card number (001-900)"
          },
          "name": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "image": {
            "type": "string",
            "format": "uri"
          },
          "type": {
            "type": "string",
            "enum": ["Monster", "Spell", "Trap"]
          },
          "attribute": {
            "type": "string",
            "enum": ["Dark", "Light", "Earth", "Water", "Fire", "Wind", "Divine"]
          },
          "race": {
            "type": "string",
            "description": "Monster race (Dragon, Spellcaster, Warrior, etc.)"
          },
          "level": {
            "type": "integer",
            "minimum": 0,
            "maximum": 12
          },
          "attack_points": {
            "type": "integer"
          },
          "defense_points": {
            "type": "integer"
          },
          "cost": {
            "type": "integer"
          },
          "rarity": {
            "type": "string",
            "enum": ["Common", "Rare", "Super Rare", "Ultra Rare"]
          }
        }
      },
      "CardsResponse": {
        "type": "object",
        "properties": {
          "cards": {
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/Card"
            }
          },
          "pagination": {
            "$ref": "#/components/schemas/Pagination"
          }
        }
      },
      "DeckSummary": {
        "type": "object",
        "properties": {
          "id": {
            "type": "integer"
          },
          "name": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "character_name": {
            "type": "string"
          },
          "archetype": {
            "type": "string"
          },
          "max_cost": {
            "type": "integer"
          },
          "total_cost": {
            "type": "integer"
          },
          "card_count": {
            "type": "integer"
          },
          "is_preset": {
            "type": "boolean"
          }
        }
      },
      "DeckWithCards": {
        "type": "object",
        "properties": {
          "id": {
            "type": "integer"
          },
          "name": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "character_name": {
            "type": "string"
          },
          "archetype": {
            "type": "string"
          },
          "cards": {
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/Card"
            }
          },
          "max_cost": {
            "type": "integer"
          },
          "total_cost": {
            "type": "integer"
          },
          "is_preset": {
            "type": "boolean"
          }
        }
      },
      "DecksResponse": {
        "type": "object",
        "properties": {
          "decks": {
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/DeckSummary"
            }
          },
          "pagination": {
            "$ref": "#/components/schemas/Pagination"
          }
        }
      },
      "Pagination": {
        "type": "object",
        "properties": {
          "page": {
            "type": "integer"
          },
          "limit": {
            "type": "integer"
          },
          "total": {
            "type": "integer"
          },
          "totalPages": {
            "type": "integer"
          }
        }
      }
    }
  }
}`
	w.Header().Set("Content-Type", "application/json")
	w.Write([]byte(swaggerJSON))
}

