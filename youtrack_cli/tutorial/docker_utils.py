"""Docker utilities for YouTrack tutorial system."""

import re
import socket
import time
from typing import Optional, Tuple

import docker
from docker.errors import DockerException, NotFound
from rich.console import Console

console = Console()

YOUTRACK_IMAGE = "jetbrains/youtrack:2025.1.66652"
CONTAINER_NAME = "youtrack-tutorial"
VOLUME_NAME = "youtrack-tutorial-data"
DEFAULT_PORT = 8080
YOUTRACK_CONTAINER_PORT = 8080


class DockerError(Exception):
    """Base exception for Docker-related errors."""

    pass


class DockerNotAvailableError(DockerError):
    """Raised when Docker is not available or not running."""

    pass


class PortInUseError(DockerError):
    """Raised when the required port is already in use."""

    pass


class YouTrackStartupError(DockerError):
    """Raised when YouTrack fails to start properly."""

    pass


def check_docker_available() -> None:
    """Check if Docker is available and running.

    Raises:
        DockerNotAvailableError: If Docker is not available or not running.
    """
    try:
        client = docker.from_env()
        client.ping()
    except DockerException as e:
        raise DockerNotAvailableError(
            "Docker is not available or not running. Please ensure Docker is installed and running."
        ) from e


def check_port_available(port: int = DEFAULT_PORT) -> None:
    """Check if the specified port is available.

    Args:
        port: Port number to check.

    Raises:
        PortInUseError: If the port is already in use.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("localhost", port))
    except OSError as e:
        raise PortInUseError(f"Port {port} is already in use. Please stop any services using this port.") from e


def pull_youtrack_image() -> None:
    """Pull the YouTrack Docker image.

    Raises:
        DockerError: If image pull fails.
    """
    try:
        client = docker.from_env()
        console.print(f"[yellow]Pulling YouTrack image: {YOUTRACK_IMAGE}[/yellow]")
        console.print("[dim]This may take a few minutes for the first time...[/dim]")

        client.images.pull(YOUTRACK_IMAGE)
        console.print(f"[green]✓ Successfully pulled {YOUTRACK_IMAGE}[/green]")

    except DockerException as e:
        raise DockerError(f"Failed to pull YouTrack image: {e}") from e


def start_youtrack_container(port: int = DEFAULT_PORT) -> Tuple[str, str]:
    """Start YouTrack container.

    Args:
        port: Host port to bind to.

    Returns:
        Tuple of (Container ID, Wizard URL).

    Raises:
        DockerError: If container startup fails.
    """
    try:
        client = docker.from_env()

        # Remove existing container if it exists
        try:
            existing_container = client.containers.get(CONTAINER_NAME)
            existing_container.remove(force=True)
            console.print(f"[yellow]Removed existing container: {CONTAINER_NAME}[/yellow]")
        except NotFound:
            pass

        # Create volume if it doesn't exist
        try:
            client.volumes.get(VOLUME_NAME)
        except NotFound:
            client.volumes.create(VOLUME_NAME)
            console.print(f"[green]Created volume: {VOLUME_NAME}[/green]")

        # Start container
        console.print(f"[yellow]Starting YouTrack container on port {port}...[/yellow]")
        container = client.containers.run(
            YOUTRACK_IMAGE,
            name=CONTAINER_NAME,
            ports={f"{YOUTRACK_CONTAINER_PORT}/tcp": port},
            volumes={VOLUME_NAME: {"bind": "/opt/youtrack/data", "mode": "rw"}},
            detach=True,
            remove=False,
        )

        console.print(f"[green]✓ YouTrack container started with ID: {container.short_id}[/green]")

        # Wait a bit for the container to generate logs
        time.sleep(2)

        # Get the wizard URL from logs
        wizard_url = get_wizard_url(port, CONTAINER_NAME)

        return container.id, wizard_url

    except DockerException as e:
        raise DockerError(f"Failed to start YouTrack container: {e}") from e


def wait_for_youtrack_ready(port: int = DEFAULT_PORT, timeout: int = 300) -> None:
    """Wait for YouTrack to be ready and accessible.

    Args:
        port: Port to check.
        timeout: Maximum time to wait in seconds.

    Raises:
        YouTrackStartupError: If YouTrack doesn't become ready within timeout.
    """
    console.print("[yellow]Waiting for YouTrack to be ready...[/yellow]")
    console.print("[dim]This may take several minutes on first startup...[/dim]")

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                result = sock.connect_ex(("localhost", port))
                if result == 0:
                    console.print("[green]✓ YouTrack is ready![/green]")
                    return
        except Exception:
            pass

        console.print(".", end="", style="dim")
        time.sleep(5)

    raise YouTrackStartupError(f"YouTrack did not become ready within {timeout} seconds")


def get_container_status() -> Optional[str]:
    """Get the status of the YouTrack tutorial container.

    Returns:
        Container status string or None if container doesn't exist.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(CONTAINER_NAME)
        return container.status
    except (DockerException, NotFound):
        return None


def stop_youtrack_container() -> None:
    """Stop the YouTrack container.

    Raises:
        DockerError: If stopping the container fails.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(CONTAINER_NAME)
        container.stop()
        console.print(f"[yellow]Stopped YouTrack container: {CONTAINER_NAME}[/yellow]")
    except NotFound:
        console.print("[dim]YouTrack container was not running[/dim]")
    except DockerException as e:
        raise DockerError(f"Failed to stop YouTrack container: {e}") from e


def remove_youtrack_container() -> None:
    """Remove the YouTrack container.

    Raises:
        DockerError: If removing the container fails.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(CONTAINER_NAME)
        container.remove(force=True)
        console.print(f"[yellow]Removed YouTrack container: {CONTAINER_NAME}[/yellow]")
    except NotFound:
        console.print("[dim]YouTrack container was not found[/dim]")
    except DockerException as e:
        raise DockerError(f"Failed to remove YouTrack container: {e}") from e


def remove_youtrack_volume() -> None:
    """Remove the YouTrack data volume.

    Raises:
        DockerError: If removing the volume fails.
    """
    try:
        client = docker.from_env()
        volume = client.volumes.get(VOLUME_NAME)
        volume.remove()
        console.print(f"[yellow]Removed YouTrack volume: {VOLUME_NAME}[/yellow]")
    except NotFound:
        console.print("[dim]YouTrack volume was not found[/dim]")
    except DockerException as e:
        raise DockerError(f"Failed to remove YouTrack volume: {e}") from e


def cleanup_youtrack_resources(remove_data: bool = False) -> None:
    """Clean up all YouTrack tutorial resources.

    Args:
        remove_data: Whether to remove the data volume as well.
    """
    console.print("[yellow]Cleaning up YouTrack tutorial resources...[/yellow]")

    try:
        stop_youtrack_container()
    except DockerError as e:
        console.print(f"[red]Warning: {e}[/red]")

    try:
        remove_youtrack_container()
    except DockerError as e:
        console.print(f"[red]Warning: {e}[/red]")

    if remove_data:
        try:
            remove_youtrack_volume()
        except DockerError as e:
            console.print(f"[red]Warning: {e}[/red]")

    console.print("[green]✓ Cleanup completed[/green]")


def get_youtrack_url(port: int = DEFAULT_PORT) -> str:
    """Get the YouTrack URL for the local instance.

    Args:
        port: Port number.

    Returns:
        YouTrack URL.
    """
    return f"http://localhost:{port}"


def get_container_logs(container_name: str = CONTAINER_NAME, lines: int = 100) -> Optional[str]:
    """Get logs from the YouTrack container.

    Args:
        container_name: Name of the container.
        lines: Number of log lines to retrieve.

    Returns:
        Container logs as string, or None if container not found.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        logs = container.logs(tail=lines).decode("utf-8")
        return logs
    except (DockerException, NotFound):
        return None


def extract_wizard_token(logs: str) -> Optional[str]:
    """Extract the wizard token from YouTrack container logs.

    Args:
        logs: Container log output.

    Returns:
        Wizard token if found, None otherwise.
    """
    # Pattern to match the wizard token in the URL
    pattern = r"wizard_token=([a-zA-Z0-9_-]+)"
    match = re.search(pattern, logs)
    if match:
        return match.group(1)
    return None


def get_wizard_url(port: int = DEFAULT_PORT, container_name: str = CONTAINER_NAME) -> str:
    """Get the complete wizard URL with token from container logs.

    Args:
        port: Port number YouTrack is running on.
        container_name: Name of the container.

    Returns:
        Complete wizard URL with token, or base URL if token not found.
    """
    logs = get_container_logs(container_name)
    if logs:
        token = extract_wizard_token(logs)
        if token:
            return f"http://localhost:{port}/?wizard_token={token}"

    # Return base URL if we can't find the token
    return get_youtrack_url(port)


def get_setup_instructions(port: int = DEFAULT_PORT, wizard_url: Optional[str] = None) -> list[str]:
    """Get step-by-step setup instructions for YouTrack.

    Args:
        port: Port number.
        wizard_url: Optional wizard URL with token.

    Returns:
        List of instruction strings.
    """
    url = wizard_url or get_youtrack_url(port)
    return [
        f"1. Open your web browser and go to: {url}",
        "",
        "2. Complete the YouTrack Configuration Wizard (5-10 minutes):",
        "   - Step 1: Set up the administrator account",
        "   - Step 2: Configure basic YouTrack settings",
        "   - Step 3: Configure email notifications (optional)",
        "   - Step 4: Create your first project (recommended: 'FPU')",
        "   - Step 5: Review and confirm your settings",
        "",
        "3. After completing the wizard:",
        "   - YouTrack will restart and apply your configuration",
        "   - This may take 1-2 minutes",
        "   - Keep the browser tab open for reference",
        "",
        "4. Once YouTrack is ready, return here to configure the CLI",
        "",
        "Note: The initial setup process typically takes 5-10 minutes.",
        "Be patient as YouTrack configures itself for first use.",
    ]
