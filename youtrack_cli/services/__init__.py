"""Services layer for YouTrack CLI.

This module provides service classes that handle pure API communication
with the YouTrack REST API. Services are responsible for:

- HTTP request/response handling
- Data transformation from API responses
- Centralized error handling
- Response caching where appropriate

Services are consumed by manager classes which handle business logic,
orchestration, and presentation concerns.
"""

from .base import BaseService
from .issues import IssueService
from .projects import ProjectService
from .users import UserService

__all__ = [
    "BaseService",
    "IssueService",
    "ProjectService",
    "UserService",
]
