import os
import json

from testflows.asserts import values
from testflows.core import *
from testflows.asserts import snapshot, values, error

from helpers.common import getuid
from parquet.requirements import *
from parquet.tests.bloom_filter import copy_parquet_to_user_files, generate_parquet_file
from parquet.tests.common import generate_non_random_values
from parquet.tests.native_reader import prepare_parquet_file
from parquet.tests.steps.bloom_filter import (
    required,
    writer_version_1_0,
    physical_to_logical_annotation,
    snappy_compression,
)
from parquet.tests.steps.general import (
    select_from_parquet,
    create_parquet_json_definition,
    save_json_definition,
    get_parquet_structure,
)


@TestStep(Given)
def read_data_for_snapshot(self, parquet_file, node=None):
    """Read data from a parquet file in a corresponding format to save in a snapshot."""
    if node is None:
        node = self.context.node

    data = select_from_parquet(
        file_name=parquet_file,
        statement="*",
        format="TSV",
        order_by="tuple(*)",
        node=node,
        settings="input_format_parquet_filter_push_down=false",
    )

    return data


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
        data = generate_non_random_values(
            physical_type()["physicalType"], physical_type()
        )
        column_name = physical_type()["physicalType"].lower()
    else:
        data = generate_non_random_values(
            logical_type()["logicalType"], physical_type()
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
        data=[data],
    )

    save_json_definition(path=path, file_definition=file_definition)

    return json_file_name, parquet_file, column_name, data


@TestCheck
def data_conversion(
    self,
    physical_type,
    logical_type,
):
    """Check that the ClickHouse can read a Parquet file with given column type when native reader is enabled."""
    with Given("I prepare the parquet file"):
        json_file_name, parquet_file, column_name, data = prepare_parquet_file(
            schema_type=required,
            writer_version=writer_version_1_0,
            physical_type=physical_type,
            logical_type=logical_type,
            compression_value=snappy_compression,
        )

    with And("I generate the parquet file"):
        generate_parquet_file(json_file_name=json_file_name)

    with Then("I check if the parquet can be read"):
        with By("copying the parquet file into the user files directory"):
            copy_parquet_to_user_files(parquet_file=parquet_file)

        with And("reading the data from the parquet file"):
            data_from_parquet = read_data_for_snapshot(parquet_file=parquet_file)
            schema_from_parquet = get_parquet_structure(file_name=parquet_file)

        with And("saving the snapshot of data from clickhouse and parquetify"):
            snapshot_value = f"ClickHouse: data [{data_from_parquet.output.strip()}] schema {schema_from_parquet.output.strip()}, parquetify data [{data}] schema {logical_type()['logicalType']}"
            snapshot_name = f"physical_{physical_type.__name__}_logical_{logical_type()['logicalType']}"
            with values() as that:
                assert that(
                    snapshot(
                        snapshot_value,
                        name=snapshot_name,
                        mode=snapshot.UPDATE,
                    )
                ), error()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Conversion("1.0"))
def all_datatypes(self):
    """Check the conversion of datatypes when we generate a parquet file using parquetify and then read that file from ClickHouse."""

    for physical_type in physical_to_logical_annotation:
        for logical_type in physical_to_logical_annotation[physical_type]:
            data_conversion(physical_type=physical_type, logical_type=logical_type)


@TestFeature
@Name("data conversion")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Supported("1.0"))
def feature(self, node="clickhouse1"):
    """Tests that check integrity and everything related to metadata files of parquet."""
    self.context.snapshot_id = "data_conversion"
    self.context.node = self.context.cluster.node(node)

    Scenario(run=all_datatypes)
