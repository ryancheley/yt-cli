"""Tests for Pydantic models and validation."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from youtrack_cli.models import (
    ApiResponse,
    CachedResponse,
    CredentialVerificationResult,
    YouTrackComment,
    YouTrackCustomField,
    YouTrackErrorResponse,
    YouTrackIssue,
    YouTrackIssueTag,
    YouTrackProject,
    YouTrackSearchResult,
    YouTrackUser,
)


class TestCachedResponse:
    """Test CachedResponse model."""

    def test_cached_response_creation(self):
        """Test creating a cached response."""
        data = {"key": "value", "number": 42}
        response = CachedResponse(data=data, status_code=200)

        assert response.data == data
        assert response.status_code == 200

    def test_cached_response_default_status_code(self):
        """Test cached response with default status code."""
        data = {"test": "data"}
        response = CachedResponse(data=data)

        assert response.status_code == 200

    def test_cached_response_json_method(self):
        """Test json() method returns data."""
        data = {"key": "value"}
        response = CachedResponse(data=data)

        assert response.json() == data

    def test_cached_response_text_property(self):
        """Test text property returns string representation."""
        data = {"key": "value"}
        response = CachedResponse(data=data)

        assert response.text == str(data)

    def test_cached_response_extra_fields_allowed(self):
        """Test that extra fields are allowed."""
        response = CachedResponse(data={"test": "data"}, status_code=201, extra_field="extra_value")

        assert response.extra_field == "extra_value"


class TestApiResponse:
    """Test ApiResponse model."""

    def test_api_response_default_values(self):
        """Test API response with default values."""
        response = ApiResponse()

        assert response.status == "success"
        assert response.message is None
        assert response.data is None

    def test_api_response_with_data(self):
        """Test API response with data."""
        data = {"result": "test"}
        response = ApiResponse(status="success", message="Operation completed", data=data)

        assert response.status == "success"
        assert response.message == "Operation completed"
        assert response.data == data

    def test_api_response_error_status(self):
        """Test API response with error status."""
        response = ApiResponse(status="error", message="Something went wrong")

        assert response.status == "error"
        assert response.message == "Something went wrong"


class TestYouTrackUser:
    """Test YouTrackUser model."""

    def test_user_minimal_creation(self):
        """Test creating user with minimal required fields."""
        user = YouTrackUser(login="testuser")

        assert user.login == "testuser"
        assert user.full_name is None
        assert user.email is None
        assert user.guest is False
        assert user.online is False
        assert user.banned is False

    def test_user_full_creation(self):
        """Test creating user with all fields."""
        user = YouTrackUser(
            login="testuser",
            fullName="Test User",
            email="test@example.com",
            jabberAccountName="test@jabber.com",
            ringId="ring123",
            guest=False,
            online=True,
            banned=False,
            tags=["tag1", "tag2"],
            savedQueries=["query1", "query2"],
            avatarUrl="https://example.com/avatar.jpg",
            profiles={"github": "testuser"},
        )

        assert user.login == "testuser"
        assert user.full_name == "Test User"
        assert user.email == "test@example.com"
        assert user.jabber_account_name == "test@jabber.com"
        assert user.ring_id == "ring123"
        assert user.online is True
        assert user.tags == ["tag1", "tag2"]
        assert user.saved_queries == ["query1", "query2"]
        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.profiles == {"github": "testuser"}

    def test_user_field_aliases(self):
        """Test that field aliases work correctly."""
        user_data = {
            "login": "testuser",
            "fullName": "Test User",
            "jabberAccountName": "test@jabber.com",
            "ringId": "ring123",
            "savedQueries": ["query1"],
            "avatarUrl": "https://example.com/avatar.jpg",
        }

        user = YouTrackUser(**user_data)

        assert user.full_name == "Test User"
        assert user.jabber_account_name == "test@jabber.com"
        assert user.ring_id == "ring123"
        assert user.saved_queries == ["query1"]
        assert user.avatar_url == "https://example.com/avatar.jpg"


class TestYouTrackProject:
    """Test YouTrackProject model."""

    def test_project_minimal_creation(self):
        """Test creating project with minimal required fields."""
        project = YouTrackProject(id="proj123", name="Test Project", shortName="TP")

        assert project.id == "proj123"
        assert project.name == "Test Project"
        assert project.short_name == "TP"
        assert project.description is None
        assert project.resolved_issues_count == 0
        assert project.issues_count == 0
        assert project.archived is False

    def test_project_full_creation(self):
        """Test creating project with all fields."""
        leader = YouTrackUser(login="leader")
        created_by = YouTrackUser(login="creator")
        created_time = datetime.now()
        updated_time = datetime.now()

        project = YouTrackProject(
            id="proj123",
            name="Test Project",
            shortName="TP",
            description="A test project",
            leader=leader,
            createdBy=created_by,
            created=created_time,
            updated=updated_time,
            resolvedIssuesCount=10,
            issuesCount=25,
            archived=False,
            template=True,
        )

        assert project.description == "A test project"
        assert project.leader == leader
        assert project.created_by == created_by
        assert project.created == created_time
        assert project.updated == updated_time
        assert project.resolved_issues_count == 10
        assert project.issues_count == 25
        assert project.template is True

    def test_project_validation_error(self):
        """Test project validation with missing required fields."""
        with pytest.raises(ValidationError):
            YouTrackProject()  # Missing required fields


class TestYouTrackCustomField:
    """Test YouTrackCustomField model."""

    def test_custom_field_minimal_creation(self):
        """Test creating custom field with minimal required fields."""
        field = YouTrackCustomField(id="field123", name="Test Field")

        assert field.id == "field123"
        assert field.name == "Test Field"
        assert field.field_type is None
        assert field.has_state_field is False
        assert field.is_public is True
        assert field.ordinal == 0

    def test_custom_field_with_value(self):
        """Test custom field with various value types."""
        # String value
        field1 = YouTrackCustomField(id="f1", name="Field1", value="string_value")
        assert field1.value == "string_value"

        # Integer value
        field2 = YouTrackCustomField(id="f2", name="Field2", value=42)
        assert field2.value == 42

        # Boolean value
        field3 = YouTrackCustomField(id="f3", name="Field3", value=True)
        assert field3.value is True

        # List value
        field4 = YouTrackCustomField(id="f4", name="Field4", value=["item1", "item2"])
        assert field4.value == ["item1", "item2"]


class TestYouTrackIssueTag:
    """Test YouTrackIssueTag model."""

    def test_issue_tag_creation(self):
        """Test creating issue tag."""
        tag = YouTrackIssueTag(
            id="tag123",
            name="bug",
            query="Type: Bug",
            color="#ff0000",
            untagged=False,
            visibleForAuthor=True,
            visibleForAssignee=True,
        )

        assert tag.id == "tag123"
        assert tag.name == "bug"
        assert tag.query == "Type: Bug"
        assert tag.color == "#ff0000"
        assert tag.untagged is False
        assert tag.visible_for_author is True
        assert tag.visible_for_assignee is True


class TestYouTrackComment:
    """Test YouTrackComment model."""

    def test_comment_creation(self):
        """Test creating comment."""
        author = YouTrackUser(login="commenter")
        created_time = datetime.now()

        comment = YouTrackComment(
            id="comment123",
            text="This is a comment",
            textPreview="This is a...",
            created=created_time,
            author=author,
            issueId="issue123",
        )

        assert comment.id == "comment123"
        assert comment.text == "This is a comment"
        assert comment.text_preview == "This is a..."
        assert comment.created == created_time
        assert comment.author == author
        assert comment.issue_id == "issue123"
        assert comment.deleted is False


class TestYouTrackIssue:
    """Test YouTrackIssue model."""

    def test_issue_minimal_creation(self):
        """Test creating issue with minimal required fields."""
        issue = YouTrackIssue(id="issue123", entityId="entity456", fieldHash=789, number=1, summary="Test Issue")

        assert issue.id == "issue123"
        assert issue.entity_id == "entity456"
        assert issue.field_hash == 789
        assert issue.number == 1
        assert issue.summary == "Test Issue"
        assert issue.description is None
        assert len(issue.custom_fields) == 0
        assert len(issue.tags) == 0
        assert len(issue.comments) == 0
        assert issue.votes == 0

    def test_issue_with_relationships(self):
        """Test issue with related objects."""
        project = YouTrackProject(id="proj1", name="Project", shortName="P")
        reporter = YouTrackUser(login="reporter")
        custom_field = YouTrackCustomField(id="cf1", name="Priority")
        tag = YouTrackIssueTag(id="tag1", name="bug")
        comment = YouTrackComment(id="c1", text="Comment")

        issue = YouTrackIssue(
            id="issue123",
            entityId="entity456",
            fieldHash=789,
            number=1,
            summary="Test Issue",
            project=project,
            reporter=reporter,
            customFields=[custom_field],
            tags=[tag],
            comments=[comment],
            description="Issue description",
            votes=5,
        )

        assert issue.project == project
        assert issue.reporter == reporter
        assert len(issue.custom_fields) == 1
        assert issue.custom_fields[0] == custom_field
        assert len(issue.tags) == 1
        assert issue.tags[0] == tag
        assert len(issue.comments) == 1
        assert issue.comments[0] == comment
        assert issue.description == "Issue description"
        assert issue.votes == 5


class TestYouTrackErrorResponse:
    """Test YouTrackErrorResponse model."""

    def test_error_response_minimal(self):
        """Test creating error response with minimal fields."""
        error = YouTrackErrorResponse(error="Invalid request")

        assert error.error == "Invalid request"
        assert error.error_description is None
        assert error.error_developer_message is None
        assert error.error_code is None

    def test_error_response_full(self):
        """Test creating error response with all fields."""
        error = YouTrackErrorResponse(
            error="Invalid request",
            error_description="The request parameters are invalid",
            error_developer_message="Parameter 'id' is required",
            error_code="INVALID_REQUEST",
            localized_error="Solicitud inválida",
        )

        assert error.error == "Invalid request"
        assert error.error_description == "The request parameters are invalid"
        assert error.error_developer_message == "Parameter 'id' is required"
        assert error.error_code == "INVALID_REQUEST"
        assert error.localized_error == "Solicitud inválida"


class TestCredentialVerificationResult:
    """Test CredentialVerificationResult model."""

    def test_verification_success(self):
        """Test successful credential verification."""
        result = CredentialVerificationResult(
            status="success", username="testuser", full_name="Test User", email="test@example.com"
        )

        assert result.status == "success"
        assert result.username == "testuser"
        assert result.full_name == "Test User"
        assert result.email == "test@example.com"
        assert result.message is None

    def test_verification_error(self):
        """Test failed credential verification."""
        result = CredentialVerificationResult(status="error", message="Authentication failed")

        assert result.status == "error"
        assert result.message == "Authentication failed"
        assert result.username is None


class TestYouTrackSearchResult:
    """Test YouTrackSearchResult model."""

    def test_search_result_creation(self):
        """Test creating search result."""
        user = YouTrackUser(login="user1")
        project = YouTrackProject(id="p1", name="Project", shortName="P")

        result = YouTrackSearchResult(
            totalHits=100,
            skip=0,
            top=20,
            hasAfter=True,
            hasBefore=False,
            afterCursor="cursor123",
            results=[user, project],
        )

        assert result.total_hits == 100
        assert result.skip == 0
        assert result.top == 20
        assert result.has_after is True
        assert result.has_before is False
        assert result.after_cursor == "cursor123"
        assert len(result.results) == 2
        assert result.results[0] == user
        assert result.results[1] == project


class TestModelValidation:
    """Test model validation edge cases."""

    def test_datetime_field_validation(self):
        """Test datetime field validation."""
        now = datetime.now()

        issue = YouTrackIssue(
            id="issue123",
            entityId="entity456",
            fieldHash=789,
            number=1,
            summary="Test Issue",
            created=now,
            updated=now,
            resolved=now,
        )

        assert issue.created == now
        assert issue.updated == now
        assert issue.resolved == now

    def test_optional_nested_models(self):
        """Test optional nested model relationships."""
        issue = YouTrackIssue(
            id="issue123",
            entityId="entity456",
            fieldHash=789,
            number=1,
            summary="Test Issue",
            project=None,
            reporter=None,
            updater=None,
        )

        assert issue.project is None
        assert issue.reporter is None
        assert issue.updater is None

    def test_list_field_defaults(self):
        """Test default empty lists for list fields."""
        issue = YouTrackIssue(id="issue123", entityId="entity456", fieldHash=789, number=1, summary="Test Issue")

        assert issue.custom_fields == []
        assert issue.tags == []
        assert issue.comments == []
        assert issue.attachments == []
        assert issue.links == []

    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed in models."""
        user = YouTrackUser(login="testuser", extra_field="extra_value", another_field={"nested": "data"})

        assert user.login == "testuser"
        assert user.extra_field == "extra_value"
        assert user.another_field == {"nested": "data"}
