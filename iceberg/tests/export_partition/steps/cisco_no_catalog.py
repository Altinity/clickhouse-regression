"""No-catalog DNS / Cisco-shaped export: S3 hive destination + Hybrid read-back.

Mirrors the manual flow in ``test-export-mtree/no-catalog.sql``: types that
``getIcebergType`` rejects (``UInt8``, ``LowCardinality(String)``, ``Enum8``,
``Array(LowCardinality(String))``) are exported to an ``ENGINE = S3`` table
with hive partitioning, then read through a Hybrid table whose cold segment is
that S3 table — not through ``IcebergS3`` DDL.
"""

import textwrap

from testflows.core import *

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import create_replicated_mergetree
from iceberg.tests.export_partition.steps.iceberg_destination import (
    DEFAULT_S3_ENDPOINT_HOST,
    DEFAULT_S3_WAREHOUSE_BUCKET,
)


# Column set covers every distinct ClickHouse type in the Cisco DNS schema
# (see test-export-mtree/no-catalog.sql) without copying alias/DEFAULT columns.
CISCO_SCHEMA_COLUMNS = """
    `eventDate` Date,
    `timestamp` UInt32,
    `version` LowCardinality(String),
    `remoteIP` String,
    `serverIP` LowCardinality(String),
    `handling` LowCardinality(String),
    `mspOrganizationId` UInt64,
    `originIds` Array(UInt64),
    `organizationIds` Array(UInt64),
    `originTypes` Array(UInt32),
    `qname` String,
    `threatTypes` Array(LowCardinality(String)),
    `threats` Array(LowCardinality(String)),
    `noisyDomain` UInt8,
    `qtype` UInt16,
    `rcode` UInt16,
    `blockedCategories` Array(UInt32),
    `allCategories` Array(UInt32),
    `flags` Array(UInt32),
    `publicSuffix` LowCardinality(String),
    `host` LowCardinality(String),
    `retention` UInt32,
    `clientReportingId_lengthPrefix` UInt8,
    `clientReportingId_schemaId` UInt16,
    `clientReportingId_vendorId` UInt32,
    `clientReportingId_deviceClassId` UInt32,
    `clientReportingId_componentClassId` UInt64,
    `clientReportingId_deviceSpecifier` String,
    `ruleId` Nullable(UInt64),
    `destinationCountries` Array(String),
    `logType` Nullable(Enum8('CSA' = 1, 'UMBRELLA' = 2)),
    `kafkaPartition` UInt8,
    `kafkaOffset` UInt64,
    `kafkaTopic` LowCardinality(String),
    `kafkaCluster` LowCardinality(String)
"""

CISCO_PARTITION_BY = "(eventDate, retention)"

# Cold rows use this date; hot Hybrid predicate keeps them on the S3 segment.
CISCO_COLD_EVENT_DATE = "2025-08-01"
CISCO_RETENTION = 30
CISCO_HOT_WATERMARK = "2025-09-13"

CISCO_INSERT_SELECT = textwrap.dedent(
    f"""
    SELECT
        toDate('{CISCO_COLD_EVENT_DATE}'),
        toUInt32(1000 + number),
        'v1',
        '10.0.0.1',
        '10.0.0.3',
        'A',
        toUInt64(number),
        [toUInt64(number)],
        [toUInt64(number)],
        [toUInt32(1)],
        concat('host-', toString(number), '.example.com'),
        CAST([], 'Array(LowCardinality(String))'),
        CAST([], 'Array(LowCardinality(String))'),
        toUInt8(number % 2),
        toUInt16(1),
        toUInt16(0),
        CAST([], 'Array(UInt32)'),
        CAST([], 'Array(UInt32)'),
        CAST([], 'Array(UInt32)'),
        '',
        '',
        toUInt32({CISCO_RETENTION}),
        toUInt8(0),
        toUInt16(0),
        toUInt32(0),
        toUInt32(0),
        toUInt64(0),
        '',
        NULL,
        CAST([], 'Array(String)'),
        if(number = 0, CAST('CSA', 'Enum8(\\'CSA\\' = 1, \\'UMBRELLA\\' = 2)'), NULL),
        toUInt8(0),
        toUInt64(number),
        '',
        ''
    FROM numbers(3)
    """
).strip()


@TestStep(Given)
def create_cisco_s3_cold_destination(
    self,
    minio_root_user,
    minio_root_password,
    table_name=None,
    node=None,
    cleanup=True,
):
    """``ENGINE = S3(...)`` hive export target (no Iceberg metadata)."""
    if node is None:
        node = self.context.node
    if table_name is None:
        table_name = f"cisco_cold_{getuid()}"

    uid = getuid()
    collection = f"cisco_s3_cold_{uid}"
    # Path under the ``warehouse`` bucket (same layout as ``iceberg_conf``).
    url = f"{DEFAULT_S3_ENDPOINT_HOST}/{DEFAULT_S3_WAREHOUSE_BUCKET}/cisco_no_catalog/{uid}/cold/"

    node.query(
        f"""
        CREATE NAMED COLLECTION {collection} AS
            url = '{url}',
            access_key_id = '{minio_root_user}',
            secret_access_key = '{minio_root_password}',
            format = 'Parquet',
            partition_strategy = 'hive',
            partition_columns_in_data_file = 1
        """
    )

    node.query(
        f"""
        CREATE TABLE {table_name} ({CISCO_SCHEMA_COLUMNS})
        ENGINE = S3({collection})
        PARTITION BY {CISCO_PARTITION_BY}
        """
    )

    try:
        yield {
            "cold_table": table_name,
            "named_collection": collection,
            "url": url,
        }
    finally:
        if cleanup:
            with Finally(f"drop S3 cold table {table_name}"):
                node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")
            with Finally(f"drop named collection {collection}"):
                node.query(f"DROP NAMED COLLECTION IF EXISTS {collection}")


@TestStep(Given)
def create_cisco_hybrid_read_table(
    self,
    hot_table,
    cold_table,
    hybrid_table=None,
    node=None,
    cleanup=True,
):
    """Hybrid table: empty hot MergeTree + cold ``ENGINE = S3`` segment."""
    if node is None:
        node = self.context.node
    if hybrid_table is None:
        hybrid_table = f"cisco_hybrid_{getuid()}"

    hot_segment = f"remote('localhost', currentDatabase(), {hot_table})"
    hot_predicate = f"eventDate >= '{CISCO_HOT_WATERMARK}'"
    cold_predicate = f"eventDate < '{CISCO_HOT_WATERMARK}'"

    node.query(
        f"""
        SET allow_experimental_hybrid_table = 1;
        CREATE TABLE {hybrid_table} ({CISCO_SCHEMA_COLUMNS})
        ENGINE = Hybrid(
            {hot_segment}, {hot_predicate},
            {cold_table}, {cold_predicate}
        )
        """
    )

    try:
        yield hybrid_table
    finally:
        if cleanup:
            with Finally(f"drop hybrid table {hybrid_table}"):
                node.query(f"DROP TABLE IF EXISTS {hybrid_table} SYNC")


@TestStep(Given)
def create_cisco_no_catalog_fixture(
    self,
    minio_root_user,
    minio_root_password,
    node=None,
):
    """Source RMT, empty hot stub, S3 cold destination — yields a fixture dict."""
    if node is None:
        node = self.context.node

    source_table = f"cisco_src_{getuid()}"
    hot_table = f"cisco_hot_{getuid()}"

    create_replicated_mergetree(
        table_name=source_table,
        columns=CISCO_SCHEMA_COLUMNS,
        partition_by=CISCO_PARTITION_BY,
        order_by="(mspOrganizationId, qname, timestamp)",
        node=node,
        cleanup=False,
    )
    create_replicated_mergetree(
        table_name=hot_table,
        columns=CISCO_SCHEMA_COLUMNS,
        partition_by=CISCO_PARTITION_BY,
        order_by="(mspOrganizationId, qname, timestamp)",
        node=node,
        cleanup=False,
    )

    cold = create_cisco_s3_cold_destination(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        node=node,
        cleanup=False,
    )

    try:
        yield {
            "source_table": source_table,
            "hot_table": hot_table,
            "cold_table": cold["cold_table"],
            "cold": cold,
        }
    finally:
        with Finally(f"drop cisco source {source_table}"):
            node.query(f"DROP TABLE IF EXISTS {source_table} SYNC")
        with Finally(f"drop cisco hot stub {hot_table}"):
            node.query(f"DROP TABLE IF EXISTS {hot_table} SYNC")
        with Finally(f"drop cisco cold S3 table {cold['cold_table']}"):
            node.query(f"DROP TABLE IF EXISTS {cold['cold_table']} SYNC")
        with Finally(f"drop cisco cold named collection {cold['named_collection']}"):
            node.query(f"DROP NAMED COLLECTION IF EXISTS {cold['named_collection']}")
