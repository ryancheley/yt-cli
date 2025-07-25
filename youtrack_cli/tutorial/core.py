"""Core tutorial engine and base classes."""

import asyncio
import asyncio.subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from rich import box
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from ..console import get_console
from .executor import ClickCommandExecutor


@dataclass
class TutorialStep:
    """Represents a single step in a tutorial."""

    title: str
    description: str
    instructions: List[str]
    command_example: Optional[str] = None
    validation_command: Optional[str] = None
    tips: Optional[List[str]] = None
    execute_action: Optional[Callable] = None
    validation_check: Optional[Callable] = None
    cleanup_action: Optional[Callable] = None
    custom_prompt_choices: Optional[List[str]] = None
    custom_prompt_handler: Optional[Callable] = None


@dataclass
class TutorialProgress:
    """Tracks progress through a tutorial."""

    module_id: str
    current_step: int = 0
    completed_steps: Optional[List[int]] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = []


class TutorialModule(ABC):
    """Base class for tutorial modules."""

    def __init__(self, module_id: str, title: str, description: str):
        self.module_id = module_id
        self.title = title
        self.description = description
        self.steps: List[TutorialStep] = []
        self.console = get_console()

    @abstractmethod
    def create_steps(self) -> List[TutorialStep]:
        """Create and return the tutorial steps."""
        pass

    def add_step(self, step: TutorialStep) -> None:
        """Add a step to this tutorial module."""
        self.steps.append(step)

    def get_steps(self) -> List[TutorialStep]:
        """Get all tutorial steps."""
        if not self.steps:
            self.steps = self.create_steps()
        return self.steps

    def display_intro(self) -> None:
        """Display tutorial introduction."""
        intro_panel = Panel(
            f"[bold blue]{self.title}[/bold blue]\n\n{self.description}",
            title="📚 Tutorial Introduction",
            border_style="blue",
            box=box.ROUNDED,
        )
        self.console.print(intro_panel)
        self.console.print()

    def display_step(self, step: TutorialStep, step_number: int, total_steps: int) -> None:
        """Display a tutorial step."""
        # Step header
        header = f"[bold cyan]Step {step_number}/{total_steps}: {step.title}[/bold cyan]"
        self.console.print(Panel(header, border_style="cyan"))

        # Description
        self.console.print(f"\n[yellow]{step.description}[/yellow]\n")

        # Instructions
        if step.instructions:
            self.console.print("[bold]Instructions:[/bold]")
            for i, instruction in enumerate(step.instructions, 1):
                self.console.print(f"  {i}. {instruction}")
            self.console.print()

        # Command example with enhanced visual indicators
        if step.command_example:
            self.console.print("[bold]Example command:[/bold]")
            command_panel = Panel(
                f"[green]{step.command_example}[/green]",
                title="[bold cyan]🚀 Executable Command[/bold cyan]",
                border_style="cyan",
                padding=(0, 1),
            )
            self.console.print(command_panel)
            self.console.print("  [dim]💡 Press [bold]Enter[/bold] to execute this command directly![/dim]\n")

        # Tips
        if step.tips:
            self.console.print("[bold]💡 Tips:[/bold]")
            for tip in step.tips:
                self.console.print(f"  • {tip}")
            self.console.print()


class TutorialEngine:
    """Main tutorial engine for running interactive tutorials."""

    def __init__(self, progress_tracker, config_manager=None):
        self.console = get_console()
        self.progress_tracker = progress_tracker
        self.modules: Dict[str, TutorialModule] = {}
        self.command_executor = ClickCommandExecutor(config_manager)

    def register_module(self, module: TutorialModule) -> None:
        """Register a tutorial module."""
        self.modules[module.module_id] = module

    def list_modules(self) -> List[TutorialModule]:
        """Get all registered tutorial modules."""
        return list(self.modules.values())

    def get_module(self, module_id: str) -> Optional[TutorialModule]:
        """Get a specific tutorial module."""
        return self.modules.get(module_id)

    def display_module_list(self) -> None:
        """Display available tutorial modules."""
        table = Table(title="📚 Available Tutorials", box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="bold blue")
        table.add_column("Description", style="yellow")
        table.add_column("Progress", style="green")

        for module in self.modules.values():
            progress = self.progress_tracker.get_progress(module.module_id)
            if progress and progress.completed_at:
                progress_text = "✅ Completed"
                progress_style = "green"
            elif progress and progress.current_step > 0:
                total_steps = len(module.get_steps())
                progress_text = f"📖 {progress.current_step}/{total_steps}"
                progress_style = "yellow"
            else:
                progress_text = "⏸️  Not started"
                progress_style = "dim"

            table.add_row(
                module.module_id,
                module.title,
                module.description,
                f"[{progress_style}]{progress_text}[/{progress_style}]",
            )

        self.console.print(table)

    async def run_module(self, module_id: str, start_step: Optional[int] = None) -> bool:
        """Run a specific tutorial module."""
        module = self.get_module(module_id)
        if not module:
            self.console.print(f"[red]❌ Tutorial module '{module_id}' not found.[/red]")
            return False

        steps = module.get_steps()
        if not steps:
            self.console.print(f"[red]❌ No steps found for tutorial '{module_id}'.[/red]")
            return False

        # Get or create progress
        progress = self.progress_tracker.get_progress(module_id)
        if not progress:
            progress = TutorialProgress(module_id=module_id)
            self.progress_tracker.save_progress(progress)

        # Determine starting step
        if start_step is not None:
            current_step = max(0, min(start_step - 1, len(steps) - 1))
        else:
            current_step = progress.current_step

        # Display tutorial introduction
        module.display_intro()

        # Confirm start
        if not Confirm.ask("Ready to start this tutorial?"):
            self.console.print("[yellow]Tutorial cancelled.[/yellow]")
            return False

        # Run tutorial steps
        total_steps = len(steps)

        while current_step < total_steps:
            step = steps[current_step]
            step_number = current_step + 1

            # Display step
            self.console.print("\n" + "=" * 60 + "\n")
            module.display_step(step, step_number, total_steps)

            # Execute step action if present
            execution_success = True
            if step.execute_action:
                execution_success = await self._execute_step_action(step, step_number)

            # Wait for user to proceed
            if execution_success:
                if step.custom_prompt_choices:
                    # Use custom prompt choices for this step
                    action = Prompt.ask(
                        "What would you like to do with your YouTrack instance?",
                        choices=step.custom_prompt_choices,
                        default=step.custom_prompt_choices[0] if step.custom_prompt_choices else "next",
                    )
                else:
                    # Use default choices with shortcuts
                    choices = ["next", "n", "repeat", "r", "skip", "s", "quit", "q"]
                    if step.command_example:
                        choices.extend(["execute", "e"])

                    prompt_text = "What would you like to do? ["
                    prompt_options = ["(n)ext", "(r)epeat", "(s)kip", "(q)uit"]
                    if step.command_example:
                        prompt_options.append("(e)xecute")
                    prompt_text += "/".join(prompt_options) + "] (Enter=next)"

                    action = Prompt.ask(prompt_text, choices=choices, default="next")

                    # Map shortcuts to full actions
                    action_map = {"n": "next", "r": "repeat", "s": "skip", "q": "quit", "e": "execute"}
                    action = action_map.get(action.lower(), action.lower())
            else:
                action = Prompt.ask(
                    "Step execution failed. What would you like to do? [(r)etry/(s)kip/(q)uit] (Enter=retry)",
                    choices=["retry", "r", "skip", "s", "quit", "q"],
                    default="retry",
                )
                # Map shortcuts to full actions
                action_map = {"r": "retry", "s": "skip", "q": "quit"}
                action = action_map.get(action.lower(), action.lower())

            if action == "quit":
                self.console.print("[yellow]Tutorial paused. You can resume later with:[/yellow]")
                self.console.print(f"[blue]yt tutorial run {module_id} --step {step_number}[/blue]")
                # Save progress
                progress.current_step = current_step
                self.progress_tracker.save_progress(progress)
                return False

            if action == "repeat" or action == "retry":
                continue  # Stay on current step

            if action == "skip":
                current_step += 1

            elif action == "next":
                # Mark step as completed
                if progress.completed_steps and current_step not in progress.completed_steps:
                    progress.completed_steps.append(current_step)
                current_step += 1

            elif action == "execute" and step.command_example:
                # Execute the command example using enhanced executor
                success = await self.command_executor.execute_command(step.command_example)
                if success:
                    self.console.print(
                        "[green]✓ Command executed successfully! You can now proceed to the next step.[/green]"
                    )
                else:
                    self.console.print(
                        "[yellow]⚠️  Command execution failed. You can still continue with the tutorial.[/yellow]"
                    )
                # Stay on current step after execution
                continue

            elif step.custom_prompt_handler and step.custom_prompt_choices and action in step.custom_prompt_choices:
                # Handle custom action
                try:
                    result = await step.custom_prompt_handler(action)
                    if result:
                        # Action completed successfully, move to next step
                        if progress.completed_steps and current_step not in progress.completed_steps:
                            progress.completed_steps.append(current_step)
                        current_step += 1
                    else:
                        # Action failed or cancelled, stay on current step
                        continue
                except Exception as e:
                    self.console.print(f"[red]Action failed: {e}[/red]")
                    continue

            # Save progress
            progress.current_step = current_step
            self.progress_tracker.save_progress(progress)

        # Tutorial completed
        self.display_completion(module)
        progress.completed_at = self.progress_tracker.get_current_timestamp()
        self.progress_tracker.save_progress(progress)
        return True

    async def _execute_step_action(self, step: TutorialStep, step_number: int) -> bool:
        """Execute a step's action and validate its success."""
        try:
            self.console.print(f"\n[blue]⚡ Executing step {step_number} action...[/blue]")

            # Execute the step action
            if step.execute_action:
                await step.execute_action()

            # Validate the action if validation check is provided
            if step.validation_check:
                if step.validation_check():
                    self.console.print("[green]✓ Step executed successfully![/green]")
                    return True
                self.console.print("[red]✗ Step execution validation failed![/red]")
                return False
            self.console.print("[green]✓ Step executed successfully![/green]")
            return True

        except Exception as e:
            self.console.print(f"[red]✗ Step execution failed: {e}[/red]")
            if hasattr(e, "__cause__") and e.__cause__:
                self.console.print(f"[red]  Caused by: {e.__cause__}[/red]")
            return False

    def display_completion(self, module: TutorialModule) -> None:
        """Display tutorial completion message."""
        completion_panel = Panel(
            f"[bold green]🎉 Congratulations![/bold green]\n\n"
            f"You have successfully completed the [cyan]{module.title}[/cyan] tutorial!\n\n"
            f"[dim]You can review this tutorial anytime or explore other tutorials.[/dim]",
            title="✅ Tutorial Complete",
            border_style="green",
            box=box.ROUNDED,
        )
        self.console.print("\n")
        self.console.print(completion_panel)

    async def _execute_command(self, command: str) -> None:
        """Execute a command and display its output.

        Args:
            command: The command to execute.
        """
        self.console.print(f"\n[blue]⚡ Executing command:[/blue] [green]{command}[/green]")

        try:
            # Show the command in a syntax panel
            syntax = Syntax(command, "bash", theme="monokai", line_numbers=False)
            self.console.print(Panel(syntax, title="Command", border_style="blue"))

            # Execute the command
            process = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, shell=True
            )

            stdout, stderr = await process.communicate()

            # Display output
            if stdout:
                output_text = stdout.decode().strip()
                if output_text:
                    self.console.print(
                        Panel(output_text, title="[green]Output[/green]", border_style="green", expand=False)
                    )

            if stderr:
                error_text = stderr.decode().strip()
                if error_text:
                    self.console.print(
                        Panel(error_text, title="[red]Error Output[/red]", border_style="red", expand=False)
                    )

            if process.returncode == 0:
                self.console.print("[green]✓ Command executed successfully![/green]\n")
            else:
                self.console.print(f"[red]✗ Command failed with exit code {process.returncode}[/red]\n")

        except Exception as e:
            self.console.print(f"[red]✗ Failed to execute command: {e}[/red]\n")

    def display_welcome(self) -> None:
        """Display welcome message for tutorial system."""
        welcome_text = Text()
        welcome_text.append("Welcome to ", style="blue")
        welcome_text.append("YouTrack CLI", style="bold cyan")
        welcome_text.append(" Interactive Tutorials!", style="blue")

        welcome_panel = Panel(
            welcome_text.plain + "\n\n" + "Learn YouTrack CLI through guided, hands-on tutorials.\n"
            "Each tutorial covers essential workflows and best practices.\n\n"
            "💡 Pro tip: You can pause any tutorial and resume later!",
            title="🎓 Tutorial System",
            border_style="blue",
            box=box.ROUNDED,
        )
        self.console.print(welcome_panel)
        self.console.print()
