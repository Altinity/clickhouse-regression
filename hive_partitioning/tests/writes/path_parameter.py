from testflows.core import *
from testflows.combinatorics import product
from hive_partitioning.tests.steps import *
from hive_partitioning.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_InvalidPath("1.0"),
)
def invalid_path(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Check that ClickHouse returns an error if `path` parameter is invalid."""
    if uri is None:
        uri = self.context.uri

    table_name = "invalid_path"

    with Given("I create table with invalid path"):
        create_table(
            table_name=table_name,
            columns="d Int32, i Int32",
            partition_by="d",
            engine=f"S3('{uri}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
            exitcode=36,
            message="DB::Exception: Invalid S3 key",
        )


@TestFeature
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_Path("1.0"),
)
@Name("path")
def feature(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Run partition by writes test."""
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
