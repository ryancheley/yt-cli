"""Base service class for YouTrack API communication."""

from typing import Any, Dict, List, Optional

import httpx

from ..auth import AuthManager
from ..client import get_client_manager
from ..logging import get_logger

logger = get_logger(__name__)


class BaseService:
    """Base class for YouTrack API services.

    Provides common functionality for API communication including:
    - Authentication handling
    - HTTP request/response management
    - JSON parsing with error handling
    - Standardized error responses
    """

    def __init__(self, auth_manager: AuthManager):
        """Initialize the service.

        Args:
            auth_manager: AuthManager instance for authentication
        """
        self.auth_manager = auth_manager

    def _parse_json_response(self, response: httpx.Response) -> Any:
        """Safely parse JSON response, handling empty or non-JSON responses.

        Args:
            response: HTTP response to parse

        Returns:
            Parsed JSON data

        Raises:
            ValueError: If response cannot be parsed as JSON
        """
        try:
            content_type = response.headers.get("content-type", "")
            if not response.text:
                raise ValueError("Empty response body")

            if "application/json" not in content_type:
                raise ValueError(f"Response is not JSON. Content-Type: {content_type}")

            return response.json()
        except Exception as e:
            # Try to provide more context about the error
            status_code = response.status_code
            preview = response.text[:200] if response.text else "empty"
            raise ValueError(
                f"Failed to parse JSON response (status {status_code}): {str(e)}. Response preview: {preview}"
            ) from e

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests.

        Returns:
            Dictionary containing authorization headers

        Raises:
            ValueError: If not authenticated
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            raise ValueError("Not authenticated")

        return {"Authorization": f"Bearer {credentials.token}"}

    def _get_base_url(self) -> str:
        """Get the base URL for API requests.

        Returns:
            Base URL for YouTrack API

        Raises:
            ValueError: If not authenticated
        """
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            raise ValueError("Not authenticated")

        return credentials.base_url.rstrip("/")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make an authenticated API request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            json_data: JSON data for request body
            additional_headers: Additional headers to include

        Returns:
            HTTP response

        Raises:
            ValueError: If not authenticated
        """
        base_url = self._get_base_url()
        url = f"{base_url}/api/{endpoint.lstrip('/')}"

        headers = self._get_auth_headers()
        if additional_headers:
            headers.update(additional_headers)

        if json_data:
            headers["Content-Type"] = "application/json"

        client_manager = get_client_manager()
        return await client_manager.make_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json_data=json_data,
        )

    def _create_success_response(self, data: Any) -> Dict[str, Any]:
        """Create a standardized success response.

        Args:
            data: Response data

        Returns:
            Standardized success response
        """
        return {"status": "success", "data": data}

    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Create a standardized error response.

        Args:
            message: Error message

        Returns:
            Standardized error response
        """
        return {"status": "error", "message": message}

    async def _handle_response(
        self, response: httpx.Response, success_codes: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Handle API response with standardized error handling.

        Args:
            response: HTTP response to handle
            success_codes: List of HTTP status codes considered successful

        Returns:
            Standardized response dictionary
        """
        if success_codes is None:
            success_codes = [200]

        try:
            if response.status_code in success_codes:
                # Some endpoints return empty responses (e.g., DELETE)
                if not response.text:
                    return self._create_success_response(None)

                data = self._parse_json_response(response)
                return self._create_success_response(data)
            else:
                error_text = response.text or f"HTTP {response.status_code}"
                return self._create_error_response(f"API request failed: {error_text}")
        except Exception as e:
            logger.error(f"Error handling response: {e}")
            return self._create_error_response(f"Error handling response: {str(e)}")
