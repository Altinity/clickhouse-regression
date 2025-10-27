from testflows.core import *
from testflows.asserts import error

from s3.tests.export_part.steps import *


# TODO checks on export_events should go here, not in sanity.py
# partsexports incrementing correctly
# duplicates incrementing correctly

@TestScenario
def duplicate_exports(self):
    """Check duplicate export attempts are properly tracked in system.events."""

    with Given("I create source and destination tables"):
        source, destination = create_source_and_destination_tables()

    with When("I insert random test data into the source table"):
        source.insert_test_data()  # default row_count=10, cardinality=1

    with And("I get a list of parts for source table"):
        source_parts = source.get_parts()
        test_part = source_parts[1]

    with And("I read initial export events"):
        events_initial = export_events()
        initial_exports = events_initial.get("PartsExports", 0)
        initial_duplicates = events_initial.get("PartsExportDuplicated", 0)

    with When("I export the same part twice"):
        export_part(parts=[test_part], source=source, destination=destination)
        export_part(parts=[test_part], source=source, destination=destination)

    with Then("I check system.events for duplicate tracking"):
        events_final = export_events()
        final_exports = events_final.get("PartsExports", 0)
        final_duplicates = events_final.get("PartsExportDuplicated", 0)

    with By("Checking we have 1 successful export"):
        assert final_exports - initial_exports == 1, error()

    with And("Checking we have 1 duplicate export"):
        assert final_duplicates - initial_duplicates == 1, error()


@TestFeature
@Name("system monitoring")
def feature(self):
    """Check system monitoring of export events."""

    Scenario(run=duplicate_exports)
