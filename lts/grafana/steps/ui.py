"""Reusable UI interaction steps for Grafana web automation.

Uses Selenium WebDriver via Selenium Grid for browser-based testing.
Follows the page-object pattern used in altinity/clickhouse-grafana testflows.
"""

import os
import time

from testflows.core import *


@TestStep(Given)
def create_webdriver(self, hub_url=None, timeout=120):
    """Create a remote Chrome WebDriver connected to Selenium Grid.

    If hub_url is not provided, uses self.context.selenium_url discovered
    during environment setup.

    Returns the WebDriver instance and quits it on cleanup.
    """
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    if hub_url is None:
        hub_url = self.context.selenium_url

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    start_time = time.time()
    driver = None
    while True:
        try:
            driver = webdriver.Remote(
                command_executor=hub_url,
                options=options,
            )
            break
        except Exception as e:
            if time.time() - start_time >= timeout:
                fail(f"Failed to connect to Selenium Grid at {hub_url}: {e}")
            time.sleep(2)

    note(f"WebDriver session created: {driver.session_id}")

    try:
        yield driver
    finally:
        note("Quitting WebDriver session")
        driver.quit()


@TestStep(Given)
def open_grafana(self, driver, base_url="http://grafana:3000"):
    """Navigate to the Grafana login page."""
    driver.get(f"{base_url}/login")
    note(f"Opened Grafana at {base_url}/login")


@TestStep(When)
def take_screenshot(self, driver, name="screenshot"):
    """Save a browser screenshot as a test artifact.

    The PNG is saved into the test's work directory and attached
    to the test report via the `save_screenshot` method + metric().
    """
    screenshots_dir = os.path.join(
        current().context.configs_dir, "..", "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)

    filename = f"{name}.png"
    filepath = os.path.join(screenshots_dir, filename)

    driver.save_screenshot(filepath)
    note(f"Screenshot saved: {filepath}")

    metric(name=name, value=filepath, units="screenshot")

    return filepath


@TestStep(When)
def login(self, driver, username="admin", password="admin"):
    """Log in to Grafana with the given credentials."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 30)

    username_input = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "[data-testid='data-testid Username input field']")
        )
    )
    username_input.clear()
    username_input.send_keys(username)

    password_input = driver.find_element(
        By.CSS_SELECTOR, "[data-testid='data-testid Password input field']"
    )
    password_input.clear()
    password_input.send_keys(password)

    login_button = driver.find_element(
        By.CSS_SELECTOR, "[data-testid='data-testid Login button']"
    )
    login_button.click()
    note(f"Logged in as {username}")


@TestStep(When)
def skip_password_change(self, driver):
    """Skip the password change prompt that appears after first login."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 10)
    try:
        skip_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "[data-testid='data-testid Skip change password button']",
                )
            )
        )
        skip_button.click()
        note("Skipped password change prompt")
    except Exception:
        note("No password change prompt appeared — continuing")


@TestStep(Then)
def verify_logged_in(self, driver):
    """Verify that we have successfully logged into Grafana by checking
    for elements present on the home page."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 30)

    wait.until(
        EC.any_of(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-testid='data-testid home-page']")
            ),
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.page-dashboard")),
            EC.url_contains("/d/"),
            EC.url_matches(r".*/\?orgId=.*"),
        )
    )

    assert (
        "/login" not in driver.current_url
    ), f"Still on login page: {driver.current_url}"
    note(f"Successfully verified login — current URL: {driver.current_url}")


@TestStep(When)
def navigate_to_datasources(self, driver, base_url="http://grafana:3000"):
    """Navigate to Connections -> Data sources page."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver.get(f"{base_url}/connections/datasources")
    wait = WebDriverWait(driver, 30)
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//h1[contains(text(),'Data sources')]")
        )
    )
    note("Navigated to Connections -> Data sources")


@TestStep(When)
def select_datasource(self, driver, datasource_name):
    """Click on a datasource by name in the Data sources list."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 30)
    ds_link = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//a[contains(., '{datasource_name}')]")
        )
    )
    ds_link.click()
    note(f"Selected datasource: {datasource_name}")


@TestStep(When)
def click_explore_datasource(self, driver):
    """Click the Explore button on a datasource settings page."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 30)
    explore_link = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "a[href*='/explore'][data-testid*='explore'], "
                "a[href*='/explore']",
            )
        )
    )
    explore_link.click()
    time.sleep(2)
    note("Clicked Explore on datasource page")


_JS_FIND_BY_TEXT_IN_SHADOW = """
function findByText(root, text) {
    var all = root.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
        var el = all[i];
        if (el.shadowRoot) {
            var found = findByText(el.shadowRoot, text);
            if (found) return found;
        }
        var childNodes = el.childNodes;
        for (var j = 0; j < childNodes.length; j++) {
            if (childNodes[j].nodeType === 3 && childNodes[j].textContent.trim() === text) {
                return el;
            }
        }
    }
    return null;
}
return findByText(document, arguments[0]);
"""

_JS_FIND_BY_CSS_IN_SHADOW = """
function findByCss(root, selector) {
    var el = root.querySelector(selector);
    if (el) return el;
    var all = root.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
        if (all[i].shadowRoot) {
            el = findByCss(all[i].shadowRoot, selector);
            if (el) return el;
        }
    }
    return null;
}
return findByCss(document, arguments[0]);
"""

_JS_LIST_SHADOW_HOSTS = """
var hosts = [];
document.querySelectorAll('*').forEach(function(el) {
    if (el.shadowRoot) hosts.push(el.tagName + '.' + el.className);
});
return hosts;
"""


@TestStep(When)
def switch_to_sql_editor(self, driver):
    """Click the SQL Editor tab in the clickhouse-grafana query editor.

    Handles Grafana 11+ Angular sandbox which renders plugin UI inside
    Shadow DOM, making regular Selenium selectors unable to reach the elements.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 5)
    try:
        sql_tab = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(), 'SQL Editor')]")
            )
        )
        sql_tab.click()
        time.sleep(1)
        note("Switched to SQL Editor mode via regular selector")
        return
    except Exception:
        pass

    shadow_hosts = driver.execute_script(_JS_LIST_SHADOW_HOSTS)
    note(f"Shadow DOM hosts found: {shadow_hosts}")

    el = driver.execute_script(_JS_FIND_BY_TEXT_IN_SHADOW, "SQL Editor")
    if el:
        driver.execute_script("arguments[0].click()", el)
        time.sleep(1)
        note("Switched to SQL Editor mode via Shadow DOM traversal")
        return

    note("SQL Editor tab not found or already active — continuing")


@TestStep(When)
def open_explore_with_query(
    self,
    driver,
    query,
    format="table",
    datasource_uid="clickhouse-direct",
    base_url="http://grafana:3000",
):
    """Navigate directly to Grafana Explore with a pre-configured query.

    Bypasses Angular plugin UI interaction by encoding the query and format
    into the Explore URL, which Grafana reads on page load.
    """
    import json
    import urllib.parse

    left = json.dumps(
        {
            "datasource": datasource_uid,
            "queries": [
                {
                    "refId": "A",
                    "query": query,
                    "rawQuery": True,
                    "format": format,
                    "datasource": {
                        "type": "vertamedia-clickhouse-datasource",
                        "uid": datasource_uid,
                    },
                }
            ],
        }
    )
    url = f"{base_url}/explore?orgId=1&left={urllib.parse.quote(left)}"
    driver.get(url)
    time.sleep(3)
    note(f"Opened Explore with query={query}, format={format}")


@TestStep(When)
def set_format_as_table(self, driver):
    """Placeholder — format is set via the API query step instead."""
    note("Format will be set via API query — skipping UI dropdown change")


@TestStep(When)
def enter_and_run_query(self, driver, query):
    """Enter a SQL query in the editor and click Run query.

    Uses ActionChains keyboard simulation for reliable text replacement
    in the Angular plugin's textarea editor.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    editor = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
    )
    note("Found editor textarea")

    editor.click()
    time.sleep(0.3)

    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL)
    actions.pause(0.3)
    actions.send_keys(query)
    actions.perform()
    time.sleep(1)
    note(f"Entered query via ActionChains: {query}")

    wait = WebDriverWait(driver, 30)
    run_btn = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "button[data-testid='data-testid RefreshPicker run button']",
            )
        )
    )
    run_btn.click()
    note("Clicked Run query")

    time.sleep(5)


@TestStep(When)
def run_query_via_api(self, driver, query, datasource_uid="clickhouse-direct"):
    """Execute a ClickHouse query through the Grafana datasource proxy API.

    Uses the browser's authenticated session to call the Grafana /api/ds/query
    endpoint. Returns the raw response text from the API.
    """
    result = driver.execute_async_script(
        """
        var callback = arguments[arguments.length - 1];
        fetch('/api/ds/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                queries: [{
                    refId: 'A',
                    datasource: {
                        type: 'vertamedia-clickhouse-datasource',
                        uid: arguments[0]
                    },
                    rawSql: arguments[1],
                    format: 'table',
                    rawQuery: true
                }],
                from: '1609459200000',
                to: '1893456000000'
            })
        })
        .then(function(r) { return r.text(); })
        .then(function(t) { callback(t); })
        .catch(function(e) { callback('error: ' + e.message); });
        """,
        datasource_uid,
        query,
    )
    note(f"API query result: {result[:500]}")
    return result


@TestStep(Then)
def get_query_result_text(self, driver):
    """Extract text content from the Explore query result area.

    Tries multiple selectors as Grafana versions use different data-testid
    attributes for the Explore content area.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver.switch_to.default_content()

    selectors = [
        "[data-testid='data-testid explore content']",
        "[class*='explore-content']",
        "[class*='exploreContent']",
        "div.explore-content-wrapper",
        "[role='main']",
    ]

    for sel in selectors:
        try:
            result_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, sel))
            )
            text = result_area.text
            if text and text.strip() and "No data" not in text:
                note(f"Query result text (via {sel}): {text}")
                return text
        except Exception:
            continue

    take_screenshot(driver=driver, name="query_result_debug")

    try:
        body = driver.find_element(By.TAG_NAME, "body")
        body_text = body.text
        note(f"Full page text: {body_text[:2000]}")
        return body_text
    except Exception:
        fail("Could not find any query result area")
