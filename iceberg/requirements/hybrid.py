# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_ClickHouse_Hybrid_Create = Requirement(
    name="RQ.ClickHouse.Hybrid.Create",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support creating Hybrid tables with the following SQL syntax:\n"
        "\n"
        "```sql\n"
        "CREATE TABLE [IF NOT EXISTS] [db.]table_name\n"
        "(\n"
        "    column1 type1,\n"
        "    column2 type2,\n"
        "    ...\n"
        ")\n"
        "ENGINE = Hybrid(table_function_1, predicate_1 [, table_function_2, predicate_2 ...])\n"
        "```\n"
        "\n"
        "[ClickHouse] SHALL require at least one `table_function, predicate` pair. Additional sources are appended as further `table_function, predicate` pairs.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.1",
)

RQ_ClickHouse_Hybrid_FirstSegment = Requirement(
    name="RQ.ClickHouse.Hybrid.FirstSegment",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL require `table_function_1` to be a table function that instantiates underlying Distributed storage, such as:\n"
        "* `remote`\n"
        "* `remoteSecure`\n"
        "* `cluster`\n"
        "* `clusterAllReplicas`\n"
        "\n"
        "The first table function SHALL also be the target of `INSERT` statements.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.2",
)

RQ_ClickHouse_Hybrid_AdditionalSegments = Requirement(
    name="RQ.ClickHouse.Hybrid.AdditionalSegments",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL accept subsequent segments as either:\n"
        "* A valid table function (for example `remote`, `remoteSecure`, `cluster`, `clusterAllReplicas`, `s3`, `s3Cluster`, `icebergCluster`), or\n"
        "* A fully qualified table name (`database.table`)\n"
        "\n"
        "Each `predicate_n` SHALL be an expression evaluated on the table columns. The engine SHALL add it to the segment’s query with an additional `AND` (for example `event_date >= '2025-09-01'` or `id BETWEEN 10 AND 15`).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.3",
)

RQ_ClickHouse_Hybrid_SchemaInference = Requirement(
    name="RQ.ClickHouse.Hybrid.SchemaInference",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support omitting the explicit column list:\n"
        "\n"
        "```sql\n"
        "CREATE TABLE [IF NOT EXISTS] [db.]table_name\n"
        "ENGINE = Hybrid(table_function_1, predicate_1 [, table_function_n, predicate_n ...])\n"
        "```\n"
        "\n"
        "In this case, [ClickHouse] SHALL detect columns and types from the first table function (including `CREATE … AS source_table` style definitions).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.4",
)

RQ_ClickHouse_Hybrid_ExperimentalGate = Requirement(
    name="RQ.ClickHouse.Hybrid.ExperimentalGate",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The Hybrid engine is experimental. [ClickHouse] SHALL gate Hybrid DDL behind `allow_experimental_hybrid_table`. When the setting is disabled, creating a Hybrid table SHALL fail. When enabled (session or profile), Hybrid DDL SHALL succeed:\n"
        "\n"
        "```sql\n"
        "SET allow_experimental_hybrid_table = 1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.5",
)

RQ_ClickHouse_Hybrid_AnalyzerRequired = Requirement(
    name="RQ.ClickHouse.Hybrid.AnalyzerRequired",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Hybrid queries SHALL be run with `enable_analyzer = 1` (formerly `allow_experimental_analyzer = 1`). The Hybrid regression suite enables the analyzer in the default profile and query settings. Behavior with `enable_analyzer = 0` is out of scope.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.6",
)

RQ_ClickHouse_Hybrid_Watermark_Exclusive = Requirement(
    name="RQ.ClickHouse.Hybrid.Watermark.Exclusive",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support mutually exclusive segment predicates such that each logical row is read from exactly one segment, and Hybrid query results match an exclusive `UNION ALL` reference over the same segments and predicates (no duplicates, no gaps for rows present in the covered dataset).\n"
        "\n"
        "Example of mutually exclusive predicates:\n"
        "* `date >= '2025-01-01'` — first segment\n"
        "* `date < '2025-01-01'` — second segment\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

RQ_ClickHouse_Hybrid_Watermark_Overlap = Requirement(
    name="RQ.ClickHouse.Hybrid.Watermark.Overlap",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow overlapping predicates. A single row may match multiple predicates and be served from multiple segments, which MAY produce duplicate rows in query results relative to a distinct exclusive reference.\n"
        "\n"
        "Example of overlapping predicates (may cause duplicates):\n"
        "* `date >= '2025-01-01'` — first segment\n"
        "* `date >= '2025-01-15'` — second segment\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.2",
)

RQ_ClickHouse_Hybrid_Watermark_Replace = Requirement(
    name="RQ.ClickHouse.Hybrid.Watermark.Replace",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support updating Hybrid watermarks via `CREATE OR REPLACE TABLE` with new static predicates. The replace operation SHALL be atomic: after the statement completes, all queries SHALL see the new watermark with no window of inconsistent routing for the same data range.\n"
        "\n"
        "```sql\n"
        "-- Original watermark at '2025-01-01'\n"
        "CREATE TABLE hybrid_table ENGINE = Hybrid(\n"
        "    remote('hot_cluster', 'db', 'table'), date >= '2025-01-01',\n"
        "    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-01-01'\n"
        ") AS source_table;\n"
        "\n"
        "-- Advance watermark to '2025-02-01' after exporting hot → cold\n"
        "CREATE OR REPLACE TABLE hybrid_table ENGINE = Hybrid(\n"
        "    remote('hot_cluster', 'db', 'table'), date >= '2025-02-01',\n"
        "    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-02-01'\n"
        ") AS source_table;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.3",
)

RQ_ClickHouse_Hybrid_PredicatePruning = Requirement(
    name="RQ.ClickHouse.Hybrid.PredicatePruning",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL prune segments that cannot contribute rows when a query’s `WHERE` clause is exclusive to one watermark band, while still returning results identical to the exclusive reference for that band.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.4",
)

RQ_ClickHouse_Hybrid_Insert_FirstSegmentOnly = Requirement(
    name="RQ.ClickHouse.Hybrid.Insert.FirstSegmentOnly",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL forward every `INSERT INTO` a Hybrid table exclusively to the first segment, including rows whose values would match a later segment’s predicate.\n"
        "\n"
        "This design:\n"
        "* Supports double-write scenarios where data is written to hot storage and later exported to cold\n"
        "* Enables cache-layer setups where writes go to a fast layer\n"
        "* Avoids ambiguous write targets when multiple segments could match\n"
        "\n"
        "```sql\n"
        "-- All inserts go to the first (hot) segment\n"
        "INSERT INTO hybrid VALUES (...);\n"
        "\n"
        "-- For multi-destination writes, use explicit inserts:\n"
        "INSERT INTO hot_table VALUES (...);\n"
        "INSERT INTO cold_table VALUES (...);\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.1",
)

RQ_ClickHouse_Hybrid_AutoCast = Requirement(
    name="RQ.ClickHouse.Hybrid.AutoCast",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When `hybrid_table_auto_cast_columns = 1` is enabled (requires `enable_analyzer = 1`), [ClickHouse] SHALL insert the necessary `CAST` operations so every shard / segment receives the schema defined by the Hybrid table header, preventing `CANNOT_CONVERT_TYPE` / `NO_COMMON_TYPE` failures for modest type seams.\n"
        "\n"
        "Manual casts in user SQL remain allowed but MAY result in double-casting.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_ClickHouse_Hybrid_TypeSeams = Requirement(
    name="RQ.ClickHouse.Hybrid.TypeSeams",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "With auto-cast enabled, [ClickHouse] SHALL support Hybrid queries across at least the following seams when headers are declared appropriately:\n"
        "* Unsigned integer vs signed counterpart (for example `UInt64` ↔ `Int64`, `UInt32` ↔ `Int32`) on MergeTree↔MergeTree and MergeTree↔Iceberg\n"
        "* `FixedString(N)` ↔ `String`\n"
        "* Aggregate paths such as `uniq` across those seams\n"
        "\n"
        "When auto-cast is disabled, [ClickHouse] MAY reject incompatible seams.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.2",
)

RQ_ClickHouse_Hybrid_QueryShapes = Requirement(
    name="RQ.ClickHouse.Hybrid.QueryShapes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support core analytic query shapes on Hybrid tables, including:\n"
        "* Filtered `SELECT`\n"
        "* `GROUP BY` aggregates (`count`, `sum`, `min`, `max`, and similar)\n"
        "* `ORDER BY` / `LIMIT`\n"
        "* Multi-segment scans that combine hot and cold predicates\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.1",
)

RQ_ClickHouse_Hybrid_CorrectnessVsUnion = Requirement(
    name="RQ.ClickHouse.Hybrid.CorrectnessVsUnion",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "For mutually exclusive watermarks, [ClickHouse] SHALL return Hybrid results that match an exclusive `UNION ALL` reference constructed from the same segments and predicates (stable fingerprints / aggregates), including under Distributed path settings exercised by the suite.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.2",
)

RQ_ClickHouse_Hybrid_LocalVsRemote = Requirement(
    name="RQ.ClickHouse.Hybrid.LocalVsRemote",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL produce correct Hybrid results for both:\n"
        "* Local execution of subquery plans on the initiator (`prefer_localhost_replica = 1`)\n"
        "* Forcing remote treatment of the local replica (`prefer_localhost_replica = 0`)\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_ClickHouse_Hybrid_SerializeQueryPlan = Requirement(
    name="RQ.ClickHouse.Hybrid.SerializeQueryPlan",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL produce correct Hybrid results when remote work is sent as:\n"
        "* SQL text (`serialize_query_plan = 0`, default), and\n"
        "* A serialized query plan (`serialize_query_plan = 1`)\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.2",
)

RQ_ClickHouse_Hybrid_AggregationStages = Requirement(
    name="RQ.ClickHouse.Hybrid.AggregationStages",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL produce correct Hybrid aggregation results across remote aggregation stages, including:\n"
        "* `complete`\n"
        "* `with_mergeable_state`\n"
        "* `with_mergeable_state_after_aggregation`\n"
        "* `with_mergeable_state_after_aggregation_and_limit`\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.3",
)

RQ_ClickHouse_Hybrid_DistributedOverDistributed = Requirement(
    name="RQ.ClickHouse.Hybrid.DistributedOverDistributed",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hybrid layouts where the first segment reads through a Distributed table (Distributed-over-Distributed), preserving fingerprint equality versus an exclusive reference.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.4",
)

RQ_ClickHouse_Hybrid_Segment_MergeTree = Requirement(
    name="RQ.ClickHouse.Hybrid.Segment.MergeTree",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hybrid segments backed by MergeTree-family tables accessed via `remote` / `cluster` / `clusterAllReplicas`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_ClickHouse_Hybrid_Segment_Iceberg = Requirement(
    name="RQ.ClickHouse.Hybrid.Segment.Iceberg",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hybrid cold (or other) segments backed by Iceberg tables / IcebergS3 destinations with exclusive watermarks and correct query results versus the exclusive reference.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.2",
)

RQ_ClickHouse_Hybrid_Segment_IcebergCatalogs = Requirement(
    name="RQ.ClickHouse.Hybrid.Segment.IcebergCatalogs",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hybrid Iceberg segments under at least the following catalog modes:\n"
        "* No external catalog (IcebergS3 / path-based)\n"
        "* Iceberg REST catalog\n"
        "* Glue catalog\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.3",
)

RQ_ClickHouse_Hybrid_Segment_IcebergCluster = Requirement(
    name="RQ.ClickHouse.Hybrid.Segment.IcebergCluster",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hybrid segments using `icebergCluster(...)`, including settings such as `object_storage_cluster_join_mode = 'local'` where applicable, with correct query results.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.4",
)

RQ_ClickHouse_Hybrid_Segment_S3Parquet = Requirement(
    name="RQ.ClickHouse.Hybrid.Segment.S3Parquet",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hybrid segments backed by `s3(...)` and `s3Cluster(...)` Parquet sources with correct query results versus the exclusive reference.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.5",
)

RQ_ClickHouse_Hybrid_SchemaVariety = Requirement(
    name="RQ.ClickHouse.Hybrid.SchemaVariety",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hybrid correctness for reduced-scale schema variety shapes that stress type mapping, including:\n"
        "* Financial: `Decimal`, `FixedString`, `Enum8`\n"
        "* Telemetry: `LowCardinality`, `DateTime64`, `Map`\n"
        "* Logs: `String`, `Array`\n"
        "* Iceberg-compatible nested types (`DateTime64`, `Array`, `Map`) on MergeTree + Iceberg\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_ClickHouse_Hybrid_SchemaRefresh = Requirement(
    name="RQ.ClickHouse.Hybrid.SchemaRefresh",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "After a segment schema change such as `ADD COLUMN`, [ClickHouse] SHALL allow refreshing the Hybrid table header via `CREATE OR REPLACE` (including `ON CLUSTER` when the left segment is cluster-scoped) so subsequent queries see the updated columns.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.2",
)

RQ_ClickHouse_Hybrid_Topology_SecureCluster = Requirement(
    name="RQ.ClickHouse.Hybrid.Topology.SecureCluster",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hybrid first segments over TLS-secured remote server configurations (secure cluster entries / `remoteSecure` path as configured in the deployment).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.1",
)

RQ_ClickHouse_Hybrid_Topology_ClusterAllReplicas = Requirement(
    name="RQ.ClickHouse.Hybrid.Topology.ClusterAllReplicas",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hybrid segments using `clusterAllReplicas(...)` with correct results versus the exclusive reference.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.2",
)

RQ_ClickHouse_Hybrid_Topology_ThreeSegments = Requirement(
    name="RQ.ClickHouse.Hybrid.Topology.ThreeSegments",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support Hybrid tables with three or more exclusive predicate bands (for example hot / warm / cold) and return results matching the corresponding multi-way exclusive `UNION ALL` reference.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.3",
)

RQ_ClickHouse_Hybrid_Lifecycle_ExportThenWatermark = Requirement(
    name="RQ.ClickHouse.Hybrid.Lifecycle.ExportThenWatermark",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the end-to-end tiered lifecycle:\n"
        "* Hybrid over exportable MergeTree + Iceberg with a static watermark\n"
        "* `EXPORT PARTITION` of cold bands into Iceberg\n"
        "* `CREATE OR REPLACE` advancing the static watermark\n"
        "* Delete of the exported range from MergeTree after the watermark advances\n"
        "\n"
        "with Hybrid results matching the exclusive reference (no gaps, no duplicates for the covered dataset).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.1",
)

RQ_ClickHouse_Hybrid_Lifecycle_OverlapDiscipline = Requirement(
    name="RQ.ClickHouse.Hybrid.Lifecycle.OverlapDiscipline",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL leave a detectable gap (missing newly cold rows) if the watermark is advanced without exporting the newly cold range into the cold segment first.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.2",
)

RQ_ClickHouse_Hybrid_Lifecycle_ReplaceDistributed = Requirement(
    name="RQ.ClickHouse.Hybrid.Lifecycle.ReplaceDistributed",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL allow replacing a Distributed head over local MergeTree with a Hybrid head (`cluster(...)` + Iceberg or equivalent) such that:\n"
        "* Query fingerprints match the prior Distributed baseline under localhost preference settings\n"
        "* `INSERT` continues to land on the local / first-segment storage\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.3",
)

RQ_ClickHouse_Hybrid_Operational_UnreachableCold = Requirement(
    name="RQ.ClickHouse.Hybrid.Operational.UnreachableCold",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the cold Iceberg segment is dropped or otherwise unreachable, [ClickHouse] SHALL still serve queries whose predicates are exclusive to the hot watermark band. Full scans that require the missing cold segment MAY error or return an incomplete set.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.1",
)

RQ_ClickHouse_Hybrid_Operational_ExportLag = Requirement(
    name="RQ.ClickHouse.Hybrid.Operational.ExportLag",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "While the cold Iceberg segment is empty and the static watermark already routes a date band to cold, [ClickHouse] SHALL return only the hot-band rows for full Hybrid scans. After `EXPORT PARTITION` fills that cold band, Hybrid SHALL cover the full exclusive dataset.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.2",
)

RQ_ClickHouse_Hybrid_ExternalReader_Iceberg = Requirement(
    name="RQ.ClickHouse.Hybrid.ExternalReader.Iceberg",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "After cold data has been exported into the Iceberg segment used by Hybrid, an external Iceberg reader (for example PyIceberg) SHALL observe the same cold-band row count as ClickHouse when reading that destination.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="13.1",
)

RQ_ClickHouse_Hybrid_QueryFuzzing = Requirement(
    name="RQ.ClickHouse.Hybrid.QueryFuzzing",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL successfully execute a broad, non-interactive set of Hybrid query shapes (including curated Hybrid SQL and upstream-derived patterns such as windows, `LIMIT BY`, CTEs, and `GLOBAL IN`) against Hybrid topologies that combine MergeTree and Iceberg / `icebergCluster` segments.\n"
        "\n"
        "Known Distributed / Hybrid limitations that are not Hybrid regressions (for example correlated subqueries on remote tables, and Nullable null-map access on some remote Iceberg paths) MAY be excluded until product support exists.\n"
    ),
    link=None,
    level=2,
    num="14.1",
)

SRS_Hybrid_Table_Engine = Specification(
    name="SRS Hybrid Table Engine",
    description=None,
    author=None,
    date=None,
    status=None,
    approved_by=None,
    approved_date=None,
    approved_version=None,
    version=None,
    group=None,
    type=None,
    link=None,
    uid=None,
    parent=None,
    children=None,
    headings=(
        Heading(name="Introduction", level=1, num="1"),
        Heading(name="Engine Definition", level=1, num="2"),
        Heading(name="RQ.ClickHouse.Hybrid.Create", level=2, num="2.1"),
        Heading(name="RQ.ClickHouse.Hybrid.FirstSegment", level=2, num="2.2"),
        Heading(name="RQ.ClickHouse.Hybrid.AdditionalSegments", level=2, num="2.3"),
        Heading(name="RQ.ClickHouse.Hybrid.SchemaInference", level=2, num="2.4"),
        Heading(name="RQ.ClickHouse.Hybrid.ExperimentalGate", level=2, num="2.5"),
        Heading(name="RQ.ClickHouse.Hybrid.AnalyzerRequired", level=2, num="2.6"),
        Heading(name="Segment Predicates (Watermarks)", level=1, num="3"),
        Heading(name="RQ.ClickHouse.Hybrid.Watermark.Exclusive", level=2, num="3.1"),
        Heading(name="RQ.ClickHouse.Hybrid.Watermark.Overlap", level=2, num="3.2"),
        Heading(name="RQ.ClickHouse.Hybrid.Watermark.Replace", level=2, num="3.3"),
        Heading(name="RQ.ClickHouse.Hybrid.PredicatePruning", level=2, num="3.4"),
        Heading(name="INSERT Behavior", level=1, num="4"),
        Heading(
            name="RQ.ClickHouse.Hybrid.Insert.FirstSegmentOnly", level=2, num="4.1"
        ),
        Heading(name="Automatic Type Alignment", level=1, num="5"),
        Heading(name="RQ.ClickHouse.Hybrid.AutoCast", level=2, num="5.1"),
        Heading(name="RQ.ClickHouse.Hybrid.TypeSeams", level=2, num="5.2"),
        Heading(name="Query Semantics", level=1, num="6"),
        Heading(name="RQ.ClickHouse.Hybrid.QueryShapes", level=2, num="6.1"),
        Heading(name="RQ.ClickHouse.Hybrid.CorrectnessVsUnion", level=2, num="6.2"),
        Heading(name="Distributed Execution Paths", level=1, num="7"),
        Heading(name="RQ.ClickHouse.Hybrid.LocalVsRemote", level=2, num="7.1"),
        Heading(name="RQ.ClickHouse.Hybrid.SerializeQueryPlan", level=2, num="7.2"),
        Heading(name="RQ.ClickHouse.Hybrid.AggregationStages", level=2, num="7.3"),
        Heading(
            name="RQ.ClickHouse.Hybrid.DistributedOverDistributed", level=2, num="7.4"
        ),
        Heading(name="Segment Storage Types", level=1, num="8"),
        Heading(name="RQ.ClickHouse.Hybrid.Segment.MergeTree", level=2, num="8.1"),
        Heading(name="RQ.ClickHouse.Hybrid.Segment.Iceberg", level=2, num="8.2"),
        Heading(
            name="RQ.ClickHouse.Hybrid.Segment.IcebergCatalogs", level=2, num="8.3"
        ),
        Heading(name="RQ.ClickHouse.Hybrid.Segment.IcebergCluster", level=2, num="8.4"),
        Heading(name="RQ.ClickHouse.Hybrid.Segment.S3Parquet", level=2, num="8.5"),
        Heading(name="Schema Variety and Refresh", level=1, num="9"),
        Heading(name="RQ.ClickHouse.Hybrid.SchemaVariety", level=2, num="9.1"),
        Heading(name="RQ.ClickHouse.Hybrid.SchemaRefresh", level=2, num="9.2"),
        Heading(name="Topology", level=1, num="10"),
        Heading(
            name="RQ.ClickHouse.Hybrid.Topology.SecureCluster", level=2, num="10.1"
        ),
        Heading(
            name="RQ.ClickHouse.Hybrid.Topology.ClusterAllReplicas", level=2, num="10.2"
        ),
        Heading(
            name="RQ.ClickHouse.Hybrid.Topology.ThreeSegments", level=2, num="10.3"
        ),
        Heading(name="Lifecycle and Tiered Storage", level=1, num="11"),
        Heading(
            name="RQ.ClickHouse.Hybrid.Lifecycle.ExportThenWatermark",
            level=2,
            num="11.1",
        ),
        Heading(
            name="RQ.ClickHouse.Hybrid.Lifecycle.OverlapDiscipline", level=2, num="11.2"
        ),
        Heading(
            name="RQ.ClickHouse.Hybrid.Lifecycle.ReplaceDistributed",
            level=2,
            num="11.3",
        ),
        Heading(name="Operational Behavior", level=1, num="12"),
        Heading(
            name="RQ.ClickHouse.Hybrid.Operational.UnreachableCold", level=2, num="12.1"
        ),
        Heading(name="RQ.ClickHouse.Hybrid.Operational.ExportLag", level=2, num="12.2"),
        Heading(name="External Readers", level=1, num="13"),
        Heading(
            name="RQ.ClickHouse.Hybrid.ExternalReader.Iceberg", level=2, num="13.1"
        ),
        Heading(name="Query Fuzzing Coverage", level=1, num="14"),
        Heading(name="RQ.ClickHouse.Hybrid.QueryFuzzing", level=2, num="14.1"),
    ),
    requirements=(
        RQ_ClickHouse_Hybrid_Create,
        RQ_ClickHouse_Hybrid_FirstSegment,
        RQ_ClickHouse_Hybrid_AdditionalSegments,
        RQ_ClickHouse_Hybrid_SchemaInference,
        RQ_ClickHouse_Hybrid_ExperimentalGate,
        RQ_ClickHouse_Hybrid_AnalyzerRequired,
        RQ_ClickHouse_Hybrid_Watermark_Exclusive,
        RQ_ClickHouse_Hybrid_Watermark_Overlap,
        RQ_ClickHouse_Hybrid_Watermark_Replace,
        RQ_ClickHouse_Hybrid_PredicatePruning,
        RQ_ClickHouse_Hybrid_Insert_FirstSegmentOnly,
        RQ_ClickHouse_Hybrid_AutoCast,
        RQ_ClickHouse_Hybrid_TypeSeams,
        RQ_ClickHouse_Hybrid_QueryShapes,
        RQ_ClickHouse_Hybrid_CorrectnessVsUnion,
        RQ_ClickHouse_Hybrid_LocalVsRemote,
        RQ_ClickHouse_Hybrid_SerializeQueryPlan,
        RQ_ClickHouse_Hybrid_AggregationStages,
        RQ_ClickHouse_Hybrid_DistributedOverDistributed,
        RQ_ClickHouse_Hybrid_Segment_MergeTree,
        RQ_ClickHouse_Hybrid_Segment_Iceberg,
        RQ_ClickHouse_Hybrid_Segment_IcebergCatalogs,
        RQ_ClickHouse_Hybrid_Segment_IcebergCluster,
        RQ_ClickHouse_Hybrid_Segment_S3Parquet,
        RQ_ClickHouse_Hybrid_SchemaVariety,
        RQ_ClickHouse_Hybrid_SchemaRefresh,
        RQ_ClickHouse_Hybrid_Topology_SecureCluster,
        RQ_ClickHouse_Hybrid_Topology_ClusterAllReplicas,
        RQ_ClickHouse_Hybrid_Topology_ThreeSegments,
        RQ_ClickHouse_Hybrid_Lifecycle_ExportThenWatermark,
        RQ_ClickHouse_Hybrid_Lifecycle_OverlapDiscipline,
        RQ_ClickHouse_Hybrid_Lifecycle_ReplaceDistributed,
        RQ_ClickHouse_Hybrid_Operational_UnreachableCold,
        RQ_ClickHouse_Hybrid_Operational_ExportLag,
        RQ_ClickHouse_Hybrid_ExternalReader_Iceberg,
        RQ_ClickHouse_Hybrid_QueryFuzzing,
    ),
    content=r"""
# SRS Hybrid Table Engine
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
* 2 [Engine Definition](#engine-definition)
    * 2.1 [RQ.ClickHouse.Hybrid.Create](#rqclickhousehybridcreate)
    * 2.2 [RQ.ClickHouse.Hybrid.FirstSegment](#rqclickhousehybridfirstsegment)
    * 2.3 [RQ.ClickHouse.Hybrid.AdditionalSegments](#rqclickhousehybridadditionalsegments)
    * 2.4 [RQ.ClickHouse.Hybrid.SchemaInference](#rqclickhousehybridschemainference)
    * 2.5 [RQ.ClickHouse.Hybrid.ExperimentalGate](#rqclickhousehybridexperimentalgate)
    * 2.6 [RQ.ClickHouse.Hybrid.AnalyzerRequired](#rqclickhousehybridanalyzerrequired)
* 3 [Segment Predicates (Watermarks)](#segment-predicates-watermarks)
    * 3.1 [RQ.ClickHouse.Hybrid.Watermark.Exclusive](#rqclickhousehybridwatermarkexclusive)
    * 3.2 [RQ.ClickHouse.Hybrid.Watermark.Overlap](#rqclickhousehybridwatermarkoverlap)
    * 3.3 [RQ.ClickHouse.Hybrid.Watermark.Replace](#rqclickhousehybridwatermarkreplace)
    * 3.4 [RQ.ClickHouse.Hybrid.PredicatePruning](#rqclickhousehybridpredicatepruning)
* 4 [INSERT Behavior](#insert-behavior)
    * 4.1 [RQ.ClickHouse.Hybrid.Insert.FirstSegmentOnly](#rqclickhousehybridinsertfirstsegmentonly)
* 5 [Automatic Type Alignment](#automatic-type-alignment)
    * 5.1 [RQ.ClickHouse.Hybrid.AutoCast](#rqclickhousehybridautocast)
    * 5.2 [RQ.ClickHouse.Hybrid.TypeSeams](#rqclickhousehybridtypeseams)
* 6 [Query Semantics](#query-semantics)
    * 6.1 [RQ.ClickHouse.Hybrid.QueryShapes](#rqclickhousehybridqueryshapes)
    * 6.2 [RQ.ClickHouse.Hybrid.CorrectnessVsUnion](#rqclickhousehybridcorrectnessvsunion)
* 7 [Distributed Execution Paths](#distributed-execution-paths)
    * 7.1 [RQ.ClickHouse.Hybrid.LocalVsRemote](#rqclickhousehybridlocalvsremote)
    * 7.2 [RQ.ClickHouse.Hybrid.SerializeQueryPlan](#rqclickhousehybridserializequeryplan)
    * 7.3 [RQ.ClickHouse.Hybrid.AggregationStages](#rqclickhousehybridaggregationstages)
    * 7.4 [RQ.ClickHouse.Hybrid.DistributedOverDistributed](#rqclickhousehybriddistributedoverdistributed)
* 8 [Segment Storage Types](#segment-storage-types)
    * 8.1 [RQ.ClickHouse.Hybrid.Segment.MergeTree](#rqclickhousehybridsegmentmergetree)
    * 8.2 [RQ.ClickHouse.Hybrid.Segment.Iceberg](#rqclickhousehybridsegmenticeberg)
    * 8.3 [RQ.ClickHouse.Hybrid.Segment.IcebergCatalogs](#rqclickhousehybridsegmenticebergcatalogs)
    * 8.4 [RQ.ClickHouse.Hybrid.Segment.IcebergCluster](#rqclickhousehybridsegmenticebergcluster)
    * 8.5 [RQ.ClickHouse.Hybrid.Segment.S3Parquet](#rqclickhousehybridsegments3parquet)
* 9 [Schema Variety and Refresh](#schema-variety-and-refresh)
    * 9.1 [RQ.ClickHouse.Hybrid.SchemaVariety](#rqclickhousehybridschemavariety)
    * 9.2 [RQ.ClickHouse.Hybrid.SchemaRefresh](#rqclickhousehybridschemarefresh)
* 10 [Topology](#topology)
    * 10.1 [RQ.ClickHouse.Hybrid.Topology.SecureCluster](#rqclickhousehybridtopologysecurecluster)
    * 10.2 [RQ.ClickHouse.Hybrid.Topology.ClusterAllReplicas](#rqclickhousehybridtopologyclusterallreplicas)
    * 10.3 [RQ.ClickHouse.Hybrid.Topology.ThreeSegments](#rqclickhousehybridtopologythreesegments)
* 11 [Lifecycle and Tiered Storage](#lifecycle-and-tiered-storage)
    * 11.1 [RQ.ClickHouse.Hybrid.Lifecycle.ExportThenWatermark](#rqclickhousehybridlifecycleexportthenwatermark)
    * 11.2 [RQ.ClickHouse.Hybrid.Lifecycle.OverlapDiscipline](#rqclickhousehybridlifecycleoverlapdiscipline)
    * 11.3 [RQ.ClickHouse.Hybrid.Lifecycle.ReplaceDistributed](#rqclickhousehybridlifecyclereplacedistributed)
* 12 [Operational Behavior](#operational-behavior)
    * 12.1 [RQ.ClickHouse.Hybrid.Operational.UnreachableCold](#rqclickhousehybridoperationalunreachablecold)
    * 12.2 [RQ.ClickHouse.Hybrid.Operational.ExportLag](#rqclickhousehybridoperationalexportlag)
* 13 [External Readers](#external-readers)
    * 13.1 [RQ.ClickHouse.Hybrid.ExternalReader.Iceberg](#rqclickhousehybridexternalreadericeberg)
* 14 [Query Fuzzing Coverage](#query-fuzzing-coverage)
    * 14.1 [RQ.ClickHouse.Hybrid.QueryFuzzing](#rqclickhousehybridqueryfuzzing)

## Introduction

The Hybrid table engine builds on top of the Distributed table engine. It allows exposing several data sources as one logical table and assigning every source its own predicate. This keeps all of the Distributed optimisations (`remote aggregation`, `skip_unused_shards`, global JOIN pushdown, and so on) while copying or migrating data across clusters, storage types, or formats.

Typical use cases include:

* Zero-downtime migrations where "old" and "new" replicas temporarily overlap
* Tiered storage, for example fresh data on a local cluster and historical data in S3 / Iceberg
* Gradual roll-outs where only a subset of rows should be served from a new backend

By giving mutually exclusive predicates to the segments (for example, `date < watermark` and `date >= watermark`), each row is read from exactly one source.

This specification defines the normative requirements for Hybrid. Behavior with `enable_analyzer = 0`, `SHARED NAMED SCALAR` / dynamic watermarks, and `TTL … EXPORT TO` is out of scope.

[ClickHouse]: https://clickhouse.com

## Engine Definition

### RQ.ClickHouse.Hybrid.Create
version: 1.0

[ClickHouse] SHALL support creating Hybrid tables with the following SQL syntax:

```sql
CREATE TABLE [IF NOT EXISTS] [db.]table_name
(
    column1 type1,
    column2 type2,
    ...
)
ENGINE = Hybrid(table_function_1, predicate_1 [, table_function_2, predicate_2 ...])
```

[ClickHouse] SHALL require at least one `table_function, predicate` pair. Additional sources are appended as further `table_function, predicate` pairs.

### RQ.ClickHouse.Hybrid.FirstSegment
version: 1.0

[ClickHouse] SHALL require `table_function_1` to be a table function that instantiates underlying Distributed storage, such as:
* `remote`
* `remoteSecure`
* `cluster`
* `clusterAllReplicas`

The first table function SHALL also be the target of `INSERT` statements.

### RQ.ClickHouse.Hybrid.AdditionalSegments
version: 1.0

[ClickHouse] SHALL accept subsequent segments as either:
* A valid table function (for example `remote`, `remoteSecure`, `cluster`, `clusterAllReplicas`, `s3`, `s3Cluster`, `icebergCluster`), or
* A fully qualified table name (`database.table`)

Each `predicate_n` SHALL be an expression evaluated on the table columns. The engine SHALL add it to the segment’s query with an additional `AND` (for example `event_date >= '2025-09-01'` or `id BETWEEN 10 AND 15`).

### RQ.ClickHouse.Hybrid.SchemaInference
version: 1.0

[ClickHouse] SHALL support omitting the explicit column list:

```sql
CREATE TABLE [IF NOT EXISTS] [db.]table_name
ENGINE = Hybrid(table_function_1, predicate_1 [, table_function_n, predicate_n ...])
```

In this case, [ClickHouse] SHALL detect columns and types from the first table function (including `CREATE … AS source_table` style definitions).

### RQ.ClickHouse.Hybrid.ExperimentalGate
version: 1.0

The Hybrid engine is experimental. [ClickHouse] SHALL gate Hybrid DDL behind `allow_experimental_hybrid_table`. When the setting is disabled, creating a Hybrid table SHALL fail. When enabled (session or profile), Hybrid DDL SHALL succeed:

```sql
SET allow_experimental_hybrid_table = 1;
```

### RQ.ClickHouse.Hybrid.AnalyzerRequired
version: 1.0

Hybrid queries SHALL be run with `enable_analyzer = 1` (formerly `allow_experimental_analyzer = 1`). The Hybrid regression suite enables the analyzer in the default profile and query settings. Behavior with `enable_analyzer = 0` is out of scope.

## Segment Predicates (Watermarks)

A **watermark** is a routing rule that determines which segments serve each row. In Hybrid tables, the watermark is encoded as predicates (SQL expressions) assigned to each segment. When a query executes, the engine evaluates each row against all segment predicates. A row that matches a predicate is served from that segment’s underlying storage.

**Predicate expression** examples: `date >= '2025-01-01'`, `id BETWEEN 10 AND 15`, `region = 'US'`.

The most common pattern uses a date-based watermark:

```sql
ENGINE = Hybrid(
    remote('hot_cluster', 'db', 'table'), date >= '2025-01-01',
    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-01-01'
)
```

* **Hot data** (`date >= '2025-01-01'`) → MergeTree / cluster for low-latency queries
* **Cold data** (`date < '2025-01-01'`) → Object storage (S3 / Iceberg) for cost efficiency

### RQ.ClickHouse.Hybrid.Watermark.Exclusive
version: 1.0

[ClickHouse] SHALL support mutually exclusive segment predicates such that each logical row is read from exactly one segment, and Hybrid query results match an exclusive `UNION ALL` reference over the same segments and predicates (no duplicates, no gaps for rows present in the covered dataset).

Example of mutually exclusive predicates:
* `date >= '2025-01-01'` — first segment
* `date < '2025-01-01'` — second segment

### RQ.ClickHouse.Hybrid.Watermark.Overlap
version: 1.0

[ClickHouse] SHALL allow overlapping predicates. A single row may match multiple predicates and be served from multiple segments, which MAY produce duplicate rows in query results relative to a distinct exclusive reference.

Example of overlapping predicates (may cause duplicates):
* `date >= '2025-01-01'` — first segment
* `date >= '2025-01-15'` — second segment

### RQ.ClickHouse.Hybrid.Watermark.Replace
version: 1.0

[ClickHouse] SHALL support updating Hybrid watermarks via `CREATE OR REPLACE TABLE` with new static predicates. The replace operation SHALL be atomic: after the statement completes, all queries SHALL see the new watermark with no window of inconsistent routing for the same data range.

```sql
-- Original watermark at '2025-01-01'
CREATE TABLE hybrid_table ENGINE = Hybrid(
    remote('hot_cluster', 'db', 'table'), date >= '2025-01-01',
    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-01-01'
) AS source_table;

-- Advance watermark to '2025-02-01' after exporting hot → cold
CREATE OR REPLACE TABLE hybrid_table ENGINE = Hybrid(
    remote('hot_cluster', 'db', 'table'), date >= '2025-02-01',
    s3Cluster('cold_cluster', 's3://bucket/path'), date < '2025-02-01'
) AS source_table;
```

### RQ.ClickHouse.Hybrid.PredicatePruning
version: 1.0

[ClickHouse] SHALL prune segments that cannot contribute rows when a query’s `WHERE` clause is exclusive to one watermark band, while still returning results identical to the exclusive reference for that band.

## INSERT Behavior

### RQ.ClickHouse.Hybrid.Insert.FirstSegmentOnly
version: 1.0

[ClickHouse] SHALL forward every `INSERT INTO` a Hybrid table exclusively to the first segment, including rows whose values would match a later segment’s predicate.

This design:
* Supports double-write scenarios where data is written to hot storage and later exported to cold
* Enables cache-layer setups where writes go to a fast layer
* Avoids ambiguous write targets when multiple segments could match

```sql
-- All inserts go to the first (hot) segment
INSERT INTO hybrid VALUES (...);

-- For multi-destination writes, use explicit inserts:
INSERT INTO hot_table VALUES (...);
INSERT INTO cold_table VALUES (...);
```

## Automatic Type Alignment

Segments can evolve independently, so the same logical column may use different physical types across segments (for example MergeTree `Decimal` vs Iceberg `Int`, or MergeTree `FixedString` vs Parquet `String`).

### RQ.ClickHouse.Hybrid.AutoCast
version: 1.0

When `hybrid_table_auto_cast_columns = 1` is enabled (requires `enable_analyzer = 1`), [ClickHouse] SHALL insert the necessary `CAST` operations so every shard / segment receives the schema defined by the Hybrid table header, preventing `CANNOT_CONVERT_TYPE` / `NO_COMMON_TYPE` failures for modest type seams.

Manual casts in user SQL remain allowed but MAY result in double-casting.

### RQ.ClickHouse.Hybrid.TypeSeams
version: 1.0

With auto-cast enabled, [ClickHouse] SHALL support Hybrid queries across at least the following seams when headers are declared appropriately:
* Unsigned integer vs signed counterpart (for example `UInt64` ↔ `Int64`, `UInt32` ↔ `Int32`) on MergeTree↔MergeTree and MergeTree↔Iceberg
* `FixedString(N)` ↔ `String`
* Aggregate paths such as `uniq` across those seams

When auto-cast is disabled, [ClickHouse] MAY reject incompatible seams.

## Query Semantics

Because predicates are applied inside every segment, Hybrid queries behave as if reading from a single Distributed table for shapes such as `ORDER BY`, `GROUP BY`, `LIMIT`, `JOIN`, and `EXPLAIN`.

Illustrative two-segment layout (hot MergeTree + historical S3 Parquet):

```sql
CREATE OR REPLACE TABLE btc_blocks_local
(
    `hash` FixedString(64),
    `number` Int64,
    `date` Date
    -- ...
)
ENGINE = MergeTree
ORDER BY (date)
PARTITION BY toYYYYMM(date);

CREATE OR REPLACE TABLE btc_blocks ENGINE = Hybrid(
    remote('localhost:9000', currentDatabase(), 'btc_blocks_local'), date >= '2025-09-01',
    s3('s3://aws-public-blockchain/v1.0/btc/blocks/**.parquet', NOSIGN), date < '2025-09-01'
) AS btc_blocks_local;
```

When sources expose different physical types (for example `FixedString(64)` versus `String` in Parquet), use auto-cast and/or explicit casts during ingestion or in the query.

### RQ.ClickHouse.Hybrid.QueryShapes
version: 1.0

[ClickHouse] SHALL support core analytic query shapes on Hybrid tables, including:
* Filtered `SELECT`
* `GROUP BY` aggregates (`count`, `sum`, `min`, `max`, and similar)
* `ORDER BY` / `LIMIT`
* Multi-segment scans that combine hot and cold predicates

### RQ.ClickHouse.Hybrid.CorrectnessVsUnion
version: 1.0

For mutually exclusive watermarks, [ClickHouse] SHALL return Hybrid results that match an exclusive `UNION ALL` reference constructed from the same segments and predicates (stable fingerprints / aggregates), including under Distributed path settings exercised by the suite.

## Distributed Execution Paths

Because Hybrid builds on Distributed, it inherits independent execution paths that SHALL all produce correct results.

### RQ.ClickHouse.Hybrid.LocalVsRemote
version: 1.0

[ClickHouse] SHALL produce correct Hybrid results for both:
* Local execution of subquery plans on the initiator (`prefer_localhost_replica = 1`)
* Forcing remote treatment of the local replica (`prefer_localhost_replica = 0`)

### RQ.ClickHouse.Hybrid.SerializeQueryPlan
version: 1.0

[ClickHouse] SHALL produce correct Hybrid results when remote work is sent as:
* SQL text (`serialize_query_plan = 0`, default), and
* A serialized query plan (`serialize_query_plan = 1`)

### RQ.ClickHouse.Hybrid.AggregationStages
version: 1.0

[ClickHouse] SHALL produce correct Hybrid aggregation results across remote aggregation stages, including:
* `complete`
* `with_mergeable_state`
* `with_mergeable_state_after_aggregation`
* `with_mergeable_state_after_aggregation_and_limit`

### RQ.ClickHouse.Hybrid.DistributedOverDistributed
version: 1.0

[ClickHouse] SHALL support Hybrid layouts where the first segment reads through a Distributed table (Distributed-over-Distributed), preserving fingerprint equality versus an exclusive reference.

## Segment Storage Types

### RQ.ClickHouse.Hybrid.Segment.MergeTree
version: 1.0

[ClickHouse] SHALL support Hybrid segments backed by MergeTree-family tables accessed via `remote` / `cluster` / `clusterAllReplicas`.

### RQ.ClickHouse.Hybrid.Segment.Iceberg
version: 1.0

[ClickHouse] SHALL support Hybrid cold (or other) segments backed by Iceberg tables / IcebergS3 destinations with exclusive watermarks and correct query results versus the exclusive reference.

### RQ.ClickHouse.Hybrid.Segment.IcebergCatalogs
version: 1.0

[ClickHouse] SHALL support Hybrid Iceberg segments under at least the following catalog modes:
* No external catalog (IcebergS3 / path-based)
* Iceberg REST catalog
* Glue catalog

### RQ.ClickHouse.Hybrid.Segment.IcebergCluster
version: 1.0

[ClickHouse] SHALL support Hybrid segments using `icebergCluster(...)`, including settings such as `object_storage_cluster_join_mode = 'local'` where applicable, with correct query results.

### RQ.ClickHouse.Hybrid.Segment.S3Parquet
version: 1.0

[ClickHouse] SHALL support Hybrid segments backed by `s3(...)` and `s3Cluster(...)` Parquet sources with correct query results versus the exclusive reference.

## Schema Variety and Refresh

### RQ.ClickHouse.Hybrid.SchemaVariety
version: 1.0

[ClickHouse] SHALL support Hybrid correctness for reduced-scale schema variety shapes that stress type mapping, including:
* Financial: `Decimal`, `FixedString`, `Enum8`
* Telemetry: `LowCardinality`, `DateTime64`, `Map`
* Logs: `String`, `Array`
* Iceberg-compatible nested types (`DateTime64`, `Array`, `Map`) on MergeTree + Iceberg

### RQ.ClickHouse.Hybrid.SchemaRefresh
version: 1.0

After a segment schema change such as `ADD COLUMN`, [ClickHouse] SHALL allow refreshing the Hybrid table header via `CREATE OR REPLACE` (including `ON CLUSTER` when the left segment is cluster-scoped) so subsequent queries see the updated columns.

## Topology

### RQ.ClickHouse.Hybrid.Topology.SecureCluster
version: 1.0

[ClickHouse] SHALL support Hybrid first segments over TLS-secured remote server configurations (secure cluster entries / `remoteSecure` path as configured in the deployment).

### RQ.ClickHouse.Hybrid.Topology.ClusterAllReplicas
version: 1.0

[ClickHouse] SHALL support Hybrid segments using `clusterAllReplicas(...)` with correct results versus the exclusive reference.

### RQ.ClickHouse.Hybrid.Topology.ThreeSegments
version: 1.0

[ClickHouse] SHALL support Hybrid tables with three or more exclusive predicate bands (for example hot / warm / cold) and return results matching the corresponding multi-way exclusive `UNION ALL` reference.

## Lifecycle and Tiered Storage

Recommended pipeline:
1. Insert new data into the first (hot) segment
2. Background process exports data from hot to cold storage (for example `EXPORT PARTITION`)
3. After verification, `CREATE OR REPLACE` the Hybrid table to advance the static watermark
4. Optionally delete the exported range from MergeTree **only after** the watermark has advanced

### RQ.ClickHouse.Hybrid.Lifecycle.ExportThenWatermark
version: 1.0

[ClickHouse] SHALL support the end-to-end tiered lifecycle:
* Hybrid over exportable MergeTree + Iceberg with a static watermark
* `EXPORT PARTITION` of cold bands into Iceberg
* `CREATE OR REPLACE` advancing the static watermark
* Delete of the exported range from MergeTree after the watermark advances

with Hybrid results matching the exclusive reference (no gaps, no duplicates for the covered dataset).

### RQ.ClickHouse.Hybrid.Lifecycle.OverlapDiscipline
version: 1.0

[ClickHouse] SHALL leave a detectable gap (missing newly cold rows) if the watermark is advanced without exporting the newly cold range into the cold segment first.

### RQ.ClickHouse.Hybrid.Lifecycle.ReplaceDistributed
version: 1.0

[ClickHouse] SHALL allow replacing a Distributed head over local MergeTree with a Hybrid head (`cluster(...)` + Iceberg or equivalent) such that:
* Query fingerprints match the prior Distributed baseline under localhost preference settings
* `INSERT` continues to land on the local / first-segment storage

## Operational Behavior

### RQ.ClickHouse.Hybrid.Operational.UnreachableCold
version: 1.0

When the cold Iceberg segment is dropped or otherwise unreachable, [ClickHouse] SHALL still serve queries whose predicates are exclusive to the hot watermark band. Full scans that require the missing cold segment MAY error or return an incomplete set.

### RQ.ClickHouse.Hybrid.Operational.ExportLag
version: 1.0

While the cold Iceberg segment is empty and the static watermark already routes a date band to cold, [ClickHouse] SHALL return only the hot-band rows for full Hybrid scans. After `EXPORT PARTITION` fills that cold band, Hybrid SHALL cover the full exclusive dataset.

## External Readers

### RQ.ClickHouse.Hybrid.ExternalReader.Iceberg
version: 1.0

After cold data has been exported into the Iceberg segment used by Hybrid, an external Iceberg reader (for example PyIceberg) SHALL observe the same cold-band row count as ClickHouse when reading that destination.

## Query Fuzzing Coverage

### RQ.ClickHouse.Hybrid.QueryFuzzing
version: 1.0

[ClickHouse] SHALL successfully execute a broad, non-interactive set of Hybrid query shapes (including curated Hybrid SQL and upstream-derived patterns such as windows, `LIMIT BY`, CTEs, and `GLOBAL IN`) against Hybrid topologies that combine MergeTree and Iceberg / `icebergCluster` segments.

Known Distributed / Hybrid limitations that are not Hybrid regressions (for example correlated subqueries on remote tables, and Nullable null-map access on some remote Iceberg paths) MAY be excluded until product support exists.
""",
)
