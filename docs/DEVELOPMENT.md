# Development

## Local CI Checks

Before pushing code, you can run the same checks that GitHub Actions will run:

```bash
# Run all CI checks locally and update README badges
./ci-local.sh
```

This script will:
- **Backend**: Check for unused imports (Spotless Gradle plugin) and run unit tests (using Mockito mocks, no database required)
- **Frontend**: Install dependencies, build check (Vite), run unit tests (Vitest), and check for unused dependencies
- **Scripts**: Run Python unit tests with coverage
- **Badges**: Automatically update README badges with current test status and coverage percentages (green if tests pass, red if they fail)

**Note**: All tests use mocks and don't require a running database. The README badges will be updated with the actual coverage percentages from test results (e.g., 60% shown as green if tests pass).

## Run Backend Locally

```bash
cd backend
./gradlew bootRun
```

The API will be available at http://localhost:8080

**Note**: Make sure PostgreSQL is running and accessible. Update `application.properties` with your database credentials if needed.

## Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000 (Vite default port)

**Note**: The frontend will proxy API requests to `http://localhost:8080` as configured in `vite.config.js`.

## Build Backend

```bash
cd backend
./gradlew clean build
```

The JAR file will be created in `build/libs/yugioh-api-1.0.0.jar`

## Build Frontend

```bash
cd frontend
npm install
npm run build
```

The production build will be created in `frontend/dist/` directory, ready to be served by a web server or Docker container.

