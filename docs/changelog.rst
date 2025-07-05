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
- **Enhanced error handling infrastructure with custom exceptions**
- **Advanced logging system with Rich formatting and debug modes**
- **Robust HTTP utilities with automatic retry logic and exponential backoff**
- **Common CLI components and decorators for consistent command behavior**
- **User-friendly error messages with actionable suggestions**
- **Structured exception hierarchy (AuthenticationError, ConnectionError, etc.)**
- **Enhanced release management with comprehensive justfile recipes**
- **Pre-flight checks for release validation and safety**
- **Automated release rollback capabilities for emergency situations**
- **Release status monitoring and health checks**
- **Comprehensive release troubleshooting documentation**

Changed
~~~~~~~
- Switched from mypy to ty for type checking (faster, modern type checker)
- Enhanced CI workflow with comprehensive quality checks
- Updated development documentation with pre-commit setup
- **Enhanced project metadata in pyproject.toml with comprehensive classifiers and URLs**
- **Improved CLI architecture with global debug and verbose options**
- **Updated troubleshooting documentation with new debugging features**
- **Improved justfile release recipes with safety checks and validation**
- **Enhanced release workflow documentation with real-world examples**
- **Updated development documentation with automated release process**

Deprecated
~~~~~~~~~~
- None

Removed
~~~~~~~
- None

Fixed
~~~~~
- **Release process reliability with proper git state validation**
- **Version consistency management between pyproject.toml and package**
- **uv.lock synchronization during release process**

Security
~~~~~~~~
- **Enhanced release process with branch protection and quality gates**

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
