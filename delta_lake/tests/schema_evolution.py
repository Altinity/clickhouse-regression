"""Schema changes across Delta commits.

``deltalake`` adds a column with ``schema_mode="merge"``. Dropping and
reordering columns without rewriting files, and type widening, need a
hand-written log: the old Parquet file stays and only the log schema moves.
"""

import pyarrow as pa
from testflows.asserts import error
from testflows.core import *

from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Read_SchemaEvolution,
    RQ_SRS_050_ClickHouse_DeltaLake_Read_SchemaReload,
    RQ_SRS_050_ClickHouse_DeltaLake_Read_TypeWidening,
)
from delta_lake.tests.steps import commit_delta_table, create_delta_table
from delta_lake.tests.steps.access import create_engine_table
from delta_lake.tests.steps.log import (
    add,
    commit,
    create_hand_table,
    field,
    metadata,
    protocol,
    upload_parquet,
)
from delta_lake.tests.steps.query import (
    delta_function,
    expect_query_lines,
    query_lines,
)

FIRST = pa.table({"id": pa.array([1, 2], pa.int64())})
SECOND = pa.table(
    {"id": pa.array([3], pa.int64()), "added": pa.array([7], pa.int64())}
)


def column_types(self, source, settings=""):
    described = query_lines(sql=f"DESCRIBE TABLE {source} {settings}".rstrip())
    return [tuple(line.split("\t")[:2]) for line in described]


def evolved_table():
    """Version 0 has ``id``. Version 1 adds ``added`` and one row."""
    table = create_delta_table(
        columns=(), data=FIRST, register=False, create_schema=False
    )
    commit_delta_table(table=table, data=SECOND, mode="append", schema_mode="merge")
    return table


@TestScenario
@Name("add column")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_SchemaEvolution("1.0"))
def add_column(self):
    """Rows from files written before the new column read it as NULL."""

    with Given("a table whose second commit adds a nullable column"):
        table = evolved_table()
        source = delta_function(self, table.http_url)

    with Then("DESCRIBE lists the new column"):
        found = column_types(self, source)
        assert found == [
            ("id", "Nullable(Int64)"),
            ("added", "Nullable(Int64)"),
        ], error(found)

    with And("older rows are NULL in that column"):
        expect_query_lines(
            sql=f"SELECT id, added FROM {source} ORDER BY id",
            expected=["1\t\\N", "2\t\\N", "3\t7"],
        )


@TestScenario
@Name("drop and reorder columns")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_SchemaEvolution("1.0"))
def drop_and_reorder(self):
    """A column removed from the log is gone, and the log order wins.

    The Parquet file still stores ``gone`` and keeps the original order.
    """

    with Given("a hand-written table"):
        table = create_hand_table()

    with And("one file with id, gone, and z"):
        name, size = upload_parquet(
            table=table,
            name="part-0.parquet",
            data=pa.table(
                {
                    "id": pa.array([1, 2], pa.int64()),
                    "gone": pa.array(["x", "y"]),
                    "z": pa.array([5, 6], pa.int32()),
                }
            ),
        )

    with And("version 0 lists id, gone, z"):
        commit(
            table=table,
            version=0,
            actions=[
                protocol(),
                metadata(
                    [field("id", "long"), field("gone", "string"), field("z", "integer")]
                ),
                add(name, size),
            ],
        )

    with And("version 1 drops gone and puts z first"):
        commit(
            table=table,
            version=1,
            actions=[metadata([field("z", "integer"), field("id", "long")])],
        )

    source = delta_function(self, table.http_url)

    with Then("DESCRIBE follows the version 1 schema"):
        found = column_types(self, source)
        assert found == [("z", "Nullable(Int32)"), ("id", "Nullable(Int64)")], error(
            found
        )

    with And("SELECT * returns z and id in that order"):
        expect_query_lines(
            sql=f"SELECT * FROM {source} ORDER BY id", expected=["5\t1", "6\t2"]
        )


@TestScenario
@Name("schema of an older version")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_SchemaEvolution("1.0"))
def older_version_schema(self):
    """delta_lake_snapshot_version reads that version with its own schema."""

    with Given("a table whose second commit adds a column"):
        table = evolved_table()
        source = delta_function(self, table.http_url)

    with Then("version 0 has only id"):
        found = column_types(
            self, source, "SETTINGS delta_lake_snapshot_version = 0"
        )
        assert found == [("id", "Nullable(Int64)")], error(found)

    with And("version 0 returns only its two rows"):
        expect_query_lines(
            sql=f"SELECT * FROM {source} ORDER BY id "
            "SETTINGS delta_lake_snapshot_version = 0",
            expected=["1", "2"],
        )


@TestScenario
@Name("schema reload")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_SchemaReload("1.0"))
def schema_reload(self):
    """With the reload setting, an engine table sees a column added after attach."""

    with Given("a Delta table with only id"):
        table = create_delta_table(
            columns=(), data=FIRST, register=False, create_schema=False
        )

    with And("an engine table attached to it"):
        name = create_engine_table(url=table.http_url)

    with When("deltalake commits a new column"):
        commit_delta_table(
            table=table, data=SECOND, mode="append", schema_mode="merge"
        )

    with Then("SELECT * with the reload setting returns the new column"):
        expect_query_lines(
            sql=f"SELECT * FROM {name} ORDER BY id "
            "SETTINGS delta_lake_reload_schema_for_consistency = 1",
            expected=["1\t\\N", "2\t\\N", "3\t7"],
        )


@TestScenario
@Name("type widening")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_TypeWidening("1.0"))
def type_widening(self):
    """integer widened to long reads both files as Int64.

    The first file stores int32 and the second stores a value that only
    fits in int64. A server without typeWidening may fail the read
    instead, but must not return a wrong value.
    """

    with Given("a hand-written table"):
        table = create_hand_table()

    with And("an int32 file at version 0"):
        first, first_size = upload_parquet(
            table=table,
            name="part-0.parquet",
            data=pa.table({"n": pa.array([1, 2], pa.int32())}),
        )
        commit(
            table=table,
            version=0,
            actions=[protocol(), metadata([field("n", "integer")]), add(first, first_size)],
        )

    with And("version 1 widens n to long and adds an int64 file"):
        second, second_size = upload_parquet(
            table=table,
            name="part-1.parquet",
            data=pa.table({"n": pa.array([5000000000], pa.int64())}),
        )
        commit(
            table=table,
            version=1,
            actions=[
                protocol(3, 7, ["typeWidening"], ["typeWidening"]),
                metadata(
                    [
                        field(
                            "n",
                            "long",
                            metadata={
                                "delta.typeChanges": [
                                    {"fromType": "integer", "toType": "long"}
                                ]
                            },
                        )
                    ],
                    configuration={"delta.enableTypeWidening": "true"},
                ),
                add(second, second_size),
            ],
        )

    source = delta_function(self, table.http_url)

    with Then("DESCRIBE reports Int64"):
        found = column_types(self, source)
        assert found == [("n", "Nullable(Int64)")], error(found)

    with And("both files return their values"):
        expect_query_lines(
            sql=f"SELECT n FROM {source} ORDER BY n",
            expected=["1", "2", "5000000000"],
        )


@TestFeature
@Name("delta schema evolution")
def feature(self):
    """Delta schema changes across commits."""
    Scenario(test=add_column)()
    Scenario(test=drop_and_reorder)()
    Scenario(test=older_version_schema)()
    Scenario(test=schema_reload)()
    Scenario(test=type_widening)()
