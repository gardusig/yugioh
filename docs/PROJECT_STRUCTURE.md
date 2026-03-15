# Project Structure

```
.
├── backend/                          # Java Spring Boot backend (web server only)
│   ├── src/main/java/com/yugioh/
│   │   ├── YugiohApplication.java   # Main application class
│   │   ├── config/                  # Configuration classes
│   │   ├── controller/             # REST controllers
│   │   ├── service/                 # Business logic services
│   │   ├── repository/              # JPA repositories
│   │   ├── model/                   # Entity models
│   │   └── dto/                     # Data transfer objects
│   ├── src/main/resources/
│   │   ├── application.properties    # Application configuration
│   │   └── application.properties   # App config (schema via scripts migrations)
│   ├── build.gradle.kts              # Gradle build configuration
│   ├── settings.gradle.kts           # Gradle settings
│   └── Dockerfile                   # Backend container definition
├── frontend/                        # React + Tailwind CSS frontend
│   ├── src/                         # React source code
│   │   ├── pages/                   # Page components
│   │   ├── components/              # Reusable components
│   │   └── api/                     # API integration layer
│   ├── public/                      # Static assets
│   ├── package.json                 # Node.js dependencies
│   ├── vite.config.js               # Vite build configuration
│   ├── tailwind.config.js           # Tailwind CSS configuration
│   └── Dockerfile                   # Frontend container definition
├── scripts/                         # Utility scripts and tools (Python)
│   ├── src/                         # Source scripts
│   │   ├── db_manager.py            # Reset, clear, seed, status
│   │   ├── run_migrations.py       # Run database migrations
│   │   ├── seed_from_csv.py        # Seed from data/*.csv
│   │   ├── generate_cards_csv.py  # Generate cards.csv from card_list
│   │   └── ...                      # Other utility scripts
│   ├── migrations/                  # SQL migrations (Flyway-style)
│   │   └── V1__initial_schema.sql
│   ├── tests/                       # Unit tests
│   ├── Dockerfile                   # Scripts container (build from repo root)
│   └── README.md                    # Scripts documentation
├── data/                            # Data files (CSV files)
│   ├── README.md                    # Data format and setup docs
│   ├── card_list.csv                # Card IDs and names
│   ├── cards.csv                    # Full card data (from generate_cards_csv.py)
│   ├── decks.csv                    # Deck metadata
│   └── deck_cards.csv               # Deck contents (deck_name, card_id, position)
└── docker-compose.yml               # Service orchestration
```

