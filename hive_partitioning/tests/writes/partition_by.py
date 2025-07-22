from testflows.core import *
from testflows.combinatorics import product
from hive_partitioning.tests.steps import *
from hive_partitioning.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_PartitionBy("1.0"),
)
def partition_by_missing(
    self,
    uri=None,
    minio_root_user=None,
    minio_root_password=None,
    uri_readonly=None,
    node=None,
):
    """Run partition by missing writes test."""

    if node is None:
        node = self.context.node

    table_name = "partition_by_missing"

    with Given("I create table without partition by"):
        create_table(
            table_name=table_name,
            engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
            node=node,
            settings=[("use_hive_partitioning", "1")],
            message="DB::Exception: Partition strategy hive can not be used without a PARTITION BY expression.",
            exitcode=36,
        )


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_PartitionKey("1.0"),
)
def partition_by_key(
    self,
    uri=None,
    minio_root_user=None,
    minio_root_password=None,
    uri_readonly=None,
    node=None,
):
    """Run partition by key writes test."""

    if node is None:
        node = self.context.node

    table_name = "partition_by_key"

    with Given("I create table with partition by"):
        create_table(
            table_name=table_name,
            columns="d Int32, i Int32",
            engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
            partition_by="d",
            node=node,
            settings=[("use_hive_partitioning", "1")],
        )

    with When("I insert data into table"):
        insert_into_table_values(
            table_name=table_name,
            values="(1, 1)",
            settings=[("use_hive_partitioning", "1")],
            node=node,
        )

    with Then("I check files in bucket"):
        files = get_bucket_files_list(node=node)
        assert f"{table_name}/d=1/" in files, error()


@TestFeature
@Requirements(
    RQ_HivePartitioning_Writes_PartitionBy("1.0"),
)
@Name("partition by")
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
