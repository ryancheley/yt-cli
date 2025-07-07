"""
Pydantic models for YouTrack API responses.

This module provides typed models for all YouTrack API responses,
replacing generic dictionary returns with proper type safety.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class CachedResponse(BaseModel):
    """Cached HTTP response model to replace inline MockResponse class."""

    model_config = ConfigDict(extra="allow")

    data: dict[str, Any]
    status_code: int = 200

    def json(self) -> dict[str, Any]:
        """Return JSON data, mimicking httpx.Response interface."""
        return self.data

    @property
    def text(self) -> str:
        """Return text representation of data."""
        return str(self.data)


class ApiResponse(BaseModel):
    """Generic API response wrapper."""

    model_config = ConfigDict(extra="allow")

    status: Literal["success", "error"] = "success"
    message: str | None = None
    data: dict[str, Any] | None = None


class YouTrackUser(BaseModel):
    """YouTrack user model."""

    model_config = ConfigDict(extra="allow")

    login: str
    full_name: str | None = Field(None, alias="fullName")
    email: str | None = None
    jabber_account_name: str | None = Field(None, alias="jabberAccountName")
    ring_id: str | None = Field(None, alias="ringId")
    guest: bool = False
    online: bool = False
    banned: bool = False
    tags: list[str] | None = None
    saved_queries: list[str] | None = Field(None, alias="savedQueries")
    avatar_url: str | None = Field(None, alias="avatarUrl")
    profiles: dict[str, Any] | None = None


class YouTrackProject(BaseModel):
    """YouTrack project model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    short_name: str = Field(alias="shortName")
    description: str | None = None
    leader: YouTrackUser | None = None
    created_by: YouTrackUser | None = Field(None, alias="createdBy")
    created: datetime | None = None
    updated: datetime | None = None
    resolved_issues_count: int = Field(0, alias="resolvedIssuesCount")
    issues_count: int = Field(0, alias="issuesCount")
    archived: bool = False
    template: bool = False


class YouTrackCustomField(BaseModel):
    """YouTrack custom field model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    field_type: str | None = Field(None, alias="fieldType")
    has_state_field: bool = Field(False, alias="hasStateField")
    is_public: bool = Field(True, alias="isPublic")
    ordinal: int = 0
    aliases: list[str] | None = None
    auto_attached: bool = Field(False, alias="autoAttached")
    value: str | int | float | bool | list[Any] | None = None


class YouTrackIssueTag(BaseModel):
    """YouTrack issue tag model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    query: str | None = None
    color: str | None = None
    untagged: bool = False
    visible_for_author: bool = Field(True, alias="visibleForAuthor")
    visible_for_assignee: bool = Field(True, alias="visibleForAssignee")


class YouTrackComment(BaseModel):
    """YouTrack comment model."""

    model_config = ConfigDict(extra="allow")

    id: str
    text: str
    text_preview: str | None = Field(None, alias="textPreview")
    created: datetime | None = None
    updated: datetime | None = None
    author: YouTrackUser | None = None
    issue_id: str | None = Field(None, alias="issueId")
    parent_id: str | None = Field(None, alias="parentId")
    deleted: bool = False
    visibility: dict[str, Any] | None = None


class YouTrackAttachment(BaseModel):
    """YouTrack attachment model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    author: YouTrackUser | None = None
    created: datetime | None = None
    updated: datetime | None = None
    size: int | None = None
    extension: str | None = None
    charset: str | None = None
    mime_type: str | None = Field(None, alias="mimeType")
    metadata_string: str | None = Field(None, alias="metadataString")
    url: str | None = None


class YouTrackIssue(BaseModel):
    """YouTrack issue model."""

    model_config = ConfigDict(extra="allow")

    id: str
    entity_id: str = Field(alias="entityId")
    field_hash: int = Field(alias="fieldHash")
    project: YouTrackProject | None = None
    number: int
    created: datetime | None = None
    updated: datetime | None = None
    updater: YouTrackUser | None = None
    resolved: datetime | None = None
    reporter: YouTrackUser | None = None
    summary: str
    description: str | None = None
    custom_fields: list[YouTrackCustomField] = Field(default_factory=list, alias="customFields")
    tags: list[YouTrackIssueTag] = Field(default_factory=list)
    comments: list[YouTrackComment] = Field(default_factory=list)
    attachments: list[YouTrackAttachment] = Field(default_factory=list)
    links: list[dict[str, Any]] = Field(default_factory=list)
    visibility: dict[str, Any] | None = None
    votes: int = 0
    votes_count: int = Field(0, alias="votesCount")
    wiki_text: str | None = Field(None, alias="wikiText")
    text_preview: str | None = Field(None, alias="textPreview")
    has_star: bool = Field(False, alias="hasStar")


class YouTrackBoard(BaseModel):
    """YouTrack board model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    favorite: bool = False
    orphans_at_the_top: bool = Field(True, alias="orphansAtTheTop")
    estimate_field: YouTrackCustomField | None = Field(None, alias="estimateField")
    columns: list[dict[str, Any]] = Field(default_factory=list)
    swimlanes: list[dict[str, Any]] = Field(default_factory=list)
    trimmed_swimlanes: list[dict[str, Any]] = Field(default_factory=list, alias="trimmedSwimlanes")


class YouTrackTimeTracking(BaseModel):
    """YouTrack time tracking model."""

    model_config = ConfigDict(extra="allow")

    id: str
    date: datetime | None = None
    duration: int | None = None  # in minutes
    description: str | None = None
    author: YouTrackUser | None = None
    issue: YouTrackIssue | None = None
    work_type: str | None = Field(None, alias="workType")
    created: datetime | None = None
    updated: datetime | None = None


class YouTrackWorkItem(BaseModel):
    """YouTrack work item model."""

    model_config = ConfigDict(extra="allow")

    id: str
    author: YouTrackUser | None = None
    creator: YouTrackUser | None = None
    text: str | None = None
    type: str | None = None
    date: datetime | None = None
    duration: int | None = None  # in minutes
    created: datetime | None = None
    updated: datetime | None = None


class YouTrackReport(BaseModel):
    """YouTrack report model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    query: str | None = None
    own: bool = False
    shared: bool = False
    pinned: bool = False
    data: dict[str, Any] | None = None
    created: datetime | None = None
    updated: datetime | None = None
    author: YouTrackUser | None = None


class YouTrackArticle(BaseModel):
    """YouTrack article model."""

    model_config = ConfigDict(extra="allow")

    id: str
    id_readable: str = Field(alias="idReadable")
    summary: str
    content: str | None = None
    created: datetime | None = None
    updated: datetime | None = None
    updater: YouTrackUser | None = None
    reporter: YouTrackUser | None = None
    project: YouTrackProject | None = None
    visibility: dict[str, Any] | None = None
    attachments: list[YouTrackAttachment] = Field(default_factory=list)
    tags: list[YouTrackIssueTag] = Field(default_factory=list)
    parent_article: str | None = Field(None, alias="parentArticle")
    child_articles: list[str] = Field(default_factory=list, alias="childArticles")
    ordinal: int = 0


class YouTrackSearchResult(BaseModel):
    """YouTrack search result model."""

    model_config = ConfigDict(extra="allow")

    total_hits: int = Field(alias="totalHits")
    skip: int = 0
    top: int = 0
    has_after: bool = Field(False, alias="hasAfter")
    has_before: bool = Field(False, alias="hasBefore")
    after_cursor: str | None = Field(None, alias="afterCursor")
    before_cursor: str | None = Field(None, alias="beforeCursor")
    results: list[YouTrackIssue | YouTrackArticle | YouTrackUser | YouTrackProject] = Field(default_factory=list)


class YouTrackErrorResponse(BaseModel):
    """YouTrack error response model."""

    model_config = ConfigDict(extra="allow")

    error: str
    error_description: str | None = Field(None, alias="error_description")
    error_developer_message: str | None = Field(None, alias="error_developer_message")
    error_code: str | None = Field(None, alias="error_code")
    localized_error: str | None = Field(None, alias="localized_error")


class CredentialVerificationResult(BaseModel):
    """Result of credential verification."""

    model_config = ConfigDict(extra="allow")

    status: Literal["success", "error"]
    username: str | None = None
    full_name: str | None = None
    email: str | None = None
    message: str | None = None
