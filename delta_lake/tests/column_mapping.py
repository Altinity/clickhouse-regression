"""Delta column mapping modes none, name, and id.

The log is hand-written. In ``name`` and ``id`` mode the Parquet columns
use physical names, and ``SELECT`` must use the logical names from the
log. ``id`` mode resolves columns by the Parquet field id.
"""

import pyarrow as pa
from testflows.asserts import error
from testflows.core import *

from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Read_ColumnMapping,
    RQ_SRS_050_ClickHouse_DeltaLake_Read_SchemaEvolution,
)
from delta_lake.tests.steps.log import (
    add,
    commit,
    create_hand_table,
    field,
    mapped_field,
    metadata,
    protocol,
    upload_parquet,
)
from delta_lake.tests.steps.query import (
    delta_function,
    expect_query_lines,
    query_lines,
)

MAPPING_PROTOCOL = protocol(2, 5)


def mapping(mode, max_id):
    return {
        "delta.columnMapping.mode": mode,
        "delta.columnMapping.maxColumnId": str(max_id),
    }


def physical_data(id_name, label_name):
    return pa.table(
        {
            id_name: pa.array([1, 2], pa.int64()),
            label_name: pa.array(["x", "y"]),
        }
    )


def column_names(self, source, settings=""):
    described = query_lines(sql=f"DESCRIBE TABLE {source} {settings}".rstrip())
    return [line.split("\t")[0] for line in described]


@TestScenario
@Name("mode none")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_ColumnMapping("1.0"))
def mode_none(self):
    """Without column mapping the Parquet names are the column names."""

    with Given("a table with columnMapping.mode none"):
        table = create_hand_table()
        name, size = upload_parquet(
            table=table, name="part-0.parquet", data=physical_data("id", "label")
        )
        commit(
            table=table,
            version=0,
            actions=[
                protocol(),
                metadata(
                    [field("id", "long"), field("label", "string")],
                    configuration={"delta.columnMapping.mode": "none"},
                ),
                add(name, size),
            ],
        )

    with Then("SELECT returns the rows by name"):
        expect_query_lines(
            sql=f"SELECT id, label FROM {delta_function(self, table.http_url)} "
            "ORDER BY id",
            expected=["1\tx", "2\ty"],
        )


@TestScenario
@Name("mode name")
@Requirements(
    RQ_SRS_050_ClickHouse_DeltaLake_Read_ColumnMapping("1.0"),
    RQ_SRS_050_ClickHouse_DeltaLake_Read_SchemaEvolution("1.0"),
)
def mode_name(self):
    """Logical names map to physical names, including after a rename.

    Version 0 calls the columns id and label. Version 1 renames label to
    renamed. Version 2 adds extra, which the old file does not store.
    """
    config = mapping("name", 2)

    with Given("a table whose Parquet columns are col-a and col-b"):
        table = create_hand_table()
        name, size = upload_parquet(
            table=table, name="part-0.parquet", data=physical_data("col-a", "col-b")
        )

    with And("version 0 maps id and label to them"):
        commit(
            table=table,
            version=0,
            actions=[
                MAPPING_PROTOCOL,
                metadata(
                    [
                        mapped_field("id", "long", 1, "col-a"),
                        mapped_field("label", "string", 2, "col-b"),
                    ],
                    configuration=config,
                ),
                add(name, size),
            ],
        )

    with And("version 1 renames label to renamed"):
        commit(
            table=table,
            version=1,
            actions=[
                metadata(
                    [
                        mapped_field("id", "long", 1, "col-a"),
                        mapped_field("renamed", "string", 2, "col-b"),
                    ],
                    configuration=config,
                )
            ],
        )

    with And("version 2 adds extra"):
        commit(
            table=table,
            version=2,
            actions=[
                metadata(
                    [
                        mapped_field("id", "long", 1, "col-a"),
                        mapped_field("renamed", "string", 2, "col-b"),
                        mapped_field("extra", "long", 3, "col-c"),
                    ],
                    configuration=mapping("name", 3),
                )
            ],
        )

    source = delta_function(self, table.http_url)

    with Then("version 0 uses the names id and label"):
        names = column_names(self, source, "SETTINGS delta_lake_snapshot_version = 0")
        assert names == ["id", "label"], error(names)
        expect_query_lines(
            sql=f"SELECT id, label FROM {source} ORDER BY id "
            "SETTINGS delta_lake_snapshot_version = 0",
            expected=["1\tx", "2\ty"],
        )

    with And("version 1 returns the same values under renamed"):
        expect_query_lines(
            sql=f"SELECT id, renamed FROM {source} ORDER BY id "
            "SETTINGS delta_lake_snapshot_version = 1",
            expected=["1\tx", "2\ty"],
        )

    with And("the latest version returns NULL for extra"):
        names = column_names(self, source)
        assert names == ["id", "renamed", "extra"], error(names)
        expect_query_lines(
            sql=f"SELECT id, renamed, extra FROM {source} ORDER BY id",
            expected=["1\tx\t\\N", "2\ty\t\\N"],
        )


def id_mode_table(self, parquet_names):
    table = create_hand_table()
    name, size = upload_parquet(
        table=table,
        name="part-0.parquet",
        data=physical_data(*parquet_names),
        field_ids={parquet_names[0]: 1, parquet_names[1]: 2},
    )
    commit(
        table=table,
        version=0,
        actions=[
            MAPPING_PROTOCOL,
            metadata(
                [
                    mapped_field("id", "long", 1, "col-a"),
                    mapped_field("label", "string", 2, "col-b"),
                ],
                configuration=mapping("id", 2),
            ),
            add(name, size),
        ],
    )
    return table


@TestScenario
@Name("mode id")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_ColumnMapping("1.0"))
def mode_id(self):
    """Field ids 1 and 2 and physical names col-a and col-b, as Spark writes them."""

    with Given("a table in id mode whose Parquet names match the physical names"):
        table = id_mode_table(self, ("col-a", "col-b"))

    with Then("SELECT returns the rows under the logical names"):
        expect_query_lines(
            sql=f"SELECT id, label FROM {delta_function(self, table.http_url)} "
            "ORDER BY id",
            expected=["1\tx", "2\ty"],
        )


@TestScenario
@Name("mode id by field id")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_ColumnMapping("1.0"))
def mode_id_by_field_id(self):
    """In id mode the field id wins even when the Parquet names differ."""

    with Given("a table in id mode whose Parquet names are unrelated"):
        table = id_mode_table(self, ("p1", "p2"))

    with Then("SELECT resolves the columns by field id"):
        expect_query_lines(
            sql=f"SELECT id, label FROM {delta_function(self, table.http_url)} "
            "ORDER BY id",
            expected=["1\tx", "2\ty"],
        )


@TestFeature
@Name("delta column mapping")
def feature(self):
    """Delta column mapping."""
    Scenario(test=mode_none)()
    Scenario(test=mode_name)()
    Scenario(test=mode_id)()
    Scenario(test=mode_id_by_field_id)()
