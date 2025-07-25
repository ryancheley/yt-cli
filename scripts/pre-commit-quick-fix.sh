#!/usr/bin/env bash

# Pre-commit Quick Fix Script
# Automatically fixes common pre-commit failures

set -e

echo "🔧 Pre-commit Quick Fix Script"
echo "==============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository!"
    exit 1
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install uv first."
    exit 1
fi

print_status "Starting quick fixes for common pre-commit issues..."

# 1. Fix formatting issues (most common)
print_status "1. Fixing code formatting with ruff..."
if uv run ruff format .; then
    print_success "Code formatting fixed"
else
    print_warning "Some formatting issues may remain"
fi

# 2. Fix linting issues that can be auto-fixed
print_status "2. Auto-fixing linting issues..."
if uv run ruff check --fix .; then
    print_success "Auto-fixable linting issues resolved"
else
    print_warning "Some linting issues require manual intervention"
fi

# 3. Fix trailing whitespace and end-of-file issues
print_status "3. Fixing whitespace and EOF issues..."
find . -name "*.py" -not -path "./.*" -not -path "./build/*" -not -path "./dist/*" -exec sed -i '' 's/[[:space:]]*$//' {} \;
find . -name "*.py" -not -path "./.*" -not -path "./build/*" -not -path "./dist/*" -exec sh -c 'if [ -s "$1" ] && [ "$(tail -c1 "$1")" != "" ]; then echo "" >> "$1"; fi' _ {} \;
print_success "Whitespace and EOF issues fixed"

# 4. Fix import sorting
print_status "4. Sorting imports..."
if uv run ruff check --select I --fix .; then
    print_success "Import sorting completed"
else
    print_warning "Some import issues may remain"
fi

# 5. Check for common issues
print_status "5. Checking for debug statements..."
if grep -r "breakpoint()" youtrack_cli/ 2>/dev/null; then
    print_warning "Found breakpoint() statements that should be removed"
fi

if grep -r "pdb.set_trace()" youtrack_cli/ 2>/dev/null; then
    print_warning "Found pdb.set_trace() statements that should be removed"
fi

# 6. Try to fix YAML/TOML formatting
print_status "6. Validating configuration files..."
for file in *.toml *.yaml *.yml; do
    if [ -f "$file" ]; then
        case "$file" in
            *.toml)
                if command -v toml-sort &> /dev/null; then
                    toml-sort "$file" --all --in-place
                    print_success "Sorted $file"
                fi
                ;;
            *.yaml|*.yml)
                # Basic YAML validation
                if uv run python -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                    print_success "$file is valid YAML"
                else
                    print_warning "$file may have YAML syntax issues"
                fi
                ;;
        esac
    fi
done

# 7. Run a quick pre-commit check on staged files only
print_status "7. Running pre-commit on staged files..."
if git diff --cached --quiet; then
    print_warning "No staged files found. Stage your changes with 'git add' first."
else
    if uv run pre-commit run --hook-stage=pre-commit; then
        print_success "Pre-commit checks passed on staged files!"
    else
        print_error "Some pre-commit checks still failing. See output above."
        echo ""
        echo "Common next steps:"
        echo "  • Fix remaining linting errors manually"
        echo "  • Check type annotations with: uv run ty check youtrack_cli/"
        echo "  • Run tests with: uv run pytest"
        echo "  • Check docstrings with: uv run pydocstyle youtrack_cli/"
        exit 1
    fi
fi

print_success "Quick fix completed! Your code should now pass most pre-commit checks."
print_status "Run 'git add .' and 'git commit' to proceed with your commit."
