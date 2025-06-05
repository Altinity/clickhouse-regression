from testflows.core import *
from testflows.combinatorics import product
from hive_partitioning.tests.steps import *
from hive_partitioning.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_S3("1.0"),
)
def s3(self, uri, uri_readonly, minio_root_user, minio_root_password, node=None):
    """Run generic writes test."""

    if node is None:
        node = self.context.node

    input_formats = ["named_collections", "positional_args"]
    hive_partition_column_types_values = [
        ("Int32", 1),
        ("String", "'1'"),
        ("Date", "'2000-01-01'"),
        ("DateTime", "'2000-01-01 00:00:00'"),
        ("UUID", "'123e4567-e89b-12d3-a456-426614174000'"),
        ("IPv4", "'192.168.1.1'"),
        ("IPv6", "'2001:db8:85a3:8d3:1319:8a2e:370:7348'"),
        ("Decimal(10, 3)", "123.45"),
        ("Float", "123.45"),
        ("Double", "123.45"),
    ]

    for input_format, type_value in product(
        input_formats, hive_partition_column_types_values
    ):
        with Scenario(name=f"{input_format} {type_value[0]}"):
            table_name = f"generic_s3_{input_format}_{type_value[0].replace('(', '_').replace(')', '').replace(',', '_').replace(' ', '_')}"

            if input_format == "named_collections":
                with Given("I create table for hive partition writes"):
                    create_table(
                        columns=f"d {type_value[0]}, i Int32",
                        table_name=table_name,
                        engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_strategy='hive')",
                        partition_by="d",
                        node=node,
                    )

            if input_format == "positional_args":
                with Given("I create table for hive partition writes"):
                    create_table(
                        columns=f"d {type_value[0]}, i Int32",
                        table_name=table_name,
                        engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
                        partition_by="d",
                        node=node,
                    )

            with When("I insert data into table"):
                insert_into_table_values(
                    node=node,
                    table_name=table_name,
                    values=f"({type_value[1]}, 1)",
                    settings=[("use_hive_partitioning", "1")],
                )
            if type_value[0] == "Float":
                with Then("I check data in table"):
                    check_select(
                        select=f"SELECT i FROM {table_name} WHERE d = '{type_value[1]}' ORDER BY i",
                        expected_result="1",
                        node=node,
                        settings=[("use_hive_partitioning", "1")],
                    )
            else:
                with Then("I check data in table"):
                    check_select(
                        select=f"SELECT i FROM {table_name} WHERE d = {type_value[1]} ORDER BY i",
                        expected_result="1",
                        node=node,
                        settings=[("use_hive_partitioning", "1")],
                    )

@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_UseHivePartitions("1.0"),
)
def s3_use_hive_partitioning(self, uri, uri_readonly, minio_root_user, minio_root_password, node=None):
    """Check that ClickHouse ignores `use_hive_partitioning=0` if `partition_stratagy=hive`."""

    if node is None:
        node = self.context.node

    table_name = "s3_use_hive_partitioning"

    with Given("I create table for hive partition writes"):
        create_table(
            columns="d Int32, i Int32",
            table_name=table_name,
            engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_strategy='hive')",
            partition_by="d",
            node=node,
        )
    with When("I insert data into table"):
        insert_into_table_values(
            node=node,
            table_name=table_name,
            values="(1, 1)",
        )

    with Then("I check data in table"):
        check_select(
            select=f"SELECT i FROM {table_name} WHERE d = 1 ORDER BY i",
            expected_result="1",
            node=node,
        )

    with Then("I check that file path"):
        files = get_bucket_files_list(node=node, filename=table_name)
        assert f"{table_name}/d=1/" in files, error()

@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_S3("1.0"),
)
def s3_many_partitions(self, uri, uri_readonly, minio_root_user, minio_root_password, node=None):
    """Run generic writes test."""

    if node is None:
        node = self.context.node

    input_formats = ["named_collections", "positional_args"]
    hive_partition_column_types_values = [
        ("Int32", 1),
        ("String", "'1'"),
        ("Date", "'2000-01-01'"),
        ("DateTime", "'2000-01-01 00:00:00'"),
        ("UUID", "'123e4567-e89b-12d3-a456-426614174000'"),
        ("IPv4", "'192.168.1.1'"),
        ("IPv6", "'2001:db8:85a3:8d3:1319:8a2e:370:7348'"),
        ("Decimal(10, 3)", "123.45"),
        ("Float", "123.45"),
        ("Double", "123.45"),
    ]

    for input_format, type_value in product(
        input_formats, hive_partition_column_types_values
    ):
        with Scenario(name=f"{input_format} {type_value[0]}"):
            table_name = f"generic_s3_many_partitions_{input_format}_{type_value[0].replace('(', '_').replace(')', '').replace(',', '_').replace(' ', '_')}"

            if input_format == "named_collections":
                with Given("I create table for hive partition writes"):
                    create_table(
                        columns=f"d1 {type_value[0]}, d2 {type_value[0]}, i Int32",
                        table_name=table_name,
                        engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_strategy='hive')",
                        partition_by="(d1, d2)",
                        node=node,
                    )

            if input_format == "positional_args":
                with Given("I create table for hive partition writes"):
                    create_table(
                        columns=f"d1 {type_value[0]}, d2 {type_value[0]}, i Int32",
                        table_name=table_name,
                        engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
                        partition_by="(d1, d2)",
                        node=node,
                    )

            with When("I insert data into table"):
                insert_into_table_values(
                    node=node,
                    table_name=table_name,
                    values=f"({type_value[1]}, {type_value[1]}, 1)",
                    settings=[("use_hive_partitioning", "1")],
                )

            with Then("I check files in bucket"):
                files = get_bucket_files_list(node=node, filename=table_name)
                value = f"{type_value[1]}" if type_value[0] in ("Int32", "Decimal(10, 3)", "Float", "Double") else f"{type_value[1][1:-1]}"
                assert f"{table_name}/d1={value}/d2={value}/" in files, error()

            if type_value[0] == "Float":
                
                with Then("I check data in table"):
                    check_select(
                        select=f"SELECT i FROM {table_name} WHERE d1 = '{type_value[1]}' AND d2 = '{type_value[1]}' ORDER BY i",
                        expected_result="1",
                        node=node,
                        settings=[("use_hive_partitioning", "1")],
                    )
            else:
                with Then("I check data in table"):
                    check_select(
                        select=f"SELECT i FROM {table_name} WHERE d1 = {type_value[1]} AND d2 = {type_value[1]} ORDER BY i",
                        expected_result="1",
                        node=node,
                        settings=[("use_hive_partitioning", "1")],
                    )

@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_FileExist("1.0"),
)
def file_exists(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that data is properly added to the file if it already exists."""

    if node is None:
        node = self.context.node

    input_formats = ["named_collections", "positional_args"]
    hive_partition_column_types_values = [
        ("Int32", 1),
        ("String", "'1'"),
        ("Date", "'2000-01-01'"),
        ("DateTime", "'2000-01-01 00:00:00'"),
        ("UUID", "'123e4567-e89b-12d3-a456-426614174000'"),
        ("IPv4", "'192.168.1.1'"),
        ("IPv6", "'2001:db8:85a3:8d3:1319:8a2e:370:7348'"),
        ("Decimal", "123.45"),
        ("Float", "123.45"),
        ("Double", "123.45"),
    ]

    for input_format, type_value in product(
        input_formats, hive_partition_column_types_values
    ):
        with Scenario(name=f"{input_format} {type_value[0]}"):
            table_name = f"file_exist_s3_{input_format}_{type_value[0]}"

            if input_format == "named_collections":
                with Given("I create table for hive partition writes"):
                    create_table(
                        columns=f"d {type_value[0]}, i Int32",
                        table_name=table_name,
                        engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_strategy='hive')",
                        partition_by="d",
                        node=node,
                    )

            if input_format == "positional_args":
                with Given("I create table for hive partition writes"):
                    create_table(
                        columns=f"d {type_value[0]}, i Int32",
                        table_name=table_name,
                        engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
                        partition_by="d",
                        node=node,
                    )

            with When("I insert data into table the first time"):
                insert_into_table_values(
                    node=node,
                    table_name=table_name,
                    values=f"({type_value[1]}, 1)",
                    settings=[("use_hive_partitioning", "1")],
                )

            with When("I insert data into table the second time"):
                insert_into_table_values(
                    node=node,
                    table_name=table_name,
                    values=f"({type_value[1]}, 2)",
                    settings=[("use_hive_partitioning", "1")],
                )

            with Then("I check data in table"):
                check_select(
                    select=f"SELECT i FROM {table_name} ORDER BY i",
                    expected_result="1\n2",
                    node=node,
                    settings=[("use_hive_partitioning", "1")],
                )


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_MissingColumn("1.0"),
)
def missing_column(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that error is returned when column defined in `PARTITION BY` clause is missing."""

    if node is None:
        node = self.context.node

    table_name = "missing_column_s3"

    with Given("I create table for hive partition writes"):
        create_table(
            columns="d Int32, i Int32",
            table_name=table_name,
            engine=f"S3(s3_conn, format = Parquet, filename='{table_name}', partition_strategy='hive')",
            partition_by="no_column",
            node=node,
            exitcode=47,
            message="DB::Exception: Missing columns",
        )


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_NullInColumn("1.0"),
)
def null_in_column(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that clickhouse returns an error when `NULL` value is inserted into column defined in `PARTITION BY` clause."""

    if node is None:
        node = self.context.node

    table_name = "null_in_column_s3"

    with Given("I create table for hive partition writes"):
        create_table(
            columns="d Nullable(Int32), i Int32",
            table_name=table_name,
            engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
            partition_by="d",
            node=node,
        )

    with When("I insert data into table the first time"):
        insert_into_table_values(
            node=node,
            table_name=table_name,
            values="(NULL, 1)",
            settings=[("use_hive_partitioning", "1")],
            exitcode=48,
            message="DB::Exception: Method getDataAt is not supported for Nullable",
        )


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_UnsupportedTypes("1.0"),
)
def unsupported_types(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that clickhouse returns an error when column defined in `PARTITION BY` clause has unsupported type."""

    if node is None:
        node = self.context.node

    table_name = "unsupported_types_s3"
    with Given("I create table for hive partition writes"):
        create_table(
            columns="d Map(String, UInt64), i Int32",
            table_name=table_name,
            engine=f"S3(s3_conn, format = Parquet, filename='{table_name}', partition_strategy='hive')",
            partition_by="d",
            node=node,
        )
    with When("I insert data into table"):
        insert_into_table_values(
            node=node,
            table_name=table_name,
            values="({'key1': 1}, 1)",
            settings=[("use_hive_partitioning", "1")],
            exitcode=6,
            message="DB::Exception: Illegal character",
        )


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_ReadOnlyBucket("1.0"),
)
def read_only_bucket(self, uri, uri_readonly, minio_root_user, minio_root_password, node=None):
    """Check that clickhouse returns an error when trying to write to a read-only bucket."""

    if node is None:
        node = self.context.node

    table_name = "read_only_s3"

    with Given("I create table for hive partition writes"):
        create_table(
            columns="d Int32, i Int32",
            table_name=table_name,
            engine=f"S3('{uri_readonly}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
            partition_by="d",
            node=node,
        )

    with When("I insert data into table"):
        insert_into_table_values(
            node=node,
            table_name=table_name,
            values="(1, 1)",
            settings=[("use_hive_partitioning", "1")],
            exitcode=243,
            message="DB::Exception: Failed to check existence"
        )


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_NonAccessibleBucket("1.0"),
)
def non_accessible_bucket(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that clickhouse returns an error when trying to write to a non-accessible bucket."""

    if node is None:
        node = self.context.node

    table_name = "non_accessible_bucket_s3"

    with Given("I create table for hive partition writes"):
        create_table(
            columns="d Int32, i Int32",
            table_name=table_name,
            engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}_invalid', '', Parquet, 'auto', 'hive')",
            partition_by="d",
            node=node,
        )

    with When("I insert data into table"):
        insert_into_table_values(
            node=node,
            table_name=table_name,
            values="(1, 1)",
            settings=[("use_hive_partitioning", "1")],
            exitcode=243,
            message="DB::Exception: Failed to check existence",
        )


@TestScenario
@Requirements(
    RQ_HivePartitioning_HivePartitionWrites_ParallelInserts("1.0"),
)
def parallel_inserts(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that clickhouse parallel inserts for hive partition writes."""

    if node is None:
        node = self.context.node

    table_name = "parallel_inserts_s3"

    with Given("I create table for hive partition writes"):
        create_table(
            columns="d Int32, i Int32",
            table_name=table_name,
            engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
            partition_by="d",
            node=node,
        )

    with When("I insert data into table in parallel"):
        with Pool(5) as pool:
            try:
                for i in range(5):
                    When(
                        name=f"parallel insert {i}",
                        test=insert_into_table_values,
                        parallel=True,
                        executor=pool,
                    )(
                        table_name=table_name,
                        values="(1, 1)",
                        settings=[("use_hive_partitioning", "1")],
                    )
            finally:
                join()

    with Then("I check data in table"):
        check_select(
            select=f"SELECT i FROM {table_name} WHERE d = 1 ORDER BY i",
            expected_result="1\n1\n1\n1\n1",
            node=node,
            settings=[("use_hive_partitioning", "1")],
        )


@TestFeature
@Requirements(
    RQ_HivePartitioning_HivePartitionWritesSyntax_Generic("1.0"),
    RQ_HivePartitioning_HivePartitionWrites_PartitionStratagy("1.0"),
)
@Name("generic")
def feature(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Run generic writes test."""
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
