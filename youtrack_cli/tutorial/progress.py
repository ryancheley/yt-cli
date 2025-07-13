"""Progress tracking system for tutorials."""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .core import TutorialProgress


class ProgressTracker:
    """Tracks and persists tutorial progress."""

    def __init__(self, config_dir: Optional[str] = None):
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".config" / "youtrack-cli"

        self.progress_file = self.config_dir / "tutorial_progress.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._progress_cache: Dict[str, TutorialProgress] = {}
        self._load_progress()

    def _load_progress(self) -> None:
        """Load progress from file."""
        if not self.progress_file.exists():
            self._progress_cache = {}
            return

        try:
            with open(self.progress_file) as f:
                data = json.load(f)

            self._progress_cache = {}
            for module_id, progress_data in data.items():
                progress = TutorialProgress(
                    module_id=progress_data["module_id"],
                    current_step=progress_data.get("current_step", 0),
                    completed_steps=progress_data.get("completed_steps", []),
                    started_at=progress_data.get("started_at"),
                    completed_at=progress_data.get("completed_at"),
                )
                self._progress_cache[module_id] = progress

        except (json.JSONDecodeError, KeyError, OSError):
            # If file is corrupted, start fresh
            self._progress_cache = {}

    def _save_progress(self) -> None:
        """Save progress to file."""
        try:
            data = {}
            for module_id, progress in self._progress_cache.items():
                data[module_id] = asdict(progress)

            with open(self.progress_file, "w") as f:
                json.dump(data, f, indent=2)

        except OSError:
            # Handle write errors gracefully
            pass

    def get_progress(self, module_id: str) -> Optional[TutorialProgress]:
        """Get progress for a specific module."""
        return self._progress_cache.get(module_id)

    def save_progress(self, progress: TutorialProgress) -> None:
        """Save progress for a module."""
        if not progress.started_at:
            progress.started_at = self.get_current_timestamp()

        self._progress_cache[progress.module_id] = progress
        self._save_progress()

    def reset_progress(self, module_id: str) -> bool:
        """Reset progress for a specific module."""
        if module_id in self._progress_cache:
            del self._progress_cache[module_id]
            self._save_progress()
            return True
        return False

    def get_all_progress(self) -> Dict[str, TutorialProgress]:
        """Get progress for all modules."""
        return self._progress_cache.copy()

    def get_completed_modules(self) -> List[str]:
        """Get list of completed module IDs."""
        return [module_id for module_id, progress in self._progress_cache.items() if progress.completed_at is not None]

    def get_in_progress_modules(self) -> List[str]:
        """Get list of modules that are in progress."""
        return [
            module_id
            for module_id, progress in self._progress_cache.items()
            if progress.current_step > 0 and progress.completed_at is None
        ]

    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp as ISO string."""
        return datetime.now().isoformat()

    def get_completion_stats(self) -> Dict[str, int]:
        """Get completion statistics."""
        completed = len(self.get_completed_modules())
        in_progress = len(self.get_in_progress_modules())
        total = len(self._progress_cache)

        return {
            "completed": completed,
            "in_progress": in_progress,
            "not_started": max(0, total - completed - in_progress),
            "total": total,
        }
