from testflows.core import *

from s3.tests.common import *
from s3.requirements import *

@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_S3Cluster_remote("1.0"))
def s3Cluster_remote(self):
    """Check that s3Cluster function supports remote calls.
    """
    table1_name = "table_" + getuid()
    table2_name = "table_" + getuid()
    uri = self.context.uri

    node = current().context.node
    expected = "427"
    cluster_name = 'replicated_cluster'

    with Given("I create a table"):
        simple_table(node=node, name=table1_name, policy="default")

    with And("I create a second table for comparison"):
        replicated_table_cluster(table_name=table2_name, storage_policy="default", columns="d UInt64")

    with And(f"I store simple data in the first table {table1_name}"):
        node.query(f"INSERT INTO {table1_name} VALUES (427)")

    with When(f"I export the data to S3 using the table function"):
        insert_to_s3_function(filename=f"remote_{cluster_name}.csv", table_name=table1_name)

    with And("I download data from s3 minio using clickhouse1 as remote_host"):
        node.query(f"INSERT INTO {table2_name} SELECT * FROM "
                   f"remote('clickhouse1', s3Cluster('{cluster_name}','{uri}remote_{cluster_name}.csv', 'minio_user', 'minio123', 'CSVWithNames', 'd UInt64'))")

    with Then(
            f"""I check that a simple SELECT * query on the second table
                    {table2_name} returns matching data on the second node"""
    ):
        r = self.context.cluster.node("clickhouse2").query(f"SELECT * FROM {table2_name} FORMAT CSV").output.strip()
        assert r == expected, error()

    with When("I download data from s3 minio using clickhouse2 as remote_host"):
        node.query(f"INSERT INTO {table2_name} SELECT * FROM "
                   f"remote('clickhouse2', s3Cluster('{cluster_name}','{uri}remote_{cluster_name}.csv', 'minio_user', 'minio123', 'CSVWithNames', 'd UInt64'))")

    with Then(
            f"""I check that a simple SELECT * query on the second table
                    {table2_name} returns matching data on the second node"""
    ):
        r = self.context.cluster.node("clickhouse2").query(f"SELECT * FROM {table2_name} FORMAT CSV").output.strip()
        assert r == expected, error()


@TestScenario
@Requirements(RQ_SRS_015_S3_TableFunction_S3Cluster_HivePartitioning("1.0"))
def s3Cluster_hive(self):
    """Check that s3Cluster function supports hive partitioning.
    """
    table1_name = "table_" + getuid()
    table2_name = "table_" + getuid()
    table3_name = "table_" + getuid()
    uri = self.context.uri

    node = current().context.node
    cluster_name = 'replicated_cluster'

    with Given("I create a table"):
        simple_table(node=node, name=table1_name, policy="default")

    with And("I create a second table for comparison"):
        replicated_table_cluster(table_name=table2_name, storage_policy="default", columns="d UInt64")

    with And("I create a third table for comparison"):
        replicated_table_cluster(table_name=table3_name, storage_policy="default", columns="d UInt64")

    with And(f"I store simple data in the first table {table1_name}"):
        node.query(f"INSERT INTO {table1_name} select number from numbers(1000000)")

    with When(f"I export the data to S3 using the table function using different dates"):
        for i in range(10):
            insert_to_s3_function(filename=f"date=2000-00-0{i}/hive_{cluster_name}.csv", table_name=table1_name)


    with And("I download data for the first date from s3 minio and time it"):
        started = time.time()
        node.query(f"INSERT INTO {table2_name} SELECT * FROM "
                   f"s3Cluster('{cluster_name}','{uri}date=2000-00-00/hive_{cluster_name}.csv', "
                   f"'minio_user', 'minio123', 'CSVWithNames', 'd UInt64')")

        time_downloading_part_of_the_data  = time.time() - started


    with And("I download data for the first date from s3 minio using hive partitioning and time it"):
        started = time.time()
        node.query(f"INSERT INTO {table3_name} SELECT * FROM "
                   f"s3Cluster('{cluster_name}','{uri}date=2000-00-0*/hive_{cluster_name}.csv', "
                   f"'minio_user', 'minio123', 'CSVWithNames', 'd UInt64') WHERE date='2000-00-00'")

        time_downloading_part_of_the_data_with_hive = time.time() - started

    with Then("I check time is similar"):
        assert time_downloading_part_of_the_data_with_hive < time_downloading_part_of_the_data * 2, error()
        assert time_downloading_part_of_the_data < time_downloading_part_of_the_data_with_hive * 2, error()


@TestFeature
@Name("s3Cluster")
def minio(self, uri, bucket_prefix):
    """Check that s3Cluster function perform correctly.
    """

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

    with allow_s3_truncate(self.context.node):
        for scenario in loads(current_module(), Scenario):
            scenario()
