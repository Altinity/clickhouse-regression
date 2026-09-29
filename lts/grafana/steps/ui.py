"""Reusable UI interaction steps for Grafana web automation.

Uses Selenium WebDriver via Selenium Grid for browser-based testing.
Follows the page-object pattern used in altinity/clickhouse-grafana testflows.
"""

import os
import time

from testflows.core import *

from lts.steps.docker import screenshots_dir


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
    """Save a browser screenshot to ``lts/_instances/grafana/screenshots/``,
    where CI collects it as evidence, and record it as a metric."""
    time.sleep(0.3)

    filepath = os.path.join(screenshots_dir("grafana"), f"{name}.png")

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
def verify_logged_in(self, driver, username="admin", timeout=30):
    """Verify that the browser session is logged in as ``username``.

    Waits until the browser has left the login page and the signed-in
    navigation is shown, then asks Grafana which user the session belongs
    to, which does not depend on the home page layout of a Grafana version.
    """
    import json

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait

    WebDriverWait(driver, timeout).until(
        lambda d: "/login" not in d.current_url
        and d.find_elements(
            By.CSS_SELECTOR, "[data-testid^='data-testid navigation mega-menu']"
        )
    )

    response = driver.execute_async_script(
        """
        var callback = arguments[arguments.length - 1];
        fetch('/api/user').then(function(r) { return r.text(); })
            .then(function(t) { callback(t); })
            .catch(function(e) { callback(JSON.stringify({error: e.message})); });
        """
    )
    user = json.loads(response)
    assert (
        user.get("login") == username
    ), f"session is not logged in as {username}: {response[:500]}"
    note(f"logged in as {user['login']}, current URL: {driver.current_url}")


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
        EC.element_to_be_clickable((By.XPATH, f"//a[contains(., '{datasource_name}')]"))
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
                "a[href*='/explore'][data-testid*='explore'], " "a[href*='/explore']",
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
    date_time_col=None,
    date_time_type=None,
):
    """Navigate directly to Grafana Explore with a pre-configured query.

    Bypasses Angular plugin UI interaction by encoding the query and format
    into the Explore URL, which Grafana reads on page load.

    When date_time_col and date_time_type are provided, they configure the
    timestamp column for macro expansion ($timeFilter, $timeSeries, etc).
    """
    import json
    import urllib.parse

    query_obj = {
        "refId": "A",
        "query": query,
        "rawQuery": True,
        "format": format,
        "datasource": {
            "type": "vertamedia-clickhouse-datasource",
            "uid": datasource_uid,
        },
    }
    if date_time_col:
        query_obj["dateTimeCol"] = date_time_col
    if date_time_type:
        query_obj["dateTimeType"] = date_time_type

    left = json.dumps(
        {
            "datasource": datasource_uid,
            "queries": [query_obj],
        }
    )
    url = f"{base_url}/explore?orgId=1&left={urllib.parse.quote(left)}"
    driver.get(url)
    time.sleep(3)
    note(f"Opened Explore with query={query}, format={format}")


def _visible_error(driver):
    """Return the text of a visible Grafana error alert, or ``None``.

    Grafana keeps an empty, hidden error alert in the page, so only an alert
    that is displayed and has text counts.
    """
    from selenium.webdriver.common.by import By

    for alert in driver.find_elements(
        By.CSS_SELECTOR, "[data-testid='data-testid Alert error']"
    ):
        if alert.is_displayed() and alert.text.strip():
            return alert.text.strip()
    return None


@TestStep(When)
def click_run_query(self, driver, timeout=60):
    """Click Run query in Explore and wait until result cells or an error
    appear. Fails if Grafana shows an error."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    run_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "button[data-testid='data-testid RefreshPicker run button']",
            )
        )
    )
    run_btn.click()
    note("Clicked Run query button")

    WebDriverWait(driver, timeout).until(
        lambda d: d.find_elements(By.CSS_SELECTOR, "[role='gridcell']")
        or _visible_error(d)
    )
    error = _visible_error(driver)
    if error:
        take_screenshot(driver=driver, name="query_error")
        fail(f"Grafana showed an error for the query: {error}")
    note("Query result cells rendered")


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


@TestStep(Then)
def get_result_table(self, driver):
    """Return the Explore result table as ``(headers, cells)`` lists of text.

    Reads only the table's column headers and cells, never the page text,
    so that the query text or other page content cannot satisfy a check.
    """
    from selenium.webdriver.common.by import By

    headers = [
        e.text.strip()
        for e in driver.find_elements(By.CSS_SELECTOR, "[role='columnheader']")
    ]
    cells = [
        e.text.strip()
        for e in driver.find_elements(By.CSS_SELECTOR, "[role='gridcell']")
    ]
    note(f"Result table: headers={headers} cells={cells[:20]}")
    if not cells:
        take_screenshot(driver=driver, name="query_result_missing")
        fail("the Explore result table has no cells")
    return headers, cells


@TestStep(Then)
def verify_panel_rendered(self, driver, title, series, timeout=30):
    """Verify that the dashboard panel titled ``title`` drew ``series``.

    Everything is checked inside that panel: no error status, a drawn
    time-series canvas, and a legend entry for ``series``.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait

    header = WebDriverWait(driver, timeout).until(
        lambda d: d.find_element(
            By.CSS_SELECTOR, f"[data-testid='data-testid Panel header {title}']"
        )
    )
    panel = driver.execute_script(
        "return arguments[0].closest('[data-viz-panel-key]') || arguments[0].parentElement.parentElement",
        header,
    )

    def state(_):
        if panel.find_elements(
            By.CSS_SELECTOR, "[data-testid='data-testid Panel status error']"
        ):
            return "error"
        if panel.find_elements(
            By.CSS_SELECTOR, "[data-testid='data-testid xy-canvas']"
        ):
            return "drawn"
        return None

    result = WebDriverWait(driver, timeout).until(state)
    if result == "error":
        messages = [
            e.text
            for e in panel.find_elements(
                By.CSS_SELECTOR, "[data-testid='data-testid Panel data error message']"
            )
        ]
        fail(f"panel '{title}' shows an error: {messages or panel.text}")

    legend = [
        e.text.strip()
        for e in panel.find_elements(
            By.CSS_SELECTOR, "[data-testid^='data-testid VizLegend series']"
        )
    ]
    assert series in legend, f"panel '{title}' legend {legend} has no series '{series}'"
    note(f"panel '{title}' drew series {legend}")


@TestStep(Then)
def query_datasource(self, driver, target, time_from="now-24h", time_to="now"):
    """Run a panel query ``target`` through Grafana's ``/api/ds/query``, as a
    dashboard panel does, and return its data frames.

    Each frame is returned as ``{field name: list of values}``. Fails if the
    query returns an error.
    """
    import json

    body = json.dumps({"from": time_from, "to": time_to, "queries": [target]})
    response = driver.execute_async_script(
        """
        var callback = arguments[arguments.length - 1];
        fetch('/api/ds/query', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: arguments[0]
        })
        .then(function(r) { return r.text(); })
        .then(function(t) { callback(t); })
        .catch(function(e) { callback(JSON.stringify({error: e.message})); });
        """,
        body,
    )
    result = json.loads(response).get("results", {}).get(target["refId"])
    if not result or result.get("error") or result.get("status", 200) != 200:
        fail(f"/api/ds/query failed: {response[:2000]}")

    frames = []
    for frame in result.get("frames", []):
        names = [field["name"] for field in frame["schema"]["fields"]]
        frames.append(dict(zip(names, frame["data"]["values"])))
    note(
        f"/api/ds/query returned {[{k: len(v) for k, v in f.items()} for f in frames]}"
    )
    return frames


def timeseries_target(query, refid="A", datasource_uid="clickhouse-direct"):
    """Return a time-series query model for the clickhouse-grafana plugin on
    ``default.test_grafana``.

    The plugin takes the timestamp column for its time macros from
    ``dateTimeColDataType``; with it empty, ``$timeFilterMs`` and friends
    expand to an empty column name.
    """
    return {
        "refId": refid,
        "query": query,
        "rawQuery": True,
        "format": "time_series",
        "database": "default",
        "table": "test_grafana",
        "dateTimeColDataType": "event_time",
        "dateTimeType": "DATETIME",
        "round": "0s",
        "intervalFactor": 1,
        "intervalMs": 60000,
        "maxDataPoints": 1000,
        "datasource": {
            "type": "vertamedia-clickhouse-datasource",
            "uid": datasource_uid,
        },
    }


@TestStep(When)
def create_dashboard_with_timeseries_panel(self, driver, title, target):
    """Create a dashboard with one time-series panel titled ``title`` that runs
    the query model ``target``, through the Grafana API. Returns the UID."""
    import json

    dashboard_payload = json.dumps(
        {
            "dashboard": {
                "title": title,
                "panels": [
                    {
                        "id": 1,
                        "type": "timeseries",
                        "title": title,
                        "gridPos": {"h": 12, "w": 24, "x": 0, "y": 0},
                        "datasource": target["datasource"],
                        "targets": [target],
                    }
                ],
                "time": {"from": "now-24h", "to": "now"},
                "timezone": "browser",
            },
            "overwrite": True,
        }
    )

    result = driver.execute_async_script(
        """
        var callback = arguments[arguments.length - 1];
        fetch('/api/dashboards/db', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: arguments[0]
        })
        .then(function(r) { return r.json(); })
        .then(function(j) { callback(JSON.stringify(j)); })
        .catch(function(e) { callback('error: ' + e.message); });
        """,
        dashboard_payload,
    )
    note(f"Dashboard creation response: {result}")

    resp = json.loads(result)
    uid = resp.get("uid", "")
    assert uid, f"Failed to create dashboard: {result}"
    note(f"Created dashboard with UID: {uid}")
    return uid


@TestStep(When)
def navigate_to_dashboard(self, driver, uid, base_url="http://grafana:3000"):
    """Open a Grafana dashboard by UID and wait for panels to load."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver.get(f"{base_url}/d/{uid}?orgId=1&from=now-24h&to=now")
    time.sleep(5)

    WebDriverWait(driver, 30).until(
        EC.any_of(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-testid='data-testid panel content']")
            ),
            EC.presence_of_element_located((By.CSS_SELECTOR, ".panel-container")),
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-panelid]")),
        )
    )
    note(f"Dashboard loaded: {driver.current_url}")
