# YouTrack CLI Commands Reference

This document provides a comprehensive reference for all commands available in the YouTrack CLI.

## Main Command

```bash
yt [OPTIONS] COMMAND [ARGS]...
```

**Description:** YouTrack CLI - Command line interface for JetBrains YouTrack.

A powerful command line tool for managing YouTrack issues, projects, users, time tracking, and more. Designed for developers and teams who want to integrate YouTrack into their daily workflows and automation.

### Global Options
- `--version` - Show the version and exit
- `-c, --config PATH` - Path to configuration file
- `-v, --verbose` - Enable verbose output
- `--debug` - Enable debug output
- `--no-progress` - Disable progress indicators
- `--secure` - Enable enhanced security mode (prevents credential logging)
- `-h, --help` - Show help message and exit

### Command Aliases
- `i` = issues
- `a` = articles
- `p` = projects
- `u` = users
- `t` = time
- `b` = boards
- `c/cfg` = config
- `login` = auth

## Commands

### `yt issues` (alias: `i`)
**Description:** Manage issues - create, update, search, and organize your work.

#### Subcommands:
- `assign` - Assign an issue to a user
- `attach` - Manage issue attachments
- `batch` - Batch operations for issues
- `benchmark` - Benchmark field selection performance improvements
- `comments` - Manage issue comments
- `create` - Create a new issue
- `delete` - Delete an issue
- `dependencies` - Show issue dependencies and relationships in tree format
- `links` - Manage issue relationships
- `list` - List issues with filtering
- `move` - Move an issue between states or projects
- `search` - Advanced issue search
- `show` - Show detailed information about an issue
- `tag` - Manage issue tags
- `update` - Update an existing issue

### `yt articles` (alias: `a`)
**Description:** Manage knowledge base articles.

#### Subcommands:
- `attach` - Manage article attachments
- `comments` - Manage article comments
- `create` - Create a new article
- `draft` - Manage article drafts
- `edit` - Edit an existing article
- `list` - List articles with filtering
- `publish` - Publish a draft article
- `search` - Search articles
- `sort` - Sort child articles under a parent article
- `tag` - Add tags to an article
- `tree` - Display articles in hierarchical tree structure

### `yt projects` (alias: `p`)
**Description:** Manage projects - list, view, and configure project settings.

#### Subcommands:
- `archive` - Archive a project
- `configure` - Configure project settings
- `create` - Create a new project
- `list` - List all projects

### `yt users` (alias: `u`)
**Description:** User management.

#### Subcommands:
- `create` - Create a new user
- `list` - List all users
- `permissions` - Manage user permissions
- `update` - Update user information

### `yt time` (alias: `t`)
**Description:** Time tracking operations.

#### Subcommands:
- `log` - Log work time to an issue
- `report` - Generate time reports with filtering options
- `summary` - View time summaries with aggregation

### `yt boards` (alias: `b`)
**Description:** Agile board operations.

#### Subcommands:
- `list` - List all agile boards
- `update` - Update an agile board configuration
- `view` - View details of a specific agile board

### `yt auth` (alias: `login`)
**Description:** Authentication management.

#### Subcommands:
- `login` - Authenticate with YouTrack
- `logout` - Clear authentication credentials
- `token` - Manage API tokens

### `yt config` (alias: `c`, `cfg`)
**Description:** CLI configuration.

#### Subcommands:
- `get` - Get a configuration value
- `list` - List all configuration values
- `set` - Set a configuration value

### `yt admin`
**Description:** Administrative operations.

#### Subcommands:
- `fields` - Manage custom fields across projects
- `global-settings` - Manage global YouTrack settings
- `health` - System health checks and diagnostics
- `i18n` - Manage internationalization settings (alias for locale)
- `license` - License management
- `locale` - Manage YouTrack locale and language settings
- `maintenance` - System maintenance operations
- `user-groups` - Manage user groups and permissions

### `yt reports`
**Description:** Generate cross-entity reports.

#### Subcommands:
- `burndown` - Generate a burndown report for a project or sprint
- `velocity` - Generate a velocity report for recent sprints

### `yt security`
**Description:** Security and audit management.

#### Subcommands:
- `audit` - View command audit log
- `clear-audit` - Clear the command audit log
- `token-status` - Check token expiration status

### `yt tutorial`
**Description:** Interactive tutorials for learning YouTrack CLI.

#### Subcommands:
- `feedback` - Provide feedback about the tutorial system
- `list` - List available tutorials and their progress
- `progress` - Show detailed progress for all tutorials
- `reset` - Reset tutorial progress
- `run` - Run a specific tutorial module

### `yt completion`
**Description:** Generate shell completion script.

Supports bash, zsh, fish, and PowerShell shells.

### `yt setup`
**Description:** Interactive setup wizard for first-time configuration.

## Quick Start Examples

```bash
# Set up authentication
yt auth login  # or: yt login

# List your projects
yt projects list  # or: yt p list

# Create an issue
yt issues create PROJECT-123 "Fix the bug"  # or: yt i create ...

# Log work time
yt time log ISSUE-456 "2h 30m" --description "Fixed the issue"
# or: yt t log ...
```

## Documentation

For detailed usage instructions and examples, visit: https://yt-cli.readthedocs.io/

## Getting Help

- View help for any command: `yt COMMAND --help`
- View help for subcommands: `yt COMMAND SUBCOMMAND --help`
- Start with the setup wizard: `yt setup`
- Learn with tutorials: `yt tutorial list`
