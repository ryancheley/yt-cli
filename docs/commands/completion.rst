Completion Command
==================

The ``yt completion`` command generates shell completion scripts for YouTrack CLI, enabling tab completion for commands, options, and arguments in your shell. This significantly improves CLI usability by providing interactive command discovery and reducing typing errors.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The completion command provides:

* Shell completion scripts for bash, zsh, fish, and PowerShell
* Automatic installation of completion scripts to appropriate system locations
* Tab completion for commands, subcommands, options, and arguments
* Context-aware completion suggestions based on YouTrack data
* Support for custom installation paths and manual setup

Shell completion enables you to press Tab while typing commands to automatically complete command names, option names, and even project IDs or issue numbers.

Base Command
------------

.. code-block:: bash

   yt completion {bash|zsh|fish|powershell} [OPTIONS]

Command Arguments and Options
-----------------------------

**Arguments:**
  * ``{bash|zsh|fish|powershell}`` - The shell type to generate completion for

**Options:**
  * ``--install`` - Install the completion script to the appropriate system location

**Examples:**

.. code-block:: bash

   # Generate bash completion script
   yt completion bash

   # Install bash completion (requires sudo on some systems)
   yt completion bash --install

   # Generate PowerShell completion script
   yt completion powershell

   # Generate zsh completion for manual installation
   yt completion zsh > ~/.zsh/completions/_yt

Supported Shells
----------------

Bash Completion
~~~~~~~~~~~~~~

Generate and install bash completion:

.. code-block:: bash

   # Generate bash completion script
   yt completion bash

   # Install system-wide (may require sudo)
   yt completion bash --install

   # Manual installation
   yt completion bash > ~/.local/share/bash-completion/completions/yt

**Installation Locations:**
  * **System-wide:** ``/usr/share/bash-completion/completions/yt``
  * **User-specific:** ``~/.local/share/bash-completion/completions/yt``
  * **Custom:** Any location in your ``BASH_COMPLETION_USER_DIR``

**Activation:**
After installation, restart your shell or run:

.. code-block:: bash

   source ~/.bashrc

Zsh Completion
~~~~~~~~~~~~~

Generate and install zsh completion:

.. code-block:: bash

   # Generate zsh completion script
   yt completion zsh

   # Manual installation to user completion directory
   yt completion zsh > ~/.zsh/completions/_yt

   # Add to zsh fpath (add to ~/.zshrc)
   fpath=(~/.zsh/completions $fpath)

**Installation Locations:**
  * **User-specific:** ``~/.zsh/completions/_yt``
  * **Oh My Zsh:** ``~/.oh-my-zsh/completions/_yt``
  * **System-wide:** ``/usr/local/share/zsh/site-functions/_yt``

**Activation:**
Add to your ``~/.zshrc``:

.. code-block:: bash

   # Enable completion system
   autoload -U compinit && compinit

   # Add custom completion directory
   fpath=(~/.zsh/completions $fpath)

Fish Completion
~~~~~~~~~~~~~~

Generate and install fish completion:

.. code-block:: bash

   # Generate fish completion script
   yt completion fish

   # Manual installation
   yt completion fish > ~/.config/fish/completions/yt.fish

**Installation Locations:**
  * **User-specific:** ``~/.config/fish/completions/yt.fish``
  * **System-wide:** ``/usr/share/fish/completions/yt.fish``

**Activation:**
Fish automatically loads completions from the completions directory. Restart your fish shell or run:

.. code-block:: bash

   fish_config reload

PowerShell Completion
~~~~~~~~~~~~~~~~~~~~

Generate PowerShell completion:

.. code-block:: bash

   # Generate PowerShell completion script
   yt completion powershell

   # Save to file for manual installation
   yt completion powershell > yt-completion.ps1

**Installation:**
Add to your PowerShell profile:

.. code-block:: powershell

   # Check current profile location
   $PROFILE

   # Add completion source to profile
   . path\to\yt-completion.ps1

Completion Features
-------------------

Command Completion
~~~~~~~~~~~~~~~~~

Tab completion works for all CLI commands and subcommands:

.. code-block:: bash

   # Tab completion examples
   yt i<TAB>         # Completes to: yt issues
   yt issues c<TAB>  # Completes to: yt issues create
   yt pro<TAB>       # Completes to: yt projects

Option Completion
~~~~~~~~~~~~~~~~

Complete option names and flags:

.. code-block:: bash

   # Option completion examples
   yt issues list --a<TAB>      # Completes to: --assignee
   yt projects create --n<TAB>  # Completes to: --name
   yt config set --h<TAB>       # Completes to: --help

Context-Aware Completion
~~~~~~~~~~~~~~~~~~~~~~~

Advanced completion based on YouTrack data (when implemented):

.. code-block:: bash

   # Context-aware examples (future enhancement)
   yt issues update PROJ-<TAB>     # Could complete issue IDs
   yt projects show <TAB>          # Could complete project names
   yt users assign <TAB>           # Could complete usernames

Installation Methods
--------------------

Automatic Installation
~~~~~~~~~~~~~~~~~~~~~

Use the ``--install`` flag for automatic installation:

.. code-block:: bash

   # Automatic installation (recommended)
   yt completion bash --install
   yt completion zsh --install

**Benefits:**
  * Handles system-specific installation paths automatically
  * Creates necessary directories if they don't exist
  * Sets appropriate file permissions
  * Provides installation success confirmation

Manual Installation
~~~~~~~~~~~~~~~~~~~

For custom setups or when automatic installation isn't available:

.. code-block:: bash

   # Manual installation examples
   yt completion bash > ~/.local/share/bash-completion/completions/yt
   yt completion zsh > ~/.zsh/completions/_yt
   yt completion fish > ~/.config/fish/completions/yt.fish
   yt completion powershell > yt-completion.ps1

**When to Use Manual Installation:**
  * Custom completion directory structures
  * Non-standard shell configurations
  * Systems without admin access for system-wide installation
  * Integration with existing completion management systems

Team and Enterprise Setup
--------------------------

Team Installation Scripts
~~~~~~~~~~~~~~~~~~~~~~~~~

Create installation scripts for consistent team setup:

.. code-block:: bash

   #!/bin/bash
   # team-completion-setup.sh

   SHELL_TYPE=$(basename "$SHELL")

   case "$SHELL_TYPE" in
       bash)
           yt completion bash --install
           echo "Bash completion installed"
           ;;
       zsh)
           yt completion zsh > ~/.zsh/completions/_yt
           echo "Zsh completion installed"
           ;;
       fish)
           yt completion fish > ~/.config/fish/completions/yt.fish
           echo "Fish completion installed"
           ;;
       *)
           echo "Unsupported shell: $SHELL_TYPE"
           ;;
   esac

Docker and Container Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~

Include completion setup in container environments:

.. code-block:: dockerfile

   # Dockerfile completion setup
   FROM ubuntu:latest

   # Install YouTrack CLI
   RUN pip install youtrack-cli

   # Setup bash completion
   RUN yt completion bash > /etc/bash_completion.d/yt

   # Ensure completion is loaded in bashrc
   RUN echo "source /etc/bash_completion.d/yt" >> /etc/bash.bashrc

CI/CD Integration
~~~~~~~~~~~~~~~~

Include completion setup in development environment automation:

.. code-block:: yaml

   # GitHub Codespaces devcontainer.json
   {
     "name": "YouTrack Development",
     "postCreateCommand": "yt completion bash --install",
     "customizations": {
       "vscode": {
         "extensions": ["ms-vscode.vscode-json"]
       }
     }
   }

Troubleshooting
---------------

Common Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

**Permission Denied:**
  * Try manual installation to user directories instead of system-wide
  * Use ``sudo`` for system-wide installation (bash/zsh)
  * Check directory permissions for completion directories

**Completion Not Working:**
  * Restart your shell after installation
  * Verify completion script is in the correct location
  * Check that completion system is enabled in your shell

**Shell-Specific Issues:**

**Bash:**
  * Ensure ``bash-completion`` package is installed
  * Verify ``~/.bashrc`` sources completion scripts
  * Check ``BASH_COMPLETION_USER_DIR`` environment variable

**Zsh:**
  * Ensure ``compinit`` is called in ``~/.zshrc``
  * Verify completion directory is in ``fpath``
  * Check for conflicting completion configurations

**Fish:**
  * Verify fish version supports completion features
  * Check completion directory permissions
  * Restart fish shell completely

**PowerShell:**
  * Ensure execution policy allows script loading
  * Verify profile loads the completion script
  * Check PowerShell version compatibility

Verification and Testing
~~~~~~~~~~~~~~~~~~~~~~~~

Test completion installation:

.. code-block:: bash

   # Test basic command completion
   yt i<TAB>

   # Test option completion
   yt issues list --<TAB>

   # Test subcommand completion
   yt projects <TAB>

Advanced Configuration
----------------------

Custom Completion Behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~

For advanced users, completion scripts can be customized:

.. code-block:: bash

   # Generate and customize completion script
   yt completion bash > custom-yt-completion.sh

   # Edit the script to add custom completion logic
   # Then source or install the customized version

Multiple CLI Tool Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integrate YouTrack CLI completion with other development tools:

.. code-block:: bash

   # Example integration with other CLIs in team setup
   yt completion bash --install
   gh completion -s bash > ~/.local/share/bash-completion/completions/gh
   docker completion bash > ~/.local/share/bash-completion/completions/docker

Performance Considerations
--------------------------

Completion Performance
~~~~~~~~~~~~~~~~~~~~~

Large projects or extensive command histories might affect completion performance:

* **Caching:** Completion systems cache results for better performance
* **Lazy Loading:** Some completions load data only when needed
* **Filtering:** Completion results are filtered based on current input

Optimization Tips
~~~~~~~~~~~~~~~~

* Restart shells periodically to clear completion caches
* Update completion scripts when CLI is updated
* Remove unused completion scripts to reduce memory usage

See Also
--------

* Shell-specific documentation for advanced completion customization
* :doc:`config` - CLI configuration that affects completion behavior
* :doc:`alias` - Command aliases that work with completion
* Installation guide for complete CLI setup instructions
