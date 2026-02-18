"""Test scenarios for building and running clickhouse-odbc against ClickHouse LTS."""
import os

from testflows.core import *

from lts.clickhouse_odbc.requirements.requirements import (
    RQ_SRS_100_ODBC_DriverBuild,
    RQ_SRS_100_ODBC_Connection,
    RQ_SRS_100_ODBC_Compatibility_LTS,
)
from lts.clickhouse_odbc.steps.docker import (
    build_odbc_runner_image,
    run_odbc_tests_in_container,
    verify_test_results,
)


@TestScenario
@Requirements(RQ_SRS_100_ODBC_DriverBuild("1.0"))
def build_odbc_runner(self):
    """Build the ODBC runner Docker image."""
    build_odbc_runner_image(
        configs_dir=self.context.configs_dir,
        clickhouse_image=self.context.clickhouse_image,
    )


@TestScenario
@Requirements(
    RQ_SRS_100_ODBC_Connection("1.0"),
    RQ_SRS_100_ODBC_Compatibility_LTS("1.0"),
)
def run_odbc_tests(self):
    """Run the clickhouse-odbc test suite in a container."""
    run_odbc_tests_in_container(
        configs_dir=self.context.configs_dir,
        packages_dir=self.context.packages_dir,
        odbc_release=self.context.odbc_release,
    )


@TestScenario
@Requirements(RQ_SRS_100_ODBC_Compatibility_LTS("1.0"))
def check_results(self):
    """Verify test results from the ODBC test run."""
    verify_test_results(packages_dir=self.context.packages_dir)


@TestFeature
@Name("build and run")
def feature(self):
    """Build clickhouse-odbc, run tests against ClickHouse, verify results."""
    Scenario(run=build_odbc_runner)
    Scenario(run=run_odbc_tests)
    Scenario(run=check_results)
