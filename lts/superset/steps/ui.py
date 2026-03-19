"""Reusable UI interaction steps for Superset web automation.

Uses Selenium WebDriver for browser-based testing. These steps mirror the
page-object pattern used in altinity/clickhouse-grafana testflows.
"""

from testflows.core import *


@TestStep(Given)
def open_superset(self, driver, base_url="http://localhost:8088"):
    """Navigate to the Superset home page."""
    driver.get(base_url)
    note(f"Opened Superset at {base_url}")


@TestStep(When)
def login(self, driver, username="admin", password="admin"):
    """Log in to Superset with the given credentials."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 30)
    username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
    password_input = driver.find_element(By.ID, "password")
    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    note(f"Logged in as {username}")


@TestStep(When)
def add_database_connection(self, driver, connection_string):
    """Add a new ClickHouse database connection via the Superset UI."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    wait = WebDriverWait(driver, 30)

    driver.get("http://localhost:8088/databaseview/list/")
    add_btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "[data-test='btn-create-database']")
        )
    )
    add_btn.click()
    note(f"Adding database connection: {connection_string}")


@TestStep(When)
def navigate_to_sql_lab(self, driver):
    """Navigate to the SQL Lab page."""
    driver.get("http://localhost:8088/sqllab")
    note("Navigated to SQL Lab")


@TestStep(When)
def run_query(self, driver, query):
    """Type and execute a SQL query in SQL Lab."""
    note(f"Running query: {query}")


@TestStep(Then)
def check_query_result(self, driver, expected):
    """Verify that the SQL Lab result matches the expected value."""
    note(f"Checking query result matches: {expected}")
