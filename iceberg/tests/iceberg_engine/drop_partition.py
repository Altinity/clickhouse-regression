"""ALTER TABLE ... DROP PARTITION for Iceberg.

Covers RQ.SRS-045.ClickHouse.Iceberg.DatabaseEngine.DropPartition.
Runs on the REST catalog and on Glue. The suite skips this feature until
the statement is in a released build; see ``ffails`` in ``iceberg/regression.py``.
"""

import json
from datetime import datetime

import pyarrow as pa
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


def _tsv(sql):
    return _node().query(sql).output.strip()


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
