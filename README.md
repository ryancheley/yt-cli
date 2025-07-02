# YouTrack CLI

A command line interface for JetBrains YouTrack issue tracking system.

## Installation

### From PyPI (when available)

```bash
pip install yt-cli
```

### From source

```bash
git clone https://github.com/YOUR_USERNAME/yt-cli.git
cd yt-cli
uv sync --dev
uv pip install -e .
```

## Usage

```bash
yt --help
```

### Available Commands

- `yt issues` - Manage issues
- `yt articles` - Manage knowledge base articles  
- `yt projects` - Manage projects
- `yt users` - User management
- `yt time` - Time tracking operations
- `yt boards` - Agile board operations
- `yt reports` - Generate cross-entity reports
- `yt auth` - Authentication management
- `yt config` - CLI configuration
- `yt admin` - Administrative operations

## Development

This project uses `uv` for dependency management.

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/yt-cli.git
cd yt-cli

# Install dependencies
uv sync --dev

# Install the package in editable mode
uv pip install -e .
```

### Testing

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=yt_cli

# Run tests on multiple Python versions
uv run tox
```

### Linting and Formatting

```bash
# Check code style
uv run ruff check

# Format code
uv run ruff format

# Type checking
uv run mypy yt_cli
```

### Security

```bash
# Check GitHub Actions workflows
uv run zizmor .github/workflows/
```

## License

MIT License - see LICENSE file for details.