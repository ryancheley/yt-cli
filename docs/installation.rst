Installation
============

Requirements
------------

* Python 3.9 or higher
* An active YouTrack instance
* API access to your YouTrack instance

Platform-Specific Setup
------------------------

Windows
~~~~~~~

1. **Install Python** (if not already installed):

   Download Python from https://python.org/downloads/ and ensure "Add Python to PATH" is checked during installation.

2. **Verify Python installation**:

   .. code-block:: cmd

      python --version
      pip --version

3. **Install YouTrack CLI**:

   .. code-block:: cmd

      pip install youtrack-cli

macOS
~~~~~

1. **Install Python** (if not already installed):

   Using Homebrew (recommended):

   .. code-block:: bash

      brew install python

   Or download from https://python.org/downloads/

2. **Verify Python installation**:

   .. code-block:: bash

      python3 --version
      pip3 --version

3. **Install YouTrack CLI**:

   .. code-block:: bash

      pip3 install youtrack-cli

Linux (Ubuntu/Debian)
~~~~~~~~~~~~~~~~~~~~~~

1. **Install Python** (if not already installed):

   .. code-block:: bash

      sudo apt update
      sudo apt install python3 python3-pip

2. **Verify Python installation**:

   .. code-block:: bash

      python3 --version
      pip3 --version

3. **Install YouTrack CLI**:

   .. code-block:: bash

      pip3 install youtrack-cli

Installation Methods
--------------------

From PyPI (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

Install the latest stable version from PyPI:

.. code-block:: bash

   pip install youtrack-cli

From Source
~~~~~~~~~~~

Install from the latest source code:

.. code-block:: bash

   git clone https://github.com/ryancheley/yt-cli.git
   cd yt-cli
   uv sync
   uv pip install -e .

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

For development, install with development dependencies:

.. code-block:: bash

   git clone https://github.com/ryancheley/yt-cli.git
   cd yt-cli
   uv sync --dev

Using uv (Recommended for Development)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have `uv <https://docs.astral.sh/uv/>`_ installed:

.. code-block:: bash

   uv add youtrack-cli

Verification
------------

Verify the installation by checking the version:

.. code-block:: bash

   yt --version

You should see output similar to:

.. code-block:: text

   YouTrack CLI version 0.1.0

Test Enhanced Features
~~~~~~~~~~~~~~~~~~~~~~

YouTrack CLI includes enhanced error handling and debugging capabilities:

.. code-block:: bash

   # Test help system
   yt --help

   # Test verbose mode
   yt --verbose --help

   # Test debug mode for detailed troubleshooting
   yt --debug --help

If you encounter any issues during installation, the CLI now provides helpful error messages with suggestions for resolution.

Shell Completion
----------------

YouTrack CLI supports shell completion for bash, zsh, and fish shells. This enables tab completion for commands, options, and arguments, improving your workflow efficiency.

Automatic Installation
~~~~~~~~~~~~~~~~~~~~~~

The easiest way to enable shell completion is using the automatic installation:

.. code-block:: bash

   # For bash users
   yt completion bash --install

   # For zsh users
   yt completion zsh --install

   # For fish users
   yt completion fish --install

After installation, restart your shell or source your shell configuration:

.. code-block:: bash

   # For bash
   exec bash
   # or
   source ~/.bashrc

   # For zsh
   exec zsh

   # For fish
   exec fish

Manual Installation
~~~~~~~~~~~~~~~~~~~

If you prefer manual installation or the automatic installation doesn't work for your setup, you can generate and install the completion scripts manually:

**Bash Completion**

.. code-block:: bash

   # Generate and install bash completion
   yt completion bash > ~/.local/share/bash-completion/completions/yt

   # Alternative locations (depending on your system):
   # System-wide: sudo yt completion bash > /usr/share/bash-completion/completions/yt
   # User-local: yt completion bash > ~/.bash_completion.d/yt

**Zsh Completion**

.. code-block:: bash

   # Generate and install zsh completion
   yt completion zsh > ~/.local/share/zsh/site-functions/_yt

   # Make sure the completion directory is in your fpath
   # Add this to your ~/.zshrc:
   # fpath=(~/.local/share/zsh/site-functions $fpath)

   # Alternative locations:
   # System-wide: sudo yt completion zsh > /usr/local/share/zsh/site-functions/_yt
   # Custom directory: yt completion zsh > ~/.zsh/completions/_yt

**Fish Completion**

.. code-block:: bash

   # Generate and install fish completion
   yt completion fish > ~/.config/fish/completions/yt.fish

   # Alternative system-wide location:
   # sudo yt completion fish > /usr/share/fish/completions/yt.fish

Verification
~~~~~~~~~~~~

To verify that shell completion is working:

1. Start a new shell session
2. Type ``yt `` and press Tab twice
3. You should see available commands like ``issues``, ``articles``, ``projects``, etc.
4. Try typing ``yt issues `` and press Tab to see subcommands

**Example completion behavior:**

.. code-block:: bash

   $ yt <TAB><TAB>
   admin      articles   auth       boards     completion config
   issues     projects   reports    setup      time       users

   $ yt issues <TAB><TAB>
   assign     attach     comments   create     delete     links
   list       move       search     tag        update

Troubleshooting Completion
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Completion not working?**

1. **Verify installation location**: Make sure the completion script is in a directory that your shell searches for completions
2. **Check shell configuration**: Ensure completion is enabled in your shell (most modern shells have it enabled by default)
3. **Restart shell**: Completion scripts are typically loaded when the shell starts
4. **Check permissions**: Ensure the completion script file is readable

**Bash-specific issues:**

- Ensure bash-completion package is installed: ``sudo apt install bash-completion`` (Ubuntu/Debian) or ``brew install bash-completion`` (macOS)
- Check that ``/etc/bash_completion`` or ``/usr/local/etc/bash_completion`` is sourced in your ``.bashrc``

**Zsh-specific issues:**

- Verify that the completion directory is in your ``fpath``
- Run ``compinit`` to rebuild the completion cache
- Check that ``autoload -U compinit && compinit`` is in your ``.zshrc``

**Fish-specific issues:**

- Fish automatically loads completions from standard locations
- Use ``fish_config`` command to check completion settings
- Restart fish or run ``exec fish`` to reload completions

Troubleshooting Installation
----------------------------

**Enhanced Error Messages**

YouTrack CLI now provides user-friendly error messages with actionable suggestions:

- **Module not found errors**: Includes suggestions for reinstallation
- **Permission errors**: Suggests using virtual environments or user-local installation
- **Python version issues**: Clearly indicates required Python version and upgrade steps

**Debug Mode for Installation Issues**

If you encounter problems, enable debug mode to see detailed information:

.. code-block:: bash

   # Enable debug output for troubleshooting
   python -c "import youtrack_cli; print('Installation successful')" --debug

**Common Installation Issues**

The enhanced error handling helps with:

- Missing dependencies (automatically suggests installation commands)
- Python version compatibility issues
- Virtual environment configuration
- PATH and executable location problems

Next Steps
----------

After installation, you'll need to configure YouTrack CLI to connect to your YouTrack instance.
See :doc:`configuration` for details on setting up authentication and connection settings.
