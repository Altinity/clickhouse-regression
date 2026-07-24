"""Combinatorial tests for the hive S3 partition-key compatibility gate.

Covers Altinity/ClickHouse#2074 - the export gate now accepts a source
``PARTITION BY`` that is not structurally identical to the destination, as
long as every source partition provably maps to a single destination
partition. For a hive destination (bare columns only) the gate accepts a
destination term when:

  * source and destination partition keys are identical, or
  * the destination is unpartitioned, or
  * the source ``PARTITION BY`` already contains that exact term (per-column
    fast path; covers a source that adds extra columns on top of the
    destination's, in any order), or
  * ``min == max`` on the destination column across the exported source part
    (dynamic single-value proof).

The module encodes those rules in one small helper (``predict_accept``) and
sweeps ``product(SOURCE_KEYS, DEST_KEYS, SHAPES)``. Each combination runs
``EXPORT PARTITION ID`` on the first source partition and asserts the gate's
actual behaviour matches the prediction.
"""

from testflows.core import *
from testflows.combinatorics import product
from testflows.asserts import error

from helpers.common import getuid
from helpers.create import create_replicated_merge_tree_table
from s3.requirements.export_partition import (
    RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey,
)
from s3.tests.export_partition.steps import (
    create_s3_table,
    get_partitions,
    wait_for_export_to_complete,
)


COLUMNS = [
    {"name": "id", "type": "Int64"},
    {"name": "a", "type": "Int32"},
    {"name": "b", "type": "Int32"},
    {"name": "c", "type": "Int32"},
    {"name": "dt", "type": "Date"},
    {"name": "ts", "type": "DateTime"},
]

# Source terms are stored as strings (rendered directly into SQL). A tuple of
# strings represents one ``PARTITION BY`` expression: ``()`` is unpartitioned,
# ``("a",)`` is ``PARTITION BY a``, ``("a", "b")`` is ``PARTITION BY (a, b)``.
SOURCE_KEYS = [
    (),
    ("a",),
    ("b",),
    ("dt",),
    ("ts",),
    ("a", "b"),
    ("b", "a"),
    ("a", "b", "c"),
    ("a % 4",),
    ("intDiv(a, 10)",),
    ("toYYYYMM(dt)",),
    ("toDate(ts)",),
    ("toStartOfHour(ts)",),
]

# Hive rejects expression partition keys at table creation, so every
# destination term is a bare column.
DEST_KEYS = [
    (),
    ("a",),
    ("b",),
    ("dt",),
    ("ts",),
    ("a", "b"),
    ("b", "a"),
]

# Each shape is a list of VALUES rows matching COLUMNS. Shapes are chosen to
# exercise every branch of the oracle: single-value min/max, split-on-a,
# split-on-dt-within-a-month, and split-on-ts-within-a-day.
SHAPES = {
    "single_row": [
        "(1, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00')",
    ],
    "same_all": [
        "(1, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00')",
        "(2, 10, 20, 30, '2024-03-05', '2024-03-05 15:00:00')",
    ],
    "vary_a": [
        "(1, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00')",
        "(2, 11, 20, 30, '2024-03-05', '2024-03-05 12:00:00')",
    ],
    "vary_dt_within_month": [
        "(1, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00')",
        "(2, 10, 20, 30, '2024-03-20', '2024-03-20 12:00:00')",
    ],
    "vary_ts_within_day": [
        "(1, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00')",
        "(2, 10, 20, 30, '2024-03-05', '2024-03-05 18:00:00')",
    ],
}


def partition_by_sql(terms):
    """Render a term tuple as a ``PARTITION BY`` fragment."""
    if not terms:
        return "tuple()"
    if len(terms) == 1:
        return terms[0]
    return "(" + ", ".join(terms) + ")"


def term_column(term):
    """Return the column name a source term operates on."""
    if "(" in term:
        # e.g. "toYYYYMM(dt)" or "intDiv(a, 10)"
        return term[term.index("(") + 1 : term.rindex(")")].split(",")[0].strip()
    if "%" in term:
        # e.g. "a % 4"
        return term.split("%")[0].strip()
    return term.strip()


def predict_accept(source_terms, dest_terms, min_max, nullable_cols=frozenset()):
    """Predict whether the hive gate accepts.

    Returns ``(accept: bool, error_substring: str)``. On accept the substring
    is empty; on reject it is a fragment the ``BAD_ARGUMENTS`` message should
    contain.
    """
    if tuple(source_terms) == tuple(dest_terms):
        return True, ""
    if not dest_terms:
        return True, ""
    source_terms_set = set(source_terms)
    source_cols = {term_column(t) for t in source_terms}
    for col in dest_terms:
        if col in source_terms_set:
            continue
        if col not in source_cols:
            return False, f"column '{col}'"
        if col in nullable_cols:
            return False, "Nullable"
        lo, hi = min_max.get(col, (None, None))
        if lo is None:
            return False, "no min/max"
        if lo != hi:
            return False, "spans multiple destination partitions"
    return True, ""


@TestScenario
def oracle_self_tests(self):
    """Sanity-check ``predict_accept`` on every decision path (no ClickHouse)."""
    cases = [
        (("a",), ("a",), {"a": ("1", "5")}, True, "identical keys"),
        ((), (), {}, True, "both unpartitioned"),
        (("a",), (), {}, True, "destination unpartitioned"),
        (("a", "b"), ("a",), {"a": ("1", "5")}, True, "subset per-column"),
        (
            ("a", "b"),
            ("b", "a"),
            {"a": ("1", "5"), "b": ("1", "5")},
            True,
            "reversed multi-column subset",
        ),
        ((), ("a",), {"a": ("1", "5")}, False, "source empty, destination not"),
        (
            ("a",),
            ("b",),
            {"a": ("1", "5"), "b": ("1", "1")},
            False,
            "destination column not in source key",
        ),
        (
            ("a % 4",),
            ("a",),
            {"a": ("0", "4")},
            False,
            "non-monotonic source and split range",
        ),
        (
            ("a % 4",),
            ("a",),
            {"a": ("5", "5")},
            True,
            "non-monotonic source but exported partition is single-valued",
        ),
        (
            ("toYYYYMM(dt)",),
            ("dt",),
            {"dt": ("2024-03-05", "2024-03-05")},
            True,
            "monthly source, bare dt destination, exported partition holds one day",
        ),
        (
            ("toYYYYMM(dt)",),
            ("dt",),
            {"dt": ("2024-03-05", "2024-03-20")},
            False,
            "monthly source, bare dt destination, exported partition holds two days",
        ),
    ]
    for source_terms, dest_terms, min_max, expect_accept, note in cases:
        accept, _ = predict_accept(source_terms, dest_terms, min_max)
        assert accept == expect_accept, error(
            f"{note}: expected accept={expect_accept}, got {accept}"
        )


@TestScenario
def check_case(self, source_terms, dest_terms, shape_name, shape_values):
    """Run one combinatorial case: create tables, insert, export the first
    source partition, and assert the gate's response matches the oracle."""
    node = self.context.node
    src_partition_by = partition_by_sql(source_terms)
    dst_partition_by = partition_by_sql(dest_terms)

    with Given(f"a source table PARTITION BY {src_partition_by}"):
        source_table = f"src_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=source_table,
            columns=COLUMNS,
            partition_by=src_partition_by,
            cluster="replicated_cluster",
        )

    with And(f"an S3 hive destination PARTITION BY {dst_partition_by}"):
        destination_table = create_s3_table(
            table_name="dst",
            create_new_bucket=True,
            columns=COLUMNS,
            partition_by=dst_partition_by,
        )

    with And(f"data shape {shape_name}"):
        node.query(f"INSERT INTO {source_table} VALUES {', '.join(shape_values)}")

    with When("I pick the first source partition and read its min/max"):
        partition_id = get_partitions(table_name=source_table, node=node)[0]
        columns = sorted({term_column(t) for t in source_terms} | set(dest_terms))
        min_max = {}
        if columns:
            projection = ", ".join(f"min({c}), max({c})" for c in columns)
            row = (
                node.query(
                    f"SELECT {projection} FROM {source_table} "
                    f"WHERE _partition_id = '{partition_id}' FORMAT TabSeparated"
                )
                .output.strip()
                .split("\t")
            )
            min_max = {c: (row[2 * i], row[2 * i + 1]) for i, c in enumerate(columns)}

    expect_accept, expect_error = predict_accept(source_terms, dest_terms, min_max)
    query = (
        f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition_id}' "
        f"TO TABLE {destination_table}"
    )

    if expect_accept:
        with Then("the export succeeds"):
            node.query(query, settings=self.context.default_settings)
            wait_for_export_to_complete(
                partition_id=partition_id, source_table=source_table, node=node
            )
        with And("destination rows equal the exported source partition"):
            src_rows = node.query(
                f"SELECT * FROM {source_table} WHERE _partition_id = '{partition_id}' "
                f"ORDER BY id FORMAT TabSeparated"
            ).output
            dst_rows = node.query(
                f"SELECT * FROM {destination_table} ORDER BY id FORMAT TabSeparated"
            ).output
            assert src_rows == dst_rows, error()
    else:
        with Then("the export is rejected with BAD_ARGUMENTS"):
            result = node.query(
                query, settings=self.context.default_settings, no_checks=True
            )
            assert result.exitcode != 0, error(
                f"expected error, got: {result.output!r}"
            )
            assert "BAD_ARGUMENTS" in result.output, error(result.output)
            assert expect_error in result.output, error(
                f"expected {expect_error!r} in error, got: {result.output!r}"
            )
        with And("nothing is scheduled in system.replicated_partition_exports"):
            scheduled = node.query(
                f"SELECT count() FROM system.replicated_partition_exports "
                f"WHERE source_table = '{source_table}' "
                f"AND destination_table = '{destination_table}' "
                f"AND partition_id = '{partition_id}'"
            ).output.strip()
            assert scheduled == "0", error(
                f"expected 0 scheduled after synchronous reject, got {scheduled}"
            )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def compatibility_matrix(self):
    """Sweep ``product(SOURCE_KEYS, DEST_KEYS, SHAPES)`` and assert every
    combination against the oracle."""
    with Pool(4) as pool:
        for source_terms, dest_terms, (shape_name, shape_values) in product(
            SOURCE_KEYS, DEST_KEYS, list(SHAPES.items())
        ):
            name = (
                f"src[{partition_by_sql(source_terms)}] "
                f"dst[{partition_by_sql(dest_terms)}] "
                f"shape[{shape_name}]"
            )
            Scenario(name, test=check_case, parallel=True, executor=pool)(
                source_terms=source_terms,
                dest_terms=dest_terms,
                shape_name=shape_name,
                shape_values=shape_values,
            )
        join()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def per_partition_acceptance(self):
    """Acceptance is per-partition: with one source table holding two
    partitions - one single-valued for the destination, one split - the
    single-valued one exports and the split one is rejected."""
    node = self.context.node

    with Given("a source RMT PARTITION BY toYYYYMM(dt)"):
        source_table = f"src_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=source_table,
            columns=[{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}],
            partition_by="toYYYYMM(dt)",
            cluster="replicated_cluster",
        )

    with And("an S3 hive destination PARTITION BY dt"):
        destination_table = create_s3_table(
            table_name="dst",
            create_new_bucket=True,
            columns=[{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}],
            partition_by="dt",
        )

    with And("March holds two days (splits) and April holds one day (single)"):
        node.query(
            f"INSERT INTO {source_table} VALUES "
            f"(1, '2024-03-05'), (2, '2024-03-20'), (3, '2024-04-10')"
        )

    with When("I export the March partition"):
        result = node.query(
            f"ALTER TABLE {source_table} EXPORT PARTITION ID '202403' "
            f"TO TABLE {destination_table}",
            settings=self.context.default_settings,
            no_checks=True,
        )
    with Then("it is rejected synchronously and nothing is scheduled"):
        assert result.exitcode != 0, error(f"expected reject, got: {result.output!r}")
        assert "BAD_ARGUMENTS" in result.output, error(result.output)
        assert "spans multiple destination partitions" in result.output, error(
            result.output
        )
        scheduled = node.query(
            f"SELECT count() FROM system.replicated_partition_exports "
            f"WHERE source_table = '{source_table}' AND partition_id = '202403'"
        ).output.strip()
        assert scheduled == "0", error(f"expected 0 scheduled, got {scheduled}")

    with When("I export the April partition"):
        node.query(
            f"ALTER TABLE {source_table} EXPORT PARTITION ID '202404' "
            f"TO TABLE {destination_table}",
            settings=self.context.default_settings,
        )
        wait_for_export_to_complete(
            partition_id="202404", source_table=source_table, node=node
        )
    with Then("only the April row is present in the destination"):
        rows = node.query(
            f"SELECT id, dt FROM {destination_table} ORDER BY id FORMAT TabSeparated"
        ).output.strip()
        assert rows == "3\t2024-04-10", error(f"got: {rows!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def subset_round_trip(self):
    """A source PARTITION BY (year, country) into a destination PARTITION BY
    year is the flagship "new" accept case. Every source part has a single
    year, so every partition is accepted through the per-column fast path.
    The exported data must round-trip losslessly back into a fresh
    ReplicatedMergeTree with the source's partition key."""
    node = self.context.node
    columns = [
        {"name": "id", "type": "UInt64"},
        {"name": "year", "type": "UInt16"},
        {"name": "country", "type": "String"},
    ]

    with Given("source RMT PARTITION BY (year, country)"):
        source_table = f"src_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=source_table,
            columns=columns,
            partition_by="(year, country)",
            cluster="replicated_cluster",
        )
    with And("S3 hive destination PARTITION BY year"):
        destination_table = create_s3_table(
            table_name="dst",
            create_new_bucket=True,
            columns=columns,
            partition_by="year",
        )
    with And("three source partitions across two years"):
        node.query(
            f"INSERT INTO {source_table} VALUES "
            f"(1, 2020, 'US'), (2, 2020, 'FR'), (3, 2021, 'US')"
        )

    with When("I export every source partition"):
        for partition_id in get_partitions(table_name=source_table, node=node):
            node.query(
                f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition_id}' "
                f"TO TABLE {destination_table}",
                settings=self.context.default_settings,
            )
            wait_for_export_to_complete(
                partition_id=partition_id, source_table=source_table, node=node
            )

    with Then("the destination holds every source row"):
        src_rows = node.query(
            f"SELECT id, year, country FROM {source_table} ORDER BY id "
            f"FORMAT TabSeparated"
        ).output
        dst_rows = node.query(
            f"SELECT id, year, country FROM {destination_table} ORDER BY id "
            f"FORMAT TabSeparated"
        ).output
        assert src_rows == dst_rows, error()

    with And("round-tripping back into a fresh RMT reproduces the source"):
        roundtrip_table = f"rt_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=roundtrip_table,
            columns=columns,
            partition_by="(year, country)",
            cluster="replicated_cluster",
        )
        node.query(f"INSERT INTO {roundtrip_table} SELECT * FROM {destination_table}")
        rt_rows = node.query(
            f"SELECT id, year, country FROM {roundtrip_table} ORDER BY id "
            f"FORMAT TabSeparated"
        ).output
        assert rt_rows == src_rows, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def nullable_partition_column_rejected(self):
    """A Nullable partition column can only match through the identical-AST
    or per-column fast paths - the dynamic proof always rejects it because a
    NULL forms its own destination partition. Source PARTITION BY (a, b)
    with ``b Nullable(Int32)`` into destination PARTITION BY b: the fast
    paths still accept (b is in source terms). Same source into destination
    PARTITION BY a with ``a Nullable(Int32)`` and different values of a
    forces the dynamic path, which must reject."""
    node = self.context.node
    columns = [
        {"name": "id", "type": "Int64"},
        {"name": "a", "type": "Nullable(Int32)"},
        {"name": "b", "type": "Int32"},
    ]

    with Given("source RMT PARTITION BY (b) with a Nullable"):
        source_table = f"src_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=source_table,
            columns=columns,
            partition_by="b",
            cluster="replicated_cluster",
        )

    with And(
        "S3 hive destination PARTITION BY a (Nullable) - covered by neither fast path"
    ):
        destination_table = create_s3_table(
            table_name="dst",
            create_new_bucket=True,
            columns=columns,
            partition_by="a",
        )

    with And("rows where a differs"):
        node.query(f"INSERT INTO {source_table} VALUES (1, 10, 5), (2, 11, 5)")

    with When("I export the source partition"):
        partition_id = get_partitions(table_name=source_table, node=node)[0]
        result = node.query(
            f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition_id}' "
            f"TO TABLE {destination_table}",
            settings=self.context.default_settings,
            no_checks=True,
        )
    with Then("it is rejected with BAD_ARGUMENTS"):
        assert result.exitcode != 0, error(f"expected reject, got: {result.output!r}")
        assert "BAD_ARGUMENTS" in result.output, error(result.output)


@TestFeature
@Name("partition key compatibility")
def feature(self):
    """Partition-key compatibility gate for hive S3 exports (Altinity/ClickHouse#2074)."""
    Scenario(run=oracle_self_tests)
    Scenario(run=compatibility_matrix)
    Scenario(run=per_partition_acceptance)
    Scenario(run=subset_round_trip)
    Scenario(run=nullable_partition_column_rejected)
