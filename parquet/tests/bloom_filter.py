import base64
import datetime
import json

from decimal import Decimal
from inspect import stack

from helpers.common import *
from parquet.requirements import *
from parquet.tests.common import generate_values
from parquet.tests.outline import import_export
from parquet.tests.steps.bloom_filter import *
from parquet.tests.steps.general import (
    select_from_parquet,
    parquetify,
    get_parquet_structure,
    rows_read,
    create_parquet_json_definition,
    save_json_definition,
)


@TestStep(Given)
def prepare_parquet_file(
    self, schema_type, writer_version, physical_type, logical_type, compression_value
):
    """Prepare the JSON definition and determine necessary parameters for the parquet file."""
    json_file_name = (
        f"{compression_value()['compression']}_{physical_type()['physicalType']}_"
        f"{logical_type()['logicalType']}_" + getuid() + ".json"
    )
    path = self.context.json_files_local + "/" + json_file_name

    if logical_type()["logicalType"] == "NONE":
        data = generate_values(
            physical_type()["physicalType"], self.context.number_of_inserts
        )
        column_name = physical_type()["physicalType"].lower()
    else:
        data = generate_values(
            logical_type()["logicalType"], self.context.number_of_inserts
        )
        column_name = logical_type()["logicalType"].lower()

    parquet_file = (
        f"{compression_value()['compression']}_{physical_type()['physicalType']}_"
        f"{logical_type()['logicalType']}_" + getuid() + ".parquet"
    )

    file_definition = create_parquet_json_definition(
        schema_type=schema_type,
        writer_version=writer_version,
        physical_type=physical_type,
        logical_type=logical_type,
        compression_value=compression_value,
        parquet_file=parquet_file,
        data=data,
        enable_bloom_filter="all",
    )
    snapshot_name = (
        f"{file_definition['options']['compression']}_{physical_type()['physicalType']}_"
        f"{logical_type()['logicalType']}_{file_definition['schema'][0]['schemaType']}_"
        f"{file_definition['options']['writerVersion'].replace('.', '_')}"
    )

    save_json_definition(path=path, file_definition=file_definition)

    return json_file_name, parquet_file, column_name, data, snapshot_name


@TestStep(Given)
def generate_parquet_file(self, json_file_name):
    """Generate the parquet file from its JSON definition."""
    json_file_path = self.context.json_files + "/" + json_file_name
    return parquetify(
        json_file=json_file_path,
        output_path=self.context.parquet_output_path,
        no_checks=True,
    )


@TestStep(Given)
def open_client(self):
    """Open a ClickHouse client instance."""
    bash_tools = self.context.cluster.node("bash-tools")
    node = self.context.node
    return bash_tools.client(
        client_args={"host": node.name, "statistics": "null", "no_stack_trace": "null"}
    )


@TestStep(When)
def get_all_columns(self, table_name, database, node=None):

    if node is None:
        node = self.context.node

    node.query(
        f"SELECT arrayStringConcat(groupArray(name), ',') AS column_names FROM system.columns WHERE database = '{database}' AND table = '{table_name}';"
    )


@TestStep(Given)
def total_number_of_rows(self, file_name, node=None, stack_trace=None, client=True):
    """Get the total number of rows in the parquet file."""

    if node is None:
        node = self.context.node

    with By(f"getting the total number of rows in the parquet file {file_name}"):
        r = f"SELECT COUNT(*) FROM file('{file_name}', Parquet)"

        if stack_trace is not None:
            data = node.query(r, stack_trace=stack_trace)
        else:
            data = node.query(r)

    if client:
        return int(data.output[0][0])
    else:
        return int(data.output.strip())


@TestScenario
def read_and_write_file_with_bloom(self):
    """Read all files from a bloom directory that contains parquet files with bloom filters."""
    files = [
        "binary_bloom.gz.parquet",
        "timestamp_bloom.gz.parquet",
        "double_bloom.gz.parquet",
        "integer_bloom.gz.parquet",
        "decimal_bloom.gz.parquet",
        "struct_bloom.gz.parquet",
        "long_bloom.gz.parquet",
        "date_bloom.gz.parquet",
        "boolean_bloom.gz.parquet",
        "map_bloom.gz.parquet",
        "multi_column_bloom.gz.parquet",
        "array_bloom.gz.parquet",
        "float_bloom.gz.parquet",
    ]

    for file in files:
        with Given(f"I import and export the parquet file {file}"):
            import_export(
                snapshot_name=f"{file}_structure",
                import_file=os.path.join("bloom", file),
                snapshot_id=self.context.snapshot_id,
                settings=[("session_timezone", "UTC")],
            )


@TestCheck
def check_parquet_with_bloom(
    self, file_name, statement, condition, bloom_filter, filter_pushdown, native_reader
):
    """Check if the bloom filter is being used by ClickHouse."""

    with Given("I get the total number of rows in the parquet file"):
        initial_rows = total_number_of_rows(
            file_name="bloom/multi_column_bloom.gz.parquet", client=False
        )

    with And(
        "I read from the parquet file",
        description=f"Bloom Filter: {bloom_filter}, Filter Pushdown: {filter_pushdown}",
    ):
        with By(
            "selecting and saving the data from a parquet file without bloom filter enabled"
        ):
            order_by = "tuple(*)" if "ORDER BY" not in condition else False

            values_without_bloom = select_from_parquet(
                file_name=file_name,
                statement=statement,
                condition=condition,
                settings=f"input_format_parquet_use_native_reader={native_reader}",
                order_by=order_by,
            )

        with And(
            f"selecting and saving the data from a parquet file with bloom filter {bloom_filter} and filter pushdown {filter_pushdown}"
        ):
            data = select_from_parquet(
                file_name=file_name,
                statement=statement,
                condition=condition,
                format="Json",
                settings=f"input_format_parquet_bloom_filter_push_down={bloom_filter},input_format_parquet_filter_push_down={filter_pushdown},use_cache_for_count_from_files=false, input_format_parquet_use_native_reader={native_reader}",
                order_by=order_by,
            )

            values_with_bloom = select_from_parquet(
                file_name=file_name,
                statement=statement,
                condition=condition,
                settings=f"input_format_parquet_bloom_filter_push_down={bloom_filter},input_format_parquet_filter_push_down={filter_pushdown},use_cache_for_count_from_files=false, input_format_parquet_use_native_reader={native_reader}",
                order_by=order_by,
            )

    with Then("I check that the number of rows read is correct"):
        read_rows = rows_read(data.output.strip(), client=False)
        if bloom_filter == "true":
            with By(
                "Checking that the number of rows read is lower then the total number of rows of a file"
            ):
                assert read_rows < initial_rows, error()
        else:
            with By(
                "Checking that the number of rows read is equal to the total number of rows of a file"
            ):
                assert read_rows == initial_rows, error()

    with And(
        "I check that the data is the same when reading with bloom filter and without"
    ):
        assert (
            values_without_bloom.output.strip() == values_with_bloom.output.strip()
        ), f"Data is not the same, {values_without_bloom.output.strip()} != {values_with_bloom.output.strip()}"


@TestSketch(Scenario)
def read_bloom_filter_parquet_files(self):
    """Read all files from a bloom directory that contains parquet files with bloom filters."""

    file_name = "bloom/multi_column_bloom.gz.parquet"
    statements = [
        "*",
        "f32",
        "f64",
        "int",
        "str",
        "fixed_str",
        "array",
        "f32,f64,int,str,fixed_str,array",
    ]
    filter = ["true", "false"]
    native_reader = "false"
    conditions = [
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC'",
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC' OR str='KCGEY'",
        "WHERE f32=toFloat32(-15.910733) AND fixed_str IN ('BYYC', 'DCXV') ORDER BY f32 ASC",
        "WHERE f64 IN (toFloat64(22.89182051713945), toFloat64(68.62704389505595)) ORDER BY f32",
        "WHERE has(array, 69778) ORDER BY f32 ASC",
        "WHERE hasAll(array, [69778,58440,2913,64975,92300]) ORDER BY f32 ASC",
        "WHERE has(array, toInt32(toString(69778)))",
        "WHERE hasAny(array, [69778,58440,2913,64975,92300]) ORDER BY f32 asc",
        "WHERE '48' NOT IN 'int' AND fixed_str='BYYC'",
    ]

    check_parquet_with_bloom(
        file_name=file_name,
        bloom_filter=either(*filter),
        filter_pushdown="false",
        condition=either(*conditions),
        statement=either(*statements),
        native_reader=native_reader,
    )


@TestSketch(Scenario)
def read_bloom_filter_parquet_files_native_reader(self):
    """Read all files from a bloom directory that contains parquet files with bloom filters using the ClickHouse parquet native reader."""

    file_name = "bloom/bloom_no_arrays.gz.parquet"
    statements = [
        "*",
        "f32",
        "f64",
        "int",
        "str",
        "fixed_str",
        "f32,f64,int,str,fixed_str",
    ]
    filter = ["true", "false"]
    native_reader = "true"
    conditions = [
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC'",
        "WHERE f32=toFloat32(-64.12787) AND fixed_str='BYYC' OR str='KCGEY'",
        "WHERE f32=toFloat32(-15.910733) AND fixed_str IN ('BYYC', 'DCXV') ORDER BY f32 ASC",
        "WHERE f64 IN (toFloat64(22.89182051713945), toFloat64(68.62704389505595)) ORDER BY f32",
        "WHERE '48' NOT IN 'int' AND fixed_str='BYYC'",
    ]

    check_parquet_with_bloom(
        file_name=file_name,
        bloom_filter=either(*filter),
        filter_pushdown="false",
        condition=either(*conditions),
        statement=either(*statements),
        native_reader=native_reader,
    )


@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter_DataTypes_Complex("1.0")
)
@TestScenario
def native_reader_array_bloom(self):
    """Read a parquet file with bloom filter and array column using the ClickHouse parquet native reader."""
    file = "array_bloom.gz.parquet"

    select_from_parquet(
        file_name=file,
        format="Json",
        settings=f"input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down=false,use_cache_for_count_from_files=false, input_format_parquet_use_native_reader=true",
    )


@TestStep(Then)
def check_data_without_parquet_statistics(self, data_with_bloom, data_without_bloom):
    """Check that the data is the same when reading with bloom filter and without while removing the rows_read values from the output."""
    data_with_bloom = data_with_bloom.output
    data_without_bloom = data_without_bloom.output

    data_with_bloom.pop(-1)
    data_without_bloom.pop(-1)

    assert data_with_bloom == data_without_bloom, error()


@TestStep(Given)
def copy_into_user_files(self, file_path, node=None):
    """Copy a parquet file into the user files directory."""
    if node is None:
        node = self.context.node

    node.command(f"cp {file_path} /var/lib/clickhouse/user_files")


@TestStep(Given)
def copy_parquet_to_user_files(self, parquet_file):
    """Copy a parquet file into the user files directory."""
    copy_into_user_files(
        file_path=self.context.parquet_output_path + "/" + parquet_file
    )


@TestStep(Given)
def get_total_rows(self, parquet_file, client=None):
    """Get the total number of rows in the parquet file."""
    if client is None:
        client = self.context.node

    return total_number_of_rows(file_name=parquet_file, node=client, stack_trace=False)


@TestStep(Given)
def handle_conversion_error(
    self, parquet_file, statement, condition, client, native_reader, key_column=None
):
    """Handle errors during conversion check and return whether to proceed."""
    check_conversion = select_from_parquet(
        file_name=parquet_file,
        statement=statement,
        condition=condition,
        format="TabSeparated",
        settings=f"input_format_parquet_use_native_reader={native_reader}",
        order_by="tuple(*)",
        node=client,
        no_checks=True,
        stack_trace=False,
        key_column=key_column,
    )
    return check_conversion.errorcode == 0


@TestStep(Given)
def read_data_with_and_without_bloom(
    self,
    parquet_file,
    statement,
    condition,
    client,
    native_reader,
    filter_pushdown,
    key_column=None,
):
    """Read data from a parquet file with and without bloom filter."""
    data_without_bloom = select_from_parquet(
        file_name=parquet_file,
        statement=statement,
        format="TabSeparated",
        settings=f"input_format_parquet_use_native_reader={native_reader}",
        order_by="tuple(*)",
        node=client,
        condition=condition,
        stack_trace=False,
        key_column=key_column,
    )

    data_with_bloom = select_from_parquet(
        file_name=parquet_file,
        statement=statement,
        format="TabSeparated",
        settings=f"input_format_parquet_bloom_filter_push_down=true,"
        f"input_format_parquet_filter_push_down={filter_pushdown},"
        f"use_cache_for_count_from_files=false, input_format_parquet_use_native_reader={native_reader}",
        order_by="tuple(*)",
        node=client,
        condition=condition,
        stack_trace=False,
        key_column=key_column,
    )
    return data_without_bloom, data_with_bloom


@TestStep(Given)
def get_file_structure(self, parquet_file):
    """Retrieve the structure of a parquet file."""
    return get_parquet_structure(file_name=parquet_file)


@TestStep(Then)
def verify_rows_read(
    self,
    data_with_bloom,
    initial_rows,
    file_structure,
    conversion,
    snapshot_name,
    condition,
):
    """Verify the number of rows read from the parquet file."""
    read_rows = rows_read(data_with_bloom.output)
    snapshot(
        f"{read_rows}, initial_rows: {initial_rows}, file_structure: {file_structure.output}, "
        f"condition: {condition}",
        name=f"{snapshot_name}_{conversion}",
        id="bloom_filter",
        mode=snapshot.UPDATE,
    )


@TestStep(Then)
def compare_data_with_and_without_bloom(self, data_with_bloom, data_without_bloom):
    """Compare data read with and without bloom filter."""
    check_data_without_parquet_statistics(
        data_with_bloom=data_with_bloom,
        data_without_bloom=data_without_bloom,
    )


@TestStep(Then)
def check_all_field_type_conversions(
    self,
    parquet_file,
    client,
    column_name,
    data,
    statement,
    native_reader,
    filter_pushdown,
    conversions,
    snapshot_name,
):
    """Check all conversions for the parquet file via checking if the conversion returns an error and loop through all possible ClickHouse data conversions."""
    with When("I copy the parquet file into the user files directory"):
        copy_parquet_to_user_files(parquet_file=parquet_file)

    with And("I get the total number of rows in the parquet file"):
        initial_rows = get_total_rows(parquet_file=parquet_file, client=client)

    for conversion in conversions:
        condition = f"WHERE {column_name} = {conversion}('{data[-1]}')"
        with Check("I check that the bloom filter is being used by ClickHouse"):
            if not handle_conversion_error(
                parquet_file=parquet_file,
                statement=statement,
                condition=condition,
                client=client,
                native_reader=native_reader,
            ):
                continue

            data_without_bloom, data_with_bloom = read_data_with_and_without_bloom(
                parquet_file=parquet_file,
                statement=statement,
                condition=condition,
                client=client,
                native_reader=native_reader,
                filter_pushdown=filter_pushdown,
            )

            file_structure = get_file_structure(parquet_file=parquet_file)

            with Then("I check that the number of rows read is correct"):
                verify_rows_read(
                    data_with_bloom=data_with_bloom,
                    initial_rows=initial_rows,
                    file_structure=file_structure,
                    conversion=conversion,
                    snapshot_name=snapshot_name,
                    condition=f"WHERE {column_name} = {conversion}(value)",
                )

            with And(
                "I check that the data is the same when reading with bloom filter and without"
            ):
                compare_data_with_and_without_bloom(
                    data_with_bloom=data_with_bloom,
                    data_without_bloom=data_without_bloom,
                )


@TestStep(Then)
def check_all_key_column_type_conversions(
    self,
    parquet_file,
    client,
    column_name,
    data,
    statement,
    native_reader,
    filter_pushdown,
    conversions,
    snapshot_name,
):
    """Check all conversions for the parquet file via checking if the conversion returns an error and loop through all possible ClickHouse key column conversions."""
    with When("I copy the parquet file into the user files directory"):
        copy_parquet_to_user_files(parquet_file=parquet_file)

    with And("I get the total number of rows in the parquet file"):
        initial_rows = get_total_rows(parquet_file=parquet_file, client=client)

    for conversion in conversions:
        condition = f"WHERE {column_name} = '{data[-1]}'"
        key_column = f"{column_name} {conversion}"
        with Check("I check that the bloom filter is being used by ClickHouse"):
            if not handle_conversion_error(
                parquet_file=parquet_file,
                statement=statement,
                condition=condition,
                client=client,
                native_reader=native_reader,
                key_column=key_column,
            ):
                continue

            data_without_bloom, data_with_bloom = read_data_with_and_without_bloom(
                parquet_file=parquet_file,
                statement=statement,
                condition=condition,
                client=client,
                native_reader=native_reader,
                filter_pushdown=filter_pushdown,
                key_column=key_column,
            )

            file_structure = get_file_structure(parquet_file=parquet_file)

            with Then("I check that the number of rows read is correct"):
                verify_rows_read(
                    data_with_bloom=data_with_bloom,
                    initial_rows=initial_rows,
                    file_structure=file_structure,
                    conversion=conversion,
                    snapshot_name=snapshot_name,
                    condition=f"WHERE {column_name} = 'value'",
                )

            with And(
                "I check that the data is the same when reading with bloom filter and without"
            ):
                compare_data_with_and_without_bloom(
                    data_with_bloom=data_with_bloom,
                    data_without_bloom=data_without_bloom,
                )


@TestCheck
def check_bloom_filter_on_parquet(
    self,
    schema_type,
    writer_version,
    physical_type,
    logical_type,
    compression_value,
    statement,
    native_reader,
    filter_pushdown,
    conversions,
    check,
):
    """Check if the bloom filter is being used by ClickHouse."""
    with Given("I prepare the parquet file"):
        json_file_name, parquet_file, column_name, data, snapshot_name = (
            prepare_parquet_file(
                schema_type=schema_type,
                writer_version=writer_version,
                physical_type=physical_type,
                logical_type=logical_type,
                compression_value=compression_value,
            )
        )

    with And("I generate the parquet file"):
        generate_parquet = generate_parquet_file(json_file_name=json_file_name)

    with And("I open a single ClickHouse client instance"):
        if generate_parquet.exitcode != 0:
            skip("Incorrect JSON file structure")
        with open_client() as client:
            check(
                parquet_file=parquet_file,
                client=client,
                column_name=column_name,
                data=data,
                statement=statement,
                native_reader=native_reader,
                filter_pushdown=filter_pushdown,
                conversions=conversions,
                snapshot_name=snapshot_name,
            )


@TestSketch(Outline)
@Flags(TE)
def field_type_conversions_with_bloom_filter(self, logical_type, statements=None):
    """Read parquet files with different structure with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""

    if statements is None:
        statements = ["*"]

    filter = ["true", "false"]
    check_bloom_filter_on_parquet(
        schema_type=either(*schema_type),
        writer_version=either(*writer_version),
        physical_type=either(*physical_types),
        logical_type=logical_type,
        compression_value=either(*compression),
        statement=either(*statements),
        native_reader="false",
        filter_pushdown=either(*filter),
        conversions=conversions,
        check=check_all_field_type_conversions,
    )


@TestSketch(Outline)
@Flags(TE)
def key_column_type_conversions_with_bloom_filter(self, logical_type, statements=None):
    """Read parquet files with different structure with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""

    if statements is None:
        statements = ["*"]

    filter = ["true", "false"]
    check_bloom_filter_on_parquet(
        schema_type=either(*schema_type),
        writer_version=either(*writer_version),
        physical_type=either(*physical_types),
        logical_type=logical_type,
        compression_value=either(*compression),
        statement=either(*statements),
        native_reader="false",
        filter_pushdown=either(*filter),
        conversions=clickhouse_datatypes,
        check=check_all_key_column_type_conversions,
    )


@TestScenario
def supported_expressions(self):
    """Check which expressions are supported for bloom filter evaluation."""
    conditions = ["=", "!=", "IN", "NOT IN", ">", "<", ">=", "<="]
    file_path = os.path.join("bloom", "int_150_row_groups.parquet")
    for i in conditions:
        with Given(
            "I read from the parquet when bloom filter pushdown is enabled",
            description=f"expression: {i}",
        ):

            condition = (
                f"WHERE int8 {i} '3760'"
                if i not in ["IN", "NOT IN"]
                else f"WHERE int8 {i} ['3760', '3761']"
            )

            data = select_from_parquet(
                file_name=file_path,
                statement="*",
                condition=condition,
                format="Json",
                settings="input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down=false,use_cache_for_count_from_files=false",
            )

        with When("I get total number of rows of the file"):
            initial_rows = total_number_of_rows(file_name=file_path, client=False)

        with And("I get rows read"):
            read_rows = rows_read(data.output.strip(), client=False)

        with Then(
            "I check that the number of rows read is lower then the total number of rows of a file"
        ):
            assert (
                read_rows < initial_rows
            ), f"rows read {read_rows} is not less than total rows {initial_rows}"


@TestSketch(Scenario)
@Flags(TE)
def utf8_to_field_type(self):
    """Read parquet files with utf-8 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=utf8)


@TestSketch(Scenario)
@Flags(TE)
def decimal_to_field_type(self):
    """Read parquet files with decimal logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=decimal)


@TestSketch(Scenario)
@Flags(TE)
def date_to_field_type(self):
    """Read parquet files with date logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=date)


@TestSketch(Scenario)
@Flags(TE)
def time_millis_to_field_type(self):
    """Read parquet files with time-millis logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=time_millis)


@TestSketch
@Flags(TE)
def time_micros_to_field_type(self):
    """Read parquet files with time-micros logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=time_micros)


@TestSketch(Scenario)
@Flags(TE)
def timestamp_millis_to_field_type(self):
    """Read parquet files with timestamp-millis logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=timestamp_millis)


@TestSketch(Scenario)
@Flags(TE)
def timestamp_micros_to_field_type(self):
    """Read parquet files with timestamp-micros logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=timestamp_micros)


@TestSketch(Scenario)
@Flags(TE)
def enum_to_field_type(self):
    """Read parquet files with enum logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=enum)


@TestSketch(Scenario)
@Flags(TE)
def map_to_field_type(self):
    """Read parquet files with map logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=map)


@TestSketch(Scenario)
@Flags(TE)
def list_to_field_type(self):
    """Read parquet files with list logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=list)


@TestSketch(Scenario)
@Flags(TE)
def string_to_field_type(self):
    """Read parquet files with string logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=string)


@TestSketch(Scenario)
@Flags(TE)
def map_key_value_to_field_type(self):
    """Read parquet files with map key value logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=map_key_value)


@TestSketch(Scenario)
@Flags(TE)
def time_to_field_type(self):
    """Read parquet files with time logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=time)


@TestSketch(Scenario)
@Flags(TE)
def integer_to_field_type(self):
    """Read parquet files with integer logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=integer)


@TestSketch(Scenario)
@Flags(TE)
def json_to_field_type(self):
    """Read parquet files with json logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=json_type)


@TestSketch(Scenario)
@Flags(TE)
def bson_to_field_type(self):
    """Read parquet files with bson logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=bson)


@TestSketch(Scenario)
@Flags(TE)
def uuid_to_field_type(self):
    """Read parquet files with uuid logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=uuid)


@TestSketch(Scenario)
@Flags(TE)
def interval_to_field_type(self):
    """Read parquet files with interval logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=interval)


@TestSketch(Scenario)
@Flags(TE)
def float16_to_field_type(self):
    """Read parquet files with float16 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=float16)


@TestSketch(Scenario)
@Flags(TE)
def uint8_to_field_type(self):
    """Read parquet files with uint8 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=uint8)


@TestSketch(Scenario)
@Flags(TE)
def uint16_to_field_type(self):
    """Read parquet files with uint16 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=uint16)


@TestSketch(Scenario)
@Flags(TE)
def uint32_to_field_type(self):
    """Read parquet files with uint32 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=uint32)


@TestSketch(Scenario)
@Flags(TE)
def uint64_to_field_type(self):
    """Read parquet files with uint64 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=uint64)


@TestSketch(Scenario)
@Flags(TE)
def int8_to_field_type(self):
    """Read parquet files with int8 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=int8)


@TestSketch(Scenario)
@Flags(TE)
def int16_to_field_type(self):
    """Read parquet files with int16 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=int16)


@TestSketch(Scenario)
@Flags(TE)
def int32_to_field_type(self):
    """Read parquet files with int32 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=int32)


@TestSketch(Scenario)
@Flags(TE)
def int64_to_field_type(self):
    """Read parquet files with int64 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=int64)


@TestSketch(Scenario)
@Flags(TE)
def no_logical_type_to_field_type(self):
    """Read parquet files with no logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    field_type_conversions_with_bloom_filter(logical_type=no_logical_type)


@TestSketch(Scenario)
@Flags(TE)
def utf8_to_key_column_type(self):
    """Read parquet files with utf-8 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=utf8)


@TestSketch(Scenario)
@Flags(TE)
def decimal_to_key_column_type(self):
    """Read parquet files with decimal logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=decimal)


@TestSketch(Scenario)
@Flags(TE)
def date_to_key_column_type(self):
    """Read parquet files with date logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=date)


@TestSketch(Scenario)
@Flags(TE)
def time_millis_to_key_column_type(self):
    """Read parquet files with time-millis logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=time_millis)


@TestSketch
@Flags(TE)
def time_micros_to_key_column_type(self):
    """Read parquet files with time-micros logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=time_micros)


@TestSketch(Scenario)
@Flags(TE)
def timestamp_millis_to_key_column_type(self):
    """Read parquet files with timestamp-millis logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=timestamp_millis)


@TestSketch(Scenario)
@Flags(TE)
def timestamp_micros_to_key_column_type(self):
    """Read parquet files with timestamp-micros logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=timestamp_micros)


@TestSketch(Scenario)
@Flags(TE)
def enum_to_key_column_type(self):
    """Read parquet files with enum logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=enum)


@TestSketch(Scenario)
@Flags(TE)
def map_to_key_column_type(self):
    """Read parquet files with map logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=map)


@TestSketch(Scenario)
@Flags(TE)
def list_to_key_column_type(self):
    """Read parquet files with list logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=list)


@TestSketch(Scenario)
@Flags(TE)
def string_to_key_column_type(self):
    """Read parquet files with string logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=string)


@TestSketch(Scenario)
@Flags(TE)
def map_key_value_to_key_column_type(self):
    """Read parquet files with map key value logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=map_key_value)


@TestSketch(Scenario)
@Flags(TE)
def time_to_key_column_type(self):
    """Read parquet files with time logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=time)


@TestSketch(Scenario)
@Flags(TE)
def integer_to_key_column_type(self):
    """Read parquet files with integer logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=integer)


@TestSketch(Scenario)
@Flags(TE)
def json_to_key_column_type(self):
    """Read parquet files with json logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=json_type)


@TestSketch(Scenario)
@Flags(TE)
def bson_to_key_column_type(self):
    """Read parquet files with bson logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=bson)


@TestSketch(Scenario)
@Flags(TE)
def uuid_to_key_column_type(self):
    """Read parquet files with uuid logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=uuid)


@TestSketch(Scenario)
@Flags(TE)
def interval_to_key_column_type(self):
    """Read parquet files with interval logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=interval)


@TestSketch(Scenario)
@Flags(TE)
def float16_to_key_column_type(self):
    """Read parquet files with float16 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=float16)


@TestSketch(Scenario)
@Flags(TE)
def uint8_to_key_column_type(self):
    """Read parquet files with uint8 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=uint8)


@TestSketch(Scenario)
@Flags(TE)
def uint16_to_key_column_type(self):
    """Read parquet files with uint16 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=uint16)


@TestSketch(Scenario)
@Flags(TE)
def uint32_to_key_column_type(self):
    """Read parquet files with uint32 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=uint32)


@TestSketch(Scenario)
@Flags(TE)
def uint64_to_key_column_type(self):
    """Read parquet files with uint64 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=uint64)


@TestSketch(Scenario)
@Flags(TE)
def int8_to_key_column_type(self):
    """Read parquet files with int8 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=int8)


@TestSketch(Scenario)
@Flags(TE)
def int16_to_key_column_type(self):
    """Read parquet files with int16 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=int16)


@TestSketch(Scenario)
@Flags(TE)
def int32_to_key_column_type(self):
    """Read parquet files with int32 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=int32)


@TestSketch(Scenario)
@Flags(TE)
def int64_to_key_column_type(self):
    """Read parquet files with int64 logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=int64)


@TestSketch(Scenario)
@Flags(TE)
def no_logical_type_to_key_column_type(self):
    """Read parquet files with no logical type with bloom filter enabled and validate that the bloom filter is being used by ClickHouse and data integrity is kept."""
    key_column_type_conversions_with_bloom_filter(logical_type=no_logical_type)


@TestSuite
def sanity_checks(self):
    """Run sanity checks for the bloom filter on parquet files."""
    Scenario(run=read_and_write_file_with_bloom)
    Scenario(run=read_bloom_filter_parquet_files)
    Scenario(run=read_bloom_filter_parquet_files_native_reader)
    Scenario(run=native_reader_array_bloom)
    Scenario(run=supported_expressions)


@TestSuite
def logical_datatypes_key_column_type(self):
    """Running combinatorial checks that validate bloom filter is correctly utilized by ClickHouse for Parquet files with different logical types when using key column type conversion.

    The following query is considered as key column type conversion:

    SELECT integer_column FORM file('file.parquet', Parquet, 'integer_column String') WHERE column = 'value'

    """

    Scenario(run=utf8_to_key_column_type)
    Scenario(run=decimal_to_key_column_type)
    Scenario(run=date_to_key_column_type)
    Scenario(run=time_millis_to_key_column_type)
    Scenario(run=time_micros_to_key_column_type)
    Scenario(run=timestamp_millis_to_key_column_type)
    Scenario(run=timestamp_micros_to_key_column_type)
    Scenario(run=enum_to_key_column_type)
    Scenario(run=map_to_key_column_type)
    Scenario(run=list_to_key_column_type)
    Scenario(run=string_to_key_column_type)
    Scenario(run=map_key_value_to_key_column_type)
    Scenario(run=time_to_key_column_type)
    Scenario(run=integer_to_key_column_type)
    Scenario(run=json_to_key_column_type)
    Scenario(run=bson_to_key_column_type)
    Scenario(run=uuid_to_key_column_type)
    Scenario(run=interval_to_key_column_type)
    Scenario(run=float16_to_key_column_type)
    Scenario(run=uint8_to_key_column_type)
    Scenario(run=uint16_to_key_column_type)
    Scenario(run=uint32_to_key_column_type)
    Scenario(run=uint64_to_key_column_type)
    Scenario(run=int8_to_key_column_type)
    Scenario(run=int16_to_key_column_type)
    Scenario(run=int32_to_key_column_type)
    Scenario(run=int64_to_key_column_type)
    Scenario(run=no_logical_type_to_key_column_type)


@TestSuite
def logical_datatypes_field_type(self):
    """Running combinatorial checks that validate bloom filter is correctly utilized by ClickHouse for Parquet files with different logical types when using field type conversion.

    The following query is considered as field type conversion:

    SELECT xyz FORM file('file.parquet', Parquet) WHERE column = toInt32('value')
    """

    Scenario(run=utf8_to_field_type)
    Scenario(run=decimal_to_field_type)
    Scenario(run=date_to_field_type)
    Scenario(run=time_millis_to_field_type)
    Scenario(run=time_micros_to_field_type)
    Scenario(run=timestamp_millis_to_field_type)
    Scenario(run=timestamp_micros_to_field_type)
    Scenario(run=enum_to_field_type)
    Scenario(run=map_to_field_type)
    Scenario(run=list_to_field_type)
    Scenario(run=string_to_field_type)
    Scenario(run=map_key_value_to_field_type)
    Scenario(run=time_to_field_type)
    Scenario(run=integer_to_field_type)
    Scenario(run=json_to_field_type)
    Scenario(run=bson_to_field_type)
    Scenario(run=uuid_to_field_type)
    Scenario(run=interval_to_field_type)
    Scenario(run=float16_to_field_type)
    Scenario(run=uint8_to_field_type)
    Scenario(run=uint16_to_field_type)
    Scenario(run=uint32_to_field_type)
    Scenario(run=uint64_to_field_type)
    Scenario(run=int8_to_field_type)
    Scenario(run=int16_to_field_type)
    Scenario(run=int32_to_field_type)
    Scenario(run=int64_to_field_type)
    Scenario(run=no_logical_type_to_field_type)


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter("1.0"))
@Name("bloom")
def feature(self, node="clickhouse1", number_of_inserts=1500, stress_bloom=False):
    """Check if we can read from ap parquet file with bloom filter and validate that the bloom filter is being used
    by ClickHouse.

    The combinations used:
        - Check that ClickHouse can read and then write back the parquet files that have bloom filter applied to them.
    Combinatorics:
        statements:
            - "*",
            - "f32",
            - "f64",
            - "int",
            - "str",
            - "fixed_str",
            - "array",
            - "f32,f64,int,str,fixed_str,array",
        settings:
            - input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down=true
            - input_format_parquet_bloom_filter_push_down=false,input_format_parquet_filter_push_down=false
            - input_format_parquet_bloom_filter_push_down=true,input_format_parquet_filter_push_down=false
            - input_format_parquet_bloom_filter_push_down=false,input_format_parquet_filter_push_down=true
        conditions:
            - WHERE
            - OR
            - AND
            - IN
            - NOT IN
            - has()
            - hasAny()
            - hasAll()
        - Check that the bloom filter is being used by ClickHouse when doing conversions like SELECT * FROM file('file.parquet', Parquet) WHERE column = toInt32('value')
            - Check all possible conversions
    """
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "bloom"
    self.context.json_files_local = os.path.join(
        current_dir(), "..", "data", "json_files"
    )
    self.context.json_files = "/json_files"
    self.context.parquet_output_path = "/parquet-files"
    self.context.number_of_inserts = number_of_inserts

    if stress_bloom:
        Feature(run=logical_datatypes_field_type)
        Feature(run=logical_datatypes_key_column_type)
    else:
        Feature(run=sanity_checks)
