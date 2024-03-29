#!/usr/bin/env python3
import random

from testflows.core import *

from alter_stress.tests.steps import interrupt_network, interrupt_node
from ssl_server.tests.zookeeper.steps import add_zookeeper_config_file

from vfs.tests.steps import *
from vfs.requirements import *


@TestScenario
@Requirements(
    RQ_SRS038_DiskObjectStorageVFS_System_AddKeeper("0.0"),
    RQ_SRS038_DiskObjectStorageVFS_System_RemoveKeeper("0.0"),
)
def stop_zookeeper(self):
    nodes = self.context.ch_nodes
    insert_rows = 100000
    n_inserts = 12
    fault_probability = 0

    with interrupt_node(random.choice(self.context.zk_nodes)):
        for attempt in retries(timeout=120, delay=5):
            with attempt:
                with Given("a table is created"):
                    _, table_name = replicated_table_cluster(
                        storage_policy="external_vfs",
                    )

    with interrupt_node(random.choice(self.context.zk_nodes)):
        with Given("data is inserted"):
            retry(insert_random, timeout=120, delay=5)(
                node=random.choice(nodes),
                table_name=table_name,
                rows=insert_rows,
                settings=f"insert_keeper_fault_injection_probability={fault_probability}",
            )
            for _ in range(n_inserts - 1):
                insert_random(
                    node=random.choice(nodes),
                    table_name=table_name,
                    rows=insert_rows,
                    settings=f"insert_keeper_fault_injection_probability={fault_probability}",
                )

    with interrupt_node(self.context.zk_nodes[0]):
        with interrupt_node(self.context.zk_nodes[1]):
            with interrupt_node(self.context.zk_nodes[2]):
                with Given("I trigger merges"):
                    for node in nodes:
                        optimize(node=node, table_name=table_name, final=False)

    with interrupt_node(random.choice(self.context.zk_nodes)):
        with Then("I check that tables are consistent"):
            for node in nodes:
                retry(assert_row_count, timeout=120, delay=5)(
                    node=node, table_name=table_name, rows=insert_rows * n_inserts
                )


@TestScenario
@Tags("sanity")
@Requirements(RQ_SRS038_DiskObjectStorageVFS_System_Delete("1.0"))
def delete(self):
    """
    Check that when a table is dropped, data in S3 is cleaned up.
    """
    bucket_name = self.context.bucket_name
    bucket_path = self.context.bucket_path
    table_name = "vfs_deleting_replicas"
    nodes = self.context.ch_nodes[:2]
    columns = "d UInt64"

    with Given("I get the size of the s3 bucket before adding data"):
        size_empty = get_stable_bucket_size(
            name=bucket_name,
            prefix=bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )

    with Given("I have a replicated table with vfs storage"):
        for node in nodes:
            create_one_replica(
                node=node,
                table_name=table_name,
                columns=columns,
                storage_policy="external_vfs",
            )

    with And("I add data to the table on the first node"):
        insert_random(
            node=nodes[0], table_name=table_name, columns=columns, rows=1000000
        )

    with And("I wait for the second node to sync"):
        sync_replica(node=nodes[1], table_name=table_name, timeout=10)

    with And("I check the row count on the second node"):
        assert_row_count(node=nodes[1], table_name=table_name, rows=1000000)

    with When("I check how much data was added to the s3 bucket"):
        size_after_insert = get_bucket_size(
            name=bucket_name,
            prefix=bucket_path,
            minio_enabled=self.context.minio_enabled,
            access_key=self.context.secret_access_key,
            key_id=self.context.access_key_id,
        )
        assert size_after_insert > size_empty, error()

    with When("I drop the table on the second node"):
        delete_one_replica(node=nodes[1], table_name=table_name)

    with Then("The size of the s3 bucket should be the same"):
        check_stable_bucket_size(
            name=bucket_name,
            prefix=bucket_path,
            expected_size=size_after_insert,
            tolerance=500,
            minio_enabled=self.context.minio_enabled,
        )

    with And("I check the row count on the first node"):
        assert_row_count(node=nodes[0], table_name=table_name, rows=1000000)

    with When("I drop the table on the first node"):
        delete_one_replica(node=nodes[0], table_name=table_name)

    with Then(
        "The size of the s3 bucket should be very close to the size before adding any data"
    ):
        check_stable_bucket_size(
            name=bucket_name,
            prefix=bucket_path,
            expected_size=size_empty,
            tolerance=15,
            minio_enabled=self.context.minio_enabled,
        )


@TestScenario
@Requirements(RQ_SRS038_DiskObjectStorageVFS_System_CompactWideParts("1.0"))
def wide_parts(self):
    """Check that data can be stored in S3 using only wide data parts."""
    name = "table_" + getuid()
    part_types = None
    node = current().context.node
    value = "427"

    try:
        with Given(
            f"""I create table using S3 storage policy external_vfs,
                    min_bytes_for_wide_parts set to 0"""
        ):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d
                SETTINGS storage_policy='external_vfs',
                min_bytes_for_wide_part=0
            """
            )

        with When("I store simple data in the table"):
            node.query(f"INSERT INTO {name} VALUES ({value})")

        with And("I get the part types for the data added in this table"):
            part_types = node.query(
                f"SELECT part_type FROM system.parts WHERE table = '{name}'"
            ).output.splitlines()

        with Then("The part type should be Wide"):
            for _type in part_types:
                assert _type == "Wide", error()

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestScenario
@Requirements(RQ_SRS038_DiskObjectStorageVFS_System_CompactWideParts("1.0"))
def compact_parts(self):
    """Check that data can be stored in S3 using only compact data parts."""
    name = "table_" + getuid()
    part_types = None
    node = current().context.node
    value = "427"

    try:
        with Given(
            f"""I create table using S3 storage policy external_vfs,
                    min_bytes_for_wide_parts set to a very large value"""
        ):
            node.query(
                f"""
                CREATE TABLE {name} (
                    d UInt64
                ) ENGINE = MergeTree()
                ORDER BY d
                SETTINGS storage_policy='external_vfs',
                min_bytes_for_wide_part=100000
            """
            )

        with When("I store simple data in the table, stored as compact parts"):
            node.query(f"INSERT INTO {name} VALUES ({value})")

        with And("I get the part types for the data added in this table"):
            part_types = node.query(
                f"SELECT part_type FROM system.parts WHERE table = '{name}'"
            ).output.splitlines()

        with Then("The part type should be Compact"):
            for _type in part_types:
                assert _type == "Compact", error()

    finally:
        with Finally("I drop the table"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestStep
def get_active_part_count(self, node, table_name):
    """Get the number of active parts for a table."""
    r = node.query(f"SELECT sum(active) FROM system.parts where table='{table_name}'")
    return int(r.output)


@TestOutline(Scenario)
@Tags("long", "combinatoric")
@Requirements(RQ_SRS038_DiskObjectStorageVFS_System_Optimize("0.0"))
@Examples("table_settings", [[None], [WIDE_PART_SETTING], [COMPACT_PART_SETTING]])
def optimize_parts(self, table_settings):
    """Check that OPTIMIZE works as expected on VFS."""

    table_name = "opt_table_" + getuid()
    nodes = self.context.ch_nodes
    n_inserts = 3000
    insert_size = 1000

    with Given("I have a vfs table"):
        replicated_table_cluster(
            table_name=table_name,
            storage_policy="external_vfs",
            settings=table_settings,
        )

    with And("I perform many inserts"):
        for _ in range(n_inserts):
            By(test=insert_random, parallel=True)(
                node=random.choice(nodes), table_name=table_name, rows=insert_size
            )
        join()

    with When("Check the number of active parts"):
        initial_part_count = get_active_part_count(node=nodes[0], table_name=table_name)

    with And("I perform OPTIMIZE"):
        optimize(node=nodes[0], table_name=table_name, final=False)

    with Then("There should be fewer active parts"):
        for attempt in retries(timeout=15, delay=1):
            with attempt:
                optimized_part_count = get_active_part_count(
                    node=nodes[0], table_name=table_name
                )
                assert optimized_part_count < initial_part_count, error()

    with When("I perform OPTIMIZE FINAL"):
        optimize(node=nodes[0], table_name=table_name, final=True)

    with Then("There should be fewer active parts"):
        for attempt in retries(timeout=60, delay=1):
            with attempt:
                final_part_count = get_active_part_count(
                    node=nodes[0], table_name=table_name
                )
                assert final_part_count < optimized_part_count, error()

    # ClickHouse does not actually guarantee that the below will happen in finite time
    # with Then("there should be only one active part"):
    #     assert final_part_count == 1, error()

    with And("there should still be the same amount of data"):
        for attempt in retries(timeout=60, delay=1):
            with attempt:
                assert_row_count(
                    node=nodes[0], table_name=table_name, rows=n_inserts * insert_size
                )


@TestScenario
@Tags("sanity")
@Requirements(RQ_SRS038_DiskObjectStorageVFS_System_Events("1.0"))
def vfs_events(self):
    """Check that vfs events are created."""
    node = self.context.node
    table_name = "vfs_events"
    insert_size = 10_000_000

    vfs_events = [
        "VFSGcRunsCompleted",
        "VFSGcRunsException",
        "VFSGcRunsSkipped",
        "VFSGcTotalSeconds",
        "VFSGcCumulativeSnapshotBytesRead",
        "VFSGcCumulativeLogItemsRead",
    ]

    with Given("I enable vfs with small vfs_gc_sleep_ms"):
        enable_vfs(disk_names=["external"], vfs_gc_sleep_ms=100)

    with Given("I have a vfs table"):
        replicated_table_cluster(
            table_name=table_name,
            storage_policy="external",
        )

    with When("I make two inserts"):
        insert_random(node=node, table_name=table_name, rows=insert_size)
        insert_random(node=node, table_name=table_name, rows=insert_size)

    with And("I disable the network to trigger exceptions"):
        cluster = self.context.cluster
        with interrupt_network(cluster, node, "vfs"):
            time.sleep(2)

    with And("I wait for the parts to merge"):
        optimize(node=node, table_name=table_name, final=True)

    with When("I query for vfs events"):
        r = node.query("SELECT event FROM system.events WHERE event like 'VFS%'")

    for event in vfs_events:
        with Check(event):
            with Then("I check that the event exists"):
                assert event in r.output, error()


@TestScenario
@Requirements(
    RQ_SRS038_DiskObjectStorageVFS_System_ConnectionInterruption_FaultInjection("0.0")
)
def fault_injection(self):
    """Test that ClickHouse is robust against injected faults."""
    nodes = self.context.ch_nodes
    table_name = "fault_injection"
    rows_per_insert = 5000
    insert_rounds = 5
    fault_probability = 0.3

    with Given("I have a replicated vfs table"):
        replicated_table_cluster(
            table_name=table_name,
            storage_policy="external_vfs",
            columns="d UInt64",
        )

    with When(
        f"I perform inserts with insert_keeper_fault_injection_probability={fault_probability}"
    ):
        for _ in range(insert_rounds):
            for node in nodes:
                with By(f"Inserting {rows_per_insert} rows on {node.name}"):
                    insert_random(
                        node=node,
                        table_name=table_name,
                        columns="d UInt64",
                        rows=rows_per_insert,
                        no_checks=True,
                        settings=f"insert_keeper_fault_injection_probability={fault_probability}",
                    )

    with Then("I check the number of rows in the table"):
        retry(assert_row_count, timeout=5, delay=1)(
            node=nodes[0],
            table_name=table_name,
            rows=(rows_per_insert * insert_rounds * len(nodes)),
        )


@TestOutline(Scenario)
@Examples(
    "settings, check_inserts",
    [
        [{"syncLimit": "1"}, True],
        [{"tickTime": "30"}, True],
        [{"maxSessionTimeout": "2000"}, True],
        [{"syncLimit": "1", "tickTime": "30"}, True],
        [{"syncLimit": "1", "tickTime": "30", "maxSessionTimeout": "2000"}, True],
    ],
)
def zookeeper_timeout(self, settings, check_inserts=True):
    """Check for data loss with session timeouts"""
    nodes = self.context.ch_nodes
    rows_per_insert = 5000
    insert_rounds = 5

    with Given("a replicated vfs table"):
        _, table_name = replicated_table_cluster(
            storage_policy="external_vfs",
        )

    with When("I perform inserts"):
        for _ in range(insert_rounds):
            for node in nodes:
                with By(f"Inserting {rows_per_insert} rows on {node.name}"):
                    insert_random(
                        node=node,
                        table_name=table_name,
                        rows=rows_per_insert,
                        no_checks=False,
                    )

    with Given("short timeout config for zookeeper"):
        for node in self.context.zk_nodes:
            add_zookeeper_config_file(entries=settings, restart=True, node=node)

    with When("I perform inserts"):
        for _ in range(insert_rounds):
            for node in nodes:
                with By(f"Inserting {rows_per_insert} rows on {node.name}"):
                    insert_random(
                        node=node,
                        table_name=table_name,
                        rows=rows_per_insert,
                        no_checks=(not check_inserts),
                    )

    with And("I optimize"):
        for node in nodes:
            optimize(node=node, table_name=table_name)

    with Then("I check the number of rows in the table"):
        check_consistency(nodes=nodes, table_name=table_name)

        if check_inserts:
            assert_row_count(
                node=nodes[0],
                table_name=table_name,
                rows=(rows_per_insert * insert_rounds * len(nodes) * 2) ,
            )


@TestFeature
@Name("system")
def feature(self):
    """Test cluster functionality."""

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
