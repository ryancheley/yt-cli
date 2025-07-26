"""Tests for BaseService."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from youtrack_cli.services.base import BaseService


class TestBaseService:
    """Test cases for BaseService."""

    @pytest.fixture
    def mock_auth_manager(self):
        """Create mock auth manager."""
        return Mock()

    @pytest.fixture
    def base_service(self, mock_auth_manager):
        """Create BaseService instance."""
        return BaseService(mock_auth_manager)

    def test_init(self, mock_auth_manager):
        """Test BaseService initialization."""
        service = BaseService(mock_auth_manager)
        assert service.auth_manager == mock_auth_manager

    @pytest.mark.asyncio
    async def test_make_request_get(self, base_service):
        """Test _make_request with GET method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)

            response = await base_service._make_request("GET", "test/endpoint")

            assert response == mock_response
            mock_client.return_value.__aenter__.return_value.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_post_with_json(self, base_service):
        """Test _make_request with POST method and JSON data."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "123"}

        test_data = {"name": "test"}

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.request = AsyncMock(return_value=mock_response)

            response = await base_service._make_request("POST", "test/endpoint", json_data=test_data)

            assert response == mock_response

    @pytest.mark.asyncio
    async def test_handle_response_success(self, base_service):
        """Test _handle_response with successful response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}

        result = await base_service._handle_response(mock_response)

        assert result["status"] == "success"
        assert result["data"] == {"result": "success"}

    @pytest.mark.asyncio
    async def test_handle_response_error(self, base_service):
        """Test _handle_response with error response."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"

        result = await base_service._handle_response(mock_response)

        assert result["status"] == "error"
        assert "404" in result["message"]

    def test_create_error_response(self, base_service):
        """Test _create_error_response."""
        error_msg = "Test error message"
        result = base_service._create_error_response(error_msg)

        assert result["status"] == "error"
        assert result["message"] == error_msg

    def test_create_success_response(self, base_service):
        """Test _create_success_response."""
        test_data = {"id": "123", "name": "test"}
        result = base_service._create_success_response(test_data)

        assert result["status"] == "success"
        assert result["data"] == test_data
