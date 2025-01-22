import os
import json

from testflows.core import *
from helpers.common import getuid
from parquet.requirements import *
from parquet.tests.steps.general import select_from_parquet


def contains_value(data, target):
    """Recursively check if `target` is contained anywhere in the nested `data`."""
    if isinstance(data, dict):
        return any(contains_value(v, target) for v in data.values())
    elif isinstance(data, list):
        return any(contains_value(item, target) for item in data)
    else:
        return data == target


@TestStep(Given)
def read_metadata_from_file(self, file_name):
    """Read metadata from a parquet file."""

    metadata = select_from_parquet(
        file_name=file_name, file_type="ParquetMetadata", statement="*", format="JSON"
    )

    return metadata


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_ExtraEntries("1.0")
)
def extra_metadata(self):
    """Check that extra metadata that is stored inside the parquet file footer can be read by ClickHouse."""
    node = self.context.node
    file_path = os.path.join("metadata", "example_with_extra_metadata.parquet")
    value_to_find = "Sample Parquet file with extra metadata"

    with Given("I read metadata from the parquet file"):
        data = read_metadata_from_file(file_name=file_path)

    with When("I search for the extra metadata entries in the metadata"):
        data = json.loads(data.output.strip())
        is_present = contains_value(data, value_to_find)
    with Then("I check if the custom metadata is present in the output"):
        assert is_present, "The custom metadata is not present in the output"


@TestFeature
@Name("metadata")
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Metadata("1.0"))
def feature(self, node="clickhouse1"):
    """Tests that check integrity and everything related to metadata files of parquet."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=extra_metadata)
