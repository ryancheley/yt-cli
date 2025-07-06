Performance Optimizations
=========================

This document describes the performance optimizations implemented in yt-cli to improve response times and resource usage, especially when working with large datasets.

Overview
--------

The yt-cli includes several performance optimizations:

1. **HTTP Connection Pooling** - Reuses HTTP connections for better performance
2. **Caching Layer** - Caches frequently accessed resources to reduce API calls
3. **Pagination Helpers** - Efficiently handles large result sets
4. **Batch Operations** - Processes multiple requests concurrently
5. **Response Optimization** - Requests only needed fields and supports streaming

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

The pagination helpers automatically fetch all results from paginated endpoints:

.. code-block:: python

   from youtrack_cli.utils import paginate_results

   # Fetch all issues with automatic pagination
   all_issues = await paginate_results(
       endpoint="https://youtrack.example.com/api/issues",
       headers=auth_headers,
       page_size=100,  # Items per page
       max_results=1000,  # Optional limit
   )

Parameters
~~~~~~~~~~

- ``endpoint``: API endpoint URL
- ``headers``: Optional request headers
- ``params``: Optional query parameters
- ``page_size``: Number of items per page (default: 100)
- ``max_results``: Maximum number of results to fetch (None for all)

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

Field Selection
~~~~~~~~~~~~~~~

Request only the fields you need to reduce response size and processing time:

.. code-block:: python

   from youtrack_cli.utils import optimize_fields

   # Optimize API parameters to only fetch needed fields
   params = optimize_fields(
       base_params={"project": "PROJ"},
       fields=["id", "summary", "state", "assignee"],
       exclude_fields=["description", "comments"]
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
