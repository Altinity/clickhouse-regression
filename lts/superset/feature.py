"""Apache Superset sub-suite feature loaded by the LTS orchestrator."""

import os

from testflows.core import *

from lts.superset.requirements.requirements import (
    SRS_101_Apache_Superset_ClickHouse_Integration_LTS_Testing,
)
from lts.superset.steps.environment import (
    superset_environment,
    wait_for_superset,
    wait_for_selenium,
)


@TestFeature
@Name("superset")
@Specifications(SRS_101_Apache_Superset_ClickHouse_Integration_LTS_Testing)
def feature(
    self,
    superset_version="4.1.1",
    clickhouse_driver="clickhouse-connect",
    selenium_version="4.40.0",
):
    """Run Superset integration tests against a ClickHouse image."""
    suite_dir = os.path.dirname(os.path.abspath(__file__))
    configs_dir = os.path.join(suite_dir, "configs")
    clickhouse_image = self.context.clickhouse_image

    self.context.configs_dir = configs_dir
    self.context.superset_version = superset_version
    self.context.clickhouse_driver = clickhouse_driver

    note(f"ClickHouse image: {clickhouse_image}")
    note(f"Superset version: {superset_version}")
    note(f"ClickHouse driver: {clickhouse_driver}")

    with Given("Superset and ClickHouse environment is up"):
        superset_environment(
            configs_dir=configs_dir,
            clickhouse_image=clickhouse_image,
            superset_version=superset_version,
            clickhouse_driver=clickhouse_driver,
            selenium_version=selenium_version,
        )

    with And("Superset is healthy"):
        wait_for_superset()

    with And("Selenium Grid is ready"):
        wait_for_selenium()

    Feature(run=load("lts.superset.tests.ui_smoke", "feature"))
