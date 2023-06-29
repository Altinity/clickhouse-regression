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

    with When(
        "I run the SELECT query with the glob pattern inside the Parquet file path"
    ):
        node.query(query)


@TestScenario
@Examples(
    "query snapshot_name",
    rows=[
        (f"SELECT * FROM file('{glob1}/*', Parquet)", "asterisk"),
        (f"SELECT * FROM file('{glob1}/**', Parquet)", "globstar"),
        (f"SELECT * FROM file('{glob1}/t?.parquet', Parquet)", "question_mark"),
        (f"SELECT * FROM file('{glob1}/t{{1..2}}.parquet', Parquet)", "range"),
    ],
)
def glob1(self):
    for example in self.examples:
        select_with_glob(query=example[0], snapshot_name=example[1])


@TestScenario
@Examples(
    "query snapshot_name",
    rows=[
        (f"SELECT * FROM file('{glob3}/?/dir/*', Parquet)", "nested_glob_1"),
        (f"SELECT * FROM file('{glob3}/?/dir/**', Parquet)", "nested_glob_2"),
        (f"SELECT * FROM file('{glob3}/?/???/**', Parquet)", "nested_glob_3"),
        (
            f"SELECT * FROM file('{glob3}/?/dir/*{{p,a,r,q,u,e,t}}', Parquet)",
            "nested_glob_4",
        ),
        (f"SELECT * FROM file('{glob3}/?/y.*', Parquet)", "single_nested_glob"),
        (f"SELECT * FROM file('{glob3}/?/y.*', Parquet)", "single_nested_glob"),
    ],
)
def glob2(self):
    for example in self.examples:
        select_with_glob(query=example[0], snapshot_name=example[1])


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Glob("1.0"))
@Name("glob")
def feature(self, node="clickhouse1"):
    """Check using glob pattern when importing from Parquet files."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
