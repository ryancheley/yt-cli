# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.11.1] - 2025-07-24

### Fixed
- Fix TypeError in 'yt new' command (#370)
- Fix TypeError in 'yt ls' command - incorrect parameter name (#367, #369)
  - Changed parameter name from project to project_id when invoking list_issues
  - Built query string from type, priority, and tag parameters
  - Added all required parameters with appropriate defaults

## [0.11.0] - 2025-07-24

### Added
- CLI testing agent for automated command validation (#368)
  - Create comprehensive CLI testing agent at .claude/agents/cli-tester.md
  - Integrate agent into implement command workflow
  - Add automatic CLI testing to pre-commit validation
  - Ensure all CLI changes are tested before PR creation
- Comprehensive documentation testing system (#347)
  - Automated testing of code examples in documentation to ensure they stay current
  - Link checking automation in CI/CD pipeline to validate external and internal links
  - Documentation build verification to catch build failures early
  - Sphinx doctest integration with mock environment setup for consistent testing
  - Pre-commit hooks for documentation quality enforcement
  - Documentation quality gates requiring all tests to pass before merging
  - Comprehensive developer guidelines for writing testable documentation
  - CI/CD integration with dedicated documentation testing job
  - RST file doctest support with proper configuration and error handling
- New `yt articles reorder` command for previewing article sorting and ordering (#330)
  - Provides comprehensive preview of how articles would be reordered by title, ID, or friendly ID
  - Supports project and parent-based filtering for targeted reordering
  - Includes table and JSON output formats for automation and scripting
  - Shows position changes with clear indicators (↑, ↓, =) and current ordinal values
  - Displays API limitation notices and step-by-step manual reordering instructions
  - Implements case-sensitive/insensitive title sorting options
  - Adds reverse sorting capability for all sort criteria
  - Features comprehensive error handling and validation

### Fixed
- Fix README and CONTRIBUTING placeholder URLs to use correct repository URL (#340)
  - Replaced `YOUR_USERNAME` placeholders with `ryancheley` in README.md and CONTRIBUTING.md
  - Updated GitHub links for issues, discussions, and repository cloning
  - Ensures professional documentation appearance and working links
- Fix `yt articles sort` command to properly display child articles and remove misleading functionality (#327)
  - Fixed child article filtering bug that prevented proper parent-child relationship matching
  - Replaced misleading `--update` flag with `--sort-by` and `--reverse` options for display sorting
  - Added proper sorting by title, creation date, or update date for visualization
  - Updated documentation to clarify API limitations (article reordering requires web interface)
  - Improved user experience with clear messaging about manual reordering requirements
- Fix `yt articles sort` command not finding child articles that exist in tree view (#324)
  - Added logic to resolve parent article readable IDs to internal IDs for proper filtering
  - Child articles are now correctly identified when using readable parent IDs (e.g., "FPU-A-1")
  - Ensures consistent behavior between `yt articles tree` and `yt articles sort` commands
- Fix `yt issues show` command displaying "N/A" for State, Priority, and Type fields (#323)
  - Added fallback logic to check custom fields when built-in fields are not available
  - Implemented `_get_field_with_fallback` method to handle both built-in and custom field structures
  - Ensures consistent field resolution between table and detail views
- Fix `yt articles tree` command missing child articles in tree display (#320)
  - Resolved ID mismatch between parent grouping (internal IDs) and child matching (readable IDs)
  - Tree now correctly displays hierarchical article structure with all child articles
- Fix `yt articles tree` command throwing NoneType error when parentArticle field is null (#299)
- Replace internal IDs with user-friendly IDs in CLI output for better UX (#313)
  - `yt issues attach list` now shows filename as primary identifier with internal ID moved to last column
  - `yt issues links list` now shows user-friendly issue IDs (e.g., "FPU-5" instead of "3-2")
  - `yt time list` and `yt time report` now show user-friendly issue IDs in Issue column
  - Time entry IDs moved to last column as "Entry ID" for reference
- Fix integer timestamp rendering error in `yt issues show` command (#319)
  - Timestamps are now properly formatted as human-readable strings instead of raw integers
  - Added `format_timestamp` utility function to handle Unix timestamp conversion

## [0.10.0] - 2025-07-20

### Added
- Missing `yt time list` command referenced in documentation (#287, #288)
- Enhanced tutorial UX with single-letter shortcuts and inline command execution (#286)
- Secure ClickCommandExecutor for tutorial inline command execution (#289)
- Return friendly issue ID instead of internal ID when creating issues (#290)

### Fixed
- Fix tests output and test compatibility issues
- Fix 'Type unknown' in `yt projects fields list` command (#294, #295)
  - Updated API request to include fieldType presentation for proper field type display
  - Field types now show correctly as enum[1], user[1], state[1], etc. instead of 'Unknown'
- Fix 'None' permissions column in `yt users groups` and `yt users roles` commands (#293)
  - Enhanced API field configurations to properly retrieve group and role permissions
  - Improved fallback methods to include permissions data when primary API calls fail
  - Fixed early return logic that was preventing permission retrieval attempts
- Fix duplicate commands in projects tutorial steps 2 and 3 (#285)
- Fix Docker tutorial step 9 cleanup options prompt mismatch (#284)
- Fix --assignee flag not working in 'yt issues update' command (#282)
- Fix time log command using correct YouTrack API endpoint (#281)
- Fix incorrect command in 'yt tutorial issues' interactive guide (#280)

### Improved
- Groups display to reflect YouTrack architecture
- Enhanced tutorial inline command execution with secure ClickCommandExecutor (#289)
- Visual indicators for executable commands with enhanced UI
- Command whitelisting for security and safety
- Confirmation prompts for destructive operations
- Better integration with YouTrack CLI context and authentication

## [0.9.2] - 2025-07-17

### Fixed
- User groups, teams, and roles commands returning empty results (#268)

## [0.9.1] - 2025-07-17

### Fixed
- Release script to prevent incomplete releases (#266)

## [0.9.0] - 2025-07-17

### Added
- Non-interactive options for automation and CI/CD (#261)
  - `--force` flag for delete commands (replaces `--confirm` for consistency)
  - `--leader` option for project creation to avoid interactive prompts
  - `--password` option for user creation with security warnings
- User permission query commands (#263)
  - `yt users groups <user_id>` - Display groups that a user belongs to
  - `yt users roles <user_id>` - Display roles assigned to a user
  - `yt users teams <user_id>` - Display teams that a user is a member of
  - Support for both table and JSON output formats
- `--active-only` flag to `yt users list` command (#262)

### Fixed
- Docker tutorial URL placeholders in YouTrack configuration wizard output (#264)
- Issue tag removal 404 error (#260)
- Multiple critical issues with articles functionality (#258)
- Time logging 500 Internal Server Error (#257)
- Time report functionality NoneType error (#241)
- Time report rendering error with integer values (#240)
- Article creation by making --project-id required (#239)
- Time logging date property type mismatch error (#237)
- Issue creation with project short names (#235, #236)
- State, Priority, and Type fields showing N/A in issues list (#234)
- Docker tutorial YouTrack image pull failure (#227)

### Improved
- Command syntax documentation with clearer examples and error messages (#250, #251)
- Help text for common commands to prevent syntax errors
- Interactive command behavior documentation
- Comprehensive troubleshooting guide for command syntax errors
- Better error messages with helpful suggestions for incorrect command usage
- Documentation examples for dry-run and batch operations (#256)

## [0.8.1] - 2025-07-13

### Added
- Convert docs from Markdown to reStructuredText (#217)

### Fixed
- Docker tutorial execution - container now actually starts (#222)
- Backspace sequences appearing as literal text in CLI help (#219)
- Missing Sphinx extensions for documentation build (#218)

### Improved
- Synchronize changelog documentation and add missing releases (#223)
- Configure ReadTheDocs to build only on version updates and PyPI releases (#225)

## [0.8.0] - 2025-07-13

### Added
- API field selection optimization for improved performance (#184, #213)
- Internationalization/locale settings commands (#215)
- Docker-based YouTrack instance option in tutorial (#216)

### Fixed
- Type checking issues with type ignore comments (#214)

## [0.7.0] - 2025-07-13

### Added
- Tutorial command for guided learning experience (#183, #211)
- CHANGELOG.md file following Keep a Changelog format (#210)
- CONTRIBUTING.md file with comprehensive contribution guidelines (#210)

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
- Table display data inconsistencies in issues list (#136)
- Error generating projects list (#137)
- Security Audit list not showing user (#138)
- Articles HTML response parsing and add authentication validation (#135)
- Boards HTML response parsing and add authentication validation (#134)
- Time summary JSON parsing for empty responses (#133)
- Auth login not persisting config data and API key masking (#132)

### Improved
- Test performance optimizations (#139)

## [0.4.0] - 2024-11-15

### Added
- Configuration Management: Replace Manual File Parsing with Proper dotenv Usage (#118, #124)
- Type Safety: Improve Type Annotations and Create Pydantic Response Models (#117, #123)
- Resource Management: Add Proper Client Manager Cleanup (#116, #122)
- Security: Add SSL Verification Override Warnings (#114, #120)

### Fixed
- Exception handling: Replace bare exception catch with specific handlers (#121)
- Security: Fix Client Manager Type Checker Bypass (#119)
- SSL verification not being respected in API calls (#112)
- ReadTheDocs build configuration (#110)

### Changed
- Convert markdown docs to RST and remove MyST-Parser dependency
- Improved Sphinx configuration

## [0.3.9] - 2024-10-01

### Fixed
- Version determination for CLI --version command
- ArticleManager SSL verification - Update to use centralized HTTPClientManager (#109)
- BoardManager SSL verification - Update to use centralized HTTPClientManager (#108)
- AdminManager SSL verification - Use centralized HTTPClientManager (#105)
- ProjectManager SSL verification - Complete implementation (#101)

### Added
- Formatting fixes from pre-commit hooks (#106, #107)
- IssueManager tests for HTTPClientManager migration (#100)
- GitHub issue resolution process (#103)

## [0.3.8] - 2024-09-15

### Fixed
- Type checker errors in client and logging tests (#91)

## [0.3.7] - 2024-09-01

### Added
- SSL certificate verification options to auth command (#90)

## [0.3.6] - 2024-08-15

### Fixed
- Field mapping mismatch in admin license and health commands (#88)

## [0.3.5] - 2024-08-01

### Fixed
- Version bump consistency

## [0.3.4] - 2024-07-15

### Fixed
- Admin license show command 404 error (#83, #85)

### Improved
- Apply ruff formatting to admin.py (#84)

## [0.3.3] - 2024-07-01

### Added
- Markdown file input support to `yt articles create` command (#81)

## [0.3.2] - 2024-06-15

### Fixed
- Admin user-groups 404 error by using Hub REST API (#79)
- Admin license usage API endpoint to resolve 404 error (#78)
- Admin license show command 404 error (#77)
- Admin health check endpoint 404 error (#76)

### Changed
- Updated justfile to use ty type checker

## [0.3.1] - 2024-06-01

### Fixed
- Duplicate commands in CLI help output (#71)

## [0.3.0] - 2024-05-15

### Added
- Comprehensive performance optimizations (#56, #69)
- Command aliases for common operations (#67)
- Security enhancements (#53, #66)
- Progress indicators for long-running operations (#52, #65)
- Shell completion support (#51, #64)
- py.typed marker for type checking support (#62, #63)
- __all__ declarations to control module exports (#61)
- Comprehensive logging system (#30, #59)

### Fixed
- Type checker mismatch in tox.ini (#58)

### Changed
- Standardized dependency groups in pyproject.toml (#68)
- Enhanced release process with comprehensive justfile recipes and documentation

## [0.2.2] - 2024-04-15

### Fixed
- Type checker mismatch in tox.ini (#58)
- Version mismatch between __init__.py and pyproject.toml (#57)

## [0.2.1] - 2024-04-01

### Fixed
- Users API endpoint from /api/admin/users to /api/users (#45)
- Admin_manager initialization in admin commands (#40, #42)
- API endpoint construction issues (#39)
- JSON parsing errors in issues, articles, and boards commands (#38)
- Authentication endpoint 404 error (#33)

### Added
- pytest-randomly for randomized test execution (#44)

## [0.2.0] - 2024-03-15

### Added
- Initial CLI functionality
- Basic YouTrack integration
- Core command structure
- Authentication system
- Basic issue management commands
- Admin command structure

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
