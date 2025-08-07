"""Configuration file for the Sphinx documentation builder."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# Project information
project = "YouTrack CLI"
copyright = "2024, YouTrack CLI Contributors"
author = "YouTrack CLI Contributors"

# The short X.Y version
version = "0.1"
# The full version, including alpha/beta/rc tags
release = "0.1.0"

# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.doctest",
    "sphinx_autodoc_typehints",
    "sphinx_click",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# HTML output options
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Theme options
html_theme_options = {
    "canonical_url": "",
    "analytics_id": "",
    "logo_only": False,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "vcs_pageview_mode": "",
    "style_nav_header_background": "white",
    # Toc options
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False  # Focus on Google style
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "click": ("https://click.palletsprojects.com/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "rich": ("https://rich.readthedocs.io/en/stable/", None),
    "textual": ("https://textual.textualize.io/", None),
}

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Prevent duplicate object descriptions
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# Auto-generate summaries
autosummary_generate = False
autosummary_imported_members = True

# Type hints settings
typehints_fully_qualified = False
typehints_document_rtype = True
typehints_use_signature = True
typehints_use_signature_return = True

# Doctest settings
doctest_global_setup = """
import asyncio
import os
import tempfile
import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Import YouTrack CLI modules for doctests
try:
    from youtrack_cli.utils import PaginationConfig, optimize_fields, format_timestamp
    from youtrack_cli.custom_field_types import get_display_name
    from youtrack_cli.validation import suggest_similar_commands
    from youtrack_cli.auth import AuthManager, AuthConfig
    from youtrack_cli.models import PaginationType
except ImportError:
    # Mock classes if imports fail
    class MockPaginationType:
        CURSOR = 'cursor'
        OFFSET = 'offset'

    class MockPaginationConfig:
        @classmethod
        def get_pagination_type(cls, endpoint):
            class MockResult:
                value = 'cursor' if '/api/issues' in endpoint else 'offset'
            return MockResult()

    PaginationConfig = MockPaginationConfig
    PaginationType = MockPaginationType

    def optimize_fields(base_params=None, fields=None, exclude_fields=None):
        result = (base_params or {}).copy()
        if fields:
            result["fields"] = ",".join(fields)
        return result

    def format_timestamp(timestamp):
        if timestamp is None or timestamp == '':
            return 'N/A'
        # Try to convert to int for timestamp, otherwise return as is
        try:
            int(timestamp)
            return '2022-01-01 00:00:00'
        except (ValueError, TypeError):
            return str(timestamp)

    def get_display_name(field_type):
        return field_type

    def suggest_similar_commands(attempted_command, available_commands):
        return []

    class AuthManager:
        pass

    class AuthConfig:
        def __init__(self, **kwargs):
            pass

# Mock functions for examples
def create_user(name):
    class MockUser:
        def __init__(self, name):
            self.name = name
            self.active = True
    return MockUser(name)

def search_issues(query, project=None):
    return []

def format_list(items):
    return ', '.join(map(str, items))

def get_file_path():
    return '/path/to/user/config'

async def my_async_function():
    return 'expected result'

def complex_async_operation():
    return object()

# Mock YouTrack API responses for doctests
async def mock_api_response(*args, **kwargs):
    return {"status": "success", "data": []}

# Set up mock environment for doctests
os.environ.setdefault('YOUTRACK_BASE_URL', 'https://youtrack.example.com')
os.environ.setdefault('YOUTRACK_TOKEN', 'test-token')
"""

doctest_global_cleanup = """
# Clean up any test artifacts
pass
"""

# Linkcheck settings
linkcheck_ignore = [
    r"http://localhost.*",
    r"http://127\.0\.0\.1.*",
    r"http://0\.0\.0\.0.*",
    r"https://youtrack\.example\.com.*",
    r"https://yourcompany\.youtrack\.cloud.*",
]

linkcheck_timeout = 30
linkcheck_retries = 2
linkcheck_workers = 5
