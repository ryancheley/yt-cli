Changelog
=========

All notable changes to YouTrack CLI will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

Added
~~~~~
- Initial project structure and CLI framework
- Basic issue management commands
- Authentication system with token support
- Configuration management
- Rich terminal output with tables and colors
- Comprehensive test suite
- Documentation with Sphinx and Read the Docs integration
- Pre-commit hooks for automated code quality checks
- zizmor security analysis for GitHub Actions

Changed
~~~~~~~
- Switched from mypy to ty for type checking (faster, modern type checker)
- Enhanced CI workflow with comprehensive quality checks
- Updated development documentation with pre-commit setup

Deprecated
~~~~~~~~~~
- None

Removed
~~~~~~~
- None

Fixed
~~~~~
- None

Security
~~~~~~~~
- None

[0.1.0] - 2024-07-02
---------------------

Added
~~~~~
- Initial release of YouTrack CLI
- Core CLI framework using Click
- Rich terminal output support
- Basic project structure
- Development tooling setup (ruff, ty, pytest)
- Documentation framework
- CI/CD pipeline configuration
