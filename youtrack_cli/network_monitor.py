"""Network traffic monitoring for YouTrack reordering analysis."""

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


@dataclass
class NetworkRequest:
    """Captured network request data."""

    timestamp: str
    method: str
    url: str
    headers: Dict[str, str]
    request_data: Optional[str] = None
    response_status: Optional[int] = None
    response_data: Optional[str] = None


class YouTrackNetworkMonitor:
    """Monitor network traffic during YouTrack operations."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.driver: Optional[webdriver.Chrome] = None
        self.captured_requests: List[NetworkRequest] = []

    def setup_monitoring_browser(self) -> bool:
        """Setup Chrome with network monitoring enabled."""
        if not SELENIUM_AVAILABLE:
            print("Selenium not available. Install with: pip install selenium")
            return False

        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        # Enable network logging
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--enable-logging")
        options.add_argument("--log-level=0")

        # Performance logging to capture network events
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        try:
            self.driver = webdriver.Chrome(options=options)
            self._setup_network_interception()
            return True
        except Exception as e:
            print(f"Failed to setup browser: {e}")
            return False

    def _setup_network_interception(self):
        """Setup network request interception."""
        if not self.driver:
            return

        try:
            # Enable network domain
            self.driver.execute_cdp_cmd("Network.enable", {})
            self.driver.execute_cdp_cmd("Runtime.enable", {})

            # Add network event listeners
            self.driver.add_cdp_listener("Network.requestWillBeSent", self._on_request_sent)
            self.driver.add_cdp_listener("Network.responseReceived", self._on_response_received)

        except Exception as e:
            print(f"Failed to setup network interception: {e}")

    def _on_request_sent(self, event):
        """Handle network request sent event."""
        try:
            request_data = event.get("request", {})
            url = request_data.get("url", "")

            # Only capture requests to YouTrack API or relevant endpoints
            if self.base_url in url or "/api/" in url or "article" in url.lower() or "ordinal" in url.lower():
                captured_request = NetworkRequest(
                    timestamp=datetime.now().isoformat(),
                    method=request_data.get("method", "UNKNOWN"),
                    url=url,
                    headers=request_data.get("headers", {}),
                    request_data=json.dumps(request_data.get("postData")) if request_data.get("postData") else None,
                )

                self.captured_requests.append(captured_request)
                print(f"📡 Captured: {captured_request.method} {url}")

        except Exception as e:
            print(f"Error capturing request: {e}")

    def _on_response_received(self, event):
        """Handle network response received event."""
        try:
            response_data = event.get("response", {})
            url = response_data.get("url", "")

            # Find matching request and update with response data
            for request in reversed(self.captured_requests):
                if request.url == url and request.response_status is None:
                    request.response_status = response_data.get("status")
                    break

        except Exception as e:
            print(f"Error capturing response: {e}")

    def start_monitoring_session(self, project_id: str) -> bool:
        """Start an interactive monitoring session."""
        if not self.setup_monitoring_browser():
            return False

        try:
            # Navigate to YouTrack articles
            articles_url = f"{self.base_url}/articles/{project_id}"
            print(f"🌐 Navigating to: {articles_url}")
            self.driver.get(articles_url)
            time.sleep(3)

            print("🎯 INSTRUCTIONS:")
            print("1. The browser is now open and monitoring network traffic")
            print("2. Please manually reorder articles using drag-and-drop")
            print("3. When finished, close the browser or press Ctrl+C")
            print("4. All network requests will be captured and analyzed")
            print("\n⚡ Monitoring started... Perform your reordering now!")

            # Keep the session alive
            input("Press Enter when you've finished reordering articles...")

            return True

        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            return True
        except Exception as e:
            print(f"❌ Monitoring session failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

    def analyze_captured_requests(self) -> Dict[str, Any]:
        """Analyze captured requests for reordering patterns."""
        if not self.captured_requests:
            return {"status": "error", "message": "No requests captured"}

        analysis = {
            "total_requests": len(self.captured_requests),
            "api_requests": [],
            "potential_reorder_endpoints": [],
            "interesting_patterns": [],
        }

        for request in self.captured_requests:
            if "/api/" in request.url:
                analysis["api_requests"].append(
                    {
                        "method": request.method,
                        "url": request.url,
                        "has_post_data": request.request_data is not None,
                        "status": request.response_status,
                    }
                )

                # Look for potential reordering endpoints
                if any(keyword in request.url.lower() for keyword in ["order", "ordinal", "position", "move", "sort"]):
                    analysis["potential_reorder_endpoints"].append(request.url)

                # Look for POST/PUT/PATCH requests to articles
                if request.method in ["POST", "PUT", "PATCH"] and "article" in request.url.lower():
                    analysis["interesting_patterns"].append(
                        {
                            "type": "article_modification",
                            "method": request.method,
                            "url": request.url,
                            "timestamp": request.timestamp,
                        }
                    )

        return analysis

    def export_captured_requests(self, filename: str = "youtrack_network_capture.json"):
        """Export captured requests to file for analysis."""
        try:
            export_data = {
                "capture_timestamp": datetime.now().isoformat(),
                "total_requests": len(self.captured_requests),
                "requests": [asdict(req) for req in self.captured_requests],
            }

            with open(filename, "w") as f:
                json.dump(export_data, f, indent=2)

            print(f"📄 Exported {len(self.captured_requests)} requests to {filename}")
            return True

        except Exception as e:
            print(f"❌ Failed to export requests: {e}")
            return False

    def generate_api_reproduction_script(self) -> str:
        """Generate a script to reproduce the captured API calls."""
        script_lines = [
            "#!/usr/bin/env python3",
            "# Generated script to reproduce YouTrack reordering API calls",
            "import requests",
            "import json",
            "",
            f"BASE_URL = '{self.base_url}'",
            "TOKEN = 'YOUR_TOKEN_HERE'",
            "headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}",
            "",
        ]

        for i, request in enumerate(self.captured_requests):
            if "/api/" in request.url and request.method in ["POST", "PUT", "PATCH"]:
                script_lines.extend(
                    [
                        f"# Request {i + 1}: {request.method} {request.url}",
                        f"response_{i} = requests.{request.method.lower()}(",
                        f"    '{request.url}',",
                        "    headers=headers,",
                    ]
                )

                if request.request_data:
                    script_lines.append(f"    json={request.request_data},")

                script_lines.extend([")", f"print(f'Response {i + 1}: {{response_{i}.status_code}}')", ""])

        return "\n".join(script_lines)


async def monitor_youtrack_reordering(base_url: str, project_id: str) -> Dict[str, Any]:
    """Main function to monitor YouTrack reordering network traffic."""
    monitor = YouTrackNetworkMonitor(base_url)

    print("🔍 Starting YouTrack Network Traffic Analysis")
    print("=" * 50)

    # Start monitoring session
    success = monitor.start_monitoring_session(project_id)

    if not success:
        return {"status": "error", "message": "Failed to start monitoring session"}

    # Analyze captured requests
    analysis = monitor.analyze_captured_requests()

    # Export for further analysis
    monitor.export_captured_requests()

    # Generate reproduction script
    repro_script = monitor.generate_api_reproduction_script()
    with open("youtrack_reorder_reproduction.py", "w") as f:
        f.write(repro_script)

    print("\n📊 ANALYSIS RESULTS:")
    print(f"Total requests captured: {analysis['total_requests']}")
    print(f"API requests: {len(analysis['api_requests'])}")
    print(f"Potential reorder endpoints: {len(analysis['potential_reorder_endpoints'])}")

    if analysis["potential_reorder_endpoints"]:
        print("\n🎯 POTENTIAL REORDERING ENDPOINTS:")
        for endpoint in analysis["potential_reorder_endpoints"]:
            print(f"  • {endpoint}")

    return {
        "status": "success",
        "message": "Network monitoring completed",
        "analysis": analysis,
        "captured_requests": len(monitor.captured_requests),
    }
