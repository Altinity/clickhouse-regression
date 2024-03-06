#!/usr/bin/env python3
from random import choice

from testflows.core import *
from testflows.combinatorics import CoveringArray

from helpers.tables import create_table, Column
from helpers.datatypes import *

from vfs.tests.steps import *
from vfs.requirements import *

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
    "n_cols": [10, 500, 2000],
    "n_tables": [1, 3],
    "part_type": ["unspecified", "wide", "compact"],
    "fault_probability": [0, 0.2],
}


@TestStep(Given)
def create_test_table(
    self,
    engine: str,
    replicated: bool,
    storage_policy: str,
    n_cols: int,
    part_type: str,
):
    "Create a randomly named table using the provided arguments for testing."
    cluster_name = "replicated_cluster" if replicated else None

    table_name = "table_" + getuid()

    settings = f"storage_policy='{storage_policy}'"

    if part_type == "compact":
        settings += "," + COMPACT_PART_SETTING
    elif part_type == "wide":
        settings += "," + WIDE_PART_SETTING

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


@TestOutline(Scenario)
@Tags("combinatoric")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Combinatoric_Insert("1.0"))
def check_table_combination(
    self,
    engine: str,
    replicated: bool,
    n_cols: int,
    n_tables: int,
    part_type: str,
    fault_probability: float,
):
    """
    Test that the given table parameters create a functional table.
    """
    nodes = self.context.ch_nodes
    storage_policy = "external"
    tables = []
    n_rows = 10000

    for i in range(n_tables):
        with Given(f"table#{i} created with the parameter combination"):
            table = create_test_table(
                engine=engine,
                replicated=replicated,
                n_cols=n_cols,
                storage_policy=storage_policy,
                part_type=part_type,
            )
            tables.append(table)

    insert_node = self.context.node
    query_nodes = nodes if replicated else [self.context.node]

    for i, table in enumerate(tables):
        if replicated:
            insert_node = choice(nodes)

        with Given(f"data is inserted into table#{i} on {insert_node.name}"):
            insert_node.query(
                f"""
                INSERT INTO {table.name} ({','.join([c.name for c in table.columns])})
                SELECT
                    1 AS sign,
                    1 AS ver,
                    * FROM generateRandom('{','.join([c.full_definition() for c in table.columns][2:])}')
                LIMIT {n_rows}
                SETTINGS insert_keeper_fault_injection_probability={fault_probability}
                """
            )

        for node in query_nodes:
            with Then(f"the data in table#{i} on {node.name} can be queried"):
                retry(assert_row_count, timeout=30, delay=0.2)(
                    node=node, table_name=table.name, rows=n_rows
                )


@TestFeature
@Name("create insert")
@Requirements(RQ_SRS_038_DiskObjectStorageVFS_Combinatoric("0.0"))
def feature(self):
    """Test CREATE and INSERT commands with VFS enabled on a variety of table configurations."""

    covering_array_strength = len(table_configurations) if self.context.stress else 2

    with Given("I have S3 disks configured"):
        s3_config()

    with And("VFS is enabled"):
        enable_vfs()

    for table_config in CoveringArray(
        table_configurations, strength=covering_array_strength
    ):
        if table_config["n_cols"] > 500 and table_config["part_type"] != "unspecified":
            continue

        title = ",".join([f"{k}={v}" for k, v in table_config.items()])
        Scenario(title, test=check_table_combination)(**table_config)
