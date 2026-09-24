"""What of the CREATE TABLE definition reaches Iceberg, and the rejection
matrix for everything that cannot (plan §3.3)."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import *


# (partition expression, column definition, iceberg transform, one value, predicate)
ACCEPTED_TRANSFORMS = [
    (
        "i",
        "i Int64",
        "identity",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "i = 1",
    ),
    (
        "s",
        "s String",
        "identity",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "s = 'a'",
    ),
    (
        "d",
        "d Date",
        "identity",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "d = '2024-01-02'",
    ),
    (
        "toYearNumSinceEpoch(d)",
        "d Date",
        "year",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "d = '2024-01-02'",
    ),
    (
        "toMonthNumSinceEpoch(d)",
        "d Date",
        "month",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "d = '2024-01-02'",
    ),
    (
        "toRelativeDayNum(d)",
        "d Date",
        "day",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "d = '2024-01-02'",
    ),
    (
        "toYearNumSinceEpoch(t)",
        "t DateTime64(6)",
        "year",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "i = 1",
    ),
    (
        "toMonthNumSinceEpoch(t)",
        "t DateTime64(6)",
        "month",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "i = 1",
    ),
    (
        "toRelativeDayNum(t)",
        "t DateTime64(6)",
        "day",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "i = 1",
    ),
    (
        "toRelativeHourNum(t)",
        "t DateTime64(6)",
        "hour",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "i = 1",
    ),
    (
        "icebergTruncate(4, s)",
        "s String",
        "truncate[4]",
        "(1, 'abcdef', '2024-01-02', '2024-01-02 03:04:05')",
        "s = 'abcdef'",
    ),
    (
        "icebergTruncate(10, i)",
        "i Int64",
        "truncate[10]",
        "(17, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "i = 17",
    ),
    (
        "icebergBucket(8, i)",
        "i Int64",
        "bucket[8]",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "i = 1",
    ),
    (
        "icebergBucket(8, s)",
        "s String",
        "bucket[8]",
        "(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        "s = 'a'",
    ),
]

COLUMNS = ["i Int64", "s String", "d Date", "t DateTime64(6)"]


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy("1.0"))
def accepted_transforms(self):
    """Every accepted PARTITION BY expression registers the matching Iceberg
    transform, takes a row, answers a partition predicate, and writes the
    data file under a partition directory."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )

    for expression, _, transform, values, predicate in ACCEPTED_TRANSFORMS:
        with Check(f"PARTITION BY {expression}", flags=TE):
            namespace = f"ns_{getuid()}"  # own namespace per table: a CREATE into an existing namespace costs ~33 s (findings.md #3)
            table_name = f"t_{getuid()}"
            ch_name = clickhouse_table_name(database_name, namespace, table_name)
            args = dict(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                database_name=database_name,
            )

            with When("CREATE TABLE"):
                create_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                    columns=COLUMNS,
                    partition_by=expression,
                )

            with Then("PyIceberg spec carries the transform"):
                table = catalog.load_table(f"{namespace}.{table_name}")
                transforms = [str(f.transform) for f in table.spec().fields]
                assert transforms == [transform], error(
                    f"{transforms} != [{transform}]"
                )

            with When("INSERT one row and SELECT it with a partition predicate"):
                insert_into_native_iceberg_table(table_name=ch_name, values_sql=values)
                got = self.context.node.query(
                    f"SELECT count() FROM {ch_name} WHERE {predicate}"
                ).output.strip()
                assert got == "1", error(got)

            with And("state invariants"):
                state = snapshot_state(**args)
                check_state_invariants(**args, expected=PRESENT, state=state)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy("1.0"))
def partition_values_in_manifest(self):
    """The partition value of a written data file is recorded in its manifest
    entry, which an external reader (PyIceberg `plan_files`) sees. Iceberg
    prescribes no directory layout; ClickHouse writes flat
    `data/data-<uuid>.parquet` paths, so the manifest is the only oracle.

    Needs a manifest list an external reader can parse; see findings.md
    finding 5 (missing Avro field-ids, upstream ClickHouse#111786)."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    ch_name = clickhouse_table_name(database_name, namespace, table_name)
    with When("create an identity-partitioned table and insert one row"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
            partition_by="i",
        )
        insert_into_native_iceberg_table(
            table_name=ch_name,
            values_sql="(1, 'a', '2024-01-02', '2024-01-02 03:04:05')",
        )
    with Then("the manifest entry carries the partition value"):
        files = list(
            catalog.load_table(f"{namespace}.{table_name}").scan().plan_files()
        )
        assert files, error("no data files after INSERT")
        for task in files:
            record = task.file.partition
            assert len(record) == 1 and record[0] == 1, error(
                f"data file {task.file.file_path} has partition {record}"
            )


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy("1.0"))
def composite_partition(self):
    """PARTITION BY (identity, bucket) registers two spec fields."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"

    with When("CREATE TABLE with a composite key"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
            partition_by="(d, icebergBucket(4, i))",
        )

    with Then("both transforms are registered in order"):
        table = catalog.load_table(f"{namespace}.{table_name}")
        assert pyiceberg_spec_shape(table) == [
            (3, "identity"),
            (1, "bucket[4]"),
        ], error(str(table.spec()))


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy("1.0"))
def no_partition_by(self):
    """Without PARTITION BY the spec is empty."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        columns=COLUMNS,
    )
    table = catalog.load_table(f"{namespace}.{table_name}")
    assert pyiceberg_spec_shape(table) == [], error(str(table.spec()))


@TestOutline(Scenario)
@Requirements(
    RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy_RejectedExpressions("1.0"),
    RQ_Iceberg_NativeCreateDrop_FailedCreateLeavesNoTrace("1.0"),
)
@Examples(
    "expression",
    [
        ("toYYYYMM(d)",),
        ("intDiv(i, 10)",),
        ("i % 7",),
        ("cityHash64(s)",),
        ("toStartOfMonth(d)",),
        ("(i, toYYYYMM(d))",),
    ],
)
def rejected_partition_expressions(self, expression):
    """A PARTITION BY expression Iceberg cannot express is BAD_ARGUMENTS and
    leaves no table, no namespace and no object behind."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    for path in (ENGINE_LESS, EXPLICIT_ENGINE):
        with Check(path, flags=TE):
            with By("snapshot state"):
                before = snapshot_state(**args)
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                path=path,
                columns=COLUMNS,
                partition_by=expression,
                exitcode=BAD_ARGUMENTS,
                message="iceberg partitioning",
            )
            with By("snapshot state"):
                after = snapshot_state(**args)
            assert_rejected_no_trace(
                before=before, after=after, namespace_expected=False
            )


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy_TransformParameters("1.0"))
def non_positive_transform_parameters(self):
    """D5: icebergBucket / icebergTruncate with N <= 0 are rejected before
    anything is written."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace = f"ns_{getuid()}"

    for function, column in (("icebergBucket", "i"), ("icebergTruncate", "s")):
        for n in (0, -1):
            with Check(f"{function}({n}, {column})", flags=TE):
                table_name = f"t_{getuid()}"
                args = dict(
                    catalog=catalog,
                    namespace=namespace,
                    table_name=table_name,
                    database_name=database_name,
                )
                with By("snapshot state"):
                    before = snapshot_state(**args)
                create_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                    columns=COLUMNS,
                    partition_by=f"{function}({n}, {column})",
                    exitcode=BAD_ARGUMENTS,
                    message="requires a positive",
                )
                with By("snapshot state"):
                    after = snapshot_state(**args)
                assert_rejected_no_trace(
                    before=before, after=after, namespace_expected=False
                )


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_OrderBy("1.0"))
@Examples(
    "order_by expected",
    [
        (None, []),
        ("i", [(1, "identity")]),
        ("(i, s)", [(1, "identity"), (2, "identity")]),
    ],
)
def order_by(self, order_by, expected):
    """ORDER BY becomes the sort order; a non-empty one has a non-zero id."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        columns=COLUMNS,
        order_by=order_by,
    )
    table = catalog.load_table(f"{namespace}.{table_name}")
    assert pyiceberg_sort_shape(table) == expected, error(str(table.sort_order()))
    if expected:
        assert table.sort_order().order_id != 0, error(
            "non-empty sort order has order-id 0"
        )
    else:
        assert table.sort_order().order_id == 0, error(
            "empty sort order should be unsorted (id 0)"
        )


STORAGE_CLAUSES = {
    "PRIMARY KEY": "PRIMARY KEY i",
    "SAMPLE BY": "SAMPLE BY i",
    "TTL": "TTL d + INTERVAL 1 DAY",
    "engine SETTINGS": None,  # passed as engine_settings
}


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_UnsupportedStorageClauses("1.0"))
def unsupported_storage_clauses(self):
    """C3: PRIMARY KEY, SAMPLE BY, TTL and engine SETTINGS are rejected with
    BAD_ARGUMENTS on every path (SETTINGS only where no engine is given)."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace = f"ns_{getuid()}"
    with Given("source table"):
        source = mergetree_source_table(columns=COLUMNS, order_by="i")

    for path in CREATE_PATHS:
        for clause, text in STORAGE_CLAUSES.items():
            if clause == "engine SETTINGS" and path == EXPLICIT_ENGINE:
                continue
            with Check(f"{path} / {clause}", flags=TE):
                table_name = f"t_{getuid()}"
                args = dict(
                    catalog=catalog,
                    namespace=namespace,
                    table_name=table_name,
                    database_name=database_name,
                )
                with By("snapshot state"):
                    before = snapshot_state(**args)
                create_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                    path=path,
                    columns=None if path == AS_SOURCE else COLUMNS,
                    source=source if path == AS_SOURCE else None,
                    order_by="i" if clause in ("PRIMARY KEY", "SAMPLE BY") else None,
                    storage_clauses=text,
                    engine_settings=(
                        {"index_granularity": 8192}
                        if clause == "engine SETTINGS"
                        else None
                    ),
                    exitcode=BAD_ARGUMENTS,
                    message="DataLakeCatalog CREATE TABLE",
                )
                with By("snapshot state"):
                    after = snapshot_state(**args)
                assert_rejected_no_trace(before=before, after=after)


COLUMN_MODIFIERS = {
    "DEFAULT": "i Int64 DEFAULT 1",
    "MATERIALIZED": "i Int64 MATERIALIZED 1",
    "ALIAS": "i Int64 ALIAS s",
    "EPHEMERAL": "i Int64 EPHEMERAL",
    "COMMENT": "i Int64 COMMENT 'c'",
    "CODEC": "i Int64 CODEC(ZSTD)",
    "TTL": "i Int64 TTL d + INTERVAL 1 DAY",
    "STATISTICS": "i Int64 STATISTICS(tdigest)",
    "SETTINGS": "i Int64 SETTINGS (min_compress_block_size = 1)",
    "PRIMARY KEY": "i Int64 PRIMARY KEY",
}


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_UnsupportedColumnModifiers("1.0"))
def unsupported_column_modifiers(self):
    """C3: every column modifier Iceberg cannot store is rejected naming the
    column, whether written on the statement or inherited from an AS source."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace = f"ns_{getuid()}"

    for path in CREATE_PATHS:
        for modifier, definition in COLUMN_MODIFIERS.items():
            with Check(f"{path} / {modifier}", flags=TE):
                columns = [definition, "s String", "d Date"]
                source = None
                if path == AS_SOURCE:
                    if modifier == "PRIMARY KEY":
                        skip(
                            "column-level PRIMARY KEY is not a column property after creation"
                        )
                    with By("source table"):
                        source = mergetree_source_table(
                            columns=columns,
                            order_by="tuple()",
                            query_settings=(
                                [("allow_experimental_statistics", 1)]
                                if modifier == "STATISTICS"
                                else None
                            ),
                        )
                table_name = f"t_{getuid()}"
                args = dict(
                    catalog=catalog,
                    namespace=namespace,
                    table_name=table_name,
                    database_name=database_name,
                )
                with By("snapshot state"):
                    before = snapshot_state(**args)
                create_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                    path=path,
                    columns=None if path == AS_SOURCE else columns,
                    source=source,
                    settings=(
                        [("allow_experimental_statistics", 1)]
                        if modifier == "STATISTICS"
                        else None
                    ),
                    exitcode=BAD_ARGUMENTS,
                    message=(
                        "Column 'i'" if modifier != "PRIMARY KEY" else "PRIMARY KEY"
                    ),
                )
                with By("snapshot state"):
                    after = snapshot_state(**args)
                assert_rejected_no_trace(before=before, after=after)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_UnsupportedTableElements("1.0"))
def unsupported_table_elements(self):
    """C3: indices, constraints, projections, a table-level PRIMARY KEY in
    the column list, and a table COMMENT are rejected."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace = f"ns_{getuid()}"
    cases = {
        "INDEX": dict(table_elements=["INDEX idx i TYPE minmax GRANULARITY 1"]),
        "CONSTRAINT": dict(table_elements=["CONSTRAINT c CHECK i > 0"]),
        "PROJECTION": dict(table_elements=["PROJECTION p (SELECT i ORDER BY i)"]),
        "PRIMARY KEY in column list": dict(table_elements=["PRIMARY KEY i"]),
        "table COMMENT": dict(comment="a comment"),
    }
    for path in (ENGINE_LESS, EXPLICIT_ENGINE):
        for name, extra in cases.items():
            with Check(f"{path} / {name}", flags=TE):
                table_name = f"t_{getuid()}"
                args = dict(
                    catalog=catalog,
                    namespace=namespace,
                    table_name=table_name,
                    database_name=database_name,
                )
                with By("snapshot state"):
                    before = snapshot_state(**args)
                create_table(
                    database_name=database_name,
                    namespace=namespace,
                    table_name=table_name,
                    path=path,
                    columns=COLUMNS,
                    exitcode=BAD_ARGUMENTS,
                    message="not support",  # "does not support ... indices, constraints, or projections"
                    **extra,
                )
                with By("snapshot state"):
                    after = snapshot_state(**args)
                assert_rejected_no_trace(before=before, after=after)

    with Check("AS source carrying a comment", flags=TE):
        with By("source table"):
            source = mergetree_source_table(
                columns=COLUMNS, order_by="i", comment="src comment"
            )
        table_name = f"t_{getuid()}"
        args = dict(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            database_name=database_name,
        )
        with By("snapshot state"):
            before = snapshot_state(**args)
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=AS_SOURCE,
            source=source,
            exitcode=BAD_ARGUMENTS,
            message="COMMENT is not supported",
        )
        with By("snapshot state"):
            after = snapshot_state(**args)
        assert_rejected_no_trace(before=before, after=after)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_NonTableObjects("1.0"))
def non_table_objects(self):
    """Views, dictionaries, ATTACH, CLONE AS and REPLACE forms are
    NOT_IMPLEMENTED and register nothing."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    node = self.context.node
    namespace = f"ns_{getuid()}"
    with Given("source table"):
        source = mergetree_source_table(columns=COLUMNS, order_by="i")
    name = lambda t: clickhouse_table_name(database_name, namespace, t)

    statements = {
        "CREATE VIEW": lambda t: f"CREATE VIEW {name(t)} AS SELECT 1 AS i",
        "CREATE MATERIALIZED VIEW": lambda t: f"CREATE MATERIALIZED VIEW {name(t)} ENGINE = MergeTree ORDER BY i AS SELECT i FROM {source}",
        "CREATE DICTIONARY": lambda t: (
            f"CREATE DICTIONARY {name(t)} (i Int64, s String) PRIMARY KEY i "
            f"SOURCE(CLICKHOUSE(TABLE '{source.split('.')[1]}')) LAYOUT(FLAT()) LIFETIME(0)"
        ),
        "ATTACH TABLE": lambda t: f"ATTACH TABLE {name(t)} (i Int64) ENGINE = MergeTree ORDER BY i",
        "CLONE AS": lambda t: f"CREATE TABLE {name(t)} CLONE AS {source}",
        "CREATE OR REPLACE TABLE": lambda t: f"CREATE OR REPLACE TABLE {name(t)} (i Int64)",
        "REPLACE TABLE": lambda t: f"REPLACE TABLE {name(t)} (i Int64)",
    }
    for label, build in statements.items():
        with Check(label, flags=TE):
            table_name = f"t_{getuid()}"
            args = dict(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                database_name=database_name,
            )
            with By("snapshot state"):
                before = snapshot_state(**args)
            node.query(
                build(table_name),
                exitcode=NOT_IMPLEMENTED,
                message="DataLakeCatalog supports only plain CREATE TABLE",
                ignore_exception=True,
            )
            with By("snapshot state"):
                after = snapshot_state(**args)
            assert_rejected_no_trace(before=before, after=after)


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_Schema_EngineSettings("1.0"))
@Examples("format_version", [(1,), (2,)])
def engine_settings_with_explicit_engine(self, format_version):
    """Positive control: with an explicit engine, SETTINGS are the engine's
    storage settings and iceberg_format_version reaches the metadata."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        path=EXPLICIT_ENGINE,
        columns=COLUMNS,
        engine_settings={"iceberg_format_version": format_version},
    )
    with When("read registered metadata"):
        metadata, _ = read_registered_metadata(
            catalog=catalog, namespace=namespace, table_name=table_name
        )
    assert metadata["format-version"] == format_version, error(
        metadata["format-version"]
    )


@TestFeature
@Name("schema")
def feature(self, minio_root_user, minio_root_password):
    """PARTITION BY / ORDER BY translation and the rejection matrix."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
