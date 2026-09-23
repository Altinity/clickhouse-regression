"""DataLakeCatalog reads Iceberg v3 row lineage.

Spark writes the table into the REST catalog on ``rest:8181`` (the
``iceberg_spark`` container). ClickHouse reads the same table and must
return the same ``_row_id`` and ``_last_updated_sequence_number`` Spark
returns. ``system.iceberg_files.first_row_id`` is the id assigned to the
first row of each data file.

Row lineage is part of format version 3. A format version 2 table leaves
both virtual columns and ``first_row_id`` null. The Spark image has to
write lineage (iceberg-spark-runtime 1.10 or newer); an older image fails
in the Spark SELECT, which is the signal to update the image.
"""

from testflows.core import *
from testflows.asserts import error

from helpers.common import (
    getuid,
    check_clickhouse_version,
    check_if_antalya_build,
)

import iceberg.tests.steps.spark as spark
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.metrics as metrics
from iceberg.tests.deletion_vectors.steps.common import cleanup_created_tables

# Spark's ``demo`` catalog is this REST catalog, not ice-rest-catalog.
SPARK_REST_CATALOG_URL = "http://rest:8181"
SPARK_REST_WAREHOUSE = "s3://warehouse"
SPARK_STORAGE_ENDPOINT = "http://minio:9000/warehouse"

# Appends only. Copy-on-write is set on the rewrite scenario so an UPDATE
# rewrites the data file instead of committing a deletion vector.
V3_APPEND = {"format-version": "3"}
V3_COPY_ON_WRITE = {
    "format-version": "3",
    "write.update.mode": "copy-on-write",
    "write.delete.mode": "copy-on-write",
}
V2 = {"format-version": "2"}


def _row_lineage_supported(test):
    """True when this build exposes the v3 row-lineage virtual columns.

    Antalya carries them from 26.6 (backport of ClickHouse#115603).
    Upstream merged that change to master on 2026-08-28, after the 26.8
    branch, so a non-Antalya build needs 26.9 or newer.
    """
    if check_if_antalya_build(test):
        return check_clickhouse_version(">=26.6")(test)
    return check_clickhouse_version(">=26.9")(test)


def _insert_range(start, end, data="'a'"):
    """One Spark INSERT of ``[start, end)`` as a single data file."""
    return (
        f"INSERT INTO {{table}} SELECT /*+ COALESCE(1) */ id, {data} "
        f"FROM range({start}, {end})"
    )


def _parse_optional_int(value):
    if value in ("\\N", "NULL", "null", ""):
        return None
    return int(value)


def _lineage_from_rows(rows):
    """``id -> (_row_id, _last_updated_sequence_number)`` from TSV cells."""
    lineage = {}
    for row in rows:
        if len(row) != 3 or row[0] == "":
            fail(f"expected three lineage columns, got {row!r}")
        lineage[int(row[0])] = (
            _parse_optional_int(row[1]),
            _parse_optional_int(row[2]),
        )
    return lineage


def _clickhouse_lineage(
    database_name,
    namespace,
    table_name,
    where_clause=None,
    log_comment=None,
    use_iceberg_partition_pruning=None,
):
    result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        columns="id, _row_id, _last_updated_sequence_number",
        order_by="id",
        where_clause=where_clause,
        log_comment=log_comment,
        use_iceberg_partition_pruning=use_iceberg_partition_pruning,
        input_format_parquet_filter_push_down="0",
        input_format_parquet_bloom_filter_push_down="0",
        use_iceberg_metadata_files_cache="0",
        use_cache_for_count_from_files="0",
    )
    rows = [
        line.split("\t")
        for line in result.output.splitlines()
        if line.strip()
    ]
    return _lineage_from_rows(rows)


def _spark_lineage(namespace, table_name):
    rows = spark.select_rows(
        namespace=namespace,
        table_name=table_name,
        columns="id, _row_id, _last_updated_sequence_number",
        order_by="id",
    )
    return _lineage_from_rows(rows)


def _assert_matches_spark(database_name, namespace, table_name):
    clickhouse = _clickhouse_lineage(database_name, namespace, table_name)
    spark_rows = _spark_lineage(namespace, table_name)
    assert clickhouse == spark_rows, error(
        f"lineage mismatch:\nclickhouse={clickhouse}\nspark={spark_rows}"
    )
    return clickhouse


def _open_catalog_database(minio_root_user, minio_root_password):
    return iceberg_engine.create_experimental_iceberg_database_with_rest_catalog(
        s3_access_key_id=minio_root_user,
        s3_secret_access_key=minio_root_password,
        rest_catalog_url=SPARK_REST_CATALOG_URL,
        warehouse=SPARK_REST_WAREHOUSE,
        storage_endpoint=SPARK_STORAGE_ENDPOINT,
        auth_header=None,
    )


def _data_file_first_row_ids(database_name, namespace, table_name):
    """Resolved ``first_row_id`` of each live DATA file, or None when unset."""
    catalog_table = f"{namespace}.{table_name}"
    result = current().context.node.query(
        f"""
        SELECT table, first_row_id
        FROM system.iceberg_files
        WHERE database = '{database_name}'
          AND content = 'DATA'
        ORDER BY table, first_row_id
        FORMAT TabSeparated
        """
    )
    rows = [line.split("\t") for line in result.output.splitlines() if line.strip()]
    matched = [row for row in rows if row[0] == catalog_table]
    assert matched, error(
        f"no DATA files for {database_name}.{catalog_table} in "
        f"system.iceberg_files. Rows in this database: {rows}"
    )
    return [_parse_optional_int(row[1]) for row in matched]


@TestScenario
def inherited_row_ids(self, minio_root_user, minio_root_password):
    """Two appends assign a contiguous ``_row_id`` range per file.

    ``_last_updated_sequence_number`` is that file's data sequence number.
    ``system.iceberg_files.first_row_id`` is the first id of each range.
    """
    with Given("a v3 table with two single-file appends"):
        namespace, table_name = spark.create_table(
            namespace=f"lineage_{getuid()}",
            columns="id BIGINT, data STRING",
            properties=V3_APPEND,
            setup_statements=[
                _insert_range(0, 10, data="'a'"),
                _insert_range(10, 20, data="'b'"),
            ],
        )

    with And("a DataLakeCatalog database over the Spark REST catalog"):
        database_name = _open_catalog_database(minio_root_user, minio_root_password)

    with Then("ClickHouse returns the same lineage Spark does"):
        lineage = _assert_matches_spark(database_name, namespace, table_name)

    with And("each append is one file with a contiguous id range"):
        by_sequence = {}
        for row_id, sequence_number in lineage.values():
            assert row_id is not None and sequence_number is not None, error(
                f"a v3 append must assign lineage, got {lineage}"
            )
            by_sequence.setdefault(sequence_number, []).append(row_id)

        assert len(by_sequence) == 2, error(
            f"expected one sequence number per append, got {sorted(by_sequence)}"
        )
        for sequence_number, row_ids in by_sequence.items():
            assert len(row_ids) == 10, error(
                f"sequence {sequence_number} has {len(row_ids)} rows, expected 10"
            )
            assert max(row_ids) - min(row_ids) + 1 == len(row_ids), error(
                f"sequence {sequence_number} row ids are not contiguous: {sorted(row_ids)}"
            )
            assert len(set(row_ids)) == len(row_ids), error(
                f"duplicate _row_id in sequence {sequence_number}"
            )

    with And("system.iceberg_files.first_row_id is the start of each range"):
        first_row_ids = _data_file_first_row_ids(database_name, namespace, table_name)
        expected = sorted(min(row_ids) for row_ids in by_sequence.values())
        assert sorted(first_row_ids) == expected, error(
            f"first_row_id {first_row_ids} != range starts {expected}"
        )


@TestScenario
def copied_rows_keep_row_ids(self, minio_root_user, minio_root_password):
    """A copy-on-write update keeps ``_row_id`` and stamps a new sequence on the changed row.

    Rows copied without a change keep both values. Rows inserted afterwards
    receive ids that do not overlap the copied ones.
    """
    with Given("a v3 copy-on-write table with four rows in one file"):
        namespace, table_name = spark.create_table(
            namespace=f"lineage_{getuid()}",
            columns="id BIGINT, data STRING",
            properties=V3_COPY_ON_WRITE,
            setup_statements=[_insert_range(0, 4)],
        )

    with And("a DataLakeCatalog database over the Spark REST catalog"):
        database_name = _open_catalog_database(minio_root_user, minio_root_password)

    with And("the lineage of the initial append"):
        before = _assert_matches_spark(database_name, namespace, table_name)
        assert set(before) == {0, 1, 2, 3}, error(f"unexpected ids: {sorted(before)}")

    with When("Spark rewrites the file to update one row"):
        spark.update_rows(
            namespace=namespace,
            table_name=table_name,
            set_clause="data = 'z'",
            condition="id = 1",
        )

    with Then("copied rows keep their ids and only the updated row gets a new sequence"):
        after = _assert_matches_spark(database_name, namespace, table_name)
        for row_key in (0, 2, 3):
            assert after[row_key] == before[row_key], error(
                f"id {row_key} changed from {before[row_key]} to {after[row_key]}"
            )
        assert after[1][0] == before[1][0], error(
            f"updated row changed _row_id from {before[1][0]} to {after[1][0]}"
        )
        assert after[1][1] is not None and before[1][1] is not None, error(after)
        assert after[1][1] > before[1][1], error(
            f"updated row sequence did not advance: {before[1]} -> {after[1]}"
        )

    with And("the rewritten file's first_row_id is a newly reserved block"):
        # Materialized ``_row_id`` values stay 0..3. The manifest assigns a
        # fresh first_row_id past that block; readers must not use it in
        # place of the stored ids.
        first_row_ids = _data_file_first_row_ids(database_name, namespace, table_name)
        assert len(first_row_ids) == 1, error(
            f"copy-on-write update should leave one data file, got {first_row_ids}"
        )
        copied_ids = [row_id for row_id, _ in after.values()]
        assert first_row_ids[0] is not None, error("rewritten file has no first_row_id")
        assert first_row_ids[0] == max(copied_ids) + 1, error(
            f"first_row_id {first_row_ids[0]} is not just past copied ids {sorted(copied_ids)}"
        )

    with When("Spark appends two new rows"):
        spark.insert_rows(
            namespace=namespace,
            table_name=table_name,
            values="(4, 'n'), (5, 'n')",
        )

    with Then("new rows get ids outside the copied set and copied rows stay put"):
        final = _assert_matches_spark(database_name, namespace, table_name)
        for row_key in (0, 1, 2, 3):
            assert final[row_key] == after[row_key], error(
                f"id {row_key} changed after the append: {after[row_key]} -> {final[row_key]}"
            )
        new_ids = {final[4][0], final[5][0]}
        assert None not in new_ids, error(f"new rows missing _row_id: {final}")
        assert new_ids.isdisjoint(copied_ids), error(
            f"new row ids {new_ids} overlap copied ids {sorted(copied_ids)}"
        )


@TestScenario
def null_without_lineage(self, minio_root_user, minio_root_password):
    """A format version 2 table has no row lineage, and the data still reads."""
    with Given("a v2 table with four rows"):
        namespace, table_name = spark.create_table(
            namespace=f"lineage_{getuid()}",
            columns="id BIGINT, data STRING",
            properties=V2,
            setup_statements=[_insert_range(0, 4)],
        )

    with And("a DataLakeCatalog database over the Spark REST catalog"):
        database_name = _open_catalog_database(minio_root_user, minio_root_password)

    with Then("both virtual columns are null"):
        lineage = _clickhouse_lineage(database_name, namespace, table_name)
        assert set(lineage) == {0, 1, 2, 3}, error(f"unexpected ids: {sorted(lineage)}")
        assert all(values == (None, None) for values in lineage.values()), error(
            f"v2 lineage must be null, got {lineage}"
        )

    with And("the rows themselves are still returned"):
        result = iceberg_engine.read_data_from_clickhouse_iceberg_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns="id, data",
            order_by="id",
        )
        assert result.output.strip() == "0\ta\n1\ta\n2\ta\n3\ta", error()

    with And("system.iceberg_files.first_row_id is null"):
        first_row_ids = _data_file_first_row_ids(database_name, namespace, table_name)
        assert first_row_ids, error("v2 table produced no DATA files")
        assert all(value is None for value in first_row_ids), error(
            f"v2 first_row_id must be null, got {first_row_ids}"
        )


def _pruned_files(log_comment):
    return int(
        metrics.get_IcebergMinMaxIndexPrunedFiles(log_comment=log_comment).output.strip()
    )


@TestScenario
def row_id_filter_prunes_files(self, minio_root_user, minio_root_password):
    """A ``_row_id`` point lookup skips every data file whose range does not contain it.

    The skip is ``IcebergMinMaxIndexPrunedFiles``. The same lookup with
    manifest pruning disabled skips nothing and returns the same row.
    """
    file_rows = 10
    file_count = 5

    with Given("a v3 table with five single-file appends"):
        namespace, table_name = spark.create_table(
            namespace=f"lineage_{getuid()}",
            columns="id BIGINT, data STRING",
            properties=V3_APPEND,
            setup_statements=[
                _insert_range(index * file_rows, (index + 1) * file_rows)
                for index in range(file_count)
            ],
        )

    with And("a DataLakeCatalog database over the Spark REST catalog"):
        database_name = _open_catalog_database(minio_root_user, minio_root_password)

    with And("lineage that matches Spark, one contiguous range per append"):
        lineage = _assert_matches_spark(database_name, namespace, table_name)
        by_sequence = {}
        for row_key, (row_id, sequence_number) in lineage.items():
            by_sequence.setdefault(sequence_number, []).append((row_key, row_id))
        assert len(by_sequence) == file_count, error(
            f"expected {file_count} files, got sequences {sorted(by_sequence)}"
        )
        middle = sorted(by_sequence)[file_count // 2]
        middle_rows = by_sequence[middle]
        assert len(middle_rows) == file_rows, error(middle_rows)
        target_id, target_row_id = sorted(middle_rows)[file_rows // 2]

    with When(f"a point lookup of _row_id {target_row_id} with pruning enabled"):
        enabled_comment = f"row_lineage_prune_{getuid()}"
        enabled = _clickhouse_lineage(
            database_name,
            namespace,
            table_name,
            where_clause=f"_row_id = {target_row_id}",
            log_comment=enabled_comment,
            use_iceberg_partition_pruning="1",
        )

    with Then("the lookup returns that row and skips the other files"):
        assert list(enabled) == [target_id], error(
            f"lookup of _row_id {target_row_id} returned {enabled}"
        )
        assert _pruned_files(enabled_comment) == file_count - 1, error()

    with When("the same lookup with manifest pruning disabled"):
        disabled_comment = f"row_lineage_noprune_{getuid()}"
        disabled = _clickhouse_lineage(
            database_name,
            namespace,
            table_name,
            where_clause=f"_row_id = {target_row_id}",
            log_comment=disabled_comment,
            use_iceberg_partition_pruning="0",
        )

    with Then("the row is the same and no file is skipped"):
        assert disabled == enabled, error(
            f"pruning changed the result: {enabled} vs {disabled}"
        )
        assert _pruned_files(disabled_comment) == 0, error()


@TestFeature
@Name("row lineage")
def feature(self, minio_root_user, minio_root_password):
    """Read Iceberg v3 row lineage through DataLakeCatalog."""
    if not _row_lineage_supported(self):
        skip(
            "row lineage virtual columns need Antalya >= 26.6 "
            "or ClickHouse >= 26.9 (ClickHouse#115603)"
        )

    self.context.spark_created_tables = []

    with Given("the Spark writer container is ready"):
        spark.wait_for_spark()

    try:
        for scenario in (
            inherited_row_ids,
            copied_rows_keep_row_ids,
            null_without_lineage,
            row_id_filter_prunes_files,
        ):
            Scenario(test=scenario)(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
    finally:
        with Finally("drop Spark tables"):
            cleanup_created_tables()
