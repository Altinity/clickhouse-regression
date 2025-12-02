from testflows.core import *

from s3.requirements import *
from s3.tests.common import *


@TestOutline
@Requirements(RQ_SRS_015_S3_TableFunction_S3Cluster_HivePartitioning("1.0"))
def s3Cluster_hive(self, cluster_name):
    """Check that s3Cluster function supports hive partitioning."""

    table1_name = "table_" + getuid()
    table2_name = "table_" + getuid()
    table3_name = "table_" + getuid()
    table4_name = "table_" + getuid()
    uri = self.context.uri

    node = current().context.node

    columns = (
        "d UInt64"
        if check_clickhouse_version("<25.6.5")(self)
        and not check_if_antalya_build(self)
        else "d UInt64, date Date, year UInt64"
    )

    with Given("I create a table"):
        if check_clickhouse_version(">=25.6.5")(self) and check_if_antalya_build(self):
            simple_table(node=node, name=table1_name, policy="default", columns=columns)
        else:
            simple_table(node=node, name=table1_name, policy="default")

    if cluster_name is not None:
        with And("I create a second table for comparison"):
            if check_clickhouse_version(">=25.6.5")(self) and check_if_antalya_build(
                self
            ):
                distributed_table_cluster(
                    table_name=table2_name, cluster_name=cluster_name, columns=columns
                )
            else:
                distributed_table_cluster(
                    table_name=table2_name,
                    cluster_name=cluster_name,
                    columns="d UInt64",
                )

        with And("I create a third table for comparison"):
            if check_clickhouse_version(">=25.6.5")(self) and check_if_antalya_build(
                self
            ):
                distributed_table_cluster(
                    table_name=table3_name, cluster_name=cluster_name, columns=columns
                )
            else:
                distributed_table_cluster(
                    table_name=table3_name,
                    cluster_name=cluster_name,
                    columns="d UInt64",
                )
    else:
        with And("I create a second table for comparison"):
            if check_clickhouse_version(">=25.6.5")(self) and check_if_antalya_build(
                self
            ):
                simple_table(
                    node=node, name=table2_name, policy="default", columns=columns
                )
            else:
                simple_table(node=node, name=table2_name, policy="default")

        with And("I create a third table for comparison"):
            if check_clickhouse_version(">=25.6.5")(self) and check_if_antalya_build(
                self
            ):
                simple_table(
                    node=node, name=table3_name, policy="default", columns=columns
                )
            else:
                simple_table(node=node, name=table3_name, policy="default")

    with And(f"I store simple data in the first table {table1_name}"):
        if check_clickhouse_version(">=25.6.5")(self) and check_if_antalya_build(self):
            node.query(
                f"INSERT INTO {table1_name} (d, date, year) select number, '2000-01-01'::Date, 2000 from numbers(1000000)"
            )
        else:
            node.query(f"INSERT INTO {table1_name} select number from numbers(1000000)")

    with When(
        f"I export the data to S3 using the table function using different dates"
    ):
        for i in range(25):
            if check_clickhouse_version(">=25.6.5")(self) and check_if_antalya_build(
                self
            ):
                insert_to_s3_function(
                    filename=f"date=2000-01-{'0' if i < 9 else ''}{i+1}/hive_{cluster_name}.csv",
                    table_name=table1_name,
                    columns=columns,
                )
            else:
                insert_to_s3_function(
                    filename=f"date=2000-01-{'0' if i < 9 else ''}{i+1}/hive_{cluster_name}.csv",
                    table_name=table1_name,
                )

    if cluster_name is not None:
        with And("I download data for the first date from s3 minio and time it"):
            started = time.time()
            if check_clickhouse_version(">=25.6.5")(self) and check_if_antalya_build(
                self
            ):
                node.query(
                    f"INSERT INTO {table2_name} (d, date, year) SELECT count(*), '2000-01-01'::Date, 2000 FROM "
                    f"s3Cluster('{cluster_name}','{uri}date=2000-01-01/hive_{cluster_name}.csv', "
                    f"'minio_user', 'minio123', 'CSVWithNames', '{columns}')",
                    settings=[("use_hive_partitioning", 1)],
                )
            else:
                node.query(
                    f"INSERT INTO {table2_name} SELECT count(*) FROM "
                    f"s3Cluster('{cluster_name}','{uri}date=2000-01-01/hive_{cluster_name}.csv', "
                    f"'minio_user', 'minio123', 'CSVWithNames', 'd UInt64')",
                    settings=[("use_hive_partitioning", 1)],
                )

            time_downloading_part_of_the_data = time.time() - started

        with And(
            "I download data for the first date from s3 minio using hive partitioning and time it"
        ):
            started = time.time()
            if check_clickhouse_version(">=25.6.5")(self) and check_if_antalya_build(
                self
            ):
                node.query(
                    f"INSERT INTO {table3_name} (d, date, year) SELECT count(*), '2000-01-01'::Date, 2000 FROM "
                    f"s3Cluster('{cluster_name}','{uri}date=2000-01-*/hive_{cluster_name}.csv', "
                    f"'minio_user', 'minio123', 'CSVWithNames', '{columns}') WHERE date='2000-01-01'",
                    settings=[("use_hive_partitioning", 1)],
                )
            else:
                node.query(
                    f"INSERT INTO {table3_name} SELECT count(*) FROM "
                    f"s3Cluster('{cluster_name}','{uri}date=2000-01-*/hive_{cluster_name}.csv', "
                    f"'minio_user', 'minio123', 'CSVWithNames', 'd UInt64') WHERE date='2000-01-01'",
                    settings=[("use_hive_partitioning", 1)],
                )

            time_downloading_part_of_the_data_with_hive = time.time() - started

    else:
        with And("I download data for the first dates from s3 minio and time it"):
            started = time.time()
            if check_clickhouse_version(">=25.6.5")(self) and check_if_antalya_build(
                self
            ):
                node.query(
                    f"INSERT INTO {table2_name} (d, date, year) SELECT count(*), '2000-01-01'::Date, 2000 FROM "
                    f"s3('{uri}date=2000-01-01/hive_{cluster_name}.csv', "
                    f"'minio_user', 'minio123', 'CSVWithNames', '{columns}')",
                    settings=[("use_hive_partitioning", 1)],
                )
            else:
                node.query(
                    f"INSERT INTO {table2_name} SELECT count(*) FROM "
                    f"s3('{uri}date=2000-01-01/hive_{cluster_name}.csv', "
                    f"'minio_user', 'minio123', 'CSVWithNames', 'd UInt64')",
                    settings=[("use_hive_partitioning", 1)],
                )

            time_downloading_part_of_the_data = time.time() - started

        with And(
            "I download data for the first dates from s3 minio using hive partitioning and time it"
        ):
            started = time.time()
            if check_clickhouse_version(">=25.6.5")(self) and check_if_antalya_build(
                self
            ):
                node.query(
                    f"INSERT INTO {table3_name} (d, date, year) SELECT count(*), '2000-01-01'::Date, 2000 FROM "
                    f"s3('{uri}date=2000-01-*/hive_{cluster_name}.csv', "
                    f"'minio_user', 'minio123', 'CSVWithNames', '{columns}') WHERE date='2000-01-01'",
                    settings=[("use_hive_partitioning", 1)],
                )
            else:
                node.query(
                    f"INSERT INTO {table3_name} SELECT count(*) FROM "
                    f"s3('{uri}date=2000-01-*/hive_{cluster_name}.csv', "
                    f"'minio_user', 'minio123', 'CSVWithNames', 'd UInt64') WHERE date='2000-01-01'",
                    settings=[("use_hive_partitioning", 1)],
                )

            time_downloading_part_of_the_data_with_hive = time.time() - started

    with Then("I check time is similar"):
        debug(time_downloading_part_of_the_data_with_hive)
        debug(time_downloading_part_of_the_data)
        assert (
            time_downloading_part_of_the_data_with_hive
            < time_downloading_part_of_the_data * 5
        ), error()
        assert (
            time_downloading_part_of_the_data
            < time_downloading_part_of_the_data_with_hive * 5
        ), error()


@TestFeature
@Name("hive partitioning")
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

        for cluster_name in cluster_names:
            with Scenario(
                "hive_partitioning_" + cluster_name
                if cluster_name is not None
                else "s3"
            ):
                s3Cluster_hive(cluster_name=cluster_name)
