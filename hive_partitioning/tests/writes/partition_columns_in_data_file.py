from testflows.core import *
from testflows.combinatorics import product
from hive_partitioning.tests.steps import *
from hive_partitioning.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_PartitionColumnsInDataFile("1.0"),
)
def write_partition_columns_into_files(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Check that ClickHouse support `partition_columns_in_data_file` parameter."""
    if uri is None:
        uri = self.context.uri

    table_name_1 = "write_partition_columns_into_files_1"
    table_name_2 = "write_partition_columns_into_files_2"

    with Given("I create table with partition_columns_in_data_file=0"):
        create_table(
            table_name=table_name_1,
            columns="d String, i Int32",
            partition_by="d",
            engine=f"S3(s3_conn, format = CSV, filename='{table_name_1}/', partition_columns_in_data_file=0, partition_strategy='hive')",
            settings=[("use_hive_partitioning", "1")],
        )
    with And("I create table with partition_columns_in_data_file=1"):
        create_table(
            table_name=table_name_2,
            columns="d String, i Int32",
            partition_by="d",
            engine=f"S3(s3_conn, format = CSV, filename='{table_name_2}/', partition_columns_in_data_file=1, partition_strategy='hive')",
            settings=[("use_hive_partitioning", "1")],
        )

    with When("I insert data into both tables"):
        insert_into_table_values(
            table_name=table_name_1,
            values=f"('random_string', 1)",
            settings=[("use_hive_partitioning", "1")],
        )
        insert_into_table_values(
            table_name=table_name_2,
            values=f"('random_string', 1)",
            settings=[("use_hive_partitioning", "1")],
        )

    with Then("I check that files in bucket are different"):
        files_1 = (
            get_bucket_files_list(filename=table_name_1).split("\n")[-2][:-1]
            + "/"
            + get_bucket_files_list(filename=table_name_1).split("\n")[-1]
        )
        files_2 = (
            get_bucket_files_list(filename=table_name_2).split("\n")[-2][:-1]
            + "/"
            + get_bucket_files_list(filename=table_name_2).split("\n")[-1]
        )
        assert not ("random_string" in get_bucket_file(file_path=files_1)), error()
        assert "random_string" in get_bucket_file(file_path=files_2), error()


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_PartitionColumnsInDataFile("1.0"),
)
def write_partition_columns_into_files_default(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Check that `partition_columns_in_data_file` parameter is set to `0` by default."""
    if uri is None:
        uri = self.context.uri

    table_name = "write_partition_columns_into_files_default"

    with Given("I create table with default write partition columns into files"):
        create_table(
            table_name=table_name,
            columns="d String, i Int32",
            partition_by="d",
            engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_columns_in_data_file=0, partition_strategy='hive')",
            settings=[("use_hive_partitioning", "1")],
        )
    with When("I insert data into table"):
        insert_into_table_values(
            table_name=table_name,
            values=f"('random_string', 1)",
            settings=[("use_hive_partitioning", "1")],
        )

    with Then("I check that partition columns are not in data file"):
        files = (
            get_bucket_files_list(filename=table_name).split("\n")[-2][:-1]
            + "/"
            + get_bucket_files_list(filename=table_name).split("\n")[-1]
        )
        assert not ("random_string" in get_bucket_file(file_path=files)), error()


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_PartitionColumnsInDataFileWrongArgument("1.0"),
)
def write_partition_columns_into_files_wrong_argument(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Check that ClickHouse returns an error if `write_partition_columns_into_files` parameter gets wrong argument."""
    if uri is None:
        uri = self.context.uri

    table_name = "write_partition_columns_into_files_wrong_argument"

    with Given("I create table with wrong write_partition_columns_into_files"):
        create_table(
            table_name=table_name,
            columns="d Int32, i Int32",
            partition_by="d",
            engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_columns_in_data_file='wrong', partition_strategy='hive')",
            exitcode=36,
            message="DB::Exception: Cannot extract UInt64 from partition_columns_in_data_file.",
            settings=[("use_hive_partitioning", "1")],
        )


@TestFeature
@Name("write partition columns into files parameter")
def feature(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Run write partition columns into files parameter test."""
    if uri is None:
        uri = self.context.uri
    if minio_root_user is None:
        minio_root_user = self.context.root_user
    if minio_root_password is None:
        minio_root_password = self.context.root_password

    for scenario in loads(current_module(), Scenario):
        Scenario(
            test=scenario,
        )(
            uri=uri,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            uri_readonly=uri_readonly,
        )
