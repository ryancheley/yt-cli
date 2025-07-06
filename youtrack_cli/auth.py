"""Authentication management for YouTrack CLI."""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from rich.console import Console

from .security import CredentialManager, SecurityConfig, TokenManager

__all__ = ["AuthConfig", "AuthManager"]


class AuthConfig(BaseModel):
    """Configuration for YouTrack authentication."""

    base_url: str = Field(..., description="YouTrack instance URL")
    token: str = Field(..., description="API token for authentication")
    username: Optional[str] = Field(None, description="Username (optional)")
    token_expiry: Optional[datetime] = Field(None, description="Token expiration date")


class AuthManager:
    """Manages authentication for YouTrack CLI."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        security_config: Optional[SecurityConfig] = None,
    ):
        """Initialize the auth manager.

        Args:
            config_path: Path to configuration file
            security_config: Security configuration
        """
        self.config_path = config_path or self._get_default_config_path()
        self.security_config = security_config or SecurityConfig()
        self.credential_manager = CredentialManager(self.security_config)
        self.token_manager = TokenManager(self.security_config)
        self.console = Console()
        load_dotenv(self.config_path)

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        config_dir = Path.home() / ".config" / "youtrack-cli"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / ".env")

    def save_credentials(
        self,
        base_url: str,
        token: str,
        username: Optional[str] = None,
        token_expiry: Optional[datetime] = None,
        use_keyring: bool = True,
    ) -> None:
        """Save authentication credentials to config file or keyring.

        Args:
            base_url: YouTrack instance URL
            token: API token
            username: Username (optional)
            token_expiry: Token expiration date (optional)
            use_keyring: Whether to use keyring for secure storage
        """
        if use_keyring and self.security_config.enable_credential_encryption:
            # Store in keyring with encryption
            self.credential_manager.store_credential("youtrack_base_url", base_url)
            self.credential_manager.store_credential("youtrack_token", token)
            if username:
                self.credential_manager.store_credential("youtrack_username", username)
            if token_expiry:
                self.credential_manager.store_credential("youtrack_token_expiry", token_expiry.isoformat())

            self.console.print("[green]✓[/green] Credentials stored securely in keyring")
        else:
            # Fallback to file storage
            config_path = Path(self.config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, "w") as f:
                f.write(f"YOUTRACK_BASE_URL={base_url}\n")
                f.write(f"YOUTRACK_TOKEN={token}\n")
                if username:
                    f.write(f"YOUTRACK_USERNAME={username}\n")
                if token_expiry:
                    f.write(f"YOUTRACK_TOKEN_EXPIRY={token_expiry.isoformat()}\n")

            self.console.print(
                "[yellow]⚠[/yellow] Credentials stored in plain text file. Consider using keyring for better security."
            )

    def load_credentials(self) -> Optional[AuthConfig]:
        """Load authentication credentials from keyring or config file.

        Returns:
            AuthConfig object if credentials exist, None otherwise
        """
        # Try to load from keyring first
        if self.security_config.enable_credential_encryption:
            base_url = self.credential_manager.retrieve_credential("youtrack_base_url")
            token = self.credential_manager.retrieve_credential("youtrack_token")
            username = self.credential_manager.retrieve_credential("youtrack_username")
            token_expiry_str = self.credential_manager.retrieve_credential("youtrack_token_expiry")

            token_expiry = None
            if token_expiry_str:
                try:
                    token_expiry = datetime.fromisoformat(token_expiry_str)
                except ValueError:
                    pass

            if base_url and token:
                try:
                    config = AuthConfig(
                        base_url=base_url,
                        token=token,
                        username=username,
                        token_expiry=token_expiry,
                    )
                    self._check_token_expiration(config)
                    return config
                except ValidationError:
                    pass

        # Fallback to environment variables/file
        base_url = os.getenv("YOUTRACK_BASE_URL")
        token = os.getenv("YOUTRACK_TOKEN")
        username = os.getenv("YOUTRACK_USERNAME")
        token_expiry_str = os.getenv("YOUTRACK_TOKEN_EXPIRY")

        token_expiry = None
        if token_expiry_str:
            try:
                token_expiry = datetime.fromisoformat(token_expiry_str)
            except ValueError:
                pass

        if not base_url or not token:
            return None

        try:
            config = AuthConfig(
                base_url=base_url,
                token=token,
                username=username,
                token_expiry=token_expiry,
            )
            self._check_token_expiration(config)
            return config
        except ValidationError:
            return None

    def clear_credentials(self) -> None:
        """Clear saved authentication credentials from both keyring and file."""
        # Clear from keyring
        if self.security_config.enable_credential_encryption:
            self.credential_manager.delete_credential("youtrack_base_url")
            self.credential_manager.delete_credential("youtrack_token")
            self.credential_manager.delete_credential("youtrack_username")
            self.credential_manager.delete_credential("youtrack_token_expiry")

        # Clear from file
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    def _check_token_expiration(self, config: AuthConfig) -> None:
        """Check token expiration and warn user if needed."""
        if not config.token_expiry:
            return

        expiration_info = self.token_manager.check_token_expiration(config.token_expiry)

        if expiration_info["status"] == "expired":
            self.console.print(f"[red]⚠ {expiration_info['message']}[/red]")
        elif expiration_info["status"] == "expiring":
            self.console.print(f"[yellow]⚠ {expiration_info['message']}[/yellow]")

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
                    f"{base_url.rstrip('/')}/api/users/me",
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
