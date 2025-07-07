"""
Pydantic models for YouTrack API responses.

This module provides typed models for all YouTrack API responses,
replacing generic dictionary returns with proper type safety.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional, Union

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
    message: Optional[str] = None
    data: Optional[dict[str, Any]] = None


class YouTrackUser(BaseModel):
    """YouTrack user model."""

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
    """YouTrack project model."""

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
    """YouTrack issue model."""

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
    """YouTrack search result model."""

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
    """Result of credential verification."""

    model_config = ConfigDict(extra="allow")

    status: Literal["success", "error"]
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    message: Optional[str] = None
