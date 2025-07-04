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

### Articles

Manage YouTrack knowledge base articles with the `yt articles` command group:

```bash
# Create a new article
yt articles create "Getting Started Guide" --content "This is a comprehensive guide..."

# Create an article in a specific project
yt articles create "API Documentation" --content "API usage guide" --project-id PROJECT-123

# Create a nested article (child of another article)
yt articles create "Advanced Features" --content "Advanced guide" --parent-id ARTICLE-456

# Create a draft article (private visibility)
yt articles create "Draft Article" --content "Work in progress" --visibility private

# List all articles
yt articles list

# List articles in table format (default)
yt articles list --format table

# List articles in JSON format
yt articles list --format json

# Filter articles by project
yt articles list --project-id PROJECT-123

# Filter articles by parent
yt articles list --parent-id ARTICLE-456

# Limit number of articles returned
yt articles list --top 20

# Display articles in hierarchical tree structure
yt articles tree

# Filter tree view by project
yt articles tree --project-id PROJECT-123

# Search articles
yt articles search "getting started"

# Search articles in a specific project
yt articles search "API" --project-id PROJECT-123

# Limit search results
yt articles search "documentation" --top 10

# Edit an article
yt articles edit ARTICLE-123 --title "Updated Title"
yt articles edit ARTICLE-123 --content "Updated content"
yt articles edit ARTICLE-123 --visibility public

# View detailed article information
yt articles edit ARTICLE-123 --show-details

# Publish a draft article
yt articles publish ARTICLE-123

# List draft articles
yt articles draft

# Filter drafts by project
yt articles draft --project-id PROJECT-123

# Sort child articles under a parent (preview mode)
yt articles sort PARENT-ARTICLE-123

# Sort child articles and apply changes (requires manual confirmation in YouTrack web interface)
yt articles sort PARENT-ARTICLE-123 --update
```

#### Article Comments

Manage comments on articles:

```bash
# Add a comment to an article
yt articles comments add ARTICLE-123 "This is a helpful article!"

# List comments on an article
yt articles comments list ARTICLE-123

# List comments in JSON format
yt articles comments list ARTICLE-123 --format json

# Update a comment (not yet implemented)
yt articles comments update COMMENT-456 "Updated comment text"

# Delete a comment (not yet implemented)
yt articles comments delete COMMENT-456
yt articles comments delete COMMENT-456 --confirm  # Skip confirmation
```

#### Article Attachments

Manage file attachments on articles:

```bash
# List attachments for an article
yt articles attach list ARTICLE-123

# List attachments in JSON format
yt articles attach list ARTICLE-123 --format json

# Upload a file to an article (not yet implemented)
yt articles attach upload ARTICLE-123 /path/to/file.pdf

# Download an attachment (not yet implemented)
yt articles attach download ARTICLE-123 ATTACHMENT-456
yt articles attach download ARTICLE-123 ATTACHMENT-456 --output /path/to/save/

# Delete an attachment (not yet implemented)
yt articles attach delete ARTICLE-123 ATTACHMENT-456
yt articles attach delete ARTICLE-123 ATTACHMENT-456 --confirm  # Skip confirmation
```

#### Article Management Features

- **Create Articles**: Create new articles with customizable settings and hierarchy
- **List Articles**: View all articles with filtering and formatting options
- **Tree View**: Display articles in hierarchical tree structure showing parent-child relationships
- **Search Articles**: Full-text search across article content and metadata
- **Edit Articles**: Update article content, titles, and visibility settings
- **Draft Management**: Create and manage draft articles before publication
- **Publish Articles**: Convert draft articles to published state
- **Comments**: Add and view comments on articles for collaboration
- **Attachments**: Manage file attachments (list functionality implemented)
- **Sorting**: View and organize child articles under parent articles
- **Rich Output**: Beautiful table and tree formatting with status indicators
- **JSON Export**: Export article data in JSON format for scripting
- **Error Handling**: Clear error messages for permissions and validation issues
- **Hierarchical Organization**: Support for nested article structures

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

### Time Tracking

Track and manage work time on YouTrack issues with the `yt time` command group:

```bash
# Log time to an issue
yt time log ISSUE-123 "2h" --description "Implemented new feature"

# Log time with work type
yt time log ISSUE-123 "1h 30m" --work-type "Development" --description "Code review"

# Log time for a specific date
yt time log ISSUE-123 "45m" --date "2024-01-15" --description "Bug fixing"

# Log time for yesterday
yt time log ISSUE-123 "2h" --date "yesterday" --description "Testing"

# Generate time reports for specific issues
yt time report --issue-id ISSUE-123

# Generate time reports for a user
yt time report --user-id USER-456

# Generate time reports for a date range
yt time report --start-date "2024-01-01" --end-date "2024-01-31"

# View time summary grouped by user (default)
yt time summary

# View time summary grouped by issue
yt time summary --group-by issue

# View time summary grouped by work type
yt time summary --group-by type

# Filter summary by date range
yt time summary --start-date "2024-01-01" --end-date "2024-01-31"

# Export reports in JSON format
yt time report --format json
yt time summary --format json
```

#### Duration Formats

The time logging supports various duration formats:

- **Hours**: `2h`, `1.5h`, `0.25h`
- **Minutes**: `30m`, `45m`, `120m`
- **Combined**: `2h 30m`, `1h 15m`
- **Numeric**: `90` (assumed to be minutes)

#### Date Formats

Date inputs support multiple formats:

- **ISO Format**: `2024-01-15`
- **US Format**: `01/15/2024`
- **European Format**: `15.01.2024`
- **Relative**: `today`, `yesterday`

#### Time Tracking Features

- **Flexible Duration Input**: Support for hours, minutes, and combined formats
- **Work Type Classification**: Categorize work by type (Development, Testing, etc.)
- **Date Flexibility**: Log time for any date, including relative dates
- **Rich Reporting**: Generate detailed reports with filtering options
- **Time Summaries**: Aggregate time data by user, issue, or work type
- **Multiple Output Formats**: View data in tables or export as JSON
- **Issue Integration**: Time tracking is tightly integrated with YouTrack issues
- **Error Handling**: Clear validation for duration formats and date inputs

### Boards

Manage YouTrack agile boards with the `yt boards` command group:

```bash
# List all agile boards
yt boards list

# List boards for a specific project
yt boards list --project-id PROJECT-123

# View detailed information about a board
yt boards view BOARD-456

# Update a board's name
yt boards update BOARD-456 --name "New Board Name"

# Export board data in JSON format
yt boards list --format json
yt boards view BOARD-456 --format json
```

#### Board Management Features

- **Board Discovery**: List all available agile boards in your YouTrack instance
- **Project Filtering**: Filter boards by specific project IDs
- **Detailed View**: Get comprehensive information about board configuration
- **Board Updates**: Modify board settings like name and configuration
- **Rich Display**: View board information in formatted tables with columns, sprints, and ownership details
- **Multiple Output Formats**: View data in tables or export as JSON
- **Error Handling**: Clear error messages for permissions and API issues

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