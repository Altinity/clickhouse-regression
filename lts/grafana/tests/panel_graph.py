"""Test scenarios for ClickHouse data in Grafana Explore and dashboard panels.

Every check reads exact values: result table cells in Explore, and for the
dashboard panel both its rendered state and the data its query returns
through Grafana. Screenshots are captured at each significant step.
"""

from testflows.core import *

from lts.grafana.requirements.requirements import (
    RQ_SRS_102_Grafana_DatasourceQuery,
    RQ_SRS_102_Grafana_PanelVisualization,
    RQ_SRS_102_Grafana_Macros_TimeSeries,
    RQ_SRS_102_Grafana_Compatibility_LTS,
)
from lts.grafana.steps.ui import (
    create_webdriver,
    open_grafana,
    login,
    skip_password_change,
    take_screenshot,
    open_explore_with_query,
    click_run_query,
    get_result_table,
    create_dashboard_with_timeseries_panel,
    navigate_to_dashboard,
    verify_panel_rendered,
    query_datasource,
    timeseries_target,
)

# init_schema.sql seeds 100 rows, one every 10 seconds back from startup.
SEEDED_ROWS = 100


@TestScenario
@Requirements(
    RQ_SRS_102_Grafana_DatasourceQuery("1.0"),
    RQ_SRS_102_Grafana_Compatibility_LTS("1.0"),
)
def explore_count_query(self):
    """Run a count query against the seeded table in Explore and check that
    the result table shows exactly the seeded row count."""

    with Given("a WebDriver connected to Selenium Grid"):
        driver = create_webdriver()

    with And("I am logged into Grafana"):
        open_grafana(driver=driver)
        login(driver=driver, username="admin", password="admin")
        skip_password_change(driver=driver)

    with When("I open Explore with a count query"):
        open_explore_with_query(
            driver=driver,
            query="SELECT count() AS c FROM default.test_grafana",
            format="table",
        )

    with And("I click Run query"):
        click_run_query(driver=driver)

    with And("I take a screenshot of the result"):
        take_screenshot(driver=driver, name="explore_count_result")

    with Then(f"the result table has one column c with the value {SEEDED_ROWS}"):
        headers, cells = get_result_table(driver=driver)
        assert headers == ["c"], f"unexpected columns {headers}"
        assert cells == [str(SEEDED_ROWS)], f"unexpected cells {cells}"


@TestScenario
@Requirements(
    RQ_SRS_102_Grafana_PanelVisualization("1.0"),
    RQ_SRS_102_Grafana_Macros_TimeSeries("1.0"),
    RQ_SRS_102_Grafana_Compatibility_LTS("1.0"),
)
def dashboard_time_series_macros(self):
    """Create a dashboard with a time-series panel whose query uses the
    $timeSeriesMs and $timeFilterMs macros, and check both that the panel
    draws the series without an error and that its query returns the seeded
    rows grouped into time buckets."""

    title = "timeSeriesMs and timeFilterMs"
    target = timeseries_target(
        "SELECT $timeSeriesMs AS t, count() AS cnt "
        "FROM default.test_grafana WHERE $timeFilterMs "
        "GROUP BY t ORDER BY t"
    )

    with Given("a WebDriver connected to Selenium Grid"):
        driver = create_webdriver()

    with And("I am logged into Grafana"):
        open_grafana(driver=driver)
        login(driver=driver, username="admin", password="admin")
        skip_password_change(driver=driver)

    with When("I create a dashboard with a time-series panel using the macros"):
        uid = create_dashboard_with_timeseries_panel(
            driver=driver, title=title, target=target
        )

    with And("I open the dashboard"):
        navigate_to_dashboard(driver=driver, uid=uid)

    with And("I take a screenshot of the dashboard"):
        take_screenshot(driver=driver, name="dashboard_macros_graph")

    with Then("the panel draws the cnt series without an error"):
        verify_panel_rendered(driver=driver, title=title, series="cnt")

    with And("the panel query returns the seeded rows in one-minute buckets"):
        frames = query_datasource(driver=driver, target=target)
        assert len(frames) == 1, f"expected one data frame, got {len(frames)}"
        buckets, counts = frames[0]["t"], frames[0]["cnt"]
        assert (
            sum(counts) == SEEDED_ROWS
        ), f"bucket counts {counts} do not add up to {SEEDED_ROWS}"
        assert buckets == sorted(buckets), "time buckets are not in order"
        assert all(
            t % 60000 == 0 for t in buckets
        ), f"buckets are not whole minutes: {buckets[:5]}"
        # 100 rows every 10 seconds span about 17 minutes.
        assert (
            15 <= len(buckets) <= 20
        ), f"expected about 17 one-minute buckets, got {len(buckets)}"


@TestFeature
@Name("panel graph")
def feature(self):
    """Test ClickHouse data in Grafana Explore and dashboard panels."""
    Scenario(run=explore_count_query)
    Scenario(run=dashboard_time_series_macros)
