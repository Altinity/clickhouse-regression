import time
import json

from testflows.core import *
from testflows.asserts import error
from s3.tests.common import *
from helpers.tables import *


@TestStep(When)
def export_events(self):
    """Get the number of successful parts exports from the system.events table."""
    node = self.context.node
    output = node.query(
        "SELECT name, value FROM system.events WHERE name LIKE '%%Export%%' FORMAT JSONEachRow",
        exitcode=0,
    ).output
    return {
        row["name"]: int(row["value"])
        for row in [json.loads(row) for row in output.splitlines()]
    }


@TestStep(When)
def export_part(self, parts, source, destination):
    """Alter export of parts."""
    node = self.context.node
    for part in parts:
        node.query(
            f"SET allow_experimental_export_merge_tree_part = 1; ALTER TABLE {source.name} EXPORT PART '{part}' TO TABLE {destination.name}",
            # settings=[("allow_experimental_export_merge_tree_part", 1)],
            exitcode=0,
        )


@TestStep(When)
def get_parts(self, table):
    """Get all parts for a table."""
    node = self.context.node
    output = node.query(
        f"SELECT name FROM system.parts WHERE table = '{table.name}'", exitcode=0
    ).output
    return [row.strip() for row in output.splitlines()]


@TestStep(When)
def stop_merges(self, table):
    """Stop merges for a table."""
    node = self.context.node
    node.query(f"SYSTEM STOP MERGES {table.name}", exitcode=0)


@TestScenario
def sanity(self):
    """Check that ClickHouse can export data parts to S3 storage."""
    node = self.context.node

    with Given("I create a source table"):
        source = create_table(
            name="source_table_" + getuid(),
            columns=[
                Column(name="p", datatype=UInt16()),
                Column(name="i", datatype=UInt64()),
            ],
            partition_by="p",
            order_by="tuple()",
            engine="MergeTree",
        )

    with And("I create a destination table"):
        table_name = "destination_table_" + getuid()
        destination = create_table(
            name=table_name,
            columns=[
                Column(name="p", datatype=UInt16()),
                Column(name="i", datatype=UInt64()),
            ],
            partition_by="p",
            engine=f"""
           S3(
              '{self.context.uri}',
              '{self.context.access_key_id}',
              '{self.context.secret_access_key}',
              format='Parquet',
              compression='auto',
              partition_strategy='hive'
            )
        """,
        )

    with And("I turn off merges for source table"):
        stop_merges(source)

    with When("I insert data into the source table"):
        for i in range(10):
            node.query(f"INSERT INTO {source.name} VALUES ({i % 10}, {i})", exitcode=0)

    with And("I get a list of parts for source table"):
        parts = get_parts(source)

    with And("I read current export events"):
        events_before = export_events()

    with When("I export parts to the destination table"):
        for _ in range(10):
            export_part(parts, source, destination)

    with And("I check that all exports are successful"):
        events_after = export_events()
        assert (
            events_after["PartsExports"] == events_before["PartsExports"] + 10
        ), error()


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
