"""Deep API exploration for YouTrack article reordering."""

from typing import Any, Dict, Optional

from youtrack_cli.client import get_client_manager


class YouTrackAPIExplorer:
    """Explore YouTrack API for hidden reordering capabilities."""

    def __init__(self, auth_manager):
        self.auth_manager = auth_manager

    async def explore_api_endpoints(self) -> Dict[str, Any]:
        """Explore different API endpoints and versions."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        base_url = credentials.base_url.rstrip("/")
        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        endpoints_to_test = [
            # Different API versions
            "/api/admin/articles",
            "/rest/articles",
            "/hub/api/articles",
            "/api/v2/articles",
            "/api/articles/reorder",
            "/api/articles/sort",
            "/api/articles/move",
            "/api/articles/position",
            # Batch operations
            "/api/articles/batch",
            "/api/commands/articles",
            "/api/workflows/articles",
            # Admin endpoints
            "/api/admin/projects/articles",
            "/api/admin/articles/ordinal",
            "/api/admin/articles/hierarchy",
            # Knowledge base specific
            "/api/knowledgeBase/articles",
            "/api/kb/articles",
            "/api/documentation/articles",
        ]

        results = []
        client_manager = get_client_manager()

        for endpoint in endpoints_to_test:
            try:
                url = f"{base_url}{endpoint}"
                response = await client_manager.make_request("GET", url, headers=headers)

                results.append(
                    {
                        "endpoint": endpoint,
                        "status": "accessible",
                        "url": url,
                        "response_length": len(response) if response else 0,
                    }
                )
                print(f"✅ {endpoint} - Accessible")

            except Exception as e:
                results.append({"endpoint": endpoint, "status": "error", "error": str(e)})
                print(f"❌ {endpoint} - {str(e)[:50]}...")

        return {"status": "success", "results": results}

    async def test_article_update_methods(self, article_id: str) -> Dict[str, Any]:
        """Test different HTTP methods and payloads for article updates."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        base_url = credentials.base_url.rstrip("/")
        headers = {"Authorization": f"Bearer {credentials.token}", "Content-Type": "application/json"}

        # Test different payloads that might trigger ordinal updates
        test_payloads = [
            # Direct ordinal setting (probably won't work)
            {"ordinal": 100},
            # Position hints
            {"position": 1},
            {"index": 1},
            {"order": 1},
            # Special metadata
            {"$ordinal": 100},
            {"metadata": {"ordinal": 100}},
            # Batch operation format
            {"commands": [{"command": "move", "position": 1}]},
            # Workflow triggers
            {"workflow": {"action": "reorder", "position": 1}},
            # Parent manipulation with position
            {"parentArticle": None, "position": 1},
        ]

        results = []
        client_manager = get_client_manager()

        for i, payload in enumerate(test_payloads):
            try:
                url = f"{base_url}/api/articles/{article_id}"

                # Test with different HTTP methods
                for method in ["POST", "PUT", "PATCH"]:
                    try:
                        response = await client_manager.make_request(method, url, headers=headers, json_data=payload)

                        results.append(
                            {
                                "test": i + 1,
                                "method": method,
                                "payload": payload,
                                "status": "success",
                                "response": response[:200] if response else None,
                            }
                        )
                        print(f"✅ Test {i + 1} ({method}) - Success")

                    except Exception as e:
                        results.append(
                            {"test": i + 1, "method": method, "payload": payload, "status": "error", "error": str(e)}
                        )

            except Exception as e:
                print(f"❌ Test {i + 1} failed: {e}")

        return {"status": "success", "results": results}

    async def explore_graphql_api(self) -> Dict[str, Any]:
        """Check if YouTrack supports GraphQL for article operations."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        base_url = credentials.base_url.rstrip("/")
        headers = {"Authorization": f"Bearer {credentials.token}", "Content-Type": "application/json"}

        graphql_endpoints = ["/graphql", "/api/graphql", "/hub/graphql", "/query"]

        # Test GraphQL query for articles
        test_query = {
            "query": """
                query GetArticles {
                    articles {
                        id
                        summary
                        ordinal
                    }
                }
            """
        }

        results = []
        client_manager = get_client_manager()

        for endpoint in graphql_endpoints:
            try:
                url = f"{base_url}{endpoint}"
                response = await client_manager.make_request("POST", url, headers=headers, json_data=test_query)

                results.append(
                    {
                        "endpoint": endpoint,
                        "status": "success",
                        "supports_graphql": True,
                        "response_preview": response[:200] if response else None,
                    }
                )
                print(f"🔍 GraphQL available at {endpoint}")

            except Exception as e:
                results.append({"endpoint": endpoint, "status": "not_available", "error": str(e)})

        return {"status": "success", "results": results}

    async def test_websocket_connections(self) -> Dict[str, Any]:
        """Test if YouTrack uses WebSockets for real-time updates."""
        credentials = self.auth_manager.load_credentials()
        if not credentials:
            return {"status": "error", "message": "Not authenticated"}

        # Convert HTTP URL to WebSocket URL
        ws_base = credentials.base_url.replace("http://", "ws://").replace("https://", "wss://")

        websocket_endpoints = [
            f"{ws_base}/ws",
            f"{ws_base}/websocket",
            f"{ws_base}/api/ws",
            f"{ws_base}/hub/ws",
            f"{ws_base}/realtime",
        ]

        results = []

        for endpoint in websocket_endpoints:
            try:
                # Note: Would need websockets library for actual testing
                results.append(
                    {"endpoint": endpoint, "status": "test_not_implemented", "note": "Would require websockets library"}
                )
                print(f"🔌 WebSocket endpoint to test: {endpoint}")

            except Exception as e:
                results.append({"endpoint": endpoint, "status": "error", "error": str(e)})

        return {"status": "success", "results": results}


async def deep_api_exploration(auth_manager, article_id: Optional[str] = None) -> Dict[str, Any]:
    """Perform comprehensive API exploration for reordering capabilities."""
    explorer = YouTrackAPIExplorer(auth_manager)

    print("🔍 YOUTRACK DEEP API EXPLORATION")
    print("=" * 50)

    exploration_results = {}

    # Test 1: Explore different API endpoints
    print("\n1️⃣ Exploring API endpoints...")
    endpoints_result = await explorer.explore_api_endpoints()
    exploration_results["endpoints"] = endpoints_result

    # Test 2: Test article update methods (if article ID provided)
    if article_id:
        print(f"\n2️⃣ Testing article update methods on {article_id}...")
        update_result = await explorer.test_article_update_methods(article_id)
        exploration_results["update_methods"] = update_result

    # Test 3: Check for GraphQL support
    print("\n3️⃣ Checking GraphQL support...")
    graphql_result = await explorer.explore_graphql_api()
    exploration_results["graphql"] = graphql_result

    # Test 4: Test WebSocket endpoints
    print("\n4️⃣ Testing WebSocket endpoints...")
    websocket_result = await explorer.test_websocket_connections()
    exploration_results["websockets"] = websocket_result

    # Generate report
    accessible_endpoints = [r for r in exploration_results["endpoints"]["results"] if r["status"] == "accessible"]

    print("\n📊 EXPLORATION SUMMARY:")
    print(f"Accessible endpoints: {len(accessible_endpoints)}")

    if accessible_endpoints:
        print("🎯 PROMISING ENDPOINTS:")
        for endpoint in accessible_endpoints:
            print(f"  • {endpoint['endpoint']}")

    return {"status": "success", "message": "Deep API exploration completed", "results": exploration_results}
