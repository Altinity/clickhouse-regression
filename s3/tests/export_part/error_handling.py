from testflows.core import *
from testflows.asserts import error

from s3.tests.export_part.steps import *
from helpers.tables import *


@TestScenario
def invalid_part_name(self):
    """Check that exporting a non-existent part returns the correct error."""

    with Given("I create source and destination tables"):
        source, destination = create_source_and_destination_tables()

    with When("I insert random test data into the source table"):
        source.insert_test_data() # default row_count=10, cardinality=1

    with And("I create an invalid part name"):
        invalid_part_name = "in_va_lid_part"

    with Then("I try to export the invalid part and expect an error"):
        results = export_part(parts=[invalid_part_name], source=source, destination=destination, exitcode=1)
        assert len(results) == 1, error()
        # note(f"Result: {results[0].output}")
        assert results[0].exitcode == 233, error()
        assert f"Unexpected part name: {invalid_part_name}" in results[0].output, error()


@TestFeature
@Name("error handling")
def feature(self):
    """Check correct error handling when exporting parts."""

    Scenario(run=invalid_part_name)