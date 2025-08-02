"""Administrative operations for YouTrack CLI."""

from typing import Any, Optional
from urllib.parse import quote

import httpx
from rich.table import Table
from rich.text import Text

from .auth import AuthManager
from .client import get_client_manager
from .console import get_console
from .custom_field_manager import CustomFieldManager

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

        # Mapping of user-friendly setting names to their category and field names
        self.setting_mappings = {
            "Max Export Items": {"category": "systemSettings", "field": "maxExportItems", "type": "int"},
            "Max Upload File Size": {"category": "systemSettings", "field": "maxUploadFileSize", "type": "int"},
            "Allow Statistics Collection": {
                "category": "systemSettings",
                "field": "allowStatisticsCollection",
                "type": "bool",
            },
            "Is Application Read Only": {
                "category": "systemSettings",
                "field": "isApplicationReadOnly",
                "type": "bool",
            },
            "Base Url": {"category": "systemSettings", "field": "baseUrl", "type": "str"},
            "Application Name": {"category": "appearanceSettings", "field": "applicationName", "type": "str"},
            "Title": {"category": "appearanceSettings", "field": "title", "type": "str"},
        }

    def _convert_setting_value(self, value: str, target_type: str) -> Any:
        """Convert a string value to the appropriate type for YouTrack API.

        Args:
            value: String value to convert
            target_type: Target type ('int', 'bool', 'str')

        Returns:
            Converted value in the appropriate type
        """
        if target_type == "int":
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to integer") from None
        elif target_type == "bool":
            if value.lower() in ("true", "1", "yes", "on", "enabled"):
                return True
            if value.lower() in ("false", "0", "no", "off", "disabled"):
                return False
            raise ValueError(f"Cannot convert '{value}' to boolean. Use true/false, yes/no, or 1/0")
        else:  # str
            return value

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
            # Check if the setting_key is a user-friendly name that needs mapping
            if setting_key in self.setting_mappings:
                mapping = self.setting_mappings[setting_key]
                category = mapping["category"]
                field_name = mapping["field"]

                # Fetch the entire category and extract the specific field
                encoded_category = quote(category, safe="")
                endpoint = f"/api/admin/globalSettings/{encoded_category}"
            else:
                # Direct category request - add fields parameter for meaningful data
                # URL-encode the setting key to handle spaces and special characters
                encoded_setting_key = quote(setting_key, safe="")
                endpoint = f"/api/admin/globalSettings/{encoded_setting_key}"
                category = setting_key
                field_name = None

            # Add appropriate fields based on the setting category
            if category == "systemSettings":
                endpoint += (
                    "?fields=baseUrl,isApplicationReadOnly,maxUploadFileSize,"
                    "maxExportItems,allowStatisticsCollection,restApiUrl,maxIssuesInSinglePageExport"
                )
            elif category == "license":
                endpoint += "?fields=username,organizations,license,expirationDate"
            elif category == "appearanceSettings":
                endpoint += "?fields=logo(url),applicationName,title"
            elif category == "notificationSettings":
                endpoint += "?fields=jabberSettings,emailSettings,mailProtocol"

            try:
                response = await client_manager.make_request(
                    "GET",
                    f"{credentials.base_url.rstrip('/')}{endpoint}",
                    headers=headers,
                    timeout=10.0,
                )
                settings = response.json()

                # If we're looking for a specific field within a category, extract it
                if field_name:
                    if field_name in settings:
                        # Return in legacy single setting format for compatibility with display logic
                        field_value = settings[field_name]
                        return {
                            "status": "success",
                            "data": {
                                "name": setting_key,
                                "value": field_value,
                                "description": f"Field '{field_name}' from {category} category",
                            },
                        }
                    return {"status": "error", "message": f"Field '{field_name}' not found in {category} settings."}
                # Return single category in the nested format for consistency
                return {"status": "success", "data": {setting_key: settings}}
            except httpx.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 403:
                        return {
                            "status": "error",
                            "message": "Insufficient permissions for global settings.",
                        }
                    if e.response.status_code == 404:
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
            if permission_errors == total_endpoints:
                return {
                    "status": "error",
                    "message": "Insufficient permissions for global settings.",
                }
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
            # Check if the setting_key is a user-friendly name that needs mapping
            if setting_key in self.setting_mappings:
                mapping = self.setting_mappings[setting_key]
                category = mapping["category"]
                field_name = mapping["field"]
                field_type = mapping["type"]

                # Convert value to the appropriate type
                try:
                    converted_value = self._convert_setting_value(value, field_type)
                except ValueError as e:
                    return {"status": "error", "message": f"Invalid value for '{setting_key}': {str(e)}"}

                # For setting individual fields, we need to use the field name directly
                # Some YouTrack APIs may accept direct field updates within categories
                encoded_category = quote(category, safe="")
                endpoint = f"{credentials.base_url.rstrip('/')}/api/admin/globalSettings/{encoded_category}"

                # Try to update the specific field within the category
                field_data = {field_name: converted_value}
                await client_manager.make_request(
                    "POST",
                    endpoint,
                    headers=headers,
                    json_data=field_data,
                    timeout=10.0,
                )
            else:
                # Direct category/setting update
                # URL-encode the setting key to handle spaces and special characters
                encoded_setting_key = quote(setting_key, safe="")
                await client_manager.make_request(
                    "POST",
                    f"{credentials.base_url.rstrip('/')}/api/admin/globalSettings/{encoded_setting_key}",
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
                if e.response.status_code == 400:
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
                if e.response.status_code == 404:
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
                if e.response.status_code == 403:
                    return {
                        "status": "error",
                        "message": "Insufficient permissions for health check. "
                        "Requires 'Low-level Admin Read' permission.",
                    }
                if e.response.status_code == 401:
                    return {
                        "status": "error",
                        "message": "Authentication failed. Your token may have expired. Run 'yt auth login' again.",
                    }
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
        return {
            "status": "error",
            "message": (
                "Cache clearing is not available through the YouTrack REST API.\n"
                "This functionality may be available through:\n"
                "- The YouTrack administrative UI\n"
                "- Server restart procedures\n"
                "- Direct server access\n\n"
                "Please consult your YouTrack administrator or the JetBrains support team for alternative methods."
            ),
        }

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
                f"{credentials.base_url.rstrip('/')}/hub/api/rest/usergroups",
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
                if e.response.status_code == 400:
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

    # Locale Management
    async def get_locale_settings(self) -> dict[str, Any]:
        """Get current locale settings.

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
                f"{credentials.base_url.rstrip('/')}/api/admin/globalSettings/localeSettings",
                headers=headers,
                params={"fields": "locale(id,name,language,locale,community),isRTL"},
                timeout=10.0,
            )

            locale_settings = response.json()
            return {"status": "success", "data": locale_settings}

        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 403:
                    return {
                        "status": "error",
                        "message": "Insufficient permissions to view locale settings.",
                    }
                if e.response.status_code == 404:
                    return {
                        "status": "error",
                        "message": "Locale settings endpoint not found.",
                    }
            return {"status": "error", "message": f"HTTP error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}

    async def set_locale_settings(self, locale_id: str) -> dict[str, Any]:
        """Set locale settings.

        Args:
            locale_id: Locale ID to set (e.g., 'en_US', 'de_DE')

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

        locale_data = {"locale": {"id": locale_id}}

        client_manager = get_client_manager()
        try:
            await client_manager.make_request(
                "POST",
                f"{credentials.base_url.rstrip('/')}/api/admin/globalSettings/localeSettings",
                headers=headers,
                json_data=locale_data,
                timeout=10.0,
            )

            return {
                "status": "success",
                "message": f"Locale updated to '{locale_id}' successfully",
            }

        except httpx.HTTPError as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 403:
                    return {
                        "status": "error",
                        "message": "Insufficient permissions to modify locale settings.",
                    }
                if e.response.status_code == 400:
                    return {
                        "status": "error",
                        "message": f"Invalid locale ID: '{locale_id}'",
                    }
            return {"status": "error", "message": f"HTTP error: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"Unexpected error: {e}"}

    async def get_available_locales(self) -> dict[str, Any]:
        """Get list of available locales.

        Note: This method tries to get locale options from the general system settings
        as YouTrack may not have a dedicated endpoint for available locales.

        Returns:
            Dictionary with operation result
        """
        # For now, return common locales as YouTrack may not have a dedicated endpoint
        # This is a fallback implementation
        common_locales = [
            {"id": "en_US", "name": "English (US)", "locale": "en_US", "language": "en", "community": False},
            {"id": "de_DE", "name": "German (Germany)", "locale": "de_DE", "language": "de", "community": False},
            {"id": "fr_FR", "name": "French (France)", "locale": "fr_FR", "language": "fr", "community": False},
            {"id": "es_ES", "name": "Spanish (Spain)", "locale": "es_ES", "language": "es", "community": False},
            {"id": "ja_JP", "name": "Japanese (Japan)", "locale": "ja_JP", "language": "ja", "community": False},
            {"id": "zh_CN", "name": "Chinese (Simplified)", "locale": "zh_CN", "language": "zh", "community": False},
            {"id": "ru_RU", "name": "Russian (Russia)", "locale": "ru_RU", "language": "ru", "community": False},
        ]

        return {
            "status": "success",
            "data": common_locales,
            "message": (
                "Note: This is a list of common locales. "
                "Actual available locales may vary based on your YouTrack installation."
            ),
        }

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
        return any(key in known_categories for key in settings)

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
        """Format setting value for display using CustomFieldManager."""
        if isinstance(value, bool):
            return "✓" if value else "✗"
        if isinstance(value, dict):
            # For nested objects, show a summary or key fields
            if "$type" in value:
                field_type = value["$type"]
                display_name = CustomFieldManager.format_field_type_for_display(field_type)
                return f"[{display_name}]"
            return str(value)
        if isinstance(value, (int, float)):
            return str(value)
        if value is None:
            return "N/A"
        return str(value)

    def display_license_info(self, license_info: dict[str, Any]) -> None:
        """Display license information.

        Args:
            license_info: License information dictionary
        """
        table = Table(title="License Information")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="blue")

        # Display username (maps to "Licensed To")
        username = license_info.get("username", "N/A")
        table.add_row("Licensed To", username)

        # Display license key (truncated for security)
        license_key = license_info.get("license", "N/A")
        if license_key != "N/A" and len(license_key) > 20:
            # Show only first 20 characters for security
            license_display = f"{license_key[:20]}..."
        else:
            license_display = license_key
        table.add_row("License Key", license_display)

        # Display error status if present or determine status
        error = license_info.get("error")
        if error:
            error_text = Text(error, style="red")
            table.add_row("Error", error_text)
            status_text = Text("Error", style="red")
        else:
            # If no error and license key exists, assume active
            is_active = license_key != "N/A" and license_key is not None
            status_color = "green" if is_active else "red"
            status_value = "Active" if is_active else "No License"
            status_text = Text(status_value, style=status_color)

        table.add_row("Status", status_text)

        self.console.print(table)

    def display_license_usage(self, license_data: dict[str, Any]) -> None:
        """Display license usage information.

        Args:
            license_data: License usage data dictionary
        """
        table = Table(title="License Usage")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="blue")

        # License ID
        license_id = license_data.get("id", "N/A")
        table.add_row("License ID", license_id)

        # Username
        username = license_data.get("username", "N/A")
        table.add_row("Username", username)

        # License Key
        license_key = license_data.get("license", "N/A")
        table.add_row("License Key", license_key)

        # Status - check for error or assume valid
        if license_data.get("error"):
            error_text = Text(license_data["error"], style="red")
            table.add_row("Error", error_text)
            status_text = Text("Error", style="red")
        else:
            status_text = Text("Valid", style="green")

        table.add_row("Status", status_text)

        self.console.print(table)

    def display_system_health(self, health_info: dict[str, Any]) -> None:
        """Display system health information.

        Args:
            health_info: Health information dictionary
        """
        table = Table(title="System Health")
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="blue")

        # Base URL
        base_url = health_info.get("baseUrl", "N/A")
        table.add_row("Base URL", base_url)

        # Application mode (read-only status)
        is_read_only = health_info.get("isApplicationReadOnly", False)
        read_only_color = "red" if is_read_only else "green"
        read_only_text = "Read-Only" if is_read_only else "Read-Write"
        mode_text = Text(read_only_text, style=read_only_color)
        table.add_row("Application Mode", mode_text)

        # File upload settings
        max_upload_size = health_info.get("maxUploadFileSize", "N/A")
        if max_upload_size != "N/A":
            # Convert bytes to MB for readability
            max_upload_mb = max_upload_size / (1024 * 1024)
            upload_text = f"{max_upload_mb:.1f} MB"
        else:
            upload_text = str(max_upload_size)
        table.add_row("Max Upload Size", upload_text)

        # Export settings
        max_export_items = health_info.get("maxExportItems", "N/A")
        table.add_row("Max Export Items", str(max_export_items))

        # Statistics collection status
        stats_collection = health_info.get("allowStatisticsCollection", False)
        stats_color = "green" if stats_collection else "yellow"
        stats_text = "Enabled" if stats_collection else "Disabled"
        stats_text_styled = Text(stats_text, style=stats_color)
        table.add_row("Statistics Collection", stats_text_styled)

        # Overall system status
        overall_status = "Healthy" if not is_read_only else "Read-Only Mode"
        status_color = "green" if not is_read_only else "yellow"
        status_text_styled = Text(overall_status, style=status_color)
        table.add_row("Overall Status", status_text_styled)

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

    def display_locale_settings(self, locale_settings: dict[str, Any]) -> None:
        """Display locale settings in a formatted table.

        Args:
            locale_settings: Locale settings dictionary
        """
        table = Table(title="Locale Settings")
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        locale = locale_settings.get("locale", {})
        is_rtl = locale_settings.get("isRTL", False)

        # Add locale information rows
        table.add_row("Language", locale.get("name", "N/A"))
        table.add_row("Locale ID", locale.get("id", "N/A"))
        table.add_row("Language Code", locale.get("language", "N/A"))
        table.add_row("Full Locale", locale.get("locale", "N/A"))

        # Display community status with color
        is_community = locale.get("community", False)
        community_text = "Yes" if is_community else "No"
        community_color = "yellow" if is_community else "green"
        community_styled = Text(community_text, style=community_color)
        table.add_row("Community Language", community_styled)

        # Display RTL status with color
        rtl_text = "Yes" if is_rtl else "No"
        rtl_color = "blue" if is_rtl else "green"
        rtl_styled = Text(rtl_text, style=rtl_color)
        table.add_row("Right-to-Left", rtl_styled)

        self.console.print(table)

    def display_available_locales(self, locales: list[dict[str, Any]], message: Optional[str] = None) -> None:
        """Display available locales in a formatted table.

        Args:
            locales: List of locale dictionaries
            message: Optional message to display
        """
        if message:
            self.console.print(f"[yellow]{message}[/yellow]\n")

        if not locales:
            self.console.print("No locales found.", style="yellow")
            return

        table = Table(title="Available Locales")
        table.add_column("Locale ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="blue")
        table.add_column("Language", style="green")
        table.add_column("Community", style="magenta")

        for locale in locales:
            locale_id = locale.get("id", "N/A")
            name = locale.get("name", "N/A")
            language = locale.get("language", "N/A")
            is_community = "Yes" if locale.get("community", False) else "No"

            table.add_row(locale_id, name, language, is_community)

        self.console.print(table)
