#!/usr/bin/env python3
from testflows.core import *
from testflows.combinatorics import CoveringArray

from helpers.tables import create_table, Column
from helpers.datatypes import *

from object_storage_vfs.tests.steps import *
from object_storage_vfs.requirements import *

table_configurations = {
    "engine": [
        "MergeTree",
        "ReplacingMergeTree",
        "CollapsingMergeTree",
        "VersionedCollapsingMergeTree",
        "AggregatingMergeTree",
        "SummingMergeTree",
    ],
    "replicated": [True, False],
    "n_cols": [10, 100, 1000, 2000],
    "n_tables": [1, 3],
    "storage_policy": ["external", "tiered"],
}


@TestStep(Given)
def create_test_table(
    self,
    engine: str,
    replicated: bool,
    storage_policy: str,
    n_cols: int,
):
    cluster_name = "replicated_cluster" if replicated else None

    table_name = "table_" + getuid()

    settings = f"storage_policy='{storage_policy}', allow_object_storage_vfs=1"

    columns = [
        Column(name="sign", datatype=Int8()),
        Column(name="ver", datatype=UInt16()),
    ]

    columns += [Column(name=f"val{i}", datatype=UInt16()) for i in range(n_cols)]

    order_by = "(val0, val1, val2)"

    partition_by = "(val0 % 4)"

    engine_args = []
    engine_str = engine
    if replicated:
        engine_str = "Replicated" + engine
        engine_args += [f"'/clickhouse/tables/{table_name}'", "'{replica}'"]

    if "Collapsing" in engine:
        engine_args.append("sign")

    if "Versioned" in engine:
        engine_args.append("ver")

    if engine_args:
        engine_str += f"({', '.join(engine_args)})"

    yield create_table(
        engine=engine_str,
        name=table_name,
        cluster=cluster_name,
        columns=columns,
        order_by=order_by,
        partition_by=partition_by,
        query_settings=settings,
        drop_sync=True,
    )


@TestOutline(Combination)
def check_table_combination(
    self,
    engine: str,
    replicated: bool,
    n_cols: int,
    n_tables: int,
    storage_policy: str,
):
    node = self.context.node
    tables = []

    for i in range(n_tables):
        with Given(f"table#{i} created with the parameter combination"):
            table = create_test_table(
                engine=engine,
                replicated=replicated,
                n_cols=n_cols,
                storage_policy=storage_policy,
            )
            tables.append(table)

    for i, table in enumerate(tables):
        with Given(f"data is inserted into table#{i}"):
            n_rows = 10000

            node.query(
                f"""
                INSERT INTO {table.name} ({','.join([c.name for c in table.columns])})
                SELECT
                    1 AS sign,
                    1 AS ver,
                    * FROM generateRandom('{','.join([c.full_definition() for c in table.columns][2:])}')
                LIMIT {n_rows}
                """
            )

        with Then(f"the data in table#{i} can be queried"):
            assert_row_count(node=node, table_name=table.name, rows=n_rows)


@TestScenario
@Name("create table")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Combinatoric("0.0"))
def table_combinations(self):
    for table_config in CoveringArray(table_configurations, strength=2):
        title = ",".join([f"{k}={v}" for k, v in table_config.items()])
        Combination(title, test=check_table_combination)(**table_config)


@TestFeature
@Name("combinatoric")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS("1.0"))
def feature(self):
    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()