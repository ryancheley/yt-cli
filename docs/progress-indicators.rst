Progress Indicators
==================

The YouTrack CLI provides visual progress indicators for long-running operations to improve user experience and provide feedback during bulk operations.

Overview
--------

Progress indicators are automatically shown for operations that may take significant time, including:

- **Report Generation**: Burndown and velocity reports with large datasets
- **Issue Operations**: Bulk issue listing, searching, and file operations
- **Admin Operations**: System maintenance tasks, cache clearing, and health checks
- **File Operations**: Upload/download of attachments

Types of Progress Indicators
----------------------------

Progress Bars
~~~~~~~~~~~~~

For operations with known duration or item count::

   ⠋ Generating burndown report... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 3/3 0:00:02 0:00:00

Features:

- Spinner animation
- Descriptive text that updates during operation
- Progress bar showing completion percentage
- Item counters (completed/total)
- Time elapsed and estimated time remaining

Spinners
~~~~~~~~

For indeterminate operations::

   ⠋ Fetching issues...

Used when the total duration or item count is unknown.

Configuration
-------------

Disabling Progress Indicators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can disable progress indicators globally using the ``--no-progress`` flag:

.. code-block:: bash

   # Disable progress indicators for a single command
   yt --no-progress reports burndown PROJECT-1

   # Disable for all subcommands
   yt --no-progress issues list --project PROJECT-1

Environment Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~

Progress indicators automatically detect the environment:

- **Interactive terminals**: Full progress bars with animations
- **Non-interactive environments**: Simplified or disabled output
- **CI/CD pipelines**: Automatically disabled to prevent log clutter

Implementation Details
----------------------

Progress Manager
~~~~~~~~~~~~~~~~

The progress system is built around a centralized ``ProgressManager`` class that:

- Manages multiple concurrent progress indicators
- Handles environment detection
- Provides context managers for easy integration
- Supports both determinate and indeterminate progress

Integration Pattern
~~~~~~~~~~~~~~~~~~~

Operations integrate progress indicators using context managers:

.. code-block:: python

   from .progress import get_progress_manager

   progress_manager = get_progress_manager()

   # For determinate progress
   with progress_manager.progress_bar("Processing items...", total=len(items)) as tracker:
       for item in items:
           # Process item
           tracker.advance()

   # For indeterminate progress
   with progress_manager.spinner("Working..."):
       # Long-running operation
       perform_operation()

Affected Commands
-----------------

Reports
~~~~~~~

All report generation commands show progress indicators:

- ``yt reports burndown`` - Shows 3-step progress for query building, data fetching, and metric calculation
- ``yt reports velocity`` - Shows progress for each sprint being analyzed

Issues
~~~~~~

Issue commands with progress indicators:

- ``yt issues list`` - Spinner during API calls for large result sets
- ``yt issues search`` - Progress bar for complex searches
- ``yt issues attach upload`` - Progress bar for file uploads
- ``yt issues attach download`` - Progress bar for file downloads

Admin
~~~~~

Administrative operations with progress:

- ``yt admin maintenance clear-cache`` - Spinner for cache clearing operations
- ``yt admin health check`` - Progress bar for multi-step diagnostics
- ``yt admin usage users report`` - Progress bar for report generation

Best Practices
---------------

For Users
~~~~~~~~~

1. **Large Operations**: Progress indicators are most helpful for operations involving:

   - More than 100 items
   - File uploads/downloads
   - Complex reports or searches

2. **CI/CD Integration**: Use ``--no-progress`` in automated scripts to keep logs clean

3. **Performance**: Progress indicators add minimal overhead and can be left enabled in most cases

For Developers
~~~~~~~~~~~~~~

1. **Integration**: Add progress indicators to any operation that:

   - Takes more than 2-3 seconds typically
   - Processes multiple items sequentially
   - Involves network I/O with potential delays

2. **Granularity**: Choose appropriate progress granularity:

   - Too fine: Updates too frequently, performance impact
   - Too coarse: Poor user experience

3. **Error Handling**: Progress indicators automatically clean up on exceptions

Performance Impact
------------------

Progress indicators are designed to have minimal performance impact:

- **Overhead**: Less than 1% for typical operations
- **Memory**: Minimal additional memory usage
- **Network**: No additional network calls
- **Rendering**: Efficient terminal rendering with minimal CPU usage

The progress system automatically disables in non-interactive environments to eliminate any overhead in automated scenarios.
