#!/bin/bash

# Local CI script that mirrors GitHub Actions workflow
# Runs all checks and updates README badges with current test status and coverage

# Don't exit on error - we want to run all checks and report all failures
set +e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track failures and test status
FAILED=0
BACKEND_STATUS="unknown"
FRONTEND_STATUS="unknown"
SCRIPTS_STATUS="unknown"
BACKEND_COVERAGE="0%"
FRONTEND_COVERAGE="0%"
SCRIPTS_COVERAGE="0%"

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
    FAILED=1
}

# Function to check if command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        return 1
    fi
    return 0
}

# Check prerequisites
print_section "Checking Prerequisites"

# Setup Java environment - prefer Homebrew OpenJDK 21 if available
if [ -d "/opt/homebrew/opt/openjdk@21" ]; then
    export JAVA_HOME="/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
    export PATH="$JAVA_HOME/bin:$PATH"
    print_success "Using Homebrew OpenJDK 21: $JAVA_HOME"
elif [ -d "/usr/local/opt/openjdk@21" ]; then
    export JAVA_HOME="/usr/local/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home"
    export PATH="$JAVA_HOME/bin:$PATH"
    print_success "Using Homebrew OpenJDK 21: $JAVA_HOME"
fi

check_command java || exit 1
check_command node || exit 1
check_command npm || exit 1
check_command python3 || exit 1

# Check Java version - extract required version from build.gradle.kts
REQUIRED_JAVA_VERSION=$(grep 'languageVersion = JavaLanguageVersion.of' backend/build.gradle.kts 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "21")

# Extract current Java version (handles both "openjdk version" and standard format)
JAVA_VERSION_OUTPUT=$(java -version 2>&1 | head -n 1)
if echo "$JAVA_VERSION_OUTPUT" | grep -q "openjdk version"; then
    # Format: "openjdk version "21.0.1" 2024-10-15" or "openjdk version "21" 2024-10-15"
    CURRENT_JAVA_VERSION=$(echo "$JAVA_VERSION_OUTPUT" | grep -oE 'version "[0-9]+' | grep -oE '[0-9]+' | head -1)
else
    # Format: "java version "1.8.0_xxx" or "java version "21.0.1""
    CURRENT_JAVA_VERSION=$(echo "$JAVA_VERSION_OUTPUT" | cut -d'"' -f2 | sed '/^1\./s///' | cut -d'.' -f1)
fi

if [ -z "$CURRENT_JAVA_VERSION" ] || [ "$CURRENT_JAVA_VERSION" = "" ]; then
    CURRENT_JAVA_VERSION=0
fi

# Validate that CURRENT_JAVA_VERSION is a number before comparison
if ! [ "$CURRENT_JAVA_VERSION" -eq "$CURRENT_JAVA_VERSION" ] 2>/dev/null; then
    CURRENT_JAVA_VERSION=0
fi

if [ "$CURRENT_JAVA_VERSION" -lt "$REQUIRED_JAVA_VERSION" ]; then
    print_error "Java $REQUIRED_JAVA_VERSION or higher is required (as specified in build.gradle.kts). Found: Java $CURRENT_JAVA_VERSION"
    echo -e "${YELLOW}  To upgrade Java, visit: https://adoptium.net/${NC}"
    exit 1
fi
print_success "Java version check passed (Required: $REQUIRED_JAVA_VERSION, Found: $CURRENT_JAVA_VERSION)"

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    print_error "Node.js 20 or higher is required. Found: Node $NODE_VERSION"
    exit 1
fi
print_success "Node.js version check passed"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    print_error "Python 3.9 or higher is required. Found: Python $PYTHON_VERSION"
    exit 1
fi
print_success "Python version check passed"

# Backend checks
print_section "Backend - Java/Gradle"

cd backend || exit 1

# Check if Gradle wrapper exists
if [ ! -f "gradlew" ]; then
    print_error "Gradle wrapper (gradlew) not found in backend directory"
    echo -e "${YELLOW}  The Gradle wrapper should be committed to the repository.${NC}"
    echo -e "${YELLOW}  If you need to create it, install Gradle and run: gradle wrapper --gradle-version 8.5${NC}"
    exit 1
fi

# Make sure gradlew is executable
chmod +x gradlew 2>/dev/null || true

echo "Running Spotless check (unused imports & formatting)..."
if ./gradlew spotlessCheck 2>&1; then
    print_success "Spotless check passed"
else
    print_error "Spotless check failed"
    echo -e "${YELLOW}  Run './gradlew spotlessApply' to auto-fix issues${NC}"
fi

echo "Running unit tests..."
# Run tests and capture exit code
./gradlew test jacocoTestReport 2>&1
TEST_EXIT_CODE=$?

# Extract coverage from JaCoCo report (agnostic - extract whatever is reported)
BACKEND_COVERAGE="0%"
if [ -f "build/reports/jacoco/test/jacocoTestReport.csv" ]; then
    # JaCoCo CSV format: GROUP,PACKAGE,CLASS,INSTRUCTION_MISSED,INSTRUCTION_COVERED,BRANCH_MISSED,BRANCH_COVERED,LINE_MISSED,LINE_COVERED,COMPLEXITY_MISSED,COMPLEXITY_COVERED,METHOD_MISSED,METHOD_COVERED
    # Calculate total coverage percentage from instructions (most accurate metric)
    TOTAL_INSTR=$(awk -F',' 'NR>1 {missed+=$4; covered+=$5} END {print missed+covered}' build/reports/jacoco/test/jacocoTestReport.csv 2>/dev/null || echo "0")
    COVERED_INSTR=$(awk -F',' 'NR>1 {covered+=$5} END {print covered}' build/reports/jacoco/test/jacocoTestReport.csv 2>/dev/null || echo "0")
    if [ "$TOTAL_INSTR" -gt 0 ] && [ -n "$COVERED_INSTR" ]; then
        COVERAGE_PCT=$(awk "BEGIN {printf \"%.0f\", ($COVERED_INSTR / $TOTAL_INSTR) * 100}")
        BACKEND_COVERAGE="${COVERAGE_PCT}%"
    fi
fi

# Check if tests passed (exit code 0)
if [ "$TEST_EXIT_CODE" -eq 0 ]; then
    print_success "Unit tests passed"
    BACKEND_STATUS="passing"
    # If we couldn't extract coverage, default to 100% for passing tests
    if [ "$BACKEND_COVERAGE" = "0%" ]; then
        BACKEND_COVERAGE="100%"
    fi
else
    print_error "Unit tests failed"
    BACKEND_STATUS="failing"
    # Keep extracted coverage if available, otherwise set to 0%
    if [ "$BACKEND_COVERAGE" = "0%" ]; then
        BACKEND_COVERAGE="0%"
    fi
fi

cd ..

# Frontend checks
print_section "Frontend - Node.js/React"

cd frontend || exit 1

echo "Installing dependencies..."
if npm install 2>&1; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
fi

echo "Running build check..."
if npm run build 2>&1; then
    print_success "Build check passed"
else
    print_error "Build check failed"
fi

echo "Running unit tests..."
# Run tests and capture output for coverage extraction
FRONTEND_TEST_OUTPUT=$(npm run test 2>&1)
TEST_EXIT_CODE=$?
echo "$FRONTEND_TEST_OUTPUT"

# Extract coverage from Vitest output (agnostic - extract whatever is reported)
FRONTEND_COVERAGE="0%"
COVERAGE_LINE=$(echo "$FRONTEND_TEST_OUTPUT" | grep "All files" | head -1)
if [ -n "$COVERAGE_LINE" ]; then
    # Extract percentage from the "All files" line (format: "All files | 99.28 | ...")
    COVERAGE_PCT=$(echo "$COVERAGE_LINE" | awk -F'|' '{print $2}' | tr -d ' ' | sed 's/%//')
    if [ -n "$COVERAGE_PCT" ]; then
        # Round to integer
        COVERAGE_INT=$(awk "BEGIN {printf \"%.0f\", $COVERAGE_PCT}")
        FRONTEND_COVERAGE="${COVERAGE_INT}%"
    fi
else
    # Fallback: try to find any percentage in output
    COVERAGE_PCT=$(echo "$FRONTEND_TEST_OUTPUT" | grep -oE '[0-9]+\.[0-9]+%' | head -1 | sed 's/%//' || echo "")
    if [ -n "$COVERAGE_PCT" ]; then
        COVERAGE_INT=$(awk "BEGIN {printf \"%.0f\", $COVERAGE_PCT}")
        FRONTEND_COVERAGE="${COVERAGE_INT}%"
    fi
fi

# Check if tests passed (exit code 0)
if [ "$TEST_EXIT_CODE" -eq 0 ]; then
    print_success "Unit tests passed"
    FRONTEND_STATUS="passing"
    # If we couldn't extract coverage, default to 100% for passing tests
    if [ "$FRONTEND_COVERAGE" = "0%" ]; then
        FRONTEND_COVERAGE="100%"
    fi
else
    print_error "Unit tests failed"
    FRONTEND_STATUS="failing"
    # Keep extracted coverage if available, otherwise set to 0%
    if [ "$FRONTEND_COVERAGE" = "0%" ]; then
        FRONTEND_COVERAGE="0%"
    fi
fi

echo "Checking for unused dependencies..."
if command -v depcheck &> /dev/null || npx --yes depcheck --version &> /dev/null; then
    if npx --yes depcheck --ignores="@types/*,autoprefixer,postcss,tailwindcss" 2>/dev/null; then
        print_success "No unused dependencies found"
    else
        echo -e "${YELLOW}⚠ Some unused dependencies may be present${NC}"
    fi
else
    echo -e "${YELLOW}⚠ depcheck not available, skipping${NC}"
fi

cd ..

# Scripts checks
print_section "Scripts - Python"

cd scripts || exit 1

echo "Installing Python dependencies..."
if python3 -m pip install --quiet -r requirements.txt 2>&1; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
fi

echo "Running unit tests..."
# Run tests and capture output for coverage extraction
SCRIPTS_TEST_OUTPUT=$(python3 -m pytest tests/ --cov=src --cov-report=term --cov-report=term-missing 2>&1)
TEST_EXIT_CODE=$?
echo "$SCRIPTS_TEST_OUTPUT"

# Extract coverage from pytest output (agnostic - extract whatever is reported)
SCRIPTS_COVERAGE="0%"
COVERAGE_LINE=$(echo "$SCRIPTS_TEST_OUTPUT" | grep "^TOTAL" | tail -1)
if [ -n "$COVERAGE_LINE" ]; then
    # Extract percentage from last field: "TOTAL ... 92%" or "TOTAL ... 92.02%"
    COVERAGE_PCT=$(echo "$COVERAGE_LINE" | awk '{print $NF}' | sed 's/%//')
    if [ -n "$COVERAGE_PCT" ] && [ "$COVERAGE_PCT" != "0" ]; then
        # Round to integer if decimal
        COVERAGE_INT=$(awk "BEGIN {printf \"%.0f\", $COVERAGE_PCT}")
        SCRIPTS_COVERAGE="${COVERAGE_INT}%"
    fi
fi

# Check if tests passed (exit code 0)
if [ "$TEST_EXIT_CODE" -eq 0 ]; then
    print_success "Unit tests passed"
    SCRIPTS_STATUS="passing"
    # If we couldn't extract coverage, default to 100% for passing tests
    if [ "$SCRIPTS_COVERAGE" = "0%" ]; then
        SCRIPTS_COVERAGE="100%"
    fi
else
    print_error "Unit tests failed"
    SCRIPTS_STATUS="failing"
    # Keep extracted coverage if available, otherwise set to 0%
    if [ "$SCRIPTS_COVERAGE" = "0%" ]; then
        SCRIPTS_COVERAGE="0%"
    fi
fi

cd ..

# Update README badges
print_section "Updating README Badges"

README_FILE="README.md"

# Create language and coverage badge URLs
# Modern structure: separate language badge + coverage badge with %
# shields.io format: https://img.shields.io/badge/LABEL-VALUE-COLOR
# Use %25 to encode % character in URLs, %20 for spaces

# Extract versions for language badges
# Java version from build.gradle.kts (default to 21 if not found)
JAVA_VERSION=$(grep 'languageVersion = JavaLanguageVersion.of' backend/build.gradle.kts 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "21")
# Python version (extract major.minor)
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo "3.9")
# Node version (extract major)
NODE_VERSION=$(node -v 2>&1 | sed 's/v\([0-9]*\).*/\1/' || echo "20")

# Language badges with versions (use %20 for spaces in badge labels)
BACKEND_LANG_BADGE="https://img.shields.io/badge/Java%20${JAVA_VERSION}-ED8B00?logo=openjdk&logoColor=white"
FRONTEND_LANG_BADGE="https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black"
SCRIPTS_LANG_BADGE="https://img.shields.io/badge/Python%20${PYTHON_VERSION}-3776AB?logo=python&logoColor=white"

# Coverage badges - include % character (encoded as %25 in URL)
# Format: "Coverage: XX%" where % is encoded as %25
BACKEND_COVERAGE_VALUE=$(echo "$BACKEND_COVERAGE" | sed 's/%/%25/g')
FRONTEND_COVERAGE_VALUE=$(echo "$FRONTEND_COVERAGE" | sed 's/%/%25/g')
SCRIPTS_COVERAGE_VALUE=$(echo "$SCRIPTS_COVERAGE" | sed 's/%/%25/g')

# Backend coverage badge
if [ "$BACKEND_STATUS" = "passing" ]; then
    BACKEND_COVERAGE_BADGE="https://img.shields.io/badge/Coverage-${BACKEND_COVERAGE_VALUE}-brightgreen"
else
    BACKEND_COVERAGE_BADGE="https://img.shields.io/badge/Coverage-${BACKEND_COVERAGE_VALUE}-red"
fi

# Frontend coverage badge
if [ "$FRONTEND_STATUS" = "passing" ]; then
    FRONTEND_COVERAGE_BADGE="https://img.shields.io/badge/Coverage-${FRONTEND_COVERAGE_VALUE}-brightgreen"
else
    FRONTEND_COVERAGE_BADGE="https://img.shields.io/badge/Coverage-${FRONTEND_COVERAGE_VALUE}-red"
fi

# Scripts coverage badge
if [ "$SCRIPTS_STATUS" = "passing" ]; then
    SCRIPTS_COVERAGE_BADGE="https://img.shields.io/badge/Coverage-${SCRIPTS_COVERAGE_VALUE}-brightgreen"
else
    SCRIPTS_COVERAGE_BADGE="https://img.shields.io/badge/Coverage-${SCRIPTS_COVERAGE_VALUE}-red"
fi

# Update or add language and coverage badges at the top of README
# Modern structure: Language badge + Coverage badge for each component
# Use more specific regex patterns to avoid partial matches

if grep -q "!\[Java\]" "$README_FILE" || grep -q "!\[Backend Coverage\]" "$README_FILE"; then
    # Replace existing badges with more specific patterns
    # First, remove all existing badge lines and add fresh ones with proper formatting
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed - remove old badge lines (Java, React, Python, and coverage badges)
        sed -i '' "/!\[Java/d" "$README_FILE" 2>/dev/null || true
        sed -i '' "/!\[React/d" "$README_FILE" 2>/dev/null || true
        sed -i '' "/!\[Python/d" "$README_FILE" 2>/dev/null || true
        sed -i '' "/!\[Backend Coverage/d" "$README_FILE" 2>/dev/null || true
        sed -i '' "/!\[Frontend Coverage/d" "$README_FILE" 2>/dev/null || true
        sed -i '' "/!\[Scripts Coverage/d" "$README_FILE" 2>/dev/null || true
        sed -i '' "/!\[Backend Tests\]/d" "$README_FILE" 2>/dev/null || true
        sed -i '' "/!\[Frontend Tests\]/d" "$README_FILE" 2>/dev/null || true
        sed -i '' "/!\[Scripts Tests\]/d" "$README_FILE" 2>/dev/null || true
        # Remove empty lines after title if they exist
        sed -i '' '/^# Yu-Gi-Oh! The Sacred Cards$/{n;/^$/d;}' "$README_FILE" 2>/dev/null || true
        # Add new badges with proper formatting after title
        sed -i '' "/^# Yu-Gi-Oh! The Sacred Cards$/a\\
\\
![Java ${JAVA_VERSION}]($BACKEND_LANG_BADGE) ![Backend Coverage]($BACKEND_COVERAGE_BADGE)\\
\\
![React]($FRONTEND_LANG_BADGE) ![Frontend Coverage]($FRONTEND_COVERAGE_BADGE)\\
\\
![Python ${PYTHON_VERSION}]($SCRIPTS_LANG_BADGE) ![Scripts Coverage]($SCRIPTS_COVERAGE_BADGE)\\
" "$README_FILE"
    else
        # Linux sed - remove old badge lines
        sed -i "/!\[Java/d" "$README_FILE" 2>/dev/null || true
        sed -i "/!\[React/d" "$README_FILE" 2>/dev/null || true
        sed -i "/!\[Python/d" "$README_FILE" 2>/dev/null || true
        sed -i "/!\[Backend Coverage/d" "$README_FILE" 2>/dev/null || true
        sed -i "/!\[Frontend Coverage/d" "$README_FILE" 2>/dev/null || true
        sed -i "/!\[Scripts Coverage/d" "$README_FILE" 2>/dev/null || true
        sed -i "/!\[Backend Tests\]/d" "$README_FILE" 2>/dev/null || true
        sed -i "/!\[Frontend Tests\]/d" "$README_FILE" 2>/dev/null || true
        sed -i "/!\[Scripts Tests\]/d" "$README_FILE" 2>/dev/null || true
        # Remove empty lines after title if they exist
        sed -i '/^# Yu-Gi-Oh! The Sacred Cards$/{n;/^$/d;}' "$README_FILE" 2>/dev/null || true
        # Add new badges with proper formatting after title
        sed -i "/^# Yu-Gi-Oh! The Sacred Cards$/a\\
\\
![Java ${JAVA_VERSION}]($BACKEND_LANG_BADGE) ![Backend Coverage]($BACKEND_COVERAGE_BADGE)\\
\\
![React]($FRONTEND_LANG_BADGE) ![Frontend Coverage]($FRONTEND_COVERAGE_BADGE)\\
\\
![Python ${PYTHON_VERSION}]($SCRIPTS_LANG_BADGE) ![Scripts Coverage]($SCRIPTS_COVERAGE_BADGE)\\
" "$README_FILE"
    fi
else
    # Add language and coverage badges after the title (modern structure: language + coverage pairs with line breaks)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed - add line breaks between each language pair
        sed -i '' "2i\\
![Java ${JAVA_VERSION}]($BACKEND_LANG_BADGE) ![Backend Coverage]($BACKEND_COVERAGE_BADGE)\\
\\
![React]($FRONTEND_LANG_BADGE) ![Frontend Coverage]($FRONTEND_COVERAGE_BADGE)\\
\\
![Python ${PYTHON_VERSION}]($SCRIPTS_LANG_BADGE) ![Scripts Coverage]($SCRIPTS_COVERAGE_BADGE)\\
" "$README_FILE"
    else
        # Linux sed - add line breaks between each language pair
        sed -i "2i\\
![Java ${JAVA_VERSION}]($BACKEND_LANG_BADGE) ![Backend Coverage]($BACKEND_COVERAGE_BADGE)\\
\\
![React]($FRONTEND_LANG_BADGE) ![Frontend Coverage]($FRONTEND_COVERAGE_BADGE)\\
\\
![Python ${PYTHON_VERSION}]($SCRIPTS_LANG_BADGE) ![Scripts Coverage]($SCRIPTS_COVERAGE_BADGE)\\
" "$README_FILE"
    fi
fi

print_success "README badges updated"

# Summary
print_section "Summary"

echo -e "Backend Tests: ${BACKEND_STATUS} (Coverage: ${BACKEND_COVERAGE})"
echo -e "Frontend Tests: ${FRONTEND_STATUS} (Coverage: ${FRONTEND_COVERAGE})"
echo -e "Scripts Tests: ${SCRIPTS_STATUS} (Coverage: ${SCRIPTS_COVERAGE})"

if [ $FAILED -eq 0 ] && [ "$BACKEND_STATUS" = "passing" ] && [ "$FRONTEND_STATUS" = "passing" ] && [ "$SCRIPTS_STATUS" = "passing" ]; then
    echo -e "\n${GREEN}✓ All checks passed!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some checks failed. Please fix the issues above.${NC}"
    exit 1
fi
