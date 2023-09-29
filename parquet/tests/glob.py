import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from parquet.tests.outline import import_export
from helpers.common import *

glob1 = os.path.join("glob")
glob3 = os.path.join("glob3")


@TestOutline
def select_with_glob(self, query, snapshot_name):
    node = self.context.node
    table_name = "table_" + getuid()

    with Check("Import"):
        with When(
            "I run the SELECT query with the glob pattern inside the Parquet file path"
        ):
            select_file = node.query(
                f"""
            SELECT * FROM {query} ORDER BY j
            """
            )

        with Then("I check that the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        select_file.output.strip(),
                        name=f"select_from_file_with_{snapshot_name}",
                    )
                ), error()

        with And(
            "I create a ClickHouse table and import Parquet files using glob patterns"
        ):
            create_table = node.query(
                f"""
                CREATE TABLE {table_name}
                ENGINE = MergeTree
                ORDER BY tuple() AS
                SELECT *
                FROM {query}
                """
            )

            table_values = node.query(f"SELECT * FROM {table_name} ORDER BY tuple(*)")

        with Then("I check that the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        table_values.output.strip(),
                        name=f"create_table_with_{snapshot_name}",
                    )
                ), error()


@TestScenario
@Examples(
    "query snapshot_name",
    rows=[
        (f"file('{glob1}/*', Parquet)", "asterisk"),
        (f"file('{glob1}/**', Parquet)", "globstar"),
        (f"file('{glob1}/t?.parquet', Parquet)", "question_mark"),
        (f"file('{glob1}/t{{1..2}}.parquet', Parquet)", "range"),
    ],
)
def glob1(self):
    """Importing multiple Parquet files using the glob patterns from a single directory."""
    for example in self.examples:
        select_with_glob(query=example[0], snapshot_name=example[1])


@TestScenario
@Examples(
    "query snapshot_name",
    rows=[
        (f"file('{glob3}/?/dir/*', Parquet)", "nested_glob_1"),
        (f"file('{glob3}/?/dir/**', Parquet)", "nested_glob_2"),
        (f"file('{glob3}/?/???/**', Parquet)", "nested_glob_3"),
        (
            f"file('{glob3}/?/dir/*{{p,a,r,q,u,e,t}}', Parquet)",
            "nested_glob_4",
        ),
        (f"file('{glob3}/?/y.*', Parquet)", "single_nested_glob"),
    ],
)
def glob2(self):
    """Importing multiple Parquet files using the glob patterns from multiple nested directories."""
    for example in self.examples:
        select_with_glob(query=example[0], snapshot_name=example[1])


@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_Glob_MultiDirectory("1.0"))
@TestScenario
def glob_with_multiple_elements(self):
    select_with_glob(
        query="file('{glob3/c/dir/z, glob/t1, glob3/a/dir/x, glob3/b/y}.parquet')",
        snapshot_name="glob_with_multiple_elements",
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_Glob("1.0"))
@Name("glob")
def feature(self, node="clickhouse1"):
    """Check glob patterns when importing from multiple Parquet files."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
