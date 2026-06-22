"""Browser-driven UI smoke test for Superset + ClickHouse.

Proves end-to-end that the chosen ClickHouse build works with Superset:

1. Environment is up (handled by parent feature).
2. A pre-created ``lts.events`` ClickHouse dataset exists.
3. The ``clickhouse`` Database connection is registered in Superset.
4. We log into Superset via the browser.
5. We navigate to Databases and visually confirm the connection.
6. We navigate to SQL Lab and run a real query against ``lts.events``.
7. We assert the result is non-empty.

A screenshot is saved at every step to ``lts/superset/screenshots/`` so the
artifact can be retrieved from CI.
"""

from testflows.core import *

from lts.superset.requirements.requirements import (
    RQ_SRS_101_Superset_DatabaseConnection,
    RQ_SRS_101_Superset_DatabaseConnection_HTTP,
    RQ_SRS_101_Superset_SQLLab_QueryExecution,
    RQ_SRS_101_Superset_Compatibility_LTS,
)
from lts.superset.steps.ui import (
    create_webdriver,
    take_screenshot,
    open_superset,
    login,
    verify_logged_in,
    seed_clickhouse_database_and_dataset,
    navigate_to_databases,
    verify_clickhouse_database_listed,
    navigate_to_sql_lab,
    run_sql_in_editor,
    get_sql_lab_result_text,
)


@TestScenario
@Requirements(
    RQ_SRS_101_Superset_DatabaseConnection("1.0"),
    RQ_SRS_101_Superset_DatabaseConnection_HTTP("1.0"),
    RQ_SRS_101_Superset_SQLLab_QueryExecution("1.0"),
    RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
)
def ui_clickhouse_smoke(self):
    """End-to-end UI proof that the LTS ClickHouse build works with Superset."""

    with Given(
        "the ClickHouse 'lts.events' table is pre-created and registered "
        "with Superset as a database + dataset"
    ):
        seed_clickhouse_database_and_dataset(
            database_name="clickhouse", schema="lts", table_name="events"
        )

    with And("a WebDriver session against Selenium Grid"):
        driver = create_webdriver()

    with When("I open the Superset login page"):
        open_superset(driver=driver)
        take_screenshot(driver=driver, name="01_login_page")

    with And("I log in as admin"):
        login(driver=driver, username="admin", password="admin")

    with Then("I land on the Superset welcome page"):
        verify_logged_in(driver=driver)
        take_screenshot(driver=driver, name="02_welcome")

    with When("I open the Databases admin page"):
        navigate_to_databases(driver=driver)
        take_screenshot(driver=driver, name="03_databases_list")

    with Then("the 'clickhouse' connection is visible in the Databases list"):
        verify_clickhouse_database_listed(driver=driver, database_name="clickhouse")
        take_screenshot(driver=driver, name="04_clickhouse_connection_visible")

    with When("I open SQL Lab"):
        navigate_to_sql_lab(driver=driver)
        take_screenshot(driver=driver, name="05_sql_lab_open")

    query = (
        "SELECT country, count() AS events, round(avg(amount), 2) AS avg_amount "
        "FROM lts.events GROUP BY country ORDER BY events DESC"
    )
    with And("I run a basic query against the pre-created lts.events dataset"):
        run_sql_in_editor(driver=driver, query=query)
        take_screenshot(driver=driver, name="06_sql_lab_results")

    with Then(
        "the SQL Lab result panel contains rows that include the seeded "
        "country values"
    ):
        result_text = get_sql_lab_result_text(driver=driver)
        assert result_text and result_text.strip(), "SQL Lab result panel was empty"
        countries_seen = [c for c in ("US", "DE", "FR", "UK", "JP") if c in result_text]
        assert countries_seen, (
            "Expected at least one of the seeded countries (US/DE/FR/UK/JP) "
            f"in the result panel, got:\n{result_text[:1000]}"
        )
        note(f"UI smoke test saw seeded countries: {countries_seen}")
        take_screenshot(driver=driver, name="07_sql_lab_result_verified")


@TestFeature
@Name("ui smoke")
def feature(self):
    """Browser-driven smoke test for the Superset + ClickHouse integration."""
    Scenario(run=ui_clickhouse_smoke)
