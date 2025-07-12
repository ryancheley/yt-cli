"""Administrative operations for YouTrack CLI."""

from typing import Any, Optional

import httpx
from rich.table import Table

from .auth import AuthManager
from .client import get_client_manager
from .console import get_console

__all__ = ["AdminManager"]


class AdminManager:
    """Manages YouTrack administrative operations."""

    def __init__(self, auth_manager: AuthManager):
        """Initialize the admin manager.

        Args:
            auth_manager: AuthManager instance for authentication
        """
        self.auth_manager = auth_manager
        self.console = get_console()

    # Global Settings Management
    async def get_global_settings(self, setting_key: Optional[str] = None) -> dict[str, Any]:
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

        client_manager = get_client_manager()

        if setting_key:
            # Single setting request - add fields parameter for meaningful data
            endpoint = f"/api/admin/globalSettings/{setting_key}"

            # Add appropriate fields based on the setting category
            if setting_key == "systemSettings":
                endpoint += (
                    "?fields=baseUrl,isApplicationReadOnly,maxUploadFileSize,"
                    "maxExportItems,allowStatisticsCollection,restApiUrl,maxIssuesInSinglePageExport"
                )
            elif setting_key == "license":
                endpoint += "?fields=username,organizations,license,expirationDate"
            elif setting_key == "appearanceSettings":
                endpoint += "?fields=logo(url),applicationName,title"
            elif setting_key == "notificationSettings":
                endpoint += "?fields=jabberSettings,emailSettings,mailProtocol"

            try:
                response = await client_manager.make_request(
                    "GET",
                    f"{credentials.base_url.rstrip('/')}{endpoint}",
                    headers=headers,
                    timeout=10.0,
                )
                settings = response.json()
                # Return single category in the nested format for consistency
                return {"status": "success", "data": {setting_key: settings}}
            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "Insufficient permissions for global settings.",
                        }
                    elif e.response.status_code == 404:
                        return {
                            "status": "error",
                            "message": f"Setting category '{setting_key}' not found.",
                        }
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                if "not found" in str(e):
                    return {
                        "status": "error",
                        "message": f"Setting category '{setting_key}' not found.",
                    }
                return {"status": "error", "message": f"Unexpected error: {e}"}
        else:
            # Comprehensive settings - try multiple known endpoints with fields
            endpoints_to_try = [
                (
                    "/api/admin/globalSettings/systemSettings?fields=baseUrl,isApplicationReadOnly,"
                    "maxUploadFileSize,maxExportItems,allowStatisticsCollection,restApiUrl,maxIssuesInSinglePageExport"
                ),
                "/api/admin/globalSettings/license?fields=username,organizations,license,expirationDate",
                "/api/admin/globalSettings/appearanceSettings?fields=logo(url),applicationName,title",
                "/api/admin/globalSettings/notificationSettings?fields=jabberSettings,emailSettings,mailProtocol",
            ]

            all_settings = {}
            permission_errors = 0
            total_endpoints = len(endpoints_to_try)

            for endpoint in endpoints_to_try:
                try:
                    response = await client_manager.make_request(
                        "GET",
                        f"{credentials.base_url.rstrip('/')}{endpoint}",
                        headers=headers,
                        timeout=10.0,
                    )
                    category_data = response.json()
                    category_name = endpoint.split("/")[-1].split("?")[0]  # Extract category name, remove query params
                    all_settings[category_name] = category_data
                except httpx.HTTPError as e:
                    if hasattr(e, "response") and e.response is not None and e.response.status_code == 403:
                        permission_errors += 1
                    # Continue trying other endpoints
                    continue

            if all_settings:
                return {"status": "success", "data": all_settings}
            elif permission_errors == total_endpoints:
                return {
                    "status": "error",
                    "message": "Insufficient permissions for global settings.",
                }
            else:
                return {"status": "error", "message": "No settings could be retrieved"}

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

        client_manager = get_client_manager()
        try:
            await client_manager.make_request(
                "POST",
                f"{credentials.base_url.rstrip('/')}/api/admin/globalSettings/{setting_key}",
                headers=headers,
                json_data=setting_data,
                timeout=10.0,
            )

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

        client_manager = get_client_manager()
        try:
            response = await client_manager.make_request(
                "GET",
                f"{credentials.base_url.rstrip('/')}/api/admin/globalSettings/license",
                headers=headers,
                params={"fields": "id,username,license,error"},
                timeout=10.0,
            )

            license_info = response.json()
            return {"status": "success", "data": license_info}

        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 403:
                    return {
                        "status": "error",
                        "message": "Insufficient permissions to view license.",
                    }
                elif e.response.status_code == 404:
                    return {
                        "status": "error",
                        "message": (
                            "License endpoint not found. This may indicate an "
                            "incompatible YouTrack version or configuration."
                        ),
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

        client_manager = get_client_manager()
        try:
            response = await client_manager.make_request(
                "GET",
                f"{credentials.base_url.rstrip('/')}/api/admin/globalSettings/license",
                headers=headers,
                params={"fields": "id,username,license,error"},
                timeout=10.0,
            )

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

        # List of endpoints to try, in order of preference
        endpoints = [
            "/api/admin/globalSettings/systemSettings?fields=baseUrl,isApplicationReadOnly,maxUploadFileSize,maxExportItems,allowStatisticsCollection",
            "/api/admin/globalSettings/systemSettings",
        ]

        client_manager = get_client_manager()
        for endpoint in endpoints:
            try:
                response = await client_manager.make_request(
                    "GET",
                    f"{credentials.base_url.rstrip('/')}{endpoint}",
                    headers=headers,
                    timeout=10.0,
                )

                health_info = response.json()
                return {"status": "success", "data": health_info}

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    continue  # Try next endpoint
                elif e.response.status_code == 403:
                    return {
                        "status": "error",
                        "message": "Insufficient permissions for health check. "
                        "Requires 'Low-level Admin Read' permission.",
                    }
                elif e.response.status_code == 401:
                    return {
                        "status": "error",
                        "message": "Authentication failed. Your token may have expired. Run 'yt auth login' again.",
                    }
                else:
                    response_text = e.response.text if hasattr(e.response, "text") else str(e)
                    return {
                        "status": "error",
                        "message": f"HTTP {e.response.status_code}: {response_text}",
                    }
            except httpx.RequestError as e:
                return {
                    "status": "error",
                    "message": f"Network error: {e}. Check your YouTrack URL and network connection.",
                }
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

        # If all endpoints failed with 404
        return {
            "status": "error",
            "message": "System health endpoint not found (404). This may indicate:\n"
            "1. Your YouTrack version doesn't support this endpoint\n"
            "2. The endpoint URL may have changed\n"
            "3. Your YouTrack instance has a different API configuration\n"
            "Please verify your YouTrack version and API access.",
        }

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

        client_manager = get_client_manager()
        try:
            await client_manager.make_request(
                "POST",
                f"{credentials.base_url.rstrip('/')}/api/admin/maintenance/clearCache",
                headers=headers,
                timeout=30.0,
            )

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

        client_manager = get_client_manager()
        try:
            response = await client_manager.make_request(
                "GET",
                f"{credentials.base_url.rstrip('/')}/hub/api/rest/usergroups",
                headers=headers,
                params=params,
                timeout=10.0,
            )

            groups_response = response.json()
            groups = groups_response.get("usergroups", [])
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

    async def create_user_group(self, name: str, description: Optional[str] = None) -> dict[str, Any]:
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

        client_manager = get_client_manager()
        try:
            response = await client_manager.make_request(
                "POST",
                f"{credentials.base_url.rstrip('/')}/api/rest/usergroups",
                headers=headers,
                json_data=group_data,
                params={"fields": "id,name,description"},
                timeout=10.0,
            )

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
            fields = "id,name,fieldType(presentation),isPrivate,hasStateMachine"

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        params = {"fields": fields}

        client_manager = get_client_manager()
        try:
            response = await client_manager.make_request(
                "GET",
                f"{credentials.base_url.rstrip('/')}/api/admin/customFieldSettings/customFields",
                headers=headers,
                params=params,
                timeout=10.0,
            )

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
            settings: Settings dictionary (can be nested by category or legacy format)
        """
        # Check if this is the new nested format (multiple categories)
        if self._is_nested_settings_format(settings):
            self._display_nested_global_settings(settings)
        elif isinstance(settings, list):
            # Legacy format: Multiple settings
            self._display_legacy_settings_list(settings)
        else:
            # Legacy format: Single setting
            self._display_legacy_single_setting(settings)

    def _is_nested_settings_format(self, settings: dict[str, Any]) -> bool:
        """Check if settings are in the new nested format with categories."""
        # The new format has category keys like 'systemSettings', 'license', etc.
        # and each category contains settings data
        if not isinstance(settings, dict):
            return False
        known_categories = {"systemSettings", "license", "appearanceSettings", "notificationSettings"}
        return any(key in known_categories for key in settings.keys())

    def _display_nested_global_settings(self, settings: dict[str, Any]) -> None:
        """Display nested global settings grouped by category."""
        table = Table(title="Global Settings")
        table.add_column("Category", style="bold magenta", no_wrap=True)
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        for category_name, category_data in settings.items():
            if isinstance(category_data, dict):
                # Skip metadata fields
                filtered_data = {k: v for k, v in category_data.items() if not k.startswith("$") and k != "id"}

                if filtered_data:
                    # Display category header for first setting in category
                    first_setting = True
                    for setting_key, setting_value in filtered_data.items():
                        category_display = self._format_category_name(category_name) if first_setting else ""
                        formatted_key = self._format_setting_key(setting_key)
                        formatted_value = self._format_setting_value(setting_value)

                        table.add_row(category_display, formatted_key, formatted_value)
                        first_setting = False

        self.console.print(table)

    def _display_legacy_settings_list(self, settings: list) -> None:
        """Display legacy format settings list."""
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

    def _display_legacy_single_setting(self, settings: dict[str, Any]) -> None:
        """Display legacy format single setting."""
        self.console.print(f"[cyan]Setting:[/cyan] {settings.get('name', 'N/A')}")
        self.console.print(f"[cyan]Value:[/cyan] {settings.get('value', 'N/A')}")
        if settings.get("description"):
            self.console.print(f"[cyan]Description:[/cyan] {settings['description']}")

    def _format_category_name(self, category_name: str) -> str:
        """Format category name for display."""
        # Convert camelCase to Title Case
        import re

        formatted = re.sub(r"([A-Z])", r" \1", category_name).strip()
        return formatted.title()

    def _format_setting_key(self, key: str) -> str:
        """Format setting key for display."""
        # Convert camelCase to readable format
        import re

        formatted = re.sub(r"([A-Z])", r" \1", key).strip()
        return formatted.title()

    def _format_setting_value(self, value: Any) -> str:
        """Format setting value for display."""
        if isinstance(value, bool):
            return "✓" if value else "✗"
        elif isinstance(value, dict):
            # For nested objects, show a summary or key fields
            if "$type" in value:
                return f"[{value['$type']}]"
            else:
                return str(value)
        elif isinstance(value, (int, float)):
            return str(value)
        elif value is None:
            return "N/A"
        else:
            return str(value)

    def display_license_info(self, license_info: dict[str, Any]) -> None:
        """Display license information.

        Args:
            license_info: License information dictionary
        """
        self.console.print("\n[bold blue]License Information[/bold blue]")

        # Display username (maps to "Licensed To")
        username = license_info.get("username", "N/A")
        self.console.print(f"[cyan]Licensed To:[/cyan] {username}")

        # Display license key (truncated for security)
        license_key = license_info.get("license", "N/A")
        if license_key != "N/A" and len(license_key) > 20:
            # Show only first 20 characters for security
            license_display = f"{license_key[:20]}..."
        else:
            license_display = license_key
        self.console.print(f"[cyan]License Key:[/cyan] {license_display}")

        # Display error status if present
        error = license_info.get("error")
        if error:
            self.console.print(f"[cyan]Error:[/cyan] [red]{error}[/red]")
            status_color = "red"
            status_text = "Error"
        else:
            # If no error and license key exists, assume active
            is_active = license_key != "N/A" and license_key is not None
            status_color = "green" if is_active else "red"
            status_text = "Active" if is_active else "No License"

        self.console.print(f"[cyan]Status:[/cyan] [{status_color}]{status_text}[/{status_color}]")

    def display_system_health(self, health_info: dict[str, Any]) -> None:
        """Display system health information.

        Args:
            health_info: Health information dictionary
        """
        self.console.print("\n[bold blue]System Settings[/bold blue]")

        # Display system settings information
        base_url = health_info.get("baseUrl", "N/A")
        self.console.print(f"[cyan]Base URL:[/cyan] {base_url}")

        # Display read-only status
        is_read_only = health_info.get("isApplicationReadOnly", False)
        read_only_color = "red" if is_read_only else "green"
        read_only_text = "Read-Only" if is_read_only else "Read-Write"
        self.console.print(f"[cyan]Application Mode:[/cyan] [{read_only_color}]{read_only_text}[/{read_only_color}]")

        # Display file upload settings
        max_upload_size = health_info.get("maxUploadFileSize", "N/A")
        if max_upload_size != "N/A":
            # Convert bytes to MB for readability
            max_upload_mb = max_upload_size / (1024 * 1024)
            self.console.print(f"[cyan]Max Upload Size:[/cyan] {max_upload_mb:.1f} MB")
        else:
            self.console.print(f"[cyan]Max Upload Size:[/cyan] {max_upload_size}")

        # Display export settings
        max_export_items = health_info.get("maxExportItems", "N/A")
        self.console.print(f"[cyan]Max Export Items:[/cyan] {max_export_items}")

        # Display statistics collection status
        stats_collection = health_info.get("allowStatisticsCollection", False)
        stats_color = "green" if stats_collection else "yellow"
        stats_text = "Enabled" if stats_collection else "Disabled"
        self.console.print(f"[cyan]Statistics Collection:[/cyan] [{stats_color}]{stats_text}[/{stats_color}]")

        # Overall system status based on read-only mode
        overall_status = "Healthy" if not is_read_only else "Read-Only Mode"
        status_color = "green" if not is_read_only else "yellow"
        self.console.print(f"[cyan]Overall Status:[/cyan] [{status_color}]{overall_status}[/{status_color}]")

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
