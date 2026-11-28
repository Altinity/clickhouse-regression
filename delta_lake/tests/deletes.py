"""Deletion vectors and file removal.

``deltalake`` rewrites files instead of writing deletion vectors, so the
log is hand-written. One file holds ids 0 to 9, and the vector marks rows
1, 3, 5, and 7. Every reader must return the six live rows.
"""

import pyarrow as pa
from testflows.core import *

from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Read_DeletionVectors,
    RQ_SRS_050_ClickHouse_DeltaLake_Read_Snapshot,
)
from delta_lake.tests.steps import (
    column,
    create_database,
    create_schema,
    register_delta_table,
)
from delta_lake.tests.steps.access import create_engine_table, function_call
from delta_lake.tests.steps.log import (
    add,
    commit,
    create_hand_table,
    field,
    inline_dv,
    metadata,
    path_dv,
    protocol,
    remove,
    upload_parquet,
    uuid_dv,
)
from delta_lake.tests.steps.query import (
    catalog_source,
    delta_function,
    expect_error,
    expect_query_lines,
    try_query,
)

DATA = pa.table({"id": pa.array(list(range(10)), pa.int64())})
DELETED = [1, 3, 5, 7]
LIVE = ["0", "2", "4", "6", "8", "9"]
COLUMNS = (column("id", "LONG", "bigint", "long"),)
DV_PROTOCOL = protocol(3, 7, ["deletionVectors"], ["deletionVectors"])
DV_CONFIG = {"delta.enableDeletionVectors": "true"}
CLUSTER = "test_cluster_two_shards_localhost"


def dv_table(self, make_dv):
    """A registered hand table whose only file has the vector ``make_dv`` returns."""
    table = create_hand_table()
    create_schema(name=table.namespace)
    name, size = upload_parquet(table=table, name="part-0.parquet", data=DATA)
    commit(
        table=table,
        version=0,
        actions=[
            DV_PROTOCOL,
            metadata([field("id", "long")], configuration=DV_CONFIG),
            add(name, size, deletion_vector=make_dv(table)),
        ],
    )
    register_delta_table(table=table, columns=COLUMNS)
    return table


def readers(self, table):
    """deltaLake, ENGINE = DeltaLake, deltaLakeCluster, and Unity."""
    access_key = self.context.rustfs_access_key
    secret_key = self.context.rustfs_secret_key
    sources = [delta_function(self, table.http_url)]
    with By("attaching an engine table"):
        sources.append(create_engine_table(url=table.http_url))
    sources.append(
        function_call(
            "deltaLakeCluster",
            table.http_url,
            access_key,
            secret_key,
            cluster=CLUSTER,
        )
    )
    with By("opening Unity"):
        sources.append(catalog_source(create_database(), table))
    return sources


def check_live_rows(self, table):
    for source in readers(self, table):
        with Then(f"{source} returns only the live rows"):
            expect_query_lines(
                sql=f"SELECT id FROM {source} ORDER BY id", expected=LIVE
            )

        with And("count() is the number of live rows"):
            expect_query_lines(
                sql=f"SELECT count() FROM {source}", expected=[str(len(LIVE))]
            )


@TestScenario
@Name("inline vector")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_DeletionVectors("1.0"))
def inline_vector(self):
    """storageType i: the vector is Z85 text in the log."""
    with Given("a table with an inline deletion vector"):
        table = dv_table(self, lambda table: inline_dv(rows=DELETED))

    check_live_rows(self, table)


@TestScenario
@Name("uuid vector")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_DeletionVectors("1.0"))
def uuid_vector(self):
    """storageType u: the vector is a file named by UUID under the table."""
    with Given("a table with a UUID-named deletion vector file"):
        table = dv_table(self, lambda table: uuid_dv(table=table, rows=DELETED))

    check_live_rows(self, table)


@TestScenario
@Name("path vector")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_DeletionVectors("1.0"))
def path_vector(self):
    """storageType p: the vector is a file at an absolute path."""
    with Given("a table with a deletion vector at an absolute path"):
        table = dv_table(self, lambda table: path_dv(table=table, rows=DELETED))

    check_live_rows(self, table)


@TestScenario
@Name("unknown storage type")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_DeletionVectors("1.0"))
def unknown_storage_type(self):
    """A storageType other than u, i, or p fails the query."""

    def bad_dv(table):
        dv = inline_dv(rows=DELETED)
        dv["storageType"] = "x"
        return dv

    with Given("a table whose deletion vector has storageType x"):
        table = dv_table(self, bad_dv)

    with When("I read it"):
        result = try_query(
            sql=f"SELECT id FROM {delta_function(self, table.http_url)} "
            "ORDER BY id FORMAT TabSeparated"
        )

    with Then("the read fails instead of returning rows"):
        expect_error(result=result, message="deletion vector")


@TestScenario
@Name("remove action")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Read_Snapshot("1.0"))
def remove_action(self):
    """A remove action drops every row of that file."""

    with Given("a hand-written table with two files"):
        table = create_hand_table()
        first, first_size = upload_parquet(
            table=table,
            name="part-0.parquet",
            data=pa.table({"id": pa.array([1, 2], pa.int64())}),
        )
        second, second_size = upload_parquet(
            table=table,
            name="part-1.parquet",
            data=pa.table({"id": pa.array([3], pa.int64())}),
        )
        commit(
            table=table,
            version=0,
            actions=[
                protocol(),
                metadata([field("id", "long")]),
                add(first, first_size),
                add(second, second_size),
            ],
        )

    with When("version 1 removes the first file"):
        commit(table=table, version=1, actions=[remove(first, first_size)])

    with Then("only the second file's row comes back"):
        source = delta_function(self, table.http_url)
        expect_query_lines(sql=f"SELECT id FROM {source} ORDER BY id", expected=["3"])
        expect_query_lines(sql=f"SELECT count() FROM {source}", expected=["1"])


@TestFeature
@Name("delta deletes")
def feature(self):
    """Delta deletion vectors and removed files."""
    Scenario(test=inline_vector)()
    Scenario(test=uuid_vector)()
    Scenario(test=path_vector)()
    Scenario(test=unknown_storage_type)()
    Scenario(test=remove_action)()
