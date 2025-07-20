"""Tutorial command group for YouTrack CLI guided learning.

This module provides interactive tutorials to help new users learn YouTrack CLI
through guided, hands-on experiences covering common workflows and best practices.
"""

import asyncio
from typing import Optional

import click
from rich.prompt import Confirm

from ..cli_utils import AliasedGroup
from ..console import get_console
from ..tutorial import ProgressTracker, TutorialEngine
from ..tutorial.modules import get_default_modules


@click.group(cls=AliasedGroup)
def tutorial() -> None:
    """Interactive tutorials for learning YouTrack CLI.

    Learn YouTrack CLI through guided, hands-on tutorials. Each tutorial
    covers essential workflows and best practices with step-by-step instructions.

    Key features:

    • Interactive step-by-step guidance

    • Progress tracking and resume capability

    • Real-world examples and tips

    • Beginner-friendly explanations

    Available tutorials:

    • setup     - Authentication and configuration

    • issues    - Creating and managing issues

    • projects  - Working with projects

    • time      - Time tracking workflows

    Examples:
    # List available tutorials
    yt tutorial list

    # Start the setup tutorial
    yt tutorial run setup

    # Resume a tutorial from a specific step
    yt tutorial run issues --step 3

    # Reset tutorial progress
    yt tutorial reset issues
    """
    pass


@tutorial.command()
@click.option("--show-progress", is_flag=True, help="Show completion progress for each tutorial")
@click.pass_context
def list(ctx: click.Context, show_progress: bool) -> None:
    """List available tutorials and their progress."""
    console = get_console()

    # Initialize tutorial system
    progress_tracker = ProgressTracker()
    config_manager = ctx.obj.get("config") if ctx.obj else None
    engine = TutorialEngine(progress_tracker, config_manager)

    # Register default modules
    for module in get_default_modules():
        engine.register_module(module)

    # Display welcome and tutorial list
    engine.display_welcome()
    engine.display_module_list()

    if show_progress:
        stats = progress_tracker.get_completion_stats()
        console.print("\n📊 [bold]Progress Summary:[/bold]")
        console.print(f"  ✅ Completed: {stats['completed']}")
        console.print(f"  📖 In Progress: {stats['in_progress']}")
        console.print(f"  ⏸️  Not Started: {stats['not_started']}")


@tutorial.command()
@click.argument("module_id")
@click.option("--step", type=int, help="Start from a specific step number")
@click.option("--reset", is_flag=True, help="Reset progress and start from the beginning")
@click.pass_context
def run(ctx: click.Context, module_id: str, step: Optional[int], reset: bool) -> None:
    """Run a specific tutorial module.

    MODULE_ID is the tutorial identifier (e.g., 'setup', 'issues', 'projects').
    Use 'yt tutorial list' to see available tutorials.
    """
    console = get_console()

    # Initialize tutorial system
    progress_tracker = ProgressTracker()
    config_manager = ctx.obj.get("config") if ctx.obj else None
    engine = TutorialEngine(progress_tracker, config_manager)

    # Register default modules
    for module in get_default_modules():
        engine.register_module(module)

    # Check if module exists
    if not engine.get_module(module_id):
        console.print(f"[red]❌ Tutorial '{module_id}' not found.[/red]")
        console.print("\nAvailable tutorials:")
        engine.display_module_list()
        return

    # Handle reset option
    if reset:
        if Confirm.ask(f"Reset progress for '{module_id}' tutorial?"):
            progress_tracker.reset_progress(module_id)
            console.print(f"[green]✅ Progress reset for '{module_id}' tutorial.[/green]")
        else:
            console.print("[yellow]Reset cancelled.[/yellow]")
            return

    # Run the tutorial
    async def run_tutorial():
        success = await engine.run_module(module_id, start_step=step)
        if success:
            console.print("\n[bold green]🎉 Tutorial completed successfully![/bold green]")
            console.print("[dim]Run 'yt tutorial list' to see other available tutorials.[/dim]")

    asyncio.run(run_tutorial())


@tutorial.command()
@click.argument("module_id", required=False)
@click.option("--all", "reset_all", is_flag=True, help="Reset progress for all tutorials")
def reset(module_id: Optional[str], reset_all: bool) -> None:
    """Reset tutorial progress.

    MODULE_ID is the tutorial to reset. Use --all to reset all tutorials.
    """
    console = get_console()
    progress_tracker = ProgressTracker()

    if reset_all:
        if Confirm.ask("Reset progress for ALL tutorials?"):
            # Get all progress and reset each module
            all_progress = progress_tracker.get_all_progress()
            for mid in all_progress.keys():
                progress_tracker.reset_progress(mid)
            console.print("[green]✅ All tutorial progress has been reset.[/green]")
        else:
            console.print("[yellow]Reset cancelled.[/yellow]")
    elif module_id:
        if Confirm.ask(f"Reset progress for '{module_id}' tutorial?"):
            if progress_tracker.reset_progress(module_id):
                console.print(f"[green]✅ Progress reset for '{module_id}' tutorial.[/green]")
            else:
                console.print(f"[yellow]No progress found for '{module_id}' tutorial.[/yellow]")
        else:
            console.print("[yellow]Reset cancelled.[/yellow]")
    else:
        console.print("[red]❌ Please specify a module ID or use --all.[/red]")
        console.print("Usage: yt tutorial reset MODULE_ID")
        console.print("       yt tutorial reset --all")


@tutorial.command()
@click.pass_context
def progress(ctx: click.Context) -> None:
    """Show detailed progress for all tutorials."""
    console = get_console()
    progress_tracker = ProgressTracker()

    # Initialize tutorial system to get module info
    config_manager = ctx.obj.get("config") if ctx.obj else None
    engine = TutorialEngine(progress_tracker, config_manager)
    for module in get_default_modules():
        engine.register_module(module)

    all_progress = progress_tracker.get_all_progress()

    if not all_progress:
        console.print("[yellow]📋 No tutorial progress found.[/yellow]")
        console.print("Start a tutorial with: [blue]yt tutorial run MODULE_ID[/blue]")
        return

    from rich import box
    from rich.table import Table

    table = Table(title="📚 Tutorial Progress Details", box=box.ROUNDED)
    table.add_column("Tutorial", style="cyan", no_wrap=True)
    table.add_column("Progress", style="yellow")
    table.add_column("Started", style="blue")
    table.add_column("Completed", style="green")
    table.add_column("Status", style="bold")

    for module_id, progress in all_progress.items():
        module = engine.get_module(module_id)
        title = module.title if module else module_id

        if progress.completed_at:
            status = "[green]✅ Complete[/green]"
            progress_text = "100%"
        elif progress.current_step > 0:
            total_steps = len(module.get_steps()) if module else 0
            if total_steps > 0:
                progress_pct = int((progress.current_step / total_steps) * 100)
                progress_text = f"{progress.current_step}/{total_steps} ({progress_pct}%)"
            else:
                progress_text = f"Step {progress.current_step}"
            status = "[yellow]📖 In Progress[/yellow]"
        else:
            progress_text = "0%"
            status = "[dim]⏸️  Started[/dim]"

        started = progress.started_at[:10] if progress.started_at else "-"
        completed = progress.completed_at[:10] if progress.completed_at else "-"

        table.add_row(title, progress_text, started, completed, status)

    console.print(table)

    # Show summary stats
    stats = progress_tracker.get_completion_stats()
    console.print(
        f"\n📊 [bold]Summary:[/bold] {stats['completed']} completed, "
        f"{stats['in_progress']} in progress, {stats['not_started']} not started"
    )


@tutorial.command()
def feedback() -> None:
    """Provide feedback about the tutorial system."""
    console = get_console()

    from rich import box
    from rich.panel import Panel

    feedback_panel = Panel(
        "[bold cyan]We'd love your feedback![/bold cyan]\n\n"
        "Help us improve the YouTrack CLI tutorial system:\n\n"
        "🐛 [yellow]Report issues:[/yellow] https://github.com/ryancheley/yt-cli/issues\n"
        "💡 [yellow]Suggest improvements:[/yellow] Create a feature request\n"
        "⭐ [yellow]Rate the tutorials:[/yellow] Leave a GitHub star\n\n"
        "[dim]Your feedback helps make YouTrack CLI better for everyone![/dim]",
        title="💬 Tutorial Feedback",
        border_style="cyan",
        box=box.ROUNDED,
    )

    console.print(feedback_panel)


# Add aliases for common commands
tutorial.add_alias("ls", "list")
tutorial.add_alias("start", "run")
