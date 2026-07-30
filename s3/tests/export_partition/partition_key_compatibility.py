from testflows.core import *
from testflows.combinatorics import product
from testflows.asserts import error

from helpers.common import getuid
from helpers.create import create_replicated_merge_tree_table
from s3.requirements.export_partition import (
    RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey,
)
from s3.tests.export_partition.steps import (
    assert_export_rejected,
    assert_no_scheduled_exports,
    count_rows,
    create_s3_table,
    create_temp_bucket,
    disable_failpoint,
    drop_partition_by_id,
    enable_failpoint,
    export_partition_by_id,
    get_first_partition_id,
    get_partition_id_where,
    get_partition_min_max,
    get_partitions,
    insert_values,
    RETRYABLE_FAILPOINT,
    select_rows,
    setup_source_and_hive_destination,
    short_backoff_settings,
    start_export,
    wait_for_exception_count,
    wait_for_export_to_complete,
)


# Error codes referenced in reject assertions (see
# ``export_partition_local_backoff_policy.md``).
BAD_ARGUMENTS = 36
INCOMPATIBLE_COLUMNS = 122
NUMBER_OF_COLUMNS_DOESNT_MATCH = 20


# Matrix inputs for ``compatibility_matrix``: columns available in the
# source/destination schema, source and destination PARTITION BY term
# tuples, and value shapes chosen to hit every oracle branch.
COLUMNS = [
    {"name": "id", "type": "Int64"},
    {"name": "a", "type": "Int32"},
    {"name": "b", "type": "Int32"},
    {"name": "c", "type": "Int32"},
    {"name": "dt", "type": "Date"},
    {"name": "ts", "type": "DateTime"},
    {"name": "s", "type": "String"},
]

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


def _partition_by_sql(terms):
    """Render a term tuple as the SQL body of a ``PARTITION BY`` clause."""
    if not terms:
        return "tuple()"
    if len(terms) == 1:
        return terms[0]
    return "(" + ", ".join(terms) + ")"


def _term_column(term):
    """Return the underlying column a source term operates on
    (``toYYYYMM(dt)`` -> ``dt``, ``a % 4`` -> ``a``, ``a`` -> ``a``)."""
    if "(" in term:
        return term[term.index("(") + 1 : term.rindex(")")].split(",")[0].strip()
    if "%" in term:
        return term.split("%")[0].strip()
    return term.strip()


def _predict_accept(source_terms, dest_terms, min_max):
    """Predict whether the hive gate accepts. Returns
    ``(accept, expected_substrings)``; on reject every substring in the
    tuple must appear in the ``BAD_ARGUMENTS`` message so both the
    reason and the offending column are pinned.
    """
    if tuple(source_terms) == tuple(dest_terms):
        return True, ()
    if not dest_terms:
        return True, ()
    source_terms_set = set(source_terms)
    source_cols = {_term_column(t) for t in source_terms}
    for col in dest_terms:
        if col in source_terms_set:
            continue
        if col not in source_cols:
            return False, (f"column '{col}'",)
        lo, hi = min_max[col]
        if lo != hi:
            return False, ("multiple destination partitions", f"column '{col}'")
    return True, ()


@TestScenario
def oracle_self_tests(self):
    """Pin ``_predict_accept`` on every decision path in pure Python so
    an oracle regression is caught before any ClickHouse run."""
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
            ("multiple destination partitions", "column 'a'"),
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
            ("multiple destination partitions", "column 'dt'"),
            "monthly source, bare dt destination, exported partition holds two days",
        ),
    ]
    for (
        source_terms,
        dest_terms,
        min_max,
        expect_accept,
        expect_subs,
        note_text,
    ) in cases:
        accept, substrings = _predict_accept(source_terms, dest_terms, min_max)
        assert accept == expect_accept, error(
            f"{note_text}: expected accept={expect_accept}, got {accept}"
        )
        assert substrings == expect_subs, error(
            f"{note_text}: expected substrings={expect_subs!r}, got {substrings!r}"
        )


@TestScenario
def check_case(self, source_terms, dest_terms, shape_name, shape_values):
    """One matrix cell: build the tables, insert the shape, export the
    first source partition, and compare the gate's response to the
    oracle. Only the first source partition is exercised per cell (the
    remaining partitions are structurally homogeneous, so testing them
    is redundant; heterogeneous per-table behaviour is covered by
    ``per_partition_acceptance``).
    """
    node = self.context.node
    with Given("source RMT and hive S3 destination"):
        source_table, destination_table = setup_source_and_hive_destination(
            src_columns=COLUMNS,
            src_partition_by=_partition_by_sql(source_terms),
            dst_partition_by=_partition_by_sql(dest_terms),
        )
    with And("data inserted into source"):
        insert_values(table_name=source_table, values=", ".join(shape_values))

    with When("I pick the first source partition and read its min/max"):
        partition_id = get_first_partition_id(table_name=source_table)
        relevant_cols = sorted(
            {_term_column(t) for t in source_terms} | set(dest_terms)
        )
        min_max = get_partition_min_max(
            source_table=source_table,
            partition_id=partition_id,
            columns=relevant_cols,
            node=node,
        )
    expect_accept, expect_substrings = _predict_accept(
        source_terms, dest_terms, min_max
    )

    if expect_accept:
        with Then("the export succeeds"):
            export_partition_by_id(
                source_table=source_table,
                destination_table=destination_table,
                partition_id=partition_id,
                node=node,
            )
        with And("destination rows equal the exported source partition"):
            src_rows = select_rows(
                table_name=source_table,
                where=f"_partition_id = '{partition_id}'",
                order_by="id",
            )
            dst_rows = select_rows(table_name=destination_table, order_by="id")
            assert src_rows == dst_rows, error()
    else:
        with Then("the export is rejected with BAD_ARGUMENTS and nothing is scheduled"):
            assert_export_rejected(
                source_table=source_table,
                destination_table=destination_table,
                partition_id=partition_id,
                exitcode=BAD_ARGUMENTS,
                expected_substrings=("BAD_ARGUMENTS",) + expect_substrings,
            )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def compatibility_matrix(self):
    """Assert every ``product(SOURCE_KEYS, DEST_KEYS, SHAPES)``
    combination against the oracle."""
    with Pool(4) as pool:
        for source_terms, dest_terms, (shape_name, shape_values) in product(
            SOURCE_KEYS, DEST_KEYS, list(SHAPES.items())
        ):
            name = (
                f"src[{_partition_by_sql(source_terms)}] "
                f"dst[{_partition_by_sql(dest_terms)}] "
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
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="toYYYYMM(dt)",
        dst_partition_by="dt",
    )
    insert_values(
        table_name=source_table,
        values="(1, '2024-03-05'), (2, '2024-03-20'), (3, '2024-04-10')",
    )

    with When("I export the March partition (two days)"):
        assert_export_rejected(
            source_table=source_table,
            destination_table=destination_table,
            partition_id="202403",
            exitcode=BAD_ARGUMENTS,
            expected_substrings=(
                "BAD_ARGUMENTS",
                "multiple destination partitions",
                "column 'dt'",
            ),
        )
    with When("I export the April partition (single day)"):
        export_partition_by_id(
            source_table=source_table,
            destination_table=destination_table,
            partition_id="202404",
            node=self.context.node,
        )
    with Then("only the April row is in the destination"):
        rows = select_rows(
            table_name=destination_table, columns="id, dt", order_by="id"
        )
        assert rows == "3\t2024-04-10", error(f"got: {rows!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def multi_part_partition_reject(self):
    """The gate must fold min/max across all parts of a source partition,
    not judge per part. Two single-day inserts (kept as separate parts by
    stopping merges) span two days in aggregate and must reject."""
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="toYYYYMM(dt)",
        dst_partition_by="dt",
        stop_merges=True,
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05')")
    insert_values(table_name=source_table, values="(2, '2024-03-20')")

    with And("both inserts landed as separate active parts"):
        parts = count_rows(
            table_name="system.parts",
            where=(f"table = '{source_table}' AND partition_id = '202403' AND active"),
        )
        assert parts == 2, error(f"expected 2 active parts, got {parts}")

    assert_export_rejected(
        source_table=source_table,
        destination_table=destination_table,
        partition_id="202403",
        exitcode=BAD_ARGUMENTS,
        expected_substrings=(
            "BAD_ARGUMENTS",
            "multiple destination partitions",
            "column 'dt'",
        ),
    )


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
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="(year, toYYYYMM(dt), country)",
        dst_partition_by="(year, dt, country)",
    )
    insert_values(
        table_name=source_table,
        values=(
            "(1, 2024, '2024-03-05', 'US'), (2, 2024, '2024-03-05', 'US'), "
            "(3, 2024, '2024-03-05', 'FR'), (4, 2024, '2024-03-20', 'FR')"
        ),
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
        rows = select_rows(
            table_name=destination_table,
            columns="id, year, dt, country",
            order_by="id",
        )
        assert rows == ("1\t2024\t2024-03-05\tUS\n2\t2024\t2024-03-05\tUS"), error(
            f"got: {rows!r}"
        )

    with When("I export the two-day FR partition"):
        assert_export_rejected(
            source_table=source_table,
            destination_table=destination_table,
            partition_id=fr_partition,
            exitcode=BAD_ARGUMENTS,
            expected_substrings=(
                "BAD_ARGUMENTS",
                "multiple destination partitions",
                "column 'dt'",
            ),
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def export_partition_all_gate_is_atomic(self):
    """``EXPORT PARTITION ALL`` runs the gate synchronously while
    scheduling, so a single failing partition rejects the whole ALTER
    with ``BAD_ARGUMENTS``. ``export_merge_tree_partition_all_on_error``
    governs **runtime** conflicts during async processing, not the
    scheduling-time gate: ``skip_conflicts`` still yields the same
    reject.
    """
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="toYYYYMM(dt)",
        dst_partition_by="dt",
    )
    insert_values(
        table_name=source_table,
        values="(1, '2024-03-05'), (2, '2024-03-20'), (3, '2024-04-10')",
    )

    for on_error in ("throw_first", "skip_conflicts"):
        with When(f"I run EXPORT PARTITION ALL with on_error={on_error}"):
            result = node.query(
                f"ALTER TABLE {source_table} EXPORT PARTITION ALL "
                f"TO TABLE {destination_table} "
                f"SETTINGS export_merge_tree_partition_all_on_error = '{on_error}'",
                settings=self.context.default_settings,
                exitcode=BAD_ARGUMENTS,
                ignore_exception=True,
            )
        with Then(f"[{on_error}] the whole ALTER is rejected synchronously"):
            for fragment in (
                "BAD_ARGUMENTS",
                "multiple destination partitions",
                "column 'dt'",
            ):
                assert fragment in result.output, error(result.output)
        with And(f"[{on_error}] nothing is scheduled and destination stays empty"):
            assert_no_scheduled_exports(
                source_table=source_table,
                destination_table=destination_table,
                node=node,
            )
            assert count_rows(table_name=destination_table) == 0, error(
                f"[{on_error}] expected empty destination"
            )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def subset_round_trip(self):
    """Flagship new-accept case: source ``(year, country)`` -> destination
    ``year``. Every source partition holds one year, so all export through
    the per-column fast path. Round-trip through S3 back into a fresh RMT
    to assert end-to-end data integrity.
    """
    node = self.context.node
    columns = [
        {"name": "id", "type": "UInt64"},
        {"name": "year", "type": "UInt16"},
        {"name": "country", "type": "String"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="(year, country)",
        dst_partition_by="year",
    )
    insert_values(
        table_name=source_table,
        values="(1, 2020, 'US'), (2, 2020, 'FR'), (3, 2021, 'US')",
    )

    with When("I export every source partition"):
        for partition_id in get_partitions(table_name=source_table, node=node):
            export_partition_by_id(
                source_table=source_table,
                destination_table=destination_table,
                partition_id=partition_id,
                node=node,
            )

    src_rows = select_rows(
        table_name=source_table, columns="id, year, country", order_by="id"
    )
    dst_rows = select_rows(
        table_name=destination_table, columns="id, year, country", order_by="id"
    )
    with Then("the destination holds every source row"):
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
        rt_rows = select_rows(
            table_name=roundtrip_table, columns="id, year, country", order_by="id"
        )
        assert rt_rows == src_rows, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def reversed_multicolumn_partition_key_layout(self):
    """Source ``PARTITION BY (year, country)``, destination
    ``PARTITION BY (country, year)``. Gate accepts (both terms are bare
    columns of source key). Assert destination partition directories
    reflect the destination ``(country, year)`` order.
    """
    node = self.context.node
    columns = [
        {"name": "id", "type": "UInt64"},
        {"name": "year", "type": "UInt16"},
        {"name": "country", "type": "String"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="(year, country)",
        dst_partition_by="(country, year)",
    )
    insert_values(table_name=source_table, values="(1, 2024, 'FR')")

    source_partition = get_first_partition_id(table_name=source_table)
    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=source_partition,
        node=node,
    )

    with Then("destination row content matches source"):
        rows = select_rows(
            table_name=destination_table, columns="id, year, country", order_by="id"
        )
        assert rows == "1\t2024\tFR", error(f"got: {rows!r}")

    with And("destination hive directories lead with country, not year"):
        dst_path = select_rows(table_name=destination_table, columns="DISTINCT _path")
        assert "/country=FR/year=2024/" in dst_path, error(
            f"expected destination hive layout '/country=FR/year=2024/' "
            f"(destination key order), got {dst_path!r} "
            f"(source partition was {source_partition!r})"
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def swapped_same_type_columns_positional_cast(self):
    """Two same-type payload columns with the same names on both sides
    but their positions swapped between source and destination. The
    gate compares by name (both sides ``PARTITION BY ts``) and accepts,
    while payload CAST is positional, so source ``ts`` would land in
    destination ``x`` and vice versa. Compare by explicit column name
    (``SELECT *`` would print identically under a swap) and pin the
    destination ``ts`` holding source ``ts`` values (2024), not source
    ``x`` values (2020).
    """
    node = self.context.node
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "ts", "type": "DateTime"},
        {"name": "x", "type": "DateTime"},
    ]
    dst_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "x", "type": "DateTime"},
        {"name": "ts", "type": "DateTime"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="ts",
    )
    insert_values(
        table_name=source_table,
        values=(
            "(1, '2024-03-05 12:00:00', '2020-01-01 09:00:00'), "
            "(2, '2024-03-05 12:00:00', '2020-01-02 09:00:00')"
        ),
    )

    partition_id = get_first_partition_id(table_name=source_table)
    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=partition_id,
        node=node,
    )

    with Then("values stay with the column they came from (name-based compare)"):
        src_rows = select_rows(
            table_name=source_table, columns="id, ts, x", order_by="id"
        )
        dst_rows = select_rows(
            table_name=destination_table, columns="id, ts, x", order_by="id"
        )
        assert src_rows == dst_rows, error(
            f"schema-swap silently corrupted values:\nsrc={src_rows!r}\ndst={dst_rows!r}"
        )
    with And("destination ts holds 2024 (source ts), destination x holds 2020"):
        dst_ts_years = select_rows(
            table_name=destination_table,
            columns="DISTINCT toYear(ts)",
            order_by="1",
        )
        assert dst_ts_years == "2024", error(f"got dst ts years: {dst_ts_years!r}")
        dst_x_years = select_rows(
            table_name=destination_table,
            columns="DISTINCT toYear(x)",
            order_by="1",
        )
        assert dst_x_years == "2020", error(f"got dst x years: {dst_x_years!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def swap_under_multi_part_and_export_all(self):
    """Combine the schema-swap hazard with multi-part partitions and
    ``EXPORT PARTITION ALL``. Source has two source partitions each
    landing as separate parts (merges stopped). Assert swap invariants
    hold for every partition exported via one ``EXPORT PARTITION ALL``.
    """
    node = self.context.node
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "ts", "type": "DateTime"},
        {"name": "x", "type": "DateTime"},
    ]
    dst_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "x", "type": "DateTime"},
        {"name": "ts", "type": "DateTime"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="toDate(ts)",
        stop_merges=True,
    )
    insert_values(
        table_name=source_table,
        values="(1, '2024-03-05 12:00:00', '2020-01-01 09:00:00')",
    )
    insert_values(
        table_name=source_table,
        values="(2, '2024-04-10 12:00:00', '2020-02-02 09:00:00')",
    )

    with When("I run EXPORT PARTITION ALL and wait for both to COMPLETE"):
        node.query(
            f"ALTER TABLE {source_table} EXPORT PARTITION ALL "
            f"TO TABLE {destination_table}",
            settings=self.context.default_settings,
        )
        for partition_id in get_partitions(table_name=source_table, node=node):
            wait_for_export_to_complete(
                source_table=source_table, partition_id=partition_id, node=node
            )

    with Then("values stay with the column they came from on every row"):
        src_rows = select_rows(
            table_name=source_table, columns="id, ts, x", order_by="id"
        )
        dst_rows = select_rows(
            table_name=destination_table, columns="id, ts, x", order_by="id"
        )
        assert src_rows == dst_rows, error(
            f"schema-swap corruption under EXPORT PARTITION ALL:\n"
            f"src={src_rows!r}\ndst={dst_rows!r}"
        )
    with And("destination ts holds 2024 across both partitions"):
        dst_ts_years = select_rows(
            table_name=destination_table,
            columns="DISTINCT toYear(ts)",
            order_by="1",
        )
        assert dst_ts_years == "2024", error(f"got: {dst_ts_years!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def extra_destination_column_without_default(self):
    """Destination has an extra payload column without ``DEFAULT`` /
    ``MATERIALIZED``. Positional CAST cannot bind it. Expected: reject
    at the schema guard with ``NUMBER_OF_COLUMNS_DOESNT_MATCH`` (190).
    """
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "a", "type": "Int32"},
    ]
    dst_columns = src_columns + [{"name": "b", "type": "Int32"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="a",
    )
    insert_values(table_name=source_table, values="(1, 42)")

    assert_export_rejected(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        exitcode=NUMBER_OF_COLUMNS_DOESNT_MATCH,
        expected_substrings=("NUMBER_OF_COLUMNS_DOESNT_MATCH",),
    )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def extra_destination_column_with_default(self):
    """Destination has an extra payload column with ``DEFAULT``.
    Positional INSERT semantics should populate it from the default
    expression. Expected: accept; destination has the extra column
    filled with the default (42 here).
    """
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "a", "type": "Int32"},
    ]
    dst_columns = src_columns + [
        {"name": "b", "type": "Int32", "default": "42"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="a",
    )
    insert_values(table_name=source_table, values="(1, 10), (2, 10)")

    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        node=self.context.node,
    )
    with Then("id and a match source, b is filled with the default"):
        rows = select_rows(
            table_name=destination_table, columns="id, a, b", order_by="id"
        )
        assert rows == "1\t10\t42\n2\t10\t42", error(f"got: {rows!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def extra_destination_column_materialized(self):
    """A hive S3 destination cannot declare an extra ``MATERIALIZED``
    column at all: the S3 engine accepts only ordinary columns, so
    ``CREATE TABLE`` is rejected before any export runs. This is also why
    the export arity check, which skips MATERIALIZED columns, cannot be
    exercised against a hive S3 destination.
    """
    node = self.context.node
    table_name = f"dst_{getuid()}"

    with Given("a temporary bucket path"):
        create_temp_bucket()

    with When("I create a hive S3 destination with a MATERIALIZED column"):
        node.query(
            f"CREATE TABLE {table_name} "
            f"(id Int64, a Int32, a_doubled Int32 MATERIALIZED a * 2) "
            f"ENGINE = S3('{self.context.uri}', "
            f"'{self.context.access_key_id}', "
            f"'{self.context.secret_access_key}', "
            f"filename='{table_name}', format='Parquet', "
            f"partition_strategy='hive') PARTITION BY a",
            exitcode=BAD_ARGUMENTS,
            message=(
                "DB::Exception: Special columns like MATERIALIZED, ALIAS or EPHEMERAL "
                "are not supported for s3 storage."
            ),
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def source_has_more_columns_than_destination(self):
    """Source has more payload columns than destination. Positional CAST
    cannot bind the tail. Expected: reject at the schema guard with
    ``NUMBER_OF_COLUMNS_DOESNT_MATCH`` (190).
    """
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "a", "type": "Int32"},
        {"name": "b", "type": "Int32"},
    ]
    dst_columns = src_columns[:2]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="a",
    )
    insert_values(table_name=source_table, values="(1, 10, 20)")

    assert_export_rejected(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        exitcode=NUMBER_OF_COLUMNS_DOESNT_MATCH,
        expected_substrings=("NUMBER_OF_COLUMNS_DOESNT_MATCH",),
    )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def partition_key_type_widening(self):
    """Same partition-key column name, safe widening cast on the type
    (``UInt16`` -> ``UInt32``). Expected: accept; destination values
    preserved.
    """
    src_columns = [
        {"name": "id", "type": "UInt64"},
        {"name": "year", "type": "UInt16"},
    ]
    dst_columns = [
        {"name": "id", "type": "UInt64"},
        {"name": "year", "type": "UInt32"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="year",
    )
    insert_values(table_name=source_table, values="(1, 2024), (2, 2024)")

    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        node=self.context.node,
    )
    with Then("destination holds the same values with the widened type"):
        rows = select_rows(
            table_name=destination_table, columns="id, year", order_by="id"
        )
        assert rows == "1\t2024\n2\t2024", error(f"got: {rows!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def partition_key_type_narrowing(self):
    """Same partition-key column name, unsafe narrowing cast on the type
    (``UInt32`` -> ``UInt16``). Expected: reject at the schema guard
    with ``INCOMPATIBLE_COLUMNS`` (122).
    """
    src_columns = [
        {"name": "id", "type": "UInt64"},
        {"name": "year", "type": "UInt32"},
    ]
    dst_columns = [
        {"name": "id", "type": "UInt64"},
        {"name": "year", "type": "UInt16"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="year",
    )
    insert_values(table_name=source_table, values="(1, 2024), (2, 2024)")

    assert_export_rejected(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        exitcode=INCOMPATIBLE_COLUMNS,
        expected_substrings=("INCOMPATIBLE_COLUMNS", "year"),
    )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def partition_key_timezone_drift(self):
    """Same partition-key column name and the same bare ``PARTITION BY ts``
    on both sides, but source ``ts`` is ``DateTime('UTC')`` and destination
    is ``DateTime('Asia/Tokyo')``. A timezone is only a parse/format
    attribute of ``DateTime``, so casting between two timezones keeps the
    underlying instant: the exported row must read back as the same point in
    time, and must agree with what ``INSERT ... SELECT`` puts in an
    identically shaped destination. Hive writes the partition value into the
    object path as text, so the paths are recorded too -- they show which
    timezone each writer formatted with.
    """
    node = self.context.node
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "ts", "type": "DateTime('UTC')"},
    ]
    dst_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "ts", "type": "DateTime('Asia/Tokyo')"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="ts",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05 15:00:00')")

    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        node=node,
    )
    with Given("a second destination of the same shape filled by INSERT SELECT"):
        inserted_table = create_s3_table(
            table_name="dst_inserted",
            create_new_bucket=True,
            columns=dst_columns,
            partition_by="ts",
        )
        node.query(f"INSERT INTO {inserted_table} SELECT * FROM {source_table}")

    with When("I read the instant and the hive path written by each writer"):
        epochs = node.query(
            f"SELECT toUnixTimestamp((SELECT ts FROM {source_table})), "
            f"toUnixTimestamp((SELECT ts FROM {destination_table})), "
            f"toUnixTimestamp((SELECT ts FROM {inserted_table})) "
            f"FORMAT TabSeparated"
        ).output.strip()
        src_epoch, exported_epoch, inserted_epoch = epochs.split("\t")
        exported_path = select_rows(
            table_name=destination_table, columns="DISTINCT _path"
        )
        inserted_path = select_rows(table_name=inserted_table, columns="DISTINCT _path")
        evidence = (
            f"source epoch={src_epoch}; "
            f"exported epoch={exported_epoch} path={exported_path!r}; "
            f"INSERT SELECT epoch={inserted_epoch} path={inserted_path!r}"
        )

    with Then("EXPORT PARTITION and INSERT SELECT store the same instant"):
        assert exported_epoch == inserted_epoch, error(evidence)
    with And("that instant is the source instant"):
        assert exported_epoch == src_epoch, error(evidence)
    with And("the destination reads it back in Tokyo, one day ahead of UTC"):
        exported_date = select_rows(
            table_name=destination_table, columns="DISTINCT toDate(ts)"
        )
        assert exported_date == "2024-03-06", error(
            f"expected destination-side toDate(ts) = 2024-03-06 (Tokyo), "
            f"got {exported_date!r}; {evidence}"
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def payload_lossy_cast_uint64_to_int32(self):
    """Lossy cast on a **payload** column (not the partition key).
    Source ``cnt UInt64``, destination ``cnt Int32``. Values that fit in
    Int32 still trigger ``INCOMPATIBLE_COLUMNS`` because the type
    mapping itself is unsafe; ``export_merge_tree_part_allow_lossy_cast``
    is the opt-in.
    """
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "dt", "type": "Date"},
        {"name": "cnt", "type": "UInt64"},
    ]
    dst_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "dt", "type": "Date"},
        {"name": "cnt", "type": "Int32"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="dt",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05', 100)")

    assert_export_rejected(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        exitcode=INCOMPATIBLE_COLUMNS,
        expected_substrings=("INCOMPATIBLE_COLUMNS", "cnt"),
        check_no_scheduled=False,
    )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def payload_lossy_cast_with_opt_in_accepts(self):
    """Paired with ``payload_lossy_cast_uint64_to_int32``: with
    ``export_merge_tree_part_allow_lossy_cast = 1`` the same
    UInt64 -> Int32 payload cast is accepted (values that fit in Int32
    land correctly; the setting is the user's explicit opt-in).
    """
    node = self.context.node
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "dt", "type": "Date"},
        {"name": "cnt", "type": "UInt64"},
    ]
    dst_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "dt", "type": "Date"},
        {"name": "cnt", "type": "Int32"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="dt",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05', 100)")

    partition_id = get_first_partition_id(table_name=source_table)
    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=partition_id,
        node=node,
        query_settings_sql=(" SETTINGS export_merge_tree_part_allow_lossy_cast = 1"),
    )
    with Then("destination has the row with cnt preserved"):
        row = select_rows(table_name=destination_table, columns="id, dt, cnt")
        assert row == "1\t2024-03-05\t100", error(f"got: {row!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def partition_key_case_sensitivity(self):
    """Column names are case-sensitive: source column is ``Ts``,
    destination is ``ts``. The name-based gate must reject with
    ``column 'ts'`` (not found in source key).
    """
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "Ts", "type": "DateTime"},
    ]
    dst_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "ts", "type": "DateTime"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="Ts",
        dst_partition_by="ts",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05 12:00:00')")

    assert_export_rejected(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        exitcode=BAD_ARGUMENTS,
        expected_substrings=("BAD_ARGUMENTS", "column 'ts'"),
    )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def payload_column_name_mismatch(self):
    """Realistic ETL shape: source names its date ``order_date``,
    destination renames it to ``ship_date``. Positional CAST would
    happily land the values, but the name-based gate must reject with
    ``column 'ship_date'`` (not in source key columns).
    """
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "order_date", "type": "DateTime"},
    ]
    dst_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "ship_date", "type": "DateTime"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="order_date",
        dst_partition_by="ship_date",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05 12:00:00')")

    assert_export_rejected(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        exitcode=BAD_ARGUMENTS,
        expected_substrings=("BAD_ARGUMENTS", "column 'ship_date'"),
    )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def algebraically_equivalent_partition_expression(self):
    """A destination key that is algebraically equivalent to the source key
    but textually different (source ``toYYYYMM(dt)``, destination
    ``toYYYYMM(dt) + 0``) cannot be set up at all: hive partitioning
    requires every partition-by term to be a bare storage column, so
    ``CREATE TABLE`` is rejected before any export runs. This is why the
    gate's textual-versus-semantic comparison cannot be reached from a hive
    S3 destination.
    """
    node = self.context.node
    table_name = f"dst_{getuid()}"

    with Given("a temporary bucket path"):
        create_temp_bucket()

    with When("I create a hive S3 destination with an expression partition key"):
        node.query(
            f"CREATE TABLE {table_name} "
            f"(id Int64, dt Date) "
            f"ENGINE = S3('{self.context.uri}', "
            f"'{self.context.access_key_id}', "
            f"'{self.context.secret_access_key}', "
            f"filename='{table_name}', format='Parquet', "
            f"partition_strategy='hive') PARTITION BY toYYYYMM(dt) + 0",
            exitcode=BAD_ARGUMENTS,
            message=(
                "DB::Exception: Hive partitioning expects that the partition by "
                "expression columns are a part of the storage columns"
            ),
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def partition_key_lowcardinality_string(self):
    """``LowCardinality(String)`` is the default string type in real-world
    analytics tables, but hive partitioning accepts only plain ``String``
    or ``FixedString`` for a partition column (see
    ``partition_key_unsupported_types_hive_rejects``). So the realistic
    shape is a ``LowCardinality(String)`` source key exported into a
    ``String`` destination key, which the export has to cast. Round-trip
    every partition and confirm the values survive.
    """
    node = self.context.node
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "country", "type": "LowCardinality(String)"},
    ]
    dst_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "country", "type": "String"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="country",
    )
    insert_values(table_name=source_table, values="(1, 'FR'), (2, 'FR'), (3, 'US')")

    with When("I export every source partition"):
        for partition_id in get_partitions(table_name=source_table, node=node):
            export_partition_by_id(
                source_table=source_table,
                destination_table=destination_table,
                partition_id=partition_id,
                node=node,
            )
    with Then("destination holds every source row"):
        src_rows = select_rows(
            table_name=source_table, columns="id, country", order_by="id"
        )
        dst_rows = select_rows(
            table_name=destination_table, columns="id, country", order_by="id"
        )
        assert src_rows == dst_rows, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def partition_key_fixedstring(self):
    """``FixedString(N)`` is in the Hive-supported partition types list.
    Round-trip a partition and confirm rows match.
    """
    columns = [
        {"name": "id", "type": "Int64"},
        {"name": "code", "type": "FixedString(3)"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="code",
    )
    insert_values(table_name=source_table, values="(1, 'FRA'), (2, 'FRA')")

    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        node=self.context.node,
    )
    with Then("destination holds both rows"):
        src_rows = select_rows(
            table_name=source_table, columns="id, code", order_by="id"
        )
        dst_rows = select_rows(
            table_name=destination_table, columns="id, code", order_by="id"
        )
        assert src_rows == dst_rows, error()


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def partition_key_datetime64(self):
    """``DateTime64(N)`` is a hive-supported partition type. Hive carries
    the partition value as text in the object path, so the sub-second part
    has to survive that round trip. Export a partition and confirm the
    value comes back with its milliseconds intact.
    """
    columns = [
        {"name": "id", "type": "Int64"},
        {"name": "ts", "type": "DateTime64(3)"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="ts",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05 15:00:00.123')")

    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        node=self.context.node,
    )
    with Then("the destination holds the same value, milliseconds included"):
        src_rows = select_rows(table_name=source_table, columns="id, ts", order_by="id")
        dst_rows = select_rows(
            table_name=destination_table, columns="id, ts", order_by="id"
        )
        assert src_rows == dst_rows, error(f"src={src_rows!r}, dst={dst_rows!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def partition_key_unsupported_types_hive_rejects(self):
    """Hive partitioning accepts the integer widths, ``String``,
    ``FixedString``, ``Date``, ``Date32``, ``Time``, ``Time64``,
    ``DateTime``, ``DateTime64`` and ``Bool`` as partition columns (see
    ``RQ.HivePartitioning.Writes.DataTypes``) -- the server's error text
    names a shorter summary than the set it actually accepts. Iterate over
    types outside that set and confirm destination CREATE TABLE rejects
    each one.
    """
    node = self.context.node

    with Given("a temporary bucket path"):
        create_temp_bucket()

    cases = [
        ("Nullable(Int32)", "Nullable(Int32)"),
        ("Enum8", "Enum8('a' = 1, 'b' = 2)"),
        ("UUID", "UUID"),
        ("Decimal(9, 2)", "Decimal(9, 2)"),
        ("LowCardinality(String)", "LowCardinality(String)"),
    ]
    for label, type_expr in cases:
        with When(f"I try to CREATE the destination with PARTITION BY {label}"):
            table_name = f"dst_unsupported_{getuid()}"
            engine = (
                f"S3('{self.context.uri}', '{self.context.access_key_id}', "
                f"'{self.context.secret_access_key}', filename='{table_name}', "
                f"format='Parquet', compression='auto', "
                f"partition_strategy='hive')"
            )
            result = node.query(
                f"CREATE TABLE {table_name} (id Int64, k {type_expr}) "
                f"ENGINE = {engine} PARTITION BY k",
                no_checks=True,
                settings=self.context.default_settings,
            )
        with Then(f"[{label}] CREATE TABLE fails with the Hive type-restriction"):
            assert result.exitcode != 0, error(
                f"[{label}] expected CREATE TABLE to fail, exit={result.exitcode}"
            )
            assert (
                "Hive partitioning" in result.output
                or "partition column" in result.output
            ), error(
                f"[{label}] expected Hive-partitioning error, got: {result.output!r}"
            )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def payload_complex_types_round_trip(self):
    """Payload columns (not partition key) can be complex types
    (Nullable, LowCardinality, Array, Tuple). Round-trip a mixed-bag
    payload and confirm every column value is preserved.
    """
    columns = [
        {"name": "id", "type": "Int64"},
        {"name": "dt", "type": "Date"},
        {"name": "n", "type": "Nullable(Int64)"},
        {"name": "s", "type": "LowCardinality(String)"},
        {"name": "arr", "type": "Array(Int32)"},
        {"name": "tpl", "type": "Tuple(a Int32, b String)"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="dt",
    )
    insert_values(
        table_name=source_table,
        values=(
            "(1, '2024-03-05', 42, 'FR', [1, 2, 3], (7, 'seven')), "
            "(2, '2024-03-05', NULL, 'US', [], (0, ''))"
        ),
    )

    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        node=self.context.node,
    )
    with Then("destination row content matches source column-by-column"):
        src_rows = select_rows(
            table_name=source_table,
            columns="id, dt, n, s, arr, tpl",
            order_by="id",
        )
        dst_rows = select_rows(
            table_name=destination_table,
            columns="id, dt, n, s, arr, tpl",
            order_by="id",
        )
        assert src_rows == dst_rows, error(f"\nsrc={src_rows!r}\ndst={dst_rows!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def re_export_same_partition_idempotency(self):
    """Recovery-flow question: what happens if I export the same source
    partition twice back-to-back? Users must not silently double their
    data — either the count stays at 1 (no-op / idempotent) or the
    second call errors; duplication would be a bug.
    """
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="dt",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05')")
    partition_id = get_first_partition_id(table_name=source_table)

    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=partition_id,
        node=node,
    )
    assert count_rows(table_name=destination_table) == 1, error(
        "expected 1 row after first export"
    )

    with When("I export the same partition a second time"):
        second = node.query(
            f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition_id}' "
            f"TO TABLE {destination_table}",
            settings=self.context.default_settings,
            no_checks=True,
        )
    with Then("re-export must not silently double the destination"):
        second_count = count_rows(table_name=destination_table)
        note(
            f"re-export exit={second.exitcode}, destination row count "
            f"went from 1 to {second_count}"
        )
        assert not (second.exitcode == 0 and second_count == 2), error(
            f"re-export silently duplicated the row: dst count = {second_count}, "
            f"second-call exit = {second.exitcode}"
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def export_drop_source_partition_export_again(self):
    """User workflow: export a partition, drop it from source (data is
    safely in S3 now), then attempt to export the same partition_id
    again. Must not silently double the destination.
    """
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="dt",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05')")
    partition_id = get_first_partition_id(table_name=source_table)

    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=partition_id,
        node=node,
    )
    drop_partition_by_id(table_name=source_table, partition_id=partition_id)
    with When("I attempt to export the same partition_id again"):
        result = node.query(
            f"ALTER TABLE {source_table} EXPORT PARTITION ID '{partition_id}' "
            f"TO TABLE {destination_table}",
            settings=self.context.default_settings,
            no_checks=True,
        )
    with Then("the second export does not silently succeed"):
        dst_count = count_rows(table_name=destination_table)
        note(
            f"post-drop re-export exit={result.exitcode}, destination count={dst_count}"
        )
        assert dst_count == 1, error(
            f"post-drop re-export changed destination unexpectedly: "
            f"exit={result.exitcode}, count={dst_count}"
        )


def _run_export_under_failpoint(
    self,
    source_table,
    destination_table,
    partition_id,
    node,
    mid_flight_action,
):
    """Common driver for the "concurrent X during export under failpoint"
    scenarios: enable the retryable failpoint, start the export, wait for
    a retry to be observed, run ``mid_flight_action()`` while the export
    is stalled, then disable the failpoint and wait for completion.

    The failpoint is armed on every replica, not just the one issuing the
    ALTER: any replica can pick up the part, so arming a single node leaves
    the export free to succeed elsewhere and never stall.
    """
    try:
        with When("I enable the retryable failpoint and schedule the export"):
            enable_failpoint(failpoint=RETRYABLE_FAILPOINT)
            start_export(
                source_table=source_table,
                destination_table=destination_table,
                partition=partition_id,
                node=node,
                settings=short_backoff_settings(initial=1, max_backoff=2),
            )
        with And("I wait until at least one retry has been observed"):
            wait_for_exception_count(
                source_table=source_table,
                partition=partition_id,
                min_count=1,
                node=node,
                timeout=30,
                delay=1,
            )
        with And("I perform the mid-flight action"):
            mid_flight_action()
        with When("I disable the failpoint and wait for COMPLETED"):
            disable_failpoint(failpoint=RETRYABLE_FAILPOINT)
            wait_for_export_to_complete(
                source_table=source_table,
                partition_id=partition_id,
                node=node,
            )
    finally:
        for cluster_node in self.context.nodes:
            cluster_node.query(
                f"SYSTEM DISABLE FAILPOINT {RETRYABLE_FAILPOINT}", no_checks=True
            )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def concurrent_insert_during_export_under_failpoint(self):
    """Under a retryable failpoint (export retries with backoff), insert
    a new row into the same source partition mid-flight. The export's
    effect on the destination must be limited to parts registered at
    scheduling time — new inserts must not silently land without a
    second EXPORT.
    """
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="dt",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05')")
    partition_id = get_first_partition_id(table_name=source_table)

    _run_export_under_failpoint(
        self,
        source_table=source_table,
        destination_table=destination_table,
        partition_id=partition_id,
        node=node,
        mid_flight_action=lambda: insert_values(
            table_name=source_table, values="(2, '2024-03-05')"
        ),
    )

    with Then("destination must not silently include the mid-export insert"):
        dst_ids = select_rows(table_name=destination_table, columns="id", order_by="id")
        assert dst_ids == "1", error(
            f"expected only id=1 in destination (scheduler must freeze part-list "
            f"at registration), got ids={dst_ids!r}"
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def concurrent_merge_during_export(self):
    """Source has two parts (merges stopped). Under a retryable
    failpoint, re-enable merges so the two parts collapse into one
    while the export retries. Destination must match the source at
    scheduling time.
    """
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="dt",
        stop_merges=True,
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05')")
    insert_values(table_name=source_table, values="(2, '2024-03-05')")
    partition_id = get_first_partition_id(table_name=source_table)

    def _merge_parts():
        node.query(f"SYSTEM START MERGES {source_table}")
        node.query(f"OPTIMIZE TABLE {source_table} FINAL")

    _run_export_under_failpoint(
        self,
        source_table=source_table,
        destination_table=destination_table,
        partition_id=partition_id,
        node=node,
        mid_flight_action=_merge_parts,
    )

    with Then("destination contains both original rows exactly once"):
        dst_rows = select_rows(
            table_name=destination_table, columns="id, dt", order_by="id"
        )
        assert dst_rows == "1\t2024-03-05\n2\t2024-03-05", error(f"got: {dst_rows!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def accept_records_completed_task_in_system_table(self):
    """A successful export leaves a COMPLETED row with sane metadata in
    ``system.replicated_partition_exports``. Pin the happy-path shape.
    """
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="dt",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05')")
    partition_id = get_first_partition_id(table_name=source_table)

    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=partition_id,
        node=node,
    )
    with Then("system.replicated_partition_exports has a COMPLETED row"):
        row = select_rows(
            table_name="system.replicated_partition_exports",
            columns="status, exception_count, partition_id, destination_table",
            where=(
                f"source_table = '{source_table}' "
                f"AND partition_id = '{partition_id}'"
            ),
        )
        assert row, error("no row in system.replicated_partition_exports")
        status, exc_count, part_id, dst = row.split("\t")
        assert status == "COMPLETED", error(f"status={status!r}")
        assert exc_count == "0", error(f"exception_count={exc_count!r}")
        assert part_id == partition_id, error(f"partition_id={part_id!r}")
        assert dst == destination_table, error(f"destination_table={dst!r}")


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def query_log_contains_export_partition_query(self):
    """Basic auditability: after ``ALTER TABLE ... EXPORT PARTITION``,
    the query must show up in ``system.query_log`` (QueryFinish event)
    so operators can see when an export was triggered.
    """
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="dt",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05')")

    export_partition_by_id(
        source_table=source_table,
        destination_table=destination_table,
        partition_id=get_first_partition_id(table_name=source_table),
        node=node,
    )
    node.query("SYSTEM FLUSH LOGS")

    with Then("system.query_log has a QueryFinish for the EXPORT PARTITION statement"):
        finish_rows = count_rows(
            table_name="system.query_log",
            where=(
                "type = 'QueryFinish' "
                "AND query LIKE '%EXPORT PARTITION%' "
                f"AND query LIKE '%{source_table}%' "
                f"AND query LIKE '%{destination_table}%'"
            ),
        )
        assert finish_rows >= 1, error(
            f"expected >=1 QueryFinish for EXPORT PARTITION on "
            f"{source_table} -> {destination_table}, got {finish_rows}"
        )


@TestSuite
def oracle(self):
    """Pure-Python self-tests for ``_predict_accept``."""
    Scenario(run=oracle_self_tests)


@TestSuite
def gate_decisions(self):
    """Core gate accept/reject behavior: the full matrix plus targeted
    per-partition, multi-part, three-term-destination, and
    ``EXPORT PARTITION ALL`` variants."""
    Scenario(run=compatibility_matrix)
    Scenario(run=per_partition_acceptance)
    Scenario(run=multi_part_partition_reject)
    Scenario(run=three_term_destination_mixed_decisions)
    Scenario(run=export_partition_all_gate_is_atomic)


@TestSuite
def data_integrity_round_trip(self):
    """End-to-end integrity of accepted exports and destination partition
    layout follows the destination DDL, not the source."""
    Scenario(run=subset_round_trip)
    Scenario(run=reversed_multicolumn_partition_key_layout)


@TestSuite
def positional_cast_hazards(self):
    """Name-based partition-key gate + positional payload CAST can
    silently corrupt data when schema positions disagree."""
    Scenario(run=swapped_same_type_columns_positional_cast)
    Scenario(run=swap_under_multi_part_and_export_all)


@TestSuite
def schema_arity_and_defaults(self):
    """Payload column-count mismatches (extra dest with/without DEFAULT
    or MATERIALIZED; source has more columns)."""
    Scenario(run=extra_destination_column_without_default)
    Scenario(run=extra_destination_column_with_default)
    Scenario(run=extra_destination_column_materialized)
    Scenario(run=source_has_more_columns_than_destination)


@TestSuite
def type_mismatch_and_lossy_cast(self):
    """Same-name partition-key column with different types (widen /
    narrow / timezone drift) and payload lossy-cast with/without opt-in."""
    Scenario(run=partition_key_type_widening)
    Scenario(run=partition_key_type_narrowing)
    Scenario(run=partition_key_timezone_drift)
    Scenario(run=payload_lossy_cast_uint64_to_int32)
    Scenario(run=payload_lossy_cast_with_opt_in_accepts)


@TestSuite
def partition_key_shape(self):
    """Name-based gate corner cases and non-bare destination partition
    keys: case sensitivity, renamed payload columns, and algebraically-
    equivalent expressions."""
    Scenario(run=partition_key_case_sensitivity)
    Scenario(run=payload_column_name_mismatch)
    Scenario(run=algebraically_equivalent_partition_expression)


@TestSuite
def production_types(self):
    """Real-world DDL type coverage for hive S3 partition columns."""
    Scenario(run=partition_key_lowcardinality_string)
    Scenario(run=partition_key_fixedstring)
    Scenario(run=partition_key_datetime64)
    Scenario(run=partition_key_unsupported_types_hive_rejects)
    Scenario(run=payload_complex_types_round_trip)


@TestSuite
def lifecycle_and_concurrency(self):
    """User workflows: re-export idempotency, export-then-drop
    -then-re-export, and concurrent INSERT / MERGE hitting an export
    that is retrying under a failpoint."""
    Scenario(run=re_export_same_partition_idempotency)
    Scenario(run=export_drop_source_partition_export_again)
    Scenario(run=concurrent_insert_during_export_under_failpoint)
    Scenario(run=concurrent_merge_during_export)


@TestSuite
def observability(self):
    """Successful exports leave a COMPLETED row in
    ``system.replicated_partition_exports`` and a ``QueryFinish`` in
    ``system.query_log`` for the initiating statement."""
    Scenario(run=accept_records_completed_task_in_system_table)
    Scenario(run=query_log_contains_export_partition_query)


@TestFeature
@Name("partition key compatibility")
def feature(self):
    """Partition-key compatibility gate for hive S3 exports."""
    Feature(run=oracle)
    Feature(run=gate_decisions)
    Feature(run=data_integrity_round_trip)
    Feature(run=positional_cast_hazards)
    Feature(run=schema_arity_and_defaults)
    Feature(run=type_mismatch_and_lossy_cast)
    Feature(run=partition_key_shape)
    Feature(run=production_types)
    Feature(run=lifecycle_and_concurrency)
    Feature(run=observability)
