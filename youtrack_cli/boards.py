"""Board management for YouTrack CLI."""

from typing import Any, Optional

import httpx
from rich.console import Console
from rich.table import Table

from .auth import AuthManager


class BoardManager:
    """Manages YouTrack agile boards operations."""

    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.console = Console()

    def _parse_json_response(self, response: httpx.Response) -> Any:
        """Safely parse JSON response, handling empty or non-JSON responses."""
        try:
            content_type = response.headers.get("content-type", "")
            if not response.text:
                raise ValueError("Empty response body")

            if "application/json" not in content_type:
                raise ValueError(f"Response is not JSON. Content-Type: {content_type}")

            return response.json()
        except Exception as e:
            # Try to provide more context about the error
            status_code = response.status_code
            preview = response.text[:200] if response.text else "empty"
            raise ValueError(
                f"Failed to parse JSON response (status {status_code}): {str(e)}. "
                f"Response preview: {preview}"
            ) from e

    async def list_boards(self, project_id: Optional[str] = None) -> dict[str, Any]:
        """List all agile boards."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url}/api/agiles"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        params = {}
        if project_id:
            params["project"] = project_id

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                boards = self._parse_json_response(response)

                # Display boards in a table
                table = Table(title="Agile Boards")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="magenta")
                table.add_column("Project", style="green")
                table.add_column("Owner", style="yellow")

                for board in boards:
                    table.add_row(
                        board.get("id", ""),
                        board.get("name", ""),
                        (
                            board.get("projects", [{}])[0].get("name", "N/A")
                            if board.get("projects")
                            else "N/A"
                        ),
                        board.get("owner", {}).get("name", "N/A"),
                    )

                self.console.print(table)
                return {"status": "success", "boards": boards}

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            self.console.print(f"❌ Error listing boards: {error_msg}", style="red")
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = str(e)
            self.console.print(f"❌ Error listing boards: {error_msg}", style="red")
            return {"status": "error", "message": error_msg}

    async def view_board(self, board_id: str) -> dict[str, Any]:
        """View details of a specific agile board."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        url = f"{credentials.base_url}/api/agiles/{board_id}"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                board = self._parse_json_response(response)

                # Display board details
                self.console.print(
                    f"[bold cyan]Board: {board.get('name', 'N/A')}[/bold cyan]"
                )
                self.console.print(f"ID: {board.get('id', 'N/A')}")
                self.console.print(
                    f"Owner: {board.get('owner', {}).get('name', 'N/A')}"
                )

                if board.get("projects"):
                    projects = ", ".join([p.get("name", "") for p in board["projects"]])
                    self.console.print(f"Projects: {projects}")

                if board.get("columns"):
                    self.console.print("\n[bold]Columns:[/bold]")
                    for i, column in enumerate(board["columns"], 1):
                        self.console.print(f"  {i}. {column.get('name', 'N/A')}")

                if board.get("sprints"):
                    self.console.print(f"\nSprints: {len(board['sprints'])}")

                return {"status": "success", "board": board}

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            self.console.print(f"❌ Error viewing board: {error_msg}", style="red")
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = str(e)
            self.console.print(f"❌ Error viewing board: {error_msg}", style="red")
            return {"status": "error", "message": error_msg}

    async def update_board(
        self, board_id: str, name: Optional[str] = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Update an agile board configuration."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # Build update data
        update_data = {}
        if name:
            update_data["name"] = name

        # Add any additional fields from kwargs
        update_data.update(kwargs)

        if not update_data:
            return {"status": "error", "message": "No update fields provided"}

        url = f"{credentials.base_url}/api/agiles/{board_id}"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=update_data)
                response.raise_for_status()
                board = self._parse_json_response(response)

                self.console.print(
                    f"✅ Board '{board.get('name', board_id)}' updated successfully",
                    style="green",
                )
                return {"status": "success", "board": board}

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            self.console.print(f"❌ Error updating board: {error_msg}", style="red")
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = str(e)
            self.console.print(f"❌ Error updating board: {error_msg}", style="red")
            return {"status": "error", "message": error_msg}
