from testflows.core import *
from testflows.combinatorics import product
from testflows.asserts import error

from helpers.common import getuid
from helpers.create import create_replicated_merge_tree_table
from s3.requirements.export_partition import (
    RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey,
)
from s3.tests.export_partition.steps import (
    assert_no_scheduled_exports,
    create_s3_table,
    export_partition_by_id,
    get_partition_id_where,
    get_partition_min_max,
    get_partitions,
)


COLUMNS = [
    {"name": "id", "type": "Int64"},
    {"name": "a", "type": "Int32"},
    {"name": "b", "type": "Int32"},
    {"name": "c", "type": "Int32"},
    {"name": "dt", "type": "Date"},
    {"name": "ts", "type": "DateTime"},
    {"name": "s", "type": "String"},
]

# Tuple of strings = one PARTITION BY expression rendered into SQL:
# `()` is unpartitioned, `("a",)` is `PARTITION BY a`, etc.
SOURCE_KEYS = [
    (),
    ("a",),
    ("b",),
    ("dt",),
    ("ts",),
    ("s",),
    ("a", "b"),
    ("b", "a"),
    ("a", "b", "c"),
    ("a", "s"),
    ("a % 4",),
    ("intDiv(a, 10)",),
    ("toYYYYMM(dt)",),
    ("toDate(ts)",),
    ("toStartOfHour(ts)",),
]

# Hive only allows bare-column destination partition keys.
DEST_KEYS = [
    (),
    ("a",),
    ("b",),
    ("dt",),
    ("ts",),
    ("s",),
    ("a", "b"),
    ("b", "a"),
    ("a", "s"),
]

# VALUES rows matching COLUMNS. Chosen to hit every oracle branch:
# single-value min/max, splits on a/dt/ts/s.
SHAPES = {
    "single_row": [
        "(1, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00', 'x')",
    ],
    "same_all": [
        "(1, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00', 'x')",
        "(2, 10, 20, 30, '2024-03-05', '2024-03-05 15:00:00', 'x')",
    ],
    "vary_a": [
        "(1, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00', 'x')",
        "(2, 11, 20, 30, '2024-03-05', '2024-03-05 12:00:00', 'x')",
    ],
    "vary_dt_within_month": [
        "(1, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00', 'x')",
        "(2, 10, 20, 30, '2024-03-20', '2024-03-20 12:00:00', 'x')",
    ],
    "vary_ts_within_day": [
        "(1, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00', 'x')",
        "(2, 10, 20, 30, '2024-03-05', '2024-03-05 18:00:00', 'x')",
    ],
    "vary_s": [
        "(1, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00', 'x')",
        "(2, 10, 20, 30, '2024-03-05', '2024-03-05 12:00:00', 'y')",
    ],
}


def partition_by_sql(terms):
    """Render a term tuple as the SQL body of a ``PARTITION BY`` clause."""
    if not terms:
        return "tuple()"
    if len(terms) == 1:
        return terms[0]
    return "(" + ", ".join(terms) + ")"


def term_column(term):
    """Return the underlying column a source term operates on
    (``toYYYYMM(dt)`` -> ``dt``, ``a % 4`` -> ``a``, ``a`` -> ``a``)."""
    if "(" in term:
        return term[term.index("(") + 1 : term.rindex(")")].split(",")[0].strip()
    if "%" in term:
        return term.split("%")[0].strip()
    return term.strip()


def predict_accept(source_terms, dest_terms, min_max):
    """Predict whether the hive gate accepts.

    Returns ``(accept, expected_substrings)``. On reject every substring in
    the tuple must appear in the ``BAD_ARGUMENTS`` message so both the
    reason and the offending column are pinned.
    """
    if tuple(source_terms) == tuple(dest_terms):
        return True, ()
    if not dest_terms:
        return True, ()
    source_terms_set = set(source_terms)
    source_cols = {term_column(t) for t in source_terms}
    for col in dest_terms:
        if col in source_terms_set:
            continue
        if col not in source_cols:
            return False, (f"column '{col}'",)
        lo, hi = min_max[col]
        if lo != hi:
            return False, ("spans multiple destination partitions", f"column '{col}'")
    return True, ()


@TestScenario
def oracle_self_tests(self):
    """Pin ``predict_accept`` on every decision path in pure Python so a
    regression in the oracle is caught before any ClickHouse run."""
    cases = [
        (("a",), ("a",), {"a": ("1", "5")}, True, (), "identical keys"),
        ((), (), {}, True, (), "both unpartitioned"),
        (("a",), (), {}, True, (), "destination unpartitioned"),
        (("a", "b"), ("a",), {"a": ("1", "5")}, True, (), "subset per-column"),
        (
            ("a", "b"),
            ("b", "a"),
            {"a": ("1", "5"), "b": ("1", "5")},
            True,
            (),
            "reversed multi-column subset",
        ),
        (
            (),
            ("a",),
            {"a": ("1", "5")},
            False,
            ("column 'a'",),
            "source empty, destination not",
        ),
        (
            ("a",),
            ("b",),
            {"a": ("1", "5"), "b": ("1", "1")},
            False,
            ("column 'b'",),
            "destination column not in source key",
        ),
        (
            ("a % 4",),
            ("a",),
            {"a": ("0", "4")},
            False,
            ("spans multiple destination partitions", "column 'a'"),
            "non-monotonic source and split range",
        ),
        (
            ("a % 4",),
            ("a",),
            {"a": ("5", "5")},
            True,
            (),
            "non-monotonic source but exported partition is single-valued",
        ),
        (
            ("toYYYYMM(dt)",),
            ("dt",),
            {"dt": ("2024-03-05", "2024-03-05")},
            True,
            (),
            "monthly source, bare dt destination, exported partition holds one day",
        ),
        (
            ("toYYYYMM(dt)",),
            ("dt",),
            {"dt": ("2024-03-05", "2024-03-20")},
            False,
            ("spans multiple destination partitions", "column 'dt'"),
            "monthly source, bare dt destination, exported partition holds two days",
        ),
    ]
    for source_terms, dest_terms, min_max, expect_accept, expect_subs, note in cases:
        accept, substrings = predict_accept(source_terms, dest_terms, min_max)
        assert accept == expect_accept, error(
            f"{note}: expected accept={expect_accept}, got {accept}"
        )
        assert substrings == expect_subs, error(
            f"{note}: expected substrings={expect_subs!r}, got {substrings!r}"
        )


@TestScenario
def check_case(self, source_terms, dest_terms, shape_name, shape_values):
    """One matrix cell: build the tables, insert the shape, export the
    first source partition, and compare the gate's response to the oracle."""
    node = self.context.node
    src_partition_by = partition_by_sql(source_terms)
    dst_partition_by = partition_by_sql(dest_terms)

    with Given(f"a source RMT PARTITION BY {src_partition_by}"):
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
        relevant_cols = sorted({term_column(t) for t in source_terms} | set(dest_terms))
        min_max = get_partition_min_max(
            source_table=source_table,
            partition_id=partition_id,
            columns=relevant_cols,
            node=node,
        )

    expect_accept, expect_substrings = predict_accept(source_terms, dest_terms, min_max)

    if expect_accept:
        with Then("the export succeeds"):
            export_partition_by_id(
                source_table=source_table,
                destination_table=destination_table,
                partition_id=partition_id,
                node=node,
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
            result = export_partition_by_id(
                source_table=source_table,
                destination_table=destination_table,
                partition_id=partition_id,
                node=node,
                exitcode=36,
            )
            assert "BAD_ARGUMENTS" in result.output, error(result.output)
            for fragment in expect_substrings:
                assert fragment in result.output, error(
                    f"expected {fragment!r} in error, got: {result.output!r}"
                )
        with And("nothing is scheduled"):
            assert_no_scheduled_exports(
                source_table=source_table,
                destination_table=destination_table,
                partition_id=partition_id,
                node=node,
            )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def compatibility_matrix(self):
    """Assert every ``product(SOURCE_KEYS, DEST_KEYS, SHAPES)`` combination
    against the oracle."""
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
    """The gate decides per partition: in one table with a split March
    partition and a single-day April partition, March rejects and April
    exports."""
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]

    with Given("a source RMT PARTITION BY toYYYYMM(dt)"):
        source_table = f"src_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=source_table,
            columns=columns,
            partition_by="toYYYYMM(dt)",
            cluster="replicated_cluster",
        )
    with And("an S3 hive destination PARTITION BY dt"):
        destination_table = create_s3_table(
            table_name="dst",
            create_new_bucket=True,
            columns=columns,
            partition_by="dt",
        )
    with And("March splits (two days) and April is single-day"):
        node.query(
            f"INSERT INTO {source_table} VALUES "
            f"(1, '2024-03-05'), (2, '2024-03-20'), (3, '2024-04-10')"
        )

    with When("I export the March partition"):
        result = export_partition_by_id(
            source_table=source_table,
            destination_table=destination_table,
            partition_id="202403",
            node=node,
            exitcode=36,
        )
    with Then("it is rejected synchronously and nothing is scheduled"):
        assert "BAD_ARGUMENTS" in result.output, error(result.output)
        assert "spans multiple destination partitions" in result.output, error(
            result.output
        )
        assert "column 'dt'" in result.output, error(result.output)
        assert_no_scheduled_exports(
            source_table=source_table, partition_id="202403", node=node
        )

    with When("I export the April partition"):
        export_partition_by_id(
            source_table=source_table,
            destination_table=destination_table,
            partition_id="202404",
            node=node,
        )
    with Then("only the April row is present in the destination"):
        rows = node.query(
            f"SELECT id, dt FROM {destination_table} ORDER BY id FORMAT TabSeparated"
        ).output.strip()
        assert rows == "3\t2024-04-10", error(f"got: {rows!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def subset_round_trip(self):
    """Flagship new-accept case: source ``(year, country)`` -> destination
    ``year``. Every source partition holds one year, so all export through
    the per-column fast path. Assert end-to-end data integrity by
    round-tripping through S3 back into a fresh RMT."""
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
            export_partition_by_id(
                source_table=source_table,
                destination_table=destination_table,
                partition_id=partition_id,
                node=node,
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
def multi_part_partition_reject(self):
    """The gate must fold min/max across all parts of a source partition,
    not judge per part. Two single-day inserts (kept as separate parts by
    stopping merges) span two days in aggregate and must reject."""
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]

    with Given("a source RMT with merges stopped, PARTITION BY toYYYYMM(dt)"):
        source_table = f"src_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=source_table,
            columns=columns,
            partition_by="toYYYYMM(dt)",
            cluster="replicated_cluster",
            stop_merges=True,
        )
    with And("an S3 hive destination PARTITION BY dt"):
        destination_table = create_s3_table(
            table_name="dst",
            create_new_bucket=True,
            columns=columns,
            partition_by="dt",
        )
    with And("two single-day inserts into the same partition"):
        node.query(f"INSERT INTO {source_table} VALUES (1, '2024-03-05')")
        node.query(f"INSERT INTO {source_table} VALUES (2, '2024-03-20')")
    with And("both inserts landed as separate active parts"):
        parts = node.query(
            f"SELECT count() FROM system.parts WHERE table = '{source_table}' "
            f"AND partition_id = '202403' AND active"
        ).output.strip()
        assert parts == "2", error(f"expected 2 active parts, got {parts}")

    with When("I export the March partition"):
        result = export_partition_by_id(
            source_table=source_table,
            destination_table=destination_table,
            partition_id="202403",
            node=node,
            exitcode=36,
        )
    with Then("the gate rejects on combined min/max, naming column 'dt'"):
        assert "BAD_ARGUMENTS" in result.output, error(result.output)
        assert "spans multiple destination partitions" in result.output, error(
            result.output
        )
        assert "column 'dt'" in result.output, error(result.output)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def three_term_destination_mixed_decisions(self):
    """A 3-term hive destination mixes fast-path and dynamic decisions.
    Source ``(year, toYYYYMM(dt), country)`` -> destination
    ``(year, dt, country)``: ``year`` and ``country`` take the per-column
    fast path; ``dt`` must be proved single-valued dynamically. Single-day
    US partition accepts, two-day FR partition rejects on ``column 'dt'``.
    """
    node = self.context.node
    columns = [
        {"name": "id", "type": "Int64"},
        {"name": "year", "type": "UInt16"},
        {"name": "dt", "type": "Date"},
        {"name": "country", "type": "String"},
    ]

    with Given("source RMT PARTITION BY (year, toYYYYMM(dt), country)"):
        source_table = f"src_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=source_table,
            columns=columns,
            partition_by="(year, toYYYYMM(dt), country)",
            cluster="replicated_cluster",
        )
    with And("S3 hive destination PARTITION BY (year, dt, country)"):
        destination_table = create_s3_table(
            table_name="dst",
            create_new_bucket=True,
            columns=columns,
            partition_by="(year, dt, country)",
        )
    with And("one single-day US partition and one two-day FR partition"):
        node.query(
            f"INSERT INTO {source_table} VALUES "
            f"(1, 2024, '2024-03-05', 'US'), (2, 2024, '2024-03-05', 'US'), "
            f"(3, 2024, '2024-03-05', 'FR'), (4, 2024, '2024-03-20', 'FR')"
        )

    with When("I look up the US and FR source partition ids"):
        us_partition = get_partition_id_where(
            source_table=source_table, where="country = 'US'", node=node
        )
        fr_partition = get_partition_id_where(
            source_table=source_table, where="country = 'FR'", node=node
        )

    with When("I export the single-day US partition"):
        export_partition_by_id(
            source_table=source_table,
            destination_table=destination_table,
            partition_id=us_partition,
            node=node,
        )
    with Then("only the US rows land in the destination"):
        rows = node.query(
            f"SELECT id, year, dt, country FROM {destination_table} "
            f"ORDER BY id FORMAT TabSeparated"
        ).output.strip()
        assert rows == "1\t2024\t2024-03-05\tUS\n2\t2024\t2024-03-05\tUS", error(
            f"got: {rows!r}"
        )

    with When("I export the two-day FR partition"):
        result = export_partition_by_id(
            source_table=source_table,
            destination_table=destination_table,
            partition_id=fr_partition,
            node=node,
            exitcode=36,
        )
    with Then("it rejects with 'spans multiple destination partitions' on 'dt'"):
        assert "BAD_ARGUMENTS" in result.output, error(result.output)
        assert "spans multiple destination partitions" in result.output, error(
            result.output
        )
        assert "column 'dt'" in result.output, error(result.output)


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def export_partition_all_gate_is_atomic(self):
    """``EXPORT PARTITION ALL`` runs the gate synchronously while
    scheduling, so a single failing partition rejects the whole ALTER with
    ``BAD_ARGUMENTS``. The ``export_merge_tree_partition_all_on_error``
    setting governs **runtime** conflicts during async processing, not the
    scheduling-time gate: ``skip_conflicts`` still yields the same reject.
    """
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]

    with Given("a source RMT PARTITION BY toYYYYMM(dt)"):
        source_table = f"src_{getuid()}"
        create_replicated_merge_tree_table(
            table_name=source_table,
            columns=columns,
            partition_by="toYYYYMM(dt)",
            cluster="replicated_cluster",
        )
    with And("an S3 hive destination PARTITION BY dt"):
        destination_table = create_s3_table(
            table_name="dst",
            create_new_bucket=True,
            columns=columns,
            partition_by="dt",
        )
    with And("March splits (two days) and April is single-day"):
        node.query(
            f"INSERT INTO {source_table} VALUES "
            f"(1, '2024-03-05'), (2, '2024-03-20'), (3, '2024-04-10')"
        )

    for on_error in ("throw_first", "skip_conflicts"):
        with When(f"I run EXPORT PARTITION ALL with on_error={on_error}"):
            result = node.query(
                f"ALTER TABLE {source_table} EXPORT PARTITION ALL "
                f"TO TABLE {destination_table} "
                f"SETTINGS export_merge_tree_partition_all_on_error = '{on_error}'",
                settings=self.context.default_settings,
                exitcode=36,
                ignore_exception=True,
            )
        with Then(f"[{on_error}] the whole ALTER is rejected synchronously"):
            assert "BAD_ARGUMENTS" in result.output, error(result.output)
            assert "spans multiple destination partitions" in result.output, error(
                result.output
            )
            assert "column 'dt'" in result.output, error(result.output)
        with And(f"[{on_error}] nothing is scheduled and destination stays empty"):
            assert_no_scheduled_exports(
                source_table=source_table,
                destination_table=destination_table,
                node=node,
            )
            dst_count = node.query(
                f"SELECT count() FROM {destination_table}"
            ).output.strip()
            assert dst_count == "0", error(
                f"[{on_error}] expected empty destination, got {dst_count}"
            )


@TestFeature
@Name("partition key compatibility")
def feature(self):
    """Partition-key compatibility gate for hive S3 exports (Altinity/ClickHouse#2074)."""
    Scenario(run=oracle_self_tests)
    Scenario(run=compatibility_matrix)
    Scenario(run=per_partition_acceptance)
    Scenario(run=multi_part_partition_reject)
    Scenario(run=three_term_destination_mixed_decisions)
    Scenario(run=export_partition_all_gate_is_atomic)
    Scenario(run=subset_round_trip)
