#!/usr/bin/env python3
import random

from testflows.core import *
from testflows.combinatorics import CoveringArray

from helpers.common import getuid
from helpers.tables import create_table, Column
from helpers.datatypes import *

from s3.requirements import *
from s3.tests.common import default_s3_disk_and_volume, assert_row_count


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
}

WIDE_PART_SETTING = "min_bytes_for_wide_part=0"
COMPACT_PART_SETTING = "min_bytes_for_wide_part=1000000000000"


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
        settings=[("distributed_ddl_task_timeout ", 600)],
        drop_sync=True,
    )


def build_insert_query(table, n_cols: int, n_rows: int, table_index: int):
    """
    Build an INSERT query that generates unique ORDER BY keys to avoid
    deduplication issues with engines like ReplacingMergeTree, AggregatingMergeTree, etc.

    The ORDER BY is (val0, val1, val2), so we ensure these columns have unique
    combinations by deriving them deterministically from the row number.
    We add table_index offset to ensure uniqueness across multiple tables.
    """
    columns_str = ",".join([c.name for c in table.columns])

    # Generate unique val0, val1, val2 from row number to avoid ORDER BY key collisions
    # Use table_index offset to ensure uniqueness across tables
    offset = table_index * n_rows
    unique_key_cols = f"""
        toUInt16((number + {offset}) % 65536) AS val0,
        toUInt16(intDiv(number + {offset}, 65536) % 65536) AS val1,
        toUInt16(intDiv(number + {offset}, 65536 * 65536) % 65536) AS val2"""

    # Generate random values for remaining columns (val3 onwards)
    if n_cols > 3:
        random_cols = ", " + ", ".join(
            [f"toUInt16(rand() % 65536) AS val{i}" for i in range(3, n_cols)]
        )
    else:
        random_cols = ""

    return f"""
        INSERT INTO {table.name} ({columns_str})
        SELECT
            1 AS sign,
            1 AS ver,
            {unique_key_cols}{random_cols}
        FROM numbers({n_rows})
        """

@TestOutline(Scenario)
@Tags("combinatoric")
def check_table_combination(
    self,
    engine: str,
    replicated: bool,
    n_cols: int,
    n_tables: int,
    part_type: str,
):
    """
    Test that the given table parameters create a functional table.
    """
    nodes = self.context.ch_nodes
    storage_policy = "external"
    tables = []
    insert_size = 3_000_000
    n_rows = insert_size // n_cols

    my_random = random.Random(42)

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
            insert_node = my_random.choice(nodes)

        with Given(f"data is inserted into table#{i} on {insert_node.name}"):
            insert_node.query(
                build_insert_query(table, n_cols, n_rows, table_index=i),
                settings=[("distributed_ddl_task_timeout ", 300)],
                timeout=300,
            )

        for node in query_nodes:
            with Then(f"the data in table#{i} on {node.name} can be queried"):
                retry(assert_row_count, timeout=60, delay=5)(
                    node=node, table_name=table.name, rows=n_rows
                )


@TestFeature
@Name("combinatoric table")
@Requirements(
    RQ_SRS_015_S3_Disk_MergeTree("1.0"),
    RQ_SRS_015_S3_Disk_MergeTree_MergeTree("1.0"),
    RQ_SRS_015_S3_Disk_MergeTree_ReplacingMergeTree("1.0"),
    RQ_SRS_015_S3_Disk_MergeTree_SummingMergeTree("1.0"),
    RQ_SRS_015_S3_Disk_MergeTree_AggregatingMergeTree("1.0"),
    RQ_SRS_015_S3_Disk_MergeTree_CollapsingMergeTree("1.0"),
    RQ_SRS_015_S3_Disk_MergeTree_VersionedCollapsingMergeTree("1.0"),
)
def feature(self, uri):
    """Test CREATE and INSERT commands on a variety of table configurations."""

    self.context.uri = uri

    cluster = self.context.cluster
    self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]

    covering_array_strength = len(table_configurations) if self.context.stress else 2

    with Given("I have S3 disks configured"):
        default_s3_disk_and_volume()

    for table_config in CoveringArray(
        table_configurations, strength=covering_array_strength
    ):
        title = ",".join([f"{k}={v}" for k, v in table_config.items()])
        Scenario(title, test=check_table_combination)(**table_config)
