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

Next Steps
----------

After installation, you'll need to configure YouTrack CLI to connect to your YouTrack instance.
See :doc:`configuration` for details on setting up authentication and connection settings.