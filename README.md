# YouTrack CLI

A powerful command line interface for JetBrains YouTrack issue tracking system.

[![Documentation Status](https://readthedocs.org/projects/yt-cli/badge/?version=latest)](https://yt-cli.readthedocs.io/en/latest/?badge=latest)

## Features

- **Complete YouTrack Management**: Issues, articles, projects, users, time tracking, boards, and reporting
- **Enterprise Security Features**: Command audit logging, credential encryption, token expiration warnings
- **Flexible Authentication**: Secure token-based authentication with keyring integration
- **Rich Output Formats**: Beautiful tables and JSON export for automation
- **Progress Indicators**: Visual feedback for long-running operations with Rich progress bars
- **Comprehensive Configuration**: Customizable defaults and environment-specific settings
- **Administrative Tools**: System management, user groups, and health monitoring
- **Developer-Friendly**: Built with modern Python practices and extensive documentation
- **Enhanced Error Handling**: User-friendly error messages with actionable suggestions
- **Advanced Logging**: Rich logging with debug and verbose modes for troubleshooting
- **Robust HTTP Operations**: Automatic retry logic with exponential backoff for reliability

## Quick Start

### Installation

#### Using uv (Recommended)

The fastest and most reliable way to install YouTrack CLI:

```bash
# Install uv first (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install YouTrack CLI as a tool
uv tool install youtrack-cli

# Verify installation
yt --version
```

#### Traditional pip installation

```bash
# From PyPI (when available)
pip install yt-cli

# With virtual environment (recommended for pip)
python -m venv youtrack-env
source youtrack-env/bin/activate  # Linux/macOS
# or
youtrack-env\Scripts\activate     # Windows
pip install yt-cli
```

#### Development installation

```bash
# Clone and set up for development
git clone https://github.com/YOUR_USERNAME/yt-cli.git
cd yt-cli

# Using uv (recommended)
uv sync --dev
uv pip install -e .

# Or using pip (requires pip >= 24.0 for PEP 735 support)
pip install -e . --group dev
```

### Authentication

```bash
# Login to your YouTrack instance
yt auth login

# Login with SSL certificate verification disabled (for self-signed certificates)
yt auth login --no-verify-ssl

# Verify authentication
yt auth token --show
```

### Shell Completion

YouTrack CLI supports tab completion for bash, zsh, and fish shells:

```bash
# Enable shell completion (see docs for full instructions)
yt completion bash --install
```

📖 **[Complete shell completion guide](https://yt-cli.readthedocs.io/en/latest/installation.html#shell-completion)**

### Basic Usage

```bash
# List projects
yt projects list

# Create an article
yt articles create "Getting Started" --content "Welcome to our documentation"

# Create an article from a markdown file
yt articles create "API Documentation" --file api-docs.md

# Log work time
yt time log ISSUE-123 "2h" --description "Feature development"

# Generate reports with progress indicators
yt reports burndown PROJECT-123

# Disable progress indicators for automation
yt --no-progress reports velocity PROJECT-123

# Enable debug logging for troubleshooting
yt --debug issues list
```

## Documentation

**📚 [Complete Documentation](https://yt-cli.readthedocs.io/en/latest/)**

For comprehensive guides, examples, and API reference, visit our documentation:

- **[Quick Start Guide](https://yt-cli.readthedocs.io/en/latest/quickstart.html)** - Get up and running quickly
- **[Command Reference](https://yt-cli.readthedocs.io/en/latest/commands/)** - Detailed documentation for all commands
- **[Configuration Guide](https://yt-cli.readthedocs.io/en/latest/configuration.html)** - Customize your CLI experience
- **[Development Guide](https://yt-cli.readthedocs.io/en/latest/development.html)** - Contributing and development setup

## Available Commands

| Command Group | Description |
|--------------|-------------|
| `yt issues` | Complete issue lifecycle management with search, comments, and relationships |
| `yt articles` | Manage knowledge base articles with hierarchical organization and tagging |
| `yt projects` | Create and manage YouTrack projects |
| `yt users` | User management and permissions |
| `yt time` | Time tracking with flexible duration formats |
| `yt boards` | Agile board operations and management |
| `yt reports` | Generate burndown and velocity reports |
| `yt auth` | Authentication and credential management |
| `yt config` | CLI configuration and preferences |
| `yt admin` | Administrative operations (requires admin privileges) |

## Command Examples

### Issues
```bash
# Create and manage issues
yt issues create PROJECT-123 "Fix login bug" --type Bug --priority High --assignee john.doe
yt issues list --project-id PROJECT-123 --state Open
yt issues search "priority:Critical state:Open"
yt issues update ISSUE-456 --state "In Progress"

# Comments and collaboration
yt issues comments add ISSUE-456 "Fixed in latest build"
yt issues attach upload ISSUE-456 /path/to/screenshot.png

# Issue relationships
yt issues links create ISSUE-456 ISSUE-789 "depends on"
yt issues tag add ISSUE-456 urgent
```

### Articles
```bash
# Create and manage knowledge base
yt articles create "API Guide" --content "Comprehensive API documentation"

# Create articles from markdown files
yt articles create "Installation Guide" --file docs/install.md

# Organize existing documentation
yt articles create "Developer Guide" --file dev-guide.md --project-id PROJECT-123

# Tag articles for better organization
yt articles tag ARTICLE-123 documentation tutorial

yt articles tree --project-id PROJECT-123
yt articles search "authentication"
```

### Projects
```bash
# Project management
yt projects create "Web App" "WEB" --leader john.doe --template scrum
yt projects list --show-archived
yt projects configure WEB --description "Main web application"
```

### Time Tracking
```bash
# Flexible time logging
yt time log ISSUE-123 "2h 30m" --work-type "Development"
yt time report --start-date "2024-01-01" --end-date "2024-01-31"
yt time summary --group-by user
```

### Reporting
```bash
# Project insights
yt reports burndown PROJECT-123 --sprint "Sprint 1"
yt reports velocity PROJECT-123 --sprints 10
```

## Help and Support

- 📖 **[Documentation](https://yt-cli.readthedocs.io/en/latest/)** - Comprehensive guides and examples
- 🐛 **[Issue Tracker](https://github.com/YOUR_USERNAME/yt-cli/issues)** - Report bugs and request features
- 💬 **[Discussions](https://github.com/YOUR_USERNAME/yt-cli/discussions)** - Ask questions and share ideas

## Development

This project uses `uv` for dependency management.

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/yt-cli.git
cd yt-cli

# Install dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install

# Install the package in editable mode
uv pip install -e .
```

### Testing

This project uses `pytest` with randomized test execution to ensure test reliability:

```bash
# Run tests (automatically randomized order)
uv run pytest

# Run tests with coverage
uv run pytest --cov=yt_cli

# Run tests on multiple Python versions
uv run tox

# Run tests with specific random seed for reproducibility
uv run pytest --randomly-seed=12345

# Disable randomization if needed
uv run pytest --randomly-dont-shuffle
```

**Randomized Testing**: Tests run in random order by default using `pytest-randomly` to catch order-dependent bugs and improve test reliability. Each test run displays the random seed used, which can be reused to reproduce specific test failures.

### Code Quality

This project uses comprehensive pre-commit hooks for code quality:

```bash
# Run all quality checks (automatically runs on commit)
uv run pre-commit run --all-files

# Individual quality checks
uv run ruff check      # Linting
uv run ruff format     # Code formatting
uv run ty check        # Type checking
```

### Pre-commit Hooks

The project includes comprehensive pre-commit hooks that run automatically before each commit:

- **File Quality**: Trailing whitespace, end-of-file fixes, YAML/TOML validation
- **Code Quality**: Ruff linting and formatting, ty type checking
- **Testing**: Full pytest test suite
- **Security**: zizmor GitHub Actions security analysis

To run pre-commit hooks manually:

```bash
# Run all hooks on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run pytest
```

### Security

```bash
# Check GitHub Actions workflows
uv run zizmor .github/workflows/
```

## License

MIT License - see LICENSE file for details.
