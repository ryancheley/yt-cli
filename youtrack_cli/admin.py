"""Administrative operations for YouTrack CLI."""

from typing import Any, Optional

import httpx
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .auth import AuthManager


class AdminManager:
    """Manages YouTrack administrative operations."""

    def __init__(self, auth_manager: AuthManager):
        """Initialize the admin manager.

        Args:
            auth_manager: AuthManager instance for authentication
        """
        self.auth_manager = auth_manager
        self.console = Console()

    # Global Settings Management
    async def get_global_settings(
        self, setting_key: Optional[str] = None
    ) -> dict[str, Any]:
        """Get global YouTrack settings.

        Args:
            setting_key: Specific setting key to retrieve

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        endpoint = "/api/admin/globalSettings"
        if setting_key:
            endpoint += f"/{setting_key}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{credentials.base_url.rstrip('/')}{endpoint}",
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()

                settings = response.json()
                return {"status": "success", "data": settings}

            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "Insufficient permissions for global settings.",
                        }
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

    async def set_global_setting(self, setting_key: str, value: str) -> dict[str, Any]:
        """Set a global YouTrack setting.

        Args:
            setting_key: Setting key to update
            value: New value for the setting

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        setting_data = {"value": value}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{credentials.base_url.rstrip('/')}/api/admin/globalSettings/{setting_key}",
                    headers=headers,
                    json=setting_data,
                    timeout=10.0,
                )
                response.raise_for_status()

                return {
                    "status": "success",
                    "message": f"Setting '{setting_key}' updated successfully",
                }

            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "Insufficient permissions to modify settings.",
                        }
                    elif e.response.status_code == 400:
                        return {
                            "status": "error",
                            "message": "Invalid setting key or value.",
                        }
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

    # License Management
    async def get_license_info(self) -> dict[str, Any]:
        """Get YouTrack license information.

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{credentials.base_url.rstrip('/')}/api/admin/license",
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()

                license_info = response.json()
                return {"status": "success", "data": license_info}

            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "Insufficient permissions to view license.",
                        }
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

    async def get_license_usage(self) -> dict[str, Any]:
        """Get license usage statistics.

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{credentials.base_url.rstrip('/')}/api/admin/license/usage",
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()

                usage_info = response.json()
                return {"status": "success", "data": usage_info}

            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "Insufficient permissions to view usage.",
                        }
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

    # System Health and Maintenance
    async def get_system_health(self) -> dict[str, Any]:
        """Get system health status.

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{credentials.base_url.rstrip('/')}/api/admin/health",
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()

                health_info = response.json()
                return {"status": "success", "data": health_info}

            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "Insufficient permissions for health check.",
                        }
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

    async def clear_caches(self) -> dict[str, Any]:
        """Clear system caches.

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{credentials.base_url.rstrip('/')}/api/admin/maintenance/clearCache",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()

                return {
                    "status": "success",
                    "message": "System caches cleared successfully",
                }

            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "Insufficient permissions for maintenance.",
                        }
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

    # User Groups Management
    async def list_user_groups(self, fields: Optional[str] = None) -> dict[str, Any]:
        """List all user groups.

        Args:
            fields: Comma-separated list of fields to return

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        if not fields:
            fields = "id,name,description,users(login,fullName)"

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        params = {"fields": fields}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{credentials.base_url.rstrip('/')}/api/admin/groups",
                    headers=headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()

                groups = response.json()
                return {"status": "success", "data": groups}

            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "Insufficient permissions to view groups.",
                        }
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

    async def create_user_group(
        self, name: str, description: Optional[str] = None
    ) -> dict[str, Any]:
        """Create a new user group.

        Args:
            name: Group name
            description: Group description

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        group_data = {"name": name}
        if description:
            group_data["description"] = description

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{credentials.base_url.rstrip('/')}/api/admin/groups",
                    headers=headers,
                    json=group_data,
                    params={"fields": "id,name,description"},
                    timeout=10.0,
                )
                response.raise_for_status()

                created_group = response.json()
                return {
                    "status": "success",
                    "data": created_group,
                    "message": f"Group '{name}' created successfully",
                }

            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "Insufficient permissions to create groups.",
                        }
                    elif e.response.status_code == 400:
                        return {
                            "status": "error",
                            "message": "Invalid group data or group already exists.",
                        }
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

    # Custom Fields Management
    async def list_custom_fields(self, fields: Optional[str] = None) -> dict[str, Any]:
        """List all custom fields.

        Args:
            fields: Comma-separated list of fields to return

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        if not fields:
            fields = "id,name,fieldType,isPrivate,hasStateMachine"

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        params = {"fields": fields}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{credentials.base_url.rstrip('/')}/api/admin/customFieldSettings/customFields",
                    headers=headers,
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()

                fields_data = response.json()
                return {"status": "success", "data": fields_data}

            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "Insufficient permissions to view fields.",
                        }
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

    # Display Methods
    def display_global_settings(self, settings: dict[str, Any]) -> None:
        """Display global settings in a formatted table.

        Args:
            settings: Settings dictionary
        """
        if isinstance(settings, list):
            # Multiple settings
            table = Table(title="Global Settings")
            table.add_column("Setting", style="cyan", no_wrap=True)
            table.add_column("Value", style="green")
            table.add_column("Description", style="dim")

            for setting in settings:
                table.add_row(
                    setting.get("name", "N/A"),
                    str(setting.get("value", "N/A")),
                    setting.get("description", ""),
                )

            self.console.print(table)
        else:
            # Single setting
            self.console.print(f"[cyan]Setting:[/cyan] {settings.get('name', 'N/A')}")
            self.console.print(f"[cyan]Value:[/cyan] {settings.get('value', 'N/A')}")
            if settings.get("description"):
                self.console.print(
                    f"[cyan]Description:[/cyan] {settings['description']}"
                )

    def display_license_info(self, license_info: dict[str, Any]) -> None:
        """Display license information.

        Args:
            license_info: License information dictionary
        """
        self.console.print("\n[bold blue]License Information[/bold blue]")
        self.console.print(
            f"[cyan]License Type:[/cyan] {license_info.get('type', 'N/A')}"
        )
        self.console.print(
            f"[cyan]Licensed To:[/cyan] {license_info.get('licensedTo', 'N/A')}"
        )

        if license_info.get("expirationDate"):
            self.console.print(
                f"[cyan]Expires:[/cyan] {license_info['expirationDate']}"
            )

        if license_info.get("maxUsers"):
            self.console.print(f"[cyan]Max Users:[/cyan] {license_info['maxUsers']}")

        # Display active status
        is_active = license_info.get("isActive", False)
        status_color = "green" if is_active else "red"
        status_text = "Active" if is_active else "Inactive"
        self.console.print(
            f"[cyan]Status:[/cyan] [{status_color}]{status_text}[/{status_color}]"
        )

    def display_system_health(self, health_info: dict[str, Any]) -> None:
        """Display system health information.

        Args:
            health_info: Health information dictionary
        """
        self.console.print("\n[bold blue]System Health[/bold blue]")

        # Overall status
        overall_status = health_info.get("status", "unknown")
        status_color = "green" if overall_status == "healthy" else "red"
        self.console.print(
            f"[cyan]Overall Status:[/cyan] "
            f"[{status_color}]{overall_status.title()}[/{status_color}]"
        )

        # Individual checks
        checks = health_info.get("checks", [])
        if checks:
            table = Table(title="Health Checks")
            table.add_column("Check", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Message", style="dim")

            for check in checks:
                status = check.get("status", "unknown")
                color = "green" if status == "healthy" else "red"
                table.add_row(
                    check.get("name", "Unknown"),
                    Text(status.title(), style=color),
                    check.get("message", ""),
                )

            self.console.print(table)

    def display_user_groups(self, groups: list[dict[str, Any]]) -> None:
        """Display user groups in a formatted table.

        Args:
            groups: List of group dictionaries
        """
        if not groups:
            self.console.print("No user groups found.", style="yellow")
            return

        table = Table(title="User Groups")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description", style="blue")
        table.add_column("Members", style="green")

        for group in groups:
            name = group.get("name", "N/A")
            description = group.get("description", "")
            users = group.get("users", [])
            member_count = len(users) if users else 0

            table.add_row(name, description, str(member_count))

        self.console.print(table)

    def display_custom_fields(self, fields: list[dict[str, Any]]) -> None:
        """Display custom fields in a formatted table.

        Args:
            fields: List of field dictionaries
        """
        if not fields:
            self.console.print("No custom fields found.", style="yellow")
            return

        table = Table(title="Custom Fields")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Type", style="blue")
        table.add_column("Private", style="magenta")
        table.add_column("State Machine", style="green")

        for field in fields:
            name = field.get("name", "N/A")
            field_type = field.get("fieldType", {}).get("presentation", "N/A")
            is_private = "Yes" if field.get("isPrivate", False) else "No"
            has_state_machine = "Yes" if field.get("hasStateMachine", False) else "No"

            table.add_row(name, field_type, is_private, has_state_machine)

        self.console.print(table)
