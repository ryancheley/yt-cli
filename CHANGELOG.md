# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CHANGELOG.md file following Keep a Changelog format
- CONTRIBUTING.md file with comprehensive contribution guidelines

## [0.6.1] - 2025-07-13

### Fixed
- Fix test to handle ANSI escape codes in issue display (#209)

## [0.6.0] - 2025-07-13

### Added
- Formal docstring conventions implementation (#180, #208)
- Comprehensive integration testing with proper markers (#207)

### Fixed
- Pytest coroutine warnings and test isolation issues (#206)
- Test recipe flexibility and reduced output verbosity (#205)
- Type checker diagnostics and improved test compatibility (#204)

## [0.5.1] - 2025-07-13

### Fixed
- Global settings display - handle nested API response structure (#203)
- Custom fields Type column showing N/A instead of actual field types (#202)
- Suppressed expected keyring item not found errors during logout (#198)

## [0.5.0] - 2025-07-13

### Added
- Enhanced Rich Library features with panels and tree views (#191)
- Pagination for large table outputs (#190)
- Centralized console management and theming support (#189)
- Cursor pagination support for YouTrack API (#188)
- Comprehensive test coverage for core modules (#187)
- Enhanced custom field value extraction support (#186)

### Fixed
- Boards list showing empty Name and N/A for Project/Owner fields (#197)
- URL construction causing double slashes in API requests (#195)
- Article list project filtering by using correct API endpoint (#193)
- Python 3.9 asyncio event loop issue in cache
- Python 3.9 compatibility for cursor pagination

## [0.4.1] - 2024-12-01

### Fixed
- Minor bug fixes and stability improvements

## [0.4.0] - 2024-11-15

### Added
- Enhanced CLI functionality
- Improved error handling
- Better user experience features

### Changed
- Performance optimizations
- Code refactoring for better maintainability

## [0.3.9] - 2024-10-01

### Added
- Additional CLI commands
- Enhanced configuration options

### Fixed
- Various bug fixes and improvements

## [0.3.8] - 2024-09-15

### Added
- New features for issue management
- Improved API integration

## [0.3.7] - 2024-09-01

### Fixed
- Critical bug fixes
- Performance improvements

## [0.3.6] - 2024-08-15

### Added
- Initial CLI functionality
- Basic YouTrack integration
- Core command structure

---

### Legend

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

### Links

- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [YouTrack CLI Repository](https://github.com/ryan-murphy/yt-cli)
