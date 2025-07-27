"""Tests for tutorial docker utilities."""

from unittest.mock import MagicMock, patch

import pytest
from docker.errors import DockerException, NotFound

from youtrack_cli.tutorial.docker_utils import (
    CONTAINER_NAME,
    DEFAULT_PORT,
    VOLUME_NAME,
    YOUTRACK_IMAGE,
    DockerError,
    DockerNotAvailableError,
    PortInUseError,
    YouTrackStartupError,
    check_docker_available,
    check_port_available,
    cleanup_youtrack_resources,
    extract_wizard_token,
    get_container_logs,
    get_container_status,
    get_setup_instructions,
    get_wizard_url,
    get_youtrack_url,
    pull_youtrack_image,
    remove_youtrack_container,
    remove_youtrack_volume,
    start_youtrack_container,
    stop_youtrack_container,
    wait_for_youtrack_ready,
)


class TestDockerAvailability:
    """Test Docker availability checking."""

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_check_docker_available_success(self, mock_docker):
        """Test successful Docker availability check."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_client.ping.return_value = True

        # Should not raise an exception
        check_docker_available()

        mock_docker.assert_called_once()
        mock_client.ping.assert_called_once()

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_check_docker_available_failure(self, mock_docker):
        """Test Docker availability check when Docker is not available."""
        mock_docker.side_effect = DockerException("Docker not running")

        with pytest.raises(DockerNotAvailableError) as exc_info:
            check_docker_available()

        assert "Docker is not available or not running" in str(exc_info.value)

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_check_docker_available_ping_failure(self, mock_docker):
        """Test Docker availability check when ping fails."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_client.ping.side_effect = DockerException("Ping failed")

        with pytest.raises(DockerNotAvailableError) as exc_info:
            check_docker_available()

        assert "Docker is not available or not running" in str(exc_info.value)


class TestPortAvailability:
    """Test port availability checking."""

    @patch("youtrack_cli.tutorial.docker_utils.socket.socket")
    def test_check_port_available_success(self, mock_socket):
        """Test successful port availability check."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.bind.return_value = None

        # Should not raise an exception
        check_port_available(8080)

        mock_sock.bind.assert_called_once_with(("localhost", 8080))

    @patch("youtrack_cli.tutorial.docker_utils.socket.socket")
    def test_check_port_available_in_use(self, mock_socket):
        """Test port availability check when port is in use."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.bind.side_effect = OSError("Address already in use")

        with pytest.raises(PortInUseError) as exc_info:
            check_port_available(8080)

        assert "Port 8080 is already in use" in str(exc_info.value)

    def test_check_port_available_default_port(self):
        """Test port availability check with default port."""
        with patch("youtrack_cli.tutorial.docker_utils.socket.socket") as mock_socket:
            mock_sock = MagicMock()
            mock_socket.return_value.__enter__.return_value = mock_sock

            check_port_available()

            mock_sock.bind.assert_called_once_with(("localhost", DEFAULT_PORT))


class TestImagePulling:
    """Test Docker image pulling."""

    @patch("youtrack_cli.tutorial.docker_utils.console")
    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_pull_youtrack_image_success(self, mock_docker, mock_console):
        """Test successful image pulling."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        pull_youtrack_image()

        mock_client.images.pull.assert_called_once_with(YOUTRACK_IMAGE)
        mock_console.print.assert_called()

    @patch("youtrack_cli.tutorial.docker_utils.console")
    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_pull_youtrack_image_failure(self, mock_docker, mock_console):
        """Test image pulling failure."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_client.images.pull.side_effect = DockerException("Pull failed")

        with pytest.raises(DockerError) as exc_info:
            pull_youtrack_image()

        assert "Failed to pull YouTrack image" in str(exc_info.value)


class TestContainerManagement:
    """Test container management functions."""

    @patch("youtrack_cli.tutorial.docker_utils.get_wizard_url")
    @patch("youtrack_cli.tutorial.docker_utils.time.sleep")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_start_youtrack_container_success(self, mock_docker, mock_console, mock_sleep, mock_get_wizard):
        """Test successful container startup."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        # Mock existing container
        mock_existing = MagicMock()
        mock_client.containers.get.side_effect = [mock_existing, NotFound("Container not found")]

        # Mock volume creation
        mock_client.volumes.get.side_effect = NotFound("Volume not found")
        mock_volume = MagicMock()
        mock_client.volumes.create.return_value = mock_volume

        # Mock container run
        mock_container = MagicMock()
        mock_container.id = "container123"
        mock_container.short_id = "con123"
        mock_client.containers.run.return_value = mock_container

        mock_get_wizard.return_value = "http://localhost:8080/?wizard_token=abc123"

        container_id, wizard_url = start_youtrack_container(8080)

        assert container_id == "container123"
        assert wizard_url == "http://localhost:8080/?wizard_token=abc123"
        mock_existing.remove.assert_called_once_with(force=True)
        mock_client.volumes.create.assert_called_once_with(VOLUME_NAME)
        mock_client.containers.run.assert_called_once()

    @patch("youtrack_cli.tutorial.docker_utils.console")
    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_start_youtrack_container_failure(self, mock_docker, mock_console):
        """Test container startup failure."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_client.containers.run.side_effect = DockerException("Run failed")

        with pytest.raises(DockerError) as exc_info:
            start_youtrack_container()

        assert "Failed to start YouTrack container" in str(exc_info.value)

    @patch("youtrack_cli.tutorial.docker_utils.console")
    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_stop_youtrack_container_success(self, mock_docker, mock_console):
        """Test successful container stopping."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container

        stop_youtrack_container()

        mock_client.containers.get.assert_called_once_with(CONTAINER_NAME)
        mock_container.stop.assert_called_once()

    @patch("youtrack_cli.tutorial.docker_utils.console")
    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_stop_youtrack_container_not_found(self, mock_docker, mock_console):
        """Test stopping container when container doesn't exist."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_client.containers.get.side_effect = NotFound("Container not found")

        # Should not raise an exception
        stop_youtrack_container()

        mock_console.print.assert_called()

    @patch("youtrack_cli.tutorial.docker_utils.console")
    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_stop_youtrack_container_failure(self, mock_docker, mock_console):
        """Test container stopping failure."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        mock_container = MagicMock()
        mock_container.stop.side_effect = DockerException("Stop failed")
        mock_client.containers.get.return_value = mock_container

        with pytest.raises(DockerError) as exc_info:
            stop_youtrack_container()

        assert "Failed to stop YouTrack container" in str(exc_info.value)

    @patch("youtrack_cli.tutorial.docker_utils.console")
    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_remove_youtrack_container_success(self, mock_docker, mock_console):
        """Test successful container removal."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        mock_container = MagicMock()
        mock_client.containers.get.return_value = mock_container

        remove_youtrack_container()

        mock_container.remove.assert_called_once_with(force=True)

    @patch("youtrack_cli.tutorial.docker_utils.console")
    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_remove_youtrack_container_not_found(self, mock_docker, mock_console):
        """Test removing container when container doesn't exist."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_client.containers.get.side_effect = NotFound("Container not found")

        # Should not raise an exception
        remove_youtrack_container()

        mock_console.print.assert_called()

    @patch("youtrack_cli.tutorial.docker_utils.console")
    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_remove_youtrack_volume_success(self, mock_docker, mock_console):
        """Test successful volume removal."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        mock_volume = MagicMock()
        mock_client.volumes.get.return_value = mock_volume

        remove_youtrack_volume()

        mock_volume.remove.assert_called_once()

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_get_container_status_success(self, mock_docker):
        """Test getting container status when container exists."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        mock_container = MagicMock()
        mock_container.status = "running"
        mock_client.containers.get.return_value = mock_container

        status = get_container_status()

        assert status == "running"

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_get_container_status_not_found(self, mock_docker):
        """Test getting container status when container doesn't exist."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_client.containers.get.side_effect = NotFound("Container not found")

        status = get_container_status()

        assert status is None

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_get_container_status_docker_error(self, mock_docker):
        """Test getting container status when Docker error occurs."""
        mock_docker.side_effect = DockerException("Docker error")

        status = get_container_status()

        assert status is None


class TestWaitForYouTrack:
    """Test waiting for YouTrack to be ready."""

    @patch("youtrack_cli.tutorial.docker_utils.time.sleep")
    @patch("youtrack_cli.tutorial.docker_utils.time.time")
    @patch("youtrack_cli.tutorial.docker_utils.socket.socket")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_wait_for_youtrack_ready_success(self, mock_console, mock_socket, mock_time, mock_sleep):
        """Test successful wait for YouTrack ready."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.connect_ex.return_value = 0  # Success

        # Mock time to simulate first attempt succeeding
        mock_time.side_effect = [0, 1]  # start_time, current_time

        wait_for_youtrack_ready(8080, 300)

        mock_sock.connect_ex.assert_called_with(("localhost", 8080))
        mock_console.print.assert_called()

    @patch("youtrack_cli.tutorial.docker_utils.time.sleep")
    @patch("youtrack_cli.tutorial.docker_utils.time.time")
    @patch("youtrack_cli.tutorial.docker_utils.socket.socket")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_wait_for_youtrack_ready_timeout(self, mock_console, mock_socket, mock_time, mock_sleep):
        """Test timeout waiting for YouTrack ready."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.connect_ex.return_value = 1  # Connection refused

        # Mock time to simulate timeout
        mock_time.side_effect = [0, 301]  # start_time, current_time (past timeout)

        with pytest.raises(YouTrackStartupError) as exc_info:
            wait_for_youtrack_ready(8080, 300)

        assert "YouTrack did not become ready within 300 seconds" in str(exc_info.value)

    @patch("youtrack_cli.tutorial.docker_utils.time.sleep")
    @patch("youtrack_cli.tutorial.docker_utils.time.time")
    @patch("youtrack_cli.tutorial.docker_utils.socket.socket")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_wait_for_youtrack_ready_exception_handling(self, mock_console, mock_socket, mock_time, mock_sleep):
        """Test exception handling during wait."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.connect_ex.side_effect = [Exception("Network error"), 0]  # First fails, second succeeds

        # Mock time progression
        mock_time.side_effect = [0, 5, 10]  # start_time, first check, second check

        wait_for_youtrack_ready(8080, 300)

        assert mock_sock.connect_ex.call_count == 2


class TestLogsAndWizard:
    """Test log handling and wizard URL extraction."""

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_get_container_logs_success(self, mock_docker):
        """Test successful log retrieval."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client

        mock_container = MagicMock()
        mock_container.logs.return_value = b"Log line 1\nLog line 2\n"
        mock_client.containers.get.return_value = mock_container

        logs = get_container_logs(CONTAINER_NAME, 50)

        assert logs == "Log line 1\nLog line 2\n"
        mock_container.logs.assert_called_once_with(tail=50)

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_get_container_logs_not_found(self, mock_docker):
        """Test log retrieval when container not found."""
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        mock_client.containers.get.side_effect = NotFound("Container not found")

        logs = get_container_logs(CONTAINER_NAME)

        assert logs is None

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_get_container_logs_docker_error(self, mock_docker):
        """Test log retrieval when Docker error occurs."""
        mock_docker.side_effect = DockerException("Docker error")

        logs = get_container_logs(CONTAINER_NAME)

        assert logs is None

    def test_extract_wizard_token_success(self):
        """Test successful wizard token extraction."""
        logs = "Some log content\nwizard_token=abc123def456\nMore log content"

        token = extract_wizard_token(logs)

        assert token == "abc123def456"

    def test_extract_wizard_token_not_found(self):
        """Test wizard token extraction when token not found."""
        logs = "Some log content without token"

        token = extract_wizard_token(logs)

        assert token is None

    def test_extract_wizard_token_multiple_matches(self):
        """Test wizard token extraction with multiple matches (should return first)."""
        logs = "wizard_token=first123\nwizard_token=second456"

        token = extract_wizard_token(logs)

        assert token == "first123"

    @patch("youtrack_cli.tutorial.docker_utils.get_container_logs")
    def test_get_wizard_url_with_token(self, mock_get_logs):
        """Test getting wizard URL with token."""
        mock_get_logs.return_value = "Log content\nwizard_token=abc123\nMore logs"

        url = get_wizard_url(8080, CONTAINER_NAME)

        assert url == "http://localhost:8080/?wizard_token=abc123"

    @patch("youtrack_cli.tutorial.docker_utils.get_container_logs")
    def test_get_wizard_url_no_token(self, mock_get_logs):
        """Test getting wizard URL when no token found."""
        mock_get_logs.return_value = "Log content without token"

        url = get_wizard_url(8080, CONTAINER_NAME)

        assert url == "http://localhost:8080"

    @patch("youtrack_cli.tutorial.docker_utils.get_container_logs")
    def test_get_wizard_url_no_logs(self, mock_get_logs):
        """Test getting wizard URL when no logs available."""
        mock_get_logs.return_value = None

        url = get_wizard_url(8080, CONTAINER_NAME)

        assert url == "http://localhost:8080"


class TestUtilityFunctions:
    """Test utility functions."""

    def test_get_youtrack_url_default_port(self):
        """Test getting YouTrack URL with default port."""
        url = get_youtrack_url()

        assert url == f"http://localhost:{DEFAULT_PORT}"

    def test_get_youtrack_url_custom_port(self):
        """Test getting YouTrack URL with custom port."""
        url = get_youtrack_url(9080)

        assert url == "http://localhost:9080"

    def test_get_setup_instructions_default(self):
        """Test getting setup instructions with default URL."""
        instructions = get_setup_instructions(8080)

        assert isinstance(instructions, list)
        assert len(instructions) > 5
        assert "http://localhost:8080" in instructions[0]
        assert "YouTrack Configuration Wizard" in " ".join(instructions)

    def test_get_setup_instructions_with_wizard_url(self):
        """Test getting setup instructions with wizard URL."""
        wizard_url = "http://localhost:8080/?wizard_token=abc123"
        instructions = get_setup_instructions(8080, wizard_url)

        assert isinstance(instructions, list)
        assert wizard_url in instructions[0]

    def test_get_setup_instructions_structure(self):
        """Test setup instructions structure."""
        instructions = get_setup_instructions()

        # Should contain numbered steps
        step_1_found = any("1." in instruction for instruction in instructions)
        step_2_found = any("2." in instruction for instruction in instructions)
        step_3_found = any("3." in instruction for instruction in instructions)

        assert step_1_found
        assert step_2_found
        assert step_3_found


class TestCleanup:
    """Test cleanup functionality."""

    @patch("youtrack_cli.tutorial.docker_utils.remove_youtrack_volume")
    @patch("youtrack_cli.tutorial.docker_utils.remove_youtrack_container")
    @patch("youtrack_cli.tutorial.docker_utils.stop_youtrack_container")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_cleanup_youtrack_resources_with_data(
        self, mock_console, mock_stop, mock_remove_container, mock_remove_volume
    ):
        """Test cleanup with data removal."""
        cleanup_youtrack_resources(remove_data=True)

        mock_stop.assert_called_once()
        mock_remove_container.assert_called_once()
        mock_remove_volume.assert_called_once()

    @patch("youtrack_cli.tutorial.docker_utils.remove_youtrack_volume")
    @patch("youtrack_cli.tutorial.docker_utils.remove_youtrack_container")
    @patch("youtrack_cli.tutorial.docker_utils.stop_youtrack_container")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_cleanup_youtrack_resources_without_data(
        self, mock_console, mock_stop, mock_remove_container, mock_remove_volume
    ):
        """Test cleanup without data removal."""
        cleanup_youtrack_resources(remove_data=False)

        mock_stop.assert_called_once()
        mock_remove_container.assert_called_once()
        mock_remove_volume.assert_not_called()

    @patch("youtrack_cli.tutorial.docker_utils.remove_youtrack_container")
    @patch("youtrack_cli.tutorial.docker_utils.stop_youtrack_container")
    @patch("youtrack_cli.tutorial.docker_utils.console")
    def test_cleanup_youtrack_resources_with_errors(self, mock_console, mock_stop, mock_remove_container):
        """Test cleanup handling errors gracefully."""
        mock_stop.side_effect = DockerError("Stop failed")
        mock_remove_container.side_effect = DockerError("Remove failed")

        # Should not raise exception despite errors
        cleanup_youtrack_resources()

        mock_stop.assert_called_once()
        mock_remove_container.assert_called_once()
        # Should print warnings for errors
        assert mock_console.print.call_count >= 3  # At least start, two warnings, completion


class TestExceptionClasses:
    """Test custom exception classes."""

    def test_docker_error_inheritance(self):
        """Test DockerError inheritance."""
        error = DockerError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_docker_not_available_error_inheritance(self):
        """Test DockerNotAvailableError inheritance."""
        error = DockerNotAvailableError("Docker not available")
        assert isinstance(error, DockerError)
        assert isinstance(error, Exception)
        assert str(error) == "Docker not available"

    def test_port_in_use_error_inheritance(self):
        """Test PortInUseError inheritance."""
        error = PortInUseError("Port in use")
        assert isinstance(error, DockerError)
        assert isinstance(error, Exception)
        assert str(error) == "Port in use"

    def test_youtrack_startup_error_inheritance(self):
        """Test YouTrackStartupError inheritance."""
        error = YouTrackStartupError("Startup failed")
        assert isinstance(error, DockerError)
        assert isinstance(error, Exception)
        assert str(error) == "Startup failed"


class TestConstants:
    """Test module constants."""

    def test_constants_exist(self):
        """Test that required constants are defined."""
        assert YOUTRACK_IMAGE is not None
        assert CONTAINER_NAME is not None
        assert VOLUME_NAME is not None
        assert DEFAULT_PORT is not None
        assert isinstance(DEFAULT_PORT, int)

    def test_container_name_format(self):
        """Test container name format."""
        assert "youtrack" in CONTAINER_NAME.lower()
        assert "tutorial" in CONTAINER_NAME.lower()

    def test_volume_name_format(self):
        """Test volume name format."""
        assert "youtrack" in VOLUME_NAME.lower()
        assert "tutorial" in VOLUME_NAME.lower()

    def test_default_port_valid(self):
        """Test default port is valid."""
        assert 1 <= DEFAULT_PORT <= 65535
