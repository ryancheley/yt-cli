"""Built-in tutorial modules for YouTrack CLI."""

from typing import List, Optional

from .core import TutorialModule, TutorialStep
from .docker_utils import (
    DockerNotAvailableError,
    PortInUseError,
    YouTrackStartupError,
    check_docker_available,
    check_port_available,
    cleanup_youtrack_resources,
    get_setup_instructions,
    get_youtrack_url,
    pull_youtrack_image,
    remove_youtrack_container,
    start_youtrack_container,
    stop_youtrack_container,
    wait_for_youtrack_ready,
)


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
                command_example="yt issues list --top 10",
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
                command_example="yt projects list --fields id,name,description,leader,archived",
                tips=[
                    "Use --fields to specify which project details to show",
                    "Available fields include: id, name, description, leader, archived",
                    "Use --format json for structured output",
                ],
            ),
            TutorialStep(
                title="Working with Custom Fields",
                description="Learn about project-specific custom fields and their usage.",
                instructions=[
                    "Explore the custom fields available across all projects",
                    "Understand field types (text, enum, user, date, etc.)",
                    "See field names and their configurations",
                ],
                command_example="yt admin fields list",
                tips=[
                    "Custom fields are defined globally but used per-project",
                    "Field types determine what values can be stored",
                    "Some fields may be required for issue creation",
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


class DockerTutorial(TutorialModule):
    """Tutorial for setting up a local YouTrack instance with Docker."""

    def __init__(self):
        self._wizard_url: Optional[str] = None
        super().__init__(
            module_id="docker",
            title="Local YouTrack with Docker",
            description="Set up a local YouTrack instance using Docker for hands-on learning.",
        )

    def create_steps(self) -> List[TutorialStep]:
        """Create tutorial steps."""
        return [
            TutorialStep(
                title="Welcome to Docker Tutorial",
                description="This tutorial will guide you through setting up a local YouTrack instance "
                "using Docker, perfect for learning and experimentation.",
                instructions=[
                    "We'll use the official YouTrack Docker image",
                    "Your local instance will be accessible at http://localhost:8080",
                    "All data will be stored locally and can be preserved or removed",
                    "You'll get hands-on experience with a real YouTrack instance",
                ],
                tips=[
                    "Docker must be installed and running on your system",
                    "The first startup may take several minutes",
                    "You can keep or remove the instance when finished",
                ],
            ),
            TutorialStep(
                title="Docker Environment Check",
                description="Let's verify that Docker is available and ready for use.",
                instructions=[
                    "We'll check if Docker is installed and running on your system",
                    "This step will verify Docker availability",
                    "Any issues will be reported with helpful solutions",
                ],
                tips=[
                    "Docker Desktop must be running if you're on Windows/macOS",
                    "On Linux, ensure your user is in the docker group",
                    "If Docker is not available, install it from docker.com",
                ],
                execute_action=self._execute_docker_check,
                validation_check=self._validate_docker_available,
            ),
            TutorialStep(
                title="Port Availability Check",
                description="Verify that port 8080 is available for YouTrack.",
                instructions=[
                    "We'll check if port 8080 is available for YouTrack",
                    "This port will be used to access your local YouTrack instance",
                    "Any conflicts will be identified with suggestions",
                ],
                tips=[
                    "Port 8080 is the default for YouTrack",
                    "If in use, stop other services or we'll use a different port",
                    "Common services using 8080: Jenkins, other web applications",
                ],
                execute_action=self._execute_port_check,
                validation_check=self._validate_port_available,
            ),
            TutorialStep(
                title="Download YouTrack Image",
                description="Download the official YouTrack Docker image.",
                instructions=[
                    "We'll download the official jetbrains/youtrack Docker image",
                    "This step may take a few minutes on first run",
                    "The image will be cached for future use",
                ],
                tips=[
                    "This may take a few minutes depending on your internet speed",
                    "The image is about 1GB in size",
                    "This only needs to be done once",
                ],
                execute_action=self._execute_image_pull,
                validation_check=self._validate_image_pulled,
            ),
            TutorialStep(
                title="Start YouTrack Container",
                description="Launch your local YouTrack instance.",
                instructions=[
                    "We'll start a YouTrack container using the downloaded image",
                    "The container will be configured with appropriate settings",
                    "We'll wait for YouTrack to be fully ready before proceeding",
                ],
                tips=[
                    "The container will start in the background",
                    "Initial startup takes several minutes",
                    "We'll wait for YouTrack to be fully ready",
                ],
                execute_action=self._execute_container_start,
                validation_check=self._validate_container_running,
            ),
            TutorialStep(
                title="YouTrack Initial Setup",
                description="Complete the initial YouTrack configuration in your browser.",
                instructions=self._get_web_setup_instructions(),
                tips=[
                    "Use any credentials you like - this is your local instance",
                    "Create a test project for practicing CLI commands",
                    "The 'FPU' project name works well for examples",
                ],
            ),
            TutorialStep(
                title="Configure CLI for Local Instance",
                description="Set up the YouTrack CLI to work with your local instance.",
                instructions=self._get_cli_config_instructions(),
                command_example="yt auth login --base-url http://localhost:8080 --token YOUR_TOKEN",
                tips=[
                    "Get your API token from Profile → Account Security → API Tokens",
                    "The base URL should be http://localhost:8080",
                    "Test the connection with 'yt projects list'",
                ],
            ),
            TutorialStep(
                title="Practice with Your Local Instance",
                description="Try some basic operations with your local YouTrack.",
                instructions=[
                    "List your projects: yt projects list",
                    "Create a test issue: yt issues create PROJECT-ID 'Test issue'",
                    "View the issue: yt issues show PROJECT-123",
                    "Update the issue: yt issues update PROJECT-123 --state 'In Progress'",
                ],
                tips=[
                    "Replace PROJECT-ID with your actual project ID",
                    "Issue IDs follow the pattern PROJECT-NUMBER",
                    "Try different commands to explore the CLI",
                ],
            ),
            TutorialStep(
                title="Cleanup Options",
                description="Decide what to do with your local YouTrack instance.",
                instructions=self._get_cleanup_instructions(),
                tips=[
                    "Keeping the instance lets you continue practicing",
                    "Removing saves disk space and cleans up resources",
                    "You can always create a new instance later",
                ],
                custom_prompt_choices=["keep", "stop", "remove", "cleanup", "skip"],
                custom_prompt_handler=self._handle_cleanup_action,
            ),
        ]

    def _get_docker_check_instructions(self) -> List[str]:
        """Get instructions for Docker availability check."""
        try:
            check_docker_available()
            return [
                "✓ Docker is available and running!",
                "Your system is ready to run YouTrack containers",
                "Proceeding to the next step...",
            ]
        except DockerNotAvailableError as e:
            return [
                f"✗ Docker check failed: {e}",
                "Please install Docker and ensure it's running",
                "Visit https://docker.com for installation instructions",
                "Restart this tutorial after Docker is ready",
            ]

    def _get_port_check_instructions(self) -> List[str]:
        """Get instructions for port availability check."""
        try:
            check_port_available()
            return [
                "✓ Port 8080 is available!",
                "YouTrack will be accessible at http://localhost:8080",
                "Ready to proceed with container setup",
            ]
        except PortInUseError as e:
            return [
                f"✗ Port check failed: {e}",
                "Please stop any services using port 8080",
                "Or we can use a different port if needed",
                "Common culprits: Jenkins, other web servers",
            ]

    def _get_image_pull_instructions(self) -> List[str]:
        """Get instructions for pulling YouTrack image."""
        try:
            pull_youtrack_image()
            return [
                "✓ YouTrack image downloaded successfully!",
                "Image is now available for container creation",
                "Ready to start the YouTrack container",
            ]
        except Exception as e:
            return [
                f"✗ Image pull failed: {e}",
                "Check your internet connection",
                "Ensure Docker has permission to pull images",
                "You may need to retry this step",
            ]

    def _get_container_start_instructions(self) -> List[str]:
        """Get instructions for starting YouTrack container."""
        try:
            container_id, wizard_url = start_youtrack_container()
            wait_for_youtrack_ready()
            # Store wizard URL for later use
            self._wizard_url = wizard_url
            return [
                f"✓ YouTrack container started! (ID: {container_id[:12]})",
                "✓ YouTrack is now ready and accessible",
                "",
                f"Configuration Wizard URL: {wizard_url}",
                "",
                "The URL above includes a one-time wizard token for initial setup.",
                "Copy and paste this URL into your browser to begin configuration.",
            ]
        except (Exception, YouTrackStartupError) as e:
            return [
                f"✗ Container startup failed: {e}",
                "Check Docker logs for more details",
                "Ensure no other services are using port 8080",
                "You may need to retry this step",
            ]

    def _get_web_setup_instructions(self) -> List[str]:
        """Get web setup instructions."""
        return get_setup_instructions(wizard_url=self._wizard_url)

    def _get_cli_config_instructions(self) -> List[str]:
        """Get CLI configuration instructions."""
        return [
            "Now let's configure the CLI to use your local YouTrack:",
            "1. In YouTrack, go to your Profile (top right)",
            "2. Go to Account Security → API Tokens",
            "3. Create a new token with appropriate permissions",
            "4. Copy the token and run the command below",
            f"5. Use base URL: {get_youtrack_url()}",
        ]

    def _get_cleanup_instructions(self) -> List[str]:
        """Get cleanup instructions."""
        return [
            "What would you like to do with your local YouTrack instance?",
            "",
            "Options:",
            "1. Keep running - Continue using it for practice",
            "2. Stop container - Keep data but stop the service",
            "3. Remove container - Remove container but keep data volume",
            "4. Full cleanup - Remove everything (container + data)",
            "",
            "Choose based on your needs:",
            "- Keep if you want to continue learning",
            "- Stop if you're done for now but might return",
            "- Remove if you want to clean up completely",
        ]

    # Execution methods for Docker tutorial steps
    async def _execute_docker_check(self) -> None:
        """Execute Docker availability check."""
        check_docker_available()

    async def _execute_port_check(self) -> None:
        """Execute port availability check."""
        check_port_available()

    async def _execute_image_pull(self) -> None:
        """Execute YouTrack image pull."""
        pull_youtrack_image()

    async def _execute_container_start(self) -> None:
        """Execute YouTrack container start."""
        # Get the container ID and wizard URL
        _, wizard_url = start_youtrack_container()
        self._wizard_url = wizard_url
        wait_for_youtrack_ready()

    # Validation methods for Docker tutorial steps
    def _validate_docker_available(self) -> bool:
        """Validate Docker is available."""
        try:
            check_docker_available()
            return True
        except DockerNotAvailableError:
            return False

    def _validate_port_available(self) -> bool:
        """Validate port 8080 is available."""
        try:
            check_port_available()
            return True
        except PortInUseError:
            return False

    def _validate_image_pulled(self) -> bool:
        """Validate YouTrack image is available."""
        try:
            # Import locally to avoid issues
            import docker

            client = docker.from_env()
            client.images.get("jetbrains/youtrack:2025.1.66652")
            return True
        except Exception:
            return False

    def _validate_container_running(self) -> bool:
        """Validate YouTrack container is running and ready."""
        try:
            # Check if container is running first
            import docker

            client = docker.from_env()
            containers = client.containers.list(filters={"name": "youtrack"})
            if not containers:
                return False

            # Check if YouTrack is ready
            import requests

            response = requests.get(get_youtrack_url(), timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def cleanup_resources(self, remove_data: bool = False) -> None:
        """Clean up Docker resources."""
        cleanup_youtrack_resources(remove_data=remove_data)

    async def _handle_cleanup_action(self, action: str) -> bool:
        """Handle cleanup action selected by user.

        Args:
            action: The selected cleanup action.

        Returns:
            True if action completed successfully, False otherwise.
        """
        from ..console import get_console

        console = get_console()

        if action == "keep":
            console.print("[green]✓ Keeping YouTrack instance running[/green]")
            console.print("Your YouTrack instance will continue running in the background.")
            console.print(f"Access it at: {get_youtrack_url()}")
            console.print("You can stop it later with: docker stop youtrack-tutorial")
            return True

        if action == "stop":
            console.print("[yellow]Stopping YouTrack container...[/yellow]")
            try:
                stop_youtrack_container()
                console.print("[green]✓ YouTrack container stopped[/green]")
                console.print("Data is preserved. Restart with: docker start youtrack-tutorial")
                return True
            except Exception as e:
                console.print(f"[red]Failed to stop container: {e}[/red]")
                return False

        elif action == "remove":
            console.print("[yellow]Removing YouTrack container (keeping data)...[/yellow]")
            try:
                remove_youtrack_container()
                console.print("[green]✓ YouTrack container removed[/green]")
                console.print("Data volume preserved. You can create a new container later.")
                return True
            except Exception as e:
                console.print(f"[red]Failed to remove container: {e}[/red]")
                return False

        elif action == "cleanup":
            console.print("[yellow]Performing full cleanup (removing container and data)...[/yellow]")
            try:
                cleanup_youtrack_resources(remove_data=True)
                console.print("[green]✓ Full cleanup completed[/green]")
                console.print("All YouTrack tutorial resources have been removed.")
                return True
            except Exception as e:
                console.print(f"[red]Failed to cleanup: {e}[/red]")
                return False

        elif action == "skip":
            console.print("[blue]Skipping cleanup - your YouTrack instance will keep running[/blue]")
            console.print(f"Access it at: {get_youtrack_url()}")
            return True

        else:
            console.print(f"[red]Unknown action: {action}[/red]")
            return False


def get_default_modules() -> List[TutorialModule]:
    """Get the default set of tutorial modules."""
    return [
        SetupTutorial(),
        IssuesTutorial(),
        ProjectsTutorial(),
        TimeTutorial(),
        DockerTutorial(),
    ]
