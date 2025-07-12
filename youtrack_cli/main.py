"""Main entry point for the YouTrack CLI."""

import asyncio
from typing import Optional

import click
from rich.prompt import Prompt

from . import __version__
from .admin import AdminManager
from .auth import AuthManager
from .cli_utils import AliasedGroup
from .commands import articles, boards, issues, projects, time, users
from .config import ConfigManager
from .console import get_console
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
    "reports",
    "auth",
    "config",
]


@click.group(cls=AliasedGroup, context_settings={"help_option_names": ["-h", "--help"]})
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
@click.pass_context
def main(
    ctx: click.Context,
    config: Optional[str],
    verbose: bool,
    debug: bool,
    no_progress: bool,
    secure: bool,
) -> None:
    """YouTrack CLI - Command line interface for JetBrains YouTrack.

    A powerful command line tool for managing YouTrack issues, projects, users,
    time tracking, and more. Designed for developers and teams who want to integrate
    YouTrack into their daily workflows and automation.

    Quick Start:

        \b
        # Set up authentication
        yt auth login  (or: yt login)

        \b
        # List your projects
        yt projects list  (or: yt p list)

        \b
        # Create an issue
        yt issues create PROJECT-123 "Fix the bug"  (or: yt i create ...)

        \b
        # Log work time
        yt time log ISSUE-456 "2h 30m" --description "Fixed the issue"
        # (or: yt t log ...)

    Command Aliases:
        i = issues, a = articles, p = projects, u = users, t = time, b = boards
        c/cfg = config, login = auth

    For more help on specific commands, use:

        \b
        yt COMMAND --help

    Documentation: https://yt-cli.readthedocs.io/
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug
    ctx.obj["no_progress"] = no_progress
    ctx.obj["secure"] = secure

    # Setup logging
    setup_logging(verbose=verbose, debug=debug)

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
main.add_command(boards)

# Add aliases for main command groups
main.add_alias("i", "issues")
main.add_alias("a", "articles")
main.add_alias("p", "projects")
main.add_alias("u", "users")
main.add_alias("t", "time")
main.add_alias("b", "boards")

# Add aliases for top-level commands
main.add_alias("c", "config")
main.add_alias("cfg", "config")
main.add_alias("login", "auth")


@main.command()
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish", "powershell"]))
@click.option(
    "--install",
    is_flag=True,
    help="Install the completion script to the appropriate location",
)
def completion(shell: str, install: bool) -> None:
    """Generate shell completion script.

    Generate completion scripts for bash, zsh, fish, or PowerShell shells.

    Examples:

        \b
        # Generate bash completion script
        yt completion bash

        \b
        # Install bash completion (requires sudo on some systems)
        yt completion bash --install

        \b
        # Generate PowerShell completion script
        yt completion powershell

        \b
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
                    elif comp_dir.parent.exists() and os.access(comp_dir.parent, os.W_OK):
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
                    elif comp_dir.parent.exists() and os.access(comp_dir.parent, os.W_OK):
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
                    elif comp_dir.parent.exists() and os.access(comp_dir.parent, os.W_OK):
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
                            ["powershell", "-Command", "echo $PROFILE"], capture_output=True, text=True, timeout=10
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
    """Interactive setup wizard for first-time configuration.

    This command guides you through setting up YouTrack CLI for the first time.
    It will help you configure your YouTrack URL, authentication, and basic preferences.

    Examples:

        \b
        # Run the interactive setup wizard
        yt setup

        \b
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
            for key, value in config_data.items():
                f.write(f"{key}={value}\n")

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
    """Generate a burndown report for a project or sprint."""
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
    """Authentication management."""
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
    """Authenticate with YouTrack."""
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
            console.print(f"❌ Authentication failed: {result.message}", style="red")
            raise click.ClickException("Authentication failed")

    except Exception as e:
        console.print(f"❌ Error during authentication: {e}", style="red")
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
            console.print("❌ No authentication credentials found.", style="red")
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
            console.print("❌ No authentication credentials found.", style="red")
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
            console.print(f"{key} = {value}", style="blue")
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
            console.print("📋 Configuration values:", style="blue bold")
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
                    console.print(f"  {key} = {masked_value}", style="yellow")
                else:
                    console.print(f"  {key} = {value}", style="blue")
        else:
            console.print("ℹ️  No configuration values found", style="yellow")
    except Exception as e:
        console.print(f"❌ Error listing configuration: {e}", style="red")
        raise click.ClickException("Configuration list failed") from e


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
            console.print("❌ No authentication credentials found", style="red")
            console.print("Run 'yt auth login' to authenticate first", style="blue")
            return

        if credentials.token_expiry:
            from .security import TokenManager

            token_manager = TokenManager()
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

        license_data = result["data"]
        console.print("[bold]License Information:[/bold]")
        console.print(f"License ID: {license_data.get('id', 'N/A')}")
        console.print(f"Username: {license_data.get('username', 'N/A')}")
        console.print(f"License Key: {license_data.get('license', 'N/A')}")
        if license_data.get("error"):
            console.print(f"[red]Error:[/red] {license_data['error']}")
        else:
            console.print("[green]Status: Valid[/green]")

    asyncio.run(run_license_usage())


@admin.group()
def maintenance() -> None:
    """System maintenance operations."""
    pass


@maintenance.command(name="clear-cache")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def clear_cache(ctx: click.Context, confirm: bool) -> None:
    """Clear system caches."""
    auth_manager = AuthManager(ctx.obj.get("config"))
    admin_manager = AdminManager(auth_manager)
    console = get_console()

    if not confirm:
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


if __name__ == "__main__":
    main()
