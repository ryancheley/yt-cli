"""Tests for utility functions in utils.py."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from youtrack_cli.exceptions import (
    CommandValidationError,
    ParameterError,
    UsageError,
    YouTrackError,
)
from youtrack_cli.utils import (
    PaginationConfig,
    PaginationType,
    batch_get_resources,
    batch_requests,
    display_error,
    display_info,
    display_success,
    display_warning,
    format_timestamp,
    handle_error,
    make_request,
    optimize_fields,
    paginate_articles,
    paginate_issues,
    paginate_projects,
    paginate_results,
    paginate_users,
    stream_large_response,
)


class TestPaginationType:
    """Test PaginationType enum."""

    def test_pagination_type_values(self):
        """Test pagination type enum values."""
        assert PaginationType.CURSOR.value == "cursor"
        assert PaginationType.OFFSET.value == "offset"


class TestPaginationConfig:
    """Test PaginationConfig class."""

    def test_default_values(self):
        """Test default pagination configuration values."""
        assert PaginationConfig.DEFAULT_API_PAGE_SIZE == 100
        assert PaginationConfig.DEFAULT_DISPLAY_PAGE_SIZE == 50
        assert isinstance(PaginationConfig.MAX_RESULTS_PER_ENTITY, dict)
        assert isinstance(PaginationConfig.PAGINATION_SUPPORT, dict)

    def test_get_pagination_type_known_endpoints(self):
        """Test pagination type detection for known endpoints."""
        assert PaginationConfig.get_pagination_type("/api/issues") == PaginationType.CURSOR
        assert PaginationConfig.get_pagination_type("/api/admin/projects") == PaginationType.OFFSET
        assert PaginationConfig.get_pagination_type("/api/users") == PaginationType.OFFSET
        assert PaginationConfig.get_pagination_type("/api/articles") == PaginationType.OFFSET

    def test_get_pagination_type_unknown_endpoint(self):
        """Test pagination type detection for unknown endpoints defaults to offset."""
        with patch("youtrack_cli.utils.logger") as mock_logger:
            result = PaginationConfig.get_pagination_type("/api/unknown")
            assert result == PaginationType.OFFSET
            mock_logger.debug.assert_called_once()

    def test_get_max_results_known_entities(self):
        """Test max results for known entity types."""
        assert PaginationConfig.get_max_results("issues") == 10000
        assert PaginationConfig.get_max_results("projects") == 1000
        assert PaginationConfig.get_max_results("users") == 5000
        assert PaginationConfig.get_max_results("articles") == 2000
        assert PaginationConfig.get_max_results("reports") == 1000

    def test_get_max_results_unknown_entity(self):
        """Test max results for unknown entity types defaults to 1000."""
        assert PaginationConfig.get_max_results("unknown") == 1000


class TestMakeRequest:
    """Test make_request function."""

    @pytest.mark.asyncio
    async def test_make_request_success(self):
        """Test successful HTTP request."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        mock_client_manager = Mock()
        mock_client_manager.make_request = AsyncMock(return_value=mock_response)

        with patch("youtrack_cli.utils.get_client_manager", return_value=mock_client_manager):
            response = await make_request("GET", "https://test.com")

            assert response == mock_response
            mock_client_manager.make_request.assert_called_once_with(
                method="GET",
                url="https://test.com",
                headers=None,
                params=None,
                json_data=None,
                timeout=None,
                max_retries=3,
            )

    @pytest.mark.asyncio
    async def test_make_request_with_parameters(self):
        """Test HTTP request with all parameters."""
        mock_response = Mock(spec=httpx.Response)
        mock_client_manager = Mock()
        mock_client_manager.make_request = AsyncMock(return_value=mock_response)

        headers = {"Authorization": "Bearer token"}
        params = {"query": "test"}
        json_data = {"data": "value"}

        with patch("youtrack_cli.utils.get_client_manager", return_value=mock_client_manager):
            response = await make_request(
                "POST",
                "https://test.com",
                headers=headers,
                params=params,
                json_data=json_data,
                timeout=30.0,
                max_retries=5,
            )

            assert response == mock_response
            mock_client_manager.make_request.assert_called_once_with(
                method="POST",
                url="https://test.com",
                headers=headers,
                params=params,
                json_data=json_data,
                timeout=30.0,
                max_retries=5,
            )


class TestPaginateResults:
    """Test paginate_results function."""

    @pytest.mark.asyncio
    async def test_paginate_results_cursor_pagination_auto_detect(self):
        """Test cursor pagination with auto-detection."""
        mock_response_data = {
            "results": [{"id": 1}, {"id": 2}],
            "hasAfter": False,
            "hasBefore": False,
            "afterCursor": "cursor123",
            "beforeCursor": "cursor456",
        }

        with patch("youtrack_cli.utils.make_request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response

            result = await paginate_results("/api/issues")

            assert result["results"] == [{"id": 1}, {"id": 2}]
            assert result["total_results"] == 2
            assert result["pagination_type"] == "cursor"
            assert result["has_after"] is False
            assert result["has_before"] is False
            assert result["after_cursor"] == "cursor123"
            assert result["before_cursor"] == "cursor456"

    @pytest.mark.asyncio
    async def test_paginate_results_offset_pagination(self):
        """Test offset pagination."""
        mock_response_data = [{"id": 1}, {"id": 2}]

        with patch("youtrack_cli.utils.make_request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response

            result = await paginate_results("/api/admin/projects", use_cursor_pagination=False)

            assert result["results"] == [{"id": 1}, {"id": 2}]
            assert result["total_results"] == 2
            assert result["pagination_type"] == "offset"
            assert result["after_cursor"] is None
            assert result["before_cursor"] is None

    @pytest.mark.asyncio
    async def test_paginate_results_with_max_results(self):
        """Test pagination with max results limit."""
        mock_response_data = [{"id": i} for i in range(150)]

        with patch("youtrack_cli.utils.make_request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response

            result = await paginate_results("/api/admin/projects", max_results=100)

            assert len(result["results"]) == 100
            assert result["total_results"] == 100

    @pytest.mark.asyncio
    async def test_paginate_results_cursor_validation_error(self):
        """Test cursor pagination parameter validation."""
        with pytest.raises(ValueError, match="Cannot specify both after_cursor and before_cursor"):
            await paginate_results(
                "/api/issues",
                after_cursor="after",
                before_cursor="before",
                use_cursor_pagination=True,
            )

    @pytest.mark.asyncio
    async def test_paginate_results_json_parsing_error(self):
        """Test handling of JSON parsing errors."""
        with patch("youtrack_cli.utils.make_request") as mock_request:
            mock_response = Mock()
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_request.return_value = mock_response

            with pytest.raises(YouTrackError, match="Failed to parse response"):
                await paginate_results("/api/issues")


class TestSpecificPaginationFunctions:
    """Test specific pagination wrapper functions."""

    @pytest.mark.asyncio
    async def test_paginate_issues(self):
        """Test issues pagination wrapper."""
        with patch("youtrack_cli.utils.paginate_results") as mock_paginate:
            mock_result = {"results": [], "total_results": 0}
            mock_paginate.return_value = mock_result

            result = await paginate_issues("/api/issues")

            assert result == mock_result
            mock_paginate.assert_called_once_with(
                endpoint="/api/issues",
                headers=None,
                params=None,
                page_size=None,
                max_results=10000,  # Issues max results
                after_cursor=None,
                before_cursor=None,
                use_cursor_pagination=True,
            )

    @pytest.mark.asyncio
    async def test_paginate_projects(self):
        """Test projects pagination wrapper."""
        with patch("youtrack_cli.utils.paginate_results") as mock_paginate:
            mock_result = {"results": [], "total_results": 0}
            mock_paginate.return_value = mock_result

            result = await paginate_projects("/api/admin/projects")

            assert result == mock_result
            mock_paginate.assert_called_once_with(
                endpoint="/api/admin/projects",
                headers=None,
                params=None,
                page_size=None,
                max_results=1000,  # Projects max results
                use_cursor_pagination=False,
            )

    @pytest.mark.asyncio
    async def test_paginate_users(self):
        """Test users pagination wrapper."""
        with patch("youtrack_cli.utils.paginate_results") as mock_paginate:
            mock_result = {"results": [], "total_results": 0}
            mock_paginate.return_value = mock_result

            result = await paginate_users("/api/users")

            assert result == mock_result
            mock_paginate.assert_called_once_with(
                endpoint="/api/users",
                headers=None,
                params=None,
                page_size=None,
                max_results=5000,  # Users max results
                use_cursor_pagination=False,
            )

    @pytest.mark.asyncio
    async def test_paginate_articles(self):
        """Test articles pagination wrapper."""
        with patch("youtrack_cli.utils.paginate_results") as mock_paginate:
            mock_result = {"results": [], "total_results": 0}
            mock_paginate.return_value = mock_result

            result = await paginate_articles("/api/articles")

            assert result == mock_result
            mock_paginate.assert_called_once_with(
                endpoint="/api/articles",
                headers=None,
                params=None,
                page_size=None,
                max_results=2000,  # Articles max results
                use_cursor_pagination=False,
            )


class TestBatchRequests:
    """Test batch request functions."""

    @pytest.mark.asyncio
    async def test_batch_requests(self):
        """Test batch HTTP requests."""
        requests = [
            {"method": "GET", "url": "https://test.com/1"},
            {"method": "GET", "url": "https://test.com/2"},
        ]
        mock_responses = [Mock(), Mock()]

        mock_client_manager = Mock()
        mock_client_manager.batch_requests = AsyncMock(return_value=mock_responses)

        with patch("youtrack_cli.utils.get_client_manager", return_value=mock_client_manager):
            responses = await batch_requests(requests, max_concurrent=5)

            assert responses == mock_responses
            mock_client_manager.batch_requests.assert_called_once_with(requests, 5)

    @pytest.mark.asyncio
    async def test_batch_get_resources_success(self):
        """Test successful batch resource fetching."""
        base_url = "https://test.com/issues/{id}"
        resource_ids = ["PROJ-1", "PROJ-2"]

        mock_responses = []
        for i, resource_id in enumerate(resource_ids):
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": resource_id, "data": f"test{i}"}
            mock_responses.append(mock_response)

        with patch("youtrack_cli.utils.batch_requests", return_value=mock_responses):
            results = await batch_get_resources(base_url, resource_ids)

            assert len(results) == 2
            assert results[0]["id"] == "PROJ-1"
            assert results[1]["id"] == "PROJ-2"

    @pytest.mark.asyncio
    async def test_batch_get_resources_with_failures(self):
        """Test batch resource fetching with some failures."""
        base_url = "https://test.com/issues/{id}"
        resource_ids = ["PROJ-1", "PROJ-2"]

        # First request succeeds, second fails
        mock_responses = []
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = {"id": "PROJ-1"}
        mock_responses.append(mock_response1)

        mock_response2 = Mock()
        mock_response2.status_code = 404
        mock_responses.append(mock_response2)

        with patch("youtrack_cli.utils.batch_requests", return_value=mock_responses):
            with patch("youtrack_cli.utils.logger") as mock_logger:
                results = await batch_get_resources(base_url, resource_ids)

                assert len(results) == 2
                assert results[0]["id"] == "PROJ-1"
                assert results[1] is None
                mock_logger.warning.assert_called_once()

    def test_batch_get_resources_invalid_url(self):
        """Test batch resource fetching with invalid URL."""
        with pytest.raises(ValueError, match="base_url must contain {id} placeholder"):
            asyncio.run(batch_get_resources("https://test.com/issues", ["PROJ-1"]))


class TestOptimizeFields:
    """Test optimize_fields function."""

    def test_optimize_fields_with_field_selection(self):
        """Test field optimization with field selection."""
        base_params = {"query": "test"}
        fields = ["id", "summary", "state"]

        with patch("youtrack_cli.utils.logger") as mock_logger:
            result = optimize_fields(base_params, fields=fields)

            assert result["query"] == "test"
            assert result["fields"] == "id,summary,state"
            mock_logger.debug.assert_called_once_with("Field selection applied", fields=fields)

    def test_optimize_fields_with_exclude_fields(self):
        """Test field optimization with exclude fields."""
        base_params = {"query": "test"}
        exclude_fields = ["description", "comments"]

        with patch("youtrack_cli.utils.logger") as mock_logger:
            result = optimize_fields(base_params, exclude_fields=exclude_fields)

            assert result["query"] == "test"
            assert result["_exclude_fields"] == exclude_fields
            mock_logger.debug.assert_called_once_with("Fields to exclude noted", exclude_fields=exclude_fields)

    def test_optimize_fields_empty_params(self):
        """Test field optimization with empty base params."""
        fields = ["id", "summary"]

        result = optimize_fields(fields=fields)

        assert result["fields"] == "id,summary"

    def test_optimize_fields_no_modifications(self):
        """Test field optimization with no modifications."""
        base_params = {"query": "test"}

        result = optimize_fields(base_params)

        assert result == {"query": "test"}


class TestStreamLargeResponse:
    """Test stream_large_response function."""

    @pytest.mark.asyncio
    async def test_stream_large_response_success(self):
        """Test successful streaming response."""
        mock_chunks = [b"chunk1", b"chunk2", b"chunk3"]

        async def mock_aiter_bytes(chunk_size):
            for chunk in mock_chunks:
                yield chunk

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.aiter_bytes = mock_aiter_bytes

        mock_client = Mock()
        mock_client.stream.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_client.stream.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_client_manager = Mock()
        mock_client_manager.get_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_manager.get_client.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("youtrack_cli.utils.get_client_manager", return_value=mock_client_manager):
            chunks = []
            async for chunk in stream_large_response("https://test.com"):
                chunks.append(chunk)

            assert chunks == mock_chunks

    @pytest.mark.asyncio
    async def test_stream_large_response_error(self):
        """Test streaming response with error status."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.aread = AsyncMock(return_value=b"Not found")

        mock_client = Mock()
        mock_client.stream.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_client.stream.return_value.__aexit__ = AsyncMock(return_value=None)

        mock_client_manager = Mock()
        mock_client_manager.get_client.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_manager.get_client.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("youtrack_cli.utils.get_client_manager", return_value=mock_client_manager):
            with pytest.raises(YouTrackError, match="Stream request failed with status 404"):
                async for _chunk in stream_large_response("https://test.com"):
                    pass


class TestHandleError:
    """Test handle_error function."""

    def test_handle_error_youtrack_error(self):
        """Test handling YouTrackError."""
        error = YouTrackError("API error", suggestion="Try again")

        with patch("youtrack_cli.utils.logger") as mock_logger:
            result = handle_error(error, "test operation")

            assert result["status"] == "error"
            assert result["message"] == "API error"
            assert result["suggestion"] == "Try again"
            mock_logger.error.assert_called_once()

    def test_handle_error_usage_error(self):
        """Test handling UsageError with enhanced information."""
        error = UsageError(
            "Invalid usage",
            command_path="yt command",
            usage_syntax="yt command [options]",
            examples=["yt issues list", "yt projects create"],
            common_mistakes=["Don't use spaces", "Remember the dash"],
        )

        result = handle_error(error)

        assert result["status"] == "error"
        assert result["message"] == "Invalid usage"
        assert result["usage_syntax"] == "yt command [options]"
        assert result["examples"] == ["yt issues list", "yt projects create"]
        assert result["common_mistakes"] == ["Don't use spaces", "Remember the dash"]

    def test_handle_error_command_validation_error(self):
        """Test handling CommandValidationError."""
        error = CommandValidationError(
            "Invalid command",
            similar_commands=["issues", "projects"],
            usage_example="yt issues list",
        )

        result = handle_error(error)

        assert result["status"] == "error"
        assert result["similar_commands"] == ["issues", "projects"]
        assert result["usage_example"] == "yt issues list"

    def test_handle_error_parameter_error(self):
        """Test handling ParameterError."""
        error = ParameterError(
            "Invalid parameter",
            parameter_name="priority",
            valid_choices=["low", "medium", "high"],
            usage_example="--priority high",
        )

        result = handle_error(error)

        assert result["status"] == "error"
        assert result["parameter_name"] == "priority"
        assert result["valid_choices"] == ["low", "medium", "high"]
        assert result["usage_example"] == "--priority high"

    def test_handle_error_unexpected_error(self):
        """Test handling unexpected errors."""
        error = ValueError("Unexpected error")

        with patch("youtrack_cli.utils.logger") as mock_logger:
            result = handle_error(error, "test operation")

            assert result["status"] == "error"
            assert "unexpected error occurred" in result["message"].lower()
            assert "try again" in result["suggestion"].lower()
            mock_logger.error.assert_called_once()


class TestDisplayFunctions:
    """Test display utility functions."""

    def test_display_error_basic(self):
        """Test basic error display."""
        error_result = {"message": "Test error"}

        with patch("youtrack_cli.utils.console") as mock_console:
            display_error(error_result)

            mock_console.print.assert_called_once_with("[red]❌ Error:[/red] Test error")

    def test_display_error_with_usage_syntax(self):
        """Test error display with usage syntax."""
        error_result = {
            "message": "Usage error",
            "usage_syntax": "yt command [options]",
            "examples": ["yt issues list", "yt projects create"],
            "common_mistakes": ["Don't forget the dash"],
        }

        with patch("youtrack_cli.utils.console") as mock_console:
            display_error(error_result)

            # Should print error message, usage, examples, and common mistakes
            assert mock_console.print.call_count >= 4

    def test_display_error_with_similar_commands(self):
        """Test error display with similar commands."""
        error_result = {
            "message": "Command error",
            "similar_commands": ["issues", "projects"],
            "usage_example": "yt issues list",
        }

        with patch("youtrack_cli.utils.console") as mock_console:
            display_error(error_result)

            # Should print error, suggestions, and usage
            assert mock_console.print.call_count >= 3

    def test_display_error_with_parameter_info(self):
        """Test error display with parameter information."""
        error_result = {
            "message": "Parameter error",
            "parameter_name": "priority",
            "valid_choices": ["low", "medium", "high"],
            "usage_example": "--priority high",
        }

        with patch("youtrack_cli.utils.console") as mock_console:
            display_error(error_result)

            # Should print error, choices, and usage
            assert mock_console.print.call_count >= 3

    def test_display_success(self):
        """Test success message display."""
        with patch("youtrack_cli.utils.console") as mock_console:
            display_success("Operation completed")

            mock_console.print.assert_called_once_with("[green]Success:[/green] Operation completed")

    def test_display_info(self):
        """Test info message display."""
        with patch("youtrack_cli.utils.console") as mock_console:
            display_info("Information message")

            mock_console.print.assert_called_once_with("[blue]Info:[/blue] Information message")

    def test_display_warning(self):
        """Test warning message display."""
        with patch("youtrack_cli.utils.console") as mock_console:
            display_warning("Warning message")

            mock_console.print.assert_called_once_with("[yellow]Warning:[/yellow] Warning message")


class TestFormatTimestamp:
    """Test format_timestamp function."""

    def test_format_timestamp_none(self):
        """Test formatting None timestamp."""
        assert format_timestamp(None) == "N/A"

    def test_format_timestamp_integer(self):
        """Test formatting integer timestamp (milliseconds)."""
        # January 1, 2023 at 12:00:00 UTC (1672574400000 ms)
        timestamp = 1672574400000
        result = format_timestamp(timestamp)
        # Just check that it returns a properly formatted date (timezone may vary)
        assert "2023-01-01" in result
        assert len(result.split()) == 2  # Should have date and time parts

    def test_format_timestamp_string_digits(self):
        """Test formatting string timestamp with digits."""
        timestamp = "1672574400000"
        result = format_timestamp(timestamp)
        # Just check that it returns a properly formatted date (timezone may vary)
        assert "2023-01-01" in result
        assert len(result.split()) == 2  # Should have date and time parts

    def test_format_timestamp_iso_string(self):
        """Test formatting ISO format string."""
        timestamp = "2023-01-01T12:00:00Z"
        result = format_timestamp(timestamp)
        assert "2023-01-01 12:00:00" in result

    def test_format_timestamp_invalid_string(self):
        """Test formatting invalid string returns as-is."""
        timestamp = "invalid-date"
        result = format_timestamp(timestamp)
        assert result == "invalid-date"

    def test_format_timestamp_empty_string(self):
        """Test formatting empty string."""
        assert format_timestamp("") == "N/A"
        assert format_timestamp("   ") == "N/A"

    def test_format_timestamp_overflow_error(self):
        """Test formatting timestamp that causes overflow."""
        # Very large timestamp that might cause overflow
        timestamp = 9999999999999999999

        with patch("youtrack_cli.utils.logger") as mock_logger:
            result = format_timestamp(timestamp)

            # Should return string representation and log warning
            assert result == str(timestamp)
            mock_logger.warning.assert_called_once()

    def test_format_timestamp_type_error(self):
        """Test formatting timestamp with wrong type."""
        # List doesn't meet int/str conditions, so returns N/A without warning
        result = format_timestamp([1, 2, 3])
        assert result == "N/A"

    def test_format_timestamp_exception_error(self):
        """Test formatting timestamp that causes exception and logs warning."""
        # Mock a timestamp that causes an exception during processing
        with patch("youtrack_cli.utils.datetime") as mock_datetime:
            mock_datetime.fromtimestamp.side_effect = ValueError("Invalid timestamp")

            with patch("youtrack_cli.utils.logger") as mock_logger:
                result = format_timestamp(1234567890000)  # This will trigger the exception

                # Should return the string representation and log warning
                assert result == "1234567890000"
                mock_logger.warning.assert_called_once()
