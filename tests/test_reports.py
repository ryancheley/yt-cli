"""Tests for the reports module."""

from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from youtrack_cli.auth import AuthConfig, AuthManager
from youtrack_cli.main import main
from youtrack_cli.reports import ReportManager


class TestReportManager:
    """Test ReportManager functionality."""

    @pytest.fixture
    def auth_manager(self):
        """Create a mock auth manager for testing."""
        auth_manager = Mock(spec=AuthManager)
        auth_manager.load_credentials.return_value = AuthConfig(
            base_url="https://test.youtrack.cloud",
            token="test-token",
            username="test-user",
        )
        return auth_manager

    @pytest.fixture
    def report_manager(self, auth_manager):
        """Create a ReportManager instance for testing."""
        return ReportManager(auth_manager)

    @pytest.mark.asyncio
    async def test_generate_burndown_report_success(self, report_manager, auth_manager):
        """Test successful burndown report generation."""
        mock_issues = [
            {
                "id": "1",
                "summary": "Test Issue 1",
                "resolved": 1234567890,
                "created": 1234567000,
                "state": {"name": "Done"},
                "spent": {"value": 120},  # 2 hours in minutes
            },
            {
                "id": "2",
                "summary": "Test Issue 2",
                "resolved": None,
                "created": 1234567000,
                "state": {"name": "In Progress"},
                "spent": {"value": 60},  # 1 hour in minutes
            },
        ]

        with patch("youtrack_cli.reports.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_response = Mock()
            mock_response.json.return_value = mock_issues

            async def mock_make_request(*args, **kwargs):
                return mock_response

            mock_client_manager.make_request = mock_make_request
            mock_get_client.return_value = mock_client_manager

            result = await report_manager.generate_burndown_report(
                project_id="TEST",
                sprint_id="sprint-1",
                start_date="2024-01-01",
                end_date="2024-01-31",
            )

            assert result["status"] == "success"
            assert result["data"]["project"] == "TEST"
            assert result["data"]["sprint"] == "sprint-1"
            assert result["data"]["total_issues"] == 2
            assert result["data"]["resolved_issues"] == 1
            assert result["data"]["remaining_issues"] == 1
            assert result["data"]["completion_rate"] == 50.0
            assert result["data"]["total_effort_hours"] == 3.0  # (120 + 60) / 60

    @pytest.mark.asyncio
    async def test_generate_burndown_report_no_auth(self, report_manager):
        """Test burndown report generation without authentication."""
        report_manager.auth_manager.load_credentials.return_value = None

        result = await report_manager.generate_burndown_report("TEST")

        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

    @pytest.mark.asyncio
    async def test_generate_burndown_report_http_error(self, report_manager, auth_manager):
        """Test burndown report generation with HTTP error."""
        with patch("youtrack_cli.reports.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()

            async def mock_make_request(*args, **kwargs):
                raise Exception("Connection failed")

            mock_client_manager.make_request = mock_make_request
            mock_get_client.return_value = mock_client_manager

            result = await report_manager.generate_burndown_report("TEST")

            assert result["status"] == "error"
            assert "Unexpected error" in result["message"]

    @pytest.mark.asyncio
    async def test_generate_velocity_report_success(self, report_manager, auth_manager):
        """Test successful velocity report generation."""
        mock_project_data = {
            "id": "TEST",
            "name": "Test Project",
            "versions": [
                {"id": "v1", "name": "Sprint 1", "releaseDate": "2024-01-15"},
                {"id": "v2", "name": "Sprint 2", "releaseDate": "2024-01-30"},
            ],
        }

        mock_sprint_issues = [
            {"id": "1", "resolved": 1234567890, "spent": {"value": 120}},
            {"id": "2", "resolved": None, "spent": {"value": 60}},
        ]

        with patch("youtrack_cli.reports.get_client_manager") as mock_get_client:
            mock_client_manager = Mock()
            mock_responses = [
                Mock(json=lambda: mock_project_data),  # Project response
                Mock(json=lambda: mock_sprint_issues),  # Sprint 1 issues
                Mock(json=lambda: mock_sprint_issues),  # Sprint 2 issues
            ]

            response_iter = iter(mock_responses)

            async def mock_make_request(*args, **kwargs):
                return next(response_iter)

            mock_client_manager.make_request = mock_make_request
            mock_get_client.return_value = mock_client_manager

            result = await report_manager.generate_velocity_report("TEST", sprints=2)

            assert result["status"] == "success"
            assert result["data"]["project"] == "TEST"
            assert result["data"]["sprints_analyzed"] == 2
            assert len(result["data"]["sprints"]) == 2
            assert result["data"]["average_issues_per_sprint"] == 1.0
            assert result["data"]["average_effort_per_sprint"] == 3.0

    @pytest.mark.asyncio
    async def test_generate_velocity_report_no_auth(self, report_manager):
        """Test velocity report generation without authentication."""
        report_manager.auth_manager.load_credentials.return_value = None

        result = await report_manager.generate_velocity_report("TEST")

        assert result["status"] == "error"
        assert "Not authenticated" in result["message"]

    def test_display_burndown_report(self, report_manager, capsys):
        """Test burndown report display."""
        burndown_data = {
            "project": "TEST",
            "sprint": "sprint-1",
            "period": "2024-01-01 to 2024-01-31",
            "total_issues": 10,
            "resolved_issues": 7,
            "remaining_issues": 3,
            "completion_rate": 70.0,
            "total_effort_hours": 15.5,
        }

        with patch("rich.console.Console.print") as mock_print:
            report_manager.display_burndown_report(burndown_data)

            # Verify that print was called multiple times with project info
            mock_print.assert_called()
            call_args = [call[0][0] for call in mock_print.call_args_list]
            project_info_found = any("TEST" in str(arg) for arg in call_args)
            assert project_info_found

    def test_display_velocity_report(self, report_manager):
        """Test velocity report display."""
        velocity_data = {
            "project": "TEST",
            "sprints_analyzed": 2,
            "sprints": [
                {
                    "name": "Sprint 1",
                    "release_date": "2024-01-15",
                    "total_issues": 8,
                    "resolved_issues": 6,
                    "total_effort_hours": 12.0,
                },
                {
                    "name": "Sprint 2",
                    "release_date": "2024-01-30",
                    "total_issues": 10,
                    "resolved_issues": 8,
                    "total_effort_hours": 15.0,
                },
            ],
            "average_issues_per_sprint": 9.0,
            "average_effort_per_sprint": 13.5,
        }

        with patch("rich.console.Console.print") as mock_print:
            report_manager.display_velocity_report(velocity_data)

            # Verify that print was called
            mock_print.assert_called()

    def test_display_velocity_report_empty(self, report_manager):
        """Test velocity report display with no sprint data."""
        velocity_data = {"project": "TEST", "sprints_analyzed": 0, "sprints": []}

        with patch("rich.console.Console.print") as mock_print:
            report_manager.display_velocity_report(velocity_data)

            # Verify that it shows "No sprint data available"
            mock_print.assert_called()
            call_args = [call[0][0] for call in mock_print.call_args_list]
            no_data_found = any("No sprint data available" in str(arg) for arg in call_args)
            assert no_data_found


class TestReportsCommands:
    """Test reports CLI commands."""

    def setup_method(self):
        """Set up test method."""
        self.runner = CliRunner()

    @patch("youtrack_cli.main.ReportManager")
    @patch("youtrack_cli.main.AuthManager")
    @patch("youtrack_cli.main.ConfigManager")
    def test_burndown_command_success(self, mock_config, mock_auth, mock_report):
        """Test burndown command execution."""
        # Mock the AuthManager instance to return a username for audit logging
        mock_auth_instance = mock_auth.return_value
        mock_auth_instance.get_current_user_sync.return_value = "test_user"

        # Mock the async function
        mock_report_instance = mock_report.return_value
        mock_report_instance.generate_burndown_report.return_value = {
            "status": "success",
            "data": {
                "project": "TEST",
                "total_issues": 10,
                "resolved_issues": 7,
                "remaining_issues": 3,
                "completion_rate": 70.0,
                "total_effort_hours": 15.5,
            },
        }

        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["reports", "burndown", "TEST"])

            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    @patch("youtrack_cli.main.ReportManager")
    @patch("youtrack_cli.main.AuthManager")
    @patch("youtrack_cli.main.ConfigManager")
    def test_velocity_command_success(self, mock_config, mock_auth, mock_report):
        """Test velocity command execution."""
        # Mock the AuthManager instance to return a username for audit logging
        mock_auth_instance = mock_auth.return_value
        mock_auth_instance.get_current_user_sync.return_value = "test_user"

        # Mock the async function
        mock_report_instance = mock_report.return_value
        mock_report_instance.generate_velocity_report.return_value = {
            "status": "success",
            "data": {
                "project": "TEST",
                "sprints_analyzed": 3,
                "sprints": [],
                "average_issues_per_sprint": 8.0,
                "average_effort_per_sprint": 12.0,
            },
        }

        with patch("asyncio.run") as mock_asyncio:
            result = self.runner.invoke(main, ["reports", "velocity", "TEST", "--sprints", "3"])

            assert result.exit_code == 0
            mock_asyncio.assert_called_once()

    def test_reports_group_help(self):
        """Test reports group help command."""
        result = self.runner.invoke(main, ["reports", "--help"])

        assert result.exit_code == 0
        assert "Generate cross-entity reports" in result.output
        assert "burndown" in result.output
        assert "velocity" in result.output

    def test_burndown_command_help(self):
        """Test burndown command help."""
        result = self.runner.invoke(main, ["reports", "burndown", "--help"])

        assert result.exit_code == 0
        assert "Generate a burndown report" in result.output
        assert "--sprint" in result.output
        assert "--start-date" in result.output
        assert "--end-date" in result.output

    def test_velocity_command_help(self):
        """Test velocity command help."""
        result = self.runner.invoke(main, ["reports", "velocity", "--help"])

        assert result.exit_code == 0
        assert "Generate a velocity report" in result.output
        assert "--sprints" in result.output
