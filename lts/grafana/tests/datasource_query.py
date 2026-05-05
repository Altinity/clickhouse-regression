"""Test scenarios for querying ClickHouse through the Grafana datasource plugin."""
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
    click_explore_datasource,
    switch_to_sql_editor,
    run_query_via_api,
)


def expected_version_from_image(clickhouse_image):
    """Extract the expected ClickHouse version from the Docker image tag."""
    tag = clickhouse_image.rsplit(":", 1)[-1] if ":" in clickhouse_image else ""
    if tag.startswith("0-"):
        tag = tag[2:]
    return tag


@TestScenario
@Requirements(
    RQ_SRS_102_Grafana_DatasourceQuery("1.0"),
    RQ_SRS_102_Grafana_Compatibility_LTS("1.0"),
)
def select_version_via_explore(self):
    """Navigate to a ClickHouse datasource in Grafana, run SELECT version()
    via the SQL Editor in Explore, and verify the result matches the
    expected ClickHouse server version."""

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

    with And("I click Explore to open the query editor"):
        click_explore_datasource(driver=driver)

    with And("I switch to the SQL Editor"):
        switch_to_sql_editor(driver=driver)

    with And("I take a screenshot of the SQL Editor"):
        take_screenshot(driver=driver, name="sql_editor")

    with And("I query ClickHouse for version via Grafana API"):
        result_text = run_query_via_api(
            driver=driver, query="SELECT version()"
        )

    with Then("the result should contain the ClickHouse version"):
        assert re.search(
            r"\d+\.\d+\.\d+", result_text
        ), f"No version pattern found in result: {result_text}"

        if expected_version:
            assert expected_version in result_text, (
                f"Expected version '{expected_version}' not found in result: {result_text}"
            )
            note(f"Version matches: {expected_version}")
        else:
            note(f"Version returned: {result_text}")


@TestFeature
@Name("datasource query")
def feature(self):
    """Test querying ClickHouse through the Grafana datasource plugin."""
    Scenario(run=select_version_via_explore)
