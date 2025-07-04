"""Report generation for YouTrack CLI."""

from typing import Any, Optional

import httpx
from rich.console import Console
from rich.table import Table

from .auth import AuthManager


class ReportManager:
    """Manages YouTrack report generation operations."""

    def __init__(self, auth_manager: AuthManager):
        """Initialize the report manager.

        Args:
            auth_manager: AuthManager instance for authentication
        """
        self.auth_manager = auth_manager
        self.console = Console()

    async def generate_burndown_report(
        self,
        project_id: str,
        sprint_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate a burndown report for a project or sprint.

        Args:
            project_id: Project ID or short name
            sprint_id: Sprint ID (optional)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            Dictionary with operation result
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {
                "status": "error",
                "message": "Not authenticated. Run 'yt auth login' first.",
            }

        # Build query for issues
        query_parts = [f"project: {project_id}"]

        if sprint_id:
            query_parts.append(f"Fix versions: {sprint_id}")

        if start_date and end_date:
            query_parts.append(f"created: {start_date} .. {end_date}")

        query = " ".join(query_parts)

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Accept": "application/json",
        }

        params = {
            "query": query,
            "fields": "id,summary,resolved,created,updated,state(name),spent(value)",
            "$top": "1000",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{credentials.base_url.rstrip('/')}/api/issues",
                    headers=headers,
                    params=params,
                    timeout=30.0,
                )
                response.raise_for_status()

                issues = response.json()

                # Calculate burndown metrics
                total_issues = len(issues)
                resolved_issues = len([i for i in issues if i.get("resolved")])
                remaining_issues = total_issues - resolved_issues

                # Calculate total effort if story points available
                total_effort = sum(
                    issue.get("spent", {}).get("value", 0) for issue in issues
                )

                burndown_data = {
                    "project": project_id,
                    "sprint": sprint_id,
                    "period": (
                        f"{start_date} to {end_date}"
                        if start_date and end_date
                        else "All time"
                    ),
                    "total_issues": total_issues,
                    "resolved_issues": resolved_issues,
                    "remaining_issues": remaining_issues,
                    "completion_rate": (
                        round((resolved_issues / total_issues * 100), 2)
                        if total_issues > 0
                        else 0
                    ),
                    "total_effort_hours": (
                        total_effort / 60 if total_effort > 0 else 0
                    ),  # Convert minutes to hours
                    "issues": issues,
                }

                return {"status": "success", "data": burndown_data}

            except httpx.HTTPError as e:
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

    async def generate_velocity_report(
        self, project_id: str, sprints: int = 5
    ) -> dict[str, Any]:
        """Generate a velocity report for recent sprints.

        Args:
            project_id: Project ID or short name
            sprints: Number of recent sprints to analyze

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

        # Get project versions (sprints)
        async with httpx.AsyncClient() as client:
            try:
                # First get the project to find versions
                project_response = await client.get(
                    f"{credentials.base_url.rstrip('/')}/api/admin/projects/{project_id}",
                    headers=headers,
                    params={"fields": "id,name,versions(id,name,released,releaseDate)"},
                    timeout=10.0,
                )
                project_response.raise_for_status()
                project_data = project_response.json()

                versions = project_data.get("versions", [])
                recent_versions = sorted(
                    versions, key=lambda v: v.get("releaseDate", ""), reverse=True
                )[:sprints]

                velocity_data: dict[str, Any] = {
                    "project": project_id,
                    "sprints_analyzed": len(recent_versions),
                    "sprints": [],
                }

                for version in recent_versions:
                    # Get issues for this sprint/version
                    query = f"project: {project_id} Fix versions: {version['name']}"

                    issues_response = await client.get(
                        f"{credentials.base_url.rstrip('/')}/api/issues",
                        headers=headers,
                        params={
                            "query": query,
                            "fields": "id,resolved,spent(value)",
                            "$top": "1000",
                        },
                        timeout=30.0,
                    )
                    issues_response.raise_for_status()
                    sprint_issues = issues_response.json()

                    resolved_count = len(
                        [i for i in sprint_issues if i.get("resolved")]
                    )
                    total_effort = sum(
                        issue.get("spent", {}).get("value", 0)
                        for issue in sprint_issues
                    )

                    sprint_data = {
                        "name": version["name"],
                        "release_date": version.get("releaseDate"),
                        "total_issues": len(sprint_issues),
                        "resolved_issues": resolved_count,
                        "total_effort_hours": (
                            total_effort / 60 if total_effort > 0 else 0
                        ),
                    }
                    velocity_data["sprints"].append(sprint_data)

                # Calculate average velocity
                if velocity_data["sprints"]:
                    avg_resolved = sum(
                        s["resolved_issues"] for s in velocity_data["sprints"]
                    ) / len(velocity_data["sprints"])
                    avg_effort = sum(
                        s["total_effort_hours"] for s in velocity_data["sprints"]
                    ) / len(velocity_data["sprints"])

                    velocity_data["average_issues_per_sprint"] = round(avg_resolved, 2)
                    velocity_data["average_effort_per_sprint"] = round(avg_effort, 2)

                return {"status": "success", "data": velocity_data}

            except httpx.HTTPError as e:
                return {"status": "error", "message": f"HTTP error: {e}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected error: {e}"}

    def display_burndown_report(self, burndown_data: dict[str, Any]) -> None:
        """Display burndown report in a formatted table.

        Args:
            burndown_data: Burndown report data
        """
        self.console.print(
            f"\n[bold blue]Burndown Report - {burndown_data['project']}[/bold blue]"
        )

        if burndown_data.get("sprint"):
            self.console.print(f"[cyan]Sprint:[/cyan] {burndown_data['sprint']}")

        self.console.print(f"[cyan]Period:[/cyan] {burndown_data['period']}")
        self.console.print(
            f"[cyan]Total Issues:[/cyan] {burndown_data['total_issues']}"
        )
        self.console.print(
            f"[cyan]Resolved Issues:[/cyan] {burndown_data['resolved_issues']}"
        )
        self.console.print(
            f"[cyan]Remaining Issues:[/cyan] {burndown_data['remaining_issues']}"
        )
        self.console.print(
            f"[cyan]Completion Rate:[/cyan] {burndown_data['completion_rate']}%"
        )

        if burndown_data["total_effort_hours"] > 0:
            self.console.print(
                f"[cyan]Total Effort:[/cyan] "
                f"{burndown_data['total_effort_hours']:.1f} hours"
            )

        # Create progress bar visualization
        completion_rate = burndown_data["completion_rate"]
        bar_length = 20
        filled_length = int(bar_length * completion_rate / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)

        self.console.print(f"\n[cyan]Progress:[/cyan] [{bar}] {completion_rate}%")

    def display_velocity_report(self, velocity_data: dict[str, Any]) -> None:
        """Display velocity report in a formatted table.

        Args:
            velocity_data: Velocity report data
        """
        self.console.print(
            f"\n[bold blue]Velocity Report - {velocity_data['project']}[/bold blue]"
        )

        if not velocity_data["sprints"]:
            self.console.print("No sprint data available.", style="yellow")
            return

        table = Table(title=f"Recent {velocity_data['sprints_analyzed']} Sprints")
        table.add_column("Sprint", style="cyan", no_wrap=True)
        table.add_column("Release Date", style="dim")
        table.add_column("Total Issues", style="blue")
        table.add_column("Resolved", style="green")
        table.add_column("Effort (hrs)", style="magenta")

        for sprint in velocity_data["sprints"]:
            table.add_row(
                sprint["name"],
                sprint.get("release_date", "N/A"),
                str(sprint["total_issues"]),
                str(sprint["resolved_issues"]),
                f"{sprint['total_effort_hours']:.1f}",
            )

        self.console.print(table)

        # Display averages
        if velocity_data.get("average_issues_per_sprint"):
            self.console.print(
                f"\n[cyan]Average Issues per Sprint:[/cyan] "
                f"{velocity_data['average_issues_per_sprint']}"
            )
            self.console.print(
                f"[cyan]Average Effort per Sprint:[/cyan] "
                f"{velocity_data['average_effort_per_sprint']:.1f} hours"
            )
