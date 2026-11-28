"""Read an older snapshot with ``delta_lake_snapshot_version``.

Version 0 has ids 1 and 2. Version 1 appends 3. Version 2 overwrites
the table with 10.
"""

import pyarrow as pa
from testflows.asserts import error
from testflows.core import *

from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Read_Kernel,
    RQ_SRS_050_ClickHouse_DeltaLake_Read_TimeTravel,
)
from delta_lake.tests.steps import (
    column,
    commit_delta_table,
    create_database,
    create_delta_table,
)
from delta_lake.tests.steps.access import create_engine_table
from delta_lake.tests.steps.query import (
    catalog_source,
    delta_function,
    expect_error,
    expect_query_lines,
    kernel_setting,
    try_query,
)

COLUMNS = (column("id", "LONG", "bigint", "long"),)

VERSIONS = {
    0: ["1", "2"],
    1: ["1", "2", "3"],
    2: ["10"],
}


def ids(*values):
    return pa.table({"id": pa.array(list(values), pa.int64())})


def three_versions():
    table = create_delta_table(columns=COLUMNS, data=ids(1, 2))
    commit_delta_table(table=table, data=ids(3), mode="append")
    commit_delta_table(table=table, data=ids(10), mode="overwrite")
    return table


def readers(self, table):
    sources = [delta_function(self, table.http_url)]
    with By("attaching an engine table"):
        sources.append(create_engine_table(url=table.http_url))
    with By("opening Unity"):
        sources.append(catalog_source(create_database(), table))
    return sources


@TestScenario
@Name("pinned versions")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_TimeTravel("1.0"))
def pinned_versions(self):
    """Each version returns its rows, and -1 returns the latest."""

    with Given("a table with three versions"):
        table = three_versions()

    for source in readers(self, table):
        for version, expected in VERSIONS.items():
            with Then(f"{source} at version {version} returns {expected}"):
                expect_query_lines(
                    sql=f"SELECT id FROM {source} ORDER BY id "
                    f"SETTINGS delta_lake_snapshot_version = {version}",
                    expected=expected,
                )

        with And("version -1 returns the latest snapshot"):
            expect_query_lines(
                sql=f"SELECT id FROM {source} ORDER BY id "
                "SETTINGS delta_lake_snapshot_version = -1",
                expected=VERSIONS[2],
            )


@TestScenario
@Name("missing version")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_TimeTravel("1.0"))
def missing_version(self):
    """A version after the latest commit fails instead of returning the latest."""

    with Given("a table with three versions"):
        table = three_versions()

    with When("I read version 99"):
        result = try_query(
            sql=f"SELECT id FROM {delta_function(self, table.http_url)} "
            "SETTINGS delta_lake_snapshot_version = 99 FORMAT TabSeparated"
        )

    with Then("the read fails"):
        expect_error(result=result, message="end version 99")


@TestScenario
@Name("pinned version without the kernel")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_Kernel("1.0"))
def pinned_without_kernel(self):
    """With the kernel off, a pinned version never returns the latest snapshot.

    Servers up to 26.10 fail the query. Newer servers read the pinned
    version without the kernel, which is also correct.
    """
    setting = kernel_setting(self)

    with Given("a table with three versions"):
        table = three_versions()
        source = delta_function(self, table.http_url)

    with When(f"I read version 0 with {setting} = 0"):
        result = try_query(
            sql=f"SELECT id FROM {source} ORDER BY id "
            f"SETTINGS delta_lake_snapshot_version = 0, {setting} = 0 "
            "FORMAT TabSeparated"
        )

    with Then("the read fails or returns exactly the version 0 rows"):
        if result.exitcode == 0:
            found = result.output.splitlines()
            assert found == VERSIONS[0], error(found)

    with And("the latest snapshot still reads with the kernel off"):
        expect_query_lines(
            sql=f"SELECT id FROM {source} ORDER BY id SETTINGS {setting} = 0",
            expected=VERSIONS[2],
        )


@TestFeature
@Name("delta time travel")
def feature(self):
    """Delta time travel."""
    Scenario(test=pinned_versions)()
    Scenario(test=missing_version)()
    Scenario(test=pinned_without_kernel)()
