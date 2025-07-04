API Reference
=============

This section documents the Python API for YouTrack CLI. While the primary interface
is the command-line tool, the underlying Python modules can be used programmatically.

.. toctree::
   :maxdepth: 2

   client
   models
   exceptions
   utils

Core Modules
------------

.. autosummary::
   :toctree: _autosummary

   youtrack_cli.client
   youtrack_cli.models
   youtrack_cli.exceptions
   youtrack_cli.utils

Client API
----------

The :class:`~youtrack_cli.client.YouTrackClient` is the main interface for interacting
with YouTrack programmatically:

.. code-block:: python

   from youtrack_cli.client import YouTrackClient

   client = YouTrackClient(
       url="https://your-company.myjetbrains.com/youtrack",
       token="your-api-token"
   )

   # List issues
   issues = client.issues.list(assignee="me", state="open")

   # Create an issue
   issue = client.issues.create(
       title="Bug report",
       description="Something is broken",
       project="PROJECT-ID"
   )

   # Update an issue
   client.issues.update(issue.id, state="In Progress")

Models
------

YouTrack CLI uses Pydantic models for data validation and serialization.
Key models include:

* :class:`~youtrack_cli.models.Issue` - Issue data structure
* :class:`~youtrack_cli.models.Project` - Project information
* :class:`~youtrack_cli.models.User` - User details
* :class:`~youtrack_cli.models.Comment` - Issue comments
* :class:`~youtrack_cli.models.Attachment` - File attachments

Configuration
-------------

Programmatic configuration using the settings system:

.. code-block:: python

   from youtrack_cli.config import Settings

   settings = Settings(
       youtrack_url="https://your-company.myjetbrains.com/youtrack",
       youtrack_token="your-api-token",
       default_project="PROJECT-ID"
   )

   client = YouTrackClient.from_settings(settings)

Error Handling
--------------

YouTrack CLI defines several exception types for different error conditions:

.. code-block:: python

   from youtrack_cli.exceptions import (
       YouTrackError,
       AuthenticationError,
       NotFoundError,
       ValidationError
   )

   try:
       issue = client.issues.get("INVALID-ID")
   except NotFoundError:
       print("Issue not found")
   except AuthenticationError:
       print("Authentication failed")
   except YouTrackError as e:
       print(f"YouTrack error: {e}")

Utilities
---------

Helper functions and utilities:

.. code-block:: python

   from youtrack_cli.utils import (
       format_duration,
       parse_issue_id,
       validate_project_key
   )

   # Format time duration
   formatted = format_duration(7200)  # "2h"

   # Parse issue ID
   project, number = parse_issue_id("PROJECT-123")

   # Validate project key
   is_valid = validate_project_key("PROJ")

Integration Examples
-------------------

Custom Scripts
~~~~~~~~~~~~~~

Creating custom automation scripts:

.. code-block:: python

   #!/usr/bin/env python3
   """Auto-assign issues based on keywords."""

   from youtrack_cli.client import YouTrackClient
   from youtrack_cli.config import Settings

   def auto_assign_issues():
       settings = Settings()
       client = YouTrackClient.from_settings(settings)

       # Get unassigned issues
       issues = client.issues.list(assignee=None, state="Open")

       for issue in issues:
           if "frontend" in issue.summary.lower():
               client.issues.update(issue.id, assignee="frontend-team")
           elif "backend" in issue.summary.lower():
               client.issues.update(issue.id, assignee="backend-team")

   if __name__ == "__main__":
       auto_assign_issues()

Jupyter Notebooks
~~~~~~~~~~~~~~~~~

Using YouTrack CLI in data analysis:

.. code-block:: python

   import pandas as pd
   from youtrack_cli.client import YouTrackClient

   client = YouTrackClient(url="...", token="...")

   # Get issues data
   issues = client.issues.list(project="PROJECT-ID")

   # Convert to DataFrame
   df = pd.DataFrame([issue.dict() for issue in issues])

   # Analyze issue metrics
   state_counts = df.groupby('state').size()
   print(state_counts)

Web Applications
~~~~~~~~~~~~~~~~

Integrating with web frameworks:

.. code-block:: python

   from flask import Flask, jsonify
   from youtrack_cli.client import YouTrackClient

   app = Flask(__name__)
   client = YouTrackClient(url="...", token="...")

   @app.route('/api/issues')
   def get_issues():
       issues = client.issues.list(state="Open")
       return jsonify([issue.dict() for issue in issues])

   @app.route('/api/issues', methods=['POST'])
   def create_issue():
       data = request.json
       issue = client.issues.create(**data)
       return jsonify(issue.dict()), 201
