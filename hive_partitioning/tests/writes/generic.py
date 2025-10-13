from testflows.core import *
from testflows.combinatorics import product
from hive_partitioning.tests.steps import *
from hive_partitioning.requirements.requirements import *
from helpers.common import run_duckdb_query


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_SupportedDataTypes("1.0"),
)
def s3_supported_types(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that ClickHouse supports only supported types for hive partitioning."""

    if node is None:
        node = self.context.node

    hive_partition_column_types_values = supported_types_example_values

    input_formats = ["named_collections", "positional_args"]
    for input_format, type_value in product(
        input_formats, hive_partition_column_types_values
    ):
        for i, value in enumerate(type_value[1]):
            scenarios = ["min", "max", "random_value"]
            with Scenario(name=f"{input_format} {type_value[0]} {scenarios[i]}"):
                table_name = f"generic_s3_{input_format}_{type_value[0].replace('(', '_').replace(')', '').replace(',', '_').replace(' ', '_').replace('\'', '').replace('\"', '')}_{scenarios[i]}"

                if input_format == "named_collections":
                    with Given("I create table for hive partition writes"):
                        create_table(
                            columns=f"p {type_value[0]}, i Int32",
                            table_name=table_name,
                            engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_strategy='hive')",
                            partition_by="p",
                            node=node,
                            settings=[
                                ("allow_experimental_object_type", "1"),
                                ("enable_time_time64_type", "1"),
                            ],
                        )

                if input_format == "positional_args":
                    with Given("I create table for hive partition writes"):
                        create_table(
                            columns=f"p {type_value[0]}, i Int32",
                            table_name=table_name,
                            engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
                            partition_by="p",
                            node=node,
                            settings=[
                                ("allow_experimental_object_type", "1"),
                                ("enable_time_time64_type", "1"),
                            ],
                        )

                with When("I insert data into table"):
                    insert_into_table_values(
                        node=node,
                        table_name=table_name,
                        values=f"({value}, 1)",
                    )

                with Then("I check data in table"):
                    check_select(
                        select=f"SELECT i FROM {table_name} WHERE p = {value} ORDER BY i",
                        expected_result="1",
                        node=node,
                    )


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_DataTypesUnsupported("1.0"),
)
def s3_unsupported_types(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that clickhouse returns an error when column defined in `PARTITION BY` clause has unsupported type."""

    if node is None:
        node = self.context.node

    hive_partition_column_types_values = unsupported_types_example_values

    input_formats = ["named_collections", "positional_args"]

    for input_format, type_value in product(
        input_formats, hive_partition_column_types_values
    ):
        with Scenario(name=f"{input_format} {type_value[0]}"):
            table_name = f"s3_unsupported_types_{input_format}_{type_value[0].replace('(', '_').replace(')', '').replace(',', '_').replace(' ', '_').replace('\'', '').replace('\"', '')}"

            if input_format == "named_collections":
                with Given("I create table for hive partition writes"):
                    r = create_table(
                        columns=f"p {type_value[0]}, i Int32",
                        table_name=table_name,
                        engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_strategy='hive')",
                        partition_by="p",
                        node=node,
                        settings=[
                            ("allow_experimental_object_type", "1"),
                            ("enable_time_time64_type", "1"),
                        ],
                    )
            if input_format == "positional_args":
                with Given("I create table for hive partition writes"):
                    r = create_table(
                        columns=f"p {type_value[0]}, i Int32",
                        table_name=table_name,
                        engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
                        partition_by="p",
                        node=node,
                        settings=[
                            ("allow_experimental_object_type", "1"),
                            ("enable_time_time64_type", "1"),
                        ],
                    )
                with Then("I check exit code and message"):
                    assert (
                        r.exitcode == 37 or r.exitcode == 36 or r.exitcode == 44
                    ), error()
                    assert (
                        ("DB::Exception: Column with type" in r.output)
                        or (
                            "DB::Exception: Hive partitioning supports only partition columns of types"
                            in r.output
                        )
                        or ("is not allowed in key expression" in r.output)
                    ), error()


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_SupportedDataTypes("1.0"),
)
def s3_supported_characters(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that ClickHouse supports all the characters in the partition key except `{}\/"'*?`."""

    if node is None:
        node = self.context.node

    not_supported_characters = ["{", "}", "\\", '"', "'", "*", "?", "/"]

    if self.context.stress:
        characters_range = range(32, 1114111, 16)
    else:
        characters_range = range(32, 256, 16)
    for i in characters_range:
        with When("I create string for test"):
            string = "".join([chr(j) if j > 32 else "" for j in range(i, i + 16)])
            debug(string)
            string = remove_unsupported_character(string, not_supported_characters)
            debug(string)
            string = replace_ascii_characters(string)
            debug(string)
        with Scenario(name=f"characters from {i} to {i+16}"):
            table_name = f"s3_supported_characters_{i}_{i+16}"

            with Given("I create table for hive partition writes"):
                create_table(
                    columns="d String, i Int32",
                    table_name=table_name,
                    engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_strategy='hive')",
                    partition_by="d",
                    node=node,
                )
            with When("I insert data into table"):
                insert_into_table_values(
                    node=node,
                    table_name=table_name,
                    values=f"('{string}', 1)",
                )
            with Then("I check data in table"):
                check_select(
                    select=f"SELECT i FROM {table_name} WHERE d = '{string}' ORDER BY i",
                    expected_result="1",
                    node=node,
                )


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_DataTypesUnsupported("1.0"),
)
def s3_not_supported_characters(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that ClickHouse does not support the characters in the partition key `{}\/"'*?`."""

    if node is None:
        node = self.context.node

    not_supported_characters = ["{", "}", "\\", "/", '"', "'", "*", "?"]

    for character in not_supported_characters:
        i = ord(character)
        with Scenario(name=f"x{hex(i)[2:]}"):
            table_name = f"s3_not_supported_characters_{i}"

            with Given("I create table for hive partition writes"):
                create_table(
                    columns="d String, i Int32",
                    table_name=table_name,
                    engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_strategy='hive')",
                    partition_by="d",
                    node=node,
                )

            with When("I insert data into table"):
                insert_into_table_values(
                    node=node,
                    table_name=table_name,
                    values=f"('\\x{hex(i)[2:]}', 1)",
                    exitcode=6,
                    message=f"DB::Exception: Illegal character",
                )


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_SupportedDataTypes("1.0"),
)
def s3_partition_key_length(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that ClickHouse supports the partition key with 1024 length and returns an error if length is greater than 1024."""

    if node is None:
        node = self.context.node

    table_name = "s3_partition_key_length"

    with Given("I create table for hive partition writes"):
        create_table(
            columns="d String, i Int32",
            table_name=table_name,
            engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_strategy='hive')",
            partition_by="d",
            node=node,
        )
    with When("I insert data into table"):
        insert_into_table_values(
            node=node,
            table_name=table_name,
            values=f"('{'a'*1023}', 1)",
        )
    with Then("I check data in table"):
        check_select(
            select=f"SELECT i FROM {table_name} WHERE d = '{'a'*500}' ORDER BY i",
            expected_result="1",
            node=node,
        )
    with When("I insert data into table with length greater than 1024"):
        r = insert_into_table_values(
            node=node,
            table_name=table_name,
            values=f"('{'a'*1024}', 1)",
        )
    with Then("I check exit code and message"):
        assert r.exitcode == 36, error()
        assert "DB::Exception: Incorrect key length" in r.output, error()


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_Expressions("1.0"),
)
def hive_partition_expressions(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that ClickHouse does not support expressions in the partition key."""

    if node is None:
        node = self.context.node

    table_name = "s3_expressions"

    with Given("I create table for hive partition writes"):
        r = create_table(
            columns="p Int32, i Int32",
            table_name=table_name,
            engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_strategy='hive')",
            partition_by="abs(p)",
            node=node,
        )

    with Then("I check exit code and message"):
        assert r.exitcode == 36, error()
        assert (
            "DB::Exception: Hive partitioning expects that the partition by expression columns are a part of the storage columns"
            in r.output
        ), error()


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_PartitionsParts("1.0"),
    RQ_HivePartitioning_Writes_FileExist("1.0"),
)
def s3_partitions_parts(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that ClickHouse supports hive partition writes with partitions and parts."""

    if node is None:
        node = self.context.node

    partitions = [1, 30]
    parts = [1, 30]

    for partition, part in product(partitions, parts):
        with Scenario(name=f"partition={partition} part={part}"):
            table_name = f"s3_partitions_parts_{partition}_{part}"

            with Given("I create table for hive partition writes"):
                create_table(
                    columns="d Int32, i Int32",
                    table_name=table_name,
                    engine=f"S3(s3_conn, format = Parquet, filename='{table_name}/', partition_strategy='hive')",
                    partition_by="d",
                    node=node,
                )

            with When("I insert data into table"):
                for i in range(part):
                    insert_into_table_select(
                        node=node,
                        table_name=table_name,
                        select_statement=f"number AS d, {i} AS i from numbers({partition})",
                    )

            with Then("I check data in table"):
                check_select(
                    select=f"SELECT count() FROM {table_name}",
                    expected_result=f"{partition * part}",
                    node=node,
                )
                check_select(
                    select=f"SELECT count() FROM {table_name} WHERE d = 0",
                    expected_result=f"{part}",
                    node=node,
                )
                check_select(
                    select=f"SELECT count() FROM {table_name} WHERE i = 0",
                    expected_result=f"{partition}",
                    node=node,
                )


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_UseHivePartitions("1.0"),
)
def s3_use_hive_partitioning(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that ClickHouse ignores `use_hive_partitioning=0` if `partition_strategy=hive`."""

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
            settings=[("use_hive_partitioning", "0")],
        )
    with When("I insert data into table"):
        insert_into_table_values(
            node=node,
            table_name=table_name,
            values="(1, 1)",
            settings=[("use_hive_partitioning", "0")],
        )

    with Then("I check data in table"):
        check_select(
            select=f"SELECT i FROM {table_name} WHERE d = 1 ORDER BY i",
            expected_result="1",
            node=node,
            settings=[("use_hive_partitioning", "0")],
        )

    with Then("I check that file path"):
        files = get_bucket_files_list(node=node, filename=table_name)
        assert f"{table_name}/d=1/" in files, error()


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_MissingColumn("1.0"),
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
    RQ_HivePartitioning_Writes_NullableDataType("1.0"),
)
def null_in_column(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that clickhouse returns an error if columns defined in the `PARTITION BY` clause is Nullable."""

    if node is None:
        node = self.context.node

    table_name = "null_in_column_s3"

    with Given("I create table for hive partition writes"):
        r = create_table(
            columns="d Nullable(Int32), i Int32",
            table_name=table_name,
            engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
            partition_by="d",
            node=node,
        )

    with Then("I check exit code and message"):
        assert r.exitcode == 36, error()
        assert (
            "DB::Exception: Hive partitioning supports only partition columns of types"
            in r.output
        ), error()


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_ReadOnlyBucket("1.0"),
)
def read_only_bucket(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
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
            message="DB::Exception: Failed to check existence",
        )


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_NonAccessibleBucket("1.0"),
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
    RQ_HivePartitioning_Writes_ParallelInserts("1.0"),
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


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_ParallelInserts("1.0"),
)
def parallel_inserts_different_users(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that clickhouse parallel inserts for hive partition writes."""

    if node is None:
        node = self.context.node

    table_name = "parallel_inserts_different_users_s3"

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
                        name=f"parallel insert {i} from default user",
                        test=insert_into_table_values,
                        parallel=True,
                        executor=pool,
                    )(
                        table_name=table_name,
                        values="(1, 1)",
                        settings=[("use_hive_partitioning", "1"), ("user", "default")],
                    )
                    When(
                        name=f"parallel insert {i} from second user",
                        test=insert_into_table_values,
                        parallel=True,
                        executor=pool,
                    )(
                        table_name=table_name,
                        values="(1, 1)",
                        settings=[
                            ("use_hive_partitioning", "1"),
                            ("user", "second_user"),
                        ],
                    )
            finally:
                join()

    with Then("I check data in table"):
        check_select(
            select=f"SELECT i FROM {table_name} WHERE d = 1 ORDER BY i",
            expected_result="1\n1\n1\n1\n1\n1\n1\n1\n1\n1",
            node=node,
            settings=[("use_hive_partitioning", "1")],
        )


@TestScenario
@Requirements(
    RQ_HivePartitioning_Writes_WriteFail("1.0"),
)
def write_fail(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that clickhouse performs correctly if write fails."""

    if node is None:
        node = self.context.node

    table_name = "write_fail_s3"

    with Given("I create table for hive partition writes"):
        create_table(
            columns="d Int32, i Int32",
            table_name=table_name,
            engine=f"S3('{uri}{table_name}/', '{minio_root_user}', '{minio_root_password}', '', Parquet, 'auto', 'hive')",
            partition_by="d",
            node=node,
        )
    with And("I create source table"):
        create_table(
            columns="d Int32, i String",
            table_name="source",
            engine="Log()",
            node=node,
        )
    with And("I insert data into source table"):
        insert_into_table_select(
            table_name="source",
            select_statement="number AS d, number AS i FROM numbers(100000)",
            node=node,
        )
        insert_into_table_values(
            table_name="source",
            values="(100000, 'wrong_value')",
            node=node,
        )

    with When("I insert data into table"):
        insert_into_table_select(
            node=node,
            table_name=table_name,
            select_statement=f"d, toInt32(i) as i FROM source",
            no_checks=True,
        )

    with Then("I check data in table"):
        check_select(
            select=f"SELECT i, d FROM {table_name} WHERE d = '1' ORDER BY i",
            expected_result="",
            node=node,
        )


@TestFeature
@Requirements(RQ_HivePartitioning_Writes_S3("1.0"))
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
