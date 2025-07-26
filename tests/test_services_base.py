"""Tests for BaseService."""

from unittest.mock import Mock

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

    def test_create_error_response(self, base_service):
        """Test _create_error_response method."""
        error_msg = "Test error"
        response = base_service._create_error_response(error_msg)

        assert response["status"] == "error"
        assert response["message"] == error_msg

    def test_parse_json_response_success(self, base_service):
        """Test successful JSON parsing."""
        mock_response = Mock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.text = '{"key": "value"}'
        mock_response.json.return_value = {"key": "value"}

        result = base_service._parse_json_response(mock_response)
        assert result == {"key": "value"}

    def test_parse_json_response_empty(self, base_service):
        """Test parsing empty response."""
        mock_response = Mock()
        mock_response.text = ""

        with pytest.raises(ValueError, match="Empty response body"):
            base_service._parse_json_response(mock_response)

    def test_parse_json_response_not_json(self, base_service):
        """Test parsing non-JSON response."""
        mock_response = Mock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.text = "<html>Not JSON</html>"

        with pytest.raises(ValueError, match="Response is not JSON"):
            base_service._parse_json_response(mock_response)
