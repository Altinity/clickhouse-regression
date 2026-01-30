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
def select_with_glob(
    self,
    query,
    snapshot_name,
    columns=None,
    order_by=None,
    suspicious_low_cardinality=False,
):
    node = self.context.node
    table_name = "table_" + getuid()

    if suspicious_low_cardinality:
        suspicious_low_cardinality = [("allow_suspicious_low_cardinality_types", 1)]

    with Check("Import"):
        with When(
            "I run the SELECT query with the glob pattern inside the Parquet file path"
        ):
            if order_by is None:
                order_by = "j"

            if columns is None:
                columns = "*"

            select_file = node.query(
                f"""
            SELECT {columns} FROM {query} ORDER BY {order_by} FORMAT TabSeparated
            """
            )

        with Then("I check that the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        select_file.output.strip(),
                        name=f"select_from_file_with_{snapshot_name}",
                        mode=self.context.snapshot_mode,
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
                """,
                settings=suspicious_low_cardinality,
            )

            if check_clickhouse_version(">23.9")(self):
                order = "ALL"
            else:
                order = "tuple(*)"

            table_values = node.query(
                f"SELECT {columns} FROM {table_name} ORDER BY {order} FORMAT TabSeparated"
            )

        with Then("I check that the output is correct"):
            with values() as that:
                assert that(
                    snapshot(
                        table_values.output.strip(),
                        name=f"create_table_with_{snapshot_name}",
                        mode=self.context.snapshot_mode,
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


@TestScenario
@Examples(
    "query snapshot_name",
    rows=[
        (f"file('glob_million/z.parquet', Parquet)", "glob_million_files_1"),
        (f"file('glob_million/*.parquet', Parquet)", "glob_million_files_2"),
        (f"file('glob_million/z.*', Parquet)", "glob_million_files_3"),
        (f"file('glob_million/{{z,a,h}}.parquet', Parquet)", "glob_million_files_4"),
        (f"file('glob_million/t1.parquet', Parquet)", "glob_million_files_5"),
    ],
)
def million_extensions(self):
    """Check that glob patterns can pick up a parquet file between one million files with all possible three letter extensions."""
    node = self.context.node
    directory = "/var/lib/clickhouse/user_files/glob_million"
    try:
        with Given(
            "I generate million files with all possible three letter extensions"
        ):
            node.command(f"cd {directory}")
            node.command("./generate_million_files.sh")

        for example in self.examples:
            select_with_glob(
                query=example[0],
                snapshot_name=example[1],
            )
    finally:
        with Finally("I clean up generated files"):
            node.command("rm -rf file.*")


@TestScenario
@Examples(
    "query snapshot_name",
    rows=[
        (f"file('fastparquet/split/cat=fred/catnum=?/*.parquet', Parquet)", "cat_fred"),
        (
            f"file('fastparquet/split/cat=freda/catnum=?/*.parquet', Parquet)",
            "cat_freda",
        ),
    ],
)
def fastparquet_globs(self):
    """Importing multiple Parquet files using the glob patterns from a single directory."""
    snapshot_name = (
        "above_25_8"
        if check_clickhouse_version(">=25.8")(self)
        or check_clickhouse_version(">=25.6")(self)
        and check_if_antalya_build(self)
        else ""
    )

    suspicious_low_cardinality = (
        True if check_clickhouse_version(">=25.6")(self) else False
    )
    columns = "num"
    order_by = "ALL" if check_clickhouse_version(">23.9")(self) else "tuple(*)"

    for example in self.examples:
        select_with_glob(
            columns=columns,
            query=example[0],
            snapshot_name=f"{example[1]}{snapshot_name}",
            order_by=order_by,
            suspicious_low_cardinality=suspicious_low_cardinality,
        )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_Glob("1.0"))
@Name("glob")
def feature(self, node="clickhouse1"):
    """Check glob patterns when importing from multiple Parquet files."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
