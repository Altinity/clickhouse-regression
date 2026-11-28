"""How the reader replays a hand-written Delta log.

Each scenario writes the actions it needs and reads with ``deltaLake()``.
"""

import pyarrow as pa
from testflows.core import *

from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Protocol_CatalogManaged,
    RQ_SRS_050_ClickHouse_DeltaLake_Protocol_DataChange,
    RQ_SRS_050_ClickHouse_DeltaLake_Protocol_Format,
    RQ_SRS_050_ClickHouse_DeltaLake_Protocol_Paths,
    RQ_SRS_050_ClickHouse_DeltaLake_Protocol_Replay,
    RQ_SRS_050_ClickHouse_DeltaLake_Protocol_UnknownFields,
)
from delta_lake.tests.steps.log import (
    add,
    commit,
    commit_info,
    create_hand_table,
    field,
    metadata,
    protocol,
    remove,
    upload_parquet,
)
from delta_lake.tests.steps.query import (
    delta_function,
    expect_error,
    expect_query_lines,
    try_query,
)

FIELDS = [field("id", "long")]


def ids(*values):
    return pa.table({"id": pa.array(list(values), pa.int64())})


def one_file_table(self, protocol_action=None, provider="parquet", extra_actions=()):
    table = create_hand_table()
    name, size = upload_parquet(table=table, name="part-0.parquet", data=ids(1, 2))
    commit(
        table=table,
        version=0,
        actions=[
            protocol_action or protocol(),
            metadata(FIELDS, provider=provider),
            add(name, size),
            *extra_actions,
        ],
    )
    return table


def select_ids(self, table):
    return f"SELECT id FROM {delta_function(self, table.http_url)} ORDER BY id"


@TestScenario
@Name("add and remove replay")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Protocol_Replay("1.0"))
def add_remove_replay(self):
    """A file added at version 0 and removed at version 1 is not read."""

    with Given("two files added at version 0"):
        table = create_hand_table()
        first, first_size = upload_parquet(table=table, name="a.parquet", data=ids(1, 2))
        second, second_size = upload_parquet(table=table, name="b.parquet", data=ids(3))
        commit(
            table=table,
            version=0,
            actions=[
                protocol(),
                metadata(FIELDS),
                add(first, first_size),
                add(second, second_size),
            ],
        )

    with When("version 1 removes the first file and adds a third"):
        third, third_size = upload_parquet(table=table, name="c.parquet", data=ids(4))
        commit(
            table=table,
            version=1,
            actions=[remove(first, first_size), add(third, third_size)],
        )

    with Then("the snapshot has the second and third files"):
        expect_query_lines(sql=select_ids(self, table), expected=["3", "4"])


@TestScenario
@Name("encoded paths")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Protocol_Paths("1.0"))
def encoded_paths(self):
    """The add path is URI-encoded. The object key is the decoded name."""

    with Given("a file stored as 'b c%.parquet'"):
        table = create_hand_table()
        name, size = upload_parquet(table=table, name="b c%.parquet", data=ids(5))

    with And("the log names it 'b%20c%25.parquet'"):
        commit(
            table=table,
            version=0,
            actions=[protocol(), metadata(FIELDS), add("b%20c%25.parquet", size)],
        )

    with Then("the row of that file comes back"):
        expect_query_lines(sql=select_ids(self, table), expected=["5"])


@TestScenario
@Name("non parquet provider")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Protocol_Format("1.0"))
def non_parquet_provider(self):
    """format.provider csv fails the read instead of reading the files as Parquet."""

    with Given("a log whose format provider is csv"):
        table = one_file_table(self, provider="csv")

    with When("I read it"):
        result = try_query(sql=select_ids(self, table) + " FORMAT TabSeparated")

    with Then("the read fails"):
        expect_error(result=result)


@TestScenario
@Name("data change false")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Protocol_DataChange("1.0"))
def data_change_false(self):
    """A compaction commit with dataChange false leaves the rows unchanged."""

    with Given("a table with one file"):
        table = one_file_table(self)

    with When("version 1 replaces it with a copy, dataChange false on both actions"):
        name, size = upload_parquet(table=table, name="compacted.parquet", data=ids(1, 2))
        commit(
            table=table,
            version=1,
            actions=[
                remove("part-0.parquet", data_change=False),
                add(name, size, data_change=False),
            ],
        )

    with Then("the rows are the same and appear once"):
        expect_query_lines(sql=select_ids(self, table), expected=["1", "2"])


@TestScenario
@Name("unknown fields")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Protocol_UnknownFields("1.0"))
def unknown_fields(self):
    """Fields the reader does not know, in add and in commitInfo, are ignored."""

    with Given("a log with unknown fields"):
        table = create_hand_table()
        name, size = upload_parquet(table=table, name="part-0.parquet", data=ids(1, 2))
        commit(
            table=table,
            version=0,
            actions=[
                commit_info({"futureCommitField": {"nested": 1}}),
                protocol(),
                metadata(FIELDS),
                add(name, size, extra={"futureAddField": [1, 2, 3]}),
            ],
        )

    with Then("the rows come back"):
        expect_query_lines(sql=select_ids(self, table), expected=["1", "2"])


@TestScenario
@Name("catalog managed")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Protocol_CatalogManaged("1.0"))
def catalog_managed(self):
    """A table with the catalogManaged reader feature fails closed."""

    with Given("a log whose protocol requires catalogManaged"):
        table = one_file_table(
            self, protocol_action=protocol(3, 7, ["catalogManaged"], ["catalogManaged"])
        )

    with When("I read it"):
        result = try_query(sql=select_ids(self, table) + " FORMAT TabSeparated")

    with Then("the read fails"):
        expect_error(result=result, message="Catalog-managed table")


@TestFeature
@Name("delta protocol")
def feature(self):
    """Delta log replay."""
    Scenario(test=add_remove_replay)()
    Scenario(test=encoded_paths)()
    Scenario(test=non_parquet_provider)()
    Scenario(test=data_change_false)()
    Scenario(test=unknown_fields)()
    Scenario(test=catalog_managed)()
