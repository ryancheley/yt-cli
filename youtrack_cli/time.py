"""Time tracking management for YouTrack CLI."""

from datetime import datetime, timedelta
from typing import Any, Optional

from rich.table import Table

from .auth import AuthManager
from .client import get_client_manager
from .console import get_console

__all__ = ["TimeManager"]


class TimeManager:
    """Manages YouTrack time tracking operations."""

    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.console = get_console()

    def _parse_json_response(self, response) -> Any:
        """Safely parse JSON response, handling empty or non-JSON responses."""
        try:
            if not response.text.strip():
                raise ValueError("Empty response body")

            return response.json()
        except ValueError as e:
            if "Expecting value" in str(e):
                # This is the specific error from the issue
                raise ValueError(
                    "Received empty response. This may indicate no time entries exist "
                    "or time tracking is not enabled for your account."
                ) from e
            raise ValueError(f"Failed to parse JSON response: {str(e)}") from e
        except Exception as e:
            raise ValueError(f"Unexpected error parsing response: {str(e)}") from e

    async def log_time(
        self,
        issue_id: str,
        duration: str,
        date: Optional[str] = None,
        description: Optional[str] = None,
        work_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """Log work time to an issue."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # Parse duration (e.g., "2h 30m", "1.5h", "90m")
        duration_minutes = self._parse_duration(duration)
        if duration_minutes is None:
            return {"status": "error", "message": "Invalid duration format"}

        # Parse date or use current date
        work_date = self._parse_date(date) if date else datetime.now().isoformat()

        work_item_data = {
            "duration": {"minutes": duration_minutes},
            "date": work_date,
        }

        if description:
            work_item_data["description"] = description
        if work_type:
            work_item_data["type"] = {"name": work_type}

        url = f"{credentials.base_url}/api/issues/{issue_id}/timeTracking/workItems"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(
                method="POST", url=url, json_data=work_item_data, headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "message": f"Logged {duration} to issue {issue_id}",
                    "data": data,
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to log time: {error_text}",
                }
        except Exception as e:
            return {"status": "error", "message": f"Error logging time: {str(e)}"}

    async def get_time_entries(
        self,
        issue_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get time entries with optional filtering."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        params = {}
        if fields:
            params["fields"] = fields
        if user_id:
            params["author"] = user_id
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        if issue_id:
            # Get time entries for a specific issue
            url = f"{credentials.base_url}/api/issues/{issue_id}/timeTracking/workItems"
        else:
            # Get all time entries
            url = f"{credentials.base_url}/api/workItems"

        headers = {"Authorization": f"Bearer {credentials.token}"}

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(method="GET", url=url, params=params, headers=headers)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                return {
                    "status": "success",
                    "data": data,
                    "count": len(data) if isinstance(data, list) else 1,
                }
            else:
                error_text = response.text
                return {
                    "status": "error",
                    "message": f"Failed to get time entries: {error_text}",
                }
        except ValueError as e:
            # Handle JSON parsing errors specifically
            return {
                "status": "error",
                "message": f"Response parsing error: {str(e)}",
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error getting time entries: {str(e)}",
            }

    async def get_time_summary(
        self,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        group_by: str = "user",
    ) -> dict[str, Any]:
        """Get time tracking summary with aggregation."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # First get all time entries
        time_entries_result = await self.get_time_entries(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            fields="id,duration,date,description,author(id,fullName),issue(id,summary),type(name)",
        )

        if time_entries_result["status"] != "success":
            return time_entries_result

        time_entries = time_entries_result["data"]
        if not isinstance(time_entries, list):
            time_entries = [time_entries]

        # Aggregate data
        summary = self._aggregate_time_data(time_entries, group_by)

        return {
            "status": "success",
            "data": summary,
            "total_entries": len(time_entries),
        }

    def _parse_duration(self, duration: str) -> Optional[int]:
        """Parse duration string to minutes."""
        duration = duration.lower().strip()

        # Handle formats like "2h 30m", "1.5h", "90m", "1h", "30m"
        total_minutes = 0

        # Extract hours
        if "h" in duration:
            parts = duration.split("h")
            try:
                hours = float(parts[0].strip())
                total_minutes += int(hours * 60)
                duration = parts[1].strip() if len(parts) > 1 else ""
            except ValueError:
                return None

        # Extract minutes
        if "m" in duration:
            parts = duration.split("m")
            try:
                minutes = int(parts[0].strip())
                total_minutes += minutes
            except ValueError:
                return None
        elif duration and not duration.isspace():
            # If there's remaining text without 'm', assume it's minutes
            try:
                minutes = int(duration)
                total_minutes += minutes
            except ValueError:
                return None

        return total_minutes if total_minutes > 0 else None

    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format."""
        try:
            # Try different date formats
            formats = ["%Y-%m-%d", "%m/%d/%Y", "%d.%m.%Y", "%Y-%m-%d %H:%M:%S"]

            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.isoformat()
                except ValueError:
                    continue

            # If no format matches, try relative dates
            if date_str.lower() == "today":
                return datetime.now().isoformat()
            elif date_str.lower() == "yesterday":
                return (datetime.now() - timedelta(days=1)).isoformat()

            return date_str
        except Exception:
            return date_str

    def _aggregate_time_data(self, time_entries: list[dict[str, Any]], group_by: str) -> dict[str, Any]:
        """Aggregate time data by specified grouping."""
        summary = {}
        total_minutes = 0

        for entry in time_entries:
            duration = entry.get("duration", {})
            minutes = duration.get("minutes", 0) if isinstance(duration, dict) else 0
            total_minutes += minutes

            # Group by user, issue, or type
            if group_by == "user":
                key = entry.get("author", {}).get("fullName", "Unknown")
            elif group_by == "issue":
                issue = entry.get("issue", {})
                key = f"{issue.get('id', 'Unknown')} - {issue.get('summary', 'No summary')}"
            elif group_by == "type":
                key = entry.get("type", {}).get("name", "No type")
            else:
                key = "All"

            if key not in summary:
                summary[key] = {"minutes": 0, "entries": 0, "hours": 0.0}

            summary[key]["minutes"] += minutes
            summary[key]["entries"] += 1

        # Convert minutes to hours for display
        for key in summary:
            summary[key]["hours"] = round(summary[key]["minutes"] / 60, 2)

        return {
            "groups": summary,
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 2),
        }

    def display_time_entries(self, time_entries: list[dict[str, Any]]) -> None:
        """Display time entries in a table format."""
        if not time_entries:
            self.console.print("No time entries found.", style="yellow")
            return

        table = Table(title="Time Entries")
        table.add_column("ID", style="cyan")
        table.add_column("Issue", style="green")
        table.add_column("Duration", style="blue")
        table.add_column("Date", style="magenta")
        table.add_column("Author", style="yellow")
        table.add_column("Description", style="white")
        table.add_column("Type", style="red")

        for entry in time_entries:
            duration = entry.get("duration", {})
            minutes = duration.get("minutes", 0) if isinstance(duration, dict) else 0
            hours = round(minutes / 60, 2)
            duration_str = f"{hours}h ({minutes}m)"

            issue = entry.get("issue", {})
            issue_str = f"{issue.get('id', 'N/A')} - {issue.get('summary', 'No summary')[:30]}"

            table.add_row(
                entry.get("id", "N/A"),
                issue_str,
                duration_str,
                entry.get("date", "N/A"),
                entry.get("author", {}).get("fullName", "N/A"),
                entry.get("description", "N/A")[:40],
                entry.get("type", {}).get("name", "N/A"),
            )

        self.console.print(table)

    def display_time_summary(self, summary: dict[str, Any]) -> None:
        """Display time summary in a formatted way."""
        self.console.print("\n[bold blue]Time Summary[/bold blue]")
        self.console.print(f"Total Time: {summary['total_hours']}h ({summary['total_minutes']} minutes)")

        if summary.get("groups"):
            table = Table(title="Time by Group")
            table.add_column("Group", style="cyan")
            table.add_column("Hours", style="green")
            table.add_column("Minutes", style="blue")
            table.add_column("Entries", style="magenta")

            for group, data in summary["groups"].items():
                table.add_row(
                    group,
                    str(data["hours"]),
                    str(data["minutes"]),
                    str(data["entries"]),
                )

            self.console.print(table)
