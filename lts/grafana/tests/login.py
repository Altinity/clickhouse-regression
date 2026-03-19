"""Test scenarios for Grafana login with ClickHouse backend."""

from testflows.core import *

from lts.grafana.requirements.requirements import (
    RQ_SRS_102_Grafana_Login,
    RQ_SRS_102_Grafana_Compatibility_LTS,
)
from lts.grafana.steps.ui import (
    create_webdriver,
    open_grafana,
    take_screenshot,
    login,
    skip_password_change,
    verify_logged_in,
)


@TestScenario
@Requirements(
    RQ_SRS_102_Grafana_Login("1.0"),
    RQ_SRS_102_Grafana_Compatibility_LTS("1.0"),
)
def login_with_default_credentials(self):
    """Verify that Grafana allows logging in with default admin credentials
    when backed by a ClickHouse datasource."""

    with Given("a WebDriver connected to Selenium Grid"):
        driver = create_webdriver()

    with And("I open the Grafana login page"):
        open_grafana(driver=driver)

    with And("I take a screenshot of the login page"):
        take_screenshot(driver=driver, name="grafana_login_page")

    with When("I log in with default admin credentials"):
        login(driver=driver, username="admin", password="admin")

    with And("I skip the password change prompt if shown"):
        skip_password_change(driver=driver)

    with Then("I should be on the Grafana home page"):
        verify_logged_in(driver=driver)

    with And("I take a screenshot of the home page after login"):
        take_screenshot(driver=driver, name="grafana_after_login")


@TestFeature
@Name("login")
def feature(self):
    """Test Grafana login scenarios."""
    Scenario(run=login_with_default_credentials)
