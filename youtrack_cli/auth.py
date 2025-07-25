"""Authentication management for YouTrack CLI.

This module provides secure authentication management including token storage,
credential verification, and session management for YouTrack API access.

Example:
    >>> # auth_manager = AuthManager()  # doctest: +SKIP
    >>> # result = await auth_manager.verify_credentials()  # doctest: +SKIP
    >>> # if result.status == 'success':  # doctest: +SKIP
    >>> #     print(f"Authenticated as {result.username}")  # doctest: +SKIP
    >>> print("Authentication manager example")
    Authentication manager example
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

from .client import reset_client_manager_sync
from .config import ConfigManager
from .console import get_console
from .models import CredentialVerificationResult
from .security import CredentialManager, SecurityConfig, TokenManager

__all__ = ["AuthConfig", "AuthManager"]


class AuthConfig(BaseModel):
    """Configuration for YouTrack authentication.

    Stores authentication configuration including base URL, API token,
    and optional metadata like username and token expiry.

    Attributes:
        base_url: YouTrack instance URL (required).
        token: API token for authentication (required).
        username: Username associated with token (optional).
        token_expiry: Token expiration date (optional).
    """

    base_url: str = Field(..., description="YouTrack instance URL")
    token: str = Field(..., description="API token for authentication")
    username: Optional[str] = Field(None, description="Username (optional)")
    token_expiry: Optional[datetime] = Field(None, description="Token expiration date")


class AuthManager:
    """Manages authentication for YouTrack CLI.

    Provides comprehensive authentication management including secure token
    storage using system keyring, credential verification, and session
    management for YouTrack API interactions.

    The manager handles both environment-based and keyring-based credential
    storage with automatic fallback mechanisms and security best practices.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        security_config: Optional[SecurityConfig] = None,
    ):
        """Initialize the auth manager.

        Args:
            config_path: Path to configuration file. If None, uses default
                location in user's home directory.
            security_config: Security configuration for encryption and keyring.
                If None, uses default security settings.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.security_config = security_config or SecurityConfig()
        self.credential_manager = CredentialManager(self.security_config)
        self.token_manager = TokenManager(self.security_config)
        self.console = get_console()
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
        verify_ssl: bool = True,
    ) -> None:
        """Save authentication credentials to config file or keyring.

        Args:
            base_url: YouTrack instance URL
            token: API token
            username: Username (optional)
            token_expiry: Token expiration date (optional)
            use_keyring: Whether to use keyring for secure storage
            verify_ssl: Whether SSL verification is enabled
        """
        if use_keyring and self.security_config.enable_credential_encryption:
            # Store in keyring with encryption
            self.credential_manager.store_credential("youtrack_base_url", base_url)
            self.credential_manager.store_credential("youtrack_token", token)
            if username:
                self.credential_manager.store_credential("youtrack_username", username)
            if token_expiry:
                self.credential_manager.store_credential("youtrack_token_expiry", token_expiry.isoformat())
            # Store SSL verification setting
            self.credential_manager.store_credential("youtrack_verify_ssl", str(verify_ssl))

            # Also store non-sensitive config to .env file for config list visibility
            config_manager = ConfigManager(self.config_path)
            config_manager.set_config("YOUTRACK_BASE_URL", base_url)
            if username:
                config_manager.set_config("YOUTRACK_USERNAME", username)
            config_manager.set_config("YOUTRACK_VERIFY_SSL", str(verify_ssl).lower())
            # Store a reference that token is in keyring
            config_manager.set_config("YOUTRACK_API_KEY", "[Stored in keyring]")

            self.console.print("[green]✓[/green] Credentials stored securely in keyring")
        else:
            # Fallback to file storage using ConfigManager for consistency
            config_manager = ConfigManager(self.config_path)
            config_manager.set_config("YOUTRACK_BASE_URL", base_url)
            config_manager.set_config("YOUTRACK_TOKEN", token)
            if username:
                config_manager.set_config("YOUTRACK_USERNAME", username)
            if token_expiry:
                config_manager.set_config("YOUTRACK_TOKEN_EXPIRY", token_expiry.isoformat())
            # Save SSL verification setting
            config_manager.set_config("YOUTRACK_VERIFY_SSL", str(verify_ssl).lower())

            self.console.print(
                "[yellow]⚠[/yellow] Credentials stored in plain text file. Consider using keyring for better security."
            )

        # Reset the client manager to pick up new SSL settings
        reset_client_manager_sync()

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
            self.credential_manager.delete_credential("youtrack_verify_ssl")

        # Clear from file - use ConfigManager to only clear auth-related keys
        config_manager = ConfigManager(self.config_path)
        config_manager.unset_config("YOUTRACK_BASE_URL")
        config_manager.unset_config("YOUTRACK_TOKEN")
        config_manager.unset_config("YOUTRACK_USERNAME")
        config_manager.unset_config("YOUTRACK_TOKEN_EXPIRY")
        config_manager.unset_config("YOUTRACK_VERIFY_SSL")
        config_manager.unset_config("YOUTRACK_API_KEY")

        # Reset the client manager to pick up new SSL settings
        reset_client_manager_sync()

    def _check_token_expiration(self, config: AuthConfig) -> None:
        """Check token expiration and warn user if needed."""
        if not config.token_expiry:
            return

        expiration_info = self.token_manager.check_token_expiration(config.token_expiry)

        if expiration_info["status"] == "expired":
            self.console.print(f"[red]⚠ {expiration_info['message']}[/red]")
        elif expiration_info["status"] == "expiring":
            self.console.print(f"[yellow]⚠ {expiration_info['message']}[/yellow]")

    async def refresh_token(self) -> bool:
        """Attempt to refresh the current token.

        Returns:
            True if token was successfully refreshed, False otherwise
        """
        credentials = self.load_credentials()
        if not credentials:
            self.console.print("[red]No authentication credentials found[/red]")
            return False

        if not self.token_manager.is_token_renewable(credentials.token):
            self.console.print("[yellow]Current token does not support refresh[/yellow]")
            return False

        try:
            # Get SSL verification setting
            verify_ssl_str = os.getenv("YOUTRACK_VERIFY_SSL", "true").lower()
            verify_ssl = verify_ssl_str not in ("false", "0", "no", "off")

            new_token = await self.token_manager.request_new_token(credentials.base_url, credentials.token, verify_ssl)

            if new_token:
                # Update stored credentials with new token
                self.save_credentials(
                    base_url=credentials.base_url,
                    token=new_token,
                    username=credentials.username,
                    token_expiry=credentials.token_expiry,  # Keep existing expiry for now
                    use_keyring=self.security_config.enable_credential_encryption,
                    verify_ssl=verify_ssl,
                )
                self.console.print("[green]✓ Token refreshed successfully[/green]")
                return True
            else:
                self.console.print("[red]Token refresh failed[/red]")
                return False

        except Exception as e:
            self.console.print(f"[red]Token refresh error: {str(e)}[/red]")
            return False

    async def auto_refresh_if_needed(self) -> bool:
        """Check if token needs refresh and attempt it automatically.

        Returns:
            True if no refresh was needed or refresh was successful, False if refresh failed
        """
        if not self.security_config.enable_automatic_token_refresh:
            return True

        credentials = self.load_credentials()
        if not credentials or not credentials.token_expiry:
            return True

        if not self.token_manager.should_refresh_token(credentials.token_expiry):
            return True

        if not self.token_manager.is_token_renewable(credentials.token):
            return True

        self.console.print("[yellow]Token is expiring soon, attempting automatic refresh...[/yellow]")
        return await self.refresh_token()

    def get_current_user_sync(self) -> Optional[str]:
        """Get the current authenticated user's username from stored credentials.

        Returns:
            Username if credentials are available, None otherwise
        """
        credentials = self.load_credentials()
        if not credentials:
            return None
        return credentials.username

    async def get_current_user(self) -> Optional[str]:
        """Get the current authenticated user's username.

        Returns:
            Username if credentials are available, None otherwise
        """
        credentials = self.load_credentials()
        if not credentials:
            return None

        try:
            verification_result = await self.verify_credentials(
                credentials.base_url, credentials.token, verify_ssl=True
            )
            if verification_result.status == "success":
                return verification_result.username
        except Exception:
            # If verification fails, fallback to stored username
            pass

        # Fallback to stored username from credentials
        return credentials.username

    async def verify_credentials(
        self, base_url: str, token: str, verify_ssl: bool = True
    ) -> CredentialVerificationResult:
        """Verify credentials with YouTrack API.

        Args:
            base_url: YouTrack instance URL
            token: API token
            verify_ssl: Whether to verify SSL certificates

        Returns:
            Dictionary with verification result

        Raises:
            httpx.HTTPError: If request fails
        """
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

        # Configure SSL verification
        client_kwargs = {"timeout": 10.0}
        if not verify_ssl:
            client_kwargs["verify"] = False

        async with httpx.AsyncClient(**client_kwargs) as client:
            try:
                response = await client.get(
                    f"{base_url.rstrip('/')}/api/users/me",
                    headers=headers,
                )
                response.raise_for_status()

                user_data = response.json()
                return CredentialVerificationResult(
                    status="success",
                    username=user_data.get("login", "Unknown"),
                    full_name=user_data.get("fullName", "Unknown"),
                    email=user_data.get("email", "Unknown"),
                )
            except httpx.HTTPError as e:
                return CredentialVerificationResult(status="error", message=str(e))
            except Exception as e:
                return CredentialVerificationResult(status="error", message=str(e))
