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
                # Return empty list for empty responses
                return []

            return response.json()
        except ValueError as e:
            if "Expecting value" in str(e) or "Empty response body" in str(e):
                # Return empty list for empty responses instead of raising an error
                return []
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

        # Parse date or use current timestamp
        work_date = self._parse_date(date) if date else int(datetime.now().timestamp() * 1000)

        work_item_data = {
            "duration": {"minutes": duration_minutes},
            "date": work_date,
        }

        if description:
            work_item_data["text"] = description
        if work_type:
            work_item_data["type"] = {"name": work_type}

        url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/timeTracking/workItems"
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(
                method="POST", url=url, json_data=work_item_data, headers=headers
            )

            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    "status": "success",
                    "message": f"Logged {duration} to issue {issue_id}",
                    "data": data,
                }
            error_text = response.text
            return {
                "status": "error",
                "message": f"Failed to log time (HTTP {response.status_code}): {error_text}",
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

        # Use issue-specific endpoint when filtering by issue_id
        if issue_id:
            url = f"{credentials.base_url.rstrip('/')}/api/issues/{issue_id}/timeTracking/workItems"
        else:
            # Get all time entries from the global endpoint
            url = f"{credentials.base_url.rstrip('/')}/api/workItems"

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        try:
            client_manager = get_client_manager()
            response = await client_manager.make_request(method="GET", url=url, params=params, headers=headers)
            if response.status_code == 200:
                data = self._parse_json_response(response)
                # Handle empty response or None data
                if data is None:
                    data = []
                elif not isinstance(data, list):
                    data = [data] if data else []
                return {
                    "status": "success",
                    "data": data,
                    "count": len(data),
                }
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
            fields="id,duration(minutes),date,description,author(id,fullName),issue(id,summary),type(name)",
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

    def _parse_date(self, date_str: str) -> int:
        """Parse date string to timestamp in milliseconds."""
        try:
            # Try different date formats
            formats = ["%Y-%m-%d", "%m/%d/%Y", "%d.%m.%Y", "%Y-%m-%d %H:%M:%S"]

            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return int(parsed_date.timestamp() * 1000)
                except ValueError:
                    continue

            # If no format matches, try relative dates
            if date_str.lower() == "today":
                return int(datetime.now().timestamp() * 1000)
            if date_str.lower() == "yesterday":
                return int((datetime.now() - timedelta(days=1)).timestamp() * 1000)

            # If all else fails, try to parse as ISO format
            parsed_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return int(parsed_date.timestamp() * 1000)
        except Exception:
            # Default to current timestamp if parsing fails
            return int(datetime.now().timestamp() * 1000)

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
                work_type = entry.get("type")
                if isinstance(work_type, dict) and work_type.get("name"):
                    key = work_type.get("name")
                else:
                    key = "No type"
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
        # Handle None
        if time_entries is None:
            self.console.print("No time entries found.", style="yellow")
            return

        # Ensure time_entries is a list
        if not isinstance(time_entries, list):
            time_entries = [time_entries] if time_entries else []

        # Handle empty list
        if not time_entries:
            self.console.print("No time entries found.", style="yellow")
            return

        table = Table(title="Time Entries")
        table.add_column("Issue", style="green")
        table.add_column("Duration", style="blue")
        table.add_column("Date", style="magenta")
        table.add_column("Author", style="yellow")
        table.add_column("Description", style="white")
        table.add_column("Type", style="red")
        table.add_column("Entry ID", style="cyan")

        for entry in time_entries:
            # Handle duration - extract minutes from YouTrack DurationValue
            duration = entry.get("duration", {})
            if isinstance(duration, dict):
                minutes = duration.get("minutes", 0)
            else:
                minutes = 0
            hours = round(minutes / 60, 2) if minutes > 0 else 0
            duration_str = f"{hours}h ({minutes}m)" if minutes > 0 else "No duration"

            # Handle issue information
            issue = entry.get("issue", {})
            if isinstance(issue, dict):
                # Format issue ID to show user-friendly project format
                issue_id = issue.get("id", "N/A")
                project = issue.get("project", {})
                project_short_name = project.get("shortName") if project else None
                issue_number = issue.get("numberInProject") if issue.get("numberInProject") else None

                # Create user-friendly ID format (e.g., "FPU-5" instead of "3-2")
                if project_short_name and issue_number:
                    formatted_issue_id = f"{project_short_name}-{issue_number}"
                else:
                    formatted_issue_id = issue_id

                issue_str = f"{formatted_issue_id} - {issue.get('summary', 'No summary')[:30]}"
            else:
                issue_str = "N/A"

            # Format date from timestamp to readable format
            date_value = entry.get("date")
            if isinstance(date_value, int):
                formatted_date = datetime.fromtimestamp(date_value / 1000).strftime("%Y-%m-%d %H:%M")
            else:
                formatted_date = str(date_value) if date_value else "N/A"

            # Handle author information
            author = entry.get("author", {})
            if isinstance(author, dict):
                author_name = author.get("fullName", "N/A")
            else:
                author_name = "N/A"

            # Handle work type - can be null/None
            work_type = entry.get("type")
            if isinstance(work_type, dict) and work_type.get("name"):
                type_name = work_type.get("name")
            else:
                type_name = ""

            # Handle description
            description = entry.get("description")
            if description is not None and str(description).strip():
                description = str(description)
                if len(description) > 40:
                    description = description[:40]
            else:
                description = ""

            table.add_row(
                issue_str,
                duration_str,
                formatted_date,
                author_name,
                str(description),
                type_name,
                str(entry.get("id", "N/A")),
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
