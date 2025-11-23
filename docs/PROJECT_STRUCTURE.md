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
│   │   └── db/migration/             # Flyway database migrations
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
│   │   ├── crawl_cards.py           # Card data crawler
│   │   ├── db_manager.py            # Reset/clear/seed helper
│   │   ├── gather_card_data.py      # Gather card data to CSV
│   │   └── ...                      # Other utility scripts
│   ├── tests/                       # Unit tests
│   ├── Dockerfile                   # Scripts container definition
│   └── README.md                    # Scripts documentation
├── data/                            # Data files (CSV files)
│   ├── card_list.csv                # Card names list
│   └── cards_data.csv               # Complete card data (generated)
└── docker-compose.yml               # Service orchestration
```

