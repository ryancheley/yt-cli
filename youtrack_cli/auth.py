"""Authentication management for YouTrack CLI."""

import os
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError


class AuthConfig(BaseModel):
    """Configuration for YouTrack authentication."""

    base_url: str = Field(..., description="YouTrack instance URL")
    token: str = Field(..., description="API token for authentication")
    username: Optional[str] = Field(None, description="Username (optional)")


class AuthManager:
    """Manages authentication for YouTrack CLI."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the auth manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or self._get_default_config_path()
        load_dotenv(self.config_path)

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        config_dir = Path.home() / ".config" / "youtrack-cli"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / ".env")

    def save_credentials(
        self, base_url: str, token: str, username: Optional[str] = None
    ) -> None:
        """Save authentication credentials to config file.

        Args:
            base_url: YouTrack instance URL
            token: API token
            username: Username (optional)
        """
        config_path = Path(self.config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w") as f:
            f.write(f"YOUTRACK_BASE_URL={base_url}\n")
            f.write(f"YOUTRACK_TOKEN={token}\n")
            if username:
                f.write(f"YOUTRACK_USERNAME={username}\n")

    def load_credentials(self) -> Optional[AuthConfig]:
        """Load authentication credentials from config file.

        Returns:
            AuthConfig object if credentials exist, None otherwise
        """
        base_url = os.getenv("YOUTRACK_BASE_URL")
        token = os.getenv("YOUTRACK_TOKEN")
        username = os.getenv("YOUTRACK_USERNAME")

        if not base_url or not token:
            return None

        try:
            return AuthConfig(base_url=base_url, token=token, username=username)
        except ValidationError:
            return None

    def clear_credentials(self) -> None:
        """Clear saved authentication credentials."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    async def verify_credentials(self, base_url: str, token: str) -> dict[str, str]:
        """Verify credentials with YouTrack API.

        Args:
            base_url: YouTrack instance URL
            token: API token

        Returns:
            Dictionary with verification result

        Raises:
            httpx.HTTPError: If request fails
        """
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{base_url.rstrip('/')}/api/admin/users/me",
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()

                user_data = response.json()
                return {
                    "status": "success",
                    "username": user_data.get("login", "Unknown"),
                    "full_name": user_data.get("fullName", "Unknown"),
                    "email": user_data.get("email", "Unknown"),
                }
            except httpx.HTTPError as e:
                return {"status": "error", "message": str(e)}
            except Exception as e:
                return {"status": "error", "message": str(e)}
