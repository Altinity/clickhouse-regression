"""Change data feed with ``delta_lake_snapshot_start_version`` and ``_end_version``.

``deltalake`` writes ``_change_data`` files for delete and update when
``delta.enableChangeDataFeed`` is on. An append has only ``add`` actions,
and a hand-written commit with only a ``remove`` reports deletes.
"""

import pyarrow as pa
from testflows.asserts import error
from testflows.core import *

from deltalake import DeltaTable as DeltaTableReader

from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Read_ChangeDataFeed,
)
from delta_lake.tests.steps import commit_delta_table, create_delta_table
from delta_lake.tests.steps.catalog import _storage_options
from delta_lake.tests.steps.log import (
    add,
    commit,
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
    kernel_setting,
    try_query,
)

CDF = {"delta.enableChangeDataFeed": "true"}
SCHEMA = pa.schema([pa.field("id", pa.int64()), pa.field("v", pa.string())])
CHANGES = "id, v, _change_type, _commit_version"
CHANGE_ROWS = [
    "3\tc\tinsert\t1",
    "1\ta\tdelete\t2",
    "2\tB\tupdate_postimage\t3",
    "2\tb\tupdate_preimage\t3",
]


def rows(*values):
    return pa.Table.from_pylist(
        [{"id": id_, "v": v} for id_, v in values], schema=SCHEMA
    )


def table_versions(self, configuration):
    """v0 inserts 1 and 2, v1 appends 3, v2 deletes 1, v3 updates 2 to B."""
    table = create_delta_table(
        columns=(),
        data=rows((1, "a"), (2, "b")),
        register=False,
        create_schema=False,
        configuration=configuration,
    )
    commit_delta_table(table=table, data=rows((3, "c")), mode="append")
    options = _storage_options(
        self.context.rustfs_access_key, self.context.rustfs_secret_key
    )
    DeltaTableReader(table.location, storage_options=options).delete("id = 1")
    DeltaTableReader(table.location, storage_options=options).update(
        updates={"v": "'B'"}, predicate="id = 2"
    )
    return table


def range_sql(source, start, end=None):
    settings = f"delta_lake_snapshot_start_version = {start}"
    if end is not None:
        settings += f", delta_lake_snapshot_end_version = {end}"
    return (
        f"SELECT {CHANGES} FROM {source} "
        f"ORDER BY _commit_version, id, _change_type SETTINGS {settings}"
    )


@TestScenario
@Name("change rows")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_ChangeDataFeed("1.0"))
def change_rows(self):
    """Versions 1 to 3 report the insert, the delete, and both update images.

    The insert comes from an add action. The delete and the update come
    from the _change_data files of those commits.
    """
    with Given("a table with change data feed and four versions"):
        table = table_versions(self, CDF)
        source = delta_function(self, table.http_url)

    with Then("versions 1 to 3 return one change per row image"):
        expect_query_lines(sql=range_sql(source, 1, 3), expected=CHANGE_ROWS)

    with And("version 2 alone returns only the delete"):
        expect_query_lines(sql=range_sql(source, 2, 2), expected=["1\ta\tdelete\t2"])


@TestScenario
@Name("remove only commit")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_ChangeDataFeed("1.0"))
def remove_only_commit(self):
    """A commit with only a remove action reports its rows as deletes."""

    with Given("a hand-written table with change data feed"):
        table = create_hand_table()
        name, size = upload_parquet(
            table=table, name="part-0.parquet", data=rows((1, "a"), (2, "b"))
        )
        commit(
            table=table,
            version=0,
            actions=[
                protocol(1, 4),
                metadata(
                    [field("id", "long"), field("v", "string")], configuration=CDF
                ),
                add(name, size),
            ],
        )

    with When("version 1 removes the file"):
        commit(table=table, version=1, actions=[remove(name, size)])

    with Then("version 1 reports both rows as deletes"):
        expect_query_lines(
            sql=range_sql(delta_function(self, table.http_url), 1, 1),
            expected=["1\ta\tdelete\t1", "2\tb\tdelete\t1"],
        )


@TestScenario
@Name("invalid ranges")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_ChangeDataFeed("1.0"))
def invalid_ranges(self):
    """An end version alone, a table without the feed, and the kernel off all fail."""
    setting = kernel_setting(self)

    with Given("a table with change data feed"):
        table = table_versions(self, CDF)
        source = delta_function(self, table.http_url)

    with And("the same history without change data feed"):
        plain = table_versions(self, None)
        plain_source = delta_function(self, plain.http_url)

    with When("I set only delta_lake_snapshot_end_version"):
        result = try_query(
            sql=f"SELECT id FROM {source} "
            "SETTINGS delta_lake_snapshot_end_version = 3 FORMAT TabSeparated"
        )

    with Then("the read fails"):
        expect_error(result=result, message="delta_lake_snapshot_start_version")

    with When("I read a range from the table without change data feed"):
        result = try_query(sql=range_sql(plain_source, 0, 1) + " FORMAT TabSeparated")

    with Then("the read fails"):
        expect_error(result=result, message="Change data feed is unsupported")

    with When(f"I read a range with {setting} = 0"):
        result = try_query(
            sql=range_sql(source, 1, 3) + f", {setting} = 0 FORMAT TabSeparated"
        )

    with Then("the read fails or returns exactly the changes"):
        if result.exitcode == 0:
            found = result.output.splitlines()
            assert found == CHANGE_ROWS, error(found)


@TestFeature
@Name("delta change data feed")
def feature(self):
    """Delta change data feed."""
    Scenario(test=change_rows)()
    Scenario(test=remove_only_commit)()
    Scenario(test=invalid_ranges)()
