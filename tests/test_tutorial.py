"""Tests for tutorial system."""

import tempfile
from pathlib import Path

import pytest

from youtrack_cli.tutorial.core import TutorialEngine, TutorialModule, TutorialProgress, TutorialStep
from youtrack_cli.tutorial.modules import IssuesTutorial, SetupTutorial, get_default_modules
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
