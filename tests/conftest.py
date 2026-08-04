"""Global test configuration and fixtures."""

import os
from unittest.mock import patch

import pytest


@pytest.fixture(scope="function", autouse=True)
def isolate_environment():
    """Ensure test isolation by saving and restoring environment variables."""
    # YouTrack environment variables that could cause test contamination
    youtrack_env_vars = ["YOUTRACK_BASE_URL", "YOUTRACK_TOKEN", "YOUTRACK_USERNAME", "YOUTRACK_VERIFY_SSL"]

    # Store original values
    original_env: dict[str, str | None] = {}
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
def isolate_keyring():
    """Give each test a fresh, empty in-memory keyring backend.

    The keyring backend is process-wide global state that pytest does not reset
    between tests, so credentials written (or leaked) by one test could be read
    by another under randomized ordering. This mirrors ``isolate_environment``
    for the keyring and removes any dependency on the developer's real keychain.
    """
    import keyring
    from keyring.backend import KeyringBackend

    class _MemKeyring(KeyringBackend):
        priority = 1

        def __init__(self):
            super().__init__()
            self._store: dict[tuple[str, str], str] = {}

        def get_password(self, service, username):
            return self._store.get((service, username))

        def set_password(self, service, username, password):
            self._store[(service, username)] = password

        def delete_password(self, service, username):
            self._store.pop((service, username), None)

    previous = keyring.get_keyring()
    keyring.set_keyring(_MemKeyring())
    try:
        yield
    finally:
        keyring.set_keyring(previous)


@pytest.fixture(scope="function", autouse=True)
def mock_dotenv_loading():
    """Mock dotenv loading to prevent real config files from loading."""
    with (
        patch("youtrack_cli.auth.load_dotenv") as mock_auth_load_dotenv,
        patch("youtrack_cli.config.load_dotenv") as mock_config_load_dotenv,
    ):
        yield mock_auth_load_dotenv, mock_config_load_dotenv
