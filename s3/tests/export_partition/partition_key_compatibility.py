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


# Every scenario in this module must exercise the compatibility gate added by
# Altinity/ClickHouse#2074, which only runs when the source and destination
# ``PARTITION BY`` differ. ``setup_source_and_hive_destination`` mirrors
# ``src_partition_by`` into ``dst_partition_by`` when the latter is omitted,
# which makes the two keys textually identical and short-circuits the gate on
# its identical-keys fast path -- i.e. pre-#2074 behaviour. So a scenario here
# either passes an explicit ``dst_partition_by`` that differs from the source,
# or it belongs in one of the general export suites (``datatypes``,
# ``schema_compatibility``, ``sanity``, ``system_monitoring``).
BAD_ARGUMENTS = 36

# The payload schema guard (``verifyExportSchemaCastable``) is a separate check
# from the partition-key gate, and its own coverage lives in
# ``schema_compatibility.py``. These codes are needed here only for the
# scenarios that make the two checks meet: #2074 hoists the schema guard ahead
# of the gate, and a cast on the destination partition column lands on exactly
# the column the gate's dynamic proof reasons about.
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
def partition_key_timezone_drift(self):
    """Timezone drift on a key pair that only this feature accepts.
    Source ``PARTITION BY toDate(ts)`` with ``ts DateTime('UTC')`` into a
    bare ``PARTITION BY ts`` destination with ``ts DateTime('Asia/Tokyo')``
    reaches the dynamic proof: ``ts`` is only present in the source key
    under ``toDate``, so the gate has to show the exported partition is
    single-valued on ``ts``.

    The gate reasons about min/max in the source's timezone while hive
    formats the partition value into the object path in the destination's,
    so the two can disagree on which calendar day this row belongs to. A
    timezone is only a parse/format attribute of ``DateTime``, so the
    underlying instant must survive: the exported row must read back as
    the same point in time and must agree with what ``INSERT ... SELECT``
    puts in an identically shaped destination. The paths are recorded too
    -- they show which timezone each writer formatted with.
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
        src_partition_by="toDate(ts)",
        dst_partition_by="ts",
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
def swapped_same_type_columns_positional_cast(self):
    """The partition-key gate matches destination terms by column **name**
    while the payload CAST is **positional**, and this feature widens the
    set of schema pairs that get through the gate -- so the two rules now
    disagree on more shapes than before.

    Source ``PARTITION BY (ts, x)`` into destination ``PARTITION BY ts``
    is accepted only via the per-column fast path (identical-key
    comparison rejects it). The two payload columns carry the same names
    and types on both sides but swapped positions, so a positional CAST
    would land source ``ts`` in destination ``x`` and vice versa. Compare
    by explicit column name (``SELECT *`` would print identically under a
    swap) and pin destination ``ts`` holding source ``ts`` values (2024),
    not source ``x`` values (2020).
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
        src_partition_by="(ts, x)",
        dst_partition_by="ts",
    )
    insert_values(
        table_name=source_table,
        values=(
            "(1, '2024-03-05 12:00:00', '2020-01-01 09:00:00'), "
            "(2, '2024-03-05 12:00:00', '2020-01-01 09:00:00')"
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
    """Combine the schema-swap hazard with the dynamic proof, multi-part
    partitions and ``EXPORT PARTITION ALL``.

    Source ``PARTITION BY toDate(ts)`` into destination ``PARTITION BY ts``
    can only be accepted by proving each exported partition is
    single-valued on ``ts``, and each partition here is spread over two
    parts (merges stopped), so the proof has to fold min/max across both.
    Every partition is scheduled by a single ``EXPORT PARTITION ALL``, and
    the swap invariants must hold for all of them.
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
        dst_partition_by="ts",
        stop_merges=True,
    )
    with Given("two partitions, each spread over two parts with one ts value"):
        insert_values(
            table_name=source_table,
            values="(1, '2024-03-05 12:00:00', '2020-01-01 09:00:00')",
        )
        insert_values(
            table_name=source_table,
            values="(2, '2024-03-05 12:00:00', '2020-01-02 09:00:00')",
        )
        insert_values(
            table_name=source_table,
            values="(3, '2024-04-10 12:00:00', '2020-02-02 09:00:00')",
        )
        insert_values(
            table_name=source_table,
            values="(4, '2024-04-10 12:00:00', '2020-02-03 09:00:00')",
        )
    with And("every source partition really has two active parts"):
        for partition_id in get_partitions(table_name=source_table, node=node):
            parts = count_rows(
                table_name="system.parts",
                where=(
                    f"table = '{source_table}' "
                    f"AND partition_id = '{partition_id}' AND active"
                ),
            )
            assert parts == 2, error(
                f"partition {partition_id}: expected 2 active parts, got {parts}"
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
    S3 destination, and why every destination term the gate sees is a bare
    column.
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
def schema_guard_runs_before_the_gate(self):
    """When a destination is wrong in **both** ways, which error wins?

    #2074 hoists ``verifyExportSchemaCastable`` ahead of the compatibility
    gate so that the gate "sees a resolved part and a validated schema".
    That makes the schema guard a precondition of the gate: if the payload
    schema does not line up, the gate cannot have run, so the schema error
    is the one the user must see.

    Source has one payload column more than the destination (positional
    CAST cannot bind the tail) **and** is partitioned by ``toYYYYMM(dt)``
    into a ``dt`` destination on a partition holding two days (the gate
    would reject it). Expect the schema error, deterministically, with
    nothing written.
    """
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "dt", "type": "Date"},
        {"name": "extra", "type": "Int32"},
    ]
    dst_columns = src_columns[:2]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="toYYYYMM(dt)",
        dst_partition_by="dt",
    )
    insert_values(
        table_name=source_table,
        values="(1, '2024-03-05', 1), (2, '2024-03-20', 2)",
    )

    with When("I export the partition that fails both checks"):
        result = assert_export_rejected(
            source_table=source_table,
            destination_table=destination_table,
            partition_id="202403",
            exitcode=NUMBER_OF_COLUMNS_DOESNT_MATCH,
            expected_substrings=("NUMBER_OF_COLUMNS_DOESNT_MATCH",),
            check_no_scheduled=False,
        )
    with Then("the schema guard reported it, not the partition-key gate"):
        assert "multiple destination partitions" not in result.output, error(
            f"expected the payload schema guard to reject first (#2074 hoists "
            f"verifyExportSchemaCastable ahead of the compatibility gate), but "
            f"the gate's split-partition error surfaced instead: {result.output!r}"
        )
    with And("nothing was written to the destination"):
        assert count_rows(table_name=destination_table) == 0, error(
            "expected an empty destination after a rejected export"
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def widened_type_on_dynamically_proved_partition_column(self):
    """The dynamic proof reads min/max from the source part's index in the
    **source** column type, while the value is written in the
    **destination's** type. Put a cast on exactly the column the proof
    reasons about: source ``PARTITION BY toYYYYMM(dt)`` with ``dt Date``
    into destination ``PARTITION BY dt`` with ``dt Date32``.

    ``dt`` is only in the source key under ``toYYYYMM``, so every decision
    here goes through the proof. The widening cast must not change either
    answer: a single-day partition still accepts and a two-day partition
    still rejects on ``column 'dt'``.
    """
    node = self.context.node
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "dt", "type": "Date"},
    ]
    dst_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "dt", "type": "Date32"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="toYYYYMM(dt)",
        dst_partition_by="dt",
    )
    insert_values(
        table_name=source_table,
        values=(
            "(1, '2024-03-05'), (2, '2024-03-05'), "
            "(3, '2024-04-10'), (4, '2024-04-25')"
        ),
    )

    with When("I export the single-day March partition"):
        export_partition_by_id(
            source_table=source_table,
            destination_table=destination_table,
            partition_id="202403",
            node=node,
        )
    with Then("the rows land with the day preserved under the widened type"):
        rows = select_rows(
            table_name=destination_table, columns="id, dt", order_by="id"
        )
        assert rows == "1\t2024-03-05\n2\t2024-03-05", error(f"got: {rows!r}")

    with When("I export the two-day April partition"):
        assert_export_rejected(
            source_table=source_table,
            destination_table=destination_table,
            partition_id="202404",
            exitcode=BAD_ARGUMENTS,
            expected_substrings=(
                "BAD_ARGUMENTS",
                "multiple destination partitions",
                "column 'dt'",
            ),
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def lossy_cast_on_dynamically_proved_partition_column(self):
    """The hive counterpart of the Iceberg lossy-cast partition-column
    path: a lossy cast landing on the column the dynamic proof runs over.

    Source ``PARTITION BY intDiv(n, 100)`` with ``n Int64`` into
    destination ``PARTITION BY n`` with ``n Int32``. ``n`` appears in the
    source key only under ``intDiv``, so acceptance depends on proving the
    partition single-valued on ``n``, and the ``Int64 -> Int32`` mapping is
    unsafe, so the payload guard needs
    ``export_merge_tree_part_allow_lossy_cast``.

    Without the opt-in the export is rejected on the cast. With it the
    export succeeds and the proof still holds: a cast can merge two source
    values into one destination value but never split one into two, so a
    partition proved single-valued in the source type stays single-valued
    in the destination type.
    """
    node = self.context.node
    src_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "n", "type": "Int64"},
    ]
    dst_columns = [
        {"name": "id", "type": "Int64"},
        {"name": "n", "type": "Int32"},
    ]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=src_columns,
        dst_columns=dst_columns,
        src_partition_by="intDiv(n, 100)",
        dst_partition_by="n",
    )
    insert_values(table_name=source_table, values="(1, 500), (2, 500)")
    partition_id = get_first_partition_id(table_name=source_table)

    with When("I export without the lossy-cast opt-in"):
        assert_export_rejected(
            source_table=source_table,
            destination_table=destination_table,
            partition_id=partition_id,
            exitcode=INCOMPATIBLE_COLUMNS,
            expected_substrings=("INCOMPATIBLE_COLUMNS", "n"),
            check_no_scheduled=False,
        )
    with And("the rejected attempt wrote nothing"):
        assert count_rows(table_name=destination_table) == 0, error(
            "expected an empty destination after a rejected export"
        )

    with When("I export the same partition with the opt-in"):
        export_partition_by_id(
            source_table=source_table,
            destination_table=destination_table,
            partition_id=partition_id,
            node=node,
            query_settings_sql=(
                " SETTINGS export_merge_tree_part_allow_lossy_cast = 1"
            ),
        )
    with Then("the proved single value survives the narrowing cast"):
        rows = select_rows(table_name=destination_table, columns="id, n", order_by="id")
        assert rows == "1\t500\n2\t500", error(f"got: {rows!r}")


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
def gate_decision_survives_concurrent_insert(self):
    """The gate runs once, synchronously, at scheduling time -- so a
    decision it already made must not be invalidated by rows that arrive
    afterwards.

    Source ``PARTITION BY toYYYYMM(dt)`` into destination
    ``PARTITION BY dt``: partition ``202403`` holds a single day, so the
    dynamic proof accepts it. Under a retryable failpoint (export stalls
    and retries with backoff) a second row from a **different day** is
    inserted into that same source partition, which is exactly the shape
    the gate rejects. The export must still complete against the part
    list frozen at registration, and the destination must still contain
    the single day the gate promised.
    """
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="toYYYYMM(dt)",
        dst_partition_by="dt",
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05')")

    _run_export_under_failpoint(
        self,
        source_table=source_table,
        destination_table=destination_table,
        partition_id="202403",
        node=node,
        mid_flight_action=lambda: insert_values(
            table_name=source_table, values="(2, '2024-03-20')"
        ),
    )

    with Then("destination must not silently include the mid-export insert"):
        dst_ids = select_rows(table_name=destination_table, columns="id", order_by="id")
        assert dst_ids == "1", error(
            f"expected only id=1 in destination (scheduler must freeze part-list "
            f"at registration), got ids={dst_ids!r}"
        )
    with And("the destination still holds the single day the gate proved"):
        dst_days = select_rows(
            table_name=destination_table, columns="DISTINCT dt", order_by="1"
        )
        assert dst_days == "2024-03-05", error(
            f"gate accepted 202403 as single-valued on dt, but the destination "
            f"ended up with days={dst_days!r}"
        )


@TestScenario
@Requirements(RQ_ClickHouse_ExportPartition_Restrictions_PartitionKey("2.0"))
def gate_decision_survives_concurrent_merge(self):
    """The dynamic proof folds min/max across the parts registered at
    scheduling time; those parts must keep being usable if a merge
    replaces them mid-flight.

    Source ``PARTITION BY toYYYYMM(dt)`` into destination
    ``PARTITION BY dt`` with two parts holding the same day (merges
    stopped), so the proof has to fold across both to accept. Under a
    retryable failpoint the merges are re-enabled and the two parts
    collapse into one while the export retries. The destination must
    match the source as it was at scheduling time.
    """
    node = self.context.node
    columns = [{"name": "id", "type": "Int64"}, {"name": "dt", "type": "Date"}]
    source_table, destination_table = setup_source_and_hive_destination(
        src_columns=columns,
        src_partition_by="toYYYYMM(dt)",
        dst_partition_by="dt",
        stop_merges=True,
    )
    insert_values(table_name=source_table, values="(1, '2024-03-05')")
    insert_values(table_name=source_table, values="(2, '2024-03-05')")

    with Given("the partition is spread over two active parts"):
        parts = count_rows(
            table_name="system.parts",
            where=(f"table = '{source_table}' AND partition_id = '202403' AND active"),
        )
        assert parts == 2, error(f"expected 2 active parts, got {parts}")

    def _merge_parts():
        node.query(f"SYSTEM START MERGES {source_table}")
        node.query(f"OPTIMIZE TABLE {source_table} FINAL")

    _run_export_under_failpoint(
        self,
        source_table=source_table,
        destination_table=destination_table,
        partition_id="202403",
        node=node,
        mid_flight_action=_merge_parts,
    )

    with Then("destination contains both original rows exactly once"):
        dst_rows = select_rows(
            table_name=destination_table, columns="id, dt", order_by="id"
        )
        assert dst_rows == "1\t2024-03-05\n2\t2024-03-05", error(f"got: {dst_rows!r}")


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
def gate_rejects(self):
    """Name-based gate corner cases and non-bare destination partition
    keys: case sensitivity, renamed payload columns, and algebraically-
    equivalent expressions."""
    Scenario(run=partition_key_case_sensitivity)
    Scenario(run=payload_column_name_mismatch)
    Scenario(run=algebraically_equivalent_partition_expression)


@TestSuite
def gate_and_schema_guard(self):
    """Where the payload schema guard and the partition-key gate meet:
    which check reports first when both fail, and what a cast on the
    destination partition column does to the dynamic proof."""
    Scenario(run=schema_guard_runs_before_the_gate)
    Scenario(run=widened_type_on_dynamically_proved_partition_column)
    Scenario(run=lossy_cast_on_dynamically_proved_partition_column)


@TestSuite
def data_integrity_round_trip(self):
    """End-to-end integrity of newly-accepted exports: destination
    partition layout follows the destination DDL rather than the source,
    and a timezone difference between the two sides preserves the
    instant."""
    Scenario(run=subset_round_trip)
    Scenario(run=reversed_multicolumn_partition_key_layout)
    Scenario(run=partition_key_timezone_drift)


@TestSuite
def positional_cast_hazards(self):
    """Name-based partition-key gate + positional payload CAST can
    silently corrupt data when schema positions disagree, on key pairs
    that only this feature accepts."""
    Scenario(run=swapped_same_type_columns_positional_cast)
    Scenario(run=swap_under_multi_part_and_export_all)


@TestSuite
def gate_decision_durability(self):
    """A gate decision is made once at scheduling time; concurrent
    INSERT / MERGE into the source partition must not invalidate it."""
    Scenario(run=gate_decision_survives_concurrent_insert)
    Scenario(run=gate_decision_survives_concurrent_merge)


@TestFeature
@Name("partition key compatibility")
def feature(self):
    """Partition-key compatibility gate for hive S3 exports
    (Altinity/ClickHouse#2074)."""
    Feature(run=oracle)
    Feature(run=gate_decisions)
    Feature(run=gate_rejects)
    Feature(run=gate_and_schema_guard)
    Feature(run=data_integrity_round_trip)
    Feature(run=positional_cast_hazards)
    Feature(run=gate_decision_durability)
