Installation
============

Requirements
------------

* Python 3.9 or higher
* An active YouTrack instance
* API access to your YouTrack instance

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

   git clone https://github.com/your-org/youtrack-cli.git
   cd youtrack-cli
   pip install -e .

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

For development, install with development dependencies:

.. code-block:: bash

   git clone https://github.com/your-org/youtrack-cli.git
   cd youtrack-cli
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