"""Partitioned Delta tables written by ``deltalake`` with ``partition_by``.

Partition values live in the log, not in the Parquet files. A filter on
the partition column must return the matching rows with and without the
engine predicate, and ``_path`` must only name files from that partition.
"""

import pyarrow as pa
from testflows.asserts import error
from testflows.core import *

from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Read_PartitionPruning,
    RQ_SRS_050_ClickHouse_DeltaLake_Schema_PartitionColumns,
)
from delta_lake.tests.steps import (
    column,
    create_database,
    create_delta_table,
)
from delta_lake.tests.steps.query import (
    catalog_source,
    delta_function,
    expect_query_lines,
    query_lines,
)

COLUMNS = (
    column("id", "LONG", "bigint", "long"),
    column("region", "STRING", "string", "string"),
)

DATA = pa.table(
    {
        "id": pa.array([1, 2, 3, 4], pa.int64()),
        "region": pa.array(["eu", "us", "us", None]),
    }
)


def partitioned_table():
    return create_delta_table(columns=COLUMNS, data=DATA, partition_by=["region"])


def readers(self, table):
    with By("opening Unity"):
        database = create_database()
    return [delta_function(self, table.http_url), catalog_source(database, table)]


@TestScenario
@Name("partition filter")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_PartitionPruning("1.0"))
def partition_filter(self):
    """region = 'us' returns ids 2 and 3, and _path is only from region=us."""

    with Given("a Delta table partitioned by region"):
        table = partitioned_table()

    for source in readers(self, table):
        with Then(f"the filter on {source} returns the us rows"):
            expect_query_lines(
                sql=f"SELECT id, region FROM {source} WHERE region = 'us' ORDER BY id",
                expected=["2\tus", "3\tus"],
            )

        with And("_path names only files under region=us"):
            paths = query_lines(
                sql=f"SELECT DISTINCT _path FROM {source} WHERE region = 'us'"
            )
            assert paths, error(paths)
            for path in paths:
                assert "/region=us/" in path, error(paths)

        with And("delta_lake_enable_engine_predicate = 0 returns the same rows"):
            expect_query_lines(
                sql=f"SELECT id, region FROM {source} WHERE region = 'us' "
                "ORDER BY id SETTINGS delta_lake_enable_engine_predicate = 0",
                expected=["2\tus", "3\tus"],
            )

        with And("a filter that matches no partition returns nothing"):
            expect_query_lines(
                sql=f"SELECT id FROM {source} WHERE region = 'apac'", expected=[]
            )


@TestScenario
@Name("partition columns")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Schema_PartitionColumns("1.0"))
def partition_columns(self):
    """The partition column is a regular column, and a null value is NULL."""

    with Given("a Delta table partitioned by region with one null region"):
        table = partitioned_table()

    for source in readers(self, table):
        with Then(f"DESCRIBE {source} lists region as Nullable(String)"):
            described = query_lines(sql=f"DESCRIBE TABLE {source}")
            found = [tuple(line.split("\t")[:2]) for line in described]
            assert ("region", "Nullable(String)") in found, error(described)

        with And("every row carries its partition value"):
            expect_query_lines(
                sql=f"SELECT id, region FROM {source} ORDER BY id",
                expected=["1\teu", "2\tus", "3\tus", "4\t\\N"],
            )

        with And("the null partition is NULL, not an empty string"):
            expect_query_lines(
                sql=f"SELECT id FROM {source} WHERE region IS NULL", expected=["4"]
            )


@TestFeature
@Name("delta partitions")
def feature(self):
    """Partitioned Delta tables."""
    Scenario(test=partition_filter)()
    Scenario(test=partition_columns)()
