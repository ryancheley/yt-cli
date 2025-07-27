"""Tests for tutorial commands."""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import click
import pytest
from click.testing import CliRunner

from youtrack_cli.commands.tutorial import feedback, list, progress, reset, run, tutorial


# Get the actual tutorial module for cross-version compatibility
def get_tutorial_module():
    """Get the actual tutorial module (not the Click group) for patching."""
    return sys.modules["youtrack_cli.commands.tutorial"]


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


@pytest.fixture
def mock_ctx():
    """Create a mock Click context."""
    ctx = MagicMock()
    ctx.obj = {"config": {"base_url": "http://localhost:8080"}}
    return ctx


@pytest.fixture
def mock_progress_tracker():
    """Create a mock progress tracker."""
    tracker = MagicMock()
    tracker.get_completion_stats.return_value = {"completed": 2, "in_progress": 1, "not_started": 3}
    tracker.get_all_progress.return_value = {
        "setup": MagicMock(current_step=0, started_at="2023-01-01T10:00:00Z", completed_at="2023-01-01T10:30:00Z"),
        "issues": MagicMock(current_step=3, started_at="2023-01-02T09:00:00Z", completed_at=None),
    }
    return tracker


@pytest.fixture
def mock_tutorial_engine():
    """Create a mock tutorial engine."""
    engine = MagicMock()

    # Mock modules
    setup_module = MagicMock()
    setup_module.title = "Getting Started"
    setup_module.get_steps.return_value = [MagicMock(), MagicMock(), MagicMock()]

    issues_module = MagicMock()
    issues_module.title = "Working with Issues"
    issues_module.get_steps.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]

    engine.get_module.side_effect = lambda mid: {"setup": setup_module, "issues": issues_module}.get(mid)

    engine.run_module = AsyncMock(return_value=True)

    return engine


@pytest.fixture
def mock_default_modules():
    """Create mock default modules."""
    setup_module = MagicMock()
    setup_module.module_id = "setup"
    setup_module.title = "Getting Started"

    issues_module = MagicMock()
    issues_module.module_id = "issues"
    issues_module.title = "Working with Issues"

    return [setup_module, issues_module]


class TestTutorialGroup:
    """Test the main tutorial command group."""

    def test_tutorial_group_exists(self):
        """Test that tutorial group is properly configured."""
        assert isinstance(tutorial, click.Group)
        assert tutorial.name == "tutorial"

    def test_tutorial_group_has_commands(self):
        """Test that tutorial group has expected commands."""
        expected_commands = ["list", "run", "reset", "progress", "feedback"]

        # Test that we can get each command without error
        for cmd in expected_commands:
            assert tutorial.get_command(None, cmd) is not None

    def test_tutorial_group_has_aliases(self):
        """Test that tutorial group has aliases."""
        # Check if aliases are configured
        assert hasattr(tutorial, "aliases")


class TestListCommand:
    """Test the tutorial list command."""

    def test_list_command_basic(
        self,
        runner,
        mock_default_modules,
        mock_tutorial_engine,
        mock_progress_tracker,
    ):
        """Test basic list command functionality."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch.object(tutorial_module, "TutorialEngine") as mock_engine_class,
            patch.object(tutorial_module, "get_default_modules") as mock_get_modules,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_engine_class.return_value = mock_tutorial_engine
            mock_get_modules.return_value = mock_default_modules

            # Run command
            result = runner.invoke(list, [], obj={"config": {}})

            # Assertions
            assert result.exit_code == 0
            mock_tutorial_engine.display_welcome.assert_called_once()
            mock_tutorial_engine.display_module_list.assert_called_once()
            mock_tutorial_engine.register_module.assert_called()

    def test_list_command_with_progress(
        self,
        runner,
        mock_default_modules,
        mock_tutorial_engine,
        mock_progress_tracker,
    ):
        """Test list command with progress display."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch.object(tutorial_module, "TutorialEngine") as mock_engine_class,
            patch.object(tutorial_module, "get_default_modules") as mock_get_modules,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_engine_class.return_value = mock_tutorial_engine
            mock_get_modules.return_value = mock_default_modules

            # Run command
            result = runner.invoke(list, ["--show-progress"], obj={"config": {}})

            # Assertions
            assert result.exit_code == 0
            mock_progress_tracker.get_completion_stats.assert_called_once()
            # Check that progress stats are displayed
            assert "Progress Summary" in result.output
            assert "Completed: 2" in result.output
            assert "In Progress: 1" in result.output
            assert "Not Started: 3" in result.output


class TestRunCommand:
    """Test the tutorial run command."""

    def test_run_command_success(
        self,
        runner,
        mock_default_modules,
        mock_tutorial_engine,
        mock_progress_tracker,
    ):
        """Test successful tutorial run."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch.object(tutorial_module, "TutorialEngine") as mock_engine_class,
            patch.object(tutorial_module, "get_default_modules") as mock_get_modules,
            patch("asyncio.run") as mock_asyncio,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_engine_class.return_value = mock_tutorial_engine
            mock_get_modules.return_value = mock_default_modules

            # Mock async run to call the coroutine
            def run_coro(coro):
                # Simulate successful completion
                return None

            mock_asyncio.side_effect = run_coro

            # Run command
            result = runner.invoke(run, ["setup"], obj={"config": {}})

            # Assertions
            assert result.exit_code == 0
            mock_tutorial_engine.get_module.assert_called_with("setup")
            mock_asyncio.assert_called_once()

    def test_run_command_module_not_found(
        self,
        runner,
        mock_default_modules,
        mock_tutorial_engine,
        mock_progress_tracker,
    ):
        """Test run command with non-existent module."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch.object(tutorial_module, "TutorialEngine") as mock_engine_class,
            patch.object(tutorial_module, "get_default_modules") as mock_get_modules,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_engine_class.return_value = mock_tutorial_engine
            mock_get_modules.return_value = mock_default_modules

            # Make get_module return None for non-existent module
            mock_tutorial_engine.get_module.return_value = None

            # Run command
            result = runner.invoke(run, ["nonexistent"], obj={"config": {}})

            # Assertions
            assert result.exit_code == 0
            assert "Tutorial 'nonexistent' not found" in result.output
            assert "Available tutorials:" in result.output
            mock_tutorial_engine.display_module_list.assert_called_once()

    def test_run_command_with_reset(
        self,
        runner,
        mock_default_modules,
        mock_tutorial_engine,
        mock_progress_tracker,
    ):
        """Test run command with reset option."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch.object(tutorial_module, "TutorialEngine") as mock_engine_class,
            patch.object(tutorial_module, "get_default_modules") as mock_get_modules,
            patch("rich.prompt.Confirm.ask") as mock_confirm,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_engine_class.return_value = mock_tutorial_engine
            mock_get_modules.return_value = mock_default_modules
            mock_confirm.return_value = True

            # Run command
            result = runner.invoke(run, ["setup", "--reset"], obj={"config": {}})

            # Assertions
            assert result.exit_code == 0
            mock_confirm.assert_called_once_with("Reset progress for 'setup' tutorial?")
            mock_progress_tracker.reset_progress.assert_called_once_with("setup")
            assert "Progress reset for 'setup' tutorial" in result.output

    def test_run_command_reset_cancelled(
        self,
        runner,
        mock_default_modules,
        mock_tutorial_engine,
        mock_progress_tracker,
    ):
        """Test run command with reset cancelled."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch.object(tutorial_module, "TutorialEngine") as mock_engine_class,
            patch.object(tutorial_module, "get_default_modules") as mock_get_modules,
            patch("rich.prompt.Confirm.ask") as mock_confirm,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_engine_class.return_value = mock_tutorial_engine
            mock_get_modules.return_value = mock_default_modules
            mock_confirm.return_value = False

            # Run command
            result = runner.invoke(run, ["setup", "--reset"], obj={"config": {}})

            # Assertions
            assert result.exit_code == 0
            mock_confirm.assert_called_once_with("Reset progress for 'setup' tutorial?")
            mock_progress_tracker.reset_progress.assert_not_called()
            assert "Reset cancelled" in result.output

    def test_run_command_with_step(
        self,
        runner,
        mock_default_modules,
        mock_tutorial_engine,
        mock_progress_tracker,
    ):
        """Test run command with specific step."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch.object(tutorial_module, "TutorialEngine") as mock_engine_class,
            patch.object(tutorial_module, "get_default_modules") as mock_get_modules,
            patch("asyncio.run") as mock_asyncio,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_engine_class.return_value = mock_tutorial_engine
            mock_get_modules.return_value = mock_default_modules
            mock_asyncio.return_value = None

            # Run command
            result = runner.invoke(run, ["setup", "--step", "3"], obj={"config": {}})

            # Assertions
            assert result.exit_code == 0
            mock_asyncio.assert_called_once()


class TestResetCommand:
    """Test the tutorial reset command."""

    def test_reset_specific_module(self, runner, mock_progress_tracker):
        """Test resetting specific module."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch("rich.prompt.Confirm.ask") as mock_confirm,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_confirm.return_value = True
            mock_progress_tracker.reset_progress.return_value = True

            # Run command
            result = runner.invoke(reset, ["setup"])

            # Assertions
            assert result.exit_code == 0
            mock_confirm.assert_called_once_with("Reset progress for 'setup' tutorial?")
            mock_progress_tracker.reset_progress.assert_called_once_with("setup")
            assert "Progress reset for 'setup' tutorial" in result.output

    def test_reset_all_modules(self, runner, mock_progress_tracker):
        """Test resetting all modules."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch("rich.prompt.Confirm.ask") as mock_confirm,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_confirm.return_value = True
            mock_progress_tracker.get_all_progress.return_value = {"setup": MagicMock(), "issues": MagicMock()}

            # Run command
            result = runner.invoke(reset, ["--all"])

            # Assertions
            assert result.exit_code == 0
            mock_confirm.assert_called_once_with("Reset progress for ALL tutorials?")
            assert mock_progress_tracker.reset_progress.call_count == 2
            assert "All tutorial progress has been reset" in result.output

    def test_reset_cancelled(self, runner, mock_progress_tracker):
        """Test reset cancelled."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch("rich.prompt.Confirm.ask") as mock_confirm,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_confirm.return_value = False

            # Run command
            result = runner.invoke(reset, ["setup"])

            # Assertions
            assert result.exit_code == 0
            mock_confirm.assert_called_once_with("Reset progress for 'setup' tutorial?")
            mock_progress_tracker.reset_progress.assert_not_called()
            assert "Reset cancelled" in result.output

    def test_reset_no_module_specified(self, runner, mock_progress_tracker):
        """Test reset with no module specified."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker

            # Run command
            result = runner.invoke(reset, [])

            # Assertions
            assert result.exit_code == 0
            assert "Please specify a module ID or use --all" in result.output
            assert "Usage: yt tutorial reset MODULE_ID" in result.output

    def test_reset_module_not_found(self, runner, mock_progress_tracker):
        """Test reset with module that has no progress."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch("rich.prompt.Confirm.ask") as mock_confirm,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_confirm.return_value = True
            mock_progress_tracker.reset_progress.return_value = False

            # Run command
            result = runner.invoke(reset, ["nonexistent"])

            # Assertions
            assert result.exit_code == 0
            mock_confirm.assert_called_once_with("Reset progress for 'nonexistent' tutorial?")
            mock_progress_tracker.reset_progress.assert_called_once_with("nonexistent")
            assert "No progress found for 'nonexistent' tutorial" in result.output


class TestProgressCommand:
    """Test the tutorial progress command."""

    def test_progress_command_with_data(
        self,
        runner,
        mock_default_modules,
        mock_tutorial_engine,
        mock_progress_tracker,
    ):
        """Test progress command with existing data."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch.object(tutorial_module, "TutorialEngine") as mock_engine_class,
            patch.object(tutorial_module, "get_default_modules") as mock_get_modules,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_engine_class.return_value = mock_tutorial_engine
            mock_get_modules.return_value = mock_default_modules

            # Run command
            result = runner.invoke(progress, [], obj={"config": {}})

            # Assertions
            assert result.exit_code == 0
            mock_progress_tracker.get_all_progress.assert_called_once()
            mock_progress_tracker.get_completion_stats.assert_called_once()
            # Should display table and summary
            assert "Tutorial Progress Details" in result.output
            assert "Summary:" in result.output

    def test_progress_command_no_data(self, runner):
        """Test progress command with no existing data."""
        # Setup mocks using cross-version compatible approach
        mock_console_instance = MagicMock()
        mock_progress_tracker = MagicMock()
        mock_progress_tracker.get_all_progress.return_value = {}

        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
        ):
            mock_console.return_value = mock_console_instance
            mock_tracker_class.return_value = mock_progress_tracker

            # Run command
            result = runner.invoke(progress, [], obj={"config": {}})

            # Assertions
            assert result.exit_code == 0
            assert "No tutorial progress found" in result.output
            assert "Start a tutorial with:" in result.output


class TestFeedbackCommand:
    """Test the tutorial feedback command."""

    @patch("youtrack_cli.console.get_console")
    def test_feedback_command(self, mock_console, runner):
        """Test feedback command functionality."""
        # Setup mocks
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        # Run command
        result = runner.invoke(feedback, [])

        # Assertions
        assert result.exit_code == 0
        assert "We'd love your feedback!" in result.output
        assert "Report issues:" in result.output
        assert "github.com/ryancheley/yt-cli/issues" in result.output
        assert "Tutorial Feedback" in result.output


class TestTutorialIntegration:
    """Test tutorial command integration scenarios."""

    def test_tutorial_workflow(
        self,
        runner,
        mock_default_modules,
        mock_tutorial_engine,
        mock_progress_tracker,
    ):
        """Test a complete tutorial workflow."""
        tutorial_module = get_tutorial_module()

        with (
            patch("youtrack_cli.console.get_console") as mock_console,
            patch.object(tutorial_module, "ProgressTracker") as mock_tracker_class,
            patch.object(tutorial_module, "TutorialEngine") as mock_engine_class,
            patch.object(tutorial_module, "get_default_modules") as mock_get_modules,
        ):
            # Setup mocks
            mock_console_instance = MagicMock()
            mock_console.return_value = mock_console_instance

            mock_tracker_class.return_value = mock_progress_tracker
            mock_engine_class.return_value = mock_tutorial_engine
            mock_get_modules.return_value = mock_default_modules

            # Test list command first
            result1 = runner.invoke(list, [], obj={"config": {}})
            assert result1.exit_code == 0

            # Test progress command
            result2 = runner.invoke(progress, [], obj={"config": {}})
            assert result2.exit_code == 0

            # Test feedback command
            result3 = runner.invoke(feedback, [])
            assert result3.exit_code == 0

            # Verify all commands executed successfully
            assert all(result.exit_code == 0 for result in [result1, result2, result3])

    def test_tutorial_command_help(self, runner):
        """Test tutorial command help output."""
        result = runner.invoke(tutorial, ["--help"])

        assert result.exit_code == 0
        assert "Interactive tutorials for learning YouTrack CLI" in result.output
        assert "setup" in result.output
        assert "issues" in result.output
        assert "projects" in result.output
        assert "time" in result.output

    def test_tutorial_subcommand_help(self, runner):
        """Test tutorial subcommand help."""
        # Test list help
        result1 = runner.invoke(list, ["--help"])
        assert result1.exit_code == 0
        assert "List available tutorials" in result1.output

        # Test run help
        result2 = runner.invoke(run, ["--help"])
        assert result2.exit_code == 0
        assert "Run a specific tutorial module" in result2.output

        # Test reset help
        result3 = runner.invoke(reset, ["--help"])
        assert result3.exit_code == 0
        assert "Reset tutorial progress" in result3.output
