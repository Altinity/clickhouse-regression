"""Datatypes: deletion vectors delete whole rows by position, independently
of the schema's shape. One wide fixture table carries a column for every
Iceberg type the Spark writer supports — boolean, int, long, float, double,
decimal, date, timestamp, timestamp_ntz, string, binary, list, map, struct,
nested combinations, and a Nullable column — and every scenario verifies its
own column reflects only the surviving rows.

Every column derives deterministically from ``id`` so the expected
aggregates are computed in Python; each check expression evaluates to a
single literal that must match exactly."""

import datetime

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.schemas as schemas

ROWS = 100
DELETED = [i for i in range(ROWS) if i % 10 == 0]
SURVIVORS = [i for i in range(ROWS) if i % 10 != 0]


def _expected_checks():
    """(name, ClickHouse expression, expected literal output) per datatype.

    Each expression evaluates to one literal over the surviving rows only,
    so any resurrection or loss of rows changes the output."""
    n = len(SURVIVORS)
    ssum = sum(SURVIVORS)
    even = sum(1 for i in SURVIVORS if i % 2 == 0)
    nulls = sum(1 for i in SURVIVORS if i % 3 == 0)
    not_null_sum = sum(i for i in SURVIVORS if i % 3 != 0)
    base_date = datetime.date(2024, 1, 1)
    min_date = base_date + datetime.timedelta(days=min(SURVIVORS))
    max_date = base_date + datetime.timedelta(days=max(SURVIVORS))

    return [
        ("boolean", "countIf(flag)", str(even)),
        ("int", "sum(i32)", str(2 * ssum)),
        ("long", "sum(i64)", str(1000000 * ssum)),
        ("float", f"abs(sum(f32) - {ssum * 0.5}) < 0.01", "1"),
        ("double", f"abs(sum(f64) - {ssum * 0.25}) < 0.01", "1"),
        ("decimal", f"abs(toFloat64(sum(dec)) - {ssum + n * 0.25}) < 0.001", "1"),
        (
            "date",
            f"min(d) = toDate('{min_date}') AND max(d) = toDate('{max_date}')",
            "1",
        ),
        ("timestamp", "uniqExact(ts)", str(n)),
        ("timestamp ntz", "uniqExact(ts_ntz)", str(n)),
        ("string", "uniqExact(s)", str(n)),
        ("binary", "uniqExact(bin)", str(n)),
        ("array", "sum(length(arr))", str(2 * n)),
        ("map", "sum(m['k'])", str(ssum)),
        ("struct", "sum(st.a)", str(ssum)),
        ("struct nested array", "sum(length(st.tags))", str(n)),
        # Spark ARRAY<INT> elements are nullable, and arraySum rejects
        # Nullable element types — strip the (never actually NULL)
        # nullability before aggregating
        (
            "map of arrays",
            "sum(arraySum(arrayMap(x -> assumeNotNull(x), nested['k'])))",
            str(ssum),
        ),
        ("nullable nulls", "countIf(isNull(nl))", str(nulls)),
        ("nullable values", "sum(nl)", str(not_null_sum)),
    ]


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_ComplexSchemas("1.0"))
def datatype_column(self, name, expression, expected):
    """One typed column reflects only the surviving rows."""
    with Then(f"{expression} over survivors equals {expected}"):
        result = common.read_result(table=self.context.table, columns=expression)
        assert result.output.strip() == expected, error(
            f"{name}: {expression} = {result.output.strip()!r}, "
            f"expected {expected!r}"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_ComplexSchemas("1.0"))
def nested_projection(self):
    """Reading a subset of nested fields excludes deleted rows."""
    with Then("a projection of nested fields returns only surviving rows"):
        result = common.read_result(
            table=self.context.table,
            columns="id, st.a, m['k']",
            order_by="id",
        )
        lines = [
            line.split("\t") for line in result.output.splitlines() if line.strip()
        ]
        assert [int(line[0]) for line in lines] == SURVIVORS, error(
            f"nested projection returned {len(lines)} rows"
        )
        assert all(line[0] == line[1] == line[2] for line in lines), error(
            "nested field values do not match their row's id"
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_ComplexSchemas("1.0"))
def datatypes(self):
    """Every supported Iceberg datatype on one wide table with a deletion
    vector."""
    with Given("a wide table with every supported datatype and a vector"):
        columns, insert = schemas.columns_and_insert("wide", ROWS)
        table = common.table_with_deletion_vectors(
            rows=0,
            columns=columns,
            setup_statements=[
                insert,
                "DELETE FROM {table} WHERE id % 10 = 0",
            ],
        )
        self.context.table = table

    with And("the visible id set reflects the vector"):
        common.assert_visible_ids(table=table, ids=SURVIVORS)

    for name, expression, expected in _expected_checks():
        Scenario(test=datatype_column, name=name)(
            name=name, expression=expression, expected=expected
        )

    Scenario(run=nested_projection)


@TestFeature
@Name("datatypes")
def feature(self, minio_root_user, minio_root_password):
    """Deletion vectors across all supported Iceberg datatypes."""
    Suite(run=datatypes)
