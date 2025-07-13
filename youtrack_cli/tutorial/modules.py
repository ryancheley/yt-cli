"""Built-in tutorial modules for YouTrack CLI."""

from typing import List

from .core import TutorialModule, TutorialStep


class SetupTutorial(TutorialModule):
    """Tutorial for setting up YouTrack CLI authentication."""

    def __init__(self):
        super().__init__(
            module_id="setup",
            title="Getting Started with YouTrack CLI",
            description="Learn how to authenticate and configure YouTrack CLI for first use.",
        )

    def create_steps(self) -> List[TutorialStep]:
        """Create tutorial steps."""
        return [
            TutorialStep(
                title="Welcome to YouTrack CLI",
                description="YouTrack CLI is a powerful command-line tool for managing "
                "YouTrack issues, projects, and workflows.",
                instructions=[
                    "YouTrack CLI helps you work with YouTrack from your terminal",
                    "You can create issues, track time, manage projects, and more",
                    "This tutorial will guide you through the basic setup process",
                ],
                tips=[
                    "You can get help for any command with --help",
                    "Most commands have short aliases (e.g., 'yt i' for 'yt issues')",
                    "The CLI supports both interactive and batch operations",
                ],
            ),
            TutorialStep(
                title="Authentication Setup",
                description="First, you need to authenticate with your YouTrack instance using an API token.",
                instructions=[
                    "Go to your YouTrack instance in a web browser",
                    "Navigate to Profile → Account Security → API Tokens",
                    "Create a new token with appropriate permissions",
                    "Copy the token for the next step",
                ],
                command_example="yt auth login",
                tips=[
                    "API tokens are more secure than username/password",
                    "You can have multiple tokens for different purposes",
                    "Tokens can be revoked if compromised",
                ],
            ),
            TutorialStep(
                title="Verify Your Setup",
                description="Let's verify that your authentication is working correctly.",
                instructions=[
                    "Run the command to list your projects",
                    "This will test your authentication and connection",
                    "You should see a list of projects you have access to",
                ],
                command_example="yt projects list",
                tips=[
                    "If you see an error, check your token and URL",
                    "Make sure your YouTrack instance is accessible",
                    "You can update your token with 'yt auth token --update'",
                ],
            ),
            TutorialStep(
                title="Configuration Options",
                description="Learn about optional configuration settings to customize your experience.",
                instructions=[
                    "You can set a default project to save typing",
                    "Configure your preferred output format",
                    "View all current configuration settings",
                ],
                command_example="yt config list",
                tips=[
                    "Configuration is stored in ~/.config/youtrack-cli/",
                    "You can edit settings with 'yt config set KEY VALUE'",
                    "Some settings can be overridden with command flags",
                ],
            ),
        ]


class IssuesTutorial(TutorialModule):
    """Tutorial for basic issue management."""

    def __init__(self):
        super().__init__(
            module_id="issues",
            title="Working with Issues",
            description="Learn how to create, update, and manage YouTrack issues using the CLI.",
        )

    def create_steps(self) -> List[TutorialStep]:
        """Create tutorial steps."""
        return [
            TutorialStep(
                title="Understanding Issues",
                description="Issues are the core of YouTrack - they represent tasks, bugs, "
                "features, and other work items.",
                instructions=[
                    "Issues belong to projects and have unique IDs",
                    "Each issue has a summary, description, and various fields",
                    "Issues can be assigned, prioritized, and tracked through workflows",
                ],
                tips=[
                    "Issue IDs follow the pattern PROJECT-NUMBER (e.g., FPU-123)",
                    "Issues can have custom fields specific to your project",
                    "You can link issues to show relationships",
                ],
            ),
            TutorialStep(
                title="Listing Issues",
                description="Start by exploring existing issues in your projects.",
                instructions=[
                    "List issues from all projects you have access to",
                    "Try filtering by assignee, state, or project",
                    "Notice the different output formats available",
                ],
                command_example="yt issues list --limit 10",
                tips=[
                    "Use --assignee me to see issues assigned to you",
                    "Filter by state with --state Open or --state Resolved",
                    "The --project-id flag restricts results to a specific project",
                ],
            ),
            TutorialStep(
                title="Creating Your First Issue",
                description="Create a new issue to practice the CLI workflow.",
                instructions=[
                    "Choose a project ID from your available projects",
                    "Create an issue with a clear, descriptive summary",
                    "Optionally set type, priority, and assignee",
                ],
                command_example='yt issues create PROJECT-ID "Tutorial practice issue"',
                tips=[
                    "Use quotes around summaries with spaces",
                    "You can add a description with --description",
                    "Set issue type with --type (Bug, Task, Feature, etc.)",
                    "Note: Issue creation requires proper project permissions",
                ],
            ),
            TutorialStep(
                title="Viewing Issue Details",
                description="Learn how to get detailed information about a specific issue.",
                instructions=[
                    "Use the issue ID from the previous step",
                    "View the full issue details including custom fields",
                    "Try different output formats (table, json, yaml)",
                ],
                command_example="yt issues show ISSUE-ID",
                tips=[
                    "Use --format json for machine-readable output",
                    "The show command displays detailed issue information",
                    "You can copy issue IDs from the list command",
                ],
            ),
            TutorialStep(
                title="Updating Issues",
                description="Practice updating issue fields and status.",
                instructions=[
                    "Update the issue you created earlier",
                    "Try changing the state, priority, or assignee",
                    "Add a comment to describe what you changed",
                ],
                command_example='yt issues update ISSUE-ID --state "In Progress"',
                tips=[
                    "Use tab completion to see available states",
                    "You can update multiple fields in one command",
                    "Always add comments when changing issue status",
                ],
            ),
        ]


class ProjectsTutorial(TutorialModule):
    """Tutorial for working with projects."""

    def __init__(self):
        super().__init__(
            module_id="projects",
            title="Managing Projects",
            description="Learn how to work with YouTrack projects and their configurations.",
        )

    def create_steps(self) -> List[TutorialStep]:
        """Create tutorial steps."""
        return [
            TutorialStep(
                title="Understanding Projects",
                description="Projects organize issues and define workflows, fields, and permissions.",
                instructions=[
                    "Each project has a unique ID and name",
                    "Projects have their own custom fields and workflows",
                    "User permissions are often project-specific",
                ],
                tips=[
                    "Project IDs are typically short codes like 'FPU' or 'PROJ'",
                    "Projects can be archived when no longer active",
                    "Each project can have different issue types",
                ],
            ),
            TutorialStep(
                title="Exploring Project Lists",
                description="Learn how to view and filter your available projects.",
                instructions=[
                    "List all projects you have access to",
                    "Look for project IDs, names, and descriptions",
                    "Notice which projects are archived vs active",
                ],
                command_example="yt projects list",
                tips=[
                    "Use --archived to see archived projects",
                    "The --format flag changes output style",
                    "Project IDs are used in issue creation and filtering",
                ],
            ),
            TutorialStep(
                title="Project Details",
                description="Get detailed information about a specific project.",
                instructions=[
                    "Choose a project from your list",
                    "View its configuration, custom fields, and workflows",
                    "Understand the project's structure",
                ],
                command_example="yt projects list",
                tips=[
                    "Custom fields vary between projects",
                    "Workflows define how issues move through states",
                    "Some fields may be required for issue creation",
                ],
            ),
            TutorialStep(
                title="Working with Custom Fields",
                description="Learn about project-specific custom fields and their usage.",
                instructions=[
                    "Explore the custom fields available in your project",
                    "Understand field types (text, enum, user, date, etc.)",
                    "See which fields are required vs optional",
                ],
                command_example="# Note: Project field details require admin access",
                tips=[
                    "Enum fields have predefined values",
                    "User fields can be assigned to team members",
                    "Date fields help with scheduling and tracking",
                ],
            ),
        ]


class TimeTutorial(TutorialModule):
    """Tutorial for time tracking features."""

    def __init__(self):
        super().__init__(
            module_id="time",
            title="Time Tracking",
            description="Learn how to log work time and track effort on issues.",
        )

    def create_steps(self) -> List[TutorialStep]:
        """Create tutorial steps."""
        return [
            TutorialStep(
                title="Understanding Time Tracking",
                description="YouTrack can track time spent on issues for project management and billing.",
                instructions=[
                    "Time can be logged against any issue",
                    "Work items have duration, description, and work type",
                    "Time data helps with project planning and reporting",
                ],
                tips=[
                    "Time can be entered in various formats (1h 30m, 90m, 1.5h)",
                    "Work types help categorize different kinds of effort",
                    "Time entries can be edited or deleted if needed",
                ],
            ),
            TutorialStep(
                title="Logging Time",
                description="Practice logging work time against an issue.",
                instructions=[
                    "Choose an issue you've worked on",
                    "Log time with a clear description of the work done",
                    "Specify the work type if your project uses them",
                ],
                command_example='yt time log ISSUE-ID "2h 30m" --description "Fixed the bug"',
                tips=[
                    "Be specific in your work descriptions",
                    "Log time regularly for accurate tracking",
                    "Include the --work-type flag if your project requires it",
                    "Note: Time tracking requires appropriate permissions",
                ],
            ),
            TutorialStep(
                title="Viewing Time Entries",
                description="Learn how to view time entries for issues and projects.",
                instructions=[
                    "View time entries for a specific issue",
                    "See who logged time and when",
                    "Understand the time entry details",
                ],
                command_example="yt time list --issue ISSUE-ID",
                tips=[
                    "Use --author to filter by who logged the time",
                    "Date ranges can be specified with --start and --end",
                    "Time reports help with project tracking",
                ],
            ),
        ]


def get_default_modules() -> List[TutorialModule]:
    """Get the default set of tutorial modules."""
    return [
        SetupTutorial(),
        IssuesTutorial(),
        ProjectsTutorial(),
        TimeTutorial(),
    ]
