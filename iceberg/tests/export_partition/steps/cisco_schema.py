"""Cisco DNS-shaped schema for export casting tests (PR 1779).

Based on ``antalya-hackathon/schema_sample.sql``. The source table keeps the
production MergeTree column types; the Iceberg destination uses castable
Iceberg-native equivalents (see :data:`CISCO_DEST_COLUMNS`).
"""

import textwrap

CISCO_SOURCE_COLUMNS = """
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

# Iceberg-legal destination types reachable from the source via
# ``canBeSafelyCast`` / INSERT SELECT (PR 1779 export parity target).
CISCO_DEST_COLUMNS = """
    `eventDate` Date,
    `timestamp` UInt32,
    `version` String,
    `remoteIP` String,
    `serverIP` String,
    `handling` String,
    `mspOrganizationId` UInt64,
    `originIds` Array(UInt64),
    `organizationIds` Array(UInt64),
    `originTypes` Array(UInt32),
    `qname` String,
    `threatTypes` Array(String),
    `threats` Array(String),
    `noisyDomain` Int32,
    `qtype` Int32,
    `rcode` Int32,
    `blockedCategories` Array(UInt32),
    `allCategories` Array(UInt32),
    `flags` Array(UInt32),
    `publicSuffix` String,
    `host` String,
    `retention` UInt32,
    `clientReportingId_lengthPrefix` Int32,
    `clientReportingId_schemaId` Int32,
    `clientReportingId_vendorId` UInt32,
    `clientReportingId_deviceClassId` UInt32,
    `clientReportingId_componentClassId` UInt64,
    `clientReportingId_deviceSpecifier` String,
    `ruleId` Nullable(UInt64),
    `destinationCountries` Array(String),
    `logType` Nullable(String),
    `kafkaPartition` Int32,
    `kafkaOffset` UInt64,
    `kafkaTopic` String,
    `kafkaCluster` String
"""

CISCO_PARTITION_BY = "(eventDate, retention)"

CISCO_EVENT_DATE = "2025-08-01"
CISCO_RETENTION = 30

CISCO_INSERT_SELECT = textwrap.dedent(
    f"""
    SELECT
        toDate('{CISCO_EVENT_DATE}'),
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

CISCO_WHERE = (
    f"eventDate = toDate('{CISCO_EVENT_DATE}') AND retention = {CISCO_RETENTION}"
)

# LowCardinality/Enum unwrap and narrow integer promotion are lossy under
# PR 1779's export cast gate; match INSERT SELECT parity with explicit opt-in.
CISCO_EXPORT_SETTINGS = [("export_merge_tree_part_allow_lossy_cast", 1)]
