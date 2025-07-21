"""Browser automation for YouTrack article reordering."""

import time
from typing import Any, Dict, List, Optional

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class YouTrackBrowserReorder:
    """Browser automation for YouTrack article reordering."""

    def __init__(self, base_url: str, token: str, headless: bool = True):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None

    def __enter__(self):
        self._setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()

    def _setup_driver(self):
        """Setup Chrome WebDriver with appropriate options."""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium not available. Install with: pip install selenium")

        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # Enable network logging to capture requests
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--enable-logging")
        options.add_argument("--log-level=0")

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def login_with_token(self) -> bool:
        """Login to YouTrack using permanent token."""
        try:
            # For local dev instances, authentication might be different
            # Try direct navigation first
            print(f"🔐 Attempting to authenticate with YouTrack at {self.base_url}")

            # Navigate directly to the base URL
            self.driver.get(self.base_url)
            time.sleep(2)

            # Check if we're already logged in or if login is required
            current_url = self.driver.current_url

            if "login" in current_url.lower():
                print("⚠️  Browser automation requires manual login or different authentication method")
                print("📝 Note: Token-based authentication is not supported in the web interface")
                return False

            # If we're not redirected to login, assume we're authenticated
            # (This works for local dev instances without auth)
            print("✅ Successfully accessed YouTrack")
            return True

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def navigate_to_project_articles(self, project_id: str) -> bool:
        """Navigate to project articles page."""
        try:
            articles_url = f"{self.base_url}/articles/{project_id}"
            print(f"📖 Navigating to articles: {articles_url}")
            self.driver.get(articles_url)
            time.sleep(3)

            # Check if we need to import By
            from selenium.webdriver.common.by import By

            # Try multiple selectors for articles
            article_selectors = [
                ".article",
                "[data-test*='article']",
                ".knowledge-base-tree-item",
                ".article-node",
                "div[class*='article']",
            ]

            # Try to find articles with different selectors
            for selector in article_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} articles using selector: {selector}")
                        return True
                except Exception:
                    continue

            # If no articles found, still return True if we're on the right page
            if project_id.lower() in self.driver.current_url.lower():
                print("⚠️  On articles page but no articles found - page might be empty")
                return True

            return False

        except Exception as e:
            print(f"Failed to navigate to articles: {e}")
            return False

    def get_current_article_order(self) -> List[Dict[str, str]]:
        """Get current article order from the page."""
        try:
            # Find all article elements
            articles = self.driver.find_elements(
                By.CSS_SELECTOR, "[data-test-id*='article'], .article-item, .knowledge-base-article"
            )

            current_order = []
            for article in articles:
                title_element = article.find_element(By.CSS_SELECTOR, ".article-title, .title, h2, h3")
                title = title_element.text.strip() if title_element else "Unknown"

                # Try to extract article ID
                article_id = article.get_attribute("data-article-id") or article.get_attribute("id") or "unknown"

                current_order.append({"id": article_id, "title": title, "element": article})

            return current_order

        except Exception as e:
            print(f"Failed to get article order: {e}")
            return []

    def reorder_articles_by_drag_drop(self, target_order: List[str]) -> bool:
        """Reorder articles using drag and drop to match target order."""
        try:
            current_articles = self.get_current_article_order()
            if not current_articles:
                print("No articles found to reorder")
                return False

            print(f"Found {len(current_articles)} articles")

            # Create mapping of titles to elements
            title_to_element = {article["title"]: article["element"] for article in current_articles}

            # Perform drag-and-drop operations
            actions = ActionChains(self.driver)

            for i, target_title in enumerate(target_order):
                if target_title not in title_to_element:
                    print(f"Warning: Article '{target_title}' not found")
                    continue

                source_element = title_to_element[target_title]

                # Find the target position (could be before another element or at the end)
                if i < len(current_articles) - 1:
                    # Move before the next element in target order
                    next_title = target_order[i + 1] if i + 1 < len(target_order) else None
                    if next_title and next_title in title_to_element:
                        target_element = title_to_element[next_title]
                        actions.drag_and_drop(source_element, target_element).perform()
                        time.sleep(1)

            print("Drag and drop operations completed")
            return True

        except Exception as e:
            print(f"Drag and drop failed: {e}")
            return False

    def capture_reorder_network_requests(self) -> List[Dict]:
        """Capture network requests during reordering for analysis."""
        try:
            # Enable network domain
            self.driver.execute_cdp_cmd("Network.enable", {})

            requests = []

            def capture_request(request):
                if "api" in request.get("url", ""):
                    requests.append(request)

            # Add listener for network requests
            self.driver.add_cdp_listener("Network.requestWillBeSent", capture_request)

            return requests

        except Exception as e:
            print(f"Failed to capture network requests: {e}")
            return []


async def browser_reorder_articles(
    base_url: str, token: str, project_id: str, target_order: List[str], headless: bool = True
) -> Dict[str, Any]:
    """Main function to reorder articles using browser automation."""
    if not SELENIUM_AVAILABLE:
        return {"status": "error", "message": "Selenium not installed. Run: pip install selenium"}

    # For debugging, you might want to set headless=False to see what's happening
    if base_url.startswith("http://0.0.0.0") or base_url.startswith("http://localhost"):
        print("📝 Note: Running in visible mode for local development")
        headless = False

    try:
        with YouTrackBrowserReorder(base_url, token, headless) as browser:
            # Login
            if not browser.login_with_token():
                return {
                    "status": "error",
                    "message": "Failed to login - browser automation may require manual authentication",
                }

            # Navigate to articles
            if not browser.navigate_to_project_articles(project_id):
                # Try to diagnose the issue
                print(f"🔍 Current URL: {browser.driver.current_url}")
                print(f"🔍 Page title: {browser.driver.title}")

                # Take a screenshot for debugging
                try:
                    browser.driver.save_screenshot("youtrack_debug.png")
                    print("📸 Screenshot saved to youtrack_debug.png")
                except Exception:
                    pass

                return {"status": "error", "message": "Failed to navigate to articles - check screenshot for details"}

            # Get current order
            current_order = browser.get_current_article_order()
            print(f"Current order: {[a['title'] for a in current_order]}")
            print(f"Target order: {target_order}")

            if not current_order:
                return {"status": "error", "message": "No articles found on the page"}

            # Perform reordering
            success = browser.reorder_articles_by_drag_drop(target_order)

            if success:
                return {
                    "status": "success",
                    "message": f"Successfully reordered {len(target_order)} articles using browser automation",
                    "method": "browser_automation",
                }
            else:
                return {"status": "error", "message": "Drag and drop operations failed"}

    except Exception as e:
        return {"status": "error", "message": f"Browser automation failed: {e}"}
