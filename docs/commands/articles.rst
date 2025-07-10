Articles Command Group
======================

The ``yt articles`` command group provides comprehensive management of YouTrack's knowledge base articles. Articles are documents that can be organized hierarchically and support comments and attachments.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

YouTrack articles serve as a knowledge base for documentation, guides, and collaborative content. The articles command group allows you to:

* Create, edit, and organize articles
* Manage article visibility and publishing status
* Handle hierarchical article structures (parent-child relationships)
* Tag articles for better organization and categorization
* Add and manage comments on articles
* Handle file attachments
* Search and filter articles
* Display articles in tree structures

Base Command
------------

.. code-block:: bash

   yt articles [OPTIONS] COMMAND [ARGS]...

Article Management Commands
---------------------------

create
~~~~~~

Create a new article in YouTrack.

.. code-block:: bash

   yt articles create TITLE [OPTIONS]

**Arguments:**

* ``TITLE`` - The title of the article (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--content, -c``
     - text
     - Article content (required if --file not provided)
   * - ``--file, -f``
     - path
     - Path to markdown file containing article content (required if --content not provided)
   * - ``--project-id, -p``
     - string
     - Project ID to associate with the article
   * - ``--parent-id``
     - string
     - Parent article ID for nested articles
   * - ``--summary, -s``
     - string
     - Article summary (defaults to title)
   * - ``--visibility``
     - choice
     - Article visibility: public, private, project (default: public)

**Examples:**

.. code-block:: bash

   # Create a simple article with inline content
   yt articles create "Getting Started Guide" --content "This is a comprehensive guide..."

   # Create an article from a markdown file
   yt articles create "Getting Started Guide" --file getting-started.md

   # Create an article in a specific project from a file
   yt articles create "API Documentation" --file api-docs.md --project-id PROJECT-123

   # Create a nested article (child of another article) from a file
   yt articles create "Advanced Features" --file advanced.md --parent-id ARTICLE-456

   # Create a draft article (private visibility) from a file
   yt articles create "Draft Article" --file draft.md --visibility private

   # Create an article with inline content (traditional approach)
   yt articles create "API Documentation" --content "API usage guide" --project-id PROJECT-123

edit
~~~~

Edit an existing article's properties.

.. code-block:: bash

   yt articles edit ARTICLE_ID [OPTIONS]

**Arguments:**

* ``ARTICLE_ID`` - The ID of the article to edit (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--title, -t``
     - string
     - New article title
   * - ``--content, -c``
     - string
     - New article content
   * - ``--summary, -s``
     - string
     - New article summary
   * - ``--visibility``
     - choice
     - New visibility level: public, private, project
   * - ``--show-details``
     - flag
     - Show detailed article information

**Examples:**

.. code-block:: bash

   # Update article title
   yt articles edit ARTICLE-123 --title "Updated Title"

   # Update article content
   yt articles edit ARTICLE-123 --content "Updated content"

   # Change visibility
   yt articles edit ARTICLE-123 --visibility public

   # View detailed article information
   yt articles edit ARTICLE-123 --show-details

publish
~~~~~~~

Publish a draft article (change from private to public visibility).

.. code-block:: bash

   yt articles publish ARTICLE_ID

**Arguments:**

* ``ARTICLE_ID`` - The ID of the draft article to publish (required)

**Examples:**

.. code-block:: bash

   # Publish a draft article
   yt articles publish ARTICLE-123

Article Listing and Discovery
-----------------------------

list
~~~~

List articles with filtering and formatting options.

.. code-block:: bash

   yt articles list [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--project-id, -p``
     - string
     - Filter by project ID
   * - ``--parent-id``
     - string
     - Filter by parent article ID
   * - ``--fields, -f``
     - string
     - Comma-separated list of fields to return
   * - ``--top, -t``
     - integer
     - Maximum number of articles to return
   * - ``--query, -q``
     - string
     - Search query to filter articles
   * - ``--format``
     - choice
     - Output format: table, json (default: table)

**Examples:**

.. code-block:: bash

   # List all articles
   yt articles list

   # List articles in table format (default)
   yt articles list --format table

   # List articles in JSON format
   yt articles list --format json

   # Filter articles by project
   yt articles list --project-id PROJECT-123

   # Filter articles by parent
   yt articles list --parent-id ARTICLE-456

   # Limit number of articles returned
   yt articles list --top 20

tree
~~~~

Display articles in hierarchical tree structure showing parent-child relationships.

.. code-block:: bash

   yt articles tree [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--project-id, -p``
     - string
     - Filter by project ID
   * - ``--fields, -f``
     - string
     - Comma-separated list of fields to return
   * - ``--top, -t``
     - integer
     - Maximum number of articles to return

**Examples:**

.. code-block:: bash

   # Display articles in hierarchical tree structure
   yt articles tree

   # Filter tree view by project
   yt articles tree --project-id PROJECT-123

search
~~~~~~

Search articles using full-text search.

.. code-block:: bash

   yt articles search QUERY [OPTIONS]

**Arguments:**

* ``QUERY`` - Search query string (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--project-id, -p``
     - string
     - Filter by project ID
   * - ``--top, -t``
     - integer
     - Maximum number of results to return
   * - ``--format``
     - choice
     - Output format: table, json (default: table)

**Examples:**

.. code-block:: bash

   # Search articles
   yt articles search "getting started"

   # Search articles in a specific project
   yt articles search "API" --project-id PROJECT-123

   # Limit search results
   yt articles search "documentation" --top 10

draft
~~~~~

List and manage draft articles (articles with private visibility).

.. code-block:: bash

   yt articles draft [OPTIONS]

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--project-id, -p``
     - string
     - Filter by project ID
   * - ``--format``
     - choice
     - Output format: table, json (default: table)

**Examples:**

.. code-block:: bash

   # List draft articles
   yt articles draft

   # Filter drafts by project
   yt articles draft --project-id PROJECT-123

sort
~~~~

View and organize child articles under a parent article.

.. code-block:: bash

   yt articles sort PARENT_ID [OPTIONS]

**Arguments:**

* ``PARENT_ID`` - The ID of the parent article (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--update``
     - flag
     - Apply changes to YouTrack after confirmation

**Examples:**

.. code-block:: bash

   # Sort child articles under a parent (preview mode)
   yt articles sort PARENT-ARTICLE-123

   # Sort child articles and apply changes (requires manual confirmation in YouTrack web interface)
   yt articles sort PARENT-ARTICLE-123 --update

Tag Management
--------------

tag
~~~

Add tags to an article for better organization and categorization.

.. code-block:: bash

   yt articles tag ARTICLE_ID [TAG_NAME1] [TAG_NAME2] ...

**Arguments:**

* ``ARTICLE_ID`` - The ID of the article to tag (required)
* ``TAG_NAME`` - Names of tags to add (optional, if not provided shows interactive selection)

**Interactive Mode:**

When no tag names are provided, the command enters interactive mode where you can:

* View all available tags in the system
* Select multiple tags using numbered indices
* Confirm your selection before applying

**Examples:**

.. code-block:: bash

   # Add specific tags to an article
   yt articles tag ARTICLE-123 bug documentation

   # Interactive tag selection (shows all available tags)
   yt articles tag ARTICLE-123

   # Add a single tag
   yt articles tag ARTICLE-123 urgent

**Interactive Mode Usage:**

.. code-block:: text

   🔍 Fetching available tags...

   📋 Available tags:
     1. bug (ID: 1-0)
     2. documentation (ID: 2-0)
     3. feature (ID: 3-0)
     4. urgent (ID: 4-0)
     5. review (ID: 5-0)

   💡 Enter tag numbers separated by spaces (e.g., 1 3 5) or 'q' to quit:
   1 2 4

   🏷️  Selected tags: bug, documentation, urgent
   🔄 Adding tags to article ARTICLE-123...
   ✅ Successfully added 3 tags to article ARTICLE-123

**Features:**

* **Tag Name Matching**: When providing tag names directly, the command performs case-insensitive matching
* **Interactive Selection**: Shows all available tags with their IDs for easy selection
* **Multi-select**: Can apply multiple tags in a single operation
* **Validation**: Validates that tags exist before applying them
* **Error Handling**: Provides clear feedback for invalid tags or articles

Comment Management
------------------

comments add
~~~~~~~~~~~~

Add a comment to an article.

.. code-block:: bash

   yt articles comments add ARTICLE_ID TEXT

**Arguments:**

* ``ARTICLE_ID`` - The ID of the article (required)
* ``TEXT`` - The comment text (required)

**Examples:**

.. code-block:: bash

   # Add a comment to an article
   yt articles comments add ARTICLE-123 "This is a helpful article!"

comments list
~~~~~~~~~~~~~

List comments on an article.

.. code-block:: bash

   yt articles comments list ARTICLE_ID [OPTIONS]

**Arguments:**

* ``ARTICLE_ID`` - The ID of the article (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--format``
     - choice
     - Output format: table, json (default: table)

**Examples:**

.. code-block:: bash

   # List comments on an article
   yt articles comments list ARTICLE-123

   # List comments in JSON format
   yt articles comments list ARTICLE-123 --format json

comments update
~~~~~~~~~~~~~~~

Update an existing comment (not yet implemented).

.. code-block:: bash

   yt articles comments update COMMENT_ID TEXT

**Arguments:**

* ``COMMENT_ID`` - The ID of the comment (required)
* ``TEXT`` - The new comment text (required)

.. note::
   This functionality is not yet implemented and requires additional API endpoints.

comments delete
~~~~~~~~~~~~~~~

Delete a comment (not yet implemented).

.. code-block:: bash

   yt articles comments delete COMMENT_ID [OPTIONS]

**Arguments:**

* ``COMMENT_ID`` - The ID of the comment to delete (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--confirm``
     - flag
     - Skip confirmation prompt

.. note::
   This functionality is not yet implemented and requires additional API endpoints.

Attachment Management
---------------------

attach list
~~~~~~~~~~~

List attachments for an article.

.. code-block:: bash

   yt articles attach list ARTICLE_ID [OPTIONS]

**Arguments:**

* ``ARTICLE_ID`` - The ID of the article (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--format``
     - choice
     - Output format: table, json (default: table)

**Examples:**

.. code-block:: bash

   # List attachments for an article
   yt articles attach list ARTICLE-123

   # List attachments in JSON format
   yt articles attach list ARTICLE-123 --format json

attach upload
~~~~~~~~~~~~~

Upload a file to an article (not yet implemented).

.. code-block:: bash

   yt articles attach upload ARTICLE_ID FILE_PATH

**Arguments:**

* ``ARTICLE_ID`` - The ID of the article (required)
* ``FILE_PATH`` - Path to the file to upload (required)

.. note::
   This functionality is not yet implemented and requires multipart form upload implementation.

attach download
~~~~~~~~~~~~~~~

Download an attachment from an article (not yet implemented).

.. code-block:: bash

   yt articles attach download ARTICLE_ID ATTACHMENT_ID [OPTIONS]

**Arguments:**

* ``ARTICLE_ID`` - The ID of the article (required)
* ``ATTACHMENT_ID`` - The ID of the attachment (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--output, -o``
     - path
     - Output file path

.. note::
   This functionality is not yet implemented and requires binary file handling.

attach delete
~~~~~~~~~~~~~

Delete an attachment from an article (not yet implemented).

.. code-block:: bash

   yt articles attach delete ARTICLE_ID ATTACHMENT_ID [OPTIONS]

**Arguments:**

* ``ARTICLE_ID`` - The ID of the article (required)
* ``ATTACHMENT_ID`` - The ID of the attachment to delete (required)

**Options:**

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Option
     - Type
     - Description
   * - ``--confirm``
     - flag
     - Skip confirmation prompt

.. note::
   This functionality is not yet implemented and requires additional API endpoints.

Article Features
----------------

**Hierarchical Organization**
  Articles support parent-child relationships, allowing you to create structured documentation with nested sections.

**Visibility Control**
  Articles can have different visibility levels:

  * **public** - Visible to all users
  * **private** - Visible only to the author (draft mode)
  * **project** - Visible to project members only

**Rich Content Support**
  Articles support rich text content including formatting, links, and embedded content.

**Collaboration**
  Comments allow team members to collaborate on articles and provide feedback.

**File Attachments**
  Articles can have file attachments for additional resources and documentation.

**Search and Discovery**
  Full-text search capabilities make it easy to find relevant articles across your knowledge base.

Common Workflows
----------------

Creating Documentation Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create main documentation article
   yt articles create "Project Documentation" --content "Main documentation hub" --project-id PROJECT-123

   # Create child articles
   yt articles create "Getting Started" --content "How to get started" --parent-id MAIN-ARTICLE-ID
   yt articles create "API Reference" --content "API documentation" --parent-id MAIN-ARTICLE-ID
   yt articles create "Troubleshooting" --content "Common issues" --parent-id MAIN-ARTICLE-ID

   # View the documentation tree
   yt articles tree --project-id PROJECT-123

Draft to Publication Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create a draft article
   yt articles create "New Feature Guide" --content "Draft content" --visibility private

   # Edit and refine the draft
   yt articles edit ARTICLE-123 --content "Updated draft content"

   # Publish when ready
   yt articles publish ARTICLE-123

Content Management
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Search for articles to update
   yt articles search "outdated"

   # Update article content
   yt articles edit ARTICLE-123 --content "Updated content for 2024"

   # Add comments for collaboration
   yt articles comments add ARTICLE-123 "Please review the updated content"

   # View article details
   yt articles edit ARTICLE-123 --show-details

   # Tag articles for better organization
   yt articles tag ARTICLE-123 documentation tutorial

Working with Markdown Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create articles from existing markdown files
   yt articles create "Installation Guide" --file docs/installation.md

   # Create multiple articles from markdown files
   yt articles create "User Manual" --file user-manual.md --project-id PROJECT-123
   yt articles create "Developer Guide" --file dev-guide.md --project-id PROJECT-123

   # Organize markdown documentation into YouTrack articles
   for file in docs/*.md; do
       title=$(basename "$file" .md)
       yt articles create "$title" --file "$file" --project-id PROJECT-123
   done

Best Practices
--------------

1. **Use Hierarchical Structure**: Organize articles in a logical hierarchy using parent-child relationships.

2. **Clear Titles**: Use descriptive titles that make articles easy to find and understand.

3. **Draft First**: Create articles as drafts (private visibility) to refine content before publishing.

4. **Regular Updates**: Keep articles current by regularly reviewing and updating content.

5. **Leverage Comments**: Use comments for collaboration and feedback on article content.

6. **Project Organization**: Associate articles with relevant projects for better organization.

7. **Search Optimization**: Use clear, searchable content to make articles discoverable.

8. **Consistent Formatting**: Follow consistent formatting and style guidelines across articles.

9. **Use Markdown Files**: For complex content, consider writing in markdown files first and using the ``--file`` option for better version control and editing experience.

Error Handling
--------------

Common error scenarios and solutions:

**Permission Denied**
  Ensure you have appropriate permissions to create, edit, or view articles in the specified project.

**Article Not Found**
  Verify the article ID exists and you have access to view it.

**Invalid Parent ID**
  Check that the parent article ID exists and you have permission to create child articles.

**Visibility Restrictions**
  Ensure you have appropriate permissions for the specified visibility level.

**Content Too Large**
  YouTrack may have limits on article content size. Consider breaking large articles into smaller sections.

**File Not Found**
  Ensure the file path provided with ``--file`` exists and is accessible.

**Invalid File Content**
  The specified file must be a valid text file. Binary files or files with invalid encoding will be rejected.

**Empty File**
  Files provided with ``--file`` must contain content. Empty files will be rejected.

**Both Content and File Specified**
  You cannot use both ``--content`` and ``--file`` options simultaneously. Choose one method for providing article content.

See Also
--------

* :doc:`projects` - Project management commands
* :doc:`auth` - Authentication setup
* :doc:`config` - Configuration management
