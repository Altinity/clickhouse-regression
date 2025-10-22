from testflows.core import *
from testflows.asserts import error

from s3.tests.export_part.steps import *
from helpers.tables import *


@TestScenario
def sanity(self):
    """Check that ClickHouse can export data parts to S3 storage."""

    with Given("I create source and destination tables"):
        source, destination = create_source_and_destination_tables()

    with When("I insert random test data into the source table"):
        source.insert_test_data() # default row_count=10, cardinality=1

    with And("I get a list of parts for source table"):
        source_parts = source.get_parts()

    with And("I read current export events"):
        events_before = export_events()

    with And("I export parts to the destination table"):
        export_part(parts=source_parts, source=source, destination=destination)

    with Then("I check system.events that all exports are successful"):
        events_after = export_events()
        total_exports_after = events_after.get("PartsExports", 0) + events_after.get("PartsExportDuplicated", 0)
        total_exports_before = events_before.get("PartsExports", 0) + events_before.get("PartsExportDuplicated", 0)
        assert total_exports_after == total_exports_before + len(source_parts), error()

    with And("I read back data and assert destination matches source"):
        destination_data = destination.select_ordered_by_partition_and_index()
        source_data = source.select_ordered_by_partition_and_index()
        assert destination_data == source_data, error()


@TestFeature
@Name("sanity")
def feature(self):
    """Check basic functionality of exporting data parts to S3 storage."""

    Scenario(run=sanity)