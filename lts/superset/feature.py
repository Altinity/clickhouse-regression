"""Apache Superset sub-suite feature loaded by the LTS orchestrator."""
import os

from testflows.core import *

from lts.superset.requirements.requirements import (
    SRS_101_Apache_Superset_ClickHouse_Integration_LTS_Testing,
)


@TestFeature
@Name("superset")
@Specifications(SRS_101_Apache_Superset_ClickHouse_Integration_LTS_Testing)
def feature(
    self,
    superset_version="4.1.1",
    clickhouse_driver="clickhouse-connect",
):
    """Run Superset integration tests against a ClickHouse image."""
    suite_dir = os.path.dirname(os.path.abspath(__file__))
    configs_dir = os.path.join(suite_dir, "configs")

    self.context.configs_dir = configs_dir
    self.context.superset_version = superset_version
    self.context.clickhouse_driver = clickhouse_driver

    note(f"Superset version: {superset_version}")
    note(f"ClickHouse driver: {clickhouse_driver}")

    Feature(run=load("lts.superset.tests.connection", "feature"))
    Feature(run=load("lts.superset.tests.sql_lab", "feature"))
    Feature(run=load("lts.superset.tests.charts", "feature"))
    Feature(run=load("lts.superset.tests.dashboards", "feature"))
