Performance Optimizations
=========================

This document describes the performance optimizations implemented in yt-cli to improve response times and resource usage, especially when working with large datasets.

Overview
--------

The yt-cli includes several performance optimizations:

1. **HTTP Connection Pooling** - Reuses HTTP connections for better performance
2. **Caching Layer** - Caches frequently accessed resources to reduce API calls
3. **Field Selection Optimization** - Dynamic field selection reduces response sizes by up to 75%
4. **Pagination Helpers** - Efficiently handles large result sets
5. **Batch Operations** - Processes multiple requests concurrently
6. **Response Optimization** - Supports streaming for large responses

HTTP Connection Pooling
-----------------------

The CLI uses a centralized HTTP client manager with connection pooling to improve performance:

.. code-block:: python

   from youtrack_cli.client import get_client_manager

   # Get the shared client manager
   client_manager = get_client_manager()

   # Make requests using the pooled client
   response = await client_manager.make_request("GET", url, headers=headers)

Configuration
~~~~~~~~~~~~~

The connection pool can be configured with the following parameters:

- ``max_keepalive_connections``: Maximum number of keepalive connections (default: 20)
- ``max_connections``: Maximum total connections (default: 100)
- ``keepalive_expiry``: How long to keep idle connections alive in seconds (default: 30.0)

Caching Layer
-------------

The caching layer stores frequently accessed data in memory to reduce API calls.

Usage
~~~~~

.. code-block:: python

   from youtrack_cli.cache import cached, get_cache

   # Using the decorator
   @cached(ttl=600, key_prefix="projects")
   async def get_projects():
       # This will be cached for 10 minutes
       return await fetch_projects()

   # Manual caching
   cache = get_cache()
   await cache.set("key", data, ttl=300)
   cached_data = await cache.get("key")

Predefined Cache Decorators
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``@cache_projects(ttl=900)`` - Cache project data (15 minutes)
- ``@cache_users(ttl=1800)`` - Cache user data (30 minutes)
- ``@cache_fields(ttl=3600)`` - Cache custom field definitions (1 hour)
- ``@cache_boards(ttl=600)`` - Cache board data (10 minutes)

Cache Management
~~~~~~~~~~~~~~~~

.. code-block:: python

   from youtrack_cli.cache import get_cache, clear_cache

   cache = get_cache()

   # Get cache statistics
   stats = await cache.stats()

   # Clear expired entries
   removed_count = await cache.cleanup_expired()

   # Clear all cache
   await clear_cache()

Pagination Helpers
------------------

**NEW in v0.8.1**: Unified pagination system automatically detects and uses the optimal pagination strategy for each YouTrack API endpoint.

The yt-cli now provides a comprehensive pagination system that automatically handles the differences between YouTrack's cursor-based and offset-based pagination:

Automatic Pagination Type Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The system automatically detects which pagination type to use based on the endpoint:

- **Issues API** (``/api/issues``): Uses cursor-based pagination for optimal performance with large datasets
- **Projects API** (``/api/admin/projects``): Uses offset-based pagination
- **Users API** (``/api/users``): Uses offset-based pagination
- **Articles API** (``/api/articles``): Uses offset-based pagination

.. code-block:: python

   from youtrack_cli.utils import paginate_results

   # Auto-detects cursor pagination for issues endpoint
   result = await paginate_results(
       endpoint="https://youtrack.example.com/api/issues",
       headers=auth_headers,
       page_size=100,
       max_results=1000,
   )

   # Returns structured result with pagination metadata
   print(f"Fetched {result['total_results']} results")
   print(f"Pagination type used: {result['pagination_type']}")
   print(f"Has more results: {result['has_after']}")

Entity-Specific Pagination Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For convenience, use entity-specific pagination functions that automatically apply the correct configuration:

.. code-block:: python

   from youtrack_cli.utils import (
       paginate_issues,
       paginate_projects,
       paginate_users,
       paginate_articles
   )

   # Issues with cursor-based pagination
   issues_result = await paginate_issues(
       endpoint=f"{base_url}/api/issues",
       headers=headers,
       after_cursor="cursor_token",  # Navigate to next page
       max_results=5000,  # Automatically limited to safe defaults
   )

   # Projects with offset-based pagination
   projects_result = await paginate_projects(
       endpoint=f"{base_url}/api/admin/projects",
       headers=headers,
       max_results=1000,  # Automatically limited
   )

Centralized Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

Pagination behavior is centrally configured for consistency:

.. code-block:: python

   from youtrack_cli.utils import PaginationConfig

   # Default page sizes
   print(f"API page size: {PaginationConfig.DEFAULT_API_PAGE_SIZE}")  # 100
   print(f"Display page size: {PaginationConfig.DEFAULT_DISPLAY_PAGE_SIZE}")  # 50

   # Entity-specific limits
   print(f"Max issues: {PaginationConfig.get_max_results('issues')}")  # 10,000
   print(f"Max projects: {PaginationConfig.get_max_results('projects')}")  # 1,000

   # Check pagination type for endpoint
   pagination_type = PaginationConfig.get_pagination_type("/api/issues")
   print(f"Issues use: {pagination_type.value}")  # "cursor"

Advanced Pagination Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The unified system provides advanced features for optimal performance:

**Cursor Navigation** (Issues only):

.. code-block:: python

   # Navigate forward through pages
   result = await paginate_issues(
       endpoint=f"{base_url}/api/issues",
       headers=headers,
       after_cursor="next_page_token",
       page_size=50
   )

   # Navigate backward through pages
   result = await paginate_issues(
       endpoint=f"{base_url}/api/issues",
       headers=headers,
       before_cursor="prev_page_token",
       page_size=50
   )

**Automatic Safety Limits**:

.. code-block:: python

   # Each entity type has safe default limits
   # Issues: 10,000 max results
   # Projects: 1,000 max results
   # Users: 5,000 max results
   # Articles: 2,000 max results

Parameters
~~~~~~~~~~

**paginate_results()** - Universal pagination with auto-detection:

- ``endpoint``: API endpoint URL
- ``headers``: Optional request headers
- ``params``: Optional query parameters
- ``page_size``: Number of items per page (default: 100)
- ``max_results``: Maximum number of results to fetch (None for entity defaults)
- ``after_cursor``: Start pagination after this cursor (cursor pagination only)
- ``before_cursor``: Start pagination before this cursor (cursor pagination only)
- ``use_cursor_pagination``: Override auto-detection (None for auto-detect)

**Entity-specific functions** (``paginate_issues``, ``paginate_projects``, etc.):

- Same parameters as ``paginate_results()`` but with entity-optimized defaults
- ``paginate_issues()`` also supports ``after_cursor`` and ``before_cursor``
- Other entity functions use offset-based pagination automatically

Return Format
~~~~~~~~~~~~~

All pagination functions return a consistent format:

.. code-block:: python

   {
       "results": [...],                    # List of items
       "total_results": 150,                # Total items fetched
       "has_after": True,                   # More results available after
       "has_before": False,                 # Results available before
       "after_cursor": "next_token",        # Cursor for next page (cursor only)
       "before_cursor": None,               # Cursor for previous page (cursor only)
       "pagination_type": "cursor"          # Type used ("cursor" or "offset")
   }

Batch Operations
----------------

Process multiple requests concurrently for better performance:

.. code-block:: python

   from youtrack_cli.utils import batch_requests, batch_get_resources

   # Batch multiple different requests
   requests = [
       {"method": "GET", "url": "https://api.com/issues/PROJ-1"},
       {"method": "GET", "url": "https://api.com/issues/PROJ-2"},
       {"method": "GET", "url": "https://api.com/issues/PROJ-3"},
   ]
   responses = await batch_requests(requests, max_concurrent=10)

   # Batch fetch resources by ID
   issues = await batch_get_resources(
       base_url="https://youtrack.example.com/api/issues/{id}",
       resource_ids=["PROJ-1", "PROJ-2", "PROJ-3"],
       headers=auth_headers,
       max_concurrent=5
   )

Benefits
~~~~~~~~

- Significantly faster than sequential requests
- Controlled concurrency to avoid overwhelming the server
- Maintains request order in results
- Handles failures gracefully

Response Optimization
---------------------

Field Selection Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**NEW in v0.8.0**: Dynamic field selection optimization reduces API response sizes and improves performance by only requesting needed fields.

Field Selection Profiles
"""""""""""""""""""""""""

Three predefined profiles optimize for different use cases:

- **minimal**: Essential fields only (id, summary, state) - 75% data reduction
- **standard**: Common fields for general use (default) - 43% faster than full
- **full**: All available fields including custom fields and attachments

.. code-block:: bash

   # Use minimal profile for quick issue lists
   yt issues list --profile minimal

   # Use standard profile (default)
   yt issues list --profile standard

   # Use full profile when you need all details
   yt issues list --profile full

Custom Field Selection
""""""""""""""""""""""

Specify exactly which fields you need:

.. code-block:: bash

   # Request specific fields only
   yt issues list --fields "id,summary,state(name),assignee(login,fullName)"

   # Search with custom fields
   yt issues search "bug" --fields "id,summary,priority(name)"

Configuration
"""""""""""""

Set default field profiles in your configuration:

.. code-block:: bash

   # Set default profile for issues
   yt config set FIELD_PROFILE_ISSUES minimal

   # Set default for projects
   yt config set FIELD_PROFILE_PROJECTS standard

Performance Benchmarking
"""""""""""""""""""""""""

Benchmark field selection performance in your environment:

.. code-block:: bash

   # Run performance benchmark
   yt issues benchmark --project-id PROJECT --sample-size 50

Example benchmark results:

.. code-block:: text

   Profile      Avg Time     Performance Gain
   ----------------------------------------
   minimal      0.015s       55% faster
   standard     0.018s       43% faster
   full         0.033s       baseline

Programmatic Usage
""""""""""""""""""

Use field selection in your code:

.. code-block:: python

   from youtrack_cli.field_selection import get_field_selector

   # Get optimized field selection
   selector = get_field_selector()
   fields = selector.get_fields("issues", "minimal")

   # Custom field selection with exclusions
   fields = selector.get_fields(
       "issues",
       "standard",
       custom_fields=["priority(name)", "tags(name)"],
       exclude_fields=["description"]
   )

Streaming Large Responses
~~~~~~~~~~~~~~~~~~~~~~~~~

For large file downloads or responses, use streaming to avoid memory issues:

.. code-block:: python

   from youtrack_cli.utils import stream_large_response

   # Stream a large file download
   async with open("large_file.zip", "wb") as f:
       async for chunk in stream_large_response(download_url, headers=auth_headers):
           f.write(chunk)

Performance Monitoring
----------------------

Monitor and benchmark performance to track improvements:

.. code-block:: python

   from youtrack_cli.performance import performance_timer, benchmark_requests

   # Time individual operations
   async with performance_timer("fetch_issues", project="PROJ"):
       issues = await fetch_issues()

   # Benchmark operations
   result = await benchmark_requests(
       operation_name="api_call",
       async_func=lambda: make_api_call(),
       iterations=10,
       concurrent=3
   )

   print(f"Average duration: {result.avg_duration:.3f}s")
   print(f"Operations per second: {result.operations_per_second:.1f}")

Best Practices
--------------

For Large Datasets
~~~~~~~~~~~~~~~~~~

1. **Use pagination** with appropriate page sizes (100-500 items)
2. **Request only needed fields** using field selection
3. **Cache frequently accessed data** like project lists and user info
4. **Use batch operations** when fetching multiple resources

For High-Frequency Operations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Enable caching** with appropriate TTL values
2. **Use connection pooling** (enabled by default)
3. **Monitor performance** to identify bottlenecks
4. **Implement retry logic** with exponential backoff

For Memory-Constrained Environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Use streaming** for large file downloads
2. **Limit concurrent operations** to control memory usage
3. **Clear cache periodically** to free memory
4. **Use smaller page sizes** for pagination

Configuration
-------------

Performance settings can be configured through environment variables or configuration files:

.. code-block:: bash

   # Connection pool settings
   export YT_MAX_CONNECTIONS=50
   export YT_KEEPALIVE_CONNECTIONS=10

   # Cache settings
   export YT_CACHE_TTL=600
   export YT_CACHE_CLEANUP_INTERVAL=300

   # Request settings
   export YT_DEFAULT_PAGE_SIZE=100
   export YT_MAX_CONCURRENT=10

Monitoring
----------

Use the built-in performance monitoring to track improvements:

.. code-block:: python

   from youtrack_cli.performance import get_performance_monitor

   monitor = get_performance_monitor()

   # Get performance summary
   summary = monitor.summary("api_requests")
   print(f"Average API response time: {summary['avg_duration']:.3f}s")
   print(f"Total API calls: {summary['total_operations']}")

Troubleshooting
---------------

High Memory Usage
~~~~~~~~~~~~~~~~~

- Reduce concurrent operation limits
- Use streaming for large responses
- Clear cache more frequently
- Check for connection leaks

Slow Performance
~~~~~~~~~~~~~~~~

- Enable caching for frequently accessed data
- Use batch operations instead of sequential requests
- Monitor network latency
- Check YouTrack server performance

Connection Issues
~~~~~~~~~~~~~~~~~

- Verify connection pool settings
- Check network connectivity
- Review server-side rate limiting
- Monitor connection reuse rates
