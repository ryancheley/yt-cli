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

### Authentication

Before using most commands, you need to authenticate with your YouTrack instance:

```bash
# Login to YouTrack
yt auth login

# Login with pre-filled values
yt auth login --base-url https://yourdomain.youtrack.cloud --username yourname

# Show current authentication status (token is masked for security)
yt auth token --show

# Update your API token
yt auth token --update

# Logout and clear stored credentials
yt auth logout
```

### Configuration

The CLI supports configuration management to store settings and preferences:

```bash
# Set a configuration value
yt config set KEY VALUE

# Get a configuration value
yt config get KEY

# List all configuration values (sensitive values are masked)
yt config list

# Examples
yt config set DEFAULT_PROJECT "MY-PROJECT"
yt config set ITEMS_PER_PAGE "25"
yt config get DEFAULT_PROJECT
```

Configuration is stored in `~/.config/youtrack-cli/.env` by default. You can specify a custom configuration file using the `--config` option:

```bash
yt --config /path/to/custom.env config set KEY VALUE
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

### Projects

Manage YouTrack projects with the `yt projects` command group:

```bash
# List all projects
yt projects list

# List projects in JSON format
yt projects list --format json

# List projects including archived ones
yt projects list --show-archived

# Limit number of projects returned
yt projects list --top 10

# Create a new project
yt projects create "My New Project" "MNP" --leader john.doe

# Create a project with description and template
yt projects create "Scrum Project" "SP" --leader jane.smith \
  --description "A new scrum project" --template scrum

# View detailed project information
yt projects configure PROJECT_KEY --show-details

# Update project settings
yt projects configure PROJECT_KEY --name "Updated Name"
yt projects configure PROJECT_KEY --description "New description"
yt projects configure PROJECT_KEY --leader new.leader

# Archive a project
yt projects archive PROJECT_KEY

# Archive a project without confirmation prompt
yt projects archive PROJECT_KEY --confirm
```

#### Project Management Features

- **List Projects**: View all active projects with filtering options
- **Create Projects**: Create new projects with customizable settings
- **Configure Projects**: Update project name, description, and leader
- **Archive Projects**: Archive projects to mark them as inactive
- **Rich Output**: Beautiful table formatting with status indicators
- **JSON Export**: Export project data in JSON format for scripting
- **Error Handling**: Clear error messages for permissions and validation issues

### Users

Manage YouTrack users with the `yt users` command group:

```bash
# List all users
yt users list

# List users in JSON format
yt users list --format json

# Search for users
yt users list --query "admin"

# Limit number of users returned
yt users list --top 20

# Create a new user
yt users create newuser "New User" "newuser@company.com"

# Create a user with password and additional options
yt users create johnsmith "John Smith" "john.smith@company.com" \
  --password secretpass --force-change-password

# Create a banned user
yt users create spamuser "Spam User" "spam@example.com" --banned

# View detailed user information
yt users update USERNAME --show-details

# Update user information
yt users update USERNAME --full-name "Updated Name"
yt users update USERNAME --email "newemail@company.com"
yt users update USERNAME --password "newpassword"

# Ban or unban a user
yt users update USERNAME --banned
yt users update USERNAME --unbanned

# Force password change on next login
yt users update USERNAME --force-change-password

# Manage user permissions
yt users permissions USERNAME --action add_to_group --group-id developers
yt users permissions USERNAME --action remove_from_group --group-id admins
```

#### User Management Features

- **List Users**: View all users with search and filtering options
- **Create Users**: Create new users with customizable settings and permissions
- **Update Users**: Modify user information, passwords, and status
- **User Permissions**: Manage user group memberships and permissions
- **User Status**: Ban/unban users and manage account status
- **Rich Output**: Beautiful table formatting with status indicators
- **JSON Export**: Export user data in JSON format for scripting
- **Security**: Password prompts and secure credential handling
- **Error Handling**: Clear error messages for permissions and validation issues

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