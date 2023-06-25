import os
from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from helpers.common import *


@TestScenario
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Import_Encoding_Dictionary("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Export_Encoding_Dictionary("1.0"),
)
def binary(self):
    node = self.context.node
    table_name = "table_" + getuid()
    path_to_export = "/var/lib/clickhouse/user_files/dictionary_encoding_exports.Parquet"

    with Given("I have a Parquet file with the Dictionary encoding"):
        dict_encoded_file = os.path.join("arrow", "alltypes_dictionary.parquet")

    with Check("import"):
        with When("I try to import the Dictionary encoded Parquet file into the table"):
            node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS SELECT * FROM file('{dict_encoded_file}', Parquet)
                """
            )

        with And("I read the contents of the created table"):
            read = node.query(
                f'SELECT * FROM {table_name}'
            )

        with Then("I check the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"dictionary_encoded_parquet_examples2",
                    )
                ), error()

    with Check("export"):
        with When("I export the table back into a new parquet file"):
            node.query(
                f"SELECT * FROM {table_name} INTO OUTFILE '{path_to_export}' COMPRESSION 'none' FORMAT Parquet"
            )

        with And("I check the exported Parquet file's contents"):
            read = node.query(
                f"SELECT * FROM file('{path_to_export}', Parquet)"
            )

        with Then("output must match the snapshot", flags=XFAIL):
            with values() as that:
                assert that(
                    snapshot(
                        read.output.strip(),
                        name=f"dictionary_encoded_parquet_examples2",
                    )
                ), error()



@TestFeature
@Name("datatype conversion")
def feature(self, node="clickhouse1"):
    """Check importing and exporting Dictionary encoded parquet files."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()