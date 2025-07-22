"""Tests for time tracking functionality."""

import re
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from youtrack_cli.auth import AuthConfig
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
    auth_manager = MagicMock()
    auth_manager.load_credentials.return_value = mock_credentials
    return auth_manager


@pytest.fixture
def time_manager(mock_auth_manager):
    """Time manager instance for testing."""
    return TimeManager(mock_auth_manager)


@pytest.mark.unit
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
        from datetime import datetime

        # Test specific date formats return correct timestamps
        test_cases = [
            ("2024-01-01", datetime(2024, 1, 1).timestamp() * 1000),
            ("01/01/2024", datetime(2024, 1, 1).timestamp() * 1000),
            ("01.01.2024", datetime(2024, 1, 1).timestamp() * 1000),
        ]

        for date_str, expected_timestamp in test_cases:
            result = time_manager._parse_date(date_str)
            assert result == int(expected_timestamp), f"Failed for {date_str}"

        # Test relative dates return valid timestamps
        today_result = time_manager._parse_date("today")
        yesterday_result = time_manager._parse_date("yesterday")

        assert isinstance(today_result, int)
        assert isinstance(yesterday_result, int)
        assert today_result > yesterday_result  # today should be later than yesterday

    def test_parse_date_returns_timestamp(self, time_manager):
        """Test that _parse_date returns timestamps in milliseconds."""
        # Test with a known date
        result = time_manager._parse_date("2024-01-01")

        # Should be a timestamp in milliseconds (13-digit number for dates around 2024)
        assert isinstance(result, int)
        assert len(str(result)) == 13  # milliseconds since epoch should be 13 digits in 2024

        # Test with invalid date - should still return a valid timestamp
        invalid_result = time_manager._parse_date("invalid-date")
        assert isinstance(invalid_result, int)
        assert len(str(invalid_result)) == 13

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

    @pytest.mark.asyncio
    async def test_get_time_entries_empty_response(self, time_manager):
        """Test get_time_entries handles empty API response without NoneType error."""
        with patch("youtrack_cli.time.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.text = ""  # Empty response body
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await time_manager.get_time_entries(issue_id="ISSUE-123")

            assert result["status"] == "success"
            assert result["data"] == []  # Should return empty list, not None
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_get_time_entries_none_response(self, time_manager):
        """Test get_time_entries handles None response from JSON parsing."""
        with patch("youtrack_cli.time.get_client_manager") as mock_get_client_manager:
            mock_resp = Mock()
            mock_resp.status_code = 200
            mock_resp.json = lambda: None  # JSON parsing returns None
            mock_client_manager = Mock()
            mock_client_manager.make_request = AsyncMock(return_value=mock_resp)
            mock_get_client_manager.return_value = mock_client_manager

            result = await time_manager.get_time_entries(issue_id="ISSUE-123")

            assert result["status"] == "success"
            assert result["data"] == []  # Should convert None to empty list
            assert result["count"] == 0

    def test_display_time_entries_none_input(self, time_manager):
        """Test display_time_entries handles None input without error."""
        with patch.object(time_manager, "console") as mock_console:
            # Should not raise AttributeError: 'NoneType' object has no attribute 'get'
            time_manager.display_time_entries(None)

            mock_console.print.assert_called_once_with("No time entries found.", style="yellow")

    def test_display_time_entries_empty_list(self, time_manager):
        """Test display_time_entries handles empty list."""
        with patch.object(time_manager, "console") as mock_console:
            time_manager.display_time_entries([])

            mock_console.print.assert_called_once_with("No time entries found.", style="yellow")

    def test_display_time_entries_non_list_input(self, time_manager):
        """Test display_time_entries converts non-list input to list."""
        single_entry = {
            "id": "123",
            "duration": {"minutes": 120},
            "date": 1704067200000,  # 2024-01-01 00:00:00 UTC in milliseconds
            "author": {"fullName": "Test User"},
            "issue": {"id": "ISSUE-123", "summary": "Test Issue"},
            "type": {"name": "Development"},
            "description": "Test work",
        }

        with patch.object(time_manager, "console") as mock_console:
            time_manager.display_time_entries(single_entry)

            # Should convert single entry to list and display table
            # Table rendering makes multiple print calls (at least for the table)
            assert mock_console.print.call_count >= 1
            # Verify it's not showing "No time entries found"
            calls = [call.args for call in mock_console.print.call_calls]
            no_entries_calls = [call for call in calls if "No time entries found" in str(call)]
            assert len(no_entries_calls) == 0


@pytest.mark.unit
class TestTimeCommands:
    """Test cases for time tracking CLI commands."""

    @pytest.mark.asyncio
    async def test_list_command_success(self, mock_auth_manager):
        """Test successful time list command execution."""
        from click.testing import CliRunner

        from youtrack_cli.commands.time_tracking import list

        mock_time_entries = [
            {
                "id": "123",
                "duration": {"minutes": 120},
                "date": 1704067200000,
                "description": "Test work",
                "author": {"id": "user1", "fullName": "Test User"},
                "issue": {"id": "ISSUE-123", "summary": "Test Issue"},
                "type": {"name": "Development"},
            }
        ]

        with patch("youtrack_cli.commands.time_tracking.AuthManager") as mock_auth_class:
            mock_auth_class.return_value = mock_auth_manager
            with patch("youtrack_cli.commands.time_tracking.asyncio.run") as mock_run:
                mock_run.return_value = {
                    "status": "success",
                    "data": mock_time_entries,
                    "count": 1,
                }

                runner = CliRunner(env={"NO_COLOR": "1"})
                result = runner.invoke(list, ["--issue", "ISSUE-123"], obj={"config": None})

                assert result.exit_code == 0
                # Strip ANSI codes from output for comparison
                clean_output = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
                assert "📋 Listing time entries..." in clean_output
                assert "📊 Total entries: 1" in clean_output

    def test_list_command_with_json_format(self, mock_auth_manager):
        """Test time list command with JSON output format."""
        from click.testing import CliRunner

        from youtrack_cli.commands.time_tracking import list

        mock_time_entries = [
            {
                "id": "123",
                "duration": {"minutes": 120},
                "date": 1704067200000,
                "description": "Test work",
                "author": {"id": "user1", "fullName": "Test User"},
                "issue": {"id": "ISSUE-123", "summary": "Test Issue"},
                "type": {"name": "Development"},
            }
        ]

        with patch("youtrack_cli.commands.time_tracking.AuthManager") as mock_auth_class:
            mock_auth_class.return_value = mock_auth_manager
            with patch("youtrack_cli.time.TimeManager") as mock_time_manager_class:
                mock_time_manager = Mock()
                mock_time_manager.display_time_entries = Mock()

                # Make get_time_entries return a coroutine that resolves to the mock data
                async def mock_get_time_entries(*args, **kwargs):
                    return {
                        "status": "success",
                        "data": mock_time_entries,
                        "count": 1,
                    }

                mock_time_manager.get_time_entries = mock_get_time_entries
                mock_time_manager_class.return_value = mock_time_manager

                runner = CliRunner(env={"NO_COLOR": "1"})
                result = runner.invoke(list, ["--issue", "ISSUE-123", "--format", "json"], obj={"config": None})

                assert result.exit_code == 0
                # Strip ANSI codes from output for comparison
                clean_output = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
                assert "📋 Listing time entries..." in clean_output

    @pytest.mark.asyncio
    async def test_list_command_error(self, mock_auth_manager):
        """Test time list command with error response."""
        from click.testing import CliRunner

        from youtrack_cli.commands.time_tracking import list

        with patch("youtrack_cli.commands.time_tracking.AuthManager") as mock_auth_class:
            mock_auth_class.return_value = mock_auth_manager
            with patch("youtrack_cli.commands.time_tracking.asyncio.run") as mock_run:
                mock_run.return_value = {
                    "status": "error",
                    "message": "API error occurred",
                }

                runner = CliRunner()
                result = runner.invoke(list, ["--issue", "ISSUE-123"], obj={"config": None})

                assert result.exit_code == 1
                assert "❌ API error occurred" in result.output

    @pytest.mark.asyncio
    async def test_list_command_no_issue_filter(self, mock_auth_manager):
        """Test time list command without issue filter."""
        from click.testing import CliRunner

        from youtrack_cli.commands.time_tracking import list

        mock_time_entries = []

        with patch("youtrack_cli.commands.time_tracking.AuthManager") as mock_auth_class:
            mock_auth_class.return_value = mock_auth_manager
            with patch("youtrack_cli.commands.time_tracking.asyncio.run") as mock_run:
                mock_run.return_value = {
                    "status": "success",
                    "data": mock_time_entries,
                    "count": 0,
                }

                runner = CliRunner(env={"NO_COLOR": "1"})
                result = runner.invoke(list, [], obj={"config": None})

                assert result.exit_code == 0
                # Strip ANSI codes from output for comparison
                clean_output = re.sub(r"\x1b\[[0-9;]*m", "", result.output)
                assert "📋 Listing time entries..." in clean_output
                assert "📊 Total entries: 0" in clean_output
