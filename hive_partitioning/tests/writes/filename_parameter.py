from testflows.core import *
from testflows.combinatorics import product
from hive_partitioning.tests.steps import *
from hive_partitioning.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_InvalidFilename("1.0"),
)
def invalid_filename(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Check that ClickHouse returns an error if `filename` parameter is invalid."""
    if uri is None:
        uri = self.context.uri

    table_name = "invalid_filename"

    with Given("I create table with invalid filename"):
        create_table(
            table_name=table_name,
            columns="d Int32, i Int32",
            partition_by="d",
            engine=f"S3(s3_conn, format = Parquet, filename='invalid_filename//', partition_strategy='hive')",
            settings=[("use_hive_partitioning", "1")],
            exitcode=36,
            message="DB::Exception: Invalid S3 key",
        )


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_NotDefinedFilename("1.0"),
)
def not_defined_filename(
    self,
    uri=None,
    minio_root_user=None,
    minio_root_password=None,
    uri_readonly=None,
    node=None,
):
    """Check that ClickHouse writes table in the root directory if `filename` parameter is not defined."""
    if node is None:
        node = self.context.node

    table_name = "not_defined_filename"
    with Given("I create table with not defined filename"):
        create_table(
            table_name=table_name,
            columns="d Int32, i Int32",
            partition_by="d",
            engine=f"S3(s3_conn, format = Parquet, partition_strategy='hive')",
            settings=[("use_hive_partitioning", "1")],
        )

    with When("I insert data into table"):
        insert_into_table_values(
            table_name=table_name,
            values="(1, 1)",
            settings=[("use_hive_partitioning", "1")],
        )

    with Then("I check files in bucket"):
        files = get_bucket_files_list(node=node)
        assert f"d=1/" in files, error()


@TestFeature
@Name("filename parameter")
def feature(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Run filename parameter writes test."""
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
