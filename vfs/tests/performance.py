#!/usr/bin/env python3
import time

from testflows.core import *

from vfs.tests.steps import *
from vfs.requirements import *


@TestStep(When)
def insert_data_time(self, node, table_name, number_of_mb, start=0):
    """Insert and measure the elapsed time."""
    values = ",".join(
        f"({x})"
        for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
    )
    start_time = time.time()
    node.query(f"INSERT INTO {table_name} VALUES {values}")
    end_time = time.time()
    return end_time - start_time


@TestScenario
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Performance("1.0"))
def performance_insert(self):
    """
    Compare insert performance using object storage vfs and not using vfs.
    """
    nodes = self.context.ch_nodes

    table_name = "no_vfs_insert"
    with When("I create a replicated table on each node"):
        replicated_table_cluster(
            table_name=table_name,
            columns="d UInt64",
        )

    with And("I add data to the table and save the time taken"):
        no_vfs_time = insert_data_time(
            node=nodes[0], table_name=table_name, number_of_mb=20
        )
        metric("no_vfs", units="seconds", value=str(no_vfs_time))

    with Given("I enable VFS"):
        enable_vfs()

    table_name = "allow_vfs_insert"
    with When("I create a replicated table on each node"):
        replicated_table_cluster(
            table_name=table_name,
            columns="d UInt64",
        )

    with And("I add data to the table and save the time taken"):
        allow_vfs_time = insert_data_time(
            node=nodes[0], table_name=table_name, number_of_mb=20
        )
        metric("with_vfs", units="seconds", value=str(allow_vfs_time))

    with Finally("I print the difference in time taken"):
        metric(
            "percentage_increase",
            units="%",
            value=str(((allow_vfs_time - no_vfs_time) / no_vfs_time) * 100),
        )


@TestScenario
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Performance("1.0"))
def performance_select(self):
    """Compare select performance using object storage vfs and not using vfs."""
    nodes = self.context.ch_nodes

    try:
        table_name = "no_vfs_select"
        with When("I create a replicated table on each node"):
            replicated_table_cluster(
                table_name=table_name,
                columns="d UInt64",
            )

        with And("I add 20 Mb of data to the table"):
            insert_data_time(node=nodes[0], table_name=table_name, number_of_mb=20)

        with Then("I sync the replicas"):
            for attempt in retries(timeout=600, delay=5):
                with attempt:
                    nodes[1].query(
                        f"SYSTEM SYNC REPLICA {table_name}",
                        settings=[("receive_timeout", 600)],
                    )

        with Then("I select from the table and save the time taken"):
            start_time = time.time()
            nodes[1].query(
                f"CREATE TABLE vfsSelect Engine = MergeTree() ORDER BY d AS SELECT * FROM {table_name}"
            )
            end_time = time.time()
            no_vfs_time = end_time - start_time
            metric("no_vfs", units="seconds", value=str(no_vfs_time))

    finally:
        with Finally("I drop the tables on each node"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS vfsSelect SYNC")

    try:
        table_name = "allow_vfs_select"
        with Given("I enable VFS"):
            enable_vfs()

        with When("I create a replicated table on each node"):
            replicated_table_cluster(
                table_name=table_name,
                columns="d UInt64",
            )

        with And("I add 20 Mb of data to the table"):
            insert_data_time(node=nodes[0], table_name=table_name, number_of_mb=20)

        with Then("I sync the replicas"):
            for attempt in retries(timeout=600, delay=5):
                with attempt:
                    nodes[1].query(
                        f"SYSTEM SYNC REPLICA {table_name}",
                        settings=[("receive_timeout", 600)],
                    )

        with Then("I select from the table and save the time taken"):
            start_time = time.time()
            nodes[1].query(
                f"CREATE TABLE vfsSelect Engine = MergeTree() ORDER BY d AS SELECT * FROM {table_name}"
            )
            end_time = time.time()
            allow_vfs_time = end_time - start_time
            metric("with_vfs", units="seconds", value=str(allow_vfs_time))

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS vfsSelect SYNC")

    with Finally("I print the difference in time taken"):
        metric(
            "percentage_increase",
            units="%",
            value=str(((allow_vfs_time - no_vfs_time) / no_vfs_time) * 100),
        )


@TestScenario
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Performance("1.0"))
def performance_alter(self):
    """Compare alter table performance using object storage vfs and not using vfs."""
    nodes = self.context.ch_nodes

    def insert_data_pair(node, table_name, number_of_mb, start=0):
        values = ",".join(
            f"({x},1)"
            for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
        )
        node.query(f"INSERT INTO {table_name} VALUES {values}")

    try:
        table_name = "no_vfs_alter"
        with When("I create a replicated table on each node"):
            replicated_table_cluster(
                table_name=table_name,
                columns="d UInt64, sign Int8",
            )

        with And("I add 20 Mb of data to the table"):
            insert_data_pair(nodes[0], table_name, 20)

        with Then("I sync the replicas"):
            for attempt in retries(timeout=1200, delay=5):
                with attempt:
                    nodes[1].query(
                        f"SYSTEM SYNC REPLICA {table_name}",
                        settings=[("receive_timeout", 600)],
                        timeout=600,
                    )

        with Then("I alter the table and save the time taken"):
            start_time = time.time()
            nodes[1].query(f"ALTER TABLE {table_name} UPDATE sign = -1 WHERE 1")
            end_time = time.time()
            no_vfs_time = end_time - start_time
            metric("no_vfs", units="seconds", value=str(no_vfs_time))

    finally:
        with Finally("I drop the tables on each node"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS vfsSelect SYNC")

    try:
        table_name = "allow_vfs_alter"
        with Given("I enable VFS"):
            enable_vfs()

        with When("I create a replicated table on each node"):
            replicated_table_cluster(
                table_name=table_name,
                columns="d UInt64, sign Int8",
            )

        with And("I add 20 Mb of data to the table"):
            insert_data_pair(nodes[0], table_name, 20)

        with Then("I sync the replicas"):
            for attempt in retries(timeout=600, delay=5):
                with attempt:
                    nodes[1].query(
                        f"SYSTEM SYNC REPLICA {table_name}",
                        settings=[("receive_timeout", 600)],
                    )

        with Then("I alter the table and save the time taken"):
            start_time = time.time()
            nodes[1].query(f"ALTER TABLE {table_name} UPDATE sign = -1 WHERE sign = 1")
            end_time = time.time()
            allow_vfs_time = end_time - start_time
            metric("with_vfs", units="seconds", value=str(allow_vfs_time))

    finally:
        with Finally("I drop the table on each node"):
            for node in nodes:
                node.query("DROP TABLE IF EXISTS vfsSelect SYNC")

    with Finally("I print the difference in time taken"):
        metric(
            "percentage_increase",
            units="%",
            value=str(((allow_vfs_time - no_vfs_time) / no_vfs_time) * 100),
        )


@TestFeature
@Name("performance")
@Requirements(RQ_SRS038_DiskObjectStorageVFS_Performance("1.0"))
def feature(self):
    """Compare table performance with and without vfs."""

    with Given("I have S3 disks configured"):
        s3_config()

    for scenario in loads(current_module(), Scenario):
        scenario()
