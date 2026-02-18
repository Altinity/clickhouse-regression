"""Altinity Grafana ClickHouse plugin sub-suite feature loaded by the LTS orchestrator."""

import os

from testflows.core import *

from lts.grafana.requirements.requirements import (
    SRS_102_Altinity_Grafana_ClickHouse_Plugin_LTS_Testing,
)
from lts.grafana.steps.environment import (
    grafana_environment,
    wait_for_grafana,
    wait_for_selenium,
)


@TestFeature
@Name("grafana")
@Specifications(SRS_102_Altinity_Grafana_ClickHouse_Plugin_LTS_Testing)
def feature(
    self,
    grafana_version="latest",
    grafana_plugin_version="3.4.9",
    selenium_version="4.40.0",
):
    """Run Grafana plugin integration tests against a ClickHouse image."""
    suite_dir = os.path.dirname(os.path.abspath(__file__))
    configs_dir = os.path.join(suite_dir, "configs")
    clickhouse_image = self.context.clickhouse_image

    self.context.configs_dir = configs_dir
    self.context.grafana_version = grafana_version
    self.context.grafana_plugin_version = grafana_plugin_version

    note(f"ClickHouse image: {clickhouse_image}")
    note(f"Grafana version: {grafana_version}")
    note(f"Grafana plugin version: {grafana_plugin_version}")

    with Given("Grafana and ClickHouse environment is up"):
        grafana_environment(
            configs_dir=configs_dir,
            clickhouse_image=clickhouse_image,
            grafana_version=grafana_version,
            grafana_plugin_version=grafana_plugin_version,
            selenium_version=selenium_version,
        )

    with And("Grafana is healthy"):
        wait_for_grafana()

    with And("Selenium Grid is ready"):
        wait_for_selenium()

    Feature(run=load("lts.grafana.tests.login", "feature"))
