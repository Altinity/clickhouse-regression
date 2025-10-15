import os

from testflows.core import *

from helpers.common import getuid
from parquet.tests.common import generate_values
from parquet.tests.steps.bloom_filter import (
    compression as compression_steps,
    schema_type as schema_types,
    writer_version as writer_versions,
    physical_to_logical_annotation,
    binary_physical,
    fixed_len_byte_array_physical_16,
    fixed_len_byte_array_physical_2,
    int32_physical,
    int64_physical,
)
from parquet.tests.steps.general import (
    create_and_save_parquet_json_definition,
    generate_parquet_file,
)


@TestStep(Given)
def setup_parquet_structure(
    self,
    schema_type,
    writer_version,
    physical_type,
    logical_type,
    compression_value,
    bloom_filter,
    number_of_inserts=150,
    json_file_location=None,
):
    """Prepare the JSON definition and determine necessary parameters for the parquet file."""

    if json_file_location is None:
        json_file_location = os.path.join(current_dir(), "..", "data", "json_files")

    self.context.json_files = "/json_files"
    self.context.parquet_output_path = "/parquet-files"

    json_file_name = (
        f"{compression_value()['compression']}_{physical_type()['physicalType']}_"
        f"{logical_type()['logicalType']}_" + getuid() + ".json"
    )
    path = json_file_location + "/" + json_file_name

    if logical_type()["logicalType"] == "NONE":
        if physical_type()["physicalType"] == "FIXED_LEN_BYTE_ARRAY":
            datatype = (
                physical_type()["physicalType"] + f"({physical_type()['length']})"
            )
            note(f"datatype: {datatype}")
            data = generate_values(datatype, number_of_inserts, True)
        else:
            data = generate_values(
                physical_type()["physicalType"], number_of_inserts, True
            )
    else:
        if logical_type()["logicalType"] == "FIXED_LEN_BYTE_ARRAY":
            datatype = logical_type()["logicalType"] + f"({logical_type()['length']})"
        else:
            datatype = logical_type()["logicalType"]

        data = generate_values(datatype, number_of_inserts, True)

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
        enable_bloom_filter=bloom_filter,
    )

    return json_file_name, file_definition


@TestCheck
def generate_parquet_file_from_json(
    self,
    schema_type,
    writer_version,
    physical_type,
    logical_type,
    compression_value,
    bloom_filter,
):
    """Generate the parquet file from its JSON definition."""

    with Given("the parquet structure is set up"):
        json_file_name, file_definition = setup_parquet_structure(
            schema_type=schema_type,
            writer_version=writer_version,
            physical_type=physical_type,
            logical_type=logical_type,
            compression_value=compression_value,
            bloom_filter=bloom_filter,
        )
    json_files = "/json_files"
    json_file_path = json_files + "/" + json_file_name
    generate_parquet_file(json_file_path=json_file_path)


def _generate_files_for_physical_types(self, physical_types):
    """Helper function to generate files for a list of physical types."""
    for physical_func in physical_types:
        if physical_func in physical_to_logical_annotation:
            for logical_func in physical_to_logical_annotation[physical_func]:
                for compression_func in compression_steps:
                    for schema_func in schema_types:
                        for writer_func in writer_versions:
                            for enable_bf in (True, False):
                                generate_parquet_file_from_json(
                                    schema_type=schema_func,
                                    writer_version=writer_func,
                                    physical_type=physical_func,
                                    logical_type=logical_func,
                                    compression_value=compression_func,
                                    bloom_filter=enable_bf,
                                )


@TestSketch
def generate_first_part_files(self):
    """Generate parquet files for binary, fixed_len_byte_array_16, and fixed_len_byte_array_2 physical types."""
    _generate_files_for_physical_types(
        self,
        [
            binary_physical,
            fixed_len_byte_array_physical_16,
            fixed_len_byte_array_physical_2,
        ],
    )


@TestSketch
def generate_second_part_files(self):
    """Generate parquet files for int32 and int64 physical types."""
    _generate_files_for_physical_types(self, [int32_physical, int64_physical])


@TestSketch
def generate_third_part_files(self):
    """Generate parquet files for remaining physical types."""
    excluded_physicals = {
        binary_physical,
        fixed_len_byte_array_physical_16,
        fixed_len_byte_array_physical_2,
        int32_physical,
        int64_physical,
    }

    remaining_physicals = [
        physical_func
        for physical_func in physical_to_logical_annotation.keys()
        if physical_func not in excluded_physicals
    ]

    _generate_files_for_physical_types(self, remaining_physicals)


@TestScenario
def run_first_part_files(self):
    """Run the first part: binary_physical, fixed_len_byte_array_physical_16, fixed_len_byte_array_physical_2."""
    generate_first_part_files()


@TestScenario
def run_second_part_files(self):
    """Run the second part: int32_physical, int64_physical."""
    generate_second_part_files()


@TestScenario
def run_third_part_files(self):
    """Run the third part: remaining physical types."""
    generate_third_part_files()


@TestScenario
def run_all_possible_files(self, pool=3):
    """Run the feature to generate all possible parquet files."""

    with Pool(pool) as pool:
        Scenario(
            run=run_first_part_files,
            parallel=True,
            executor=pool,
        )
        Scenario(
            run=run_second_part_files,
            parallel=True,
            executor=pool,
        )
        Scenario(
            run=run_third_part_files,
            parallel=True,
            executor=pool,
        )
        join()

