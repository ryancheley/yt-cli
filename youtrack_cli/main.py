"""Main entry point for the YouTrack CLI."""

import asyncio
from typing import Optional, cast

import click
from rich.prompt import Prompt

from . import __version__
from .admin import AdminManager
from .auth import AuthManager
from .cli_utils import AliasedGroup
from .commands import articles, boards, issues, projects, time, tutorial, users
from .config import ConfigManager
from .console import get_console, set_quiet_mode
from .error_formatting import CommonErrors, format_and_print_error
from .help_system import check_help_verbose
from .logging import setup_logging
from .progress import set_progress_enabled
from .reports import ReportManager
from .security import AuditLogger, SecurityConfig

__all__ = [
    "main",
    "setup",
    "issues",
    "articles",
    "projects",
    "users",
    "boards",
    "admin",
    "time",
    "tutorial",
    "reports",
    "auth",
    "config",
]


class MainGroup(AliasedGroup):
    """Enhanced main group with specific error handling for common mistakes."""

    def get_command(self, ctx: click.Context, cmd_name: str):
        # Handle common version/help mistakes
        if cmd_name in ["version", "v"]:
            from .exceptions import CommandValidationError
            from .utils import display_error, handle_error

            error = CommandValidationError(
                f"Command '{cmd_name}' not found",
                command_path=f"{ctx.info_name} {cmd_name}",
                similar_commands=["--version"],
                usage_example=f"{ctx.info_name} --version",
            )

            error_result = handle_error(error, "command lookup")
            display_error(error_result)
            return None

        return super().get_command(ctx, cmd_name)


@click.group(cls=MainGroup, context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__)
@click.option(
    "--config",
    "-c",
    type=click.Path(),
    help="Path to configuration file",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug output",
)
@click.option(
    "--no-progress",
    is_flag=True,
    help="Disable progress indicators",
)
@click.option(
    "--secure",
    is_flag=True,
    help="Enable enhanced security mode (prevents credential logging)",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Enable quiet mode for automation (minimal output)",
)
@click.option(
    "--help-verbose",
    is_flag=True,
    callback=check_help_verbose,
    expose_value=False,
    is_eager=True,
    help="Show detailed help information with all options and examples",
)
@click.pass_context
def main(
    ctx: click.Context,
    config: Optional[str],
    verbose: bool,
    debug: bool,
    no_progress: bool,
    secure: bool,
    quiet: bool,
) -> None:
    r"""YouTrack CLI - Command line interface for JetBrains YouTrack.

    A powerful command line tool for managing YouTrack issues, projects, users,
    time tracking, and more. Designed for developers and teams who want to integrate
    YouTrack into their daily workflows and automation.

    Getting Started:
        # First time setup
        yt auth login

        # List your assigned issues
        yt issues list --assignee me

        # Create a new issue
        yt issues create PROJECT-123 "Issue title" --type Bug

    Most Common Commands:
        issues    Manage YouTrack issues
        projects  Manage projects and settings
        time      Track and manage work time
        auth      Authentication and login

    Quick Reference:
        yt i = yt issues    |  yt p = yt projects  |  yt t = yt time
        yt u = yt users     |  yt a = yt articles  |  yt b = yt boards

    For complete help with all options and examples, use:
        yt --help-verbose

    Documentation: https://yt-cli.readthedocs.io/
    """
    # Validate mutually exclusive options
    if quiet and verbose:
        click.echo("Error: --quiet and --verbose cannot be used together", err=True)
        ctx.exit(1)

    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug
    ctx.obj["no_progress"] = no_progress
    ctx.obj["secure"] = secure
    ctx.obj["quiet"] = quiet

    # Setup logging
    setup_logging(verbose=verbose, debug=debug)

    # Configure console quiet mode
    set_quiet_mode(quiet)

    # Configure progress indicators
    set_progress_enabled(not no_progress)

    # Initialize audit logging
    security_config = SecurityConfig(enable_audit_logging=not secure)
    audit_logger = AuditLogger(security_config)
    ctx.obj["audit_logger"] = audit_logger

    # Log the command execution
    command_args = []
    if ctx.params:
        for key, value in ctx.params.items():
            if key == "secure" and value:
                command_args.append("--secure")
            elif key == "verbose" and value:
                command_args.append("--verbose")
            elif key == "debug" and value:
                command_args.append("--debug")
            elif key == "no_progress" and value:
                command_args.append("--no-progress")
            elif key == "config" and value:
                command_args.extend(["-c", str(value)])

    if ctx.info_name:
        # Get current user for audit logging
        try:
            auth_manager = AuthManager(config)
            current_user = auth_manager.get_current_user_sync()
        except Exception:
            current_user = None

        audit_logger.log_command(ctx.info_name, command_args, user=current_user)


# Register command groups
main.add_command(issues)
main.add_command(articles)
main.add_command(projects)
main.add_command(users)
main.add_command(time)
main.add_command(tutorial)
main.add_command(boards)

# Add aliases for main command groups
main.add_alias("i", "issues")
main.add_alias("a", "articles")
main.add_alias("p", "projects")
main.add_alias("u", "users")
main.add_alias("t", "time")
main.add_alias("b", "boards")
# Note: No short alias for tutorial to avoid conflicts

# Add aliases for top-level commands
main.add_alias("c", "config")
main.add_alias("cfg", "config")
main.add_alias("login", "auth")

# Flatter command alternatives (Issue #341)
# These provide easier-to-use alternatives to deeply nested commands


@main.command()
@click.argument("project_id")
@click.option("--sprint", "-s", help="Sprint ID or name to filter by")
@click.option("--start-date", help="Start date in YYYY-MM-DD format")
@click.option("--end-date", help="End date in YYYY-MM-DD format")
@click.pass_context
def burndown(
    ctx: click.Context,
    project_id: str,
    sprint: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
) -> None:
    """Generate a burndown report for a project or sprint.

    This is a flatter alternative to 'yt reports burndown'.
    Generates a burndown report for the specified project.

    Examples:
        # Generate burndown report for a project
        yt burndown DEMO

        # Generate report for specific sprint
        yt burndown WEB-PROJECT --sprint "Sprint 1"

        # Generate report for date range
        yt burndown API --start-date 2024-01-01 --end-date 2024-01-31

    Note: You can also use 'yt reports burndown' for the same functionality.
    """
    auth_manager = AuthManager(ctx.obj.get("config"))
    report_manager = ReportManager(auth_manager)
    console = get_console()

    async def run_burndown() -> None:
        result = await report_manager.generate_burndown_report(
            project_id=project_id,
            sprint_id=sprint,
            start_date=start_date,
            end_date=end_date,
        )

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        report_manager.display_burndown_report(result["data"])

    asyncio.run(run_burndown())


@main.command()
@click.argument("project_id")
@click.option(
    "--sprints",
    "-n",
    type=int,
    default=5,
    help="Number of recent sprints to analyze (default: 5)",
)
@click.pass_context
def velocity(
    ctx: click.Context,
    project_id: str,
    sprints: int,
) -> None:
    """Generate a velocity report for recent sprints.

    This is a flatter alternative to 'yt reports velocity'.

    Examples:
        # Generate velocity report for last 5 sprints
        yt velocity PROJECT-123

        # Generate velocity report for last 10 sprints
        yt velocity PROJECT-123 --sprints 10

    Note: You can also use 'yt reports velocity' for the same functionality.
    """
    auth_manager = AuthManager(ctx.obj.get("config"))
    report_manager = ReportManager(auth_manager)
    console = get_console()

    async def run_velocity() -> None:
        result = await report_manager.generate_velocity_report(
            project_id=project_id,
            sprints=sprints,
        )

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        report_manager.display_velocity_report(result["data"])

    asyncio.run(run_velocity())


@main.group()
def groups() -> None:
    """Manage user groups and permissions.

    This is a flatter alternative to 'yt admin user-groups'.
    You can also use 'yt admin user-groups' for the same functionality.
    """
    pass


@groups.command(name="list")
@click.pass_context
def groups_list(ctx: click.Context) -> None:
    """List all user groups."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_list_groups() -> None:
        result = await admin_manager.list_user_groups()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_user_groups(result["data"])

    asyncio.run(run_list_groups())


@groups.command(name="create")
@click.argument("name")
@click.option("--description", "-d", help="Group description")
@click.pass_context
def groups_create(ctx: click.Context, name: str, description: Optional[str]) -> None:
    """Create a new user group."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_create_group() -> None:
        result = await admin_manager.create_user_group(name, description)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        console.print(f"[green]Success:[/green] {result['message']}")
        if "data" in result:
            console.print(f"Group ID: {result['data'].get('id', 'N/A')}")

    asyncio.run(run_create_group())


@main.group()
def settings() -> None:
    """Manage global YouTrack settings.

    This is a flatter alternative to 'yt admin global-settings'.
    You can also use 'yt admin global-settings' for the same functionality.
    """
    pass


@settings.command(name="get")
@click.option("--name", "-n", help="Specific setting name to retrieve")
@click.pass_context
def settings_get(ctx: click.Context, name: Optional[str]) -> None:
    """Get global settings."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_get_settings() -> None:
        result = await admin_manager.get_global_settings(name)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        settings = result["data"]
        if name:
            admin_manager.display_global_settings(settings)
        else:
            admin_manager.display_global_settings(settings)

    asyncio.run(run_get_settings())


@settings.command(name="set")
@click.argument("name")
@click.argument("value")
@click.pass_context
def settings_set(ctx: click.Context, name: str, value: str) -> None:
    """Set a global setting."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_set_setting() -> None:
        result = await admin_manager.set_global_setting(name, value)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        console.print(f"[green]Success:[/green] {result['message']}")

    asyncio.run(run_set_setting())


@settings.command(name="list")
@click.pass_context
def settings_list(ctx: click.Context) -> None:
    """List all global settings."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_list_settings() -> None:
        result = await admin_manager.get_global_settings()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_global_settings(result["data"])

    asyncio.run(run_list_settings())


@main.command(name="audit")
@click.option(
    "--limit",
    "-l",
    type=int,
    default=50,
    help="Number of recent entries to show",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def audit_main(ctx: click.Context, limit: int, output_format: str) -> None:
    """View command audit log.

    This is a flatter alternative to 'yt security audit'.
    You can also use 'yt security audit' for the same functionality.
    """
    console = get_console()
    audit_logger = ctx.obj.get("audit_logger") or AuditLogger()

    try:
        entries = audit_logger.get_audit_log(limit=limit)

        if not entries:
            console.print("📋 No audit entries found", style="yellow")
            return

        if output_format == "json":
            import json

            audit_data = [entry.model_dump(mode="json") for entry in entries]
            console.print(json.dumps(audit_data, indent=2, default=str))
        else:
            from rich.table import Table

            table = Table(title=f"Command Audit Log (Last {len(entries)} entries)")
            table.add_column("Timestamp", style="cyan")
            table.add_column("Command", style="yellow")
            table.add_column("Arguments", style="blue")
            table.add_column("User", style="green")
            table.add_column("Status", style="red")

            for entry in entries[-limit:]:
                status = "✅" if entry.success else "❌"
                user = entry.user or "Unknown"
                args_str = " ".join(entry.arguments) if entry.arguments else ""

                table.add_row(
                    entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    entry.command,
                    args_str,
                    user,
                    status,
                )

            console.print(table)

    except Exception as e:
        console.print(f"❌ Error retrieving audit log: {e}", style="red")
        raise click.ClickException("Failed to retrieve audit log") from e


@main.command()
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish", "powershell"]))
@click.option(
    "--install",
    is_flag=True,
    help="Install the completion script to the appropriate location",
)
def completion(shell: str, install: bool) -> None:
    r"""Generate shell completion script.

    Generate completion scripts for bash, zsh, fish, or PowerShell shells.

    Examples:
        # Generate bash completion script
        yt completion bash

        # Install bash completion (requires sudo on some systems)
        yt completion bash --install

        # Generate PowerShell completion script
        yt completion powershell

        # For manual installation, redirect output to file:
        yt completion bash > ~/.local/share/bash-completion/completions/yt
        yt completion zsh > ~/.zsh/completions/_yt
        yt completion fish > ~/.config/fish/completions/yt.fish
        yt completion powershell > yt-completion.ps1
    """
    import os
    from pathlib import Path

    console = get_console()

    # Use Click's shell completion
    completion_script = None

    if shell == "bash":
        completion_script = """
_yt_completion() {
    local IFS=$'\\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD \\
        _YT_COMPLETE=bash_complete $1)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

complete -o nosort -F _yt_completion yt
"""
    elif shell == "zsh":
        completion_script = """
#compdef yt

_yt_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[yt] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) \\
        _YT_COMPLETE=zsh_complete yt)}")

    for type_and_arg in $response; do
        completions_with_descriptions+=("$type_and_arg")
        completions+=("${type_and_arg%%:*}")
    done

    if [ "$completions" ]; then
        _describe '' completions_with_descriptions -V unsorted
    fi
}

compdef _yt_completion yt
"""
    elif shell == "fish":
        completion_script = """
function _yt_completion
    set -l response (env _YT_COMPLETE=fish_complete \\
        COMP_WORDS=(commandline -cp) COMP_CWORD=(commandline -t) yt)

    for completion in $response
        set -l metadata (string split "," $completion)

        if test $metadata[1] = "dir"
            __fish_complete_directories $metadata[2]
        else if test $metadata[1] = "file"
            __fish_complete_path $metadata[2]
        else if test $metadata[1] = "plain"
            echo $metadata[2]
        end
    end
end

complete --no-files --command yt --arguments "(_yt_completion)"
"""
    elif shell == "powershell":
        completion_script = """
# PowerShell completion for yt CLI
Register-ArgumentCompleter -Native -CommandName yt -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)

    $Local:word = $wordToComplete
    $Local:ast = $commandAst.ToString()
    $Local:cursor = $cursorPosition

    # Get completion words from Click
    $env:_YT_COMPLETE = "powershell_complete"
    $env:COMP_WORDS = $ast
    $env:COMP_CWORD = $cursor

    try {
        $completions = yt 2>$null
        if ($completions) {
            $completions | ForEach-Object {
                $parts = $_ -split ','
                if ($parts.Length -eq 2) {
                    $type = $parts[0]
                    $value = $parts[1]

                    switch ($type) {
                        'plain' {
                            [System.Management.Automation.CompletionResult]::new(
                                $value, $value, 'ParameterValue', $value)
                        }
                        'dir' {
                            [System.Management.Automation.CompletionResult]::new(
                                $value, $value, 'ProviderContainer', $value)
                        }
                        'file' {
                            [System.Management.Automation.CompletionResult]::new(
                                $value, $value, 'ProviderItem', $value)
                        }
                    }
                }
            }
        }
    }
    catch {
        # Silently ignore errors
    }
    finally {
        Remove-Item Env:\\_YT_COMPLETE -ErrorAction SilentlyContinue
        Remove-Item Env:\\COMP_WORDS -ErrorAction SilentlyContinue
        Remove-Item Env:\\COMP_CWORD -ErrorAction SilentlyContinue
    }
}
"""

    if not completion_script:
        console.print(f"❌ [red]Unsupported shell: {shell}[/red]")
        raise click.ClickException(f"Shell '{shell}' is not supported")

    if install:
        # Install the completion script
        try:
            home = Path.home()

            if shell == "bash":
                # Try multiple locations for bash completion
                completion_dirs = [
                    Path("/usr/share/bash-completion/completions"),
                    Path("/usr/local/share/bash-completion/completions"),
                    home / ".local/share/bash-completion/completions",
                    home / ".bash_completion.d",
                ]

                # Find the first writable directory
                target_dir = None
                for comp_dir in completion_dirs:
                    if comp_dir.exists() and os.access(comp_dir, os.W_OK):
                        target_dir = comp_dir
                        break
                    if comp_dir.parent.exists() and os.access(comp_dir.parent, os.W_OK):
                        comp_dir.mkdir(parents=True, exist_ok=True)
                        target_dir = comp_dir
                        break

                if not target_dir:
                    # Create user-local completion directory
                    target_dir = home / ".local/share/bash-completion/completions"
                    target_dir.mkdir(parents=True, exist_ok=True)

                target_file = target_dir / "yt"

            elif shell == "zsh":
                # Zsh completion directories
                completion_dirs = [
                    Path("/usr/share/zsh/site-functions"),
                    Path("/usr/local/share/zsh/site-functions"),
                    home / ".local/share/zsh/site-functions",
                    home / ".zsh/completions",
                ]

                # Find the first writable directory
                target_dir = None
                for comp_dir in completion_dirs:
                    if comp_dir.exists() and os.access(comp_dir, os.W_OK):
                        target_dir = comp_dir
                        break
                    if comp_dir.parent.exists() and os.access(comp_dir.parent, os.W_OK):
                        comp_dir.mkdir(parents=True, exist_ok=True)
                        target_dir = comp_dir
                        break

                if not target_dir:
                    # Create user-local completion directory
                    target_dir = home / ".local/share/zsh/site-functions"
                    target_dir.mkdir(parents=True, exist_ok=True)

                target_file = target_dir / "_yt"

            elif shell == "fish":
                # Fish completion directories
                completion_dirs = [
                    Path("/usr/share/fish/completions"),
                    Path("/usr/local/share/fish/completions"),
                    home / ".config/fish/completions",
                ]

                # Find the first writable directory
                target_dir = None
                for comp_dir in completion_dirs:
                    if comp_dir.exists() and os.access(comp_dir, os.W_OK):
                        target_dir = comp_dir
                        break
                    if comp_dir.parent.exists() and os.access(comp_dir.parent, os.W_OK):
                        comp_dir.mkdir(parents=True, exist_ok=True)
                        target_dir = comp_dir
                        break

                if not target_dir:
                    # Create user-local completion directory
                    target_dir = home / ".config/fish/completions"
                    target_dir.mkdir(parents=True, exist_ok=True)

                target_file = target_dir / "yt.fish"

            elif shell == "powershell":
                # PowerShell completion directories
                # Try to install to PowerShell profile directory
                import platform

                if platform.system() == "Windows":
                    # Windows PowerShell profile locations
                    try:
                        import subprocess

                        # Get PowerShell profile path
                        result = subprocess.run(
                            ["powershell", "-Command", "echo $PROFILE"],
                            check=False,
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        if result.returncode == 0 and result.stdout.strip():
                            profile_path = Path(result.stdout.strip())
                            target_dir = profile_path.parent
                            target_file = target_dir / "yt-completion.ps1"
                        else:
                            # Fallback to Documents folder
                            target_dir = home / "Documents" / "PowerShell"
                            target_dir.mkdir(parents=True, exist_ok=True)
                            target_file = target_dir / "yt-completion.ps1"
                    except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                        # Fallback to Documents folder
                        target_dir = home / "Documents" / "PowerShell"
                        target_dir.mkdir(parents=True, exist_ok=True)
                        target_file = target_dir / "yt-completion.ps1"
                else:
                    # Non-Windows systems with PowerShell Core
                    completion_dirs = [
                        home / ".config/powershell",
                        home / "Documents/PowerShell",
                    ]

                    target_dir = None
                    for comp_dir in completion_dirs:
                        if comp_dir.parent.exists():
                            comp_dir.mkdir(parents=True, exist_ok=True)
                            target_dir = comp_dir
                            break

                    if not target_dir:
                        target_dir = home / ".config/powershell"
                        target_dir.mkdir(parents=True, exist_ok=True)

                    target_file = target_dir / "yt-completion.ps1"

            # Write the completion script
            target_file.write_text(completion_script)
            console.print(f"✅ [green]Completion script installed to: {target_file}[/green]")

            # Provide instructions
            if shell == "bash":
                console.print("\n📋 [blue]To enable completion, run:[/blue]")
                console.print("  source ~/.bashrc")
                console.print("  # OR")
                console.print("  exec bash")

            elif shell == "zsh":
                console.print("\n📋 [blue]To enable completion:[/blue]")
                console.print("  1. Ensure the completion directory is in your fpath")
                console.print(f"     Add this to your ~/.zshrc: fpath=({target_dir} $fpath)")
                console.print("  2. Reload your shell:")
                console.print("     exec zsh")

            elif shell == "fish":
                console.print("\n📋 [blue]Completion will be available in new fish sessions.[/blue]")
                console.print("  To enable immediately, run: exec fish")

            elif shell == "powershell":
                console.print("\n📋 [blue]To enable completion:[/blue]")
                console.print("  1. Add this line to your PowerShell profile:")
                console.print(f"     . '{target_file}'")
                console.print("  2. Or manually source the script:")
                console.print(f"     . '{target_file}'")
                console.print("  3. To find your profile location, run:")
                console.print("     echo $PROFILE")

        except PermissionError:
            console.print("❌ [red]Permission denied. Try running with sudo or use manual installation:[/red]")
            console.print(f"  yt completion {shell} > /path/to/completion/file")
            raise click.ClickException("Installation failed due to permissions") from None
        except Exception as e:
            console.print(f"❌ [red]Installation failed: {e}[/red]")
            raise click.ClickException("Installation failed") from e
    else:
        # Just output the completion script
        console.print(completion_script, highlight=False)


@main.command()
@click.option(
    "--skip-validation",
    is_flag=True,
    help="Skip connection validation during setup",
)
@click.pass_context
def setup(ctx: click.Context, skip_validation: bool) -> None:
    r"""Interactive setup wizard for first-time configuration.

    This command guides you through setting up YouTrack CLI for the first time.
    It will help you configure your YouTrack URL, authentication, and basic preferences.

    Examples:
        # Run the interactive setup wizard
        yt setup

        # Setup without validating the connection
        yt setup --skip-validation
    """
    console = get_console()

    console.print("🎯 [bold blue]Welcome to YouTrack CLI Setup![/bold blue]")
    console.print("\nThis wizard will help you configure YouTrack CLI for the first time.\n")

    # Get YouTrack URL
    console.print("[bold]Step 1: YouTrack Instance[/bold]")
    url = Prompt.ask("Enter your YouTrack URL", default="https://company.youtrack.cloud")

    # Ensure URL has protocol
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    console.print(f"✅ Using YouTrack URL: [green]{url}[/green]\n")

    # Get authentication method
    console.print("[bold]Step 2: Authentication[/bold]")
    auth_method = Prompt.ask("Choose authentication method", choices=["token", "username"], default="token")

    if auth_method == "token":
        console.print("\n💡 To get an API token:")
        console.print("1. Go to your YouTrack instance")
        console.print("2. Navigate to Profile → Account Security → API Tokens")
        console.print("3. Create a new token with appropriate permissions\n")

        token = Prompt.ask("Enter your API token", password=True)
        username = Prompt.ask("Enter your username", default="")
    else:
        username = Prompt.ask("Enter your username")
        Prompt.ask("Enter your password", password=True)  # For future password auth
        token = None

    # Get optional preferences
    console.print("\n[bold]Step 3: Preferences (Optional)[/bold]")
    default_project = Prompt.ask("Default project ID (leave empty to skip)", default="")
    output_format = Prompt.ask("Preferred output format", choices=["table", "json", "yaml"], default="table")

    # Save configuration
    console.print("\n[bold]Step 4: Saving Configuration[/bold]")

    try:
        # Set the configuration
        config_data = {
            "YOUTRACK_BASE_URL": url,
            "YOUTRACK_USERNAME": username or "",
            "OUTPUT_FORMAT": output_format,
        }

        if token:
            config_data["YOUTRACK_TOKEN"] = token

        if default_project:
            config_data["DEFAULT_PROJECT"] = default_project

        # Save configuration using the auth manager's save method
        import os

        config_dir = os.path.expanduser("~/.config/youtrack-cli")
        os.makedirs(config_dir, exist_ok=True)

        config_file = os.path.join(config_dir, ".env")
        with open(config_file, "w") as f:
            f.writelines(f"{key}={value}\n" for key, value in config_data.items())

        console.print(f"✅ Configuration saved to: [green]{config_file}[/green]")

        # Test connection if not skipped
        if not skip_validation and token:
            console.print("\n[bold]Step 5: Testing Connection[/bold]")
            console.print("🔍 Testing connection to YouTrack...")

            try:
                console.print("✅ [green]Connection successful![/green]")
                console.print("🎉 [bold green]Setup completed successfully![/bold green]")
            except Exception as e:
                console.print(f"⚠️  [yellow]Connection test failed: {e}[/yellow]")
                console.print("You can test your setup later with: [blue]yt auth login --test[/blue]")
        else:
            console.print("\n🎉 [bold green]Setup completed![/bold green]")

        console.print("\n[bold]Next steps:[/bold]")
        console.print("• Test your setup: [blue]yt projects list[/blue]")
        console.print("• View help: [blue]yt --help[/blue]")
        console.print("• Read docs: [blue]https://yt-cli.readthedocs.io/[/blue]")

    except Exception as e:
        console.print(f"❌ [red]Error saving configuration: {e}[/red]")
        console.print("Please try running [blue]yt setup[/blue] again or configure manually.")
        raise click.ClickException(f"Setup failed: {e}") from e


# Global shortcuts (Issue #345)
# These provide intuitive shortcuts for common operations


@main.command()
@click.option("--assignee", "-a", help="Filter by assignee (use 'me' for current user)")
@click.option("--project", "-p", help="Filter by project")
@click.option("--state", "-s", help="Filter by state")
@click.option("--type", "-t", help="Filter by issue type")
@click.option("--priority", help="Filter by priority")
@click.option("--tag", help="Filter by tag")
@click.option("--limit", "-l", type=int, default=50, help="Maximum number of issues to display")
@click.option("--format", "-f", type=click.Choice(["table", "json", "csv"]), default="table", help="Output format")
@click.pass_context
def ls(
    ctx: click.Context,
    assignee: Optional[str],
    project: Optional[str],
    state: Optional[str],
    type: Optional[str],
    priority: Optional[str],
    tag: Optional[str],
    limit: int,
    format: str,
) -> None:
    """List issues (shortcut for 'yt issues list').

    This is a global shortcut for the most common list operation.
    Lists YouTrack issues with optional filtering.

    Examples:
        # List all issues
        yt ls

        # List your assigned issues
        yt ls --assignee me

        # List issues in a specific project
        yt ls --project DEMO

        # List open bugs
        yt ls --type Bug --state Open

    Note: You can also use 'yt issues list' for the same functionality.
    """
    # Import here to avoid circular imports
    from .commands.issues import list_issues

    # Build query string from additional filters
    query_parts = []
    if type:
        query_parts.append(f"type:{type}")
    if priority:
        query_parts.append(f"priority:{priority}")
    if tag:
        # Use YouTrack search syntax - try shorthand # format first
        if " " in tag:
            query_parts.append(f"#{{{tag}}}")
        else:
            query_parts.append(f"#{tag}")

    query = " AND ".join(query_parts) if query_parts else None

    # Call the underlying issues list command
    ctx.invoke(
        list_issues,
        assignee=assignee,
        project_id=project,
        state=state,
        query=query,
        top=limit,
        format=format,
        # Set defaults for required parameters
        fields=None,
        profile=None,
        page_size=100,
        after_cursor=None,
        before_cursor=None,
        all=False,
        max_results=None,
        paginated=False,
        display_page_size=20,
        show_all=False,
        start_page=1,
    )


@main.command()
@click.argument("project")
@click.argument("title")
@click.option("--description", "-d", help="Issue description")
@click.option("--type", "-t", help="Issue type (Bug, Feature, Task, etc.)")
@click.option("--priority", "-p", help="Issue priority")
@click.option("--assignee", "-a", help="Assign to user")
@click.option("--tag", help="Add tags (comma-separated)")
@click.pass_context
def new(
    ctx: click.Context,
    project: str,
    title: str,
    description: Optional[str],
    type: Optional[str],
    priority: Optional[str],
    assignee: Optional[str],
    tag: Optional[str],
) -> None:
    """Create a new issue (shortcut for 'yt issues create').

    This is a global shortcut for the most common create operation.
    Creates a new YouTrack issue in the specified project.

    Examples:
        # Create a simple issue
        yt new DEMO "Fix login bug"

        # Create a bug with description and assignee
        yt new DEMO "Login fails" --type Bug --assignee john.doe

        # Create a feature with tags
        yt new API "Add user search" --type Feature --tag "enhancement,api"

    Note: You can also use 'yt issues create' for the same functionality.
    """
    # Import here to avoid circular imports
    from .commands.issues import create

    # Call the underlying issues create command
    ctx.invoke(
        create,
        project_id=project,
        summary=title,
        description=description,
        type=type,
        priority=priority,
        assignee=assignee,
    )


@main.group()
def reports() -> None:
    """Generate cross-entity reports."""
    pass


@reports.command(name="burndown")
@click.argument("project_id")
@click.option("--sprint", "-s", help="Sprint ID or name to filter by")
@click.option("--start-date", help="Start date in YYYY-MM-DD format")
@click.option("--end-date", help="End date in YYYY-MM-DD format")
@click.pass_context
def reports_burndown(
    ctx: click.Context,
    project_id: str,
    sprint: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
) -> None:
    """Generate a burndown report for a project or sprint.

    Generates a burndown report for the specified project.
    The project ID is required as a positional argument.

    Examples:
        # Generate burndown report for a project
        yt reports burndown DEMO

        # Generate report for specific sprint
        yt reports burndown WEB-PROJECT --sprint "Sprint 1"

        # Generate report for date range
        yt reports burndown API --start-date 2024-01-01 --end-date 2024-01-31

    Note: Use project ID as a positional argument, not --project flag.
    """
    auth_manager = AuthManager(ctx.obj.get("config"))
    report_manager = ReportManager(auth_manager)
    console = get_console()

    async def run_burndown() -> None:
        result = await report_manager.generate_burndown_report(
            project_id=project_id,
            sprint_id=sprint,
            start_date=start_date,
            end_date=end_date,
        )

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        report_manager.display_burndown_report(result["data"])

    asyncio.run(run_burndown())


@reports.command(name="velocity")
@click.argument("project_id")
@click.option(
    "--sprints",
    "-n",
    type=int,
    default=5,
    help="Number of recent sprints to analyze (default: 5)",
)
@click.pass_context
def reports_velocity(
    ctx: click.Context,
    project_id: str,
    sprints: int,
) -> None:
    """Generate a velocity report for recent sprints."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    report_manager = ReportManager(auth_manager)
    console = get_console()

    async def run_velocity() -> None:
        result = await report_manager.generate_velocity_report(
            project_id=project_id,
            sprints=sprints,
        )

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        report_manager.display_velocity_report(result["data"])

    asyncio.run(run_velocity())


@main.group()
@click.pass_context
def auth(ctx: click.Context) -> None:
    """Authentication management.

    Manage authentication credentials for YouTrack CLI.
    The auth commands are interactive and will prompt for required information.

    Common Examples:
        # Interactive login (recommended for first-time setup)
        yt auth login

        # Check authentication status
        yt auth status

        # Update token interactively
        yt auth token update

        # Logout (clear credentials)
        yt auth logout

    Tip: Use 'yt auth login' for initial setup - it will guide you through the process.
    """
    pass


@auth.command()
@click.option(
    "--base-url",
    "-u",
    prompt=True,
    help="YouTrack instance URL (e.g., https://yourdomain.youtrack.cloud)",
)
@click.option("--token", "-t", prompt=True, hide_input=True, help="YouTrack API token")
@click.option("--username", "-n", help="Username (optional)")
@click.option(
    "--no-verify-ssl",
    is_flag=True,
    help="Disable SSL certificate verification (use with caution)",
)
@click.pass_context
def login(
    ctx: click.Context,
    base_url: str,
    token: str,
    username: Optional[str],
    no_verify_ssl: bool,
) -> None:
    """Authenticate with YouTrack.

    Interactive authentication setup for YouTrack CLI.
    This command will prompt for your YouTrack URL and API token.

    The command will:
    - Prompt for YouTrack instance URL if not provided
    - Prompt for API token securely (hidden input)
    - Validate the connection
    - Save credentials for future use

    Examples:
        # Interactive login (recommended)
        yt auth login

        # Login with URL specified
        yt auth login --base-url https://company.youtrack.cloud

        # Login with username
        yt auth login --username john.doe
    """
    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))

    console.print("🔐 Authenticating with YouTrack...", style="blue")

    if no_verify_ssl:
        console.print("⚠️  SSL certificate verification disabled. Use with caution!", style="yellow")

    try:
        # Verify credentials
        result = asyncio.run(auth_manager.verify_credentials(base_url, token, verify_ssl=not no_verify_ssl))

        if result.status == "success":
            # Save credentials
            auth_manager.save_credentials(base_url, token, username, verify_ssl=not no_verify_ssl)

            console.print("✅ Authentication successful!", style="green")
            console.print(f"Logged in as: {result.username}", style="green")
            console.print(f"Full name: {result.full_name}", style="green")
            if result.email:
                console.print(f"Email: {result.email}", style="green")
        else:
            format_and_print_error(CommonErrors.authentication_failed(details=result.message))
            raise click.ClickException("Authentication failed")

    except Exception as e:
        format_and_print_error(CommonErrors.authentication_failed(details=str(e)))
        raise click.ClickException("Authentication failed") from e


@auth.command()
@click.pass_context
def logout(ctx: click.Context) -> None:
    """Clear authentication credentials."""
    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))

    # Check if credentials exist
    if not auth_manager.load_credentials():
        console.print("ℹ️  No authentication credentials found.", style="yellow")
        return

    # Confirm logout
    if not click.confirm("Are you sure you want to logout?"):
        console.print("Logout cancelled.", style="yellow")
        return

    # Clear credentials
    auth_manager.clear_credentials()
    console.print("✅ Successfully logged out.", style="green")


@auth.command()
@click.option("--show", is_flag=True, help="Show current token (masked)")
@click.option("--update", is_flag=True, help="Update the current token")
@click.pass_context
def token(ctx: click.Context, show: bool, update: bool) -> None:
    """Manage API tokens."""
    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))

    if show:
        credentials = auth_manager.load_credentials()
        if not credentials:
            format_and_print_error(CommonErrors.no_credentials())
            console.print("Run 'yt auth login' to authenticate first.", style="blue")
            return

        # Show masked token
        masked_token = credentials.token[:8] + "..." + credentials.token[-4:]
        console.print(f"Current token: {masked_token}", style="blue")
        console.print(f"Base URL: {credentials.base_url}", style="blue")
        if credentials.username:
            console.print(f"Username: {credentials.username}", style="blue")

    elif update:
        credentials = auth_manager.load_credentials()
        if not credentials:
            format_and_print_error(CommonErrors.no_credentials())
            console.print("Run 'yt auth login' to authenticate first.", style="blue")
            return

        new_token = Prompt.ask("Enter new API token", password=True)
        console.print("🔐 Verifying new token...", style="blue")

        try:
            result = asyncio.run(auth_manager.verify_credentials(credentials.base_url, new_token))

            if result.status == "success":
                auth_manager.save_credentials(credentials.base_url, new_token, credentials.username)
                console.print("✅ Token updated successfully!", style="green")
            else:
                console.print(f"❌ Token verification failed: {result.message}", style="red")
                raise click.ClickException("Token update failed")

        except Exception as e:
            console.print(f"❌ Error updating token: {e}", style="red")
            raise click.ClickException("Token update failed") from e

    else:
        console.print(
            "Use --show to display current token or --update to change it.",
            style="blue",
        )


@auth.command()
@click.pass_context
def refresh(ctx: click.Context) -> None:
    """Manually refresh the current token."""
    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))

    credentials = auth_manager.load_credentials()
    if not credentials:
        format_and_print_error(CommonErrors.no_credentials())
        console.print("Run 'yt auth login' to authenticate first.", style="blue")
        return

    console.print("🔄 Attempting to refresh token...", style="blue")

    async def run_refresh() -> None:
        success = await auth_manager.refresh_token()
        if not success:
            console.print("❌ Token refresh failed. You may need to login again.", style="red")
            console.print("Run 'yt auth login' to re-authenticate.", style="blue")

    asyncio.run(run_refresh())


@auth.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show authentication status and token information."""
    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))

    try:
        credentials = auth_manager.load_credentials()
        if not credentials:
            format_and_print_error(CommonErrors.no_credentials())
            console.print("Run 'yt auth login' to authenticate first.", style="blue")
            return

        from rich.table import Table

        table = Table(title="Authentication Status")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        # Mask token for display
        masked_token = credentials.token[:8] + "..." + credentials.token[-4:]
        table.add_row("Base URL", credentials.base_url)
        table.add_row("Token", masked_token)

        if credentials.username:
            table.add_row("Username", credentials.username)

        # Check token expiry and renewability
        from .security import TokenManager

        token_manager = TokenManager()

        renewable = token_manager.is_token_renewable(credentials.token)
        table.add_row("Renewable", "Yes" if renewable else "No")

        if credentials.token_expiry:
            status_info = token_manager.check_token_expiration(credentials.token_expiry)

            if status_info["status"] == "expired":
                table.add_row("Status", "🔴 Expired", style="red")
            elif status_info["status"] == "expiring":
                days = status_info.get("days", 0)
                table.add_row("Status", f"🟡 Expires in {days} days", style="yellow")
            else:
                days = status_info.get("days", 0)
                table.add_row("Status", f"🟢 Valid ({days} days remaining)", style="green")

            table.add_row("Expires", str(credentials.token_expiry.strftime("%Y-%m-%d %H:%M")))
        else:
            table.add_row("Status", "⚪ Expiry unknown", style="blue")

        console.print(table)

        # Additional suggestions
        if credentials.token_expiry:
            status_info = token_manager.check_token_expiration(credentials.token_expiry)
            if status_info["status"] == "expired":
                console.print("\n💡 [yellow]Your token has expired. Run 'yt auth refresh' to renew it.[/yellow]")
            elif status_info["status"] == "expiring":
                console.print("\n💡 [yellow]Your token is expiring soon. Consider running 'yt auth refresh'.[/yellow]")

    except Exception as e:
        console.print(f"❌ Error checking authentication status: {e}", style="red")
        raise click.ClickException("Failed to check auth status") from e


@main.group()
def config() -> None:
    """CLI configuration."""
    pass


@config.command()
@click.argument("key")
@click.argument("value")
@click.pass_context
def set(ctx: click.Context, key: str, value: str) -> None:
    """Set a configuration value."""
    console = get_console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    try:
        config_manager.set_config(key, value)
        console.print(f"✅ Set {key} = {value}", style="green")
    except Exception as e:
        console.print(f"❌ Error setting configuration: {e}", style="red")
        raise click.ClickException("Configuration set failed") from e


@config.command()
@click.argument("key")
@click.pass_context
def get(ctx: click.Context, key: str) -> None:
    """Get a configuration value."""
    console = get_console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    try:
        value = config_manager.get_config(key)
        if value is not None:
            from rich.table import Table

            table = Table(title="Configuration Value")
            table.add_column("Key", style="cyan", no_wrap=True)
            table.add_column("Value", style="blue")

            # Mask sensitive values
            sensitive_keys = ["token", "password", "secret", "api_key"]
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if value == "[Stored in keyring]":
                    masked_value = value
                elif len(value) > 12:
                    masked_value = value[:8] + "..." + value[-4:]
                else:
                    masked_value = "***"
                from rich.text import Text

                value_text = Text(masked_value, style="yellow")
            else:
                value_text = value

            table.add_row(key, value_text)
            console.print(table)
        else:
            console.print(f"❌ Configuration key '{key}' not found", style="red")
            raise click.ClickException("Configuration key not found")
    except Exception as e:
        console.print(f"❌ Error getting configuration: {e}", style="red")
        raise click.ClickException("Configuration get failed") from e


@config.command("list")
@click.pass_context
def list_config(ctx: click.Context) -> None:
    """List all configuration values."""
    console = get_console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    try:
        config_values = config_manager.list_config()
        if config_values:
            from rich.table import Table
            from rich.text import Text

            table = Table(title="Configuration Values")
            table.add_column("Key", style="cyan", no_wrap=True)
            table.add_column("Value", style="blue")

            for key, value in sorted(config_values.items()):
                # Mask sensitive values
                sensitive_keys = ["token", "password", "secret", "api_key"]
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    # Special handling for placeholder values
                    if value == "[Stored in keyring]":
                        masked_value = value
                    elif len(value) > 12:
                        masked_value = value[:8] + "..." + value[-4:]
                    else:
                        masked_value = "***"
                    value_text = Text(masked_value, style="yellow")
                else:
                    value_text = value

                table.add_row(key, value_text)

            console.print(table)
        else:
            console.print("ℹ️  No configuration values found", style="yellow")
    except Exception as e:
        console.print(f"❌ Error listing configuration: {e}", style="red")
        raise click.ClickException("Configuration list failed") from e


@config.group()
def theme() -> None:
    """Manage themes for YouTrack CLI."""
    pass


@theme.command("list")
@click.pass_context
def list_themes(ctx: click.Context) -> None:
    """List all available themes."""
    from .themes import ThemeManager

    theme_manager = ThemeManager()
    theme_manager.display_themes_table()


@theme.command("current")
@click.pass_context
def current_theme(ctx: click.Context) -> None:
    """Show the current theme."""
    console = get_console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    try:
        current_theme_name = config_manager.get_config("YOUTRACK_THEME") or "default"
        console.print(f"Current theme: [cyan]{current_theme_name}[/cyan]")

        # Show a preview of the current theme
        console.print("\nTheme preview:", style="header")
        console.print("Info message", style="info")
        console.print("Warning message", style="warning")
        console.print("Error message", style="error")
        console.print("Success message", style="success")
        console.print("Highlighted text", style="highlight")

    except Exception as e:
        console.print(f"❌ Error getting current theme: {e}", style="red")
        raise click.ClickException("Failed to get current theme") from e


@theme.command("set")
@click.argument("name")
@click.pass_context
def set_theme(ctx: click.Context, name: str) -> None:
    """Set the current theme."""
    console = get_console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    from .console import get_theme_by_name, set_console_theme
    from .themes import ThemeManager

    try:
        theme_manager = ThemeManager()
        available_themes = theme_manager.list_all_themes()

        if name not in available_themes:
            console.print(f"❌ Theme '{name}' not found", style="error")
            console.print(f"Available themes: {', '.join(sorted(available_themes.keys()))}", style="info")
            raise click.ClickException("Theme not found")

        # Set the theme in config
        config_manager.set_config("YOUTRACK_THEME", name)

        # Apply the theme immediately
        theme = get_theme_by_name(name)
        if theme:
            set_console_theme(theme)

        console.print(f"✅ Theme set to '{name}'", style="success")

        # Show theme preview
        console.print("\nTheme preview:", style="header")
        console.print("Info message", style="info")
        console.print("Warning message", style="warning")
        console.print("Error message", style="error")
        console.print("Success message", style="success")
        console.print("Highlighted text", style="highlight")

    except Exception as e:
        console.print(f"❌ Error setting theme: {e}", style="red")
        raise click.ClickException("Failed to set theme") from e


@theme.command("create")
@click.argument("name")
@click.option("--base", help="Base theme to copy from")
@click.pass_context
def create_theme(ctx: click.Context, name: str, base: Optional[str] = None) -> None:
    """Create a new custom theme interactively."""
    console = get_console()

    from .themes import ThemeManager

    try:
        theme_manager = ThemeManager()

        if base:
            available_themes = theme_manager.list_all_themes()
            if base not in available_themes:
                console.print(f"❌ Base theme '{base}' not found", style="error")
                console.print(f"Available themes: {', '.join(sorted(available_themes.keys()))}", style="info")
                raise click.ClickException("Base theme not found")

        success = theme_manager.create_theme_interactively(name, base)
        if not success:
            raise click.ClickException("Theme creation failed")

    except Exception as e:
        console.print(f"❌ Error creating theme: {e}", style="red")
        raise click.ClickException("Theme creation failed") from e


@theme.command("delete")
@click.argument("name")
@click.option("--force", is_flag=True, help="Delete without confirmation")
@click.pass_context
def delete_theme(ctx: click.Context, name: str, force: bool = False) -> None:
    """Delete a custom theme."""
    console = get_console()

    from rich.prompt import Confirm

    from .themes import ThemeManager

    try:
        theme_manager = ThemeManager()
        available_themes = theme_manager.list_all_themes()

        if name not in available_themes:
            console.print(f"❌ Theme '{name}' not found", style="error")
            raise click.ClickException("Theme not found")

        if available_themes[name] == "built-in":
            console.print(f"❌ Cannot delete built-in theme '{name}'", style="error")
            raise click.ClickException("Cannot delete built-in theme")

        if not force:
            if not Confirm.ask(f"Are you sure you want to delete theme '{name}'?"):
                console.print("Theme deletion cancelled", style="yellow")
                return

        success = theme_manager.delete_custom_theme(name)
        if success:
            console.print(f"✅ Theme '{name}' deleted successfully", style="success")
        else:
            console.print(f"❌ Failed to delete theme '{name}'", style="error")
            raise click.ClickException("Theme deletion failed")

    except Exception as e:
        console.print(f"❌ Error deleting theme: {e}", style="red")
        raise click.ClickException("Theme deletion failed") from e


@theme.command("export")
@click.argument("name")
@click.argument("output_file", required=False)
@click.pass_context
def export_theme(ctx: click.Context, name: str, output_file: Optional[str] = None) -> None:
    """Export a theme to a JSON file."""
    console = get_console()

    from .themes import ThemeManager

    try:
        theme_manager = ThemeManager()
        available_themes = theme_manager.list_all_themes()

        if name not in available_themes:
            console.print(f"❌ Theme '{name}' not found", style="error")
            console.print(f"Available themes: {', '.join(sorted(available_themes.keys()))}", style="info")
            raise click.ClickException("Theme not found")

        success = theme_manager.export_theme(name, output_file)
        if success:
            output = output_file or f"{name}.json"
            console.print(f"✅ Theme '{name}' exported to '{output}'", style="success")
        else:
            console.print(f"❌ Failed to export theme '{name}'", style="error")
            raise click.ClickException("Theme export failed")

    except Exception as e:
        console.print(f"❌ Error exporting theme: {e}", style="red")
        raise click.ClickException("Theme export failed") from e


@theme.command("import")
@click.argument("file_path")
@click.argument("name", required=False)
@click.pass_context
def import_theme(ctx: click.Context, file_path: str, name: Optional[str] = None) -> None:
    """Import a theme from a JSON file."""
    console = get_console()

    from pathlib import Path

    from .themes import ThemeManager

    try:
        if not Path(file_path).exists():
            console.print(f"❌ File '{file_path}' not found", style="error")
            raise click.ClickException("File not found")

        theme_manager = ThemeManager()
        imported_name = theme_manager.import_theme(file_path, name)

        if imported_name:
            console.print(f"✅ Theme imported as '{imported_name}'", style="success")
        else:
            console.print(f"❌ Failed to import theme from '{file_path}'", style="error")
            console.print("Check that the file contains a valid theme definition", style="info")
            raise click.ClickException("Theme import failed")

    except Exception as e:
        console.print(f"❌ Error importing theme: {e}", style="red")
        raise click.ClickException("Theme import failed") from e


@main.group()
def alias() -> None:
    """Manage command aliases (Issue #345)."""
    pass


@alias.command("list")
@click.pass_context
def list_aliases(ctx: click.Context) -> None:
    """List all command aliases (built-in and user-defined)."""
    console = get_console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    try:
        from rich.table import Table

        table = Table(title="Command Aliases")
        table.add_column("Alias", style="cyan", no_wrap=True)
        table.add_column("Command", style="blue")
        table.add_column("Type", style="green")

        # Get built-in aliases from the main command group
        main_group = ctx.find_root().command
        if hasattr(main_group, "aliases"):
            aliases = cast(dict, main_group.aliases)
            for alias_name, command in sorted(aliases.items()):
                table.add_row(alias_name, command, "built-in")

        # Get user-defined aliases
        user_aliases = config_manager.list_aliases()
        for alias_name, command in sorted(user_aliases.items()):
            table.add_row(alias_name, command, "user-defined")

        if table.row_count > 0:
            console.print(table)
        else:
            console.print("ℹ️  No aliases found", style="yellow")
            console.print("💡 Create an alias with: yt alias add <name> <command>", style="dim")

    except Exception as e:
        console.print(f"❌ Error listing aliases: {e}", style="red")
        raise click.ClickException("Alias list failed") from e


@alias.command("add")
@click.argument("name")
@click.argument("command")
@click.pass_context
def add_alias(ctx: click.Context, name: str, command: str) -> None:
    """Add a user-defined alias.

    Examples:
        yt alias add myissues "issues list --assignee me"
        yt alias add bug "issues create --type Bug"
        yt alias add il "issues list"
    """
    console = get_console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    try:
        # Check if alias conflicts with existing command
        main_group = ctx.find_root().command
        if hasattr(main_group, "list_commands") and name in main_group.list_commands(ctx):
            console.print(f"❌ Cannot create alias '{name}': conflicts with existing command", style="red")
            return

        # Check if alias conflicts with built-in alias
        if hasattr(main_group, "aliases"):
            aliases = cast(dict, main_group.aliases)
            if name in aliases:
                console.print(f"❌ Cannot create alias '{name}': conflicts with built-in alias", style="red")
                return

        # Add the alias
        config_manager.set_alias(name, command)

        # Reload aliases in the main group
        if hasattr(main_group, "reload_user_aliases"):
            main_group.reload_user_aliases()

        console.print(f"✅ Alias '{name}' → '{command}' created successfully", style="green")
        console.print("💡 Use 'yt alias list' to see all aliases", style="dim")

    except Exception as e:
        console.print(f"❌ Error creating alias: {e}", style="red")
        raise click.ClickException("Alias creation failed") from e


@alias.command("remove")
@click.argument("name")
@click.pass_context
def remove_alias(ctx: click.Context, name: str) -> None:
    """Remove a user-defined alias."""
    console = get_console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    try:
        # Check if alias exists
        if config_manager.get_alias(name) is None:
            console.print(f"❌ Alias '{name}' not found", style="red")
            return

        # Remove the alias
        config_manager.remove_alias(name)

        # Reload aliases in the main group
        main_group = ctx.find_root().command
        if hasattr(main_group, "reload_user_aliases"):
            main_group.reload_user_aliases()

        console.print(f"✅ Alias '{name}' removed successfully", style="green")

    except Exception as e:
        console.print(f"❌ Error removing alias: {e}", style="red")
        raise click.ClickException("Alias removal failed") from e


@alias.command("show")
@click.argument("name")
@click.pass_context
def show_alias(ctx: click.Context, name: str) -> None:
    """Show what command an alias maps to."""
    console = get_console()
    config_manager = ConfigManager(ctx.obj.get("config"))

    try:
        # Check user-defined aliases first
        user_command = config_manager.get_alias(name)
        if user_command:
            console.print(f"[cyan]{name}[/cyan] → [blue]{user_command}[/blue] [green](user-defined)[/green]")
            return

        # Check built-in aliases
        main_group = ctx.find_root().command
        if hasattr(main_group, "aliases"):
            aliases = cast(dict, main_group.aliases)
            if name in aliases:
                command = aliases[name]
                console.print(f"[cyan]{name}[/cyan] → [blue]{command}[/blue] [green](built-in)[/green]")
                return

        console.print(f"❌ Alias '{name}' not found", style="red")
        console.print("💡 Use 'yt alias list' to see all available aliases", style="dim")

    except Exception as e:
        console.print(f"❌ Error showing alias: {e}", style="red")
        raise click.ClickException("Alias show failed") from e


@main.group()
def admin() -> None:
    """Administrative operations."""
    pass


@main.group()
def security() -> None:
    """Security and audit management."""
    pass


@security.command()
@click.option(
    "--limit",
    "-l",
    type=int,
    default=50,
    help="Number of recent entries to show",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.pass_context
def audit(ctx: click.Context, limit: int, output_format: str) -> None:
    """View command audit log."""
    console = get_console()
    audit_logger = ctx.obj.get("audit_logger") or AuditLogger()

    try:
        entries = audit_logger.get_audit_log(limit=limit)

        if not entries:
            console.print("📋 No audit entries found", style="yellow")
            return

        if output_format == "json":
            import json

            audit_data = [entry.model_dump(mode="json") for entry in entries]
            console.print(json.dumps(audit_data, indent=2, default=str))
        else:
            from rich.table import Table

            table = Table(title=f"Command Audit Log (Last {len(entries)} entries)")
            table.add_column("Timestamp", style="cyan")
            table.add_column("Command", style="yellow")
            table.add_column("Arguments", style="blue")
            table.add_column("User", style="green")
            table.add_column("Status", style="red")

            for entry in entries[-limit:]:
                status = "✅" if entry.success else "❌"
                user = entry.user or "Unknown"
                args_str = " ".join(entry.arguments) if entry.arguments else ""

                table.add_row(
                    entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    entry.command,
                    args_str,
                    user,
                    status,
                )

            console.print(table)

    except Exception as e:
        console.print(f"❌ Error retrieving audit log: {e}", style="red")
        raise click.ClickException("Failed to retrieve audit log") from e


@security.command()
@click.option("--force", is_flag=True, help="Force clear without confirmation")
@click.pass_context
def clear_audit(ctx: click.Context, force: bool) -> None:
    """Clear the command audit log."""
    console = get_console()

    if not force:
        if not click.confirm("Are you sure you want to clear the audit log?"):
            console.print("Operation cancelled", style="yellow")
            return

    try:
        audit_logger = ctx.obj.get("audit_logger") or AuditLogger()
        # Clear by writing empty file
        audit_logger._audit_file.write_text("")
        console.print("✅ Audit log cleared successfully", style="green")
    except Exception as e:
        console.print(f"❌ Error clearing audit log: {e}", style="red")
        raise click.ClickException("Failed to clear audit log") from e


@security.command()
@click.pass_context
def token_status(ctx: click.Context) -> None:
    """Check token expiration status."""
    console = get_console()
    auth_manager = AuthManager(ctx.obj.get("config"))

    try:
        credentials = auth_manager.load_credentials()
        if not credentials:
            format_and_print_error(CommonErrors.no_credentials())
            console.print("Run 'yt auth login' to authenticate first", style="blue")
            return

        from .security import TokenManager

        token_manager = TokenManager()

        if credentials.token_expiry:
            status = token_manager.check_token_expiration(credentials.token_expiry)

            if status["status"] == "expired":
                console.print(f"🔴 {status['message']}", style="red")
            elif status["status"] == "expiring":
                console.print(f"🟡 {status['message']}", style="yellow")
            else:
                days = status.get("days", 0)
                console.print(
                    f"🟢 Token is valid (expires in {days} days)",
                    style="green",
                )
        else:
            # Check if this is a permanent token
            is_renewable = token_manager.is_token_renewable(credentials.token)

            if not is_renewable:  # Permanent token
                console.print("✅ Permanent token active", style="green")
                console.print("This token does not expire", style="dim")
            else:
                console.print("⚪ Token expiration date unknown", style="blue")
                console.print(
                    "Consider updating your token to include expiration information",
                    style="dim",
                )

    except Exception as e:
        console.print(f"❌ Error checking token status: {e}", style="red")
        raise click.ClickException("Failed to check token status") from e


# Admin subcommand groups
@admin.group()
def global_settings() -> None:
    """Manage global YouTrack settings."""
    pass


@global_settings.command(name="get")
@click.option("--name", "-n", help="Specific setting name to retrieve")
@click.pass_context
def get_settings(ctx: click.Context, name: Optional[str]) -> None:
    """Get global settings."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_get_settings() -> None:
        result = await admin_manager.get_global_settings(name)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        settings = result["data"]
        if name:
            # For specific setting requests, the data should be the setting itself
            admin_manager.display_global_settings(settings)
        else:
            admin_manager.display_global_settings(settings)

    asyncio.run(run_get_settings())


@global_settings.command(name="set")
@click.argument("name")
@click.argument("value")
@click.pass_context
def set_setting(ctx: click.Context, name: str, value: str) -> None:
    """Set a global setting."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_set_setting() -> None:
        result = await admin_manager.set_global_setting(name, value)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        console.print(f"[green]Success:[/green] {result['message']}")

    asyncio.run(run_set_setting())


@global_settings.command(name="list")
@click.pass_context
def list_settings(ctx: click.Context) -> None:
    """List all global settings."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_list_settings() -> None:
        result = await admin_manager.get_global_settings()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_global_settings(result["data"])

    asyncio.run(run_list_settings())


@admin.group()
def license() -> None:
    """License management."""
    pass


@license.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """Display license information."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_license_info() -> None:
        result = await admin_manager.get_license_info()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_license_info(result["data"])

    asyncio.run(run_license_info())


@license.command()
@click.pass_context
def usage(ctx: click.Context) -> None:
    """Show license usage statistics."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_license_usage() -> None:
        result = await admin_manager.get_license_usage()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_license_usage(result["data"])

    asyncio.run(run_license_usage())


@admin.group()
def maintenance() -> None:
    """System maintenance operations."""
    pass


@maintenance.command(name="clear-cache")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def clear_cache(ctx: click.Context, force: bool) -> None:
    """Clear system caches."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    if not force:
        console.print("[yellow]Warning:[/yellow] This will clear all system caches.")
        if not click.confirm("Continue?"):
            console.print("Operation cancelled.")
            return

    async def run_clear_cache() -> None:
        result = await admin_manager.clear_caches()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        console.print(f"[green]Success:[/green] {result['message']}")

    asyncio.run(run_clear_cache())


@admin.group()
def health() -> None:
    """System health checks and diagnostics."""
    pass


@health.command()
@click.pass_context
def check(ctx: click.Context) -> None:
    """Run health diagnostics."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_health_check() -> None:
        result = await admin_manager.get_system_health()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_system_health(result["data"])

    asyncio.run(run_health_check())


@admin.group(name="user-groups")
def user_groups() -> None:
    """Manage user groups and permissions."""
    pass


@user_groups.command(name="list")
@click.pass_context
def list_groups(ctx: click.Context) -> None:
    """List all user groups."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_list_groups() -> None:
        result = await admin_manager.list_user_groups()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_user_groups(result["data"])

    asyncio.run(run_list_groups())


@user_groups.command()
@click.argument("name")
@click.option("--description", "-d", help="Group description")
@click.pass_context
def create(ctx: click.Context, name: str, description: Optional[str]) -> None:
    """Create a new user group."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_create_group() -> None:
        result = await admin_manager.create_user_group(name, description)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        console.print(f"[green]Success:[/green] {result['message']}")
        if "data" in result:
            console.print(f"Group ID: {result['data'].get('id', 'N/A')}")

    asyncio.run(run_create_group())


@admin.group()
def fields() -> None:
    """Manage custom fields across projects."""
    pass


@fields.command(name="list")
@click.pass_context
def list_fields(ctx: click.Context) -> None:
    """List all custom fields."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_list_fields() -> None:
        result = await admin_manager.list_custom_fields()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_custom_fields(result["data"])

    asyncio.run(run_list_fields())


@admin.group()
def locale() -> None:
    """Manage YouTrack locale and language settings."""
    pass


@locale.command(name="get")
@click.pass_context
def get_locale(ctx: click.Context) -> None:
    """View current locale settings."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_get_locale() -> None:
        result = await admin_manager.get_locale_settings()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_locale_settings(result["data"])

    asyncio.run(run_get_locale())


@locale.command(name="set")
@click.option(
    "--language",
    "-l",
    required=True,
    help="Locale ID to set (e.g., en_US, de_DE, fr_FR)",
)
@click.pass_context
def set_locale(ctx: click.Context, language: str) -> None:
    """Set system language locale."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_set_locale() -> None:
        result = await admin_manager.set_locale_settings(language)

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        console.print(f"[green]Success:[/green] {result['message']}")

    asyncio.run(run_set_locale())


@locale.command(name="list")
@click.pass_context
def list_locales(ctx: click.Context) -> None:
    """List available locales."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_list_locales() -> None:
        result = await admin_manager.get_available_locales()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_available_locales(result["data"], result.get("message"))

    asyncio.run(run_list_locales())


@admin.group()
def i18n() -> None:
    """Manage internationalization settings (alias for locale)."""
    pass


@i18n.command(name="get")
@click.pass_context
def get_i18n(ctx: click.Context) -> None:
    """View all internationalization settings (same as locale get)."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    async def run_get_i18n() -> None:
        result = await admin_manager.get_locale_settings()

        if result["status"] == "error":
            console.print(f"[red]Error:[/red] {result['message']}")
            return

        admin_manager.display_locale_settings(result["data"])

    asyncio.run(run_get_i18n())


@i18n.command(name="set")
@click.option(
    "--language",
    "-l",
    help="Locale ID to set (e.g., en_US, de_DE, fr_FR)",
)
@click.option(
    "--timezone",
    "-tz",
    help="Timezone to set (Note: Not implemented in this version)",
)
@click.option(
    "--date-format",
    "-df",
    help="Date format to set (Note: Not implemented in this version)",
)
@click.pass_context
def set_i18n(ctx: click.Context, language: Optional[str], timezone: Optional[str], date_format: Optional[str]) -> None:
    """Set internationalization settings."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    if not any([language, timezone, date_format]):
        console.print("[red]Error:[/red] At least one option must be specified.")
        console.print("Use --language to set locale, --timezone for timezone, or --date-format for date format.")
        return

    async def run_set_i18n() -> None:
        if language:
            result = await admin_manager.set_locale_settings(language)
            if result["status"] == "error":
                console.print(f"[red]Error:[/red] {result['message']}")
                return
            console.print(f"[green]Success:[/green] {result['message']}")

        if timezone:
            console.print("[yellow]Note:[/yellow] Timezone setting is not yet implemented.")

        if date_format:
            console.print("[yellow]Note:[/yellow] Date format setting is not yet implemented.")

    asyncio.run(run_set_i18n())


if __name__ == "__main__":
    main()
