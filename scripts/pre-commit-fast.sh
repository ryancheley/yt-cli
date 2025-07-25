#!/usr/bin/env bash

# Pre-commit Fast Run Script
# Runs only on staged files for faster feedback during development

set -e

echo "⚡ Pre-commit Fast Run (Staged Files Only)"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if there are staged files
if git diff --cached --quiet; then
    print_warning "No files are staged for commit."
    print_status "Stage some files first with: git add <files>"
    exit 1
fi

# Get list of staged Python files
STAGED_PY_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
STAGED_ALL_FILES=$(git diff --cached --name-only --diff-filter=ACM || true)

print_status "Found $(echo "$STAGED_ALL_FILES" | wc -l | tr -d ' ') staged files"
if [ -n "$STAGED_PY_FILES" ]; then
    print_status "Found $(echo "$STAGED_PY_FILES" | wc -l | tr -d ' ') staged Python files"
fi

# Function to run command on staged files only
run_on_staged() {
    local cmd="$1"
    local description="$2"
    local files="$3"

    if [ -z "$files" ]; then
        print_warning "Skipping $description (no relevant staged files)"
        return 0
    fi

    print_status "Running $description on staged files..."
    if eval "$cmd $files"; then
        print_success "$description passed"
        return 0
    else
        print_error "$description failed"
        return 1
    fi
}

FAILED_CHECKS=()

# 1. Trailing whitespace check (on all staged files)
if [ -n "$STAGED_ALL_FILES" ]; then
    print_status "Checking trailing whitespace..."
    TRAILING_WS_FILES=""
    for file in $STAGED_ALL_FILES; do
        if [ -f "$file" ] && grep -q '[[:space:]]$' "$file" 2>/dev/null; then
            TRAILING_WS_FILES="$TRAILING_WS_FILES $file"
        fi
    done

    if [ -n "$TRAILING_WS_FILES" ]; then
        print_error "Found trailing whitespace in: $TRAILING_WS_FILES"
        print_status "Auto-fixing trailing whitespace..."
        for file in $TRAILING_WS_FILES; do
            sed -i '' 's/[[:space:]]*$//' "$file"
        done
        print_success "Trailing whitespace fixed"
    else
        print_success "No trailing whitespace found"
    fi
fi

# 2. Ruff format check (Python files only)
if [ -n "$STAGED_PY_FILES" ]; then
    if ! run_on_staged "uv run ruff format --check" "Format check" "$STAGED_PY_FILES"; then
        FAILED_CHECKS+=("format")
        print_status "Auto-fixing format issues..."
        uv run ruff format $STAGED_PY_FILES
        print_success "Format issues fixed"
    fi
fi

# 3. Ruff lint check (Python files only)
if [ -n "$STAGED_PY_FILES" ]; then
    if ! run_on_staged "uv run ruff check" "Linting" "$STAGED_PY_FILES"; then
        FAILED_CHECKS+=("lint")
        print_status "Auto-fixing linting issues..."
        if uv run ruff check --fix $STAGED_PY_FILES; then
            print_success "Auto-fixable linting issues resolved"
        else
            print_warning "Some linting issues require manual intervention"
        fi
    fi
fi

# 4. Type checking (only on Python files in youtrack_cli/)
STAGED_SRC_FILES=$(echo "$STAGED_PY_FILES" | grep '^youtrack_cli/' || true)
if [ -n "$STAGED_SRC_FILES" ]; then
    print_status "Running type checking on staged source files..."
    if uv run ty check --project youtrack_cli $STAGED_SRC_FILES 2>/dev/null; then
        print_success "Type checking passed"
    else
        print_warning "Type checking found issues (not blocking fast check)"
        FAILED_CHECKS+=("typecheck")
    fi
fi

# 5. Quick syntax check
if [ -n "$STAGED_PY_FILES" ]; then
    print_status "Running syntax check..."
    SYNTAX_OK=true
    for file in $STAGED_PY_FILES; do
        if ! python -m py_compile "$file" 2>/dev/null; then
            print_error "Syntax error in $file"
            SYNTAX_OK=false
        fi
    done

    if $SYNTAX_OK; then
        print_success "Syntax check passed"
    else
        FAILED_CHECKS+=("syntax")
    fi
fi

# 6. Check for debug statements
if [ -n "$STAGED_PY_FILES" ]; then
    print_status "Checking for debug statements..."
    DEBUG_FILES=""
    for file in $STAGED_PY_FILES; do
        if grep -l "breakpoint()\|pdb.set_trace()" "$file" 2>/dev/null; then
            DEBUG_FILES="$DEBUG_FILES $file"
        fi
    done

    if [ -n "$DEBUG_FILES" ]; then
        print_warning "Found debug statements in: $DEBUG_FILES"
        FAILED_CHECKS+=("debug")
    else
        print_success "No debug statements found"
    fi
fi

# Summary
echo ""
print_status "=========================================="
if [ ${#FAILED_CHECKS[@]} -eq 0 ]; then
    print_success "All fast checks passed! ✨"
    print_status "Your staged files are ready for commit."
    echo ""
    print_status "To commit: git commit -m 'your message'"
    print_status "To run full pre-commit: uv run pre-commit run"
else
    print_warning "Some issues found in fast check:"
    for check in "${FAILED_CHECKS[@]}"; do
        case $check in
            "format") print_warning "  • Code formatting issues (auto-fixed)" ;;
            "lint") print_warning "  • Linting issues (some auto-fixed)" ;;
            "typecheck") print_warning "  • Type checking issues" ;;
            "syntax") print_error "  • Syntax errors (must be fixed manually)" ;;
            "debug") print_warning "  • Debug statements found" ;;
        esac
    done
    echo ""
    print_status "Next steps:"
    print_status "  1. Review and stage any auto-fixes: git add ."
    print_status "  2. Fix remaining issues manually"
    print_status "  3. Run full pre-commit: uv run pre-commit run"
fi

print_status "=========================================="
