import os

from testflows.core import *

from helpers.common import getuid
from parquet.tests.bloom_filter import (
    copy_parquet_to_user_files,
    prepare_parquet_file,
    generate_parquet_file,
    create_parquet_json_definition,
    save_json_definition,
)
from parquet.tests.common import generate_values
from parquet.tests.outline import import_export
from parquet.tests.steps.bloom_filter import (
    boolean_physical,
    no_logical_type,
    required,
    optional,
    writer_version_1_0,
    writer_version_2_0,
    compression,
    schema_type,
    writer_version,
    clickhouse_datatypes,
    integers,
    int32_physical,
    int64_physical,
    physical_to_logical_annotation,
)
from parquet.tests.steps.general import select_from_parquet
from parquet.tests.steps.arrow import *
from parquet.data.scripts.create_large_footer import create_parquet_with_large_footer


@TestStep(Given)
def read_data_without_native_reader(
    self, parquet_file, statement, node=None, key_column=None, condition=None
):
    """Read data from a parquet file with native reader enabled."""
    if node is None:
        node = self.context.node

    data_without_native_reader = select_from_parquet(
        file_name=parquet_file,
        statement=statement,
        format="TabSeparated",
        settings=f"input_format_parquet_use_native_reader=0",
        order_by="tuple(*)",
        node=node,
        condition=condition,
        key_column=key_column,
    )

    return data_without_native_reader


@TestStep(Given)
def read_data_with_native_reader(
    self, parquet_file, statement, node=None, key_column=None, condition=None
):
    """Read data from a parquet file with native reader enabled."""

    if node is None:
        node = self.context.node

    data_with_native_reader = select_from_parquet(
        file_name=parquet_file,
        statement=statement,
        format="TabSeparated",
        settings=f"input_format_parquet_use_native_reader=1",
        order_by="tuple(*)",
        node=node,
        condition=condition,
        key_column=key_column,
    )
    return data_with_native_reader


@TestStep(Given)
def read_data_with_and_without_native_reader(
    self,
    parquet_file,
    statement,
    node=None,
    key_column=None,
    condition=None,
):
    """Read data from a parquet file with and without native reader enabled."""

    if node is None:
        node = self.context.node

    data_without_native_reader = read_data_without_native_reader(
        parquet_file=parquet_file,
        statement=statement,
        node=node,
        key_column=key_column,
        condition=condition,
    )

    data_with_native_reader = read_data_with_native_reader(
        parquet_file=parquet_file,
        statement=statement,
        node=node,
        key_column=key_column,
        condition=condition,
    )
    return data_without_native_reader, data_with_native_reader


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
        data = generate_values(physical_type()["physicalType"], 15)
        column_name = physical_type()["physicalType"].lower()
    else:
        data = generate_values(logical_type()["logicalType"], 15)
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
    )

    save_json_definition(path=path, file_definition=file_definition)

    return json_file_name, parquet_file, column_name, data


@TestStep(Given)
def handle_conversion_error(
    self, parquet_file, condition=None, node=None, key_column=None, statement="*"
):
    """Handle errors during conversion check and return whether to proceed."""

    if node is None:
        node = self.context.node

    check_conversion = select_from_parquet(
        file_name=parquet_file,
        statement="*",
        condition=condition,
        format="TabSeparated",
        settings=f"input_format_parquet_use_native_reader=0",
        order_by="tuple(*)",
        node=node,
        no_checks=True,
        key_column=key_column,
    )
    return check_conversion.exitcode == 0


@TestCheck
def check_datatypes(
    self,
    schema_type,
    writer_version,
    physical_type,
    logical_type,
    compression_value,
    key_column,
):
    """Check that the ClickHouse can read a Parquet file with given column type when native reader is enabled."""
    with Given("I prepare the parquet file"):
        json_file_name, parquet_file, column_name, data = prepare_parquet_file(
            schema_type=schema_type,
            writer_version=writer_version,
            physical_type=physical_type,
            logical_type=logical_type,
            compression_value=compression_value,
        )

    with And("I generate the parquet file"):
        generate_parquet = generate_parquet_file(json_file_name=json_file_name)

    with Then("I check if the parquet can be read"):
        if generate_parquet.exitcode != 0:
            skip("Incorrect JSON file structure")

        with By("copying the parquet file into the user files directory"):
            copy_parquet_to_user_files(parquet_file=parquet_file)

        with And("reading the data with and without native reader enabled"):
            key_column = (
                f"{column_name} {key_column}" if key_column is not None else None
            )

            check_conversion = handle_conversion_error(
                parquet_file=parquet_file, key_column=key_column
            )

            if not check_conversion:
                skip(f"Incorrect conversion {logical_type.__name__} to {key_column}")

            data_without_native_reader, data_with_native_reader = (
                read_data_with_and_without_native_reader(
                    parquet_file=parquet_file, statement="*", key_column=key_column
                )
            )

        with And("checking that the data with and without native reader is the same"):
            if not check_conversion:
                skip(f"Incorrect conversion {column_name} to {key_column}")
            if (
                "DB::Exception: Unsupported encoding"
                in data_with_native_reader.output.strip()
            ):
                skip("Unsupported encoding")

            assert (
                data_without_native_reader.output.strip()
                == data_with_native_reader.output.strip()
            ), f"Data with and without native reader is different: {data_without_native_reader.output.strip()} != {data_with_native_reader.output.strip()}"


@TestScenario
def max_message_size(self):
    """Check that ClickHouse can read a Parquet file with a large message size."""

    with Given("I create a parquet file with a large footer"):
        filename = create_parquet_with_large_footer()
    with Then("I check if the parquet file can be read"):
        import_export(
            snapshot_name="max_message_size",
            import_file=filename,
            settings=[("input_format_parquet_use_native_reader_v3", 1)],
        )


@TestSketch(Scenario)
@Flags(TE)
def boolean_support(self):
    """Check that the ClickHouse can read a Parquet file with boolean column when native reader is enabled."""
    schema_types = [required, optional]
    key_columns = clickhouse_datatypes
    key_columns.append(None)
    check_datatypes(
        schema_type=either(*schema_types),
        writer_version=either(*writer_version),
        physical_type=boolean_physical,
        logical_type=no_logical_type,
        compression_value=either(*compression),
        key_column=either(*key_columns),
    )


@TestSketch
@Flags(TE)
def integer_support(self):
    """Check that the ClickHouse can read a Parquet file with integer column when native reader is enabled."""
    schema_types = [required, optional]
    key_columns = clickhouse_datatypes
    key_columns.append(None)

    key_columns = either(*key_columns)
    schemas = either(*schema_types)
    writer_versions = either(*writer_version)
    compressions = either(*compression)

    for physical_type in [int32_physical, int64_physical]:
        for logical_type in integers:
            check_datatypes(
                schema_type=schemas,
                writer_version=writer_versions,
                physical_type=physical_type,
                logical_type=logical_type,
                compression_value=compressions,
                key_column=key_columns,
            )


@TestScenario
def page_header_v2(self):
    """Check that the ClickHouse can read a Parquet file with page header version 2."""
    path = os.path.join("data", "arrow")
    header_v2_files = [
        boolean_header_v2,
        int32_header_v2,
        int64_header_v2,
        float32_header_v2,
        float64_header_v2,
        string_header_v2,
        binary_header_v2,
        timestamp_header_v2,
        list_header_v2,
        struct_header_v2,
    ]

    for file in header_v2_files:
        with Given(f"I create a parquet file {file.__name__}"):
            file_path = file(file_path=path)

        with Then("I check if the parquet file can be read"):
            import_export(
                snapshot_name=file.__name__,
                import_file=file_path.rsplit("/")[-1],
                settings="input_format_parquet_use_native_reader=1",
            )


@TestFeature
@Name("native reader")
def feature(self, node="clickhouse1"):
    """Check that the ClickHouse can read a Parquet file when native reader is enabled."""
    self.context.snapshot_id = "native_reader"
    self.context.node = self.context.cluster.node(node)
    self.context.json_files_local = os.path.join(
        current_dir(), "..", "data", "json_files"
    )
    self.context.json_files = "/json_files"
    self.context.parquet_output_path = "/parquet-files"

    Scenario(run=boolean_support)
    Scenario(run=integer_support)
    Scenario(run=page_header_v2)
    Scenario(run=max_message_size)
