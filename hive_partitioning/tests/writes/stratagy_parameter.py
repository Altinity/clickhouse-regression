from testflows.core import *
from testflows.combinatorics import product
from hive_partitioning.tests.steps import *
from hive_partitioning.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_PartitionStratagyWrongArgument("1.0"),
)
def partition_stratagy_wrong_argument(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Check that ClickHouse returns an error if `partition_stratagy` parameter gets wrong argument."""
    if uri is None:
        uri = self.context.uri

    table_name = "partition_stratagy_wrong_argument"

    with Given("I create table with wrong partition stratagy"):
        create_table(
            table_name=table_name,
            columns="d Int32, i Int32",
            partition_by="d",
            engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'wrong')",
            settings=[("use_hive_partitioning", "1")],
            exitcode=36,
            message="DB::Exception: Unknown partitioning style 'wrong'",
        )


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_PartitionStratagy("1.0"),
)
def partition_stratagy_default(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Check that `partition_stratagy` parameter is set to `auto` by default."""
    if uri is None:
        uri = self.context.uri

    table_name = "partition_stratagy_default"

    with Given("I create table with default partition stratagy"):
        create_table(
            table_name=table_name,
            columns="d Int32, i Int32",
            partition_by="d",
            engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/')",
            settings=[("use_hive_partitioning", "1")],
        )

    # with When("I insert data into table"):
    #     insert_into_table_values(
    #         table_name=table_name,
    #         values="(1, 1)",
    #         settings=[("use_hive_partitioning", "1")],
    #     )

    # with Then("I check data in table"):
    #     check_select(
    #         select=f"SELECT * FROM {table_name} ORDER BY d",
    #         expected_result="1\n",
    #     )


@TestFeature
@Name("stratagy parameter")
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
