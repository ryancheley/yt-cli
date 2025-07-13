"""Pydantic models for YouTrack API responses.

This module provides typed models for all YouTrack API responses,
replacing generic dictionary returns with proper type safety.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class CachedResponse(BaseModel):
    """Cached HTTP response model to replace inline MockResponse class.

    This model provides a cached representation of HTTP responses that mimics
    the httpx.Response interface for testing and caching purposes.

    Attributes:
        data: The response data as a dictionary.
        status_code: HTTP status code. Defaults to 200.
    """

    model_config = ConfigDict(extra="allow")

    data: dict[str, Any]
    status_code: int = 200

    def json(self) -> dict[str, Any]:
        """Return JSON data, mimicking httpx.Response interface.

        Returns:
            The response data as a dictionary.
        """
        return self.data

    @property
    def text(self) -> str:
        """Return text representation of data.

        Returns:
            String representation of the response data.
        """
        return str(self.data)


class ApiResponse(BaseModel):
    """Generic API response wrapper.

    Provides a standardized format for API responses with status,
    optional message, and data payload.

    Attributes:
        status: Response status, either 'success' or 'error'.
        message: Optional descriptive message.
        data: Optional response data payload.
    """

    model_config = ConfigDict(extra="allow")

    status: Literal["success", "error"] = "success"
    message: Optional[str] = None
    data: Optional[dict[str, Any]] = None


class YouTrackUser(BaseModel):
    """YouTrack user model.

    Represents a user account in YouTrack with all associated metadata
    including authentication status, contact information, and preferences.

    Attributes:
        login: User's login name (required).
        full_name: User's full display name.
        email: User's email address.
        jabber_account_name: Jabber/XMPP account name for notifications.
        ring_id: Ring ID for YouTrack integration.
        guest: Whether user is a guest account.
        online: Current online status.
        banned: Whether user account is banned.
        tags: User-associated tags.
        saved_queries: List of saved search queries.
        avatar_url: URL to user's avatar image.
        profiles: Additional user profile data.
    """

    model_config = ConfigDict(extra="allow")

    login: str
    full_name: Optional[str] = Field(None, alias="fullName")
    email: Optional[str] = None
    jabber_account_name: Optional[str] = Field(None, alias="jabberAccountName")
    ring_id: Optional[str] = Field(None, alias="ringId")
    guest: bool = False
    online: bool = False
    banned: bool = False
    tags: Optional[list[str]] = None
    saved_queries: Optional[list[str]] = Field(None, alias="savedQueries")
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    profiles: Optional[dict[str, Any]] = None


class YouTrackProject(BaseModel):
    """YouTrack project model.

    Represents a YouTrack project with metadata, statistics, and configuration.
    Projects are the primary organizational unit for issues in YouTrack.

    Attributes:
        id: Unique project identifier.
        name: Full project name.
        short_name: Short project identifier used in issue IDs.
        description: Optional project description.
        leader: Project lead user.
        created_by: User who created the project.
        created: Project creation timestamp.
        updated: Last modification timestamp.
        resolved_issues_count: Number of resolved issues.
        issues_count: Total number of issues.
        archived: Whether project is archived.
        template: Whether project is a template.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    short_name: str = Field(alias="shortName")
    description: Optional[str] = None
    leader: Optional[YouTrackUser] = None
    created_by: Optional[YouTrackUser] = Field(None, alias="createdBy")
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    resolved_issues_count: int = Field(0, alias="resolvedIssuesCount")
    issues_count: int = Field(0, alias="issuesCount")
    archived: bool = False
    template: bool = False


class YouTrackCustomField(BaseModel):
    """YouTrack custom field model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    field_type: Optional[str] = Field(None, alias="fieldType")
    has_state_field: bool = Field(False, alias="hasStateField")
    is_public: bool = Field(True, alias="isPublic")
    ordinal: int = 0
    aliases: Optional[list[str]] = None
    auto_attached: bool = Field(False, alias="autoAttached")
    value: Optional[Union[str, int, float, bool, list[Any]]] = None


class YouTrackIssueTag(BaseModel):
    """YouTrack issue tag model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    query: Optional[str] = None
    color: Optional[str] = None
    untagged: bool = False
    visible_for_author: bool = Field(True, alias="visibleForAuthor")
    visible_for_assignee: bool = Field(True, alias="visibleForAssignee")


class YouTrackComment(BaseModel):
    """YouTrack comment model."""

    model_config = ConfigDict(extra="allow")

    id: str
    text: str
    text_preview: Optional[str] = Field(None, alias="textPreview")
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    author: Optional[YouTrackUser] = None
    issue_id: Optional[str] = Field(None, alias="issueId")
    parent_id: Optional[str] = Field(None, alias="parentId")
    deleted: bool = False
    visibility: Optional[dict[str, Any]] = None


class YouTrackAttachment(BaseModel):
    """YouTrack attachment model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    author: Optional[YouTrackUser] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    size: Optional[int] = None
    extension: Optional[str] = None
    charset: Optional[str] = None
    mime_type: Optional[str] = Field(None, alias="mimeType")
    metadata_string: Optional[str] = Field(None, alias="metadataString")
    url: Optional[str] = None


class YouTrackIssue(BaseModel):
    """YouTrack issue model.

    Represents a YouTrack issue with all associated metadata including
    custom fields, comments, attachments, and workflow state.

    Attributes:
        id: Unique issue identifier.
        entity_id: Entity ID for database operations.
        field_hash: Hash of field values for change tracking.
        project: Associated project.
        number: Issue number within project.
        created: Issue creation timestamp.
        updated: Last modification timestamp.
        updater: User who last updated the issue.
        resolved: Resolution timestamp if resolved.
        reporter: User who reported the issue.
        summary: Issue title/summary.
        description: Detailed issue description.
        custom_fields: List of custom field values.
        tags: Issue tags for categorization.
        comments: List of comments on the issue.
        attachments: List of file attachments.
        links: Related issues and links.
        visibility: Visibility restrictions.
        votes: Number of votes.
        votes_count: Vote count.
        wiki_text: Wiki-formatted text content.
        text_preview: Preview of issue text.
        has_star: Whether issue is starred by current user.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    entity_id: str = Field(alias="entityId")
    field_hash: int = Field(alias="fieldHash")
    project: Optional[YouTrackProject] = None
    number: int
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    updater: Optional[YouTrackUser] = None
    resolved: Optional[datetime] = None
    reporter: Optional[YouTrackUser] = None
    summary: str
    description: Optional[str] = None
    custom_fields: list[YouTrackCustomField] = Field(default_factory=list, alias="customFields")
    tags: list[YouTrackIssueTag] = Field(default_factory=list)
    comments: list[YouTrackComment] = Field(default_factory=list)
    attachments: list[YouTrackAttachment] = Field(default_factory=list)
    links: list[dict[str, Any]] = Field(default_factory=list)
    visibility: Optional[dict[str, Any]] = None
    votes: int = 0
    votes_count: int = Field(0, alias="votesCount")
    wiki_text: Optional[str] = Field(None, alias="wikiText")
    text_preview: Optional[str] = Field(None, alias="textPreview")
    has_star: bool = Field(False, alias="hasStar")


class YouTrackBoard(BaseModel):
    """YouTrack board model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    favorite: bool = False
    orphans_at_the_top: bool = Field(True, alias="orphansAtTheTop")
    estimate_field: Optional[YouTrackCustomField] = Field(None, alias="estimateField")
    columns: list[dict[str, Any]] = Field(default_factory=list)
    swimlanes: list[dict[str, Any]] = Field(default_factory=list)
    trimmed_swimlanes: list[dict[str, Any]] = Field(default_factory=list, alias="trimmedSwimlanes")


class YouTrackTimeTracking(BaseModel):
    """YouTrack time tracking model."""

    model_config = ConfigDict(extra="allow")

    id: str
    date: Optional[datetime] = None
    duration: Optional[int] = None  # in minutes
    description: Optional[str] = None
    author: Optional[YouTrackUser] = None
    issue: Optional[YouTrackIssue] = None
    work_type: Optional[str] = Field(None, alias="workType")
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class YouTrackWorkItem(BaseModel):
    """YouTrack work item model."""

    model_config = ConfigDict(extra="allow")

    id: str
    author: Optional[YouTrackUser] = None
    creator: Optional[YouTrackUser] = None
    text: Optional[str] = None
    type: Optional[str] = None
    date: Optional[datetime] = None
    duration: Optional[int] = None  # in minutes
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


class YouTrackReport(BaseModel):
    """YouTrack report model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    query: Optional[str] = None
    own: bool = False
    shared: bool = False
    pinned: bool = False
    data: Optional[dict[str, Any]] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    author: Optional[YouTrackUser] = None


class YouTrackArticle(BaseModel):
    """YouTrack article model."""

    model_config = ConfigDict(extra="allow")

    id: str
    id_readable: str = Field(alias="idReadable")
    summary: str
    content: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    updater: Optional[YouTrackUser] = None
    reporter: Optional[YouTrackUser] = None
    project: Optional[YouTrackProject] = None
    visibility: Optional[dict[str, Any]] = None
    attachments: list[YouTrackAttachment] = Field(default_factory=list)
    tags: list[YouTrackIssueTag] = Field(default_factory=list)
    parent_article: Optional[str] = Field(None, alias="parentArticle")
    child_articles: list[str] = Field(default_factory=list, alias="childArticles")
    ordinal: int = 0


class YouTrackSearchResult(BaseModel):
    """YouTrack search result model.

    Represents paginated search results from YouTrack API with cursor-based
    pagination support and result metadata.

    Attributes:
        total_hits: Total number of matching results.
        skip: Number of results to skip (offset).
        top: Maximum number of results per page.
        has_after: Whether more results available after current page.
        has_before: Whether results available before current page.
        after_cursor: Cursor for next page navigation.
        before_cursor: Cursor for previous page navigation.
        results: List of search result objects (issues, articles, users, or projects).
    """

    model_config = ConfigDict(extra="allow")

    total_hits: int = Field(alias="totalHits")
    skip: int = 0
    top: int = 0
    has_after: bool = Field(False, alias="hasAfter")
    has_before: bool = Field(False, alias="hasBefore")
    after_cursor: Optional[str] = Field(None, alias="afterCursor")
    before_cursor: Optional[str] = Field(None, alias="beforeCursor")
    results: list[Union[YouTrackIssue, YouTrackArticle, YouTrackUser, YouTrackProject]] = Field(default_factory=list)


class YouTrackErrorResponse(BaseModel):
    """YouTrack error response model."""

    model_config = ConfigDict(extra="allow")

    error: str
    error_description: Optional[str] = Field(None, alias="error_description")
    error_developer_message: Optional[str] = Field(None, alias="error_developer_message")
    error_code: Optional[str] = Field(None, alias="error_code")
    localized_error: Optional[str] = Field(None, alias="localized_error")


class CredentialVerificationResult(BaseModel):
    """Result of credential verification.

    Contains the outcome of authenticating user credentials with YouTrack
    including user information and status details.

    Attributes:
        status: Verification status, either 'success' or 'error'.
        username: Verified username if successful.
        full_name: User's full name if available.
        email: User's email address if available.
        message: Descriptive message about verification result.
    """

    model_config = ConfigDict(extra="allow")

    status: Literal["success", "error"]
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    message: Optional[str] = None


class YouTrackLocale(BaseModel):
    """YouTrack locale information model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    locale: str
    language: str
    community: bool = False


class YouTrackLocaleSettings(BaseModel):
    """YouTrack locale settings model."""

    model_config = ConfigDict(extra="allow")

    locale: YouTrackLocale
    is_rtl: bool = Field(False, alias="isRTL")
