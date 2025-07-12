"""Time tracking command group for YouTrack CLI."""

import asyncio
from typing import Optional

import click

from ..auth import AuthManager
from ..console import get_console


@click.group()
def time() -> None:
    """Time tracking operations."""
    pass


@time.command()
@click.argument("issue_id")
@click.argument("duration")
@click.option("--date", "-d", help="Date for the work entry (YYYY-MM-DD or 'today')")
@click.option("--description", "-desc", help="Description of the work done")
@click.option("--work-type", "-t", help="Type of work (e.g., 'Development', 'Testing')")
@click.pass_context
def log(
    ctx: click.Context,
    issue_id: str,
    duration: str,
    date: Optional[str],
    description: Optional[str],
    work_type: Optional[str],
) -> None:
    """Log work time to an issue."""
    from ..time import TimeManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    time_manager = TimeManager(auth_manager)

    console.print(f"⏱️  Logging {duration} to issue {issue_id}...", style="blue")

    try:
        result = asyncio.run(time_manager.log_time(issue_id, duration, date, description, work_type))

        if result["status"] == "success":
            console.print(f"✅ {result['message']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException(result["message"])
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.ClickException("Failed to log time") from e


@time.command()
@click.option("--issue-id", "-i", help="Filter by specific issue ID")
@click.option("--user-id", "-u", help="Filter by specific user ID")
@click.option("--start-date", "-s", help="Start date for filtering (YYYY-MM-DD)")
@click.option("--end-date", "-e", help="End date for filtering (YYYY-MM-DD)")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def report(
    ctx: click.Context,
    issue_id: Optional[str],
    user_id: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    format: str,
) -> None:
    """Generate time reports with filtering options."""
    from ..time import TimeManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    time_manager = TimeManager(auth_manager)

    console.print("📊 Generating time report...", style="blue")

    try:
        result = asyncio.run(
            time_manager.get_time_entries(
                issue_id=issue_id,
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                fields="id,duration,date,description,author(id,fullName),issue(id,summary),type(name)",
            )
        )

        if result["status"] == "success":
            if format == "json":
                console.print_json(data=result["data"])
            else:
                time_manager.display_time_entries(result["data"])
                console.print(f"\n📈 Total entries: {result['count']}", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException(result["message"])
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.ClickException("Failed to generate report") from e


@time.command()
@click.option("--user-id", "-u", help="Filter by specific user ID")
@click.option("--start-date", "-s", help="Start date for filtering (YYYY-MM-DD)")
@click.option("--end-date", "-e", help="End date for filtering (YYYY-MM-DD)")
@click.option(
    "--group-by",
    "-g",
    type=click.Choice(["user", "issue", "type"]),
    default="user",
    help="Group summary by",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def summary(
    ctx: click.Context,
    user_id: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    group_by: str,
    format: str,
) -> None:
    """View time summaries with aggregation."""
    from ..time import TimeManager

    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))
    time_manager = TimeManager(auth_manager)

    console.print("📋 Generating time summary...", style="blue")

    try:
        result = asyncio.run(
            time_manager.get_time_summary(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                group_by=group_by,
            )
        )

        if result["status"] == "success":
            if format == "json":
                console.print_json(data=result["data"])
            else:
                time_manager.display_time_summary(result["data"])
                console.print(f"\n📊 Based on {result['total_entries']} entries", style="green")
        else:
            console.print(f"❌ {result['message']}", style="red")
            raise click.ClickException(result["message"])
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")
        raise click.ClickException("Failed to generate summary") from e
