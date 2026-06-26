"""Test scenarios for querying ClickHouse through the Grafana datasource plugin.

Uses a full browser-based UI flow: open Explore with a query, click Run,
verify results appear on screen, and take screenshots at every step.
"""

import re

from testflows.core import *

from lts.grafana.requirements.requirements import (
    RQ_SRS_102_Grafana_DatasourceQuery,
    RQ_SRS_102_Grafana_Compatibility_LTS,
)
from lts.grafana.steps.ui import (
    create_webdriver,
    open_grafana,
    login,
    skip_password_change,
    take_screenshot,
    navigate_to_datasources,
    select_datasource,
    open_explore_with_query,
    click_run_query,
    get_query_result_text,
)


def expected_version_from_image(clickhouse_image):
    """Extract the expected ClickHouse version from the Docker image tag.

    Strips the '0-' prefix and any non-numeric suffix like '.altinitytest'.
    """
    tag = clickhouse_image.rsplit(":", 1)[-1] if ":" in clickhouse_image else ""
    if tag.startswith("0-"):
        tag = tag[2:]
    match = re.match(r"(\d+\.\d+\.\d+\.\d+)", tag)
    if match:
        return match.group(1)
    match = re.match(r"(\d+\.\d+\.\d+)", tag)
    if match:
        return match.group(1)
    return tag


@TestScenario
@Requirements(
    RQ_SRS_102_Grafana_DatasourceQuery("1.0"),
    RQ_SRS_102_Grafana_Compatibility_LTS("1.0"),
)
def select_version_via_explore(self):
    """Open Grafana Explore with SELECT version(), run it via the UI,
    and verify the result matches the expected ClickHouse version."""

    clickhouse_image = self.context.clickhouse_image
    expected_version = expected_version_from_image(clickhouse_image)

    with Given("a WebDriver connected to Selenium Grid"):
        driver = create_webdriver()

    with And("I am logged into Grafana"):
        open_grafana(driver=driver)
        login(driver=driver, username="admin", password="admin")
        skip_password_change(driver=driver)

    with When("I navigate to Connections -> Data sources"):
        navigate_to_datasources(driver=driver)

    with And("I select the clickhouse-direct datasource"):
        select_datasource(driver=driver, datasource_name="clickhouse-direct")

    with And("I take a screenshot of the datasource settings"):
        take_screenshot(driver=driver, name="datasource_settings")

    with When("I open Explore with a SELECT version() query"):
        open_explore_with_query(driver=driver, query="SELECT version()")

    with And("I take a screenshot of the Explore page with the query"):
        take_screenshot(driver=driver, name="explore_query_ready")

    with And("I click Run query"):
        click_run_query(driver=driver)

    with And("I take a screenshot of the query results"):
        take_screenshot(driver=driver, name="explore_query_results")

    with Then("the result should contain the ClickHouse version"):
        result_text = get_query_result_text(driver=driver)
        assert re.search(
            r"\d+\.\d+\.\d+", result_text
        ), f"No version pattern found in result: {result_text}"

        if expected_version:
            assert (
                expected_version in result_text
            ), f"Expected version '{expected_version}' not found in result: {result_text}"
            note(f"Version matches: {expected_version}")
        else:
            note(f"Version returned: {result_text}")


@TestFeature
@Name("datasource query")
def feature(self):
    """Test querying ClickHouse through the Grafana datasource plugin."""
    Scenario(run=select_version_via_explore)
