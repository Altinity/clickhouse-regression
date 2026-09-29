"""Superset + ClickHouse tests: driver, connections and a browser-driven
SQL Lab query.

1. Superset loaded the selected ClickHouse driver.
2. Superset's test-connection API reports HTTP, HTTPS and, with
   clickhouse-sqlalchemy, native connections as working.
3. In the browser: log in, find the ``clickhouse`` connection in the
   Databases list, run a query in SQL Lab and check the exact result rows.

A screenshot is saved at every browser step to ``lts/_instances/superset/screenshots/``.
"""

from testflows.core import *

from lts.superset.requirements.requirements import (
    RQ_SRS_101_Superset_Environment_ClickHouseConnect,
    RQ_SRS_101_Superset_Environment_ClickHouseSQLAlchemy,
    RQ_SRS_101_Superset_DatabaseConnection,
    RQ_SRS_101_Superset_DatabaseConnection_HTTP,
    RQ_SRS_101_Superset_DatabaseConnection_HTTPS,
    RQ_SRS_101_Superset_DatabaseConnection_NativeProtocol,
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
    get_sql_lab_result_rows,
    test_database_connection,
    available_database_engines,
)

# The Superset engine each --clickhouse-driver choice provides, and the
# requirement that checks it.
DRIVER_ENGINES = {
    "clickhouse-connect": (
        "clickhousedb",
        RQ_SRS_101_Superset_Environment_ClickHouseConnect,
    ),
    "clickhouse-sqlalchemy": (
        "clickhouse",
        RQ_SRS_101_Superset_Environment_ClickHouseSQLAlchemy,
    ),
}

# init_schema.sql inserts 1000 rows with country = number % 5 (US, DE, FR,
# UK, JP) and amount = number * 0.5, so each country has 200 rows and an
# average amount of (k + 497.5) / 2 for its remainder k.
EXPECTED_ROWS = [
    ["DE", "200", "249.25"],
    ["FR", "200", "249.75"],
    ["JP", "200", "250.75"],
    ["UK", "200", "250.25"],
    ["US", "200", "248.75"],
]


@TestScenario
def driver_engine_available(self):
    """Check that Superset lists the engine of the selected driver."""
    engine, _ = DRIVER_ENGINES[self.context.clickhouse_driver]

    with Then(f"Superset lists the {engine} engine with a driver"):
        engines = available_database_engines()
        assert engines.get(
            engine
        ), f"engine {engine} for {self.context.clickhouse_driver} is not available: {engines}"


@TestScenario
@Requirements(
    RQ_SRS_101_Superset_DatabaseConnection("1.0"),
    RQ_SRS_101_Superset_DatabaseConnection_HTTP("1.0"),
    RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
)
def test_connection_http(self):
    """Test the HTTP connection through Superset's test-connection API."""
    with Then("Superset reports the HTTP connection as working"):
        test_database_connection(scheme="http")


@TestScenario
@Requirements(
    RQ_SRS_101_Superset_DatabaseConnection_HTTPS("1.0"),
    RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
)
def test_connection_https(self):
    """Test the HTTPS connection through Superset's test-connection API."""
    with Then("Superset reports the HTTPS connection as working"):
        test_database_connection(scheme="https")


@TestScenario
@Requirements(
    RQ_SRS_101_Superset_DatabaseConnection_NativeProtocol("1.0"),
    RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
)
def test_connection_native(self):
    """Test the native-protocol connection through Superset's test-connection
    API. Only clickhouse-sqlalchemy supports the native protocol."""
    with Then("Superset reports the native connection as working"):
        test_database_connection(scheme="native")


@TestScenario
@Requirements(
    RQ_SRS_101_Superset_DatabaseConnection("1.0"),
    RQ_SRS_101_Superset_SQLLab_QueryExecution("1.0"),
    RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
)
def ui_clickhouse_smoke(self):
    """In the browser, find the ClickHouse connection and run a query in SQL
    Lab, checking the exact result rows."""

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

    with And("I run a query against the pre-created lts.events dataset"):
        run_sql_in_editor(
            driver=driver,
            query=(
                "SELECT country, count() AS events, round(avg(amount), 2) AS avg_amount "
                "FROM lts.events GROUP BY country ORDER BY country"
            ),
        )
        take_screenshot(driver=driver, name="06_sql_lab_results")

    with Then("the result grid holds exactly the expected row per country"):
        rows = get_sql_lab_result_rows(driver=driver, columns=3)
        assert rows == EXPECTED_ROWS, f"expected {EXPECTED_ROWS}, got {rows}"
        take_screenshot(driver=driver, name="07_sql_lab_result_verified")


@TestFeature
@Name("ui smoke")
def feature(self):
    """Superset + ClickHouse driver, connection and SQL Lab tests."""
    _, driver_requirement = DRIVER_ENGINES[self.context.clickhouse_driver]
    Scenario(
        run=driver_engine_available,
        requirements=[
            driver_requirement("1.0"),
            RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
        ],
    )
    Scenario(run=test_connection_http)
    Scenario(run=test_connection_https)
    # Not run, rather than skipped, for clickhouse-connect: a skipped test
    # marks its requirements unsatisfied, while this one is just not tested.
    if self.context.clickhouse_driver == "clickhouse-sqlalchemy":
        Scenario(run=test_connection_native)
    else:
        note(
            "clickhouse-connect has no native protocol support; native connection not tested"
        )
    Scenario(run=ui_clickhouse_smoke)
