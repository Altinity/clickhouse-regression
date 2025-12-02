from testflows.core import *

from s3.requirements import *
from s3.tests.common import *


@TestOutline
@Requirements(RQ_SRS_015_S3_TableFunction_S3Cluster_remote("1.0"))
def s3Cluster_remote(self, cluster_name):
    """Check that s3Cluster function supports remote calls."""
    table1_name = "table_" + getuid()
    table2_name = "table_" + getuid()
    uri = self.context.uri

    node = current().context.node
    expected = "427"

    with Given("I create a table"):
        simple_table(node=node, name=table1_name, policy="default")

    if cluster_name is not None:
        with And("I create a second table for comparison"):
            distributed_table_cluster(
                table_name=table2_name, cluster_name=cluster_name, columns="d UInt64"
            )
    else:
        with And("I create a second table for comparison"):
            simple_table(node=node, name=table2_name, policy="default")

    with And(f"I store simple data in the first table {table1_name}"):
        node.query(f"INSERT INTO {table1_name} VALUES (427)")

    with When(f"I export the data to S3 using the table function"):
        insert_to_s3_function(
            filename=f"remote_{cluster_name}.csv", table_name=table1_name
        )

    if cluster_name is not None:
        with And("I download data from s3 minio using clickhouse1 as remote_host"):
            node.query(
                f"INSERT INTO {table2_name} SELECT * FROM "
                f"remote('clickhouse1', s3Cluster('{cluster_name}','{uri}remote_{cluster_name}.csv', 'minio_user', 'minio123', 'CSVWithNames', 'd UInt64'))"
            )
    else:
        with And("I download data from s3 minio using clickhouse1 as remote_host"):
            node.query(
                f"INSERT INTO {table2_name} SELECT * FROM "
                f"remote('clickhouse1', s3('{uri}remote_{cluster_name}.csv', 'minio_user', 'minio123', 'CSVWithNames', 'd UInt64'))"
            )

    with Then(
        f"""I check that a simple SELECT * query on the second table
                    {table2_name} returns matching data on the second node"""
    ):
        for attempt in retries(timeout=10, delay=1):
            with attempt:
                r = (
                    self.context.cluster.node("clickhouse1")
                    .query(f"SELECT * FROM {table2_name} FORMAT CSV")
                    .output.strip()
                )
                assert r == expected, error()

    if cluster_name is not None:
        with When(
            "I download data from s3 minio using clickhouse2 as remote_host using s3Cluster function"
        ):
            node.query(
                f"INSERT INTO {table2_name} SELECT * FROM "
                f"remote('clickhouse2', s3Cluster('{cluster_name}','{uri}remote_{cluster_name}.csv', 'minio_user', 'minio123', 'CSVWithNames', 'd UInt64'))"
            )
    else:
        with When(
            "I download data from s3 minio using clickhouse2 as remote_host using s3 function"
        ):
            node.query(
                f"INSERT INTO {table2_name} SELECT * FROM "
                f"remote('clickhouse2', s3('{uri}remote_{cluster_name}.csv', 'minio_user', 'minio123', 'CSVWithNames', 'd UInt64'))"
            )

    with Then(
        f"""I check that a simple SELECT * query on the second table
                    {table2_name} returns matching data on the second node"""
    ):
        for attempt in retries(timeout=10, delay=1):
            with attempt:
                r = (
                    self.context.cluster.node("clickhouse1")
                    .query(f"SELECT * FROM {table2_name} FORMAT CSV")
                    .output.strip()
                )
                assert r == expected + "\n" + expected, error()


@TestFeature
@Name("remote s3 function call")
def minio(self, uri, bucket_prefix):
    """Check that s3Cluster function perform correctly."""

    with Given("I update the config to have s3 and local disks"):
        default_s3_disk_and_volume(
            uri=uri, disk_name="minio", policy_name="minio_external"
        )

    with Given("a temporary s3 path"):
        temp_s3_path = temporary_bucket_path(
            bucket_prefix=f"{bucket_prefix}/table_function"
        )

        self.context.uri = f"{uri}table_function/{temp_s3_path}/"
        self.context.bucket_path = f"{bucket_prefix}/table_function/{temp_s3_path}"

    with Given("I add S3 credentials configuration"):
        named_s3_credentials(
            access_key_id=self.context.access_key_id,
            secret_access_key=self.context.secret_access_key,
            restart=True,
        )

    with allow_s3_truncate(self.context.node):
        cluster_names = {None}.union(self.context.clusters)
        debug(cluster_names)
        for cluster_name in cluster_names:
            with Scenario(
                "remote_call_" + cluster_name if cluster_name is not None else "s3"
            ):
                s3Cluster_remote(cluster_name=cluster_name)
