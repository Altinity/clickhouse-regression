import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from parquet.tests.bloom_filter import (
    copy_parquet_to_user_files,
    open_client,
    get_total_rows,
    get_file_structure,
    total_number_of_rows,
)
from parquet.tests.common import generate_values, generate_unique_value
from parquet.tests.outline import import_export
from helpers.common import *
from parquet.tests.steps.bloom_filter import (
    schema_type,
    writer_version,
    physical_types,
    logical_types,
    compression,
    simple_logical_types,
)
from parquet.tests.steps.general import (
    parquetify,
    create_and_save_parquet_json_definition,
    generate_parquet_file,
    select_from_parquet,
    rows_read,
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

    file_definition = create_and_save_parquet_json_definition(
        path=path,
        schema_type=schema_type,
        writer_version=writer_version,
        physical_type=physical_type,
        logical_type=logical_type,
        compression_value=compression_value,
        parquet_file=parquet_file,
        data=data,
    )

    snapshot_name = (
        f"{file_definition['options']['compression']}_{physical_type()['physicalType']}_"
        f"{logical_type()['logicalType']}_{file_definition['schema'][0]['schemaType']}_"
        f"{file_definition['options']['writerVersion'].replace('.', '_')}"
    )

    return json_file_name, file_definition, data, column_name, snapshot_name


@TestStep(Given)
def generate_parquet_file_from_json(
    self,
    schema_type,
    writer_version,
    physical_type,
    logical_type,
    compression_value,
):
    """Generate the parquet file from its JSON definition."""
    json_file_name, file_definition, data, column_name, snapshot_name = (
        prepare_parquet_file(
            schema_type=schema_type,
            writer_version=writer_version,
            physical_type=physical_type,
            logical_type=logical_type,
            compression_value=compression_value,
        )
    )

    json_file_path = self.context.json_files + "/" + json_file_name

    parquetify_output = generate_parquet_file(json_file_path=json_file_path)

    return file_definition, parquetify_output.exitcode, data, column_name, snapshot_name


@TestStep(Then)
def verify_rows_read(
    self,
    data,
    initial_rows,
    file_structure,
    snapshot_name,
    condition,
    condition_1,
    condition_2,
):
    """Verify the number of rows read from the parquet file."""
    condition_names = {">": "greater_than", "<": "less_than", ">=": "greater_than_or_equal", "<=": "less_than_or_equal", "!=": "not_equal", "=": "equal", "IN": "in", "NOT IN": "not_in"}

    read_rows = rows_read(data.output, client=False)
    snapshot(
        f"rows_read: {read_rows}, initial_rows: {initial_rows}, file_structure: {file_structure.output}, "
        f"condition: {condition}",
        name=f"{snapshot_name}_{condition_names[condition_1]}_{condition_names[condition_2]}",
        id=self.context.snapshot_id,
        # mode=snapshot.CHECK,
    )


@TestCheck
def check_bloom_and_min_max_evaluation(
    self,
    schema_type,
    writer_version,
    physical_type,
    logical_type,
    compression_value,
    condition_1,
    condition_2,
):
    """Check that bloom filter and min/max indexes are evaluated when used together."""
    node = self.context.node

    with Given("I generate a Parquet file"):
        (
            file_definition,
            parquetify_exitcode,
            data,
            column_name,
            snapshot_name,
        ) = generate_parquet_file_from_json(
            schema_type=schema_type,
            writer_version=writer_version,
            physical_type=physical_type,
            logical_type=logical_type,
            compression_value=compression_value,
        )

        parquet_file = file_definition["fileName"]

    with When("I copy the parquet file to the user files directory"):
        if parquetify_exitcode != 0:
            skip("Incorrect JSON file structure")

        copy_parquet_to_user_files(parquet_file=parquet_file)

    with And("I get the total number of rows in the parquet file"):
        if parquetify_exitcode != 0:
            skip("Incorrect JSON file structure")
        initial_rows = total_number_of_rows(file_name=parquet_file, client=False)

    with And("I run a query with the bloom filter and min/max indexes"):
        if parquetify_exitcode != 0:
            skip("Incorrect JSON file structure")

        datatype = (
            logical_type()["logicalType"]
            if logical_type()["logicalType"] != "NONE"
            else physical_type()["physicalType"]
        )

        if condition_1 in ["IN", "NOT IN"]:
            data_1 = f"['{data[len(data) // 2]}']"
        else:
            data_1 = f"'{data[len(data) // 2]}'"

        if condition_2 in ["IN", "NOT IN"]:
            data_2 = f"['{generate_unique_value(datatype, data)}']"
        else:
            data_2 = f"'{generate_unique_value(datatype, data)}'"

        condition = f"WHERE {column_name} {condition_1} {data_1} or {column_name} {condition_2} {data_2}"
        results = select_from_parquet(
            file_name=parquet_file,
            format="Json",
            settings="input_format_parquet_filter_push_down=true, input_format_parquet_bloom_filter_push_down=true",
            order_by="tuple(*)",
            condition=condition,
        )

        file_structure = get_file_structure(parquet_file=parquet_file)

    with Then("I check the number of rows read"):
        if parquetify_exitcode != 0:
            skip("Incorrect JSON file structure")
        verify_rows_read(
            data=results,
            initial_rows=initial_rows,
            file_structure=file_structure,
            condition=condition,
            condition_1=condition_1,
            condition_2=condition_2,
            snapshot_name=snapshot_name,
        )


@TestSketch(Scenario)
def bloom_filter_and_min_max_evaluation(self):
    """Check that the bloom filer and min/max evaluation work together when reading from a Parquet file."""
    conditions = ["=", "!=", "IN", "NOT IN", ">", "<", ">=", "<="]

    check_bloom_and_min_max_evaluation(
        schema_type=either(*schema_type),
        writer_version=either(*writer_version),
        physical_type=either(*physical_types),
        logical_type=either(*simple_logical_types),
        compression_value=either(*compression),
        condition_1=either(*conditions),
        condition_2=either(*conditions),
    )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_MinMax("1.0"))
def bigtuplewithnulls(self):
    """Checking importing and exporting a parquet file with Min/Max values where offset between Min and Max is zero."""
    with Given("I have a Parquet file with the zero offset between min and max"):
        import_file = os.path.join("arrow", "dict-page-offset-zero.parquet")

    import_export(
        snapshot_name="min_max_zero_offset_structure", import_file=import_file
    )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Indexes_BloomFilter("1.0"))
def bloom_filter(self):
    """Checking importing and exporting a parquet file with bloom filters applied to it."""
    with Given("I have a Parquet file with the bloom filter"):
        import_file = os.path.join(
            "filters", "data_index_bloom_encoding_with_length.parquet"
        )

    import_export(snapshot_name="bloom_filter_structure", import_file=import_file)


@TestFeature
@Name("indexing")
def feature(self, node="clickhouse1", number_of_inserts=1500):
    """Check importing and exporting parquet files with indexing."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "indexing"
    self.context.json_files_local = os.path.join(
        current_dir(), "..", "data", "json_files"
    )
    self.context.json_files = "/json_files"
    self.context.parquet_output_path = "/parquet-files"
    self.context.number_of_inserts = number_of_inserts

    for scenario in loads(current_module(), Scenario):
        scenario()
