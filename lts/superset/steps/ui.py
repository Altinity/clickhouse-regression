"""Reusable UI/API interaction steps for Apache Superset.

Browser-based steps use Selenium WebDriver via the Selenium Grid container.
A small set of REST helpers is kept solely for fixture-style setup
(creating the ClickHouse database connection and the dataset that the UI
smoke test relies on); the actual verification is done through the UI.
"""

import json
import os
import time
import urllib.request
import urllib.error

from testflows.core import *


# ---------------------------------------------------------------------------
# WebDriver
# ---------------------------------------------------------------------------


@TestStep(Given)
def create_webdriver(self, hub_url=None, timeout=120):
    """Create a remote Chrome WebDriver connected to Selenium Grid.

    If ``hub_url`` is omitted, uses ``self.context.selenium_url`` discovered
    during environment setup. Yields the driver and quits it on cleanup.
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
        try:
            driver.quit()
        except Exception:
            pass


@TestStep(When)
def take_screenshot(self, driver, name="screenshot"):
    """Save a browser screenshot under ``lts/superset/screenshots/``."""
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


# ---------------------------------------------------------------------------
# UI: navigation / login
# ---------------------------------------------------------------------------


def _internal_url(self):
    """Return the URL the browser uses to reach Superset (over the Docker network)."""
    return getattr(
        self.context, "superset_internal_url", "http://superset:8088"
    )


@TestStep(Given)
def open_superset(self, driver, base_url=None):
    """Navigate to the Superset login page."""
    if base_url is None:
        base_url = _internal_url(self)
    driver.get(f"{base_url}/login/")
    note(f"Opened Superset login at {base_url}/login/")


@TestStep(When)
def login(self, driver, username="admin", password="admin"):
    """Log in to Superset with the given credentials."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 30)
    username_input = wait.until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    password_input = driver.find_element(By.ID, "password")
    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    note(f"Logged in as {username}")


@TestStep(Then)
def verify_logged_in(self, driver):
    """Verify that the home/welcome page rendered after login."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 30)
    wait.until(
        EC.any_of(
            EC.url_contains("/superset/welcome"),
            EC.url_matches(r".*/(dashboard|chart|sqllab|welcome).*"),
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-test='welcome-page']")
            ),
            EC.presence_of_element_located((By.CSS_SELECTOR, "nav.navbar")),
        )
    )
    assert "/login" not in driver.current_url, (
        f"Still on login page: {driver.current_url}"
    )
    note(f"Successfully verified login - current URL: {driver.current_url}")


# ---------------------------------------------------------------------------
# REST helpers (used only for fixture-style seeding before UI verification)
# ---------------------------------------------------------------------------


def _superset_host_url(self):
    """Return the URL host-side requests should target."""
    return getattr(self.context, "superset_url", "http://127.0.0.1:8088")


def _http(method, url, headers=None, data=None, timeout=30):
    """Minimal urllib wrapper that returns ``(status, body_text)``."""
    payload = None
    if data is not None:
        if isinstance(data, (dict, list)):
            payload = json.dumps(data).encode("utf-8")
            headers = {**(headers or {}), "Content-Type": "application/json"}
        else:
            payload = data
    req = urllib.request.Request(
        url, data=payload, headers=headers or {}, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def _auth_headers(tokens):
    """Build the standard auth headers for Superset REST calls."""
    return {
        "Authorization": f"Bearer {tokens['access_token']}",
        "X-CSRFToken": tokens["csrf_token"],
        "Referer": "http://localhost:8088/",
    }


def _sqlalchemy_uri(driver, scheme):
    """Compose a Superset-compatible SQLAlchemy URI for ClickHouse.

    The Superset container reaches ClickHouse at ``clickhouse:8123`` (HTTP)
    or ``clickhouse:8443`` (HTTPS) on the shared Docker network.
    """
    if driver == "clickhouse-sqlalchemy":
        if scheme == "https":
            return "clickhouse+https://default:@clickhouse:8443/default?verify=false"
        return "clickhouse+http://default:@clickhouse:8123/default"

    if scheme == "https":
        return "clickhousedb+connect://default:@clickhouse:8443/default?secure=true&verify=false"
    return "clickhousedb+connect://default:@clickhouse:8123/default"


def _api_login(self, username="admin", password="admin"):
    """Acquire and cache Superset access + CSRF tokens (fixture-internal)."""
    tokens = getattr(self.context, "superset_api_tokens", None)
    if tokens:
        return tokens

    base = _superset_host_url(self)

    status, body = _http(
        "POST",
        f"{base}/api/v1/security/login",
        data={
            "username": username,
            "password": password,
            "provider": "db",
            "refresh": True,
        },
    )
    if status != 200:
        fail(f"Superset API login failed: HTTP {status}: {body}")

    access_token = json.loads(body).get("access_token")
    if not access_token:
        fail(f"Login response missing access_token: {body}")

    status, body = _http(
        "GET",
        f"{base}/api/v1/security/csrf_token/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if status != 200:
        fail(f"Could not obtain CSRF token: HTTP {status}: {body}")

    csrf_token = json.loads(body).get("result")
    tokens = {"access_token": access_token, "csrf_token": csrf_token}
    self.context.superset_api_tokens = tokens
    return tokens


def _ensure_database(self, name, scheme="http"):
    """Idempotently ensure a Superset Database row exists; return its id."""
    base = _superset_host_url(self)
    tokens = self.context.superset_api_tokens
    driver_name = self.context.clickhouse_driver

    list_url = (
        f"{base}/api/v1/database/?q="
        + urllib.request.quote(
            json.dumps(
                {
                    "filters": [
                        {"col": "database_name", "opr": "eq", "value": name}
                    ]
                }
            )
        )
    )
    status, body = _http("GET", list_url, headers=_auth_headers(tokens))
    if status == 200:
        existing = json.loads(body).get("result", [])
        if existing:
            return existing[0]["id"]

    payload = {
        "database_name": name,
        "sqlalchemy_uri": _sqlalchemy_uri(driver_name, scheme),
        "expose_in_sqllab": True,
        "allow_dml": False,
        "allow_ctas": False,
        "allow_cvas": False,
    }
    status, body = _http(
        "POST",
        f"{base}/api/v1/database/",
        headers=_auth_headers(tokens),
        data=payload,
    )
    if status not in (200, 201):
        fail(f"Failed to create database '{name}': HTTP {status}: {body}")
    return json.loads(body)["id"]


def _ensure_dataset(self, database_id, schema, table_name):
    """Idempotently ensure a Superset Dataset exists; return its id."""
    base = _superset_host_url(self)
    tokens = self.context.superset_api_tokens

    q = urllib.request.quote(
        json.dumps(
            {
                "filters": [
                    {"col": "table_name", "opr": "eq", "value": table_name},
                    {"col": "schema", "opr": "eq", "value": schema},
                ]
            }
        )
    )
    status, body = _http(
        "GET",
        f"{base}/api/v1/dataset/?q={q}",
        headers=_auth_headers(tokens),
    )
    if status == 200:
        existing = json.loads(body).get("result", [])
        if existing:
            return existing[0]["id"]

    payload = {
        "database": database_id,
        "schema": schema,
        "table_name": table_name,
    }
    status, body = _http(
        "POST",
        f"{base}/api/v1/dataset/",
        headers=_auth_headers(tokens),
        data=payload,
    )
    if status not in (200, 201):
        fail(
            f"Failed to create dataset {schema}.{table_name}: "
            f"HTTP {status}: {body}"
        )
    return json.loads(body).get("id")


# ---------------------------------------------------------------------------
# Seeding fixture: ensure the UI smoke test has a known DB + dataset
# ---------------------------------------------------------------------------


@TestStep(Given)
def seed_clickhouse_database_and_dataset(
    self,
    database_name="clickhouse",
    schema="lts",
    table_name="events",
):
    """Ensure a Superset Database row + Dataset exist for the UI smoke test.

    Idempotent: if the DB or dataset is already registered, this is a no-op.
    Stores the IDs on the context for downstream UI steps.
    """
    _api_login(self)
    db_id = _ensure_database(self, database_name, scheme="http")
    dataset_id = _ensure_dataset(self, db_id, schema, table_name)

    self.context.smoke_database_name = database_name
    self.context.smoke_database_id = db_id
    self.context.smoke_schema = schema
    self.context.smoke_table = table_name
    self.context.smoke_dataset_id = dataset_id
    note(
        f"Seeded Superset: db='{database_name}' (id={db_id}), "
        f"dataset='{schema}.{table_name}' (id={dataset_id})"
    )


# ---------------------------------------------------------------------------
# UI navigation for the smoke test
# ---------------------------------------------------------------------------


@TestStep(When)
def navigate_to_databases(self, driver, base_url=None):
    """Open the Databases admin page (`/databaseview/list/`)."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    if base_url is None:
        base_url = _internal_url(self)
    driver.get(f"{base_url}/databaseview/list/")
    wait = WebDriverWait(driver, 30)
    wait.until(
        EC.any_of(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(),'Database')]")
            ),
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-test='databases-list-table']")
            ),
        )
    )
    note("Navigated to the Databases page")


@TestStep(Then)
def verify_clickhouse_database_listed(self, driver, database_name="clickhouse"):
    """Assert the named ClickHouse connection appears in the Databases list."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 30)
    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, f"//td//*[contains(text(), '{database_name}')]")
        )
    )
    note(f"ClickHouse database '{database_name}' is listed in Superset")


@TestStep(When)
def navigate_to_sql_lab(self, driver, base_url=None):
    """Open SQL Lab (`/sqllab/`) and wait for the editor to render."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    if base_url is None:
        base_url = _internal_url(self)
    driver.get(f"{base_url}/sqllab/")
    wait = WebDriverWait(driver, 30)
    wait.until(
        EC.any_of(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".ace_editor")
            ),
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-test='sql-editor']")
            ),
        )
    )
    note("Navigated to SQL Lab")


@TestStep(When)
def run_sql_in_editor(self, driver, query):
    """Type a query into the SQL Lab editor and click Run.

    Uses the ACE editor's textarea + Ctrl+Enter to trigger execution, with a
    Run-button click as a fallback. Waits for the results panel to render
    before returning.
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 30)
    editor = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".ace_editor textarea")
        )
    )
    editor.click()
    time.sleep(0.3)

    actions = ActionChains(driver)
    actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL)
    actions.send_keys(Keys.DELETE)
    actions.send_keys(query)
    actions.perform()
    time.sleep(0.5)
    note(f"Typed query into editor: {query}")

    triggered_via_button = False
    try:
        run_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "[data-test='run-query-action'], "
                    "button[aria-label='Run query'], "
                    "button[aria-label='Run']",
                )
            )
        )
        run_btn.click()
        triggered_via_button = True
        note("Clicked Run via button")
    except Exception:
        pass

    if not triggered_via_button:
        ActionChains(driver).key_down(Keys.CONTROL).send_keys(
            Keys.ENTER
        ).key_up(Keys.CONTROL).perform()
        note("Triggered Run via Ctrl+Enter")

    WebDriverWait(driver, 60).until(
        EC.any_of(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-test='table-container'] table")
            ),
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".filterable-table-container table")
            ),
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(@class,'ant-table')]//table")
            ),
        )
    )
    note("Result table rendered")


@TestStep(Then)
def get_sql_lab_result_text(self, driver):
    """Return the visible text of the SQL Lab result panel for assertions."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 30)
    selectors = [
        "[data-test='table-container']",
        ".filterable-table-container",
        ".ant-table-wrapper",
    ]
    for sel in selectors:
        try:
            el = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, sel))
            )
            text = el.text
            if text and text.strip():
                note(
                    f"SQL Lab result text (via {sel}): "
                    f"{text[:300]}{'...' if len(text) > 300 else ''}"
                )
                return text
        except Exception:
            continue

    body = driver.find_element(By.TAG_NAME, "body").text
    note(f"Falling back to body text (truncated): {body[:500]}")
    return body
