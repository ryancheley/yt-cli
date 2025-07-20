"""Tests for batch operations functionality."""

import csv
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from youtrack_cli.auth import AuthManager
from youtrack_cli.batch import (
    BatchIssueCreate,
    BatchIssueUpdate,
    BatchOperationManager,
    BatchOperationResult,
    BatchValidationError,
    generate_template_files,
)


class TestBatchModels:
    """Test batch operation models."""

    def test_batch_issue_create_valid(self):
        """Test valid BatchIssueCreate model."""
        data = {
            "project_id": "TEST",
            "summary": "Test issue",
            "description": "Test description",
            "type": "Bug",
            "priority": "High",
            "assignee": "test.user",
        }

        issue = BatchIssueCreate(**data)
        assert issue.project_id == "TEST"
        assert issue.summary == "Test issue"
        assert issue.description == "Test description"
        assert issue.type == "Bug"
        assert issue.priority == "High"
        assert issue.assignee == "test.user"

    def test_batch_issue_create_minimal(self):
        """Test BatchIssueCreate with minimal required fields."""
        data = {"project_id": "TEST", "summary": "Test issue"}

        issue = BatchIssueCreate(**data)
        assert issue.project_id == "TEST"
        assert issue.summary == "Test issue"
        assert issue.description is None
        assert issue.type is None
        assert issue.priority is None
        assert issue.assignee is None

    def test_batch_issue_create_missing_required(self):
        """Test BatchIssueCreate with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            BatchIssueCreate(summary="Missing project_id")

        assert isinstance(exc_info.value, ValidationError)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("project_id",) for error in errors)

    def test_batch_issue_update_valid(self):
        """Test valid BatchIssueUpdate model."""
        data = {"issue_id": "TEST-123", "summary": "Updated summary", "state": "In Progress", "priority": "Medium"}

        issue = BatchIssueUpdate(**data)
        assert issue.issue_id == "TEST-123"
        assert issue.summary == "Updated summary"
        assert issue.state == "In Progress"
        assert issue.priority == "Medium"
        assert issue.description is None
        assert issue.type is None
        assert issue.assignee is None

    def test_batch_issue_update_missing_required(self):
        """Test BatchIssueUpdate with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            BatchIssueUpdate(summary="Missing issue_id")

        assert isinstance(exc_info.value, ValidationError)
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("issue_id",) for error in errors)

    def test_batch_operation_result(self):
        """Test BatchOperationResult model."""
        result = BatchOperationResult(operation="create", total_items=10, successful=8, failed=2, duration_seconds=15.5)

        assert result.operation == "create"
        assert result.total_items == 10
        assert result.successful == 8
        assert result.failed == 2
        assert result.duration_seconds == 15.5
        assert result.errors == []
        assert result.created_items == []
        assert result.dry_run is False


class TestBatchOperationManager:
    """Test BatchOperationManager functionality."""

    @pytest.fixture
    def auth_manager(self):
        """Mock AuthManager for testing."""
        return MagicMock(spec=AuthManager)

    @pytest.fixture
    def batch_manager(self, auth_manager):
        """Create BatchOperationManager for testing."""
        with patch("youtrack_cli.batch.IssueManager"):
            return BatchOperationManager(auth_manager)

    def test_init(self, auth_manager):
        """Test BatchOperationManager initialization."""
        with patch("youtrack_cli.batch.IssueManager") as mock_issue_manager:
            manager = BatchOperationManager(auth_manager)
            assert manager.auth_manager == auth_manager
            mock_issue_manager.assert_called_once_with(auth_manager)

    def create_temp_csv(self, data, headers=None):
        """Helper to create temporary CSV file."""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        writer = csv.writer(temp_file)

        if headers:
            writer.writerow(headers)

        for row in data:
            writer.writerow(row)

        temp_file.close()
        return Path(temp_file.name)

    def create_temp_json(self, data):
        """Helper to create temporary JSON file."""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(data, temp_file, indent=2)
        temp_file.close()
        return Path(temp_file.name)

    def test_validate_csv_file_create_valid(self, batch_manager):
        """Test CSV validation for create operations with valid data."""
        headers = ["project_id", "summary", "description", "type", "priority", "assignee"]
        data = [
            ["TEST", "Issue 1", "Description 1", "Bug", "High", "user1"],
            ["TEST", "Issue 2", "Description 2", "Feature", "Medium", "user2"],
        ]

        csv_file = self.create_temp_csv(data, headers)

        try:
            result = batch_manager.validate_csv_file(csv_file, "create")
            assert len(result) == 2
            assert all(isinstance(item, BatchIssueCreate) for item in result)
            assert result[0].project_id == "TEST"
            assert result[0].summary == "Issue 1"
            assert result[1].summary == "Issue 2"
        finally:
            csv_file.unlink()

    def test_validate_csv_file_create_missing_required(self, batch_manager):
        """Test CSV validation with missing required fields."""
        headers = ["summary", "description"]  # Missing project_id
        data = [["Issue 1", "Description 1"], ["Issue 2", "Description 2"]]

        csv_file = self.create_temp_csv(data, headers)

        try:
            with pytest.raises(BatchValidationError) as exc_info:
                batch_manager.validate_csv_file(csv_file, "create")

            assert "Validation failed" in str(exc_info.value)
            assert isinstance(exc_info.value, BatchValidationError)
            assert len(exc_info.value.errors) == 2  # Both rows missing project_id
        finally:
            csv_file.unlink()

    def test_validate_csv_file_update_valid(self, batch_manager):
        """Test CSV validation for update operations with valid data."""
        headers = ["issue_id", "summary", "state", "priority"]
        data = [["TEST-1", "Updated Issue 1", "In Progress", "High"], ["TEST-2", "Updated Issue 2", "Done", "Medium"]]

        csv_file = self.create_temp_csv(data, headers)

        try:
            result = batch_manager.validate_csv_file(csv_file, "update")
            assert len(result) == 2
            assert all(isinstance(item, BatchIssueUpdate) for item in result)
            assert result[0].issue_id == "TEST-1"
            assert result[0].summary == "Updated Issue 1"
        finally:
            csv_file.unlink()

    def test_validate_json_file_create_valid(self, batch_manager):
        """Test JSON validation for create operations with valid data."""
        data = [
            {
                "project_id": "TEST",
                "summary": "Issue 1",
                "description": "Description 1",
                "type": "Bug",
                "priority": "High",
                "assignee": "user1",
            },
            {"project_id": "TEST", "summary": "Issue 2", "type": "Feature"},
        ]

        json_file = self.create_temp_json(data)

        try:
            result = batch_manager.validate_json_file(json_file, "create")
            assert len(result) == 2
            assert all(isinstance(item, BatchIssueCreate) for item in result)
            assert result[0].project_id == "TEST"
            assert result[1].summary == "Issue 2"
        finally:
            json_file.unlink()

    def test_validate_json_file_invalid_format(self, batch_manager):
        """Test JSON validation with invalid format (not an array)."""
        data = {"project_id": "TEST", "summary": "Not an array"}

        json_file = self.create_temp_json(data)

        try:
            with pytest.raises(BatchValidationError) as exc_info:
                batch_manager.validate_json_file(json_file, "create")

            assert "must contain an array" in str(exc_info.value)
        finally:
            json_file.unlink()

    def test_validate_file_unsupported_format(self, batch_manager):
        """Test validation with unsupported file format."""
        temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        temp_file.close()

        try:
            with pytest.raises(BatchValidationError) as exc_info:
                batch_manager.validate_file(Path(temp_file.name), "create")

            assert "Unsupported file format" in str(exc_info.value)
        finally:
            Path(temp_file.name).unlink()

    @pytest.mark.asyncio
    async def test_batch_create_issues_dry_run(self, batch_manager):
        """Test batch create in dry-run mode."""
        items = [
            BatchIssueCreate(project_id="TEST", summary="Issue 1"),
            BatchIssueCreate(project_id="TEST", summary="Issue 2"),
        ]

        result = await batch_manager.batch_create_issues(items, dry_run=True)

        assert result.operation == "create"
        assert result.total_items == 2
        assert result.successful == 2
        assert result.failed == 0
        assert result.dry_run is True
        assert len(result.created_items) == 0  # No actual creation in dry run

    @pytest.mark.asyncio
    async def test_batch_create_issues_success(self, batch_manager):
        """Test successful batch create operations."""
        items = [
            BatchIssueCreate(project_id="TEST", summary="Issue 1"),
            BatchIssueCreate(project_id="TEST", summary="Issue 2"),
        ]

        # Mock successful API responses
        mock_responses = [
            {"status": "success", "data": {"id": "TEST-1"}},
            {"status": "success", "data": {"id": "TEST-2"}},
        ]

        batch_manager.issue_manager.create_issue = AsyncMock(side_effect=mock_responses)

        result = await batch_manager.batch_create_issues(items)

        assert result.operation == "create"
        assert result.total_items == 2
        assert result.successful == 2
        assert result.failed == 0
        assert result.created_items == ["TEST-1", "TEST-2"]
        assert result.dry_run is False

    @pytest.mark.asyncio
    async def test_batch_create_issues_with_failures(self, batch_manager):
        """Test batch create with some failures."""
        items = [
            BatchIssueCreate(project_id="TEST", summary="Issue 1"),
            BatchIssueCreate(project_id="TEST", summary="Issue 2"),
        ]

        # Mock mixed success/failure responses
        mock_responses = [
            {"status": "success", "data": {"id": "TEST-1"}},
            {"status": "error", "message": "Failed to create issue"},
        ]

        batch_manager.issue_manager.create_issue = AsyncMock(side_effect=mock_responses)

        result = await batch_manager.batch_create_issues(items, continue_on_error=True)

        assert result.operation == "create"
        assert result.total_items == 2
        assert result.successful == 1
        assert result.failed == 1
        assert result.created_items == ["TEST-1"]
        assert len(result.errors) == 1

    @pytest.mark.asyncio
    async def test_batch_update_issues_success(self, batch_manager):
        """Test successful batch update operations."""
        items = [
            BatchIssueUpdate(issue_id="TEST-1", summary="Updated Issue 1"),
            BatchIssueUpdate(issue_id="TEST-2", state="Done"),
        ]

        # Mock successful API responses
        mock_response = {"status": "success", "message": "Issue updated"}
        batch_manager.issue_manager.update_issue = AsyncMock(return_value=mock_response)

        result = await batch_manager.batch_update_issues(items)

        assert result.operation == "update"
        assert result.total_items == 2
        assert result.successful == 2
        assert result.failed == 0
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_rollback_created_issues(self, batch_manager):
        """Test rollback functionality."""
        issue_ids = ["TEST-1", "TEST-2", "TEST-3"]

        # Mock successful deletion responses
        mock_response = {"status": "success", "message": "Issue deleted"}
        batch_manager.issue_manager.delete_issue = AsyncMock(return_value=mock_response)

        deleted_count = await batch_manager.rollback_created_issues(issue_ids)

        assert deleted_count == 3
        assert batch_manager.issue_manager.delete_issue.call_count == 3

    def test_display_validation_errors(self, batch_manager):
        """Test validation error display."""
        errors = [
            {"row": 2, "field": "project_id", "value": "", "error": "field required", "type": "value_error.missing"},
            {"index": 0, "field": "issue_id", "value": None, "error": "field required", "type": "value_error.missing"},
        ]

        # This should not raise an exception
        batch_manager.display_validation_errors(errors)

    def test_display_operation_summary(self, batch_manager):
        """Test operation summary display."""
        result = BatchOperationResult(
            operation="create",
            total_items=5,
            successful=3,
            failed=2,
            duration_seconds=10.5,
            created_items=["TEST-1", "TEST-2", "TEST-3"],
        )

        # This should not raise an exception
        batch_manager.display_operation_summary(result)

    def test_save_failed_operations_json(self, batch_manager):
        """Test saving failed operations to JSON."""
        result = BatchOperationResult(
            operation="create",
            total_items=2,
            successful=1,
            failed=1,
            errors=[
                {"item_index": 1, "item_data": {"project_id": "TEST", "summary": "Failed Issue"}, "error": "API Error"}
            ],
        )

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            output_path = Path(temp_file.name)

        try:
            batch_manager.save_failed_operations(result, output_path)

            # Verify file was created and contains expected data
            assert output_path.exists()
            with open(output_path) as f:
                data = json.load(f)
                assert len(data) == 1
                assert data[0]["project_id"] == "TEST"
        finally:
            output_path.unlink()

    def test_save_failed_operations_csv(self, batch_manager):
        """Test saving failed operations to CSV."""
        result = BatchOperationResult(
            operation="update",
            total_items=2,
            successful=1,
            failed=1,
            errors=[
                {"item_index": 1, "item_data": {"issue_id": "TEST-1", "summary": "Failed Update"}, "error": "API Error"}
            ],
        )

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
            output_path = Path(temp_file.name)

        try:
            batch_manager.save_failed_operations(result, output_path)

            # Verify file was created and contains expected data
            assert output_path.exists()
            with open(output_path) as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 1
                assert rows[0]["issue_id"] == "TEST-1"
        finally:
            output_path.unlink()


class TestTemplateGeneration:
    """Test template file generation."""

    def test_generate_csv_templates(self):
        """Test CSV template generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            generate_template_files(output_dir, "csv")

            create_template = output_dir / "batch_create_template.csv"
            update_template = output_dir / "batch_update_template.csv"

            assert create_template.exists()
            assert update_template.exists()

            # Verify create template content
            with open(create_template) as f:
                reader = csv.reader(f)
                headers = next(reader)
                assert "project_id" in headers
                assert "summary" in headers

                # Should have example rows
                row1 = next(reader)
                assert len(row1) == len(headers)

    def test_generate_json_templates(self):
        """Test JSON template generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            generate_template_files(output_dir, "json")

            create_template = output_dir / "batch_create_template.json"
            update_template = output_dir / "batch_update_template.json"

            assert create_template.exists()
            assert update_template.exists()

            # Verify create template content
            with open(create_template) as f:
                data = json.load(f)
                assert isinstance(data, list)
                assert len(data) > 0
                assert "project_id" in data[0]
                assert "summary" in data[0]

    def test_generate_templates_invalid_format(self):
        """Test template generation with invalid format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            with pytest.raises(ValueError) as exc_info:
                generate_template_files(output_dir, "xml")

            assert "Unsupported format: xml" in str(exc_info.value)


class TestBatchValidationError:
    """Test BatchValidationError exception."""

    def test_batch_validation_error_creation(self):
        """Test BatchValidationError exception creation."""
        errors = [{"field": "test", "error": "test error"}]
        exception = BatchValidationError("Test message", errors)

        assert str(exception) == "Test message"
        assert exception.message == "Test message"
        assert exception.errors == errors

    def test_batch_validation_error_empty_errors(self):
        """Test BatchValidationError with empty errors list."""
        exception = BatchValidationError("Test message", [])

        assert exception.errors == []
