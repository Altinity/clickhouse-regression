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
    get_result_table,
)


@TestScenario
@Requirements(
    RQ_SRS_102_Grafana_DatasourceQuery("1.0"),
    RQ_SRS_102_Grafana_Compatibility_LTS("1.0"),
)
def select_version_via_explore(self):
    """Open Grafana Explore with SELECT version(), run it via the UI,
    and verify the result matches the expected ClickHouse version."""

    # From --clickhouse-version or the image tag; None for a moving tag such
    # as latest, which says nothing about the version.
    expected_version = self.context.clickhouse_version

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

    with Then("the result is one cell holding the ClickHouse version"):
        headers, cells = get_result_table(driver=driver)
        assert len(cells) == 1, f"expected one result cell, got {cells}"
        version = cells[0]
        assert re.fullmatch(
            r"\d+\.\d+\.\d+(\.\d+)?(\.\w+)?", version
        ), f"result cell is not a ClickHouse version: {version!r}"
        if expected_version:
            assert version.startswith(
                expected_version
            ), f"server version {version!r} does not match {expected_version!r}"
        else:
            note(f"no expected version for this image, server reports {version}")


@TestFeature
@Name("datasource query")
def feature(self):
    """Test querying ClickHouse through the Grafana datasource plugin."""
    Scenario(run=select_version_via_explore)
