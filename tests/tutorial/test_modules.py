"""Tests for tutorial modules."""

from unittest.mock import MagicMock, patch

import pytest

from youtrack_cli.tutorial.modules import (
    DockerTutorial,
    IssuesTutorial,
    ProjectsTutorial,
    SetupTutorial,
    TimeTutorial,
    get_default_modules,
)


class TestSetupTutorial:
    """Test the SetupTutorial class."""

    def test_init(self):
        """Test SetupTutorial initialization."""
        tutorial = SetupTutorial()

        assert tutorial.module_id == "setup"
        assert tutorial.title == "Getting Started with YouTrack CLI"
        assert "authenticate and configure" in tutorial.description

    def test_create_steps(self):
        """Test creating tutorial steps."""
        tutorial = SetupTutorial()
        steps = tutorial.create_steps()

        assert len(steps) == 4

        # Check first step
        assert "Welcome to YouTrack CLI" in steps[0].title
        assert "YouTrack CLI is a powerful command-line tool" in steps[0].description
        assert len(steps[0].instructions) == 3
        assert len(steps[0].tips) == 3

        # Check second step - Authentication
        assert "Authentication Setup" in steps[1].title
        assert "yt auth login" == steps[1].command_example
        assert len(steps[1].instructions) == 4

        # Check third step - Verification
        assert "Verify Your Setup" in steps[2].title
        assert "yt projects list" == steps[2].command_example

        # Check fourth step - Configuration
        assert "Configuration Options" in steps[3].title
        assert "yt config list" == steps[3].command_example


class TestIssuesTutorial:
    """Test the IssuesTutorial class."""

    def test_init(self):
        """Test IssuesTutorial initialization."""
        tutorial = IssuesTutorial()

        assert tutorial.module_id == "issues"
        assert tutorial.title == "Working with Issues"
        assert "create, update, and manage YouTrack issues" in tutorial.description

    def test_create_steps(self):
        """Test creating tutorial steps."""
        tutorial = IssuesTutorial()
        steps = tutorial.create_steps()

        assert len(steps) == 5

        # Check first step
        assert "Understanding Issues" in steps[0].title
        assert "Issues are the core of YouTrack" in steps[0].description

        # Check second step - Listing
        assert "Listing Issues" in steps[1].title
        assert "yt issues list --top 10" == steps[1].command_example

        # Check third step - Creating
        assert "Creating Your First Issue" in steps[2].title
        assert 'yt issues create PROJECT-ID "Tutorial practice issue"' == steps[2].command_example

        # Check fourth step - Viewing
        assert "Viewing Issue Details" in steps[3].title
        assert "yt issues show ISSUE-ID" == steps[3].command_example

        # Check fifth step - Updating
        assert "Updating Issues" in steps[4].title
        assert 'yt issues update ISSUE-ID --state "In Progress"' == steps[4].command_example


class TestProjectsTutorial:
    """Test the ProjectsTutorial class."""

    def test_init(self):
        """Test ProjectsTutorial initialization."""
        tutorial = ProjectsTutorial()

        assert tutorial.module_id == "projects"
        assert tutorial.title == "Managing Projects"
        assert "work with YouTrack projects" in tutorial.description

    def test_create_steps(self):
        """Test creating tutorial steps."""
        tutorial = ProjectsTutorial()
        steps = tutorial.create_steps()

        assert len(steps) == 4

        # Check first step
        assert "Understanding Projects" in steps[0].title
        assert "Projects organize issues" in steps[0].description

        # Check second step - Exploring
        assert "Exploring Project Lists" in steps[1].title
        assert "yt projects list" == steps[1].command_example

        # Check third step - Details
        assert "Project Details" in steps[2].title
        assert "yt projects list --fields id,name,description,leader,archived" == steps[2].command_example

        # Check fourth step - Custom Fields
        assert "Working with Custom Fields" in steps[3].title
        assert "yt admin fields list" == steps[3].command_example


class TestTimeTutorial:
    """Test the TimeTutorial class."""

    def test_init(self):
        """Test TimeTutorial initialization."""
        tutorial = TimeTutorial()

        assert tutorial.module_id == "time"
        assert tutorial.title == "Time Tracking"
        assert "log work time and track effort" in tutorial.description

    def test_create_steps(self):
        """Test creating tutorial steps."""
        tutorial = TimeTutorial()
        steps = tutorial.create_steps()

        assert len(steps) == 3

        # Check first step
        assert "Understanding Time Tracking" in steps[0].title
        assert "YouTrack can track time spent" in steps[0].description

        # Check second step - Logging
        assert "Logging Time" in steps[1].title
        assert 'yt time log ISSUE-ID "2h 30m" --description "Fixed the bug"' == steps[1].command_example

        # Check third step - Viewing
        assert "Viewing Time Entries" in steps[2].title
        assert "yt time list --issue ISSUE-ID" == steps[2].command_example


class TestDockerTutorial:
    """Test the DockerTutorial class."""

    def test_init(self):
        """Test DockerTutorial initialization."""
        tutorial = DockerTutorial()

        assert tutorial.module_id == "docker"
        assert tutorial.title == "Local YouTrack with Docker"
        assert "Set up a local YouTrack instance" in tutorial.description
        assert tutorial._wizard_url is None

    def test_create_steps(self):
        """Test creating tutorial steps."""
        tutorial = DockerTutorial()
        steps = tutorial.create_steps()

        assert len(steps) == 9

        # Check first step
        assert "Welcome to Docker Tutorial" in steps[0].title
        assert "Docker, perfect for learning" in steps[0].description

        # Check second step - Docker check
        assert "Docker Environment Check" in steps[1].title
        assert steps[1].execute_action is not None
        assert steps[1].validation_check is not None

        # Check third step - Port check
        assert "Port Availability Check" in steps[2].title
        assert steps[2].execute_action is not None
        assert steps[2].validation_check is not None

        # Check fourth step - Image pull
        assert "Download YouTrack Image" in steps[3].title
        assert steps[3].execute_action is not None
        assert steps[3].validation_check is not None

        # Check fifth step - Container start
        assert "Start YouTrack Container" in steps[4].title
        assert steps[4].execute_action is not None
        assert steps[4].validation_check is not None

        # Check cleanup step
        assert "Cleanup Options" in steps[8].title
        assert steps[8].custom_prompt_choices == ["keep", "stop", "remove", "cleanup", "skip"]
        assert steps[8].custom_prompt_handler is not None

    @patch("youtrack_cli.tutorial.modules.check_docker_available")
    def test_get_docker_check_instructions_success(self, mock_check):
        """Test Docker check instructions when Docker is available."""
        tutorial = DockerTutorial()

        instructions = tutorial._get_docker_check_instructions()

        assert "✓ Docker is available and running!" in instructions[0]
        assert len(instructions) == 3
        mock_check.assert_called_once()

    @patch("youtrack_cli.tutorial.modules.check_docker_available")
    def test_get_docker_check_instructions_failure(self, mock_check):
        """Test Docker check instructions when Docker is not available."""
        from youtrack_cli.tutorial.docker_utils import DockerNotAvailableError

        tutorial = DockerTutorial()
        mock_check.side_effect = DockerNotAvailableError("Docker not running")

        instructions = tutorial._get_docker_check_instructions()

        assert "✗ Docker check failed:" in instructions[0]
        assert "docker.com" in instructions[2]
        assert len(instructions) == 4

    @patch("youtrack_cli.tutorial.modules.check_port_available")
    def test_get_port_check_instructions_success(self, mock_check):
        """Test port check instructions when port is available."""
        tutorial = DockerTutorial()

        instructions = tutorial._get_port_check_instructions()

        assert "✓ Port 8080 is available!" in instructions[0]
        assert "http://localhost:8080" in instructions[1]
        assert len(instructions) == 3
        mock_check.assert_called_once()

    @patch("youtrack_cli.tutorial.modules.check_port_available")
    def test_get_port_check_instructions_failure(self, mock_check):
        """Test port check instructions when port is in use."""
        from youtrack_cli.tutorial.docker_utils import PortInUseError

        tutorial = DockerTutorial()
        mock_check.side_effect = PortInUseError("Port 8080 is in use")

        instructions = tutorial._get_port_check_instructions()

        assert "✗ Port check failed:" in instructions[0]
        assert "stop any services" in instructions[1]
        assert len(instructions) == 4

    @patch("youtrack_cli.tutorial.modules.pull_youtrack_image")
    def test_get_image_pull_instructions_success(self, mock_pull):
        """Test image pull instructions when successful."""
        tutorial = DockerTutorial()

        instructions = tutorial._get_image_pull_instructions()

        assert "✓ YouTrack image downloaded successfully!" in instructions[0]
        assert len(instructions) == 3
        mock_pull.assert_called_once()

    @patch("youtrack_cli.tutorial.modules.pull_youtrack_image")
    def test_get_image_pull_instructions_failure(self, mock_pull):
        """Test image pull instructions when pull fails."""
        tutorial = DockerTutorial()
        mock_pull.side_effect = Exception("Network error")

        instructions = tutorial._get_image_pull_instructions()

        assert "✗ Image pull failed:" in instructions[0]
        assert "internet connection" in instructions[1]
        assert len(instructions) == 4

    @patch("youtrack_cli.tutorial.modules.wait_for_youtrack_ready")
    @patch("youtrack_cli.tutorial.modules.start_youtrack_container")
    def test_get_container_start_instructions_success(self, mock_start, mock_wait):
        """Test container start instructions when successful."""
        tutorial = DockerTutorial()
        mock_start.return_value = ("container123", "http://localhost:8080/?wizard_token=abc123")

        instructions = tutorial._get_container_start_instructions()

        assert "✓ YouTrack container started!" in instructions[0]
        assert "container123"[:12] in instructions[0]
        assert "http://localhost:8080/?wizard_token=abc123" in instructions[3]
        assert tutorial._wizard_url == "http://localhost:8080/?wizard_token=abc123"
        mock_start.assert_called_once()
        mock_wait.assert_called_once()

    @patch("youtrack_cli.tutorial.modules.start_youtrack_container")
    def test_get_container_start_instructions_failure(self, mock_start):
        """Test container start instructions when start fails."""
        tutorial = DockerTutorial()
        mock_start.side_effect = Exception("Container failed")

        instructions = tutorial._get_container_start_instructions()

        assert "✗ Container startup failed:" in instructions[0]
        assert "Docker logs" in instructions[1]
        assert len(instructions) == 4

    @patch("youtrack_cli.tutorial.modules.get_setup_instructions")
    def test_get_web_setup_instructions(self, mock_get_setup):
        """Test getting web setup instructions."""
        tutorial = DockerTutorial()
        tutorial._wizard_url = "http://localhost:8080/?wizard_token=abc123"
        mock_get_setup.return_value = ["instruction1", "instruction2"]

        instructions = tutorial._get_web_setup_instructions()

        assert instructions == ["instruction1", "instruction2"]
        mock_get_setup.assert_called_once_with(wizard_url="http://localhost:8080/?wizard_token=abc123")

    @patch("youtrack_cli.tutorial.modules.get_youtrack_url")
    def test_get_cli_config_instructions(self, mock_get_url):
        """Test getting CLI configuration instructions."""
        tutorial = DockerTutorial()
        mock_get_url.return_value = "http://localhost:8080"

        instructions = tutorial._get_cli_config_instructions()

        assert "configure the CLI" in instructions[0]
        assert "API Tokens" in instructions[2]
        assert "http://localhost:8080" in instructions[-1]
        assert len(instructions) == 6

    def test_get_cleanup_instructions(self):
        """Test getting cleanup instructions."""
        tutorial = DockerTutorial()

        instructions = tutorial._get_cleanup_instructions()

        assert "What would you like to do" in instructions[0]
        assert "Keep running" in instructions[3]
        assert "Stop container" in instructions[4]
        assert "Remove container" in instructions[5]
        assert "Full cleanup" in instructions[6]
        assert len(instructions) > 10

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.modules.check_docker_available")
    async def test_execute_docker_check(self, mock_check):
        """Test executing Docker check."""
        tutorial = DockerTutorial()

        await tutorial._execute_docker_check()

        mock_check.assert_called_once()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.modules.check_port_available")
    async def test_execute_port_check(self, mock_check):
        """Test executing port check."""
        tutorial = DockerTutorial()

        await tutorial._execute_port_check()

        mock_check.assert_called_once()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.modules.pull_youtrack_image")
    async def test_execute_image_pull(self, mock_pull):
        """Test executing image pull."""
        tutorial = DockerTutorial()

        await tutorial._execute_image_pull()

        mock_pull.assert_called_once()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.modules.wait_for_youtrack_ready")
    @patch("youtrack_cli.tutorial.modules.start_youtrack_container")
    async def test_execute_container_start(self, mock_start, mock_wait):
        """Test executing container start."""
        tutorial = DockerTutorial()
        mock_start.return_value = ("container123", "http://localhost:8080/?wizard_token=abc123")

        await tutorial._execute_container_start()

        assert tutorial._wizard_url == "http://localhost:8080/?wizard_token=abc123"
        mock_start.assert_called_once()
        mock_wait.assert_called_once()

    @patch("youtrack_cli.tutorial.modules.check_docker_available")
    def test_validate_docker_available_success(self, mock_check):
        """Test validating Docker availability when available."""
        tutorial = DockerTutorial()

        result = tutorial._validate_docker_available()

        assert result is True
        mock_check.assert_called_once()

    @patch("youtrack_cli.tutorial.modules.check_docker_available")
    def test_validate_docker_available_failure(self, mock_check):
        """Test validating Docker availability when not available."""
        from youtrack_cli.tutorial.docker_utils import DockerNotAvailableError

        tutorial = DockerTutorial()
        mock_check.side_effect = DockerNotAvailableError("Docker not available")

        result = tutorial._validate_docker_available()

        assert result is False

    @patch("youtrack_cli.tutorial.modules.check_port_available")
    def test_validate_port_available_success(self, mock_check):
        """Test validating port availability when available."""
        tutorial = DockerTutorial()

        result = tutorial._validate_port_available()

        assert result is True
        mock_check.assert_called_once()

    @patch("youtrack_cli.tutorial.modules.check_port_available")
    def test_validate_port_available_failure(self, mock_check):
        """Test validating port availability when not available."""
        from youtrack_cli.tutorial.docker_utils import PortInUseError

        tutorial = DockerTutorial()
        mock_check.side_effect = PortInUseError("Port in use")

        result = tutorial._validate_port_available()

        assert result is False

    @patch("docker.from_env")
    def test_validate_image_pulled_success(self, mock_docker_from_env):
        """Test validating image pull when image exists."""
        tutorial = DockerTutorial()
        mock_client = MagicMock()
        mock_docker_from_env.return_value = mock_client
        mock_client.images.get.return_value = MagicMock()

        result = tutorial._validate_image_pulled()

        assert result is True
        mock_client.images.get.assert_called_once_with("jetbrains/youtrack:2025.1.66652")

    @patch("docker.from_env")
    def test_validate_image_pulled_failure(self, mock_docker_from_env):
        """Test validating image pull when image doesn't exist."""
        tutorial = DockerTutorial()
        mock_client = MagicMock()
        mock_docker_from_env.return_value = mock_client
        mock_client.images.get.side_effect = Exception("Image not found")

        result = tutorial._validate_image_pulled()

        assert result is False

    @patch("requests.get")
    @patch("docker.from_env")
    @patch("youtrack_cli.tutorial.modules.get_youtrack_url")
    def test_validate_container_running_success(self, mock_get_url, mock_docker_from_env, mock_requests):
        """Test validating container running when container is ready."""
        tutorial = DockerTutorial()
        mock_client = MagicMock()
        mock_docker_from_env.return_value = mock_client
        mock_container = MagicMock()
        mock_client.containers.list.return_value = [mock_container]
        mock_get_url.return_value = "http://localhost:8080"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.return_value = mock_response

        result = tutorial._validate_container_running()

        assert result is True
        mock_client.containers.list.assert_called_once_with(filters={"name": "youtrack"})
        mock_requests.assert_called_once_with("http://localhost:8080", timeout=5)

    @patch("docker.from_env")
    def test_validate_container_running_no_container(self, mock_docker_from_env):
        """Test validating container running when no container exists."""
        tutorial = DockerTutorial()
        mock_client = MagicMock()
        mock_docker_from_env.return_value = mock_client
        mock_client.containers.list.return_value = []

        result = tutorial._validate_container_running()

        assert result is False

    @patch("requests.get")
    @patch("docker.from_env")
    @patch("youtrack_cli.tutorial.modules.get_youtrack_url")
    def test_validate_container_running_not_ready(self, mock_get_url, mock_docker_from_env, mock_requests):
        """Test validating container running when container exists but not ready."""
        tutorial = DockerTutorial()
        mock_client = MagicMock()
        mock_docker_from_env.return_value = mock_client
        mock_container = MagicMock()
        mock_client.containers.list.return_value = [mock_container]
        mock_get_url.return_value = "http://localhost:8080"
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_requests.return_value = mock_response

        result = tutorial._validate_container_running()

        assert result is False

    @patch("youtrack_cli.tutorial.modules.cleanup_youtrack_resources")
    def test_cleanup_resources(self, mock_cleanup):
        """Test cleanup resources method."""
        tutorial = DockerTutorial()

        tutorial.cleanup_resources(remove_data=True)

        mock_cleanup.assert_called_once_with(remove_data=True)

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.modules.get_youtrack_url")
    async def test_handle_cleanup_action_keep(self, mock_get_url):
        """Test handling keep cleanup action."""
        tutorial = DockerTutorial()
        mock_get_url.return_value = "http://localhost:8080"

        with patch("youtrack_cli.console.get_console") as mock_get_console:
            mock_console = MagicMock()
            mock_get_console.return_value = mock_console

            result = await tutorial._handle_cleanup_action("keep")

            assert result is True
            mock_console.print.assert_called()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.modules.stop_youtrack_container")
    async def test_handle_cleanup_action_stop_success(self, mock_stop):
        """Test handling stop cleanup action successfully."""
        tutorial = DockerTutorial()

        with patch("youtrack_cli.console.get_console") as mock_get_console:
            mock_console = MagicMock()
            mock_get_console.return_value = mock_console

            result = await tutorial._handle_cleanup_action("stop")

            assert result is True
            mock_stop.assert_called_once()
            mock_console.print.assert_called()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.modules.stop_youtrack_container")
    async def test_handle_cleanup_action_stop_failure(self, mock_stop):
        """Test handling stop cleanup action with failure."""
        tutorial = DockerTutorial()
        mock_stop.side_effect = Exception("Stop failed")

        with patch("youtrack_cli.console.get_console") as mock_get_console:
            mock_console = MagicMock()
            mock_get_console.return_value = mock_console

            result = await tutorial._handle_cleanup_action("stop")

            assert result is False
            mock_console.print.assert_called()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.modules.remove_youtrack_container")
    async def test_handle_cleanup_action_remove_success(self, mock_remove):
        """Test handling remove cleanup action successfully."""
        tutorial = DockerTutorial()

        with patch("youtrack_cli.console.get_console") as mock_get_console:
            mock_console = MagicMock()
            mock_get_console.return_value = mock_console

            result = await tutorial._handle_cleanup_action("remove")

            assert result is True
            mock_remove.assert_called_once()
            mock_console.print.assert_called()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.modules.cleanup_youtrack_resources")
    async def test_handle_cleanup_action_cleanup_success(self, mock_cleanup):
        """Test handling cleanup action successfully."""
        tutorial = DockerTutorial()

        with patch("youtrack_cli.console.get_console") as mock_get_console:
            mock_console = MagicMock()
            mock_get_console.return_value = mock_console

            result = await tutorial._handle_cleanup_action("cleanup")

            assert result is True
            mock_cleanup.assert_called_once_with(remove_data=True)
            mock_console.print.assert_called()

    @pytest.mark.asyncio
    @patch("youtrack_cli.tutorial.modules.get_youtrack_url")
    async def test_handle_cleanup_action_skip(self, mock_get_url):
        """Test handling skip cleanup action."""
        tutorial = DockerTutorial()
        mock_get_url.return_value = "http://localhost:8080"

        with patch("youtrack_cli.console.get_console") as mock_get_console:
            mock_console = MagicMock()
            mock_get_console.return_value = mock_console

            result = await tutorial._handle_cleanup_action("skip")

            assert result is True
            mock_console.print.assert_called()

    @pytest.mark.asyncio
    async def test_handle_cleanup_action_unknown(self):
        """Test handling unknown cleanup action."""
        tutorial = DockerTutorial()

        with patch("youtrack_cli.console.get_console") as mock_get_console:
            mock_console = MagicMock()
            mock_get_console.return_value = mock_console

            result = await tutorial._handle_cleanup_action("unknown")

            assert result is False
            mock_console.print.assert_called()


class TestGetDefaultModules:
    """Test the get_default_modules function."""

    def test_get_default_modules(self):
        """Test getting default modules."""
        modules = get_default_modules()

        assert len(modules) == 5
        assert isinstance(modules[0], SetupTutorial)
        assert isinstance(modules[1], IssuesTutorial)
        assert isinstance(modules[2], ProjectsTutorial)
        assert isinstance(modules[3], TimeTutorial)
        assert isinstance(modules[4], DockerTutorial)

    def test_default_modules_properties(self):
        """Test default modules have correct properties."""
        modules = get_default_modules()

        module_ids = [module.module_id for module in modules]
        assert module_ids == ["setup", "issues", "projects", "time", "docker"]

        # Check that all modules have titles and descriptions
        for module in modules:
            assert module.title
            assert module.description
            assert module.module_id

    def test_default_modules_create_steps(self):
        """Test that all default modules can create steps."""
        modules = get_default_modules()

        for module in modules:
            steps = module.create_steps()
            assert len(steps) > 0

            # Each step should have required properties
            for step in steps:
                assert step.title
                assert step.description
