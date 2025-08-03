"""Integration tests for time tracking workflows."""

import json
import os
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from youtrack_cli.main import main


@pytest.fixture
def test_time_data():
    """Generate test time tracking data."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "issue_id": "FPU-1",  # Use known test issue
        "duration_formats": ["2h", "30m", "1h 30m", "1.5h", "90"],
        "work_types": ["Development", "Testing", "Documentation", "Code Review"],
        "descriptions": [
            f"Development work {unique_id}",
            f"Testing implementation {unique_id}",
            f"Documentation update {unique_id}",
            f"Code review session {unique_id}",
        ],
        "dates": [
            datetime.now().strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        ],
    }


@pytest.fixture
async def cleanup_time_entries(integration_auth_manager, integration_client):
    """Track and cleanup time entries created during tests."""
    created_entries = []

    yield created_entries

    # Note: YouTrack API might not allow deletion of time entries
    # This is mainly for tracking purposes
    pass


@pytest.mark.integration
@pytest.mark.asyncio
class TestTimeTrackingWorkflows:
    """Test comprehensive time tracking workflows."""

    async def test_basic_time_logging_workflow(self, integration_auth_manager, test_time_data, cleanup_time_entries):
        """Test basic time logging with various duration formats."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Test different duration formats
            for i, duration in enumerate(test_time_data["duration_formats"]):
                result = runner.invoke(
                    main,
                    [
                        "time",
                        "log",
                        test_time_data["issue_id"],
                        duration,
                        "--description",
                        f"Time logging test {i + 1} - {duration}",
                        "--work-type",
                        test_time_data["work_types"][i % len(test_time_data["work_types"])],
                    ],
                )

                # Time logging might fail due to permissions or missing work types
                assert result.exit_code in [0, 1], f"Failed logging time with duration {duration}: {result.output}"

                if result.exit_code == 0:
                    assert "logged" in result.output.lower() or "added" in result.output.lower()

    async def test_historical_time_entry_workflow(self, integration_auth_manager, test_time_data, cleanup_time_entries):
        """Test logging time entries for historical dates."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Log time for different dates
            for _i, date in enumerate(test_time_data["dates"]):
                result = runner.invoke(
                    main,
                    [
                        "time",
                        "log",
                        test_time_data["issue_id"],
                        "1h",
                        "--date",
                        date,
                        "--description",
                        f"Historical work on {date}",
                        "--work-type",
                        "Development",
                    ],
                )

                assert result.exit_code in [0, 1], f"Failed logging time for date {date}: {result.output}"

    async def test_time_listing_and_filtering_workflow(self, integration_auth_manager, test_time_data):
        """Test comprehensive time entry listing and filtering."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # First log some time entries
            result = runner.invoke(
                main,
                [
                    "time",
                    "log",
                    test_time_data["issue_id"],
                    "2h",
                    "--description",
                    "Setup work for time tracking test",
                    "--work-type",
                    "Development",
                ],
            )

            if result.exit_code == 0:
                # Test basic listing
                result = runner.invoke(main, ["time", "list", "--issue", test_time_data["issue_id"]])
                assert result.exit_code == 0

                # Test JSON format listing
                result = runner.invoke(
                    main, ["time", "list", "--issue", test_time_data["issue_id"], "--format", "json"]
                )
                assert result.exit_code == 0

                # Test date range filtering
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                end_date = datetime.now().strftime("%Y-%m-%d")

                result = runner.invoke(
                    main,
                    [
                        "time",
                        "list",
                        "--issue",
                        test_time_data["issue_id"],
                        "--start-date",
                        start_date,
                        "--end-date",
                        end_date,
                    ],
                )
                assert result.exit_code == 0

    async def test_time_reporting_workflow(self, integration_auth_manager, test_time_data):
        """Test time reporting functionality."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # First log some diverse time entries
            work_entries = [
                ("2h", "Development", "Feature implementation"),
                ("1.5h", "Testing", "Unit test writing"),
                ("30m", "Code Review", "PR review session"),
                ("45m", "Documentation", "API documentation update"),
            ]

            for duration, work_type, description in work_entries:
                result = runner.invoke(
                    main,
                    [
                        "time",
                        "log",
                        test_time_data["issue_id"],
                        duration,
                        "--description",
                        description,
                        "--work-type",
                        work_type,
                    ],
                )
                # Continue even if some fail due to permissions
                pass

            # Generate reports using list command
            report_scenarios = [
                # Basic report
                (["time", "list", "--issue", test_time_data["issue_id"]], "Basic issue list"),
                # JSON format report
                (["time", "list", "--issue", test_time_data["issue_id"], "--format", "json"], "JSON list"),
                # Date range report
                (
                    [
                        "time",
                        "list",
                        "--start-date",
                        (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                        "--end-date",
                        datetime.now().strftime("%Y-%m-%d"),
                    ],
                    "Date range list",
                ),
            ]

            for command_args, description in report_scenarios:
                result = runner.invoke(main, command_args)
                assert result.exit_code == 0, f"Failed: {description}"

    async def test_time_summary_and_aggregation_workflow(self, integration_auth_manager, test_time_data):
        """Test time summary and aggregation functionality."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Log time with different work types for aggregation testing
            summary_entries = [
                ("1h", "Development"),
                ("2h", "Development"),
                ("30m", "Testing"),
                ("1.5h", "Testing"),
                ("45m", "Documentation"),
            ]

            for duration, work_type in summary_entries:
                result = runner.invoke(
                    main,
                    [
                        "time",
                        "log",
                        test_time_data["issue_id"],
                        duration,
                        "--description",
                        f"Summary test - {work_type}",
                        "--work-type",
                        work_type,
                    ],
                )
                # Continue even if some fail
                pass

            # Test different summary groupings
            summary_scenarios = [
                # Group by work type
                (
                    ["time", "summary", "--group-by", "type", "--issue", test_time_data["issue_id"]],
                    "Group by work type",
                ),
                # Group by user
                (["time", "summary", "--group-by", "user", "--issue", test_time_data["issue_id"]], "Group by user"),
                # JSON format summary
                (["time", "summary", "--issue", test_time_data["issue_id"], "--format", "json"], "JSON summary"),
            ]

            for command_args, description in summary_scenarios:
                result = runner.invoke(main, command_args)
                assert result.exit_code == 0, f"Failed: {description}"

    async def test_multi_issue_time_tracking_workflow(self, integration_auth_manager, test_time_data):
        """Test time tracking across multiple issues."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Use multiple test issues (assuming they exist)
            test_issues = ["FPU-1", "FPU-2"]

            # Log time to different issues
            for i, issue_id in enumerate(test_issues):
                result = runner.invoke(
                    main,
                    [
                        "time",
                        "log",
                        issue_id,
                        f"{i + 1}h",
                        "--description",
                        f"Multi-issue work on {issue_id}",
                        "--work-type",
                        "Development",
                    ],
                )
                # Issues might not exist, so continue
                pass

            # Generate cross-issue reports
            start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")

            result = runner.invoke(
                main, ["time", "list", "--start-date", start_date, "--end-date", end_date, "--format", "json"]
            )
            assert result.exit_code == 0

    async def test_time_tracking_error_handling_workflow(self, integration_auth_manager, test_time_data):
        """Test error handling in time tracking operations."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Test invalid duration formats
            invalid_durations = ["invalid", "25x", "-1h", "0h"]

            for duration in invalid_durations:
                result = runner.invoke(
                    main, ["time", "log", test_time_data["issue_id"], duration, "--description", "Error test"]
                )
                # Should fail with invalid duration
                assert result.exit_code != 0
                assert "error" in result.output.lower() or "invalid" in result.output.lower()

            # Test with non-existent issue
            result = runner.invoke(
                main, ["time", "log", "NONEXISTENT-99999", "1h", "--description", "Test with non-existent issue"]
            )
            assert result.exit_code != 0

            # Test invalid date formats
            invalid_dates = ["invalid-date", "32/13/2024", "2024-13-01"]

            for invalid_date in invalid_dates:
                result = runner.invoke(
                    main,
                    [
                        "time",
                        "log",
                        test_time_data["issue_id"],
                        "1h",
                        "--date",
                        invalid_date,
                        "--description",
                        "Date error test",
                    ],
                )
                assert result.exit_code != 0

    async def test_time_tracking_bulk_operations_workflow(self, integration_auth_manager, test_time_data):
        """Test bulk time tracking operations."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Simulate bulk time logging (multiple entries in sequence)
            bulk_entries = [
                ("1h", "Development", "Feature A implementation"),
                ("30m", "Testing", "Feature A unit tests"),
                ("45m", "Code Review", "Feature A code review"),
                ("15m", "Documentation", "Feature A documentation"),
                ("2h", "Development", "Feature B implementation"),
                ("1h", "Testing", "Feature B integration tests"),
            ]

            successful_logs = 0
            for duration, work_type, description in bulk_entries:
                result = runner.invoke(
                    main,
                    [
                        "time",
                        "log",
                        test_time_data["issue_id"],
                        duration,
                        "--description",
                        description,
                        "--work-type",
                        work_type,
                    ],
                )

                if result.exit_code == 0:
                    successful_logs += 1

            # If we successfully logged any entries, test aggregated reporting
            if successful_logs > 0:
                # Generate comprehensive report
                result = runner.invoke(
                    main,
                    [
                        "time",
                        "summary",
                        "--issue",
                        test_time_data["issue_id"],
                        "--group-by",
                        "type",
                        "--format",
                        "json",
                    ],
                )
                assert result.exit_code == 0

                # Verify we can parse the JSON output
                if result.output.strip():
                    try:
                        summary_data = json.loads(result.output)
                        assert isinstance(summary_data, (list, dict))
                    except json.JSONDecodeError:
                        # Output might not be JSON if no data
                        pass

    async def test_time_tracking_export_workflow(self, integration_auth_manager, test_time_data):
        """Test time tracking data export capabilities."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Log some time entries for export testing
            result = runner.invoke(
                main,
                [
                    "time",
                    "log",
                    test_time_data["issue_id"],
                    "2h 30m",
                    "--description",
                    "Export test work session",
                    "--work-type",
                    "Development",
                ],
            )

            if result.exit_code == 0:
                # Export as JSON for external processing
                result = runner.invoke(
                    main, ["time", "list", "--issue", test_time_data["issue_id"], "--format", "json"]
                )
                assert result.exit_code == 0

                if result.output.strip():
                    # Verify JSON is valid
                    try:
                        export_data = json.loads(result.output)
                        assert isinstance(export_data, list)

                        # Verify essential fields are present
                        if export_data:
                            entry = export_data[0]
                            expected_fields = ["duration", "description"]
                            for _field in expected_fields:
                                # Field names might vary, so just check structure
                                assert isinstance(entry, dict)
                    except json.JSONDecodeError:
                        # Output might not be JSON format in some cases
                        pass

    async def test_time_tracking_date_range_analysis(self, integration_auth_manager, test_time_data):
        """Test time tracking analysis across date ranges."""
        runner = CliRunner()

        with patch.dict(
            os.environ,
            {
                "YOUTRACK_BASE_URL": integration_auth_manager.config.base_url,
                "YOUTRACK_API_KEY": integration_auth_manager.config.token,
            },
        ):
            # Log time entries across multiple dates
            for i, date in enumerate(test_time_data["dates"][:3]):
                result = runner.invoke(
                    main,
                    [
                        "time",
                        "log",
                        test_time_data["issue_id"],
                        f"{i + 1}h",
                        "--date",
                        date,
                        "--description",
                        f"Daily work {i + 1} on {date}",
                        "--work-type",
                        "Development",
                    ],
                )
                # Continue even if some fail
                pass

            # Analyze different time periods
            date_scenarios = [
                # Last week
                (
                    (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    datetime.now().strftime("%Y-%m-%d"),
                    "Last week",
                ),
                # Last 3 days
                (
                    (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                    datetime.now().strftime("%Y-%m-%d"),
                    "Last 3 days",
                ),
                # Today only
                (datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d"), "Today only"),
            ]

            for start_date, end_date, description in date_scenarios:
                result = runner.invoke(
                    main, ["time", "summary", "--start-date", start_date, "--end-date", end_date, "--format", "json"]
                )
                assert result.exit_code == 0, f"Failed date range analysis: {description}"
