"""Core fixtures and assertions for the deletion-vectors suite.

The canonical fixture is :func:`table_with_deletion_vectors`: Spark creates
an Iceberg format-version 3 merge-on-read table under
``s3://warehouse/<namespace>/<table>/``, inserts rows ``0..rows-1`` and
deletes a subset — committing the deletes as ``deletion-vector-v1`` blobs in
Puffin files, which is verified before the fixture returns (without
verification a copy-on-write fallback would silently test nothing).

ClickHouse then reads the same table through any access form:

* ``icebergS3`` / ``icebergS3Cluster`` table functions (``read_result``),
* the ``Iceberg`` table engine (``engine_table``),
* a ``DataLakeCatalog`` database over the same REST catalog Spark writes
  through (``catalog_database``).
"""

import io

import pyarrow.parquet as pq

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import iceberg.tests.steps.spark as spark
import iceberg.tests.steps.metrics as metrics
import iceberg.tests.steps.icebergS3 as icebergS3
import iceberg.tests.steps.iceberg_table_engine as iceberg_table_engine
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from iceberg.tests.deletion_vectors.steps import s3_objects
from iceberg.tests.deletion_vectors.steps import manifest as manifest_steps

CLUSTER_NAME = "replicated_cluster"

REST_CATALOG_URL = "http://rest:8181"
REST_WAREHOUSE = "s3://warehouse"

PUFFIN_PROFILE_EVENTS = (
    "PuffinFilesRead",
    "PuffinFileReadMicroseconds",
    "PuffinFilesCacheHits",
    "PuffinFilesCacheMisses",
    "PuffinFilesCacheWeightLost",
)


class DVTable:
    """Location info of one Spark-written Iceberg table."""

    def __init__(self, namespace, table_name):
        self.namespace = namespace
        self.table_name = table_name

    @property
    def s3_url(self):
        """Endpoint the ClickHouse nodes use to read the table."""
        return f"{s3_objects.S3_NETWORK_ENDPOINT}/{s3_objects.WAREHOUSE_BUCKET}/{self.namespace}/{self.table_name}"

    @property
    def prefix(self):
        return s3_objects.table_prefix(self.namespace, self.table_name)

    def sql_expr(self, test=None):
        """``icebergS3(...)`` expression usable as a FROM clause."""
        test = test or current()
        return (
            f"icebergS3('{self.s3_url}', "
            f"'{test.context.minio_root_user}', "
            f"'{test.context.minio_root_password}')"
        )

    def __repr__(self):
        return f"DVTable({self.namespace}.{self.table_name})"


def expected_ids(rows, deleted_ids):
    """Surviving ids after deleting *deleted_ids* from ``0..rows-1``."""
    deleted = set(deleted_ids)
    return [i for i in range(rows) if i not in deleted]


def insert_range_statement(rows, data_expr="concat('row-', CAST(id AS STRING))"):
    """Spark INSERT of rows ``(id, data)`` for id in ``0..rows-1``.

    COALESCE(1) keeps the whole INSERT in one write task so it produces
    exactly one data file — scenarios assert data-file counts and craft
    vectors against a single file's row order."""
    return (
        f"INSERT INTO {{table}} SELECT /*+ COALESCE(1) */ id, {data_expr} "
        f"FROM range({rows})"
    )


@TestStep(Given)
def table_with_deletion_vectors(
    self,
    rows=100,
    delete_condition="id % 10 = 0",
    columns="id BIGINT, data STRING",
    partitioned_by=None,
    extra_properties=None,
    setup_statements=None,
    verify_puffin=True,
):
    """Create the canonical DV fixture table.

    Args:
        rows: rows inserted as ``(id, 'row-<id>')`` for id in 0..rows-1.
            0 skips the insert (callers provide their own setup).
        delete_condition: Spark DELETE predicate committed after the insert;
            None skips the delete.
        setup_statements: replaces the default insert+delete entirely
            (``{table}`` placeholders are substituted).
        verify_puffin: assert at least one ``*.puffin`` object exists.

    Returns a :class:`DVTable`.
    """
    properties = dict(spark.MOR_V3_TBLPROPERTIES)
    properties.update(extra_properties or {})

    if setup_statements is None:
        setup_statements = []
        if rows:
            setup_statements.append(insert_range_statement(rows))
        if delete_condition is not None:
            setup_statements.append(
                f"DELETE FROM {{table}} WHERE {delete_condition}"
            )

    namespace, table_name = spark.create_table(
        columns=columns,
        partitioned_by=partitioned_by,
        properties=properties,
        setup_statements=setup_statements,
    )

    if verify_puffin:
        with By("verifying a Puffin file exists under the table location"):
            s3_objects.assert_puffin_exists(
                namespace=namespace, table_name=table_name
            )
        with And("verifying the current snapshot has a live vector entry"):
            # object existence alone can be historical (older snapshots
            # retain their files) — the current snapshot must reference one
            dv_entries = manifest_steps.find_dv_entries(namespace, table_name)
            assert dv_entries, (
                "no live deletion-vector entry in the current snapshot"
            )

    return DVTable(namespace, table_name)


@TestStep(Then)
def assert_data_file_count(self, table, count):
    """The current snapshot holds exactly *count* live data files —
    guards position-based expectations against writer layout changes."""
    files = manifest_steps.live_data_files(table.namespace, table.table_name)
    assert len(files) == count, error(
        f"expected {count} live data file(s), found {len(files)}: "
        f"{[f['file_path'] for f in files]}"
    )
    return files


def _parquet_metadata(data_file):
    """Parquet footer metadata of one live data file."""
    return pq.ParquetFile(
        io.BytesIO(s3_objects.get_object_bytes(data_file["file_path"]))
    ).metadata


@TestStep(Then)
def assert_min_row_groups(self, table, min_row_groups):
    """Every live Parquet data file of the table has at least
    *min_row_groups* row groups — so row-group-boundary scenarios really
    exercise multi-row-group files."""
    files = manifest_steps.live_data_files(table.namespace, table.table_name)
    for data_file in files:
        metadata = _parquet_metadata(data_file)
        assert metadata.num_row_groups >= min_row_groups, error(
            f"{data_file['file_path']} has {metadata.num_row_groups} "
            f"row group(s), expected at least {min_row_groups}"
        )


def _single_live_data_file(table):
    files = manifest_steps.live_data_files(table.namespace, table.table_name)
    assert len(files) == 1, (
        f"expected exactly one live data file, found {len(files)}"
    )
    return files[0]


@TestStep(Then)
def parquet_row_group_sizes(self, table):
    """Row counts of every row group of the table's single live data file —
    for deriving the actual absolute positions of row-group boundaries."""
    metadata = _parquet_metadata(_single_live_data_file(table))
    return [
        metadata.row_group(index).num_rows
        for index in range(metadata.num_row_groups)
    ]


@TestStep(Then)
def parquet_column_values(self, table, column="id"):
    """Values of *column* of the table's single live data file in physical
    row order — maps deletion-vector positions to the actual row values,
    without assuming the writer stored rows in any particular order."""
    data_file = _single_live_data_file(table)
    parquet = pq.ParquetFile(
        io.BytesIO(s3_objects.get_object_bytes(data_file["file_path"]))
    )
    return parquet.read(columns=[column]).column(column).to_pylist()


@TestStep(Then)
def read_result(
    self,
    table,
    columns="*",
    where_clause=None,
    order_by=None,
    group_by=None,
    node=None,
    log_comment=None,
    exitcode=None,
    message=None,
    settings=None,
    cluster=False,
    **extra_kwargs,
):
    """Read the table with icebergS3 (or icebergS3Cluster) using the suite
    MinIO credentials. Extra keyword arguments (e.g.
    ``use_iceberg_partition_pruning``) are forwarded to the shared read
    step."""
    kwargs = dict(
        storage_endpoint=table.s3_url,
        s3_access_key_id=self.context.minio_root_user,
        s3_secret_access_key=self.context.minio_root_password,
        columns=columns,
        where_clause=where_clause,
        order_by=order_by,
        group_by=group_by,
        node=node,
        log_comment=log_comment,
        exitcode=exitcode,
        message=message,
        settings=settings,
        **extra_kwargs,
    )
    if cluster:
        return icebergS3.read_data_with_icebergS3Cluster_table_function(
            cluster_name=CLUSTER_NAME, **kwargs
        )
    return icebergS3.read_data_with_icebergS3_table_function(**kwargs)


@TestStep(Then)
def select_ids(self, table, node=None, settings=None, cluster=False, where_clause=None):
    """Ids visible in the table, ordered."""
    result = read_result(
        table=table,
        columns="id",
        order_by="id",
        node=node,
        settings=settings,
        cluster=cluster,
        where_clause=where_clause,
    )
    return [int(line) for line in result.output.split() if line.strip()]


@TestStep(Then)
def count_rows(self, table, node=None, settings=None, cluster=False, log_comment=None):
    """count() of the table via the table function."""
    result = read_result(
        table=table,
        columns="count()",
        node=node,
        settings=settings,
        cluster=cluster,
        log_comment=log_comment,
    )
    return int(result.output.strip())


@TestStep(Then)
def assert_visible_ids(self, table, ids, node=None, settings=None, cluster=False):
    """The table exposes exactly *ids* (as an ordered set of id values)."""
    actual = select_ids(
        table=table, node=node, settings=settings, cluster=cluster
    )
    assert actual == sorted(ids), error(
        f"visible ids mismatch: expected {len(ids)} rows, got {len(actual)}; "
        f"missing={sorted(set(ids) - set(actual))[:20]}, "
        f"unexpected={sorted(set(actual) - set(ids))[:20]}"
    )


@TestStep(Given)
def engine_table(self, table, node=None):
    """CREATE TABLE ... ENGINE=Iceberg over the fixture table; returns the
    ClickHouse table name (dropped on cleanup)."""
    return iceberg_table_engine.create_table_with_iceberg_engine(
        url=table.s3_url,
        access_key_id=self.context.minio_root_user,
        secret_access_key=self.context.minio_root_password,
        node=node,
    )


@TestStep(Given)
def catalog_database(self, node=None):
    """DataLakeCatalog database over the REST catalog Spark writes through;
    returns the database name (dropped on cleanup)."""
    return iceberg_engine.create_experimental_iceberg_database_with_rest_catalog(
        s3_access_key_id=self.context.minio_root_user,
        s3_secret_access_key=self.context.minio_root_password,
        rest_catalog_url=REST_CATALOG_URL,
        warehouse=REST_WAREHOUSE,
        storage_endpoint=f"{s3_objects.S3_NETWORK_ENDPOINT}/{s3_objects.WAREHOUSE_BUCKET}",
        auth_header=None,
        node=node,
    )


def catalog_table_expr(database_name, table):
    """FROM-clause name of the fixture table inside a DataLakeCatalog
    database."""
    return f"{database_name}.`{table.namespace}.{table.table_name}`"


@TestStep(Given)
def merge_tree_oracle(
    self,
    rows,
    deleted_ids,
    node=None,
    table_name=None,
    data_expr="concat('row-', toString(number))",
):
    """MergeTree table holding exactly the rows that must survive the
    deletion vector — the comparison oracle for query-semantics scenarios.

    Args:
        data_expr: ClickHouse expression over ``number`` producing the same
            ``data`` values the Spark fixture inserted.
    """
    if node is None:
        node = self.context.node
    if table_name is None:
        table_name = f"dv_oracle_{getuid()}"

    deleted = ", ".join(str(i) for i in deleted_ids) or "-1"
    try:
        node.query(
            f"""
            CREATE TABLE {table_name} (id Int64, data String)
            ENGINE = MergeTree ORDER BY id
            """
        )
        node.query(
            f"INSERT INTO {table_name} "
            f"SELECT number, {data_expr} "
            f"FROM numbers({rows}) WHERE number NOT IN ({deleted})"
        )
        yield table_name

    finally:
        with Finally("drop the oracle table"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")


@TestStep(Then)
def assert_query_error(
    self, query, error_name, message_fragment=None, node=None, settings=None
):
    """The query fails with the given ClickHouse error *name* (e.g.
    ``BAD_ARGUMENTS``, ``ICEBERG_SPECIFICATION_VIOLATION``) and, when given,
    a distinguishing message fragment — a bare failure is not enough, the
    query must fail for the injected reason."""
    if node is None:
        node = self.context.node

    result = node.query(query, settings=settings, no_checks=True)

    assert result.exitcode != 0, error(
        f"query unexpectedly succeeded: {query}\noutput: {result.output[:2000]}"
    )
    assert error_name in result.output, error(
        f"expected error {error_name}, got:\n{result.output[:4000]}"
    )
    if message_fragment is not None:
        assert message_fragment in result.output, error(
            f"expected message fragment {message_fragment!r} in:\n"
            f"{result.output[:4000]}"
        )
    return result


@TestStep(Then)
def assert_table_read_fails(
    self, table, error_name, message_fragment=None, node=None, log_comment=None
):
    """Reading a (corrupted) table fails with the given error name and
    message fragment. Metadata caches are dropped first so the rewritten
    manifest chain is actually re-read from storage."""
    drop_iceberg_metadata_cache()
    drop_puffin_cache()

    settings = [("use_iceberg_metadata_files_cache", "0")]
    if log_comment:
        settings.append(("log_comment", log_comment))

    return assert_query_error(
        query=f"SELECT * FROM {table.sql_expr()} FORMAT Null",
        error_name=error_name,
        message_fragment=message_fragment,
        node=node,
        settings=settings,
    )


@TestStep(Then)
def get_puffin_events(self, log_comment, node=None):
    """All Puffin profile events of the queries tagged *log_comment*."""
    return {
        event: metrics.get_profile_event(
            event=event, log_comment=log_comment, node=node
        )
        for event in PUFFIN_PROFILE_EVENTS
    }


@TestStep(Then)
def get_profile_event_of_failed_query(self, event, log_comment, node=None):
    """Profile event total for a query that failed — failed queries never
    reach ``QueryFinish``, so read the ``ExceptionWhileProcessing`` (or
    ``ExceptionBeforeStart``) query_log entry instead."""
    if node is None:
        node = self.context.node

    for retry in retries(count=10, delay=1):
        with retry:
            node.query("SYSTEM FLUSH LOGS")
            count = node.query(
                f"""
                SELECT count() FROM system.query_log
                WHERE log_comment = '{log_comment}'
                AND type IN ('ExceptionWhileProcessing', 'ExceptionBeforeStart')
                """
            )
            assert int(count.output) > 0, "failed query not in query_log yet"

    result = node.query(
        f"""
        SELECT sum(ProfileEvents['{event}']) FROM system.query_log
        WHERE log_comment = '{log_comment}'
        AND type IN ('ExceptionWhileProcessing', 'ExceptionBeforeStart')
        FORMAT TabSeparated
        """
    )
    return int(result.output.strip() or 0)


@TestStep(When)
def drop_puffin_cache(self, node=None):
    """SYSTEM DROP PUFFIN FILES CACHE on one node or the whole cluster."""
    nodes = [node] if node else self.context.nodes
    for n in nodes:
        n.query("SYSTEM DROP PUFFIN FILES CACHE")


@TestStep(When)
def drop_iceberg_metadata_cache(self, node=None):
    """Drop the Iceberg metadata files cache so a corrupted-in-place
    manifest chain is re-read from storage."""
    nodes = [node] if node else self.context.nodes
    for n in nodes:
        n.query("SYSTEM DROP ICEBERG METADATA CACHE")


def unique_log_comment(prefix="dv"):
    """Unique log_comment for per-query profile-event accounting."""
    return f"{prefix}_{getuid()}"
