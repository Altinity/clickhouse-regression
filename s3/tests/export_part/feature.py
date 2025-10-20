import random

from testflows.core import *
from testflows.asserts import error

from helpers.tables import *
from s3.tests.common import *
from s3.tests.export_part.steps import *


# TODO: Simplify tests by using the same source and destination tables for all scenarios?
    # Is this better than using different tables for each scenario?
# Regardless, I think the tests can be cleaned up. Maybe create a "setup" step for making
    # source/destination tables, turning off merges, inserting test data, etc.
# Also, the insert_test_data function is not actually random (relies on a seed), so it will insert
    # the same data which can cause exports to fail if the part name is the same.
    # This can be seen by running sanity after duplicate_exports.

@TestScenario
def sanity(self):
    """Check that ClickHouse can export data parts to S3 storage."""

    with Given("I create a source table"):
        source = create_source_table()

    with And("I create a destination table"):
        destination = create_destination_table(source=source)

    with And("I turn off merges for source table"):
        source.stop_merges()

    with When("I insert random test data into the source table"):
        source.insert_test_data(random=random.Random(0)) # default row_count=10, cardinality=1

    with And("I get a list of parts for source table"):
        source_parts = source.get_parts()

    with And("I read current export events"):
        events_before = export_events()

    with And("I export parts to the destination table"):
        note(f"Exporting parts: {source_parts}")
        note(f"Source table: {source.name}")
        note(f"Destination table: {destination.name}")
        export_part(parts=source_parts, source=source, destination=destination)

    with Then("I check system.events that all exports are successful"):
        events_after = export_events()
        note(f"Events before: {events_before}")
        note(f"Events after: {events_after}")
        total_exports_after = events_after.get("PartsExports", 0) + events_after.get("PartsExportDuplicated", 0)
        total_exports_before = events_before.get("PartsExports", 0) + events_before.get("PartsExportDuplicated", 0)
        assert total_exports_after == total_exports_before + len(source_parts), error()

    with And("I read back data and assert destination matches source"):
        destination_data = destination.select_ordered_by_partition_and_index()
        source_data = source.select_ordered_by_partition_and_index()
        note(f"Destination data: {destination_data}")
        note(f"Source data: {source_data}")
        assert destination_data == source_data, error()


@TestScenario
def invalid_part_name(self):
    """Check that exporting a non-existent part returns the correct error."""

    with Given("I create a source table"):
        source = create_source_table()

    with And("I create a destination table"):
        destination = create_destination_table(source=source)

    with And("I turn off merges for source table"):
        source.stop_merges()

    with When("I insert random test data into the source table"):
        source.insert_test_data(random=random.Random(1)) # default row_count=10, cardinality=1

    with And("I create an invalid part name"):
        invalid_part_name = "in_va_lid_part"

    with Then("I try to export the invalid part and expect an error"):
        results = export_part(parts=[invalid_part_name], source=source, destination=destination, exitcode=1)
        assert len(results) == 1, error()
        # note(f"Result: {results[0].output}")
        assert results[0].exitcode == 233, error()
        assert f"Unexpected part name: {invalid_part_name}" in results[0].output, error()


@TestScenario
def duplicate_exports(self):
    """Check that duplicate export attempts are properly tracked in system.events."""

    with Given("I create a source table"):
        source = create_source_table()

    with And("I create a destination table"):
        destination = create_destination_table(source=source)

    with And("I turn off merges for source table"):
        source.stop_merges()

    with When("I insert random test data into the source table"):
        source.insert_test_data(random=random.Random(2)) # default row_count=10, cardinality=1

    with And("I get a list of parts for source table"):
        source_parts = source.get_parts()
        test_part = source_parts[1]

    with And("I read initial export events"):
        events_initial = export_events()
        initial_exports = events_initial.get("PartsExports", 0)
        initial_duplicates = events_initial.get("PartsExportDuplicated", 0)
        note(f"Initial events - Exports: {initial_exports}, Duplicates: {initial_duplicates}")

    with When("I export the same part twice"):
        note(f"Exporting part: {test_part}")
        note(f"Source table: {source.name}")
        note(f"Destination table: {destination.name}")
        # Export same part twice
        export_part(parts=[test_part], source=source, destination=destination)
        export_part(parts=[test_part], source=source, destination=destination)

    with Then("I check system.events for duplicate tracking"):
        events_final = export_events()
        final_exports = events_final.get("PartsExports", 0)
        final_duplicates = events_final.get("PartsExportDuplicated", 0)
        
        note(f"Final events - Exports: {final_exports}, Duplicates: {final_duplicates}")
        # 1 successful export
        assert final_exports - initial_exports == 1, error()
        # 1 of the exports was counted as a duplicate
        assert final_duplicates - initial_duplicates == 1, error()


@TestOutline(Feature)
@Requirements(
    # TBD
)
def outline(self):
    """Run export part scenarios."""

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)


@TestFeature
@Requirements()
@Name("export part")
def minio(self, uri, bucket_prefix):
    self.context.uri_base = uri
    self.context.bucket_prefix = bucket_prefix

    with Given("a temporary s3 path"):
        create_temp_bucket()

    outline()
