Configuration
=============

YouTrack CLI can be configured through multiple methods, allowing you to customize
its behavior to match your workflow.

Configuration Sources
--------------------

YouTrack CLI reads configuration from multiple sources in this order (later sources override earlier ones):

1. Default values
2. Configuration file (``~/.config/youtrack-cli/config.yaml``)
3. Environment variables
4. Command-line arguments

Configuration File
------------------

The configuration file is located at ``~/.config/youtrack-cli/config.yaml`` by default.
You can specify a different location using the ``--config`` flag or the ``YT_CONFIG_FILE`` environment variable.

Example configuration file:

.. code-block:: yaml

   # YouTrack instance settings
   youtrack:
     url: "https://your-company.myjetbrains.com/youtrack"
     token: "your-api-token"
     username: "your-username"
     
   # Default settings
   defaults:
     project: "PROJECT-ID"
     assignee: "me"
     output_format: "table"  # table, json, yaml
     
   # Display settings
   display:
     max_results: 50
     show_colors: true
     pager: true
     
   # Time tracking
   time:
     default_duration_format: "hours"  # hours, minutes
     round_to_minutes: 15

Authentication Methods
----------------------

API Token (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

The most secure method is using an API token:

1. Generate a token in YouTrack: ``Profile > Account Security > API Tokens``
2. Set it in configuration:

.. code-block:: bash

   yt config set youtrack.token "your-api-token"

Or set the environment variable:

.. code-block:: bash

   export YT_TOKEN="your-api-token"

Username/Password
~~~~~~~~~~~~~~~~~

For development or testing:

.. code-block:: bash

   yt config set youtrack.username "your-username"
   yt config set youtrack.password "your-password"

Or use environment variables:

.. code-block:: bash

   export YT_USERNAME="your-username"
   export YT_PASSWORD="your-password"

Environment Variables
---------------------

All configuration options can be set via environment variables using the ``YT_`` prefix:

.. code-block:: bash

   export YT_URL="https://your-company.myjetbrains.com/youtrack"
   export YT_TOKEN="your-api-token"
   export YT_DEFAULT_PROJECT="PROJECT-ID"
   export YT_OUTPUT_FORMAT="json"
   export YT_MAX_RESULTS="100"

Configuration Commands
----------------------

View Configuration
~~~~~~~~~~~~~~~~~~

View all current configuration:

.. code-block:: bash

   yt config list

View specific configuration value:

.. code-block:: bash

   yt config get youtrack.url

Set Configuration
~~~~~~~~~~~~~~~~~

Set configuration values:

.. code-block:: bash

   yt config set youtrack.url "https://your-company.myjetbrains.com/youtrack"
   yt config set defaults.project "PROJECT-ID"
   yt config set display.output_format "json"

Configuration Options Reference
-------------------------------

YouTrack Connection
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 20 50
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``youtrack.url``
     - string
     - YouTrack instance URL
   * - ``youtrack.token``
     - string
     - API token for authentication
   * - ``youtrack.username``
     - string
     - Username for authentication
   * - ``youtrack.password``
     - string
     - Password for authentication
   * - ``youtrack.verify_ssl``
     - boolean
     - Verify SSL certificates (default: true)
   * - ``youtrack.timeout``
     - integer
     - Request timeout in seconds (default: 30)

Default Values
~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 20 50
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``defaults.project``
     - string
     - Default project for new issues
   * - ``defaults.assignee``
     - string
     - Default assignee for new issues
   * - ``defaults.priority``
     - string
     - Default priority for new issues
   * - ``defaults.state``
     - string
     - Default state for new issues

Display Settings
~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 20 50
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``display.output_format``
     - string
     - Output format: table, json, yaml (default: table)
   * - ``display.max_results``
     - integer
     - Maximum results to display (default: 50)
   * - ``display.show_colors``
     - boolean
     - Enable colored output (default: true)
   * - ``display.pager``
     - boolean
     - Use pager for long output (default: true)
   * - ``display.date_format``
     - string
     - Date format string (default: %Y-%m-%d %H:%M)

Time Tracking Settings
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 20 50
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``time.default_duration_format``
     - string
     - Duration format: hours, minutes (default: hours)
   * - ``time.round_to_minutes``
     - integer
     - Round time entries to nearest N minutes (default: 15)
   * - ``time.auto_start_timer``
     - boolean
     - Auto-start timer when updating issue state (default: false)

Troubleshooting
---------------

Configuration File Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're unsure where your configuration file is located:

.. code-block:: bash

   yt config list --show-file

Permission Issues
~~~~~~~~~~~~~~~~~

If you get permission errors, ensure the configuration directory exists and is writable:

.. code-block:: bash

   mkdir -p ~/.config/youtrack-cli
   chmod 755 ~/.config/youtrack-cli

Testing Configuration
~~~~~~~~~~~~~~~~~~~~~

Test your configuration by running:

.. code-block:: bash

   yt auth login --test