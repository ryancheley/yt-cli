# Contributing to YouTrack CLI

Thank you for your interest in contributing to YouTrack CLI! This document provides comprehensive guidelines for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Release Process](#release-process)
- [Code of Conduct](#code-of-conduct)

## Getting Started

### Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git
- A YouTrack instance for testing (optional, but recommended)

### Development Environment Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/ryancheley/yt-cli.git
   cd yt-cli
   ```

2. **Set up Development Environment**
   ```bash
   # Install dependencies
   uv sync --dev

   # Install pre-commit hooks
   uv run pre-commit install
   ```

3. **Verify Installation**
   ```bash
   # Install CLI in development mode
   uv pip install -e .

   # Run tests to ensure everything works
   uv run pytest
   ```

4. **Set up YouTrack Test Environment (Optional)**
   ```bash
   # Create local environment file
   cp .env.example .env.local
   # Edit .env.local with your YouTrack credentials
   ```

## Development Environment

### Tools and Dependencies

We use modern Python tooling for development:

- **uv**: Package and dependency management
- **pytest**: Testing framework with asyncio support
- **ruff**: Code linting and formatting
- **ty**: Type checking (not mypy or pyright)
- **pre-commit**: Git hooks for code quality
- **tox**: Testing across Python versions
- **zizmor**: GitHub Actions security analysis

### Project Structure

```
yt-cli/
├── youtrack_cli/          # Main package
│   ├── commands/          # CLI command implementations
│   ├── cli_utils/         # CLI utilities and aliases
│   └── *.py              # Core modules
├── tests/                 # Test suite
│   ├── integration/       # Integration tests (require YouTrack API)
│   └── test_*.py         # Unit tests
├── docs/                  # Documentation
├── scratch/               # Development notes and issue planning
└── pyproject.toml        # Project configuration
```

## Coding Standards

### Python Style

- **Code Style**: Follow PEP 8, enforced by `ruff`
- **Line Length**: Maximum 120 characters
- **Python Version**: Support Python 3.9+
- **Type Hints**: Required for all public APIs

### Docstring Standards

We follow **Google-style docstrings** exclusively. See [Developer Guidelines](docs/developer-guidelines.md) for comprehensive documentation standards including:

- Module, class, and function docstrings
- Parameter and return value documentation
- Exception documentation with practical examples
- CLI command documentation

### Import Organization

```python
# Standard library imports
import asyncio
from typing import Optional

# Third-party imports
import click
from rich.console import Console

# Local imports
from youtrack_cli.client import YouTrackClient
from youtrack_cli.models import Issue
```

### Error Handling

- Use custom exceptions from `youtrack_cli.exceptions`
- Provide meaningful error messages
- Log errors appropriately using structured logging

### CLI Design Principles

- Use `rich` for enhanced terminal output
- Implement progress indicators for long operations
- Support pagination for large datasets
- Provide clear help text and examples

## Testing

### Test Categories

- **Unit Tests**: Fast, isolated tests in `tests/test_*.py`
- **Integration Tests**: Tests requiring YouTrack API in `tests/integration/`

### Running Tests

```bash
# Run all tests
uv run pytest

# Run unit tests only
uv run pytest -m unit

# Run integration tests (requires YouTrack setup)
uv run pytest -m integration

# Run with coverage
uv run pytest --cov=youtrack_cli

# Run tests across multiple Python versions
uv run tox
```

### Writing Tests

- Mark tests appropriately: `@pytest.mark.unit` or `@pytest.mark.integration`
- Use `pytest-asyncio` for async tests
- Mock external dependencies in unit tests
- Test both success and error cases

### Test Requirements

- All new features must have tests
- Maintain or improve test coverage
- Tests must pass on Python 3.9-3.13
- Integration tests should use the `FPU` project for testing

## Documentation

### Documentation Requirements

- **API Documentation**: Auto-generated from docstrings using Sphinx
- **User Documentation**: Located in `docs/` folder
- **README.md**: Brief overview only, detailed docs in `docs/`
- **CHANGELOG.md**: Must be updated for all user-facing changes

### Documentation Updates

When adding new features:

1. Update relevant documentation in `docs/`
2. Add examples to docstrings
3. Update command help text
4. Add changelog entry

### Building Documentation

```bash
cd docs/
uv run sphinx-build -b html . _build/html
```

## Pull Request Process

### Before Submitting

1. **Create a Feature Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Follow GitHub Issue Resolution Steps**
   - Ensure corresponding GitHub issue exists
   - Create implementation plan in `scratch/issue-{number}.md`
   - Implement changes following the plan

3. **Quality Checks**
   ```bash
   # Run linting and formatting
   uv run ruff check youtrack_cli/
   uv run ruff format youtrack_cli/

   # Run type checking
   uv run ty youtrack_cli/

   # Run tests
   uv run pytest

   # Run pre-commit hooks
   uv run pre-commit run --all-files
   ```

### Pull Request Requirements

- **Title**: Use conventional commit format (e.g., `feat: add issue filtering`)
- **Description**: Link to GitHub issue and describe changes
- **Testing**: Include test results and manual testing steps
- **Documentation**: Update relevant documentation
- **Changelog**: Add entry to `CHANGELOG.md`

### Commit Message Format

```
🎯 feat: add custom field filtering support

- Implement filtering by custom field values
- Add support for multiple filter criteria
- Update documentation and examples

Fixes #123
```

**Commit Message Requirements:**
- Start with an emoji (following project convention)
- Use conventional commit prefixes: `feat:`, `fix:`, `docs:`, `test:`, etc.
- Reference issue numbers with `Fixes #number`
- Keep first line under 50 characters
- Include bullet points for detailed changes

### Code Review Process

1. Automated checks must pass (CI/CD, pre-commit hooks)
2. Manual code review by maintainers
3. Address review feedback promptly
4. Squash merge after approval

## Issue Reporting

### Bug Reports

Use the bug report template and include:

- **Environment**: Python version, OS, YouTrack version
- **Steps to Reproduce**: Clear, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Error Logs**: Full stack traces if applicable

### Feature Requests

Use the feature request template and include:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other approaches considered
- **Implementation Ideas**: Technical suggestions (optional)

### Security Issues

Report security vulnerabilities privately to the maintainers. Do not create public issues for security concerns.

## Release Process

### Version Management

- Follow [Semantic Versioning](https://semver.org/)
- Update version in `pyproject.toml`
- Update `CHANGELOG.md` with release notes
- Create and push git tags: `git tag v1.0.0 && git push origin v1.0.0`

### Automated Publishing

The project uses trusted publishers for secure PyPI publishing:

- **Test PyPI**: Automatic on tag push to test environment
- **PyPI**: Automatic on tag push for production releases
- **GitHub Releases**: Auto-generated from tags

See [PUBLISHING.md](PUBLISHING.md) for detailed release configuration.

## Code of Conduct

This project adheres to a code of conduct that ensures a welcoming environment for all contributors:

### Our Standards

- **Be Respectful**: Treat all contributors with respect
- **Be Inclusive**: Welcome diverse perspectives and backgrounds
- **Be Collaborative**: Work together constructively
- **Be Professional**: Maintain professional communication

### Unacceptable Behavior

- Harassment or discrimination of any kind
- Personal attacks or insulting comments
- Publishing private information without consent
- Disruptive behavior in discussions

### Enforcement

Violations should be reported to project maintainers. All reports will be handled confidentially and professionally.

## Getting Help

### Documentation

- **User Documentation**: [docs/](docs/)
- **API Documentation**: Auto-generated from code
- **Troubleshooting**: [docs/troubleshooting.rst](docs/troubleshooting.rst)

### Community

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community discussions
- **Development Chat**: Link to be added

### Maintainer Contact

For questions about contributing, reach out to the maintainers through GitHub issues or discussions.

---

Thank you for contributing to YouTrack CLI! Your contributions help make this tool better for the entire community. 🚀
