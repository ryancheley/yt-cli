# YouTrack CLI Development Tasks
# Use 'just --list' to see all available commands

# Default recipe (run when just is called without arguments)
default:
    @just --list

# Development setup
[group('setup')]
install:
    #!/usr/bin/env bash
    echo "Setting up development environment..."
    uv sync --dev
    echo "✅ Development dependencies installed"

[group('setup')]
install-pre-commit:
    #!/usr/bin/env bash
    echo "Installing pre-commit hooks..."
    uv run pre-commit install
    echo "✅ Pre-commit hooks installed"

# Code quality and testing
[group('quality')]
lint:
    #!/usr/bin/env bash
    echo "Running ruff linter..."
    uv run ruff check
    echo "✅ Linting complete"

[group('quality')]
lint-fix:
    #!/usr/bin/env bash
    echo "Running ruff linter with auto-fix..."
    uv run ruff check --fix
    echo "✅ Linting with fixes complete"

[group('quality')]
format:
    #!/usr/bin/env bash
    echo "Running ruff formatter..."
    uv run ruff format
    echo "✅ Code formatting complete"

[group('quality')]
format-check:
    #!/usr/bin/env bash
    echo "Checking code formatting..."
    uv run ruff format --check
    echo "✅ Format check complete"

[group('quality')]
typecheck:
    #!/usr/bin/env bash
    echo "Running ty type checker..."
    uv run ty check --project youtrack_cli
    echo "✅ Type checking complete"

[group('quality')]
security:
    #!/usr/bin/env bash
    echo "Running security checks with zizmor..."
    uv run zizmor .github/workflows/
    echo "✅ Security check complete"

# Testing
[group('test')]
test:
    #!/usr/bin/env bash
    echo "Running pytest..."
    uv run pytest
    echo "✅ Tests complete"

[group('test')]
test-cov:
    #!/usr/bin/env bash
    echo "Running pytest with coverage..."
    uv run pytest --cov=youtrack_cli --cov-report=term-missing
    echo "✅ Tests with coverage complete"

[group('test')]
test-watch:
    #!/usr/bin/env bash
    echo "Running pytest in watch mode..."
    uv run pytest-watch
    echo "✅ Test watching stopped"

# Combined checks
[group('quality')]
check:
    #!/usr/bin/env bash
    echo "Running all quality checks..."
    just lint
    just format-check
    just typecheck
    just test
    just security
    echo "✅ All checks passed!"

[group('quality')]
fix:
    #!/usr/bin/env bash
    echo "Running auto-fixes..."
    just lint-fix
    just format
    echo "✅ Auto-fixes complete"

# Building and packaging
[group('build')]
build:
    #!/usr/bin/env bash
    echo "Building package..."
    rm -rf dist/
    uv build
    echo "✅ Package built successfully"

[group('build')]
build-check:
    #!/usr/bin/env bash
    echo "Building and checking package..."
    just build
    uv run twine check dist/*
    echo "✅ Package built and checked"

# CLI testing
[group('cli')]
run *args:
    #!/usr/bin/env bash
    echo "Running yt CLI with args: {{ args }}"
    uv run python -m youtrack_cli.main {{ args }}

[group('cli')]
help:
    #!/usr/bin/env bash
    echo "Showing yt CLI help..."
    uv run python -m youtrack_cli.main --help

[group('cli')]
version:
    #!/usr/bin/env bash
    echo "Showing yt CLI version..."
    uv run python -m youtrack_cli.main --version

# Development utilities
[group('dev')]
clean:
    #!/usr/bin/env bash
    echo "Cleaning build artifacts..."
    rm -rf dist/
    rm -rf build/
    rm -rf *.egg-info/
    rm -rf .pytest_cache/
    rm -rf .coverage
    rm -rf coverage.xml
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    echo "✅ Cleanup complete"

[group('dev')]
deps-update:
    #!/usr/bin/env bash
    echo "Updating dependencies..."
    uv sync --upgrade
    echo "✅ Dependencies updated"

[group('dev')]
deps-audit:
    #!/usr/bin/env bash
    echo "Auditing dependencies for security issues..."
    uv run pip-audit
    echo "✅ Dependency audit complete"

# Git and GitHub workflows
[group('git')]
branch name:
    #!/usr/bin/env bash
    echo "Creating new feature branch: {{ name }}"
    git checkout -b feature/{{ name }}
    echo "✅ Branch feature/{{ name }} created and checked out"

[group('git')]
pr:
    #!/usr/bin/env bash
    echo "Creating pull request..."
    gh pr create --assignee @me
    echo "✅ Pull request created"

[group('git')]
pr-checks:
    #!/usr/bin/env bash
    echo "Checking PR status..."
    gh pr checks
    echo "✅ PR checks displayed"

# Release management
[group('release')]
version-bump version:
    #!/usr/bin/env bash
    echo "Bumping version to {{ version }}..."
    sed -i '' '/^\[project\]/,/^\[/ s/^version = ".*"/version = "{{ version }}"/' pyproject.toml
    echo "✅ Version bumped to {{ version }} in pyproject.toml"
    echo "⚠️  Don't forget to commit this change before creating a release tag"

[group('release')]
tag version:
    #!/usr/bin/env bash
    echo "Creating and pushing release tag v{{ version }}..."
    git tag v{{ version }}
    git push origin v{{ version }}
    echo "✅ Release tag v{{ version }} created and pushed"
    echo "🚀 GitHub Actions will now build and publish to PyPI"

[group('release')]
release version:
    #!/usr/bin/env bash
    echo "🚀 Creating release {{ version }}..."

    # Pre-flight checks
    echo "🔍 Running pre-release checks..."

    # Check if we're on main branch
    if [ "$(git branch --show-current)" != "main" ]; then
        echo "❌ Must be on main branch for releases"
        exit 1
    fi

    # Check if working directory is clean
    if [ -n "$(git status --porcelain)" ]; then
        echo "❌ Working directory is not clean. Please commit or stash changes."
        git status --short
        exit 1
    fi

    # Check if we're up to date with remote
    git fetch origin main
    if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
        echo "❌ Local main branch is not up to date with origin/main"
        echo "Please run: git pull origin main"
        exit 1
    fi

    # Run quality checks
    echo "🔍 Running quality checks..."
    just check

    echo "✅ Pre-flight checks passed"

    # Version bump and commit
    echo "📝 Updating version to {{ version }}..."
    just version-bump {{ version }}

    # Update uv.lock if it exists
    if [ -f "uv.lock" ]; then
        echo "🔄 Updating uv.lock..."
        uv sync
    fi

    # Stage all changes (pyproject.toml and uv.lock)
    git add pyproject.toml uv.lock

    # Create commit
    git commit -m "🔖 Bump version to {{ version }}"

    # Push commit
    echo "⬆️  Pushing version bump commit..."
    git push origin main

    # Create and push tag
    echo "🏷️  Creating and pushing tag..."
    just tag {{ version }}

    echo "✅ Release {{ version }} created and published!"
    echo "🔗 Monitor release progress: https://github.com/ryancheley/yt-cli/actions"
    echo "📦 Package will be available at: https://pypi.org/project/youtrack-cli/{{ version }}/"

[group('release')]
release-check version:
    #!/usr/bin/env bash
    echo "🔍 Pre-release validation for version {{ version }}..."

    # Check version format
    if ! echo "{{ version }}" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
        echo "❌ Invalid version format. Use semantic versioning (e.g., 1.2.3)"
        exit 1
    fi

    # Check if version already exists
    if git tag -l | grep -q "^v{{ version }}$"; then
        echo "❌ Version {{ version }} already exists as a git tag"
        exit 1
    fi

    # Check current version in pyproject.toml
    current_version=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    echo "📋 Current version: $current_version"
    echo "📋 Target version: {{ version }}"

    # Verify it's a version bump
    if [ "$current_version" = "{{ version }}" ]; then
        echo "❌ Target version is the same as current version"
        exit 1
    fi

    # Check what type of release this is
    IFS='.' read -r curr_major curr_minor curr_patch <<< "$current_version"
    IFS='.' read -r new_major new_minor new_patch <<< "{{ version }}"

    if [ "$new_major" -gt "$curr_major" ]; then
        echo "🚨 MAJOR version bump detected (breaking changes)"
    elif [ "$new_minor" -gt "$curr_minor" ]; then
        echo "✨ MINOR version bump detected (new features)"
    elif [ "$new_patch" -gt "$curr_patch" ]; then
        echo "🐛 PATCH version bump detected (bug fixes)"
    else
        echo "❌ Version is not a proper increment"
        exit 1
    fi

    echo "✅ Version {{ version }} is valid for release"

[group('release')]
release-status:
    #!/usr/bin/env bash
    echo "📊 Release Status Check"
    echo "======================"

    # Current version
    current_version=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    echo "📋 Current version: $current_version"

    # Check if there are unreleased changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  Uncommitted changes present:"
        git status --short
    else
        echo "✅ Working directory clean"
    fi

    # Check recent commits since last tag
    last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "No tags found")
    if [ "$last_tag" != "No tags found" ]; then
        echo "🏷️  Last tag: $last_tag"
        commit_count=$(git rev-list ${last_tag}..HEAD --count)
        echo "📈 Commits since last tag: $commit_count"

        if [ "$commit_count" -gt 0 ]; then
            echo "📝 Recent changes:"
            git log --oneline ${last_tag}..HEAD | head -5
        fi
    else
        echo "🏷️  No previous tags found"
    fi

    # Check GitHub Actions status
    echo ""
    echo "🤖 Recent GitHub Actions:"
    gh run list --limit 3 2>/dev/null || echo "⚠️  GitHub CLI not available or not authenticated"

[group('release')]
rollback-release version:
    #!/usr/bin/env bash
    echo "⚠️  Rolling back release {{ version }}..."
    echo "This will:"
    echo "  1. Delete the git tag v{{ version }}"
    echo "  2. Revert the version bump commit"
    echo ""
    read -p "Are you sure? This cannot be undone. [y/N]: " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Delete remote tag
        echo "🗑️  Deleting remote tag..."
        git push origin :refs/tags/v{{ version }} || echo "Tag may not exist on remote"

        # Delete local tag
        git tag -d v{{ version }} 2>/dev/null || echo "Local tag may not exist"

        # Revert last commit if it's a version bump
        last_commit_msg=$(git log -1 --pretty=%B)
        if echo "$last_commit_msg" | grep -q "Bump version to {{ version }}"; then
            echo "⏪ Reverting version bump commit..."
            git reset --hard HEAD~1
            echo "⬆️  Force pushing to remote..."
            git push --force-with-lease origin main
        else
            echo "⚠️  Last commit doesn't appear to be the version bump for {{ version }}"
            echo "    Manual intervention may be required"
        fi

        echo "✅ Rollback completed"
        echo "⚠️  Note: If the release was already published to PyPI, you'll need to create a new version"
    else
        echo "❌ Rollback cancelled"
    fi

# Documentation
[group('docs')]
docs-install:
    #!/usr/bin/env bash
    echo "Installing documentation dependencies..."
    uv sync --extra docs
    echo "✅ Documentation dependencies installed"

[group('docs')]
docs-build:
    #!/usr/bin/env bash
    echo "Building documentation..."
    cd docs && uv run make html
    echo "✅ Documentation built successfully"
    echo "📖 Open docs/_build/html/index.html to view"

[group('docs')]
docs-serve:
    #!/usr/bin/env bash
    echo "Building and serving documentation with live reload..."
    cd docs && uv run make livehtml
    echo "🌐 Documentation server started at http://127.0.0.1:8000"

[group('docs')]
docs-clean:
    #!/usr/bin/env bash
    echo "Cleaning documentation build..."
    cd docs && uv run make clean
    echo "✅ Documentation build cleaned"

[group('docs')]
docs-check:
    #!/usr/bin/env bash
    echo "Checking documentation for broken links..."
    cd docs && uv run make linkcheck
    echo "✅ Documentation link check complete"

[group('docs')]
docs-test:
    #!/usr/bin/env bash
    echo "Testing documentation build..."
    just docs-clean
    just docs-build
    echo "✅ Documentation test complete"

[group('docs')]
readme-update:
    #!/usr/bin/env bash
    echo "Updating README.md..."
    echo "⚠️  Remember to update README.md with any new features or changes"
    echo "📝 Current CLI help:"
    just help

# Troubleshooting
[group('help')]
doctor:
    #!/usr/bin/env bash
    echo "🔍 Running project health checks..."
    echo ""
    echo "📦 Python version:"
    python --version
    echo ""
    echo "📦 UV version:"
    uv --version
    echo ""
    echo "📦 Git status:"
    git status --porcelain || echo "Not in a git repository"
    echo ""
    echo "📦 Virtual environment:"
    uv run python -c "import sys; print(f'Python: {sys.executable}')"
    echo ""
    echo "📦 Package installation check:"
    uv run python -c "import youtrack_cli; print('✅ youtrack_cli package importable')" || echo "❌ youtrack_cli package not importable"
    echo ""
    echo "📦 Dependencies check:"
    uv run python -c "import rich, textual, pydantic, click, httpx; print('✅ All main dependencies importable')" || echo "❌ Some dependencies missing"
    echo ""
    echo "🏥 Health check complete"

[group('help')]
workflow-help:
    #!/usr/bin/env bash
    echo "🔄 Development Workflow Help"
    echo ""
    echo "📋 Common development tasks:"
    echo "  just install           # Set up development environment"
    echo "  just check             # Run all quality checks"
    echo "  just fix               # Auto-fix code issues"
    echo "  just test              # Run tests"
    echo "  just run --help        # Test the CLI"
    echo ""
    echo "📚 Documentation tasks:"
    echo "  just docs-install      # Install documentation dependencies"
    echo "  just docs-build        # Build documentation"
    echo "  just docs-serve        # Serve docs with live reload"
    echo "  just docs-test         # Test documentation build"
    echo ""
    echo "🌟 Starting a new feature:"
    echo "  just branch my-feature # Create feature branch"
    echo "  # ... make changes ..."
    echo "  just check             # Verify changes"
    echo "  git add . && git commit -m 'feat: my feature'"
    echo "  git push origin feature/my-feature"
    echo "  just pr                # Create pull request"
    echo ""
    echo "🚀 Creating a release:"
    echo "  just release-check 0.2.3  # Validate version and check readiness"
    echo "  just release-status        # Check current status and recent changes"
    echo "  just release 0.2.3         # Full automated release process"
    echo "  just rollback-release 0.2.3  # Emergency rollback (if needed)"
    echo ""
    echo "🆘 Troubleshooting:"
    echo "  just doctor            # Check project health"
    echo "  just clean             # Clean build artifacts"
    echo "  just install           # Reinstall dependencies"
