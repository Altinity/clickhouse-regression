from testflows.core import *
from testflows.asserts import error

from helpers.tables import *
from s3.tests.common import *
from s3.tests.export_part.steps import *


@TestScenario
def sanity(self):
    """Check that ClickHouse can export data parts to S3 storage."""

    with Given("I create a source table"):
        source = create_source_table()

    with And("I create a destination table"):
        destination = create_destination_table(source=source)

    with And("I turn off merges for source table"):
        source.stop_merges()

    with When("I insert test data into the source table"):
        source.insert_test_data(row_count=10, cardinality=1)

    with And("I get a list of parts for source table"):
        parts = source.get_parts()

    with And("I read current export events"):
        events_before = export_events()

    with And("I export parts to the destination table"):
        export_part(parts=parts, source=source, destination=destination)

    with Then("I check system.events that all exports are successful"):
        events_after = export_events()
        assert events_after["PartsExports"] == events_before.get(
            "PartsExports", 0
        ) + len(parts), error()

    # FIXME: read back data and assert destination matches source


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

    with Given("a temporary s3 path"):
        temp_s3_path = temporary_bucket_path(
            bucket_prefix=f"{bucket_prefix}/export_part"
        )

        self.context.uri = f"{uri}export_part/{temp_s3_path}/"
        self.context.bucket_path = f"{bucket_prefix}/export_part/{temp_s3_path}"

    outline()
