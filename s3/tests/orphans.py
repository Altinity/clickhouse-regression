#!/usr/bin/env python3
import random

from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product

from helpers.alter import *
from helpers.queries import get_active_partition_ids, optimize
from helpers.common import getuid
from s3.tests.common import *


list_remote_files_query = """SELECT s3_subpath, s3_size, (ch_remote_path = '') as is_orphan, ch_remote_path, ch_size FROM
(
  SELECT _size as s3_size, regexpExtract(_path, '([a-zA-Z0-9\\-])/(.*)$', 2) AS s3_subpath
  FROM s3('{uri}**', '{access_key_id}', '{secret_access_key}', 'One')
) AS s3
LEFT OUTER JOIN
(
  SELECT remote_path as ch_remote_path, size as ch_size
  FROM clusterAllReplicas('{cluster_name}', system.remote_data_paths)
  WHERE disk_name = '{disk_name}'
) ch
ON s3_subpath = ch_remote_path
ORDER BY s3_subpath INTO OUTFILE '{outfile}' TRUNCATE FORMAT TSV
"""

count_orphans_query = """WITH refs AS (
 SELECT s3_subpath, s3_size, (ch_remote_path = '') as is_orphan, ch_remote_path, ch_size FROM
 (
   SELECT _size as s3_size, regexpExtract(_path, '([a-zA-Z0-9\\-])/(.*)$', 2) AS s3_subpath
   FROM s3('{uri}**', '{access_key_id}', '{secret_access_key}', 'One')
 ) AS s3
 LEFT OUTER JOIN
 (
   SELECT remote_path as ch_remote_path, size as ch_size
   FROM clusterAllReplicas('{cluster_name}', system.remote_data_paths)
   WHERE disk_name = '{disk_name}'
 ) ch
 ON s3_subpath = ch_remote_path
)
SELECT is_orphan, count(), sum(s3_size) FROM refs
GROUP BY is_orphan FORMAT TSV
"""

generate_orphan_rm_commands = """WITH comp AS (
  SELECT s3_subpath, s3_size, (ch_remote_path = '') as is_orphan, ch_remote_path, ch_size FROM
  (
    SELECT _size as s3_size, regexpExtract(_path, '([a-zA-Z0-9\\-])/(.*)$', 2) AS s3_subpath
    FROM s3('{uri}**', '{access_key_id}', '{secret_access_key}', 'One')
  ) AS s3
  LEFT OUTER JOIN
  (
    SELECT remote_path as ch_remote_path, size as ch_size
    FROM clusterAllReplicas('{cluster_name}', system.remote_data_paths) where disk_name = '{disk_name}'
  ) ch
  ON s3_subpath = ch_remote_path
),
's3://{bucket}/' AS s3_endpoint
SELECT '{aws} s3 rm '|| s3_endpoint || s3_subpath AS cmd FROM comp
WHERE is_orphan INTO OUTFILE '{outfile}' TRUNCATE FORMAT TSV"""


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

            with And("I insert more data into the table"):
                for node in self.context.ch_nodes:
                    insert_random(
                        node=node,
                        table_name=table_name,
                        columns="a UInt64, b UInt64",
                        rows=100000,
                    )

            with And("I optimize the table"):
                for node in self.context.ch_nodes:
                    optimize(node=node, table_name=table_name, final=True)

            with When("I drop the table"):
                for node in self.context.ch_nodes:
                    delete_replica(node=node, table_name=table_name, timeout=120)

            with Then("I check for orphans"):
                orphans = check_orphans()

            if orphans == True:
                Scenario(run=remove_orphans)


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

            with Then("I check for orphans"):
                orphans = check_orphans()

            if orphans == True:
                Scenario(run=remove_orphans)


@TestScenario
def freeze_and_drop(self):
    """Repeatedly freeze a part and drop a table"""

    backup_names = []
    table_names = []

    with Given("I get the size of the s3 bucket before adding data"):
        measure_buckets_before_and_after()

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

    with When("I system unfreeze the backup"):
        for backup_name in backup_names:
            for node in self.context.ch_nodes:
                node.query(f"SYSTEM UNFREEZE WITH NAME '{backup_name}'")

    with Then("I check for orphans"):
        orphans = check_orphans()

    if orphans == True:
        Scenario(run=remove_orphans)


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
            partition_by="a % 2",
        )
        replicated_table_cluster(
            table_name=table2_name,
            columns="a UInt64",
            partition_by="a % 2",
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

    with When("I unfreeze the part and attach it to the second table"):
        node = self.context.ch_nodes[0]
        alter_table_unfreeze_partition_with_name(
            node=node,
            table_name=table2_name,
            partition_name=partition_id,
            backup_name=backup_name,
        )

    with Then(
        "I check the data", description="there should be no data from the dropped table"
    ):
        node = self.context.ch_nodes[0]
        assert_row_count(node=node, table_name=table2_name, rows=0)

    with When("I system unfreeze the backup"):
        node = self.context.ch_nodes[0]
        node.query(f"SYSTEM UNFREEZE WITH NAME '{backup_name}'")

    with Then("I check for orphans"):
        orphans = check_orphans()

    if orphans == True:
        Scenario(run=remove_orphans)


@TestStep(When)
def check_orphans(self):
    node = self.context.ch_nodes[0]

    format_args = {
        "uri": self.context.uri,
        "cluster_name": "replicated_cluster",
        "disk_name": "external",
        "access_key_id": self.context.access_key_id,
        "secret_access_key": self.context.secret_access_key,
    }

    with When("I count orphans"):
        r = node.query(count_orphans_query.format(**format_args))

    with Then("I check if there are orphans"):
        for line in r.output.splitlines():
            is_orphan, count, size = line.split()
            if is_orphan == "1" and size != "0":
                return True

    return False


@TestCheck
def remove_orphans(self):

    node = self.context.ch_nodes[0]

    format_args = {
        "uri": self.context.uri,
        "cluster_name": "replicated_cluster",
        "disk_name": "external",
        "access_key_id": self.context.access_key_id,
        "secret_access_key": self.context.secret_access_key,
    }

    with When("I list remote files"):
        node.query(
            list_remote_files_query.format(
                **format_args, outfile="/share/remote_files.tsv"
            )
        )

    with When("I generate rm commands"):
        bucket = self.context.bucket_name
        aws = "aws"
        if self.context.storage == "minio":
            aws = f"aws --endpoint-url http://minio1:9001"

        node.query(
            generate_orphan_rm_commands.format(
                **format_args, outfile="/share/rm_commands.tsv", aws=aws, bucket=bucket
            )
        )

    with Then("I execute the rm commands"):
        self.context.cluster.command(
            "aws",
            f"AWS_ACCESS_KEY_ID={self.context.access_key_id} AWS_SECRET_ACCESS_KEY={self.context.secret_access_key} bash -x /share/rm_commands.tsv",
        )

    with Then("I check for orphans"):
        assert not check_orphans()


@TestFeature
def full_replication(self, uri, bucket_prefix):

    with Given("a temporary s3 path"):
        temp_s3_path = temporary_bucket_path(bucket_prefix=f"{bucket_prefix}/orphans")

        self.context.uri = f"{uri}orphans/{temp_s3_path}/"
        self.context.bucket_path = f"{bucket_prefix}/orphans/{temp_s3_path}"

    with Given("I have S3 disks configured"):
        default_s3_disk_and_volume()

    for scenario in loads(current_module(), Scenario):
        scenario()


@TestFeature
def zero_copy_replication(self, uri, bucket_prefix):

    with Given("a temporary s3 path"):
        temp_s3_path = temporary_bucket_path(bucket_prefix=f"{bucket_prefix}/orphans")

        self.context.uri = f"{uri}orphans/{temp_s3_path}/"
        self.context.bucket_path = f"{bucket_prefix}/orphans/{temp_s3_path}"

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
