import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Metadata_ParquetMetadata_MinMax("1.0"))
def bigtuplewithnulls(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = f"/var/lib/clickhouse/user_files/zero_offset_{table_name}.parquet"

    with Given(
        "I have a Parquet file with the zero offset zero. min and max are the same value."
    ):
        import_file = os.path.join("arrow", "dict-page-offset-zero.parquet")

    with And("I save file structure"):
        structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

        with values() as that:
            assert that(
                snapshot(structure.output.strip(), name="zero_offset_describe")
            ), error()

    with Check("import"):
        with When("I try to import the Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{import_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(f"SELECT * FROM {table_name}")

        with Then("I check the output is correct"):
            with values() as that:
                assert that(snapshot(read.output.strip(), name="zero_offset")), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(f"SELECT * FROM file('{path_to_export}', Parquet)")

        with Then("output must match the snapshot"):
            with values() as that:
                assert that(snapshot(read.output.strip(), name="zero_offset")), error()

        with And("I save file structure after export"):
            structure = node.query(f"DESCRIBE TABLE file('{import_file}')")

            with values() as that:
                assert that(
                    snapshot(structure.output.strip(), name="zero_offset_describe")
                ), error()


@TestFeature
@Name("indexing")
def feature(self, node="clickhouse1"):
    """Check importing and exporting parquet files with indexing."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
