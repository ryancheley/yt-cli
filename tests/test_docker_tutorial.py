"""Tests for Docker tutorial functionality."""

from unittest.mock import Mock, patch

import pytest
from docker.errors import DockerException, NotFound

from youtrack_cli.tutorial.docker_utils import (
    DockerError,
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
    remove_youtrack_volume,
    start_youtrack_container,
    stop_youtrack_container,
    wait_for_youtrack_ready,
)
from youtrack_cli.tutorial.modules import DockerTutorial


class TestDockerUtils:
    """Test Docker utility functions."""

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_check_docker_available_success(self, mock_docker):
        """Test successful Docker availability check."""
        mock_client = Mock()
        mock_docker.return_value = mock_client

        check_docker_available()

        mock_client.ping.assert_called_once()

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_check_docker_available_failure(self, mock_docker):
        """Test Docker availability check failure."""
        mock_docker.side_effect = DockerException("Docker not available")

        with pytest.raises(DockerNotAvailableError):
            check_docker_available()

    @patch("youtrack_cli.tutorial.docker_utils.socket.socket")
    def test_check_port_available_success(self, mock_socket):
        """Test successful port availability check."""
        mock_sock = Mock()
        mock_socket.return_value.__enter__.return_value = mock_sock

        check_port_available(8080)

        mock_sock.bind.assert_called_once_with(("localhost", 8080))

    @patch("youtrack_cli.tutorial.docker_utils.socket.socket")
    def test_check_port_available_failure(self, mock_socket):
        """Test port availability check failure."""
        mock_sock = Mock()
        mock_sock.bind.side_effect = OSError("Port in use")
        mock_socket.return_value.__enter__.return_value = mock_sock

        with pytest.raises(PortInUseError):
            check_port_available(8080)

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_pull_youtrack_image_success(self, mock_console, mock_docker):
        """Test successful YouTrack image pull."""
        mock_client = Mock()
        mock_docker.return_value = mock_client

        pull_youtrack_image()

        mock_client.images.pull.assert_called_once_with("jetbrains/youtrack:latest")

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_pull_youtrack_image_failure(self, mock_docker):
        """Test YouTrack image pull failure."""
        mock_client = Mock()
        mock_client.images.pull.side_effect = DockerException("Pull failed")
        mock_docker.return_value = mock_client

        with pytest.raises(DockerError):
            pull_youtrack_image()

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_start_youtrack_container_success(self, mock_console, mock_docker):
        """Test successful YouTrack container startup."""
        mock_client = Mock()
        mock_container = Mock()
        mock_container.id = "container123"
        mock_container.short_id = "contain123"

        # Mock existing container not found
        mock_client.containers.get.side_effect = NotFound("Container not found")
        mock_client.containers.run.return_value = mock_container

        # Mock volume not found, so it gets created
        mock_client.volumes.get.side_effect = NotFound("Volume not found")

        mock_docker.return_value = mock_client

        container_id = start_youtrack_container(8080)

        assert container_id == "container123"
        mock_client.volumes.create.assert_called_once()
        mock_client.containers.run.assert_called_once()

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_start_youtrack_container_failure(self, mock_docker):
        """Test YouTrack container startup failure."""
        mock_client = Mock()
        mock_client.containers.get.side_effect = NotFound("Container not found")
        mock_client.volumes.get.side_effect = NotFound("Volume not found")
        mock_client.containers.run.side_effect = DockerException("Start failed")
        mock_docker.return_value = mock_client

        with pytest.raises(DockerError):
            start_youtrack_container(8080)

    @patch("youtrack_cli.tutorial.docker_utils.time.sleep")
    @patch("youtrack_cli.tutorial.docker_utils.socket.socket")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_wait_for_youtrack_ready_success(self, mock_console, mock_socket, mock_sleep):
        """Test successful YouTrack readiness check."""
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 0  # Success
        mock_socket.return_value.__enter__.return_value = mock_sock

        wait_for_youtrack_ready(8080, timeout=10)

        mock_sock.connect_ex.assert_called_with(("localhost", 8080))

    @patch("youtrack_cli.tutorial.docker_utils.time.sleep")
    @patch("youtrack_cli.tutorial.docker_utils.time.time")
    @patch("youtrack_cli.tutorial.docker_utils.socket.socket")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_wait_for_youtrack_ready_timeout(self, mock_console, mock_socket, mock_time, mock_sleep):
        """Test YouTrack readiness check timeout."""
        mock_sock = Mock()
        mock_sock.connect_ex.return_value = 1  # Connection failed
        mock_socket.return_value.__enter__.return_value = mock_sock

        # Mock time to simulate timeout
        mock_time.side_effect = [0, 10, 20]  # Start, during, timeout

        with pytest.raises(YouTrackStartupError):
            wait_for_youtrack_ready(8080, timeout=10)

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_stop_youtrack_container_success(self, mock_console, mock_docker):
        """Test successful YouTrack container stop."""
        mock_client = Mock()
        mock_container = Mock()
        mock_client.containers.get.return_value = mock_container
        mock_docker.return_value = mock_client

        stop_youtrack_container()

        mock_container.stop.assert_called_once()

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_stop_youtrack_container_not_found(self, mock_console, mock_docker):
        """Test stopping non-existent container."""
        mock_client = Mock()
        mock_client.containers.get.side_effect = NotFound("Container not found")
        mock_docker.return_value = mock_client

        stop_youtrack_container()  # Should not raise

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_remove_youtrack_container_success(self, mock_console, mock_docker):
        """Test successful YouTrack container removal."""
        mock_client = Mock()
        mock_container = Mock()
        mock_client.containers.get.return_value = mock_container
        mock_docker.return_value = mock_client

        remove_youtrack_container()

        mock_container.remove.assert_called_once_with(force=True)

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_remove_youtrack_volume_success(self, mock_console, mock_docker):
        """Test successful YouTrack volume removal."""
        mock_client = Mock()
        mock_volume = Mock()
        mock_client.volumes.get.return_value = mock_volume
        mock_docker.return_value = mock_client

        remove_youtrack_volume()

        mock_volume.remove.assert_called_once()

    @patch("youtrack_cli.tutorial.docker_utils.stop_youtrack_container")
    @patch("youtrack_cli.tutorial.docker_utils.remove_youtrack_container")
    @patch("youtrack_cli.tutorial.docker_utils.remove_youtrack_volume")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_cleanup_youtrack_resources(self, mock_console, mock_remove_volume, mock_remove_container, mock_stop):
        """Test cleanup of YouTrack resources."""
        cleanup_youtrack_resources(remove_data=True)

        mock_stop.assert_called_once()
        mock_remove_container.assert_called_once()
        mock_remove_volume.assert_called_once()

    @patch("youtrack_cli.tutorial.docker_utils.stop_youtrack_container")
    @patch("youtrack_cli.tutorial.docker_utils.remove_youtrack_container")
    @patch("youtrack_cli.tutorial.docker_utils.remove_youtrack_volume")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_cleanup_youtrack_resources_no_data_removal(
        self, mock_console, mock_remove_volume, mock_remove_container, mock_stop
    ):
        """Test cleanup without removing data volume."""
        cleanup_youtrack_resources(remove_data=False)

        mock_stop.assert_called_once()
        mock_remove_container.assert_called_once()
        mock_remove_volume.assert_not_called()

    def test_get_youtrack_url(self):
        """Test YouTrack URL generation."""
        url = get_youtrack_url(8080)
        assert url == "http://localhost:8080"

        url = get_youtrack_url(9000)
        assert url == "http://localhost:9000"

    def test_get_setup_instructions(self):
        """Test setup instructions generation."""
        instructions = get_setup_instructions(8080)

        assert len(instructions) > 0
        assert "http://localhost:8080" in instructions[0]
        assert any("administrator" in instr for instr in instructions)


class TestDockerTutorial:
    """Test DockerTutorial class."""

    def test_docker_tutorial_init(self):
        """Test DockerTutorial initialization."""
        tutorial = DockerTutorial()

        assert tutorial.module_id == "docker"
        assert tutorial.title == "Local YouTrack with Docker"
        assert "Docker" in tutorial.description

    def test_docker_tutorial_create_steps(self):
        """Test DockerTutorial step creation."""
        tutorial = DockerTutorial()
        steps = tutorial.create_steps()

        assert len(steps) == 9  # Should have 9 steps
        assert steps[0].title == "Welcome to Docker Tutorial"
        assert steps[-1].title == "Cleanup Options"

    @patch("youtrack_cli.tutorial.modules.check_docker_available")
    def test_docker_check_instructions_success(self, mock_check):
        """Test Docker check instructions when Docker is available."""
        tutorial = DockerTutorial()
        instructions = tutorial._get_docker_check_instructions()

        assert "✓ Docker is available and running!" in instructions[0]

    @patch("youtrack_cli.tutorial.modules.check_docker_available")
    def test_docker_check_instructions_failure(self, mock_check):
        """Test Docker check instructions when Docker is not available."""
        mock_check.side_effect = DockerNotAvailableError("Docker not found")
        tutorial = DockerTutorial()
        instructions = tutorial._get_docker_check_instructions()

        assert "✗ Docker check failed" in instructions[0]

    @patch("youtrack_cli.tutorial.modules.check_port_available")
    def test_port_check_instructions_success(self, mock_check):
        """Test port check instructions when port is available."""
        tutorial = DockerTutorial()
        instructions = tutorial._get_port_check_instructions()

        assert "✓ Port 8080 is available!" in instructions[0]

    @patch("youtrack_cli.tutorial.modules.check_port_available")
    def test_port_check_instructions_failure(self, mock_check):
        """Test port check instructions when port is in use."""
        mock_check.side_effect = PortInUseError("Port in use")
        tutorial = DockerTutorial()
        instructions = tutorial._get_port_check_instructions()

        assert "✗ Port check failed" in instructions[0]

    @patch("youtrack_cli.tutorial.modules.pull_youtrack_image")
    def test_image_pull_instructions_success(self, mock_pull):
        """Test image pull instructions on success."""
        tutorial = DockerTutorial()
        instructions = tutorial._get_image_pull_instructions()

        assert "✓ YouTrack image downloaded successfully!" in instructions[0]

    @patch("youtrack_cli.tutorial.modules.pull_youtrack_image")
    def test_image_pull_instructions_failure(self, mock_pull):
        """Test image pull instructions on failure."""
        mock_pull.side_effect = Exception("Pull failed")
        tutorial = DockerTutorial()
        instructions = tutorial._get_image_pull_instructions()

        assert "✗ Image pull failed" in instructions[0]

    @patch("youtrack_cli.tutorial.modules.start_youtrack_container")
    @patch("youtrack_cli.tutorial.modules.wait_for_youtrack_ready")
    def test_container_start_instructions_success(self, mock_wait, mock_start):
        """Test container start instructions on success."""
        mock_start.return_value = "container123"
        tutorial = DockerTutorial()
        instructions = tutorial._get_container_start_instructions()

        assert "✓ YouTrack container started!" in instructions[0]
        assert "container123"[:12] in instructions[0]

    @patch("youtrack_cli.tutorial.modules.start_youtrack_container")
    def test_container_start_instructions_failure(self, mock_start):
        """Test container start instructions on failure."""
        mock_start.side_effect = Exception("Start failed")
        tutorial = DockerTutorial()
        instructions = tutorial._get_container_start_instructions()

        assert "✗ Container startup failed" in instructions[0]

    @patch("youtrack_cli.tutorial.modules.get_setup_instructions")
    def test_web_setup_instructions(self, mock_get_setup):
        """Test web setup instructions."""
        mock_get_setup.return_value = ["instruction1", "instruction2"]
        tutorial = DockerTutorial()
        instructions = tutorial._get_web_setup_instructions()

        assert instructions == ["instruction1", "instruction2"]

    def test_cli_config_instructions(self):
        """Test CLI configuration instructions."""
        tutorial = DockerTutorial()
        instructions = tutorial._get_cli_config_instructions()

        assert len(instructions) > 0
        assert any("API Tokens" in instr for instr in instructions)
        assert any("http://localhost:8080" in instr for instr in instructions)

    def test_cleanup_instructions(self):
        """Test cleanup instructions."""
        tutorial = DockerTutorial()
        instructions = tutorial._get_cleanup_instructions()

        assert len(instructions) > 0
        assert any("Keep running" in instr for instr in instructions)
        assert any("Full cleanup" in instr for instr in instructions)

    @patch("youtrack_cli.tutorial.modules.cleanup_youtrack_resources")
    def test_cleanup_resources(self, mock_cleanup):
        """Test cleanup resources method."""
        tutorial = DockerTutorial()
        tutorial.cleanup_resources(remove_data=True)

        mock_cleanup.assert_called_once_with(remove_data=True)
