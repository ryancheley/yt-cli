"""Tests for time tracking functionality."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from youtrack_cli.auth import AuthConfig, AuthManager
from youtrack_cli.time import TimeManager


@pytest.fixture
def mock_credentials():
    """Mock credentials for testing."""
    return AuthConfig(
        base_url="https://test.youtrack.cloud",
        token="test-token",
        username="test-user",
    )


@pytest.fixture
def mock_auth_manager(mock_credentials):
    """Mock auth manager for testing."""
    auth_manager = MagicMock(spec=AuthManager)
    auth_manager.load_credentials.return_value = mock_credentials
    return auth_manager


@pytest.fixture
def time_manager(mock_auth_manager):
    """Time manager instance for testing."""
    return TimeManager(mock_auth_manager)


class TestTimeManager:
    """Test cases for TimeManager class."""

    @pytest.mark.asyncio
    async def test_log_time_success(self, time_manager):
        """Test successful time logging."""
        mock_response = {
            "id": "123",
            "duration": {"minutes": 120},
            "date": "2024-01-01T12:00:00",
            "description": "Test work",
        }

        with patch("youtrack_cli.time.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_response
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await time_manager.log_time("ISSUE-123", "2h", description="Test work")

            assert result["status"] == "success"
            assert "Logged 2h to issue ISSUE-123" in result["message"]
            assert result["data"] == mock_response

    @pytest.mark.asyncio
    async def test_log_time_invalid_duration(self, time_manager):
        """Test logging time with invalid duration."""
        result = await time_manager.log_time("ISSUE-123", "invalid")

        assert result["status"] == "error"
        assert "Invalid duration format" in result["message"]

    @pytest.mark.asyncio
    async def test_log_time_no_credentials(self, time_manager):
        """Test logging time without credentials."""
        time_manager.auth_manager.load_credentials.return_value = None

        result = await time_manager.log_time("ISSUE-123", "2h")

        assert result["status"] == "error"
        assert result["message"] == "Not authenticated"

    @pytest.mark.asyncio
    async def test_log_time_api_error(self, time_manager):
        """Test logging time with API error."""
        with patch("youtrack_cli.time.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 400
            mock_resp.text = "Bad request"
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await time_manager.log_time("ISSUE-123", "2h")

            assert result["status"] == "error"
            assert "Failed to log time" in result["message"]

    @pytest.mark.asyncio
    async def test_get_time_entries_success(self, time_manager):
        """Test successful time entries retrieval."""
        mock_response = [
            {
                "id": "123",
                "duration": {"minutes": 120},
                "date": "2024-01-01T12:00:00",
                "description": "Test work",
                "author": {"id": "user1", "fullName": "Test User"},
                "issue": {"id": "ISSUE-123", "summary": "Test Issue"},
            }
        ]

        with patch("youtrack_cli.time.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_response
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await time_manager.get_time_entries(issue_id="ISSUE-123")

            assert result["status"] == "success"
            assert result["data"] == mock_response
            assert result["count"] == 1

    @pytest.mark.asyncio
    async def test_get_time_summary_success(self, time_manager):
        """Test successful time summary generation."""
        mock_time_entries = [
            {
                "id": "123",
                "duration": {"minutes": 120},
                "date": "2024-01-01T12:00:00",
                "description": "Test work",
                "author": {"id": "user1", "fullName": "Test User"},
                "issue": {"id": "ISSUE-123", "summary": "Test Issue"},
                "type": {"name": "Development"},
            },
            {
                "id": "124",
                "duration": {"minutes": 60},
                "date": "2024-01-02T12:00:00",
                "description": "More test work",
                "author": {"id": "user1", "fullName": "Test User"},
                "issue": {"id": "ISSUE-124", "summary": "Another Issue"},
                "type": {"name": "Testing"},
            },
        ]

        with patch("youtrack_cli.time.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: mock_time_entries
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await time_manager.get_time_summary(group_by="user")

            assert result["status"] == "success"
            assert result["total_entries"] == 2
            assert "Test User" in result["data"]["groups"]
            assert result["data"]["groups"]["Test User"]["minutes"] == 180
            assert result["data"]["groups"]["Test User"]["hours"] == 3.0
            assert result["data"]["total_minutes"] == 180
            assert result["data"]["total_hours"] == 3.0

    def test_parse_duration_valid_formats(self, time_manager):
        """Test parsing various valid duration formats."""
        test_cases = [
            ("2h", 120),
            ("30m", 30),
            ("1h 30m", 90),
            ("2h 45m", 165),
            ("1.5h", 90),
            ("90", 90),
            ("120m", 120),
        ]

        for duration_str, expected_minutes in test_cases:
            result = time_manager._parse_duration(duration_str)
            assert result == expected_minutes, f"Failed for {duration_str}"

    def test_parse_duration_invalid_formats(self, time_manager):
        """Test parsing invalid duration formats."""
        invalid_formats = ["invalid", "h", "m", "", "2x", "30z"]

        for duration_str in invalid_formats:
            result = time_manager._parse_duration(duration_str)
            assert result is None, f"Should be None for {duration_str}"

    def test_parse_date_formats(self, time_manager):
        """Test parsing various date formats."""
        test_cases = [
            ("2024-01-01", "2024-01-01T00:00:00"),
            ("01/01/2024", "2024-01-01T00:00:00"),
            ("01.01.2024", "2024-01-01T00:00:00"),
            ("today", None),  # Will be current date
            ("yesterday", None),  # Will be yesterday
        ]

        for date_str, expected_prefix in test_cases:
            result = time_manager._parse_date(date_str)
            if expected_prefix:
                assert result == expected_prefix
            else:
                # For relative dates, just check they return a valid ISO string
                assert "T" in result or result == date_str

    def test_aggregate_time_data_by_user(self, time_manager):
        """Test aggregating time data by user."""
        time_entries = [
            {
                "duration": {"minutes": 120},
                "author": {"fullName": "User A"},
                "issue": {"id": "ISSUE-1", "summary": "Issue 1"},
                "type": {"name": "Development"},
            },
            {
                "duration": {"minutes": 60},
                "author": {"fullName": "User A"},
                "issue": {"id": "ISSUE-2", "summary": "Issue 2"},
                "type": {"name": "Testing"},
            },
            {
                "duration": {"minutes": 90},
                "author": {"fullName": "User B"},
                "issue": {"id": "ISSUE-3", "summary": "Issue 3"},
                "type": {"name": "Development"},
            },
        ]

        result = time_manager._aggregate_time_data(time_entries, "user")

        assert result["total_minutes"] == 270
        assert result["total_hours"] == 4.5
        assert "User A" in result["groups"]
        assert "User B" in result["groups"]
        assert result["groups"]["User A"]["minutes"] == 180
        assert result["groups"]["User A"]["hours"] == 3.0
        assert result["groups"]["User A"]["entries"] == 2
        assert result["groups"]["User B"]["minutes"] == 90
        assert result["groups"]["User B"]["hours"] == 1.5
        assert result["groups"]["User B"]["entries"] == 1

    def test_aggregate_time_data_by_issue(self, time_manager):
        """Test aggregating time data by issue."""
        time_entries = [
            {
                "duration": {"minutes": 120},
                "author": {"fullName": "User A"},
                "issue": {"id": "ISSUE-1", "summary": "Issue 1"},
                "type": {"name": "Development"},
            },
            {
                "duration": {"minutes": 60},
                "author": {"fullName": "User B"},
                "issue": {"id": "ISSUE-1", "summary": "Issue 1"},
                "type": {"name": "Testing"},
            },
        ]

        result = time_manager._aggregate_time_data(time_entries, "issue")

        assert result["total_minutes"] == 180
        assert result["total_hours"] == 3.0
        assert "ISSUE-1 - Issue 1" in result["groups"]
        assert result["groups"]["ISSUE-1 - Issue 1"]["minutes"] == 180
        assert result["groups"]["ISSUE-1 - Issue 1"]["hours"] == 3.0
        assert result["groups"]["ISSUE-1 - Issue 1"]["entries"] == 2

    def test_aggregate_time_data_by_type(self, time_manager):
        """Test aggregating time data by work type."""
        time_entries = [
            {
                "duration": {"minutes": 120},
                "author": {"fullName": "User A"},
                "issue": {"id": "ISSUE-1", "summary": "Issue 1"},
                "type": {"name": "Development"},
            },
            {
                "duration": {"minutes": 60},
                "author": {"fullName": "User B"},
                "issue": {"id": "ISSUE-2", "summary": "Issue 2"},
                "type": {"name": "Development"},
            },
            {
                "duration": {"minutes": 30},
                "author": {"fullName": "User A"},
                "issue": {"id": "ISSUE-3", "summary": "Issue 3"},
                "type": {"name": "Testing"},
            },
        ]

        result = time_manager._aggregate_time_data(time_entries, "type")

        assert result["total_minutes"] == 210
        assert result["total_hours"] == 3.5
        assert "Development" in result["groups"]
        assert "Testing" in result["groups"]
        assert result["groups"]["Development"]["minutes"] == 180
        assert result["groups"]["Development"]["hours"] == 3.0
        assert result["groups"]["Development"]["entries"] == 2
        assert result["groups"]["Testing"]["minutes"] == 30
        assert result["groups"]["Testing"]["hours"] == 0.5
        assert result["groups"]["Testing"]["entries"] == 1
