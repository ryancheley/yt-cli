#!/usr/bin/env bash

# Pre-commit Doctor Script
# Diagnoses pre-commit issues and suggests fixes

set -e

echo "🏥 Pre-commit Doctor - Diagnostic Tool"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN} $1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

print_check() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_fix() {
    echo -e "${CYAN}[FIX]${NC} $1"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository!"
    exit 1
fi

print_header "Environment Check"

# Check uv installation
print_check "Checking uv installation..."
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    print_success "uv is installed: $UV_VERSION"
else
    print_error "uv is not installed"
    print_fix "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check Python version
print_check "Checking Python version..."
PYTHON_VERSION=$(uv run python --version 2>&1)
if [[ $PYTHON_VERSION == *"3.9"* ]] || [[ $PYTHON_VERSION == *"3.1"* ]]; then
    print_success "Python version compatible: $PYTHON_VERSION"
else
    print_warning "Python version may not be compatible: $PYTHON_VERSION"
    print_fix "This project requires Python 3.9+"
fi

# Check virtual environment
print_check "Checking virtual environment..."
if uv run python -c "import sys; print('Virtual env:' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'System Python')" | grep -q "Virtual env"; then
    print_success "Running in virtual environment"
else
    print_warning "Not running in virtual environment"
    print_fix "uv should handle this automatically"
fi

print_header "Dependencies Check"

# Check if dependencies are installed
print_check "Checking development dependencies..."
MISSING_DEPS=()

deps=("ruff" "pytest" "ty" "pydocstyle" "pre-commit" "zizmor")
for dep in "${deps[@]}"; do
    if uv run python -c "import $dep" 2>/dev/null; then
        print_success "$dep is available"
    else
        print_error "$dep is not available"
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    print_fix "Install missing dependencies: uv sync --dev"
fi

print_header "Pre-commit Configuration Check"

# Check if pre-commit is installed
print_check "Checking pre-commit installation..."
if [ -f ".git/hooks/pre-commit" ]; then
    print_success "Pre-commit hooks are installed"
else
    print_error "Pre-commit hooks are not installed"
    print_fix "Install hooks: uv run pre-commit install"
fi

# Check pre-commit config
print_check "Checking .pre-commit-config.yaml..."
if [ -f ".pre-commit-config.yaml" ]; then
    print_success ".pre-commit-config.yaml exists"

    # Validate YAML syntax
    if uv run python -c "import yaml; yaml.safe_load(open('.pre-commit-config.yaml'))" 2>/dev/null; then
        print_success "Pre-commit config has valid YAML syntax"
    else
        print_error "Pre-commit config has YAML syntax errors"
        print_fix "Check YAML syntax in .pre-commit-config.yaml"
    fi
else
    print_error ".pre-commit-config.yaml not found"
    print_fix "Create .pre-commit-config.yaml file"
fi

print_header "Code Quality Tools Check"

# Check ruff configuration
print_check "Checking ruff configuration..."
if uv run ruff check --help >/dev/null 2>&1; then
    print_success "Ruff is working"

    # Test ruff on a sample file
    if ls youtrack_cli/*.py >/dev/null 2>&1; then
        SAMPLE_FILE=$(ls youtrack_cli/*.py | head -1)
        if uv run ruff check "$SAMPLE_FILE" >/dev/null 2>&1; then
            print_success "Ruff check passes on sample file"
        else
            print_warning "Ruff found issues in code"
            print_fix "Run: uv run ruff check --fix ."
        fi
    fi
else
    print_error "Ruff is not working properly"
fi

# Check type checker
print_check "Checking ty type checker..."
if uv run ty --help >/dev/null 2>&1; then
    print_success "ty is working"

    # Test ty on project
    if uv run ty check --project youtrack_cli >/dev/null 2>&1; then
        print_success "Type checking passes"
    else
        print_warning "Type checking found issues"
        print_fix "Run: uv run ty check --project youtrack_cli"
    fi
else
    print_error "ty is not working properly"
fi

# Check pytest
print_check "Checking pytest..."
if uv run pytest --version >/dev/null 2>&1; then
    print_success "pytest is working"

    # Check if tests exist
    if [ -d "tests" ] && [ "$(ls -A tests/)" ]; then
        print_success "Test directory exists and has tests"
    else
        print_warning "No tests found in tests/ directory"
    fi
else
    print_error "pytest is not working properly"
fi

print_header "Common Issues Check"

# Check for common problematic patterns
print_check "Checking for debug statements..."
if grep -r "breakpoint()\|pdb.set_trace()\|print(" youtrack_cli/ 2>/dev/null | grep -v "__pycache__" | head -5; then
    print_warning "Found debug statements or print calls"
    print_fix "Remove debug statements before committing"
else
    print_success "No debug statements found"
fi

# Check for trailing whitespace
print_check "Checking for trailing whitespace..."
if grep -r "[[:space:]]$" youtrack_cli/ 2>/dev/null | head -5 | grep -v "__pycache__"; then
    print_warning "Found trailing whitespace"
    print_fix "Run: ./scripts/pre-commit-quick-fix.sh"
else
    print_success "No trailing whitespace found"
fi

# Check file permissions
print_check "Checking file permissions..."
if find . -name "*.py" -perm +111 2>/dev/null | grep -v "__pycache__" | head -5; then
    print_warning "Found Python files with execute permissions"
    print_fix "Remove execute permissions: find . -name '*.py' -exec chmod -x {} +"
else
    print_success "Python file permissions are correct"
fi

# Check for large files
print_check "Checking for large files..."
LARGE_FILES=$(find . -type f -size +1M -not -path "./.git/*" -not -path "./.*" 2>/dev/null | head -5)
if [ -n "$LARGE_FILES" ]; then
    print_warning "Found large files:"
    echo "$LARGE_FILES"
    print_fix "Consider using Git LFS for large files"
else
    print_success "No large files found"
fi

print_header "Git Status Check"

# Check git status
print_check "Checking git status..."
if git status --porcelain | grep -q .; then
    print_warning "Working directory has uncommitted changes:"
    git status --short
    print_fix "Stage changes with: git add ."
else
    print_success "Working directory is clean"
fi

# Check if there are staged files
if git diff --cached --quiet; then
    print_warning "No files are staged for commit"
    print_fix "Stage files with: git add <file>"
else
    print_success "Files are staged for commit"
fi

print_header "Recommendations"

echo "Based on the diagnosis above, here are recommended actions:"
echo ""

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "1. 🔧 Install missing dependencies:"
    echo "   uv sync --dev"
    echo ""
fi

if [ ! -f ".git/hooks/pre-commit" ]; then
    echo "2. ⚙️  Install pre-commit hooks:"
    echo "   uv run pre-commit install"
    echo ""
fi

echo "3. 🚀 Run quick fixes for common issues:"
echo "   ./scripts/pre-commit-quick-fix.sh"
echo ""

echo "4. 🧪 Run a full check:"
echo "   uv run pre-commit run --all-files"
echo ""

echo "5. 📋 For specific issues:"
echo "   • Format code: uv run ruff format ."
echo "   • Fix linting: uv run ruff check --fix ."
echo "   • Check types: uv run ty check --project youtrack_cli"
echo "   • Run tests: uv run pytest"
echo ""

print_success "Diagnosis complete! Follow the recommendations above to fix any issues."
