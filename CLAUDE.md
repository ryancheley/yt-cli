# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Plan

This is a YouTrack CLI application for interacting with JetBrains YouTrack issue tracking system via command line interface. This cli will offer an ergonomic, best practice cli and will leverage

- rich
- textual
- pydantic

We use `uv` for managing dependencies.

## Create

Each new feature must have a corresponding github issue. When working on a new issue a new feature branch must be created with the name of the branch matching the name of the issue with the issue number in it. 

For every change that is implemented, the README.md file MUST be updated to reflect that change.

## Test

All tests must pass. We use `pytest` for testing, `ruff` for linting, `ty` for type checking, `tox` for running on various versions of Python. We'll utilize `zizmor` for reviewing our GitHub Actions

## Deploy

Deployment will always be done to a feature branch. When a feature is significant enough, we'll bump the version of the tool and tag it with that version. We will have a github action that deploys this to Test PyPI and PyPI using a `release.yml` GitHub Action. 

## Project Overview


The commands for this cli will be:

**`yt issues`** - Manage issues
- `create` - Create new issues
- `list` - List issues with filtering
- `update` - Update issue fields
- `delete` - Delete issues
- `search` - Advanced issue search
- `assign` - Assign issues to users
- `move` - Move issues between states/projects
- `tag` - Manage issue tags
- `comments` - Manage issue comments
    - `add` - Add comments to issues
    - `list` - List comments on issues
    - `update` - Update existing comments
    - `delete` - Delete comments
- `attach` - Manage issue attachments
    - `upload` - Upload files to issues
    - `download` - Download attachments
    - `list` - List issue attachments
    - `delete` - Delete attachments
- `links` - Manage issue relationships
    - `create` - Link issues with relationship types
    - `list` - Show all links for an issue
    - `delete` - Remove issue links
    - `types` - List available link types

**`yt articles`** - Manage knowledge base articles
- `create` - Create new articles
- `edit` - Edit existing articles
- `publish` - Publish draft articles
- `list` - List articles with filtering
    - `tree` - Display articles in hierarchical tree structure
- `search` - Search articles
- `draft` - Manage article drafts
- `sort` - Sort child articles under a parent article (with `--update` flag to apply changes to YouTrack after confirmation)
- `comments` - Manage article comments
    - `add` - Add comments to articles
    - `list` - List comments on articles
    - `update` - Update existing comments
    - `delete` - Delete comments
- `attach` - Manage article attachments
    - `upload` - Upload files to articles
    - `download` - Download attachments
    - `list` - List article attachments
    - `delete` - Delete attachments

**`yt projects`** - Manage projects
- `list` - List all projects
- `create` - Create new projects
- `configure` - Configure project settings
- `archive` - Archive projects

**`yt users`** - User management
- `list` - List users
- `create` - Create new users
- `update` - Update user information
- `permissions` - Manage user permissions

## Workflow Commands (Top-Level)

**`yt time`** - Time tracking operations (issues only)
- `log` - Log work time
- `report` - Generate time reports
- `summary` - View time summaries

**`yt boards`** - Agile board operations
- `list` - List agile boards
- `view` - View board details
- `update` - Update board configuration

## System Commands (Top-Level)

**`yt reports`** - Generate cross-entity reports (burndown, velocity, etc.)

**`yt auth`** - Authentication management
- `login` - Authenticate with YouTrack
- `logout` - Clear authentication
- `token` - Manage API tokens

**`yt config`** - CLI configuration
- `set` - Set configuration values
- `get` - Get configuration values
- `list` - List all configuration

**`yt admin`** - Administrative operations (for users with admin permissions)
- `global-settings` - Manage global YouTrack settings
    - `get` - View global settings
    - `set` - Update global settings
    - `list` - List all global settings
- `license` - License management
    - `show` - Display license information
    - `usage` - Show license usage statistics
- `maintenance` - System maintenance operations
    - `reindex` - Reindex system data
    - `clear-cache` - Clear system caches
    - `backup` - Create system backup
- `fields` - Manage custom fields across projects
    - `create` - Create new custom fields
    - `list` - List all custom fields
    - `update` - Modify field settings
    - `delete` - Remove unused fields
- `workflows` - Manage workflow rules and automation
    - `list` - List all workflows
    - `import` - Import workflow rules
    - `export` - Export workflow configurations
    - `validate` - Validate workflow syntax
- `bundles` - Manage value bundles (enums, user groups, etc.)
    - `list` - List all bundles
    - `create` - Create new value bundles
    - `update` - Modify bundle values
    - `delete` - Remove unused bundles
- `import` - Import data from external sources
    - `issues` - Import issues from CSV/XML
    - `users` - Bulk import users
    - `projects` - Import project configurations
- `user-groups` - Manage user groups and permissions
    - `list` - List all user groups
    - `create` - Create new user groups
    - `update` - Modify group membership
    - `delete` - Remove user groups
- `permissions` - Global permission scheme management
    - `list` - List permission schemes
    - `create` - Create permission schemes
    - `update` - Modify permissions
    - `assign` - Assign permissions to groups/users
- `security` - Security settings
    - `password-policy` - Manage password policies
    - `session-timeout` - Configure session timeouts
    - `login-restrictions` - Manage login restrictions
- `vcs` - Manage VCS integrations
    - `list` - List VCS connections
    - `create` - Create new VCS integration
    - `update` - Update VCS settings
    - `test` - Test VCS connectivity
- `notifications` - Configure global notification templates and rules
    - `templates` - Manage notification templates
    - `rules` - Configure notification rules
    - `test` - Test notification delivery
- `external-auth` - Manage external authentication providers
    - `ldap` - Configure LDAP settings
    - `sso` - Manage SSO configurations
    - `test` - Test authentication providers
- `logs` - Access system logs and audit trails
    - `view` - View system logs
    - `download` - Download log files
    - `audit` - View audit trail
- `health` - System health checks and diagnostics
    - `check` - Run health diagnostics
    - `status` - Show system status
    - `metrics` - Display system metrics
- `usage` - Generate usage statistics and reports
    - `users` - User activity reports
        - `report` - Generate user activity reports
        - `export` - Export user usage data to CSV/JSON
        - `import` - Import user usage data from external sources
    - `projects` - Project usage statistics
    - `storage` - Storage usage reports

Example usage:

- `yt admin usage users report --date-range "2024-01-01:2024-12-31"`
- `yt admin usage users export --format csv --output users-activity.csv`
- `yt admin usage users import --file external-usage.json --dry-run`


## Current Configuration

- Claude Code permissions are configured in `.claude/settings.local.json`