from testflows.core import *
from testflows.asserts import error

from s3.tests.export_part.steps import *
from helpers.tables import *


# TODO: Large data export?
# But if I add too many rows, there'll be too many partitions given the current implementation -> DB ERROR


@TestScenario
def source_matches_destination(self, engine=None, row_count=10, cardinality=1):
    """Check that ClickHouse can export data parts to S3 storage."""

    with Given("I create source and destination tables"):
        source, destination = create_source_and_destination_tables(engine=engine)

    with When("I insert random test data into the source table"):
        source.insert_test_data(row_count=row_count, cardinality=cardinality)

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


@TestSketch(Scenario)
@Flags(TE)
def combinations(self):
    """Test different combinations of engines, row counts, and cardinalities."""

    engines = [
        "MergeTree",
        "ReplicatedMergeTree",
        "ReplacingMergeTree",
        "SummingMergeTree",
        "AggregatingMergeTree",
    ]
    row_counts = [1, 10]
    cardinalities = [1, 10]

    source_matches_destination(
        engine=either(*engines),
        row_count=either(*row_counts),
        cardinality=either(*cardinalities)
    )


@TestScenario
def multiple_parts(self):
    """Test exporting multiple parts in a single operation."""
    
    with Given("I create source and destination tables"):
        source, destination = create_source_and_destination_tables()
    
    with When("I insert data to create multiple parts"):
        for i in range(5):
            source.insert_test_data()
    
    with And("I get all parts and export them"):
        source_parts = source.get_parts()
        export_part(parts=source_parts, source=source, destination=destination)
    
    with Then("I verify all data was exported correctly"):
        source_data = source.select_ordered_by_partition_and_index()
        destination_data = destination.select_ordered_by_partition_and_index()
        assert source_data == destination_data, error()


@TestScenario
def empty_table(self):
    """Test exporting from an empty table."""
    
    with Given("I create empty source and destination tables"):
        source, destination = create_source_and_destination_tables()
    
    with When("I check for parts in empty table"):
        source_parts = source.get_parts()
        assert len(source_parts) == 0, error()
    
    with Then("I verify destination is also empty"):
        dest_count = destination.query("SELECT count() FROM " + destination.name)
        assert dest_count == "0", error()


@TestFeature
@Name("sanity")
def feature(self):
    """Check basic functionality of exporting data parts to S3 storage."""

    Scenario(run=empty_table)
    Scenario(run=multiple_parts)
    Scenario(run=combinations)