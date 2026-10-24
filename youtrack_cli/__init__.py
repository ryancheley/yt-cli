"""YouTrack CLI - Command line interface for JetBrains YouTrack."""

from typing import Any

__all__ = ["__version__"]

try:
    from importlib.metadata import version

    __version__ = version("youtrack-cli")
    if __version__ is None:
        raise RuntimeError("Version is None")
except Exception:
    # Fallback to reading from pyproject.toml
    try:
        import tomllib
        from pathlib import Path

        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data: dict[str, Any] = tomllib.load(f)
            __version__ = data["project"]["version"]
        else:
            __version__ = "unknown"
    except Exception:
        __version__ = "unknown"
