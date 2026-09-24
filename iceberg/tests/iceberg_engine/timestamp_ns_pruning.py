"""Nanosecond Iceberg timestamp pruning and DateTime64(9) writes.

Altinity/ClickHouse#2239. Three failures:

* Identity partition values for ``timestamp_ns`` arrive as Avro longs.
  Comparing them to a ``DateTime64(9)`` predicate without wrapping the
  scale drops the matching file.
* Some writers store nanosecond min/max bytes on Iceberg ``timestamp``
  (``DateTime64(6)``). Reading those bytes as microseconds looks like
  year 2299, so every file is pruned.
* ClickHouse used to write ``DateTime64(9)`` as ``timestamp`` while
  dumping unscaled nanosecond bounds, which recreates that layout.
  ``timestamp_ns`` is format version 3 only.
"""

from testflows.core import *
from testflows.asserts import error

from helpers.common import (
    check_clickhouse_version,
    check_if_antalya_build,
    getuid,
)

import iceberg.tests.steps.metrics as metrics
import iceberg.tests.steps.s3_objects as s3
from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_s3_destination,
)
from iceberg.tests.iceberg_engine.timestamp_ns_tables import (
    DATETIME64_MAX_US,
    ROWS,
    SPARK_TIMESTAMP_SENTINEL_US,
    clickhouse_url,
    patch_long_columns_to_timestamp_ns,
    patch_timestamp_bounds_us_to_ns,
    patch_timestamp_upper_bound,
    write_microsecond_timestamp_table,
    write_nanosecond_long_table,
)
from iceberg.tests.steps.iceberg_writes import ICEBERG_INSERT_SETTINGS


BAD_ARGUMENTS = 36


def _credentials(test):
    return test.context.minio_root_user, test.context.minio_root_password


def _literal(kind, ts_ns, utc, scale=9, timezone="UTC"):
    if kind == "fromUnixTimestamp64Nano":
        return f"fromUnixTimestamp64Nano({ts_ns})"
    whole, frac = utc.split(".")
    frac = (frac[:scale]).ljust(scale, "0")
    value = f"{whole}.{frac}" if scale else whole
    if timezone is None:
        return f"toDateTime64('{value}', {scale})"
    return f"toDateTime64('{value}', {scale}, '{timezone}')"


def _select(node, sql, pruning):
    log_comment = f"tsns_{getuid()}"
    result = node.query(
        sql,
        settings=[
            ("session_timezone", "UTC"),
            ("use_iceberg_partition_pruning", "1" if pruning else "0"),
            ("input_format_parquet_filter_push_down", "0"),
            ("input_format_parquet_bloom_filter_push_down", "0"),
            ("use_iceberg_metadata_files_cache", "0"),
            ("use_cache_for_count_from_files", "0"),
            ("log_comment", log_comment),
        ],
    )
    return result, log_comment


def _pruned(node, sql, event):
    result, log_comment = _select(node, sql, pruning=True)
    if event == "IcebergPartitionPrunedFiles":
        metric = metrics.get_IcebergPartitionPrunedFiles(log_comment=log_comment)
    else:
        metric = metrics.get_IcebergMinMaxIndexPrunedFiles(log_comment=log_comment)
    raw = metric.output.strip().splitlines()
    count = int(raw[0]) if raw and raw[0] else 0
    return result, count


def _ids(node, sql):
    result, _log_comment = _select(node, sql, pruning=False)
    return result.output.strip()


def _assert_ns_pruning(node, source, column, event, literal):
    """Equality and range predicates on one file per nanosecond row."""
    off = _ids(
        node,
        f"SELECT id, toUnixTimestamp64Nano(ts), toUnixTimestamp64Nano(value) "
        f"FROM {source} ORDER BY id",
    )
    expected = "\n".join(f"{row_id}\t{ts_ns}\t{ts_ns}" for ts_ns, row_id, _utc in ROWS)
    assert off == expected, error(off)

    eq_ns, eq_id, eq_utc = ROWS[1]
    eq_lit = _literal(literal, eq_ns, eq_utc)
    eq_sql = f"SELECT id FROM {source} WHERE {column} = {eq_lit} ORDER BY id"
    eq_result, eq_pruned = _pruned(node, eq_sql, event)
    assert eq_pruned == 3, error(eq_pruned)
    assert eq_result.output.strip() == str(eq_id), error(eq_result.output)

    le_ns, _le_id, le_utc = ROWS[1]
    le_lit = _literal(literal, le_ns, le_utc)
    le_sql = f"SELECT id FROM {source} WHERE {column} <= {le_lit} ORDER BY id"
    le_result, le_pruned = _pruned(node, le_sql, event)
    assert le_pruned == 2, error(le_pruned)
    assert le_result.output.strip() == "1\n2", error(le_result.output)

    ge_ns, _ge_id, ge_utc = ROWS[2]
    ge_lit = _literal(literal, ge_ns, ge_utc)
    ge_sql = f"SELECT id FROM {source} WHERE {column} >= {ge_lit} ORDER BY id"
    ge_result, ge_pruned = _pruned(node, ge_sql, event)
    assert ge_pruned == 2, error(ge_pruned)
    assert ge_result.output.strip() == "3\n4", error(ge_result.output)


def _iceberg_s3(location):
    user = current().context.minio_root_user
    password = current().context.minio_root_password
    return f"icebergS3('{clickhouse_url(location)}', '{user}', '{password}')"


def _create_s3_table(
    columns, user, password, format_version=None, partition_by=""
):
    extra = []
    if format_version is not None:
        extra.append(f"iceberg_format_version = {format_version}")
    return create_iceberg_s3_destination(
        columns=columns,
        partition_by=partition_by,
        minio_root_user=user,
        minio_root_password=password,
        extra_settings=extra,
    )


def _insert_ns_rows(node, table_name):
    for ts_ns, row_id, _utc in ROWS:
        node.query(
            f"INSERT INTO {table_name} VALUES "
            f"(fromUnixTimestamp64Nano({ts_ns}), fromUnixTimestamp64Nano({ts_ns}), {row_id})",
            settings=ICEBERG_INSERT_SETTINGS,
        )


def _field_types(table_name):
    keys = [
        key
        for key in s3.list_keys(f"data/{table_name}/metadata/")
        if key.endswith(".metadata.json")
    ]
    assert keys, error(table_name)

    def version(key):
        head = key.rsplit("/", 1)[-1].split("-", 1)[0].split(".", 1)[0].lstrip("v")
        try:
            return int(head)
        except ValueError:
            return -1

    meta = s3.read_json_object(max(keys, key=version))
    found = []

    def walk(obj):
        if isinstance(obj, dict):
            if isinstance(obj.get("type"), str) and "name" in obj:
                found.append((obj["name"], obj["type"]))
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)

    walk(meta)
    return meta, found


def _assert_written_type(table_name, iceberg_type, describe_needle):
    node = current().context.node
    describe = node.query(f"DESCRIBE TABLE {table_name}").output
    assert describe_needle in describe, error(describe)
    assert "DateTime64(6" not in describe, error(describe)
    meta, types = _field_types(table_name)
    assert int(meta.get("format-version")) == 3, error(meta.get("format-version"))
    assert any(type_name == iceberg_type for _name, type_name in types), error(types)


@TestOutline(Scenario)
@Examples(
    "literal",
    [
        ("fromUnixTimestamp64Nano",),
        ("toDateTime64",),
    ],
)
def identity_partition_pruning_timestamp_ns(
    self, literal
):
    """Identity pruning on ``timestamp_ns`` keeps the matching partition."""
    minio_root_user, minio_root_password = _credentials(self)
    node = self.context.node
    with Given("one file per nanosecond, partitioned by identity"):
        location = write_nanosecond_long_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            partitioned=True,
        )
    with And("declare the longs as timestamp_ns"):
        patch_long_columns_to_timestamp_ns(location)
    with Then("equality and range predicates prune only other partitions"):
        _assert_ns_pruning(
            node,
            _iceberg_s3(location),
            "ts",
            "IcebergPartitionPrunedFiles",
            literal,
        )


@TestOutline(Scenario)
@Examples(
    "literal",
    [
        ("fromUnixTimestamp64Nano",),
        ("toDateTime64",),
    ],
)
def minmax_pruning_timestamp_ns(self, literal):
    minio_root_user, minio_root_password = _credentials(self)
    """Min/max pruning on ``timestamp_ns`` keeps the matching file."""
    node = self.context.node
    with Given("one unpartitioned file per nanosecond"):
        location = write_nanosecond_long_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            partitioned=False,
        )
    with And("declare the longs as timestamp_ns"):
        patch_long_columns_to_timestamp_ns(location)
    with Then("equality and range predicates prune only other files"):
        _assert_ns_pruning(
            node,
            _iceberg_s3(location),
            "value",
            "IcebergMinMaxIndexPrunedFiles",
            literal,
        )


@TestOutline(Scenario)
@Examples("timezone", [("none",), ("UTC",)])
def minmax_pruning_datetime64_6_predicate_on_timestamp_ns(
    self, timezone
):
    """A ``DateTime64(6)`` predicate against ``timestamp_ns`` keeps overlapping files."""
    minio_root_user, minio_root_password = _credentials(self)
    if timezone == "none":
        timezone = None
    node = self.context.node
    with Given("one unpartitioned file per nanosecond"):
        location = write_nanosecond_long_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            partitioned=False,
        )
    with And("declare the longs as timestamp_ns"):
        patch_long_columns_to_timestamp_ns(location)

    source = _iceberg_s3(location)
    with Then("truncating row 2 to microseconds excludes that row"):
        # Row 2 is 1 nanosecond past the microsecond boundary.
        before = _literal(
            "toDateTime64",
            ROWS[1][0],
            ROWS[1][2],
            scale=6,
            timezone=timezone,
        )
        sql = f"SELECT id FROM {source} WHERE value <= {before} ORDER BY id"
        result, pruned = _pruned(node, sql, "IcebergMinMaxIndexPrunedFiles")
        assert pruned == 3, error(pruned)
        assert result.output.strip() == "1", error(result.output)

    with And("one microsecond later includes rows 1 and 2"):
        after = _literal(
            "toDateTime64",
            ROWS[1][0],
            "2024-03-15 12:00:00.000001000",
            scale=6,
            timezone=timezone,
        )
        sql = f"SELECT id FROM {source} WHERE value <= {after} ORDER BY id"
        result, pruned = _pruned(node, sql, "IcebergMinMaxIndexPrunedFiles")
        assert pruned == 2, error(pruned)
        assert result.output.strip() == "1\n2", error(result.output)

    with And("a scale-6 bound at row 3 keeps rows 3 and 4"):
        ge = _literal(
            "toDateTime64",
            ROWS[2][0],
            ROWS[2][2],
            scale=6,
            timezone=timezone,
        )
        sql = f"SELECT id FROM {source} WHERE value >= {ge} ORDER BY id"
        result, pruned = _pruned(node, sql, "IcebergMinMaxIndexPrunedFiles")
        assert pruned == 2, error(pruned)
        assert result.output.strip() == "3\n4", error(result.output)


@TestScenario
def minmax_pruning_nanosecond_bounds_on_timestamp(
    self
):
    """Iceberg ``timestamp`` with nanosecond min/max bytes must not drop the file.

    Same predicate shape as the customer query:
    ``WHERE col <= toDateTime64('...', 6)``.
    """
    minio_root_user, minio_root_password = _credentials(self)
    node = self.context.node
    with Given("one microsecond timestamp file"):
        location = write_microsecond_timestamp_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    with And("store the file bounds as nanoseconds"):
        patch_timestamp_bounds_us_to_ns(location)

    source = _iceberg_s3(location)
    with Then("ClickHouse reads the column as DateTime64(6)"):
        type_name = _ids(node, f"SELECT toTypeName(value) FROM {source} LIMIT 1")
        assert "DateTime64(6" in type_name, error(type_name)
        assert "DateTime64(9" not in type_name, error(type_name)
        micros = _ids(
            node,
            f"SELECT toUnixTimestamp64Micro(value) FROM {source} WHERE id = 1",
        )
        assert micros == "1704067200123456", error(micros)

    with And("the 2024 predicate keeps the file and rows 1 and 2"):
        predicate = _literal(
            "toDateTime64",
            ROWS[1][0],
            "2024-03-15 12:00:00.000001000",
            scale=6,
            timezone=None,
        )
        sql = f"SELECT id FROM {source} WHERE value <= {predicate} ORDER BY id"
        result, pruned = _pruned(node, sql, "IcebergMinMaxIndexPrunedFiles")
        assert pruned == 0, error(pruned)
        assert result.output.strip() == "1\n2", error(result.output)
        count_sql = f"SELECT count() FROM {source} WHERE value <= {predicate}"
        count, count_pruned = _pruned(
            node, count_sql, "IcebergMinMaxIndexPrunedFiles"
        )
        assert count_pruned == 0, error(count_pruned)
        assert count.output.strip() == "2", error(count.output)


@TestOutline(Scenario)
@Examples(
    "upper_bound_us",
    [
        (SPARK_TIMESTAMP_SENTINEL_US,),
        (DATETIME64_MAX_US,),
    ],
)
def minmax_pruning_far_future_microsecond_upper_bound(
    self, upper_bound_us
):
    """A far-future microsecond upper bound must not be read as nanoseconds.

    Spark's ``9999-12-31`` and ClickHouse's ``2299-12-31`` sit between 1e16
    and 1e18. Dividing them by 1000 makes the file range miss 2024.
    """
    minio_root_user, minio_root_password = _credentials(self)
    node = self.context.node
    with Given("one microsecond timestamp file"):
        location = write_microsecond_timestamp_table(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
    with And(f"set the upper bound to {upper_bound_us} microseconds"):
        patch_timestamp_upper_bound(location, upper_bound_us)

    source = _iceberg_s3(location)
    with Then("the 2024 predicate still returns rows 1 and 2"):
        predicate = _literal(
            "toDateTime64",
            ROWS[1][0],
            "2024-03-15 12:00:00.000001000",
            scale=6,
            timezone=None,
        )
        sql = f"SELECT id FROM {source} WHERE value <= {predicate} ORDER BY id"
        result, pruned = _pruned(node, sql, "IcebergMinMaxIndexPrunedFiles")
        assert pruned == 0, error(pruned)
        assert result.output.strip() == "1\n2", error(result.output)


@TestOutline(Scenario)
@Examples(
    "literal",
    [
        ("fromUnixTimestamp64Nano",),
        ("toDateTime64",),
    ],
)
def writes_minmax_pruning_datetime64_9(
    self, literal
):
    """ClickHouse writes ``DateTime64(9)`` as ``timestamp_ns`` on format version 3."""
    minio_root_user, minio_root_password = _credentials(self)
    node = self.context.node
    with Given("an unpartitioned Iceberg v3 table"):
        table_name = _create_s3_table(
            "ts DateTime64(9), value DateTime64(9), id Int32",
            minio_root_user,
            minio_root_password,
            format_version=3,
        )
    with And("insert one file per nanosecond row"):
        _assert_written_type(table_name, "timestamp_ns", "DateTime64(9)")
        _insert_ns_rows(node, table_name)
    with Then("min/max pruning keeps the matching file"):
        _assert_ns_pruning(
            node,
            table_name,
            "value",
            "IcebergMinMaxIndexPrunedFiles",
            literal,
        )


@TestOutline(Scenario)
@Examples(
    "literal",
    [
        ("fromUnixTimestamp64Nano",),
        ("toDateTime64",),
    ],
)
def writes_identity_partition_pruning_datetime64_9(
    self, literal
):
    """Identity pruning works on a ``timestamp_ns`` column ClickHouse wrote."""
    minio_root_user, minio_root_password = _credentials(self)
    node = self.context.node
    with Given("an Iceberg v3 table partitioned by ts"):
        table_name = _create_s3_table(
            "ts DateTime64(9), value DateTime64(9), id Int32",
            minio_root_user,
            minio_root_password,
            format_version=3,
            partition_by="ts",
        )
    with And("insert one partition per nanosecond row"):
        _assert_written_type(table_name, "timestamp_ns", "DateTime64(9)")
        _insert_ns_rows(node, table_name)
    with Then("identity pruning keeps the matching partition"):
        _assert_ns_pruning(
            node,
            table_name,
            "ts",
            "IcebergPartitionPrunedFiles",
            literal,
        )


@TestScenario
def writes_datetime64_9_with_timezone(self):
    """``DateTime64(9, 'UTC')`` is stored as ``timestamptz_ns``."""
    minio_root_user, minio_root_password = _credentials(self)
    node = self.context.node
    with Given("an Iceberg v3 table with an explicit UTC timezone"):
        table_name = _create_s3_table(
            "ts DateTime64(9, 'UTC'), id Int32",
            minio_root_user,
            minio_root_password,
            format_version=3,
        )
    with Then("the written field is timestamptz_ns and the row round-trips"):
        _assert_written_type(table_name, "timestamptz_ns", "UTC")
        node.query(
            f"INSERT INTO {table_name} VALUES "
            f"(fromUnixTimestamp64Nano({ROWS[0][0]}), 1)",
            settings=ICEBERG_INSERT_SETTINGS,
        )
        result = node.query(f"SELECT id FROM {table_name}")
        assert result.output.strip() == "1", error(result.output)


def _reject_datetime64_9(node, sql):
    node.query(
        sql,
        exitcode=BAD_ARGUMENTS,
        message="DB::Exception: Iceberg type",
    )


@TestOutline(Scenario)
@Examples(
    "format_version columns",
    [
        (version, columns)
        for version in (1, 2)
        for columns in (
            "ts DateTime64(9), id Int32",
            "ts DateTime64(9, 'UTC'), id Int32",
            "ts Array(DateTime64(9)), id Int32",
        )
    ],
)
def writes_datetime64_9_rejected_below_v3(
    self, format_version, columns
):
    """Format versions 1 and 2 must not accept ``DateTime64(9)``."""
    minio_root_user, minio_root_password = _credentials(self)
    node = self.context.node
    table_name = f"tsns_{getuid()}"
    url = f"http://minio:9000/warehouse/data/{table_name}/"
    sql = (
        f"CREATE TABLE {table_name} ({columns}) "
        f"ENGINE = IcebergS3('{url}', '{minio_root_user}', '{minio_root_password}') "
        f"SETTINGS s3_retry_attempts = 1, iceberg_format_version = {format_version}"
    )
    with Then(f"CREATE on format version {format_version} raises BAD_ARGUMENTS"):
        _reject_datetime64_9(node, sql)


@TestScenario
def writes_datetime64_9_rejected_on_default_format_version(
    self
):
    """CREATE without ``iceberg_format_version`` uses version 2 and rejects ``DateTime64(9)``."""
    minio_root_user, minio_root_password = _credentials(self)
    node = self.context.node
    table_name = f"tsns_{getuid()}"
    url = f"http://minio:9000/warehouse/data/{table_name}/"
    sql = (
        f"CREATE TABLE {table_name} (ts DateTime64(9), id Int32) "
        f"ENGINE = IcebergS3('{url}', '{minio_root_user}', '{minio_root_password}') "
        f"SETTINGS s3_retry_attempts = 1"
    )
    with Then("CREATE raises BAD_ARGUMENTS"):
        _reject_datetime64_9(node, sql)


@TestScenario
def writes_alter_datetime64_9_rejected_on_v2(
    self
):
    """ALTER ADD and MODIFY must not write ``timestamp_ns`` into a v2 table."""
    minio_root_user, minio_root_password = _credentials(self)
    node = self.context.node
    with Given("a v2 table of DateTime64(6)"):
        table_name = _create_s3_table(
            "ts DateTime64(6), id Int32",
            minio_root_user,
            minio_root_password,
            format_version=2,
        )
    with Then("ADD COLUMN DateTime64(9) is rejected"):
        node.query(
            f"ALTER TABLE {table_name} ADD COLUMN ts_ns Nullable(DateTime64(9))",
            settings=ICEBERG_INSERT_SETTINGS,
            exitcode=BAD_ARGUMENTS,
            message="DB::Exception: Iceberg type",
        )
    with And("MODIFY COLUMN to DateTime64(9) is rejected"):
        node.query(
            f"ALTER TABLE {table_name} MODIFY COLUMN ts DateTime64(9)",
            settings=ICEBERG_INSERT_SETTINGS,
            exitcode=BAD_ARGUMENTS,
            message="DB::Exception: Iceberg type",
        )
    with And("the column stays DateTime64(6)"):
        describe = node.query(f"DESCRIBE TABLE {table_name}").output
        assert "DateTime64(6)" in describe, error(describe)
        assert "DateTime64(9" not in describe, error(describe)


@TestScenario
def writes_alter_datetime64_9_allowed_on_v3(
    self
):
    """ALTER ADD ``Nullable(DateTime64(9))`` is valid on format version 3."""
    minio_root_user, minio_root_password = _credentials(self)
    node = self.context.node
    with Given("a v3 table"):
        table_name = _create_s3_table(
            "id Int32",
            minio_root_user,
            minio_root_password,
            format_version=3,
        )
    with When("add a nanosecond timestamp column"):
        node.query(
            f"ALTER TABLE {table_name} ADD COLUMN ts_ns Nullable(DateTime64(9))",
            settings=ICEBERG_INSERT_SETTINGS,
        )
    with Then("the column is DateTime64(9) and accepts a row"):
        describe = node.query(f"DESCRIBE TABLE {table_name}").output
        assert "DateTime64(9" in describe, error(describe)
        node.query(
            f"INSERT INTO {table_name} VALUES (1, fromUnixTimestamp64Nano({ROWS[0][0]}))",
            settings=ICEBERG_INSERT_SETTINGS,
        )
        result = node.query(f"SELECT id FROM {table_name}")
        assert result.output.strip() == "1", error(result.output)


@TestFeature
@Name("timestamp nanosecond pruning")
def feature(self, minio_root_user, minio_root_password):
    """Pruning and writes for Iceberg nanosecond timestamps (Altinity/ClickHouse#2239)."""
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password

    if not (check_if_antalya_build(self) and check_clickhouse_version(">=26.6")(self)):
        skip(
            "nanosecond Iceberg timestamp pruning needs an Antalya build >= 26.6 "
            "(Altinity/ClickHouse#2239)"
        )

    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
