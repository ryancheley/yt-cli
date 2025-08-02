"""Batch operations support for YouTrack CLI.

This module provides comprehensive batch operation capabilities including:
- Batch issue creation from CSV/JSON files
- Batch issue updates with file input
- Progress tracking with Rich progress bars
- Error handling and rollback capabilities
- Input file validation
- Dry-run mode for batch operations
- Comprehensive logging
"""

import asyncio
import csv
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

if TYPE_CHECKING:
    pass

from pydantic import BaseModel, Field, ValidationError
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from .auth import AuthManager
from .console import get_console
from .logging import get_logger
from .managers.issues import IssueManager

logger = get_logger(__name__)


class BatchIssueCreate(BaseModel):
    """Model for batch issue creation data."""

    project_id: str = Field(..., description="Project ID where issue will be created")
    summary: str = Field(..., description="Issue summary/title")
    description: Optional[str] = Field(None, description="Issue description")
    type: Optional[str] = Field(None, description="Issue type (Bug, Feature, Task, etc.)")
    priority: Optional[str] = Field(None, description="Issue priority (Critical, High, Medium, Low)")
    assignee: Optional[str] = Field(None, description="Assignee username")

    class Config:
        """Pydantic configuration."""

        extra = "forbid"  # Reject any extra fields


class BatchIssueUpdate(BaseModel):
    """Model for batch issue update data."""

    issue_id: str = Field(..., description="Issue ID to update")
    summary: Optional[str] = Field(None, description="New issue summary/title")
    description: Optional[str] = Field(None, description="New issue description")
    state: Optional[str] = Field(None, description="New issue state")
    type: Optional[str] = Field(None, description="New issue type")
    priority: Optional[str] = Field(None, description="New issue priority")
    assignee: Optional[str] = Field(None, description="New assignee username")

    class Config:
        """Pydantic configuration."""

        extra = "forbid"  # Reject any extra fields


class BatchOperationResult(BaseModel):
    """Result of a batch operation."""

    operation: str = Field(..., description="Type of operation performed")
    total_items: int = Field(..., description="Total number of items processed")
    successful: int = Field(default=0, description="Number of successful operations")
    failed: int = Field(default=0, description="Number of failed operations")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="List of errors encountered")
    created_items: List[str] = Field(default_factory=list, description="List of created item IDs")
    duration_seconds: float = Field(default=0.0, description="Operation duration in seconds")
    dry_run: bool = Field(default=False, description="Whether this was a dry run")


class BatchValidationError(Exception):
    """Exception raised when batch file validation fails."""

    def __init__(self, message: str, errors: List[Dict[str, Any]]):
        self.message = message
        self.errors = errors
        super().__init__(message)


class BatchOperationManager:
    """Manager for batch operations on YouTrack issues."""

    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.issue_manager = IssueManager(auth_manager)
        self.console = get_console()

    def validate_csv_file(
        self, file_path: Path, operation_type: str
    ) -> List[Union[BatchIssueCreate, BatchIssueUpdate]]:
        """Validate a CSV file for batch operations.

        Args:
            file_path: Path to the CSV file
            operation_type: Type of operation ('create' or 'update')

        Returns:
            List of validated batch operation objects

        Raises:
            BatchValidationError: If validation fails
        """
        errors = []
        validated_items = []

        try:
            with open(file_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 to account for header
                    try:
                        # Remove empty string values and convert to None
                        cleaned_row = {k: (v if v.strip() else None) for k, v in row.items() if v is not None}

                        if operation_type == "create":
                            validated_item = BatchIssueCreate(**cleaned_row)
                        elif operation_type == "update":
                            validated_item = BatchIssueUpdate(**cleaned_row)
                        else:
                            raise ValueError(f"Invalid operation type: {operation_type}")

                        validated_items.append(validated_item)

                    except ValidationError as e:
                        for error in e.errors():
                            errors.append(
                                {
                                    "row": row_num,
                                    "field": error["loc"][0] if error["loc"] else "unknown",
                                    "value": row.get(error["loc"][0] if error["loc"] else "unknown", ""),
                                    "error": error["msg"],
                                    "type": error["type"],
                                }
                            )
                    except Exception as e:
                        errors.append({"row": row_num, "error": str(e), "type": "general_error"})

        except FileNotFoundError as e:
            raise BatchValidationError(f"File not found: {file_path}", []) from e
        except Exception as e:
            raise BatchValidationError(f"Error reading CSV file: {e}", []) from e

        if errors:
            raise BatchValidationError(f"Validation failed with {len(errors)} errors", errors)

        return validated_items

    def validate_json_file(
        self, file_path: Path, operation_type: str
    ) -> List[Union[BatchIssueCreate, BatchIssueUpdate]]:
        """Validate a JSON file for batch operations.

        Args:
            file_path: Path to the JSON file
            operation_type: Type of operation ('create' or 'update')

        Returns:
            List of validated batch operation objects

        Raises:
            BatchValidationError: If validation fails
        """
        errors = []
        validated_items = []

        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise BatchValidationError("JSON file must contain an array of objects", [])

            for index, item in enumerate(data):
                try:
                    if operation_type == "create":
                        validated_item = BatchIssueCreate(**item)
                    elif operation_type == "update":
                        validated_item = BatchIssueUpdate(**item)
                    else:
                        raise ValueError(f"Invalid operation type: {operation_type}")

                    validated_items.append(validated_item)

                except ValidationError as e:
                    for error in e.errors():
                        errors.append(
                            {
                                "index": index,
                                "field": error["loc"][0] if error["loc"] else "unknown",
                                "value": item.get(error["loc"][0] if error["loc"] else "unknown", ""),
                                "error": error["msg"],
                                "type": error["type"],
                            }
                        )
                except Exception as e:
                    errors.append({"index": index, "error": str(e), "type": "general_error"})

        except FileNotFoundError as e:
            raise BatchValidationError(f"File not found: {file_path}", []) from e
        except json.JSONDecodeError as e:
            raise BatchValidationError(f"Invalid JSON format: {e}", []) from e
        except Exception as e:
            raise BatchValidationError(f"Error reading JSON file: {e}", []) from e

        if errors:
            raise BatchValidationError(f"Validation failed with {len(errors)} errors", errors)

        return validated_items

    async def validate_api_compatibility(self, items: List[BatchIssueUpdate]) -> List[Dict[str, Any]]:
        """Validate API compatibility for batch update items.

        This method tests whether the field values in the batch items
        are compatible with the YouTrack API, particularly for state fields
        which require special formatting.

        Args:
            items: List of validated batch update items

        Returns:
            List of validation error dictionaries (empty if all valid)
        """
        errors = []

        for i, item in enumerate(items):
            # Only validate items that have state field updates
            if item.state is not None:
                try:
                    # Use the same validation logic as IssueService.update_issue
                    # Check if the issue exists and get its project ID
                    issue_result = await self.issue_manager.issue_service.get_issue(item.issue_id, "project(id)")
                    if issue_result["status"] != "success":
                        errors.append(
                            {
                                "item_index": i,
                                "issue_id": item.issue_id,
                                "field": "issue_id",
                                "error": f"Issue {item.issue_id} not found or not accessible",
                                "type": "api_compatibility_error",
                            }
                        )
                        continue

                    # Get project ID from the issue
                    project_data = issue_result.get("data", {}).get("project", {})
                    project_id = project_data.get("id")

                    if not project_id:
                        errors.append(
                            {
                                "item_index": i,
                                "issue_id": item.issue_id,
                                "field": "state",
                                "error": "Could not determine project ID for state field validation",
                                "type": "api_compatibility_error",
                            }
                        )
                        continue

                    # Use IssueService's state field discovery logic
                    try:
                        state_field_info = await self.issue_manager.issue_service._discover_state_field_for_project(
                            project_id
                        )
                        if not state_field_info:
                            # Get available fields for better error message
                            from .services.projects import ProjectService

                            project_service = ProjectService(self.auth_manager)
                            fields_result = await project_service.get_project_custom_fields(
                                project_id, "id,name,fieldType,localizedName,isPublic,ordinal,field(fieldType,name)"
                            )

                            available_fields = []
                            if fields_result["status"] == "success":
                                available_fields = [
                                    f.get("field", {}).get("name", "")
                                    for f in fields_result["data"]
                                    if f.get("field", {}).get("name")
                                ]

                            errors.append(
                                {
                                    "item_index": i,
                                    "issue_id": item.issue_id,
                                    "field": "state",
                                    "value": item.state,
                                    "error": f"No state field found for project '{project_id}'. "
                                    + f"Available custom fields: {', '.join(available_fields) if available_fields else 'None'}. "
                                    + "Please check if the project has a state/status field configured.",
                                    "type": "api_compatibility_error",
                                }
                            )
                    except Exception as e:
                        # If state field discovery fails, we'll rely on the fallback logic
                        # This is acceptable as the actual update call will handle it
                        logger.debug(f"State field discovery failed for issue {item.issue_id}, using fallback: {e}")

                except Exception as e:
                    errors.append(
                        {
                            "item_index": i,
                            "issue_id": item.issue_id,
                            "field": "state",
                            "error": f"API compatibility check failed: {str(e)}",
                            "type": "api_compatibility_error",
                        }
                    )

        return errors

    def validate_file(
        self, file_path: Path, operation_type: str
    ) -> Union[List[BatchIssueCreate], List[BatchIssueUpdate]]:
        """Validate a batch operation file (CSV or JSON).

        Args:
            file_path: Path to the file
            operation_type: Type of operation ('create' or 'update')

        Returns:
            List of validated batch operation objects

        Raises:
            BatchValidationError: If validation fails
        """
        if file_path.suffix.lower() == ".csv":
            result = self.validate_csv_file(file_path, operation_type)
        elif file_path.suffix.lower() == ".json":
            result = self.validate_json_file(file_path, operation_type)
        else:
            raise BatchValidationError(f"Unsupported file format: {file_path.suffix}. Use .csv or .json", [])

        # Cast the result to the appropriate type based on operation_type
        if operation_type == "create":
            return cast(List[BatchIssueCreate], result)
        return cast(List[BatchIssueUpdate], result)

    async def validate_file_with_api_check(
        self, file_path: Path, operation_type: str
    ) -> Union[List[BatchIssueCreate], List[BatchIssueUpdate]]:
        """Validate a batch operation file with API compatibility checking.

        Args:
            file_path: Path to the file
            operation_type: Type of operation ('create' or 'update')

        Returns:
            List of validated batch operation objects

        Raises:
            BatchValidationError: If validation fails
        """
        # First do regular file validation
        result = self.validate_file(file_path, operation_type)

        # For updates, also check API compatibility
        if operation_type == "update":
            api_errors = await self.validate_api_compatibility(cast(List[BatchIssueUpdate], result))
            if api_errors:
                raise BatchValidationError(
                    f"API compatibility validation failed with {len(api_errors)} errors", api_errors
                )

        return result

    async def batch_create_issues(
        self, items: List[BatchIssueCreate], dry_run: bool = False, continue_on_error: bool = True
    ) -> BatchOperationResult:
        """Batch create issues from validated data.

        Args:
            items: List of validated issue creation data
            dry_run: If True, validate operations but don't execute them
            continue_on_error: If True, continue processing after errors

        Returns:
            BatchOperationResult with operation results
        """
        import time

        start_time = time.time()

        result = BatchOperationResult(operation="create", total_items=len(items), dry_run=dry_run)

        if not items:
            return result

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
        ) as progress:
            task = progress.add_task(f"{'[DRY RUN] ' if dry_run else ''}Creating issues...", total=len(items))

            for i, item in enumerate(items):
                try:
                    if dry_run:
                        # For dry run, just simulate the operation
                        await asyncio.sleep(0.01)  # Small delay to show progress
                        result.successful += 1
                        logger.info(f"[DRY RUN] Would create issue: {item.summary} in {item.project_id}")
                    else:
                        # Actually create the issue
                        create_result = await self.issue_manager.create_issue(
                            project_id=item.project_id,
                            summary=item.summary,
                            description=item.description,
                            issue_type=item.type,
                            priority=item.priority,
                            assignee=item.assignee,
                        )

                        if create_result["status"] == "success":
                            result.successful += 1
                            issue_id = create_result["data"].get("id", "unknown")
                            result.created_items.append(issue_id)
                            logger.info(f"Created issue {issue_id}: {item.summary}")
                        else:
                            result.failed += 1
                            error_info = {
                                "item_index": i,
                                "item_data": item.dict(),
                                "error": create_result["message"],
                                "api_response": create_result,
                            }
                            result.errors.append(error_info)
                            logger.error(f"Failed to create issue: {create_result['message']}")

                            if not continue_on_error:
                                break

                except Exception as e:
                    result.failed += 1
                    error_info = {
                        "item_index": i,
                        "item_data": item.dict(),
                        "error": str(e),
                        "exception_type": type(e).__name__,
                    }
                    result.errors.append(error_info)
                    logger.error(f"Exception creating issue: {e}")

                    if not continue_on_error:
                        break

                progress.update(task, advance=1)

        result.duration_seconds = time.time() - start_time
        return result

    async def batch_update_issues(
        self, items: List[BatchIssueUpdate], dry_run: bool = False, continue_on_error: bool = True
    ) -> BatchOperationResult:
        """Batch update issues from validated data.

        Args:
            items: List of validated issue update data
            dry_run: If True, validate operations but don't execute them
            continue_on_error: If True, continue processing after errors

        Returns:
            BatchOperationResult with operation results
        """
        import time

        start_time = time.time()

        result = BatchOperationResult(operation="update", total_items=len(items), dry_run=dry_run)

        if not items:
            return result

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            console=self.console,
            transient=False,
        ) as progress:
            task = progress.add_task(f"{'[DRY RUN] ' if dry_run else ''}Updating issues...", total=len(items))

            for i, item in enumerate(items):
                try:
                    if dry_run:
                        # For dry run, just simulate the operation
                        await asyncio.sleep(0.01)  # Small delay to show progress
                        result.successful += 1
                        updates = [f"{k}={v}" for k, v in item.dict().items() if v is not None and k != "issue_id"]
                        logger.info(f"[DRY RUN] Would update issue {item.issue_id}: {', '.join(updates)}")
                    else:
                        # Actually update the issue
                        update_result = await self.issue_manager.update_issue(
                            issue_id=item.issue_id,
                            summary=item.summary,
                            description=item.description,
                            state=item.state,
                            priority=item.priority,
                            assignee=item.assignee,
                            issue_type=item.type,
                        )

                        if update_result["status"] == "success":
                            result.successful += 1
                            logger.info(f"Updated issue {item.issue_id}")
                        else:
                            result.failed += 1
                            error_info = {
                                "item_index": i,
                                "item_data": item.dict(),
                                "error": update_result["message"],
                                "api_response": update_result,
                            }
                            result.errors.append(error_info)
                            logger.error(f"Failed to update issue {item.issue_id}: {update_result['message']}")

                            if not continue_on_error:
                                break

                except Exception as e:
                    result.failed += 1
                    error_info = {
                        "item_index": i,
                        "item_data": item.dict(),
                        "error": str(e),
                        "exception_type": type(e).__name__,
                    }
                    result.errors.append(error_info)
                    logger.error(f"Exception updating issue {item.issue_id}: {e}")

                    if not continue_on_error:
                        break

                progress.update(task, advance=1)

        result.duration_seconds = time.time() - start_time
        return result

    async def rollback_created_issues(self, issue_ids: List[str]) -> int:
        """Rollback (delete) created issues.

        Args:
            issue_ids: List of issue IDs to delete

        Returns:
            Number of successfully deleted issues
        """
        if not issue_ids:
            return 0

        deleted_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            console=self.console,
            transient=False,
        ) as progress:
            task = progress.add_task("Rolling back created issues...", total=len(issue_ids))

            for issue_id in issue_ids:
                try:
                    delete_result = await self.issue_manager.delete_issue(issue_id)
                    if delete_result["status"] == "success":
                        deleted_count += 1
                        logger.info(f"Rolled back (deleted) issue {issue_id}")
                    else:
                        logger.error(f"Failed to rollback issue {issue_id}: {delete_result['message']}")
                except Exception as e:
                    logger.error(f"Exception rolling back issue {issue_id}: {e}")

                progress.update(task, advance=1)

        return deleted_count

    def display_validation_errors(self, errors: List[Dict[str, Any]]) -> None:
        """Display validation errors in a formatted table.

        Args:
            errors: List of validation error dictionaries
        """
        if not errors:
            return

        table = Table(title="Validation Errors", show_header=True, header_style="bold red")

        # Determine if we have row-based (CSV) or index-based (JSON) errors
        has_rows = any("row" in error for error in errors)

        if has_rows:
            table.add_column("Row", style="cyan")
        else:
            table.add_column("Index", style="cyan")

        table.add_column("Field", style="yellow")
        table.add_column("Value", style="white")
        table.add_column("Error", style="red")

        for error in errors:
            row_or_index = str(error.get("row", error.get("index", "N/A")))
            field = error.get("field", "N/A")
            value = str(error.get("value", ""))[:50]  # Truncate long values
            error_msg = error.get("error", "Unknown error")

            table.add_row(row_or_index, field, value, error_msg)

        self.console.print(table)

    def display_operation_summary(self, result: BatchOperationResult) -> None:
        """Display a summary of the batch operation results.

        Args:
            result: The batch operation result to display
        """
        # Create summary table
        table = Table(title=f"Batch {result.operation.title()} Summary", show_header=False)
        table.add_column("Metric", style="bold")
        table.add_column("Value", style="white")

        # Add basic metrics
        table.add_row("Operation", result.operation.title())
        table.add_row("Mode", "Dry Run" if result.dry_run else "Live")
        table.add_row("Total Items", str(result.total_items))
        table.add_row("Successful", f"[green]{result.successful}[/green]")
        table.add_row("Failed", f"[red]{result.failed}[/red]" if result.failed > 0 else "0")
        table.add_row("Duration", f"{result.duration_seconds:.2f} seconds")

        if result.created_items:
            table.add_row("Created Issues", str(len(result.created_items)))

        self.console.print(table)

        # Display errors if any
        if result.errors:
            self.console.print(f"\n[red]Errors encountered ({len(result.errors)}):[/red]")
            for i, error in enumerate(result.errors[:10]):  # Show first 10 errors
                item_ref = error.get("item_index", "N/A")
                error_msg = error.get("error", "Unknown error")
                self.console.print(f"  {i + 1}. Item {item_ref}: {error_msg}")

            if len(result.errors) > 10:
                self.console.print(f"  ... and {len(result.errors) - 10} more errors")

    def save_failed_operations(self, result: BatchOperationResult, output_path: Path) -> None:
        """Save failed operations to a file for retry.

        Args:
            result: The batch operation result containing errors
            output_path: Path where to save the failed operations
        """
        if not result.errors:
            return

        failed_items = []
        for error in result.errors:
            if "item_data" in error:
                failed_items.append(error["item_data"])

        if not failed_items:
            return

        try:
            if output_path.suffix.lower() == ".json":
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(failed_items, f, indent=2)
            elif output_path.suffix.lower() == ".csv":
                if failed_items:
                    with open(output_path, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=failed_items[0].keys())
                        writer.writeheader()
                        writer.writerows(failed_items)

            self.console.print(f"[yellow]Failed operations saved to: {output_path}[/yellow]")

        except Exception as e:
            logger.error(f"Failed to save failed operations: {e}")
            self.console.print(f"[red]Failed to save failed operations: {e}[/red]")


def generate_template_files(output_dir: Path, file_format: str = "csv") -> None:
    """Generate template files for batch operations.

    Args:
        output_dir: Directory where to save template files
        file_format: Format for templates ('csv' or 'json')
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    console = get_console()

    if file_format.lower() == "csv":
        # Generate CSV templates
        create_template = output_dir / "batch_create_template.csv"
        update_template = output_dir / "batch_update_template.csv"

        # Create template
        with open(create_template, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["project_id", "summary", "description", "type", "priority", "assignee"])
            writer.writerow(["FPU", "Fix login bug", "Login fails on mobile devices", "Bug", "High", "john.doe"])
            writer.writerow(
                ["FPU", "Add user dashboard", "Create a user dashboard with metrics", "Feature", "Medium", "jane.smith"]
            )

        # Update template
        with open(update_template, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["issue_id", "summary", "description", "state", "type", "priority", "assignee"])
            writer.writerow(["FPU-1", "Updated summary", "", "In Progress", "", "High", ""])
            writer.writerow(["FPU-2", "", "Updated description text", "Done", "", "", "john.doe"])

        console.print(f"[green]Created CSV templates in {output_dir}:[/green]")
        console.print(f"  - {create_template.name}")
        console.print(f"  - {update_template.name}")

    elif file_format.lower() == "json":
        # Generate JSON templates
        create_template = output_dir / "batch_create_template.json"
        update_template = output_dir / "batch_update_template.json"

        # Create template
        create_data = [
            {
                "project_id": "FPU",
                "summary": "Fix login bug",
                "description": "Login fails on mobile devices",
                "type": "Bug",
                "priority": "High",
                "assignee": "john.doe",
            },
            {
                "project_id": "FPU",
                "summary": "Add user dashboard",
                "description": "Create a user dashboard with metrics",
                "type": "Feature",
                "priority": "Medium",
                "assignee": "jane.smith",
            },
        ]

        # Update template
        update_data = [
            {"issue_id": "FPU-1", "summary": "Updated summary", "state": "In Progress", "priority": "High"},
            {"issue_id": "FPU-2", "description": "Updated description text", "state": "Done", "assignee": "john.doe"},
        ]

        with open(create_template, "w", encoding="utf-8") as f:
            json.dump(create_data, f, indent=2)

        with open(update_template, "w", encoding="utf-8") as f:
            json.dump(update_data, f, indent=2)

        console.print(f"[green]Created JSON templates in {output_dir}:[/green]")
        console.print(f"  - {create_template.name}")
        console.print(f"  - {update_template.name}")

    else:
        raise ValueError(f"Unsupported format: {file_format}. Use 'csv' or 'json'")
