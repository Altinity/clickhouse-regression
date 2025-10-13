from testflows.core import *
from testflows.asserts import error
from hive_partitioning.requirements.requirements import *
from hive_partitioning.tests.steps import *
from testflows.combinatorics import product


@TestScenario
def s3_engine_parameters(
    self,
    uri=None,
    minio_root_user=None,
    minio_root_password=None,
    uri_readonly=None,
    node=None,
):
    """Check that s3 engine parameters are supported."""
    if node is None:
        node = self.context.node

    formats = (
        "TabSeparated",
        "TabSeparatedRaw",
        "TabSeparatedWithNames",
        "TabSeparatedWithNamesAndTypes",
        "TabSeparatedRawWithNames",
        "TabSeparatedRawWithNamesAndTypes",
        "CSV",
        "CSVWithNames",
        "CSVWithNamesAndTypes",
        "CustomSeparated",
        "CustomSeparatedWithNames",
        "CustomSeparatedWithNamesAndTypes",
        "Values",
        "JSON",
        "JSONColumns",
        "JSONColumnsWithMetadata",
        "JSONCompact",
        "JSONCompactColumns",
        "JSONEachRow",
        "JSONStringsEachRow",
        "JSONCompactEachRow",
        "JSONCompactEachRowWithNames",
        "JSONCompactEachRowWithNamesAndTypes",
        "JSONCompactStringsEachRow",
        "JSONCompactStringsEachRowWithNames",
        "JSONCompactStringsEachRowWithNamesAndTypes",
        "JSONObjectEachRow",
        "BSONEachRow",
        "TSKV",
        "Protobuf",
        "ProtobufSingle",
        "ProtobufList",
        "Avro",
        "Parquet",
        "Arrow",
        "ArrowStream",
        "ORC",
        "Npy",
        "RowBinary",
        "RowBinaryWithNames",
        "RowBinaryWithNamesAndTypes",
        "Native",
        "CapnProto",
        "MsgPack",
    )
    compressions = ("none", "gzip", "brotli", "LZMA", "zstd")

    for format, compression in product(formats, compressions):
        table_name = f"s3_engine_parameters_{format}_{compression}"
        with Scenario(name=f"{format} {compression}"):
            with Given(f"I create table {table_name}"):
                create_table(
                    table_name=table_name,
                    columns="d Int32, i Int32",
                    partition_by="d",
                    engine=f"S3(s3_conn, format = {format}, compression = {compression}, filename='{table_name}/', partition_strategy='hive')",
                    settings=[("use_hive_partitioning", "1")],
                )
            with When("I insert data into table"):
                insert_into_table_values(
                    table_name=table_name,
                    values="(1, 1)",
                    settings=[("use_hive_partitioning", "1")],
                )

            with Then("I check data in table"):
                check_select(
                    select=f"SELECT i FROM {table_name} WHERE d = 1 ORDER BY i",
                    expected_result="1",
                    node=node,
                )

            with Then("I check files in bucket"):
                files = get_bucket_files_list(node=node, filename=table_name)
                note(files)
                assert f"{table_name}/d=1/" in files, error()
                assert f".{format}".lower() in files, error()


@TestScenario
def s3_engine_parameters_partition_columns_in_data_file(
    self,
    uri=None,
    minio_root_user=None,
    minio_root_password=None,
    uri_readonly=None,
    node=None,
):
    """Check that s3 engine parameters are supported if partition columns in data file is set to true."""
    if node is None:
        node = self.context.node

    formats = (
        "TabSeparated",
        "TabSeparatedRaw",
        "TabSeparatedWithNames",
        "TabSeparatedWithNamesAndTypes",
        "TabSeparatedRawWithNames",
        "TabSeparatedRawWithNamesAndTypes",
        "CSV",
        "CSVWithNames",
        "CSVWithNamesAndTypes",
        "CustomSeparated",
        "CustomSeparatedWithNames",
        "CustomSeparatedWithNamesAndTypes",
        "Values",
        "JSON",
        "JSONColumns",
        "JSONColumnsWithMetadata",
        "JSONCompact",
        "JSONCompactColumns",
        "JSONEachRow",
        "JSONStringsEachRow",
        "JSONCompactEachRow",
        "JSONCompactEachRowWithNames",
        "JSONCompactEachRowWithNamesAndTypes",
        "JSONCompactStringsEachRow",
        "JSONCompactStringsEachRowWithNames",
        "JSONCompactStringsEachRowWithNamesAndTypes",
        "JSONObjectEachRow",
        "BSONEachRow",
        "TSKV",
        "Protobuf",
        "ProtobufSingle",
        "ProtobufList",
        "Avro",
        "Parquet",
        "Arrow",
        "ArrowStream",
        "ORC",
        "RowBinary",
        "RowBinaryWithNames",
        "RowBinaryWithNamesAndTypes",
        "Native",
        "CapnProto",
        "MsgPack",
    )
    compressions = ("none", "gzip", "brotli", "LZMA", "zstd")

    for format, compression in product(formats, compressions):
        table_name = f"s3_engine_parameters_partition_columns_in_data_file_{format}_{compression}"
        with Scenario(name=f"{format} {compression}"):
            with Given(f"I create table {table_name}"):
                create_table(
                    table_name=table_name,
                    columns="d Int32, i Int32",
                    partition_by="d",
                    engine=f"S3(s3_conn, format = {format}, compression = {compression}, filename='{table_name}/', partition_strategy='hive', partition_columns_in_data_file=true)",
                    settings=[("use_hive_partitioning", "1")],
                )
            with When("I insert data into table"):
                insert_into_table_values(
                    table_name=table_name,
                    values="(1, 1)",
                    settings=[("use_hive_partitioning", "1")],
                )

            with Then("I check data in table"):
                check_select(
                    select=f"SELECT i FROM {table_name} WHERE d = 1 ORDER BY i",
                    expected_result="1",
                    node=node,
                )

            with Then("I check files in bucket"):
                files = get_bucket_files_list(node=node, filename=table_name)
                note(files)
                assert f"{table_name}/d=1/" in files, error()
                assert f".{format}".lower() in files, error()


@TestFeature
@Requirements(
    RQ_HivePartitioning_Writes_S3EngineParameters("1.0"),
)
@Name("s3 engine parameters")
def feature(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Run s3 engine parameters test."""
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
