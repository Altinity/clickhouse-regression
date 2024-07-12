#!/usr/bin/env python3
import random

from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product

from helpers.alter import *
from helpers.queries import get_active_partition_ids
from helpers.common import getuid
from s3.tests.common import *


@TestScenario
def create_insert_and_drop(self):
    """Repeatedly create a table, insert data, and drop the table"""

    with Given("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after()

    for iteration in repeats(10, until="fail"):
        with iteration:
            with Given("a table"):
                table_name = f"table_{getuid()}"
                for node in self.context.ch_nodes:
                    replicated_table(
                        node=node, table_name=table_name, columns="a UInt64, b UInt64"
                    )

            with When("I insert data into the table"):
                for node in self.context.ch_nodes:
                    insert_random(
                        node=node,
                        table_name=table_name,
                        columns="a UInt64, b UInt64",
                        rows=100000,
                    )

            with When("I drop the table"):
                for node in self.context.ch_nodes:
                    delete_replica(node=node, table_name=table_name)


@TestScenario
def detach_and_drop(self):
    """Repeatedly detach a part and drop a table"""

    with Given("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after()

    for iteration in repeats(10, until="fail"):
        with iteration:
            with Given("a table"):
                table_name = f"table_{getuid()}"
                replicated_table_cluster(
                    table_name=table_name,
                    columns="a UInt64, b UInt64",
                    partition_by="a % 10",
                )

            with When("I insert data into the table"):
                for node in self.context.ch_nodes:
                    insert_random(
                        node=node,
                        table_name=table_name,
                        columns="a UInt64, b UInt64",
                        rows=100000,
                    )

            with When("I detach a part"):
                for i, node in enumerate(self.context.ch_nodes):
                    alter_table_detach_partition(
                        node=node, table_name=table_name, partition_name=f"{i * 2}"
                    )

            with When("I drop the table"):
                for node in self.context.ch_nodes:
                    delete_replica(node=node, table_name=table_name)


@TestScenario
def freeze_and_drop(self):
    """Repeatedly freeze a part and drop a table"""

    backup_names = []
    table_names = []

    with Given("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after()

    for iteration in repeats(3, until="fail"):
        with iteration:
            with Given("a table"):
                table_name = f"table_{getuid()}"
                table_names.append(table_name)
                replicated_table_cluster(
                    table_name=table_name,
                    columns="a UInt64, b UInt64",
                    partition_by="a % 10",
                )

            with When("I insert data into the table"):
                for node in self.context.ch_nodes:
                    insert_random(
                        node=node,
                        table_name=table_name,
                        columns="a UInt64, b UInt64",
                        rows=100000,
                    )

            with When("I freeze a part"):
                backup_name = f"backup_{getuid()}"
                backup_names.append(backup_name)
                for i, node in enumerate(self.context.ch_nodes):
                    alter_table_freeze_partition_with_name(
                        node=node,
                        table_name=table_name,
                        partition_name=f"{i * 2}",
                        backup_name=backup_name,
                    )

            with When("I drop the table"):
                for node in self.context.ch_nodes:
                    delete_replica(node=node, table_name=table_name)

    with When("I unfreeze all"):
        for backup_name in backup_names:
            for node in self.context.ch_nodes:
                node.query(f"SYSTEM UNFREEZE WITH NAME '{backup_name}'")

    with When("I drop all the restored tables"):
        for table_name in table_names:
            for node in self.context.ch_nodes:
                delete_replica(node=node, table_name=table_name)


@TestScenario
def freeze_drop_and_attach(self):
    """Freeze a part, drop a table, and attach the part back"""

    with Given("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after()

    with Given("two tables"):
        table1_name = f"table_{getuid()}"
        table2_name = f"table_{getuid()}"

        replicated_table_cluster(
            table_name=table1_name,
            columns="a UInt64",
        )
        replicated_table_cluster(
            table_name=table2_name,
            columns="a UInt64",
        )

    with When("I insert data into the first table"):
        standard_inserts(node=self.context.ch_nodes[0], table_name=table1_name)

    with When("I freeze a part"):
        backup_name = f"backup_{getuid()}"
        partition_id = get_active_partition_ids(
            node=self.context.ch_nodes[0], table_name=table1_name
        )[0]
        node = self.context.ch_nodes[0]
        alter_table_freeze_partition_with_name(
            node=node,
            table_name=table1_name,
            partition_name=partition_id,
            backup_name=backup_name,
        )

    with When("I drop the first table"):
        for node in self.context.ch_nodes:
            delete_replica(node=node, table_name=table1_name)

    with When("I attach the part to the second table"):
        node = self.context.ch_nodes[0]
        alter_table_attach_partition_from(
            node=node,
            table_name=table2_name,
            partition_name=partition_id,
            path_to_backup=backup_name,
        )

    with Then("I check the data"):
        node = self.context.ch_nodes[0]
        standard_selects(node=node, table_name=table2_name)

    with When("I unfreeze the part"):
        node = self.context.ch_nodes[0]
        alter_table_unfreeze_partition_with_name(
            node=node,
            table_name=table2_name,
            partition_name=partition_id,
            backup_name=backup_name,
        )

    with When("I unfreeze the part"):
        node = self.context.ch_nodes[0]
        node.query(f"SYSTEM UNFREEZE WITH NAME '{backup_name}'")


@TestFeature
def full_replication(self, uri, bucket_prefix):

    with Given("a temporary s3 path"):
        if self.context.storage == "gcs":
            temp_s3_path = "disk"  # temporary_bucket_path does not support gcs yet
        else:
            temp_s3_path = temporary_bucket_path(bucket_prefix=f"{bucket_prefix}/disk")

        self.context.uri = f"{uri}disk/{temp_s3_path}/"
        self.context.bucket_path = f"{bucket_prefix}/disk/{temp_s3_path}"

    with Given("I have S3 disks configured"):
        default_s3_disk_and_volume()

    for scenario in loads(current_module(), Scenario):
        scenario()


@TestFeature
@FFails(
    {
        ":etach:": (Skip, "detach not enabled with zero copy replication"),
        ":reeze:": (Skip, "freeze not enabled with zero copy replication"),
    }
)
def zero_copy_replication(self, uri, bucket_prefix):

    with Given("a temporary s3 path"):
        if self.context.storage == "gcs":
            temp_s3_path = "disk"  # temporary_bucket_path does not support gcs yet
        else:
            temp_s3_path = temporary_bucket_path(bucket_prefix=f"{bucket_prefix}/disk")

        self.context.uri = f"{uri}disk/{temp_s3_path}/"
        self.context.bucket_path = f"{bucket_prefix}/disk/{temp_s3_path}"

    with And("I have S3 disks configured"):
        default_s3_disk_and_volume()

    with And("I have merge tree configuration set to use zero copy replication"):
        if check_clickhouse_version(">=21.8")(self):
            settings = {"allow_remote_fs_zero_copy_replication": "1"}
        else:
            settings = {"allow_s3_zero_copy_replication": "1"}

        mergetree_config(settings=settings)

    for scenario in loads(current_module(), Scenario):
        scenario()


@TestFeature
@Name("orphans")
def feature(self, uri, bucket_prefix):
    """Tests that trigger orphaned parts and blocks."""

    cluster = self.context.cluster
    self.context.ch_nodes = [cluster.node(n) for n in cluster.nodes["clickhouse"]]

    Feature(test=full_replication)(uri=uri, bucket_prefix=bucket_prefix)
    Feature(test=zero_copy_replication)(uri=uri, bucket_prefix=bucket_prefix)
