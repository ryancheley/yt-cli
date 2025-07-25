"""Manager layer for YouTrack CLI.

This module provides manager classes that handle business logic,
orchestration, and presentation concerns. Managers use service
classes for pure API communication and add:

- Business logic and workflows
- Service orchestration (combining multiple API calls)
- Data validation and business rule enforcement
- Presentation logic and formatting for CLI output

Managers are consumed by command classes which handle CLI interface
concerns.
"""

from .issues import IssueManager
from .projects import ProjectManager
from .users import UserManager

__all__ = [
    "IssueManager",
    "ProjectManager",
    "UserManager",
]
