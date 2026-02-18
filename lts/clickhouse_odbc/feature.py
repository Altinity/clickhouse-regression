"""ClickHouse ODBC driver sub-suite feature loaded by the LTS orchestrator."""

import os
import sys

from testflows.core import *

from lts.clickhouse_odbc.requirements.requirements import (
    SRS_100_ClickHouse_ODBC_Driver_LTS_Testing,
)


@TestFeature
@Name("clickhouse-odbc")
@Specifications(SRS_100_ClickHouse_ODBC_Driver_LTS_Testing)
def feature(self, odbc_release="v1.5.2.20260217"):
    """Run clickhouse-odbc tests against a ClickHouse image."""
    suite_dir = os.path.dirname(os.path.abspath(__file__))

    configs_dir = os.path.join(suite_dir, "configs")
    packages_dir = os.path.join(configs_dir, "PACKAGES")
    os.makedirs(packages_dir, exist_ok=True)

    self.context.configs_dir = configs_dir
    self.context.packages_dir = packages_dir
    self.context.odbc_release = odbc_release

    Feature(run=load("lts.clickhouse_odbc.tests.build_and_run", "feature"))
