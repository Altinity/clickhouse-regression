"""Snapshots that start from a checkpoint instead of the first commit.

``deltalake`` writes a classic checkpoint with ``create_checkpoint``.
Versions 0 to 2 append ids 0, 1, and 2, the checkpoint is at version 2,
and version 3 appends id 3.
"""

import pyarrow as pa
from testflows.asserts import error
from testflows.core import *

from deltalake import DeltaTable as DeltaTableReader

from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Protocol_Replay,
    RQ_SRS_050_ClickHouse_DeltaLake_Read_Checkpoint,
)
from delta_lake.tests.steps import (
    commit_delta_table,
    create_delta_table,
    list_keys,
    put_object,
)
from delta_lake.tests.steps.catalog import BUCKET, _s3, _storage_options
from delta_lake.tests.steps.query import delta_function, expect_query_lines

EXPECTED = ["0", "1", "2", "3"]


def ids(value):
    return pa.table({"id": pa.array([value], pa.int64())})


def checkpointed_table(self):
    table = create_delta_table(
        columns=(), data=ids(0), register=False, create_schema=False
    )
    for value in (1, 2):
        commit_delta_table(table=table, data=ids(value), mode="append")
    options = _storage_options(
        self.context.rustfs_access_key, self.context.rustfs_secret_key
    )
    DeltaTableReader(table.location, storage_options=options).create_checkpoint()
    commit_delta_table(table=table, data=ids(3), mode="append")
    return table


def log_key(table, name):
    return f"{table.prefix}/_delta_log/{name}"


def delete_keys(self, keys):
    client = _s3(self.context.rustfs_access_key, self.context.rustfs_secret_key)
    for key in keys:
        client.delete_object(Bucket=BUCKET, Key=key)


@TestScenario
@Name("classic checkpoint")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_Checkpoint("1.0"))
def classic_checkpoint(self):
    """The checkpoint replaces commits 0 to 2, and the result is unchanged."""

    with Given("a table with a checkpoint at version 2"):
        table = checkpointed_table(self)
        source = delta_function(self, table.http_url)

    with Then("the checkpoint is in the log"):
        keys = list_keys(prefix=f"{table.prefix}/_delta_log")
        assert log_key(table, f"{2:020d}.checkpoint.parquet") in keys, error(keys)

    with And("the latest snapshot returns every id"):
        expect_query_lines(sql=f"SELECT id FROM {source} ORDER BY id", expected=EXPECTED)

    with When("I delete commits 0 and 1, which the checkpoint covers"):
        delete_keys(
            self, [log_key(table, f"{version:020d}.json") for version in (0, 1)]
        )

    with Then("the snapshot is the same"):
        expect_query_lines(sql=f"SELECT id FROM {source} ORDER BY id", expected=EXPECTED)


@TestScenario
@Name("incomplete multi-part checkpoint")
@Requirements(
    RQ_SRS_050_ClickHouse_DeltaLake_Read_Checkpoint("1.0"),
    RQ_SRS_050_ClickHouse_DeltaLake_Protocol_Replay("1.0"),
)
def incomplete_multipart(self):
    """Part 1 of 2 for version 3, with part 2 missing, is ignored."""

    with Given("a table with a classic checkpoint at version 2"):
        table = checkpointed_table(self)
        source = delta_function(self, table.http_url)

    with When("I add only the first part of a two-part checkpoint at version 3"):
        put_object(
            key=log_key(table, f"{3:020d}.checkpoint.{1:010d}.{2:010d}.parquet"),
            body=b"not a parquet file",
        )

    with Then("the snapshot still returns every id"):
        expect_query_lines(sql=f"SELECT id FROM {source} ORDER BY id", expected=EXPECTED)


@TestScenario
@Name("missing last checkpoint hint")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_Checkpoint("1.0"))
def missing_last_checkpoint(self):
    """Without _last_checkpoint the reader still finds the latest snapshot."""

    with Given("a table with a checkpoint at version 2"):
        table = checkpointed_table(self)
        source = delta_function(self, table.http_url)

    with When("I delete _last_checkpoint"):
        delete_keys(self, [log_key(table, "_last_checkpoint")])

    with Then("the latest snapshot returns every id"):
        expect_query_lines(sql=f"SELECT id FROM {source} ORDER BY id", expected=EXPECTED)

    with When("I also delete commits 0 and 1"):
        delete_keys(
            self, [log_key(table, f"{version:020d}.json") for version in (0, 1)]
        )

    with Then("the checkpoint is found by listing and the snapshot is the same"):
        expect_query_lines(sql=f"SELECT id FROM {source} ORDER BY id", expected=EXPECTED)


@TestFeature
@Name("delta checkpoint")
def feature(self):
    """Delta checkpoints."""
    Scenario(test=classic_checkpoint)()
    Scenario(test=incomplete_multipart)()
    Scenario(test=missing_last_checkpoint)()
