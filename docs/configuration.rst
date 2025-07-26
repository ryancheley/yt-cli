Configuration
=============

YouTrack CLI can be configured through multiple methods, allowing you to customize
its behavior to match your workflow.

Configuration Sources
--------------------

YouTrack CLI reads configuration from multiple sources in this order (later sources override earlier ones):

1. Default values
2. Configuration file (``~/.config/youtrack-cli/.env``)
3. Environment variables
4. Command-line arguments

Configuration File
------------------

The configuration file is an environment file located at ``~/.config/youtrack-cli/.env`` by default.
You can specify a different location using the ``--config`` flag.

**Creating the Configuration File:**

The easiest way to set up configuration is through the ``yt auth login`` command, which will automatically create the configuration file. Alternatively, you can create it manually:

.. code-block:: bash

   # Create configuration directory
   mkdir -p ~/.config/youtrack-cli

   # Create the .env configuration file
   cat > ~/.config/youtrack-cli/.env << EOF
   YOUTRACK_BASE_URL=https://yourcompany.youtrack.cloud
   YOUTRACK_TOKEN=your-api-token-here
   YOUTRACK_USERNAME=your-username
   EOF

**Configuration File Format:**

.. code-block:: bash

   # YouTrack instance settings (required)
   YOUTRACK_BASE_URL=https://yourcompany.youtrack.cloud
   YOUTRACK_TOKEN=perm:your-api-token-here
   YOUTRACK_USERNAME=your-username

   # Optional: Default project for commands
   DEFAULT_PROJECT=PROJECT-ID

   # Optional: Output format preference
   OUTPUT_FORMAT=table

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

   export YT_URL="https://yourcompany.youtrack.cloud"
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

   yt config set youtrack.url "https://yourcompany.youtrack.cloud"
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
     - Verify SSL certificates (default: true). **WARNING**: Disabling SSL verification is insecure and should only be used in development environments.
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

Theme Settings
~~~~~~~~~~~~~~

YouTrack CLI supports comprehensive theme customization, allowing you to personalize the appearance of console output with built-in themes or create your own custom themes.

.. list-table::
   :widths: 30 20 50
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``YOUTRACK_THEME``
     - string
     - Console theme: default, dark, light, or custom theme name (default: default)

**Built-in Themes:**

* **default**: Standard theme with cyan info text, green success, and red errors
* **dark**: High-contrast theme optimized for dark terminals with bright colors
* **light**: Theme optimized for light terminals with darker text colors

**Theme Management Commands:**

YouTrack CLI provides comprehensive theme management through the ``yt config theme`` command group:

.. code-block:: bash

   # List all available themes (built-in + custom)
   yt config theme list

   # Show current theme and preview
   yt config theme current

   # Set active theme
   yt config theme set dark

   # Create a new custom theme interactively
   yt config theme create my-theme

   # Create a theme based on an existing one
   yt config theme create my-dark --base dark

   # Delete a custom theme
   yt config theme delete my-theme

   # Export a theme to JSON file
   yt config theme export dark my-dark-theme.json

   # Import a theme from JSON file
   yt config theme import my-theme.json

   # Import with custom name
   yt config theme import downloaded-theme.json my-custom-name

**Setting a Theme:**

There are multiple ways to set your active theme:

.. code-block:: bash

   # Using theme command (recommended)
   yt config theme set dark

   # Using config command
   yt config set YOUTRACK_THEME dark

   # Via configuration file
   echo "YOUTRACK_THEME=dark" >> ~/.config/youtrack-cli/.env

   # Via environment variable
   export YOUTRACK_THEME=light

   # Test different themes temporarily
   YOUTRACK_THEME=dark yt issues list
   YOUTRACK_THEME=light yt projects list

**Creating Custom Themes:**

The ``yt config theme create`` command provides an interactive interface for creating custom themes:

.. code-block:: bash

   # Create a new theme from scratch
   yt config theme create my-theme

   # Create based on existing theme
   yt config theme create my-dark --base dark

The interactive creator will guide you through customizing:

1. **Core colors** (most commonly customized):
   - info, warning, error, success
   - header, link, highlight

2. **Additional colors** (optional):
   - field, value, muted, prompt
   - title, subtitle
   - progress indicators
   - table styling

**Custom Theme Storage:**

Custom themes are stored as JSON files in ``~/.config/youtrack-cli/themes/``:

.. code-block:: json

   {
     "name": "my-custom-theme",
     "description": "My personalized theme",
     "colors": {
       "info": "bright_blue",
       "warning": "orange",
       "error": "bright_red",
       "success": "bright_green",
       "header": "bold bright_cyan",
       "link": "blue underline",
       "highlight": "bold bright_yellow"
     }
   }

**Theme Import/Export:**

Share themes with team members or backup your customizations:

.. code-block:: bash

   # Export current theme
   yt config theme export my-theme my-team-theme.json

   # Share with team members
   yt config theme import team-theme.json

   # Export built-in theme as starting point
   yt config theme export dark dark-base.json

**Color Values:**

Themes support Rich's extensive color system:

* **Standard colors**: black, red, green, yellow, blue, magenta, cyan, white
* **Bright colors**: bright_red, bright_green, bright_blue, etc.
* **RGB colors**: rgb(255,0,0), #ff0000
* **Style modifiers**: bold, italic, underline, dim
* **Combinations**: "bold red", "underline blue", "dim cyan"

**Theme Styles Reference:**

Each theme provides consistent styling for these elements:

* **info**: Informational messages and highlights
* **warning**: Warning messages and cautions
* **success**: Success messages and confirmations
* **error**: Error messages and failures
* **prompt**: Interactive prompts and user input
* **field**: Field names and labels
* **value**: Field values and data
* **highlight**: Important text highlights
* **link**: URLs and clickable links
* **header**: Table headers and section titles
* **title**: Page and section titles
* **subtitle**: Secondary headings
* **muted**: Less important or secondary text
* **progress.description**: Progress bar descriptions
* **progress.percentage**: Progress bar percentages
* **progress.elapsed**: Progress bar elapsed time
* **table.header**: Table column headers
* **table.row**: Standard table rows
* **table.row.odd**: Alternating table rows
* **panel.border**: Panel borders
* **panel.title**: Panel titles
* **panel.subtitle**: Panel subtitles

**Theme Examples:**

Example custom theme configurations:

.. code-block:: bash

   # Minimal theme with just core colors
   yt config theme create minimal
   # Set: info=blue, warning=yellow, error=red, success=green

   # High-contrast theme for accessibility
   yt config theme create high-contrast --base dark
   # Customize with brighter, more distinct colors

   # Monochrome theme
   yt config theme create mono
   # Use only grayscale colors for minimal distraction

**Troubleshooting Themes:**

If you experience theme issues:

.. code-block:: bash

   # Reset to default theme
   yt config theme set default

   # Check current theme
   yt config theme current

   # List all available themes
   yt config theme list

   # Remove problematic custom theme
   yt config theme delete problematic-theme

Common issues:

* **Colors not displaying**: Check terminal color support
* **Theme not found**: Verify theme name with ``yt config theme list``
* **Import failed**: Validate JSON format and color values
* **Permission errors**: Ensure ``~/.config/youtrack-cli/themes/`` is writable

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

Configuration Examples
-----------------------

Basic Setup Example
~~~~~~~~~~~~~~~~~~~

Simple configuration for a single YouTrack instance:

.. code-block:: bash

   # ~/.config/youtrack-cli/.env
   YOUTRACK_BASE_URL=https://company.youtrack.cloud
   YOUTRACK_TOKEN=perm:cm9vdC5yb290.UGVybWlzc2lvbnM=.1234567890abcdef
   YOUTRACK_USERNAME=john.doe
   DEFAULT_PROJECT=WEB
   OUTPUT_FORMAT=table

Team Development Example
~~~~~~~~~~~~~~~~~~~~~~~~

Configuration optimized for team development workflows:

.. code-block:: bash

   # ~/.config/youtrack-cli/.env
   YOUTRACK_BASE_URL=https://company.youtrack.cloud
   YOUTRACK_TOKEN=perm:your-token-here
   YOUTRACK_USERNAME=team.developer

   # Project defaults
   DEFAULT_PROJECT=TEAM-PROJECT

   # Issue defaults
   DEFAULTS_ASSIGNEE=john.doe
   DEFAULTS_PRIORITY=Medium
   DEFAULTS_TYPE=Task

   # Display preferences
   OUTPUT_FORMAT=table
   MAX_RESULTS=25
   SHOW_COLORS=true
   DATE_FORMAT=%Y-%m-%d %H:%M
   YOUTRACK_THEME=dark

   # Time tracking
   TIME_ROUND_TO_MINUTES=15
   TIME_DEFAULT_DURATION_FORMAT=hours

CI/CD Pipeline Example
~~~~~~~~~~~~~~~~~~~~~~

Configuration for automated CI/CD integration:

.. code-block:: bash

   # CI environment variables
   export YT_URL="https://company.youtrack.cloud"
   export YT_TOKEN="${YOUTRACK_API_TOKEN}"  # From CI secrets
   export YT_OUTPUT_FORMAT="json"
   export YT_MAX_RESULTS="100"
   export YT_SHOW_COLORS="false"
   export YT_VERIFY_SSL="true"

Multi-Environment Example
~~~~~~~~~~~~~~~~~~~~~~~~~~

Using different configurations for different environments:

.. code-block:: bash

   # Development environment
   # ~/.config/youtrack-cli/dev.env
   YOUTRACK_BASE_URL=https://dev.youtrack.company.com
   YOUTRACK_TOKEN=perm:dev-token-here
   DEFAULT_PROJECT=DEV-PROJECT
   OUTPUT_FORMAT=table

   # Production environment
   # ~/.config/youtrack-cli/prod.env
   YOUTRACK_BASE_URL=https://youtrack.company.com
   YOUTRACK_TOKEN=perm:prod-token-here
   DEFAULT_PROJECT=PROD-PROJECT
   OUTPUT_FORMAT=json

   # Usage with different configs:
   # yt --config ~/.config/youtrack-cli/dev.env issues list
   # yt --config ~/.config/youtrack-cli/prod.env issues list

Corporate Proxy Example
~~~~~~~~~~~~~~~~~~~~~~~~

Configuration for environments behind corporate proxy:

.. code-block:: bash

   # ~/.config/youtrack-cli/.env
   YOUTRACK_BASE_URL=https://youtrack.company.com
   YOUTRACK_TOKEN=perm:your-token-here
   YOUTRACK_USERNAME=corporate.user

   # Proxy settings (via environment variables)
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   export NO_PROXY=localhost,127.0.0.1,.company.com

   # SSL settings for corporate certificates
   YOUTRACK_VERIFY_SSL=true
   YOUTRACK_TIMEOUT=60
