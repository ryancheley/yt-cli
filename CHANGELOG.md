# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.18.1] - 2025-08-09

### Changed
- 🔄 Standardize verb consistency: change 'yt alias remove' to 'yt alias delete' (#566)
  - Changed primary command from `yt alias remove` to `yt alias delete` for consistency with other entity deletion commands
  - Kept `remove` as a hidden alias for backwards compatibility
  - Updated all documentation references and error messages to use the new `delete` verb
- 🔄 Standardize verb consistency: change 'yt alias add' to 'yt alias create' (#565)
  - Changed primary command from `yt alias add` to `yt alias create` for consistency with other entity creation commands
  - Kept `add` as a hidden alias for backwards compatibility
  - Updated all documentation references to use the new `create` verb

### Fixed
- 🔐 Fix SSL certificate verification with self-signed certificates (#588)
  - Fixed SSL certificate verification to properly handle CA bundles and certificate chains
  - Improved error messages for SSL certificate verification failures with helpful suggestions
  - Added support for environment-based CA bundle configuration (YOUTRACK_CA_BUNDLE, YOUTRACK_CERT_FILE)
  - Enhanced SSL error handling with specific error types (ConnectError, HTTPStatusError)
  - Added comprehensive SSL troubleshooting documentation
  - Updated tests for SSL certificate functionality
- 📚 Fix confusing SSL verification flag documentation (Fixes #587) (#589)
  - Removed deprecated `--no-verify-ssl` standalone flag from documentation (it remains hidden in CLI)
  - Clarified that only `--verify-ssl/--no-verify-ssl` boolean flag should be used
  - Updated deprecation message to be clearer about the correct usage
  - Fixed documentation formatting issues with section underlines

## [0.18.0] - 2025-08-09

### Added
- 🔐 Add SSL certificate file support to yt auth login command (Fixes #585) (#586)
  - Added `--cert-file` option to support custom SSL certificate files during authentication
  - Enhanced SSL certificate handling for self-signed and custom certificate scenarios
  - Improved SSL error handling with specific guidance for certificate issues

## [0.17.0] - 2025-08-08

### Added
- ✨ Implement: Add markdown file article ID insertion (Fixes #583) (#584)
  - Added functionality to insert article IDs into markdown files
  - Enhanced article management workflow for documentation teams
  - Support for automated ID insertion in markdown-based documentation

## [0.16.0] - 2025-08-07

### Added
- 📚 Add comprehensive documentation for undocumented CLI commands (#579)
  - Documented missing subcommands across multiple command groups (#582)
  - Documented missing subcommands in issues command (#581)
  - Documented missing global CLI options (#580)
  - Comprehensive documentation coverage for all CLI functionality
- 📖 Implement doctest support for documentation and code examples (Fixes #571) (#574)
  - Added automated testing of code examples in documentation
  - Ensures documentation examples stay current and functional
  - Enhanced documentation quality and reliability

### Changed
- 🔄 Standardize verb consistency: change 'yt boards view' to 'yt boards show' (#573)
  - Changed primary command from `yt boards view` to `yt boards show` for consistency with other show commands
  - Kept `view` as a hidden alias for backwards compatibility
  - Updated all documentation references to use the new `show` verb

### Improved
- ⬆️ ci(deps): bump astral-sh/setup-uv from 6.3.1 to 6.4.3 (#569)
  - Updated GitHub Actions dependency for improved CI/CD performance

## [0.15.1] - 2025-08-04

### Added
- ✨ Remove deprecated admin commands and add i18n list alias (#558)
  - Remove deprecated admin commands that were causing confusion and maintenance burden
  - Add i18n list alias for better command discoverability and user experience

### Fixed
- 🧪 Fix failing user service tests to match new implementation (#564)
  - Update test fixtures and expectations to align with current user service implementation
  - Resolve test failures that were preventing CI/CD pipeline success

## [0.15.0] - 2025-08-03

### Added
- ✨ Implement article attachment delete functionality (#552)
- ✨ Implement article attachment download functionality (#551)
- ✨ Implement article comments delete functionality (#550)
- ✨ Implement article comments update command (#549)
- ✨ Add attachment IDs to issues attach list command output (#542)
- ♻️ Rename 'issues dependencies' to 'issues related' and show all relationship types dynamically (#543)
  - Rename command from `yt issues dependencies` to `yt issues related` for better clarity
  - Dynamically fetch and display all relationship types from YouTrack instance
  - Support custom relationship types specific to different YouTrack configurations
  - Enhanced tree and table formats showing relationship directions (inward/outward)
  - Maintain backward compatibility with `dependencies` as an alias
  - Improved display with proper relationship type names (sourceToTarget/targetToSource)

### Changed
- 🔧 Simplify 'yt projects fields' command to only provide list functionality (#546)
  - **BREAKING CHANGE**: Removed attach, update, and detach subcommands from `yt projects fields`
  - Command now directly lists project fields: `yt projects fields PROJECT-ID`
  - Field management operations should be performed through YouTrack web interface
  - Simplified CLI interface reduces maintenance burden and prevents accidental field modifications
  - Updated documentation to reflect read-only nature of field operations

### Fixed
- 🐛 Fix yt projects fields --fields parameter showing N/A in Name column (#548)
- 🐛 Fix help text formatting for yt projects fields command (#547)
- 🐛 Fix Type field validation to fail closed when field names unavailable (#541)
- 🐛 Fix users groups/roles/teams commands 404 errors (#540)
- 🐛 Fix time log WorkItemType entity error with work type resolution (#539)
- 🐛 Fix issues tag list command returning empty results (#538)
- 🐛 Fix complex alias execution - aliases with arguments now work (#537)
- 🐛 Fix batch create API compatibility validation (#536)
- 🐛 Fix false success in issues move command between projects (#534)
- 🐛 Fix issues move command showing error messages despite successful state changes (#533)
- 🐛 Fix assignee parameter not working in issues create command (#532)
- 🐛 Fix issue type update parameter not working in issues update command (#531)
- 🐛 Fix article visibility parameter ignored in create command (#530)
- 🐛 Fix inconsistent parent ID validation in articles create command (#529)
- 🐛 Fix article creation with readable parent IDs (#528)

## [0.13.5] - 2025-07-27

### Fixed
- 🐛 Fix issue assignment not working properly (#412)
  - Changed from using direct assignee field to custom field API structure for assignments
  - Added support for 'me' keyword in assignee parameter to automatically resolve to current user
  - Fixed API request structure to properly update assignee via customFields with SingleUserIssueCustomField type
- 🐛 Fix attachment list rendering error by converting created field to string (#418)
- 🐛 Fix issue create command project ID structure error (#419)
- 🐛 Fix move command "$type is required" error (#416, #420)
- 🐛 Fix KeyError in update command error handling (#421)
- 🐛 Fix admin maintenance clear-cache command returning 404 error (#431)
  - Updated clear_caches method to return informative error message explaining cache clearing is not available through YouTrack REST API
  - Updated documentation to clarify cache management must be done through YouTrack UI or server-side tools
  - Fixed tests to expect the correct error response

### Improved
- 🧪 Reduce excessive test coverage and eliminate redundant tests (#423)

## [0.13.4] - 2025-07-26

### Fixed
- 🐛 Fix yt issues show and dependencies commands displaying object references instead of formatted output (#409)
  - Added `__rich__()` method to `PanelGroup` class to enable proper Rich console integration for panel display
  - Fixed dependencies command data structure handling to properly extract issue information from API responses
  - Resolved "Unknown" values in dependencies tree by improving link data parsing for different API response formats
  - Fixed `yt issues assign` command error handling to display proper success/error messages instead of literal string 'message'
- 🐛 Fix issues list display formatting problems (#407)
  - Fixed empty State column by implementing fallback field name lookup for State/Status/Stage/Workflow State
  - Improved table formatting consistency and removed ANSI color code display issues
  - Enhanced column alignment for better readability in issue list output

## [0.13.3] - 2025-07-25

### Fixed
- 🐛 Fix bugs in issue creation and dependencies commands (#400-403)

## [0.13.2] - 2025-07-25

### Added
- 🎨 Theme customization for CLI appearance personalization (#397)
  - Interactive theme creation with `yt config theme create` command for custom color schemes
  - Theme management commands: list, current, set, create, delete, export, import
  - Built-in themes: default, dark, and light themes optimized for different terminal environments
  - Custom theme storage in `~/.config/youtrack-cli/themes/` with JSON format for easy sharing
  - Theme import/export functionality for sharing themes with team members
  - Comprehensive color support including standard colors, bright colors, RGB, and style modifiers
  - All CLI output consistently themed including tables, progress bars, panels, and messages
  - Interactive theme creation guide with core colors (info, warning, error, success) and optional advanced customization
  - Theme validation and error handling for invalid color values or malformed theme files
  - Backward compatibility maintained - existing `YOUTRACK_THEME` configuration continues to work
  - Full test coverage for theme management functionality including edge cases and error scenarios
- ⚡ Improve caching with advanced TTL and invalidation strategies (#392)
  - Enhanced Cache class with size-based LRU eviction to prevent unlimited memory growth
  - Tag-based cache invalidation for grouping and bulk invalidation of related entries
  - Pattern-based cache invalidation using glob patterns (e.g., 'projects:*', 'users:admin:*')
  - Bulk cache operations: `set_many()` and `delete_many()` for efficient batch processing
  - Comprehensive cache statistics including hit/miss ratios, eviction counts, and memory estimation
  - Enhanced CacheEntry with access tracking for LRU algorithms and tag support
  - Improved predefined cache decorators with appropriate tags for better organization
  - Backward compatibility maintained - all existing caching functionality continues to work unchanged
  - Full test coverage for all new caching features including concurrency scenarios
- Implement pagination for handling large result sets efficiently (#388)
  - Enhanced API client with unified pagination support for cursor-based and offset-based APIs
  - Automatic pagination type detection based on endpoint patterns
  - New CLI options for all list commands: `--page-size`, `--after-cursor`, `--before-cursor`, `--all`, `--max-results`
  - Updated `yt issues list`, `yt projects list`, `yt users list`, and `yt articles list` commands with pagination support
  - Backward compatibility maintained with existing `--top` parameter (now legacy)
  - Comprehensive pagination configuration with per-entity limits and performance optimization
  - Enhanced user experience with pagination navigation hints in CLI output
  - Full test coverage for pagination functionality including edge cases and error handling
- Add comprehensive request timeout configuration (#387)
  - Configure timeouts for all API calls to prevent hanging requests and improve reliability
  - Support for environment variables: YOUTRACK_DEFAULT_TIMEOUT, YOUTRACK_CONNECT_TIMEOUT, YOUTRACK_READ_TIMEOUT, YOUTRACK_WRITE_TIMEOUT, YOUTRACK_POOL_TIMEOUT
  - Individual timeout types (connect, read, write, pool) with fallback to default timeout
  - Enhanced HTTPClientManager with proper timeout handling and validation
  - Comprehensive test coverage for timeout configuration scenarios
- Implement automatic token rotation and refresh capabilities (#389)
  - Support automatic token refresh to handle token expiration gracefully
  - New security configuration options: enable_automatic_token_refresh, token_refresh_threshold_days, max_token_refresh_attempts
  - Enhanced TokenManager with token renewal detection and refresh request functionality
  - Automatic retry logic in HTTPClientManager for 401 errors with token refresh
  - New CLI commands: `yt auth refresh` for manual token renewal and `yt auth status` for token information
  - Intelligent token type detection (permanent vs. renewable tokens)
  - Enhanced AuthManager with automatic refresh capabilities before API requests
  - New exception classes: TokenRefreshError and TokenExpiredError for better error handling
  - Backward compatibility maintained - existing authentication flows continue to work unchanged
  - Security audit logging for token refresh operations

### Fixed
- Fix timeout parameter handling bug in HTTPClientManager.make_request() method
  - Previously used incorrect timeout.connect instead of default_timeout for fallback
  - Now properly uses configured default timeout when no specific timeout provided

## [0.12.0] - 2025-07-25

### Added
- Implement missing `yt projects show` command (#380)
  - Display detailed project information including name, ID, description, and leader
  - Support for both table and JSON output formats
  - Enhanced project management capabilities for CLI users

### Fixed
- Fix 404 error in `yt users permissions` command when managing group membership (#383)
  - Changed from incorrect YouTrack API endpoints to correct Hub API endpoints
  - Now uses `/hub/api/rest/usergroups/{group-id}/users` instead of `/api/admin/groups/{group-id}/users`
  - Fixed request format to include required user type, id, and login fields for Hub API
  - Added proper user details fetching to obtain Hub ID (ringId) for group operations
  - Updated troubleshooting documentation with solution and technical details
- Fix NoneType error in time summary group-by type command (#382)
  - Added proper null checking for time entry types in group-by operations
  - Prevents crashes when time entries have missing or null type values
  - Improved error handling for incomplete time tracking data
- Fix settings get --name and set commands URL encoding and field mapping (#381)
  - Fixed URL encoding issues for setting names with special characters
  - Corrected field mapping for proper API request structure
  - Enhanced settings management reliability and consistency
- Fix multiple CLI command issues - groups create, CSV format, tag filter, issue move (#379)
  - Fixed groups create command parameter handling and API endpoint usage
  - Resolved CSV output formatting inconsistencies across commands
  - Corrected tag filter functionality for proper issue filtering
  - Fixed issue move command to handle project transfers correctly

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
