"""ALTER TABLE ... DROP PARTITION for Iceberg.

Covers RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.DropPartition.
Runs on the REST catalog and on Glue. The suite skips this feature until
the statement is in a released build; see ``ffails`` in ``iceberg/regression.py``.
"""

import copy
import gzip
import io
import json
from datetime import date, datetime

import fastavro
import pyarrow as pa
import pyarrow.parquet as pq
from pyiceberg.partitioning import PartitionField, PartitionSpec
from pyiceberg.schema import Schema, NestedField
from pyiceberg.table.sorting import SortOrder
from pyiceberg.transforms import DayTransform, IdentityTransform
from pyiceberg.types import DoubleType, LongType, StringType, TimestampType
from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.s3_objects as s3
from iceberg.tests.iceberg_engine.native_create.steps import (
    DEFAULT_BASE_LOCATION,
    ENGINE_LESS,
    EXPLICIT_ENGINE,
    catalog_and_database,
    clickhouse_table_name,
    create_table,
    expected_table_location,
    insert_into_native_iceberg_table,
)

INSERT_SETTINGS = [("allow_insert_into_iceberg", 1)]
DROP_SETTINGS = [("allow_insert_into_iceberg", 1)]


def _node():
    return current().context.node


def _qualified(database_name, namespace, table_name):
    return clickhouse_table_name(database_name, namespace, table_name)


def _history_where(database_name, namespace, table_name):
    return (
        f"database = '{database_name}' AND table = '{namespace}.{table_name}'"
    )


def _history_count(database_name, namespace, table_name):
    return _node().query(
        "SELECT count() FROM system.iceberg_history WHERE "
        + _history_where(database_name, namespace, table_name)
    ).output.strip()


def _latest_history(database_name, namespace, table_name):
    """``(operation, summary dict)`` of the current snapshot."""
    operation, summary = (
        _node()
        .query(
            "SELECT operation, toJSONString(summary) FROM system.iceberg_history "
            "WHERE "
            + _history_where(database_name, namespace, table_name)
            + " ORDER BY made_current_at DESC, snapshot_id DESC LIMIT 1"
        )
        .output.strip()
        .split("\t", 1)
    )
    return operation, json.loads(summary)


def _tsv(sql, settings=None):
    return _node().query(sql, settings=settings).output.strip()


# The manifest rewrite below changes bytes in place. A cached copy of the
# pre-rewrite snapshot would hide the equality delete.
FRESH_METADATA = [("use_iceberg_metadata_files_cache", 0)]


def _parquet_keys(namespace, table_name):
    prefix = s3.prefix_from_uri(expected_table_location(namespace, table_name))
    return sorted(key for key in s3.list_keys(prefix) if key.endswith(".parquet"))


def _assert_fails(sql, fragment, settings=None):
    output = _node().query(sql, settings=settings, no_checks=True)
    assert output.exitcode != 0, error(output.output)
    assert fragment in output.output, error(output.output)
    return output


def _drop(ch_name, partition_sql, settings=None):
    _node().query(
        f"ALTER TABLE {ch_name} DROP PARTITION {partition_sql}",
        settings=DROP_SETTINGS if settings is None else settings,
    )


def _day_partition(day):
    """A day transform stores the day number, not the source timestamp.

    The value has to be a literal or a ``tuple(...)`` of constants.
    ``toRelativeDayNum`` is the same day number Iceberg's day transform writes.
    """
    return f"tuple(toRelativeDayNum(toDate('{day}')))"


def _explicit_engine(namespace, table_name):
    """REST ``IcebergS3`` clause: location plus the credentials the database
    engine forwards. Glue cannot use this clause. Its database engine has no
    credential arguments, and a location-only engine then has nothing to sign
    S3 requests with, so Glue tables are created without an ``ENGINE``."""
    location = f"http://minio:9000/warehouse/data/{namespace}/{table_name}/"
    user = current().context.minio_root_user
    password = current().context.minio_root_password
    return f"IcebergS3('{location}', '{user}', '{password}')"


def _system_tables_list_catalog():
    """``system.iceberg_history`` and ``system.iceberg_files`` list REST tables.

    Glue's table listing skips a table whose column list is empty, and
    ClickHouse writes only ``metadata_location`` for those tables, so both
    system tables come back empty. The rows themselves are still readable.
    See https://github.com/Altinity/ClickHouse/issues/2457.
    """
    return current().context.catalog != "glue"


def _days_since_epoch(day):
    return (day - date(1970, 1, 1)).days


def _matches_day(value, day):
    """True when *value* is the Iceberg identity-date form of *day*.

    A partition struct stores that date as a ``datetime.date``, a
    ``datetime.datetime``, or the day number Iceberg uses for the date type.
    """
    if isinstance(value, dict):
        return any(_matches_day(item, day) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_matches_day(item, day) for item in value)
    if isinstance(value, datetime):
        return value.date() == day
    if isinstance(value, date):
        return value == day
    if isinstance(value, int) and not isinstance(value, bool):
        return value == _days_since_epoch(day)
    return False


def _load_table_metadata(table_prefix):
    """Current table metadata. ClickHouse names the file ``vN`` or
    ``00000-<uuid>``, so the newest ``last-updated-ms`` wins."""
    keys = [
        key
        for key in s3.list_keys(table_prefix)
        if key.endswith(".metadata.json")
    ]
    assert keys, f"no metadata under {table_prefix}"
    best_key = None
    best_metadata = None
    best_stamp = -1
    for key in keys:
        metadata = s3.read_json_object(key)
        stamp = metadata.get("last-updated-ms") or 0
        if best_metadata is None or stamp > best_stamp or (
            stamp == best_stamp and key > best_key
        ):
            best_key, best_metadata, best_stamp = key, metadata, stamp
    return best_key, best_metadata


def _store_table_metadata(key, metadata):
    """Rewrite metadata in place, keeping gzip when the object was gzip."""
    raw = s3.get_object_bytes(key)
    body = json.dumps(metadata).encode()
    if raw[:2] == s3.GZIP_MAGIC:
        body = gzip.compress(body)
    s3.put_object_bytes(key, body)


def _bump_summary(summary, field, amount):
    summary[field] = str(int(summary.get(field, "0")) + amount)


def _read_avro(key):
    reader = fastavro.reader(io.BytesIO(s3.get_object_bytes(key)))
    records = [copy.deepcopy(record) for record in reader]
    metadata = {
        name: value
        for name, value in reader.metadata.items()
        if not name.startswith("avro.")
    }
    return records, reader.writer_schema, metadata, reader.codec


def _write_avro(key, records, schema, metadata, codec):
    out = io.BytesIO()
    fastavro.writer(out, schema, records, codec=codec, metadata=metadata)
    s3.put_object_bytes(key, out.getvalue())
    return len(out.getvalue())


def _object_key(path, table_prefix):
    """Bucket key for a manifest path, absolute or table-relative."""
    if path.startswith("s3://") or path.startswith("s3a://"):
        return s3.key_from_uri(path)
    return table_prefix + path.lstrip("/")


def _parent_join(path, name):
    parent, separator, _leaf = path.rpartition("/")
    if not separator:
        return name
    return parent + "/" + name


def _column_field_id(metadata, column):
    schema_id = metadata["current-schema-id"]
    for schema in metadata["schemas"]:
        if schema["schema-id"] == schema_id:
            for field in schema["fields"]:
                if field["name"] == column:
                    return field["id"]
    raise AssertionError(f"column {column} is not in schema {schema_id}")


def _entry_sequence(entry, manifest_sequence):
    sequence = entry.get("sequence_number")
    if sequence is None:
        sequence = manifest_sequence
    return int(sequence or 0)


def _clear_file_stats(data_file):
    """Drop bounds copied from the data file. They describe different rows."""
    for field in (
        "column_sizes",
        "value_counts",
        "null_value_counts",
        "nan_value_counts",
        "lower_bounds",
        "upper_bounds",
        "key_metadata",
        "split_offsets",
        "sort_order_id",
        "first_row_id",
        "referenced_data_file",
        "content_offset",
        "content_size_in_bytes",
    ):
        if field not in data_file or data_file[field] is None:
            continue
        if isinstance(data_file[field], dict):
            data_file[field] = {}
        elif isinstance(data_file[field], list):
            data_file[field] = []
        else:
            data_file[field] = None


def _write_equality_delete_parquet(field_id, column, value):
    schema = pa.schema(
        [
            pa.field(
                column,
                pa.int64(),
                nullable=False,
                metadata={b"PARQUET:field_id": str(field_id).encode()},
            )
        ]
    )
    out = io.BytesIO()
    pq.write_table(pa.table({column: [value]}, schema=schema), out)
    return out.getvalue()


def _add_partitioned_equality_deletes(namespace, table_name, deletes, column="id"):
    """Attach one equality-delete file per ``(day, value)`` pair.

    ClickHouse ``DELETE`` writes position deletes, and PyIceberg 0.9 rewrites
    data files instead of equality deletes, so the file and its manifest entry
    are written here. The entry is cloned from a live data file in that
    partition: the partition struct has to carry every field of the current
    spec, or ``DROP PARTITION`` rejects the file. The delete's sequence number
    is one higher than the data file, which is the Iceberg rule for applying it.
    """
    table_prefix = s3.prefix_from_uri(expected_table_location(namespace, table_name))
    metadata_key, metadata = _load_table_metadata(table_prefix)
    field_id = _column_field_id(metadata, column)
    current_id = metadata["current-snapshot-id"]
    snapshot = next(
        item for item in metadata["snapshots"] if item["snapshot-id"] == current_id
    )
    list_key = _object_key(snapshot["manifest-list"], table_prefix)
    list_records, list_schema, list_metadata, list_codec = _read_avro(list_key)

    live = []
    for list_entry in list_records:
        if list_entry.get("content", 0) != 0:
            continue
        manifest_key = _object_key(list_entry["manifest_path"], table_prefix)
        records, schema, manifest_metadata, codec = _read_avro(manifest_key)
        for entry in records:
            data_file = entry["data_file"]
            if entry.get("status") == 2 or (data_file.get("content") or 0) != 0:
                continue
            live.append(
                {
                    "entry": entry,
                    "manifest_key": manifest_key,
                    "schema": schema,
                    "metadata": manifest_metadata,
                    "codec": codec,
                    "list_entry": list_entry,
                }
            )

    new_list_entries = []
    delete_bytes = 0
    for day, value in deletes:
        matches = [
            item
            for item in live
            if _matches_day(item["entry"]["data_file"]["partition"], day)
        ]
        assert matches, (
            f"no data file in partition {day}; "
            f"partitions={[item['entry']['data_file']['partition'] for item in live]}"
        )
        source = matches[0]
        data = _write_equality_delete_parquet(field_id, column, value)
        filename = f"eq-delete-{getuid()}.parquet"
        stored_path = _parent_join(source["entry"]["data_file"]["file_path"], filename)
        s3.put_object_bytes(_object_key(stored_path, table_prefix), data)
        delete_bytes += len(data)

        entry = copy.deepcopy(source["entry"])
        data_file = entry["data_file"]
        _clear_file_stats(data_file)
        data_file["content"] = 2
        data_file["file_path"] = stored_path
        data_file["file_format"] = "PARQUET"
        data_file["record_count"] = 1
        data_file["file_size_in_bytes"] = len(data)
        data_file["equality_ids"] = [field_id]
        delete_sequence = _entry_sequence(source["entry"], source["list_entry"].get("sequence_number")) + 1
        entry["status"] = 1
        entry["snapshot_id"] = current_id
        if "sequence_number" in entry:
            entry["sequence_number"] = delete_sequence
        if "file_sequence_number" in entry:
            entry["file_sequence_number"] = delete_sequence

        manifest_metadata = dict(source["metadata"])
        content_sample = next(iter(manifest_metadata.values()), b"")
        manifest_metadata["content"] = (
            b"deletes" if isinstance(content_sample, bytes) else "deletes"
        )
        manifest_name = f"eq-delete-{getuid()}.avro"
        manifest_path = _parent_join(source["list_entry"]["manifest_path"], manifest_name)
        manifest_key = _object_key(manifest_path, table_prefix)
        manifest_length = _write_avro(
            manifest_key, [entry], source["schema"], manifest_metadata, source["codec"]
        )

        list_entry = copy.deepcopy(source["list_entry"])
        list_entry["manifest_path"] = manifest_path
        list_entry["manifest_length"] = manifest_length
        list_entry["content"] = 1
        list_entry["added_snapshot_id"] = current_id
        for key, count in (
            ("sequence_number", delete_sequence),
            ("min_sequence_number", delete_sequence),
            ("added_files_count", 1),
            ("existing_files_count", 0),
            ("deleted_files_count", 0),
            ("added_rows_count", 1),
            ("existing_rows_count", 0),
            ("deleted_rows_count", 0),
        ):
            if key in list_entry:
                list_entry[key] = count
        new_list_entries.append(list_entry)

    _write_avro(
        list_key,
        list_records + new_list_entries,
        list_schema,
        list_metadata,
        list_codec,
    )
    # DROP PARTITION subtracts the removed delete files from the parent
    # snapshot summary and rejects a total that would go negative. The
    # summary still describes the append, which had no delete files.
    summary = snapshot.setdefault("summary", {})
    _bump_summary(summary, "total-delete-files", len(deletes))
    _bump_summary(summary, "total-equality-deletes", len(deletes))
    _bump_summary(summary, "total-files-size", delete_bytes)
    _store_table_metadata(metadata_key, metadata)


@TestStep(Given)
def clickhouse_partitioned_table(
    self,
    columns,
    partition_by,
    order_by,
    path=EXPLICIT_ENGINE,
    engine_settings=None,
):
    """A catalog database and one ClickHouse-created Iceberg table.

    REST uses an explicit ``IcebergS3`` engine so ``engine_settings`` such as
    ``iceberg_format_version`` can be set. Glue creates the table without an
    ``ENGINE`` clause, because that catalog cannot keep per-table credentials.

    Returns ``(database_name, namespace, table_name, ch_name)``.
    """
    _, database_name = catalog_and_database(
        minio_root_user=self.context.minio_root_user,
        minio_root_password=self.context.minio_root_password,
        # Glue places an engine-less table under storage_endpoint, which is
        # s3://warehouse rather than s3://warehouse/data. Pin the base so the
        # purge scenario lists the same prefix as REST.
        default_base_location=(
            DEFAULT_BASE_LOCATION if self.context.catalog == "glue" else None
        ),
        clean_up_minio_bucket=False,
    )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    on_glue = self.context.catalog == "glue"
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        path=ENGINE_LESS if on_glue else path,
        columns=columns,
        partition_by=partition_by,
        order_by=order_by,
        engine_settings=None if on_glue else engine_settings,
        engine=None if on_glue else _explicit_engine(namespace, table_name),
    )
    return (
        database_name,
        namespace,
        table_name,
        _qualified(database_name, namespace, table_name),
    )


def _partitioned_table(**kwargs):
    """Call the setup step from a ``Given``, so the scenario receives the
    returned names. A step invoked directly from a scenario returns its
    test result instead."""
    with Given("a partitioned Iceberg table"):
        return clickhouse_partitioned_table(**kwargs)


def _open_catalog():
    with Given("catalog and database"):
        return catalog_and_database(
            minio_root_user=current().context.minio_root_user,
            minio_root_password=current().context.minio_root_password,
            default_base_location=None,
            clean_up_minio_bucket=False,
        )


@TestScenario
def identity_drop(self):
    """Two inserts, then drop one identity value. The other value remains
    and the new snapshot is a DELETE."""
    database_name, namespace, table_name, ch_name = _partitioned_table(
        columns=["key Int64", "val String"],
        partition_by="key",
        order_by="val",
    )
    insert_into_native_iceberg_table(
        table_name=ch_name, values_sql="(10, 'a'), (10, 'b')"
    )
    insert_into_native_iceberg_table(table_name=ch_name, values_sql="(20, 'c')")

    with When("drop partition 10"):
        _drop(ch_name, "10")

    with Then("partition 20 remains and the snapshot is a DELETE"):
        assert _tsv(f"SELECT key, val FROM {ch_name} ORDER BY key") == "20\tc", error()
        if _system_tables_list_catalog():
            operation, summary = _latest_history(database_name, namespace, table_name)
            assert operation == "DELETE", error(operation)
            assert int(summary["deleted-records"]) == 2, error(summary)


@TestScenario
def day_transform(self):
    """``PARTITION BY toRelativeDayNum(ts)`` drops every row of that day."""
    _, _, _, ch_name = _partitioned_table(
        columns=["ts DateTime64(6)", "id Int64"],
        partition_by="toRelativeDayNum(ts)",
        order_by="id",
    )
    insert_into_native_iceberg_table(
        table_name=ch_name,
        values_sql=(
            "(toDateTime64('2024-01-15 08:00:00', 6), 1), "
            "(toDateTime64('2024-01-15 23:59:59', 6), 2), "
            "(toDateTime64('2024-01-16 09:00:00', 6), 3)"
        ),
    )

    with When("drop 2024-01-15"):
        _drop(ch_name, _day_partition("2024-01-15"))

    with Then("only the next day remains"):
        assert _tsv(f"SELECT id FROM {ch_name} ORDER BY id") == "3", error()


@TestScenario
def tuple_key(self):
    """A two-field identity spec takes a tuple. A scalar and a tuple of the
    wrong width are rejected with the field count, and the table is unchanged
    by those rejects."""
    _, _, _, ch_name = _partitioned_table(
        columns=["country String", "region String", "id Int64"],
        partition_by="(country, region)",
        order_by="id",
    )
    insert_into_native_iceberg_table(
        table_name=ch_name,
        values_sql="('US', 'west', 1), ('US', 'east', 2), ('DE', 'west', 3)",
    )

    with When("reject a scalar and a tuple of the wrong width"):
        _assert_fails(
            f"ALTER TABLE {ch_name} DROP PARTITION 'US'",
            "must be: 2",
            settings=DROP_SETTINGS,
        )
        _assert_fails(
            f"ALTER TABLE {ch_name} DROP PARTITION ('US', 'west', 'extra')",
            "must be: 2",
            settings=DROP_SETTINGS,
        )
        assert _tsv(f"SELECT count() FROM {ch_name}") == "3", error()

    with Then("drop one pair"):
        _drop(ch_name, "('US', 'west')")
        assert (
            _tsv(f"SELECT country, region, id FROM {ch_name} ORDER BY id")
            == "US\teast\t2\nDE\twest\t3"
        ), error()


@TestScenario
def empty_partition_is_noop(self):
    """A value no file belongs to succeeds and does not add a snapshot."""
    database_name, namespace, table_name, ch_name = _partitioned_table(
        columns=["key Int64", "val String"],
        partition_by="key",
        order_by="val",
    )
    insert_into_native_iceberg_table(table_name=ch_name, values_sql="(10, 'a')")
    before = (
        _history_count(database_name, namespace, table_name)
        if _system_tables_list_catalog()
        else None
    )

    with When("drop a value that was never written"):
        _drop(ch_name, "99")

    with Then("rows and snapshot count stay put"):
        assert _tsv(f"SELECT val FROM {ch_name}") == "a", error()
        if before is not None:
            assert (
                _history_count(database_name, namespace, table_name) == before
            ), error()


@TestScenario
def purge_keeps_or_removes_files(self):
    """``iceberg_delete_data_on_drop`` leaves the parquet objects when off
    and removes the dropped partition's objects when on."""
    _, namespace, table_name, ch_name = _partitioned_table(
        columns=["event_date Date", "id Int64"],
        partition_by="event_date",
        order_by="id",
    )
    insert_into_native_iceberg_table(
        table_name=ch_name,
        values_sql=(
            "('2024-01-15', 1), ('2024-01-15', 2), "
            "('2024-01-16', 3), ('2024-01-17', 4)"
        ),
    )
    after_insert = _parquet_keys(namespace, table_name)
    assert len(after_insert) == 3, error(after_insert)

    with When("drop one day with purge off"):
        _drop(
            ch_name,
            "'2024-01-16'",
            settings=[
                ("allow_insert_into_iceberg", 1),
                ("iceberg_delete_data_on_drop", 0),
            ],
        )

    with Then("the rows are gone and the parquet objects remain"):
        assert _tsv(f"SELECT id FROM {ch_name} ORDER BY id") == "1\n2\n4", error()
        assert _parquet_keys(namespace, table_name) == after_insert, error()

    with When("drop another day with purge on"):
        _drop(
            ch_name,
            "'2024-01-15'",
            settings=[
                ("allow_insert_into_iceberg", 1),
                ("iceberg_delete_data_on_drop", 1),
            ],
        )

    with Then(
        "that partition's parquet object is gone and the unreferenced one stays"
    ):
        assert _tsv(f"SELECT id FROM {ch_name}") == "4", error()
        kept = _parquet_keys(namespace, table_name)
        assert len(kept) == 2, error(kept)
        assert set(kept) < set(after_insert), error(kept)


@TestScenario
def iceberg_s3_without_catalog(self):
    """``IcebergS3`` with no catalog commits the drop through the metadata
    file and the version hint."""
    node = _node()
    table_name = f"drop_partition_s3_{getuid()}"
    user = self.context.minio_root_user
    password = self.context.minio_root_password
    prefix = f"data/{table_name}/"
    try:
        write_settings = [
            ("allow_insert_into_iceberg", 1),
            ("write_full_path_in_iceberg_metadata", 1),
        ]
        node.query(
            f"CREATE TABLE {table_name} (ts DateTime64(6), id Int64) "
            f"ENGINE = IcebergS3('http://minio:9000/warehouse/{prefix}', "
            f"'{user}', '{password}') "
            f"PARTITION BY toRelativeDayNum(ts) ORDER BY id "
            f"SETTINGS iceberg_use_version_hint = 1",
            settings=[("write_full_path_in_iceberg_metadata", 1)],
        )
        node.query(
            f"INSERT INTO {table_name} VALUES "
            "(toDateTime64('2024-01-15 08:00:00', 6), 1), "
            "(toDateTime64('2024-01-16 09:00:00', 6), 2)",
            settings=write_settings,
        )
        with When("drop one day"):
            _drop(table_name, _day_partition("2024-01-15"), settings=write_settings)
        with Then("the other day remains"):
            assert _tsv(f"SELECT id FROM {table_name}") == "2", error()
    finally:
        with Finally(f"drop {table_name}"):
            node.query(f"DROP TABLE IF EXISTS {table_name}", no_checks=True)
            s3.delete_prefix(prefix)


@TestScenario
def position_deletes(self):
    """A drop removes the partition's data file and its position-delete file."""
    database_name, namespace, table_name, ch_name = _partitioned_table(
        columns=["event_date Date", "id Int64"],
        partition_by="event_date",
        order_by="id",
    )
    insert_into_native_iceberg_table(
        table_name=ch_name,
        values_sql=(
            "('2024-01-15', 1), ('2024-01-15', 2), "
            "('2024-01-16', 3), ('2024-01-17', 4)"
        ),
    )
    _node().query(
        f"DELETE FROM {ch_name} WHERE event_date = '2024-01-16'",
        settings=INSERT_SETTINGS,
    )
    _node().query(
        f"DELETE FROM {ch_name} WHERE id = 1",
        settings=INSERT_SETTINGS,
    )
    assert _tsv(f"SELECT count() FROM {ch_name}") == "2", error()
    if _system_tables_list_catalog():
        assert (
            _tsv(
                "SELECT count() FROM system.iceberg_files WHERE "
                + _history_where(database_name, namespace, table_name)
                + " AND content = 'POSITION_DELETE'"
            )
            == "2"
        ), error()

    with When("drop the day that held a data file and a position delete"):
        _drop(ch_name, "'2024-01-15'")

    with Then("that day is gone and its position delete left with it"):
        assert _tsv(f"SELECT id FROM {ch_name}") == "4", error()
        if _system_tables_list_catalog():
            operation, summary = _latest_history(database_name, namespace, table_name)
            assert operation == "DELETE", error(operation)
            assert summary["deleted-data-files"] == "1", error(summary)
            assert summary["removed-position-delete-files"] == "1", error(summary)
            assert summary["removed-position-deletes"] == "1", error(summary)


@TestScenario
def equality_deletes(self):
    """A drop removes the equality-delete file in that partition and leaves
    the equality delete in the other partition applied."""
    database_name, namespace, table_name, ch_name = _partitioned_table(
        columns=["event_date Date", "id Int64"],
        partition_by="event_date",
        order_by="id",
    )
    insert_into_native_iceberg_table(
        table_name=ch_name,
        values_sql=(
            "('2024-01-15', 1), ('2024-01-15', 2), "
            "('2024-01-16', 3), ('2024-01-16', 4)"
        ),
    )
    _add_partitioned_equality_deletes(
        namespace,
        table_name,
        [(date(2024, 1, 15), 1), (date(2024, 1, 16), 3)],
    )

    with Then("each equality delete hides its row"):
        assert (
            _tsv(
                f"SELECT id FROM {ch_name} ORDER BY id",
                settings=FRESH_METADATA,
            )
            == "2\n4"
        ), error()
        if _system_tables_list_catalog():
            assert (
                _tsv(
                    "SELECT count() FROM system.iceberg_files WHERE "
                    + _history_where(database_name, namespace, table_name)
                    + " AND content = 'EQUALITY_DELETE'",
                    settings=FRESH_METADATA,
                )
                == "2"
            ), error()

    with When("drop the day that held an equality delete"):
        _drop(
            ch_name,
            "'2024-01-15'",
            settings=DROP_SETTINGS + FRESH_METADATA,
        )

    with Then("that equality delete is gone and the other one still applies"):
        assert (
            _tsv(
                f"SELECT id FROM {ch_name} ORDER BY id",
                settings=FRESH_METADATA,
            )
            == "4"
        ), error()
        if _system_tables_list_catalog():
            operation, summary = _latest_history(database_name, namespace, table_name)
            assert operation == "DELETE", error(operation)
            assert summary["deleted-data-files"] == "1", error(summary)
            assert summary["removed-equality-delete-files"] == "1", error(summary)
            assert summary["removed-equality-deletes"] == "1", error(summary)


@TestScenario
def mixed_manifest_rewrite(self):
    """One PyIceberg append that spans three days shares a manifest.
    Dropping one day rewrites that manifest and leaves the other days."""
    catalog, database_name = _open_catalog()
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
    schema = Schema(
        NestedField(field_id=1, name="ts", field_type=TimestampType(), required=False),
        NestedField(field_id=2, name="country", field_type=StringType(), required=False),
        NestedField(field_id=3, name="id", field_type=LongType(), required=False),
        NestedField(field_id=4, name="amount", field_type=DoubleType(), required=False),
    )
    location = expected_table_location(namespace, table_name)
    with Given("pyiceberg table"):
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location=location,
            partition_spec=PartitionSpec(
                PartitionField(
                    source_id=1, field_id=1000, transform=DayTransform(), name="ts_day"
                )
            ),
            sort_order=SortOrder(),
        )
    rows = [
        {"ts": datetime(2024, 1, 15, 8, 0, 0), "country": "US", "id": 1, "amount": 10.5},
        {"ts": datetime(2024, 1, 15, 12, 30, 0), "country": "DE", "id": 2, "amount": 20.0},
        {"ts": datetime(2024, 1, 15, 23, 0, 0), "country": "US", "id": 3, "amount": 30.25},
        {"ts": datetime(2024, 1, 16, 9, 0, 0), "country": "US", "id": 4, "amount": 60.0},
        {"ts": datetime(2024, 1, 16, 18, 45, 0), "country": "DE", "id": 5, "amount": 70.75},
        {"ts": datetime(2024, 1, 17, 11, 11, 11), "country": "JP", "id": 6, "amount": 80.0},
    ]
    table.append(pa.Table.from_pylist(rows, schema=schema.as_arrow()))
    manifests = table.current_snapshot().manifests(table.io)
    assert len(manifests) == 1, error(
        f"the rewrite path needs one manifest, pyiceberg wrote {len(manifests)}"
    )

    ch_name = _qualified(database_name, namespace, table_name)
    with When("drop 2024-01-15"):
        _drop(ch_name, _day_partition("2024-01-15"))

    with Then("the other two days remain in a DELETE snapshot"):
        assert _tsv(f"SELECT id FROM {ch_name} ORDER BY id") == "4\n5\n6", error()
        if _system_tables_list_catalog():
            operation, summary = _latest_history(database_name, namespace, table_name)
            assert operation == "DELETE", error(operation)
            assert summary["deleted-data-files"] == "1", error(summary)
            assert summary["total-records"] == "3", error(summary)


@TestScenario
def drop_includes_files_from_a_finer_spec(self):
    """Files written under ``day(ts), country`` are finer than the current
    ``day(ts)`` spec, so a drop by day takes them with the current spec's files."""
    catalog, database_name = _open_catalog()
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
    schema = Schema(
        NestedField(field_id=1, name="ts", field_type=TimestampType(), required=False),
        NestedField(field_id=2, name="country", field_type=StringType(), required=False),
        NestedField(field_id=3, name="id", field_type=LongType(), required=False),
    )
    with Given("pyiceberg table"):
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location=expected_table_location(namespace, table_name),
            partition_spec=PartitionSpec(
                PartitionField(
                    source_id=1, field_id=1000, transform=DayTransform(), name="ts_day"
                ),
                PartitionField(
                    source_id=2,
                    field_id=1001,
                    transform=IdentityTransform(),
                    name="country",
                ),
            ),
            sort_order=SortOrder(),
        )
    table.append(
        pa.Table.from_pylist(
            [
                {"ts": datetime(2024, 1, 15, 8, 0, 0), "country": "US", "id": 1},
                {"ts": datetime(2024, 1, 15, 12, 0, 0), "country": "DE", "id": 2},
                {"ts": datetime(2024, 1, 16, 9, 0, 0), "country": "US", "id": 3},
            ],
            schema=schema.as_arrow(),
        )
    )
    with table.update_spec() as update:
        update.remove_field("country")
    table.append(
        pa.Table.from_pylist(
            [
                {"ts": datetime(2024, 1, 15, 20, 0, 0), "country": "JP", "id": 4},
                {"ts": datetime(2024, 1, 17, 10, 0, 0), "country": "US", "id": 5},
            ],
            schema=schema.as_arrow(),
        )
    )

    ch_name = _qualified(database_name, namespace, table_name)
    with When("drop 2024-01-15"):
        _drop(ch_name, _day_partition("2024-01-15"))

    with Then("rows from both specs on that day are gone"):
        assert _tsv(f"SELECT id FROM {ch_name} ORDER BY id") == "3\n5", error()
        if _system_tables_list_catalog():
            operation, summary = _latest_history(database_name, namespace, table_name)
            assert operation == "DELETE", error(operation)
            assert summary["deleted-data-files"] == "3", error(summary)


@TestScenario
def reject_file_from_a_coarser_spec(self):
    """A file written before the spec gained a field does not constrain every
    field of the current spec, so the drop is rejected and the rows stay."""
    catalog, database_name = _open_catalog()
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
    schema = Schema(
        NestedField(field_id=1, name="id", field_type=LongType(), required=False),
        NestedField(field_id=2, name="country", field_type=StringType(), required=False),
    )
    with Given("pyiceberg table"):
        table = catalog_steps.create_iceberg_table(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            schema=schema,
            location=expected_table_location(namespace, table_name),
            partition_spec=PartitionSpec(
                PartitionField(
                    source_id=1, field_id=1000, transform=IdentityTransform(), name="id"
                )
            ),
            sort_order=SortOrder(),
        )
    table.append(
        pa.Table.from_pylist(
            [{"id": 10, "country": "US"}],
            schema=schema.as_arrow(),
        )
    )
    with table.update_spec() as update:
        update.add_field("country", IdentityTransform(), "country")

    ch_name = _qualified(database_name, namespace, table_name)
    with When("drop a value of the evolved spec"):
        _assert_fails(
            f"ALTER TABLE {ch_name} DROP PARTITION (10, 'US')",
            "does not contain every field",
            settings=DROP_SETTINGS,
        )

    with Then("the row is still there"):
        assert _tsv(f"SELECT count() FROM {ch_name}") == "1", error()


@TestScenario
def reject_unpartitioned_all_and_id(self):
    """An unpartitioned table, ``DROP PARTITION ALL``, and ``DROP PARTITION ID``
    are rejected."""
    _, _, _, ch_name = _partitioned_table(
        columns=["id Int64", "country String"],
        partition_by="id",
        order_by="country",
    )
    insert_into_native_iceberg_table(
        table_name=ch_name, values_sql="(1, 'CA'), (2, 'PT')"
    )

    with When("ALL and a partition id"):
        _assert_fails(
            f"ALTER TABLE {ch_name} DROP PARTITION ALL",
            "ALL is not supported for Iceberg",
            settings=DROP_SETTINGS,
        )
        _assert_fails(
            f"ALTER TABLE {ch_name} DROP PARTITION ID '1'",
            "ID is not supported",
            settings=DROP_SETTINGS,
        )
        assert _tsv(f"SELECT count() FROM {ch_name}") == "2", error()

    with And("an unpartitioned table"):
        _, _, _, plain = _partitioned_table(
            columns=["id Int64"],
            partition_by=None,
            order_by="id",
        )
        insert_into_native_iceberg_table(table_name=plain, values_sql="(1)")
        _assert_fails(
            f"ALTER TABLE {plain} DROP PARTITION 1",
            "unpartitioned",
            settings=DROP_SETTINGS,
        )
        assert _tsv(f"SELECT count() FROM {plain}") == "1", error()


@TestScenario
def reject_format_version_1(self):
    """Format version 1 is rejected."""
    if self.context.catalog == "glue":
        skip(
            "iceberg_format_version requires an explicit IcebergS3 engine, "
            "and Glue rejects that engine once it carries storage credentials"
        )
    _, _, _, ch_name = _partitioned_table(
        columns=["key Int64", "val String"],
        partition_by="key",
        order_by="val",
        path=EXPLICIT_ENGINE,
        engine_settings={"iceberg_format_version": 1},
    )
    insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1, 'a')")
    _assert_fails(
        f"ALTER TABLE {ch_name} DROP PARTITION 1",
        "format-version 2",
        settings=DROP_SETTINGS,
    )
    assert _tsv(f"SELECT val FROM {ch_name}") == "a", error()


@TestScenario
def reject_format_version_3(self):
    """Format version 3 is rejected. Any format other than 2 is."""
    if self.context.catalog == "glue":
        skip(
            "iceberg_format_version requires an explicit IcebergS3 engine, "
            "and Glue rejects that engine once it carries storage credentials"
        )
    _, _, _, ch_name = _partitioned_table(
        columns=["key Int64", "val String"],
        partition_by="key",
        order_by="val",
        path=EXPLICIT_ENGINE,
        engine_settings={"iceberg_format_version": 3},
    )
    insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1, 'a')")
    _assert_fails(
        f"ALTER TABLE {ch_name} DROP PARTITION 1",
        "format-version 3",
        settings=DROP_SETTINGS,
    )
    assert _tsv(f"SELECT val FROM {ch_name}") == "a", error()


@TestScenario
def requires_allow_insert(self):
    """The statement requires ``allow_insert_into_iceberg``."""
    _, _, _, ch_name = _partitioned_table(
        columns=["key Int64", "val String"],
        partition_by="key",
        order_by="val",
    )
    insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1, 'a')")
    _assert_fails(
        f"ALTER TABLE {ch_name} DROP PARTITION 1",
        "allow_insert_into_iceberg",
        settings=[("allow_insert_into_iceberg", 0)],
    )
    assert _tsv(f"SELECT val FROM {ch_name}") == "a", error()


@TestFeature
@Name("drop partition")
def feature(self, minio_root_user, minio_root_password):
    """RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.DropPartition."""
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password

    for scenario in loads(current_module(), Scenario):
        scenario()
