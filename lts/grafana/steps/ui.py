"""Reusable UI interaction steps for Grafana web automation.

Uses Selenium WebDriver via Selenium Grid for browser-based testing.
Follows the page-object pattern used in altinity/clickhouse-grafana testflows.
"""

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
