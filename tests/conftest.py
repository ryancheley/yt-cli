"""Global test configuration and fixtures."""

import os
from typing import Optional
from unittest.mock import patch

import pytest


@pytest.fixture(scope="function", autouse=True)
def isolate_environment():
    """Ensure test isolation by saving and restoring environment variables."""
    # YouTrack environment variables that could cause test contamination
    youtrack_env_vars = ["YOUTRACK_BASE_URL", "YOUTRACK_TOKEN", "YOUTRACK_USERNAME", "YOUTRACK_VERIFY_SSL"]

    # Store original values
    original_env: dict[str, Optional[str]] = {}
    for key in youtrack_env_vars:
        original_env[key] = os.environ.get(key)

    # Clear YouTrack environment variables before each test
    for key in youtrack_env_vars:
        if key in os.environ:
            del os.environ[key]

    yield

    # Restore original environment after test
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]


@pytest.fixture(scope="function", autouse=True)
def mock_dotenv_loading():
    """Mock dotenv loading to prevent real config files from loading."""
    with (
        patch("youtrack_cli.auth.load_dotenv") as mock_auth_load_dotenv,
        patch("youtrack_cli.config.load_dotenv") as mock_config_load_dotenv,
    ):
        yield mock_auth_load_dotenv, mock_config_load_dotenv
