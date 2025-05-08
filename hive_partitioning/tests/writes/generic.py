from testflows.core import *
from hive_partitioning.tests.steps import *
from hive_partitioning.requirements.requirements import *


# @TestScenario
# @Requirements(
#     RQ_HivePartitioning_HivePartitionWrites_S3("1.0"),
# )
# def s3(self,uri, minio_root_user, minio_root_password, node=None):
#     """Run generic writes test."""
    
#     if node is None:
#         node = self.context.node

#     table_name = "generic_s3"

#     with Given("I create table for hive partition writes"):
#         create_table(
#             columns="d Int32, i Int32",
#             table_name=table_name,
#             engine=f"S3(s3_conn, format = Parquet, filename='{table_name}', partition_strategy='hive')",
#             partition_by="d", 
#             node=node
#         )
    
#     with And("I create table for hive partition reads"):
#         create_table(
#             table_name=f"{table_name}_reads",
#             columns="i Int32",
#             engine=f"S3(s3_conn, filename = '{table_name}/**', format = Parquet)",
#             node=node
#         )

#     with When("I insert data into table"):
#         insert_into_table_values(node=node, table_name=table_name, values="(1, 1)", settings=[("use_hive_partitioning", "1")])

#     with Then("I check data in table"):
#         check_select(select=f"SELECT * FROM {table_name}_reads ORDER BY i", expected_result="1", node=node, settings=[("use_hive_partitioning", "1")])




# @TestScenario
# @Requirements(
#     RQ_HivePartitioning_HivePartitionWrites_FileExist("1.0"),
# )
# def file_exist(self,uri, minio_root_user, minio_root_password, node=None):
#     """Check that data is properly added to the file if it already exists."""
    
#     if node is None:
#         node = self.context.node

#     table_name = "file_exist_s3"

#     with Given("I create table for hive partition writes"):
#         create_table(
#             columns="d Int32, i Int32",
#             table_name=table_name,
#             engine=f"S3(s3_conn, format = Parquet, filename='{table_name}', partition_strategy='hive')",
#             partition_by="d", 
#             node=node
#         )
    
#     with And("I create table for hive partition reads"):
#         create_table(
#             table_name=f"{table_name}_reads",
#             columns="i Int32",
#             engine=f"S3(s3_conn, filename = '{table_name}/**', format = Parquet)",
#             node=node
#         )

#     with When("I insert data into table the first time"):
#         insert_into_table_values(node=node, table_name=table_name, values="(1, 1)", settings=[("use_hive_partitioning", "1")])

#     with When("I insert data into table the second time"):
#         insert_into_table_values(node=node, table_name=table_name, values="(1, 2)", settings=[("use_hive_partitioning", "1")])

#     with Then("I check data in table"):
#         check_select(select=f"SELECT * FROM {table_name}_reads ORDER BY i", expected_result="1\n2", node=node, settings=[("use_hive_partitioning", "1")])



# @TestScenario
# @Requirements(
#     RQ_HivePartitioning_HivePartitionWrites_MissingColumn("1.0"),
# )
# def missing_column(self,uri, minio_root_user, minio_root_password, node=None):
#     """Check that error is returned when column defined in `PARTITION BY` clause is missing."""
    
#     if node is None:
#         node = self.context.node

#     table_name = "missing_column_s3"

#     with Given("I create table for hive partition writes"):
#         create_table(
#             columns="d Int32, i Int32",
#             table_name=table_name,
#             engine=f"S3(s3_conn, format = Parquet, filename='{table_name}', partition_strategy='hive')",
#             partition_by="no_column", 
#             node=node,
#             exitcode=47,
#             message="DB::Exception: Missing columns"
#         )


# @TestScenario
# @Requirements(
#     RQ_HivePartitioning_HivePartitionWrites_NullInColumn("1.0"),
# )
# def null_in_column(self,uri, minio_root_user, minio_root_password, node=None):
#     """Check that clickhouse returns an error when `NULL` value is inserted into column defined in `PARTITION BY` clause."""
    
#     if node is None:
#         node = self.context.node

#     table_name = "null_in_column_s3"

#     with Given("I create table for hive partition writes"):
#         create_table(
#             columns="d Nullable(Int32), i Int32",
#             table_name=table_name,
#             engine=f"S3(s3_conn, format = Parquet, filename='{table_name}', partition_strategy='hive')",
#             partition_by="d", 
#             node=node,
#         )

#     with When("I insert data into table the first time"):
#         insert_into_table_values(
#             node=node, 
#             table_name=table_name, 
#             values="(NULL, 1)", 
#             settings=[("use_hive_partitioning", "1")], 
#             exitcode=48, 
#             message="DB::Exception: Method getDataAt is not supported for Nullable"
#         )

@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_UnsupportedTypes("1.0"),
)
def unsupported_types(self,uri, minio_root_user, minio_root_password, node=None):
    """Check that clickhouse returns an error when column defined in `PARTITION BY` clause has unsupported type."""

    if node is None:
        node = self.context.node

    table_name = "unsupported_types_s3"

    with Given("I create table for hive partition writes"): 
        create_table(
            columns="d Map(String, UInt64), i Int32",
            table_name=table_name,
            engine=f"S3(s3_conn, format = Parquet, filename='{table_name}')",
            partition_by="d", 
            node=node,
        )
    with When("I insert data into table"):
        insert_into_table_values(
            node=node, 
            table_name=table_name, 
            values="({'key1': 1}, 1)", 
            settings=[("use_hive_partitioning", "1")], 
            # exitcode=6,
            # message="DB::Exception: Illegal character"
        )
    pause()

@TestFeature
@Name("generic")
def feature(self, uri=None, minio_root_user=None, minio_root_password=None):
    """Run generic writes test."""
    if uri is None:
        uri = self.context.uri
    if minio_root_user is None:
        minio_root_user = self.context.root_user
    if minio_root_password is None:
        minio_root_password = self.context.root_password

    pause()
    for scenario in loads(current_module(), Scenario):
        Scenario(
            test=scenario,
        )(uri=uri, minio_root_user=minio_root_user, minio_root_password=minio_root_password)