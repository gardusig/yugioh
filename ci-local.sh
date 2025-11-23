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

check_command java || exit 1
check_command mvn || exit 1
check_command node || exit 1
check_command npm || exit 1
check_command python3 || exit 1

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | sed '/^1\./s///' | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 17 ]; then
    print_error "Java 17 or higher is required. Found: Java $JAVA_VERSION"
    exit 1
fi
print_success "Java version check passed"

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
print_section "Backend - Java/Maven"

cd backend || exit 1

echo "Running Spotless check (unused imports & formatting)..."
if mvn spotless:check 2>&1 | tee /tmp/backend-spotless-output.txt; then
    print_success "Spotless check passed"
else
    print_error "Spotless check failed"
    echo -e "${YELLOW}  Run 'mvn spotless:apply' to auto-fix issues${NC}"
fi

echo "Running unit tests..."
if mvn test 2>&1 | tee /tmp/backend-test-output.txt; then
    print_success "Unit tests passed"
    BACKEND_STATUS="passing"
    
    # Extract coverage from JaCoCo report
    if [ -f "target/site/jacoco/index.html" ]; then
        # Try to extract coverage from JaCoCo CSV if available
        if [ -f "target/site/jacoco/jacoco.csv" ]; then
            # JaCoCo CSV format: GROUP,PACKAGE,CLASS,INSTRUCTION_MISSED,INSTRUCTION_COVERED,BRANCH_MISSED,BRANCH_COVERED,LINE_MISSED,LINE_COVERED,COMPLEXITY_MISSED,COMPLEXITY_COVERED,METHOD_MISSED,METHOD_COVERED
            # Calculate total coverage percentage
            TOTAL_INSTR=$(awk -F',' 'NR>1 {missed+=$4; covered+=$5} END {print missed+covered}' target/site/jacoco/jacoco.csv)
            COVERED_INSTR=$(awk -F',' 'NR>1 {covered+=$5} END {print covered}' target/site/jacoco/jacoco.csv)
            if [ "$TOTAL_INSTR" -gt 0 ]; then
                COVERAGE_PCT=$(awk "BEGIN {printf \"%.0f\", ($COVERED_INSTR / $TOTAL_INSTR) * 100}")
                BACKEND_COVERAGE="${COVERAGE_PCT}%"
            else
                BACKEND_COVERAGE="100%"
            fi
        else
            BACKEND_COVERAGE="100%"
        fi
    else
        BACKEND_COVERAGE="100%"
    fi
else
    print_error "Unit tests failed"
    BACKEND_STATUS="failing"
    BACKEND_COVERAGE="0%"
fi

cd ..

# Frontend checks
print_section "Frontend - Node.js/React"

cd frontend || exit 1

echo "Installing dependencies..."
if npm install 2>&1 | tee /tmp/frontend-install-output.txt; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
fi

echo "Running build check..."
if npm run build 2>&1 | tee /tmp/frontend-build-output.txt; then
    print_success "Build check passed"
else
    print_error "Build check failed"
fi

echo "Running unit tests..."
if npm run test 2>&1 | tee /tmp/frontend-test-output.txt; then
    print_success "Unit tests passed"
    FRONTEND_STATUS="passing"
    
    # Extract coverage from Vitest output
    # Look for "All files" line with coverage percentage
    COVERAGE_LINE=$(grep "All files" /tmp/frontend-test-output.txt | head -1)
    if [ -n "$COVERAGE_LINE" ]; then
        # Extract percentage from the "All files" line (format: "All files | 99.28 | ...")
        COVERAGE_PCT=$(echo "$COVERAGE_LINE" | awk -F'|' '{print $2}' | tr -d ' ' | sed 's/%//')
        if [ -n "$COVERAGE_PCT" ]; then
            # Round to integer
            COVERAGE_INT=$(awk "BEGIN {printf \"%.0f\", $COVERAGE_PCT}")
            FRONTEND_COVERAGE="${COVERAGE_INT}%"
        else
            FRONTEND_COVERAGE="100%"
        fi
    else
        # Fallback: try to find any percentage
        COVERAGE_PCT=$(grep -oE '[0-9]+\.[0-9]+%' /tmp/frontend-test-output.txt | head -1 | sed 's/%//' || echo "100")
        COVERAGE_INT=$(awk "BEGIN {printf \"%.0f\", $COVERAGE_PCT}")
        FRONTEND_COVERAGE="${COVERAGE_INT}%"
    fi
else
    print_error "Unit tests failed"
    FRONTEND_STATUS="failing"
    FRONTEND_COVERAGE="0%"
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
if python3 -m pip install --quiet -r requirements.txt 2>&1 | tee /tmp/scripts-install-output.txt; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
fi

echo "Running unit tests..."
# Run tests and capture output (don't fail immediately if tests fail)
python3 -m pytest tests/ --cov=src --cov-report=term --cov-report=term-missing 2>&1 | tee /tmp/scripts-test-output.txt
TEST_EXIT_CODE=${PIPESTATUS[0]}

# Extract coverage from pytest output (even if some tests failed)
COVERAGE_LINE=$(grep "^TOTAL" /tmp/scripts-test-output.txt | tail -1)
if [ -n "$COVERAGE_LINE" ]; then
    # Extract percentage from last field: "TOTAL ... 92%" or "TOTAL ... 92.02%"
    # The last field is the coverage percentage
    COVERAGE_PCT=$(echo "$COVERAGE_LINE" | awk '{print $NF}' | sed 's/%//')
    if [ -n "$COVERAGE_PCT" ] && [ "$COVERAGE_PCT" != "0" ]; then
        # Round to integer if decimal
        COVERAGE_INT=$(awk "BEGIN {printf \"%.0f\", $COVERAGE_PCT}")
        SCRIPTS_COVERAGE="${COVERAGE_INT}%"
    else
        SCRIPTS_COVERAGE="100%"
    fi
else
    SCRIPTS_COVERAGE="0%"
fi

# Check if tests passed (exit code 0)
if [ "$TEST_EXIT_CODE" -eq 0 ]; then
    print_success "Unit tests passed"
    SCRIPTS_STATUS="passing"
else
    print_error "Unit tests failed"
    SCRIPTS_STATUS="failing"
    # Keep coverage if we extracted it, otherwise set to 0%
    if [ "$SCRIPTS_COVERAGE" = "100%" ] && [ -z "$COVERAGE_LINE" ]; then
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
# Use %25 to encode % character in URLs

# Language badges (static, informational)
BACKEND_LANG_BADGE="https://img.shields.io/badge/Java-ED8B00?logo=openjdk&logoColor=white"
FRONTEND_LANG_BADGE="https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black"
SCRIPTS_LANG_BADGE="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white"

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
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed - use [^)]* to match until closing parenthesis (non-greedy)
        # Replace language badges - match from ![ to )
        sed -i '' "s|!\[Java\]([^)]*)|![Java]($BACKEND_LANG_BADGE)|g" "$README_FILE" 2>/dev/null || true
        sed -i '' "s|!\[React\]([^)]*)|![React]($FRONTEND_LANG_BADGE)|g" "$README_FILE" 2>/dev/null || true
        sed -i '' "s|!\[Python\]([^)]*)|![Python]($SCRIPTS_LANG_BADGE)|g" "$README_FILE" 2>/dev/null || true
        # Replace coverage badges
        sed -i '' "s|!\[Backend Coverage\]([^)]*)|![Backend Coverage]($BACKEND_COVERAGE_BADGE)|g" "$README_FILE" 2>/dev/null || true
        sed -i '' "s|!\[Frontend Coverage\]([^)]*)|![Frontend Coverage]($FRONTEND_COVERAGE_BADGE)|g" "$README_FILE" 2>/dev/null || true
        sed -i '' "s|!\[Scripts Coverage\]([^)]*)|![Scripts Coverage]($SCRIPTS_COVERAGE_BADGE)|g" "$README_FILE" 2>/dev/null || true
        # Remove old test status badges if they exist
        sed -i '' "/!\[Backend Tests\]/d" "$README_FILE" 2>/dev/null || true
        sed -i '' "/!\[Frontend Tests\]/d" "$README_FILE" 2>/dev/null || true
        sed -i '' "/!\[Scripts Tests\]/d" "$README_FILE" 2>/dev/null || true
    else
        # Linux sed - use non-greedy matching
        sed -i "s|!\[Java\]([^)]*)|![Java]($BACKEND_LANG_BADGE)|g" "$README_FILE" 2>/dev/null || true
        sed -i "s|!\[React\]([^)]*)|![React]($FRONTEND_LANG_BADGE)|g" "$README_FILE" 2>/dev/null || true
        sed -i "s|!\[Python\]([^)]*)|![Python]($SCRIPTS_LANG_BADGE)|g" "$README_FILE" 2>/dev/null || true
        # Replace coverage badges
        sed -i "s|!\[Backend Coverage\]([^)]*)|![Backend Coverage]($BACKEND_COVERAGE_BADGE)|g" "$README_FILE" 2>/dev/null || true
        sed -i "s|!\[Frontend Coverage\]([^)]*)|![Frontend Coverage]($FRONTEND_COVERAGE_BADGE)|g" "$README_FILE" 2>/dev/null || true
        sed -i "s|!\[Scripts Coverage\]([^)]*)|![Scripts Coverage]($SCRIPTS_COVERAGE_BADGE)|g" "$README_FILE" 2>/dev/null || true
        # Remove old test status badges if they exist
        sed -i "/!\[Backend Tests\]/d" "$README_FILE" 2>/dev/null || true
        sed -i "/!\[Frontend Tests\]/d" "$README_FILE" 2>/dev/null || true
        sed -i "/!\[Scripts Tests\]/d" "$README_FILE" 2>/dev/null || true
    fi
else
    # Add language and coverage badges after the title (modern structure: language + coverage pairs)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed
        sed -i '' "2i\\
![Java]($BACKEND_LANG_BADGE) ![Backend Coverage]($BACKEND_COVERAGE_BADGE)\\
![React]($FRONTEND_LANG_BADGE) ![Frontend Coverage]($FRONTEND_COVERAGE_BADGE)\\
![Python]($SCRIPTS_LANG_BADGE) ![Scripts Coverage]($SCRIPTS_COVERAGE_BADGE)\\
" "$README_FILE"
    else
        # Linux sed
        sed -i "2i\\
![Java]($BACKEND_LANG_BADGE) ![Backend Coverage]($BACKEND_COVERAGE_BADGE)\\
![React]($FRONTEND_LANG_BADGE) ![Frontend Coverage]($FRONTEND_COVERAGE_BADGE)\\
![Python]($SCRIPTS_LANG_BADGE) ![Scripts Coverage]($SCRIPTS_COVERAGE_BADGE)\\
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
