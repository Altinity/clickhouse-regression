# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_Iceberg_NativeCreateDrop_CreateTable = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.CreateTable",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `CREATE TABLE` inside a `DataLakeCatalog` database without an `ENGINE`\n"
        "clause. The statement SHALL:\n"
        "\n"
        "* build a valid Iceberg table from the declared columns, `PARTITION BY`, and `ORDER BY`;\n"
        "* register the table in the catalog under `<namespace>.<table>`;\n"
        "* make the table immediately visible in `SHOW TABLES`, `system.tables`, and to an external\n"
        "  reader attached to the same catalog;\n"
        "* leave the table empty and readable (`SELECT count()` returns `0`);\n"
        "* accept `INSERT` and return the inserted rows on `SELECT`.\n"
        "\n"
        "Nothing in the statement carries a storage endpoint or credentials; both come from the database\n"
        "definition.\n"
        "\n"
        "```sql\n"
        "CREATE TABLE lake.`analytics.daily_revenue`\n"
        "(\n"
        "    day Date,\n"
        "    region String,\n"
        "    revenue Float64\n"
        ")\n"
        "PARTITION BY toRelativeDayNum(day)\n"
        "ORDER BY region;\n"
        "\n"
        "INSERT INTO lake.`analytics.daily_revenue` VALUES ('2026-01-01', 'eu', 10.5)\n"
        "SETTINGS allow_experimental_insert_into_iceberg = 1;\n"
        "\n"
        "SELECT count() FROM lake.`analytics.daily_revenue`;\n"
        "```\n"
        "\n"
        "```text\n"
        "count()\n"
        "1\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.1",
)

RQ_Iceberg_NativeCreateDrop_CreateTable_ExplicitEngine = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.CreateTable.ExplicitEngine",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL continue to support `CREATE TABLE ... ENGINE = IcebergS3(url, key, secret)`\n"
        "(and the other `Iceberg*` engines) inside a `DataLakeCatalog` database. On this path\n"
        "[ClickHouse] writes the initial metadata file to the engine's location and registers the table in\n"
        "the catalog, and the resulting table SHALL be indistinguishable from an engine-less one to every\n"
        "reader: it appears in the catalog, reads back through the database, and loads in an external\n"
        "reader.\n"
        "\n"
        "The explicit engine path SHALL obey the same validation rules as the engine-less path for column\n"
        "modifiers, storage clauses, non-table objects, and namespace handling, so a statement that is\n"
        "rejected on one path for a schema reason is rejected on the other.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.2",
)

RQ_Iceberg_NativeCreateDrop_CreateTable_AsSource = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.CreateTable.AsSource",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `CREATE TABLE catalog_db.\\`ns.t\\` AS source_db.source_table` inside a\n"
        "`DataLakeCatalog` database:\n"
        "\n"
        "* the column names and types of the source are copied into the Iceberg schema;\n"
        "* the source's `PARTITION BY` is copied when every expression in it is one of the accepted\n"
        "  Iceberg transforms (RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy);\n"
        "* the source's `ORDER BY` is copied under the same condition;\n"
        "* `PARTITION BY` and `ORDER BY` written explicitly on the new table take precedence over the\n"
        "  source's;\n"
        "* the source's engine, engine `SETTINGS`, `PRIMARY KEY`, `SAMPLE BY`, `TTL`, and table comment\n"
        "  are NOT carried over, and if any of them is written explicitly on the new statement it is\n"
        "  rejected (RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedStorageClauses);\n"
        "* a source column carrying a modifier Iceberg cannot store (`DEFAULT`, `MATERIALIZED`, `ALIAS`,\n"
        "  `EPHEMERAL`, `COMMENT`, `CODEC`, `TTL`, `STATISTICS`, column `SETTINGS`) causes the statement\n"
        "  to be rejected with `BAD_ARGUMENTS` rather than silently creating a weaker table.\n"
        "\n"
        "The source may be a `MergeTree` table with a functional partition key, which is the migration\n"
        "case this form exists for.\n"
        "\n"
        "```sql\n"
        "CREATE TABLE lake.`migrated.events` AS default.events;\n"
        "INSERT INTO lake.`migrated.events` SELECT * FROM default.events\n"
        "SETTINGS allow_experimental_insert_into_iceberg = 1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.3",
)

RQ_Iceberg_NativeCreateDrop_SupportedCatalogs = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.SupportedCatalogs",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support native `CREATE TABLE` and `DROP TABLE` for Iceberg REST catalogs\n"
        "(including OneLake, BigLake, and Delta Sharing variants) and for the AWS Glue catalog. For any\n"
        "other catalog type of a `DataLakeCatalog` database (Unity, Hive Metastore, Paimon REST) both\n"
        "statements SHALL fail with `NOT_IMPLEMENTED` and an error message that names the supported\n"
        "catalog types, and SHALL NOT partially register or partially delete anything.\n"
        "\n"
        "The regression environment exercises the REST (`ice-rest-catalog`) and Glue (LocalStack)\n"
        "branches; every requirement in this specification applies to both unless it says otherwise.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.4",
)

RQ_Iceberg_NativeCreateDrop_Schema_Columns = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Schema.Columns",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL persist every declared column into the Iceberg schema with a stable field id\n"
        "and the Iceberg type that corresponds to the ClickHouse type, such that:\n"
        "\n"
        "* a non-`Nullable` column becomes a required Iceberg field and a `Nullable` column an optional\n"
        "  one;\n"
        "* nested types (`Array`, `Map`, `Tuple`) become `list`, `map`, and `struct` with their element\n"
        "  fields assigned ids;\n"
        "* an external reader reports the same column names, order, and types that [ClickHouse] reports\n"
        "  in `DESCRIBE TABLE`;\n"
        "* a value written by [ClickHouse] round-trips unchanged through `SELECT` and through the\n"
        "  external reader for every supported primitive and nested type.\n"
        "\n"
        "A `CREATE TABLE` with no columns SHALL be rejected with `BAD_ARGUMENTS`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL translate the `PARTITION BY` clause into the Iceberg partition spec using only\n"
        "the transforms Iceberg defines:\n"
        "\n"
        "| Expression | Iceberg transform |\n"
        "|---|---|\n"
        "| `<column>` | `identity` |\n"
        "| `toYearNumSinceEpoch(<col>)` | `year` |\n"
        "| `toMonthNumSinceEpoch(<col>)` | `month` |\n"
        "| `toRelativeDayNum(<col>)` | `day` |\n"
        "| `toRelativeHourNum(<col>)` | `hour` |\n"
        "| `icebergTruncate(N, <col>)` | `truncate[N]` |\n"
        "| `icebergBucket(N, <col>)` | `bucket[N]` |\n"
        "\n"
        "Composite partitioning `PARTITION BY (expr1, expr2, ...)` SHALL produce one partition field per\n"
        "expression, in order. A table created without `PARTITION BY` SHALL have an empty (unpartitioned)\n"
        "spec. The spec written SHALL be the one an external reader loads, and rows inserted by\n"
        "[ClickHouse] SHALL land under partition paths that reader agrees with.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.2",
)

RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy_RejectedExpressions = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy.RejectedExpressions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject with `BAD_ARGUMENTS` a `PARTITION BY` expression that is not one of the\n"
        "accepted transforms, for example `toYYYYMM(col)`, `intDiv(col, 10)`, `col % 7`, or an arbitrary\n"
        "function call. The rejection SHALL happen before any request reaches the catalog: after the\n"
        "failed statement the table SHALL NOT exist in the catalog and no metadata file SHALL exist at\n"
        "the location the table would have used.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.3",
)

RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy_TransformParameters = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy.TransformParameters",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL require the width of `icebergTruncate(N, col)` and the bucket count of\n"
        "`icebergBucket(N, col)` to be a positive integer. `N = 0` or a negative `N` SHALL be rejected with\n"
        "`BAD_ARGUMENTS` before the table is registered, so the catalog never holds a table whose\n"
        "partition spec serialises as `bucket[0]`, `bucket[-1]`, or `truncate[0]` and cannot be read.\n"
        "\n"
        "Reasoning: an invalid transform parameter is not caught by the catalog; it produces a registered\n"
        "table every reader fails on, and the only remedy is a manual drop.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.4",
)

RQ_Iceberg_NativeCreateDrop_Schema_OrderBy = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Schema.OrderBy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL translate the `ORDER BY` clause into the Iceberg sort order:\n"
        "\n"
        "* each column in `ORDER BY` becomes a sort field, in order;\n"
        "* a table created without `ORDER BY` SHALL have the unsorted order (`order-id` 0, no fields);\n"
        "* a non-empty sort order SHALL carry a non-zero `order-id` and SHALL be the order an external\n"
        "  reader loads as the table's default sort order.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.5",
)

RQ_Iceberg_NativeCreateDrop_Schema_UnsupportedStorageClauses = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedStorageClauses",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject with `BAD_ARGUMENTS` a `CREATE TABLE` in a `DataLakeCatalog` database\n"
        "that carries any storage clause Iceberg cannot persist: `PRIMARY KEY`, `SAMPLE BY`, `TTL`, and\n"
        "`UNIQUE KEY`. On the engine-less path engine `SETTINGS` SHALL also be rejected, because there is no\n"
        "engine to receive them. The error message SHALL name the offending clause.\n"
        "\n"
        "The rule applies to clauses written explicitly on a `CREATE TABLE ... AS` statement as well; a\n"
        "clause inherited from the source table is dropped, an explicit one is rejected.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.6",
)

RQ_Iceberg_NativeCreateDrop_Schema_UnsupportedColumnModifiers = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedColumnModifiers",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject with `BAD_ARGUMENTS` any column declaration carrying a modifier the\n"
        "Iceberg schema cannot store: `DEFAULT`, `MATERIALIZED`, `ALIAS`, `EPHEMERAL`, `COMMENT`, `CODEC`,\n"
        "`TTL`, `STATISTICS`, column-level `SETTINGS`, and column-level `PRIMARY KEY`. The error message\n"
        "SHALL name the column. The rule SHALL hold on the engine-less path, on the explicit engine path,\n"
        "and for columns inherited through `CREATE TABLE ... AS`.\n"
        "\n"
        "Reasoning: a `DataLakeCatalog` table is re-instantiated from the catalog on every access, so any\n"
        "property that is not in the Iceberg metadata would silently disappear after the `CREATE`.\n"
        "Rejecting is the only way the user learns that the table does not have the semantics they wrote.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.7",
)

RQ_Iceberg_NativeCreateDrop_Schema_UnsupportedTableElements = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedTableElements",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject with `BAD_ARGUMENTS` a `CREATE TABLE` in a `DataLakeCatalog` database\n"
        "that declares data-skipping indices, constraints, projections, or a table-level `PRIMARY KEY`\n"
        "(whether written in the column list or as a storage clause), and a `CREATE TABLE` that carries a\n"
        "table `COMMENT`. Since `CREATE TABLE ... AS` inherits the source's comment, a source with a comment\n"
        "SHALL be rejected the same way.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.8",
)

RQ_Iceberg_NativeCreateDrop_Schema_NonTableObjects = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Schema.NonTableObjects",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support only plain `CREATE TABLE` in a `DataLakeCatalog` database. The\n"
        "following SHALL fail with `NOT_IMPLEMENTED` and leave nothing in the catalog:\n"
        "\n"
        "* `CREATE VIEW` and `CREATE MATERIALIZED VIEW`;\n"
        "* `CREATE DICTIONARY`;\n"
        "* `ATTACH TABLE`;\n"
        "* `CREATE TABLE ... CLONE AS`;\n"
        "* `CREATE OR REPLACE TABLE` and `REPLACE TABLE`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.9",
)

RQ_Iceberg_NativeCreateDrop_Schema_EngineSettings = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Schema.EngineSettings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "On the explicit engine path [ClickHouse] SHALL accept engine `SETTINGS` and apply them as the\n"
        "engine's data lake storage settings during creation, for example `iceberg_format_version`. This is\n"
        "the positive control for RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedStorageClauses: the same\n"
        "`SETTINGS` clause that is rejected without an engine is honoured with one, and the resulting\n"
        "metadata reflects the setting's value.\n"
        "\n"
        "```sql\n"
        "CREATE TABLE lake.`ns.v2_table` (id Int64)\n"
        "ENGINE = IcebergS3('http://minio:9000/warehouse/data/ns/v2_table/', 'admin', 'password')\n"
        "SETTINGS iceberg_format_version = 2;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.10",
)

RQ_Iceberg_NativeCreateDrop_Location_Resolution = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Location.Resolution",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "On the engine-less path [ClickHouse] SHALL place a new table at `<base>/<namespace>/<table>`,\n"
        "where `<base>` is resolved in this order:\n"
        "\n"
        "1. the `default-base-location` the catalog reports, when the catalog reports one;\n"
        "2. otherwise the database setting `default_base_location`;\n"
        "3. otherwise a location derived from the database setting `storage_endpoint`\n"
        "   (RQ.Iceberg.NativeCreateDrop.Location.DerivedFromStorageEndpoint).\n"
        "\n"
        "When none of the three is available the statement SHALL fail with `BAD_ARGUMENTS` and a message\n"
        "naming `default_base_location` and `storage_endpoint`. The resolved location SHALL be the\n"
        "`location` an external reader sees on the loaded table, and the `metadata/` and `data/`\n"
        "directories SHALL be created directly under it.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.1",
)

RQ_Iceberg_NativeCreateDrop_Location_DefaultBaseLocation = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Location.DefaultBaseLocation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the `DataLakeCatalog` database setting `default_base_location`, a full\n"
        "URI such as `s3://warehouse/data`, as the base under which engine-less `CREATE TABLE` places\n"
        "tables when the catalog does not report a base location itself. Trailing slashes SHALL be\n"
        "ignored, so `s3://warehouse/data/` and `s3://warehouse/data` place tables identically. The setting\n"
        "SHALL be visible in `SHOW CREATE DATABASE`.\n"
        "\n"
        "```sql\n"
        "CREATE DATABASE lake\n"
        "ENGINE = DataLakeCatalog('http://ice-rest-catalog:5000', 'admin', 'password')\n"
        "SETTINGS catalog_type = 'rest', storage_endpoint = 'http://minio:9000/warehouse',\n"
        "         default_base_location = 's3://warehouse/data';\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.2",
)

RQ_Iceberg_NativeCreateDrop_Location_DerivedFromStorageEndpoint = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Location.DerivedFromStorageEndpoint",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When neither the catalog nor `default_base_location` supplies a base, [ClickHouse] SHALL derive\n"
        "the S3 location from the path component of `storage_endpoint`: for\n"
        "`storage_endpoint = 'http://minio:9000/warehouse'` a table `ns.tbl` is placed at\n"
        "`s3://warehouse/ns/tbl`, and for `http://minio:9000/warehouse/prefix` at\n"
        "`s3://warehouse/prefix/ns/tbl`. A `storage_endpoint` whose path is empty (`http://minio:9000/`)\n"
        "carries no bucket and SHALL cause `CREATE TABLE` to fail with `BAD_ARGUMENTS`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.3",
)

RQ_Iceberg_NativeCreateDrop_Location_VirtualHostedStyle = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Location.VirtualHostedStyle",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the database uses `storage_uri_style = 'virtual_hosted'`, [ClickHouse] SHALL NOT attempt to\n"
        "derive the bucket from `storage_endpoint`, because a virtual-hosted host (`bucket.minio.example`,\n"
        "`s3.us-east-1.amazonaws.com`, an IP address) cannot be split into bucket and service\n"
        "unambiguously. An engine-less `CREATE TABLE` on such a database SHALL fail with `BAD_ARGUMENTS`\n"
        "telling the user to set `default_base_location`, and SHALL succeed once `default_base_location`\n"
        "is set.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.4",
)

RQ_Iceberg_NativeCreateDrop_Location_BackendConsistency = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Location.BackendConsistency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "For a fixed-backend catalog, [ClickHouse] SHALL reject with `BAD_ARGUMENTS` a\n"
        "`default_base_location` whose URI scheme names a different storage backend than the catalog's\n"
        "(for example an `abfss://` base on a Glue database), because the catalog would reopen the table\n"
        "with its own backend and the table would be unreadable immediately after creation. The check\n"
        "SHALL run before anything is written or registered.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.5",
)

RQ_Iceberg_NativeCreateDrop_Location_Azure = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Location.Azure",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "For an Azure-backed catalog [ClickHouse] SHALL derive the table location in the `abfss` form\n"
        "`abfss://<container>@<account-host>/<sub-path>/<namespace>/<table>` from either a\n"
        "`https://<account-host>/<container>[/<sub-path>]` or an\n"
        "`abfss://<container>@<account-host>[/<sub-path>]` storage endpoint, and SHALL reject with\n"
        "`BAD_ARGUMENTS` an endpoint that lacks the account host or the container.\n"
        "\n"
        "Note: the regression environment has no Azure service; this requirement carries the Azure branch\n"
        "of location resolution so that the S3 coverage stands on its own.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.6",
)

RQ_Iceberg_NativeCreateDrop_Namespace_AutoCreate = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Namespace.AutoCreate",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL create the target namespace in the catalog when it does not exist yet, before\n"
        "registering the table, so that `CREATE TABLE lake.\\`new_ns.t\\`` succeeds against a catalog that\n"
        "has never seen `new_ns`. When the namespace already exists it SHALL be reused unchanged, and\n"
        "[ClickHouse] SHALL NOT issue a create request for it (a principal that may create tables but not\n"
        "namespaces stays able to create tables in a pre-provisioned namespace).\n"
        "\n"
        "The namespace SHALL be created only after all local validation has passed: a `CREATE TABLE`\n"
        "rejected for a schema, clause, or location reason SHALL leave no new namespace behind.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.7",
)

RQ_Iceberg_NativeCreateDrop_Namespace_DefaultLocation = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Namespace.DefaultLocation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When [ClickHouse] creates a namespace it SHALL register the namespace base\n"
        "(`<base>/<namespace>`) as the namespace's default location, never the first table's own\n"
        "directory. Consequently a second table created later in the same namespace without an explicit\n"
        "location SHALL land beside the first table, not inside it.\n"
        "\n"
        "On the explicit engine path the namespace base is known only when the engine's path follows the\n"
        "`<base>/<namespace>/<table>` layout; when it does not, [ClickHouse] SHALL register the namespace\n"
        "with no default location rather than with the table's directory.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.8",
)

RQ_Iceberg_NativeCreateDrop_Namespace_Nested = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Namespace.Nested",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support multi-level namespaces written with dots, such as\n"
        "`lake.\\`a.b.c.table\\``: the namespace SHALL be sent to a REST catalog as the segment list\n"
        '`["a", "b", "c"]`, the table SHALL be created at `<base>/a.b.c/table` or an equivalent the\n'
        "catalog resolves, and `INSERT` and `ALTER TABLE ... ADD COLUMN` on the created table SHALL\n"
        "succeed, since both update the catalog through the same identifier.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.9",
)

RQ_Iceberg_NativeCreateDrop_Namespace_Filtered = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Namespace.Filtered",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a `DataLakeCatalog` database restricts visibility with its `namespaces` parameter,\n"
        "[ClickHouse] SHALL reject both `CREATE TABLE` and `DROP TABLE` targeting a namespace outside the\n"
        "allowed set with `CATALOG_NAMESPACE_DISABLED`, and SHALL NOT contact the catalog for the table.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.10",
)

RQ_Iceberg_NativeCreateDrop_ExplicitEngine_IcebergFamilyOnly = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.ExplicitEngine.IcebergFamilyOnly",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject with `BAD_ARGUMENTS` a `CREATE TABLE` inside a `DataLakeCatalog`\n"
        "database whose explicit engine is not an `Iceberg*` engine (for example `MergeTree`, `Memory`,\n"
        "`S3`, `DeltaLake`). The message SHALL name the engine that was given.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_Iceberg_NativeCreateDrop_ExplicitEngine_BackendMismatch = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.ExplicitEngine.BackendMismatch",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "For a fixed-backend catalog, [ClickHouse] SHALL reject with `BAD_ARGUMENTS` an explicit engine\n"
        "that pins a different backend: `IcebergAzure`, `IcebergHDFS`, or `IcebergLocal` on a Glue\n"
        "database, for example. The error SHALL explain that the table would be reopened with the\n"
        "catalog's backend and become unreadable, and SHALL name the backend the catalog stores tables on.\n"
        "The matching engine (`IcebergS3` on Glue) SHALL be accepted. A catalog with no fixed backend\n"
        "SHALL accept any `Iceberg*` engine.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.2",
)

RQ_Iceberg_NativeCreateDrop_ExplicitEngine_GenericIcebergEngine = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.ExplicitEngine.GenericIcebergEngine",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject with `BAD_ARGUMENTS` the generic `ENGINE = Iceberg(...)` inside a\n"
        "`DataLakeCatalog` database attached to a fixed-backend catalog, because that engine chooses its\n"
        "backend from a `disk` setting that is resolved only after database-level validation. The message\n"
        "SHALL direct the user to the backend-specific engine.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.3",
)

RQ_Iceberg_NativeCreateDrop_Metadata_InitialFile = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Metadata.InitialFile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "After a successful `CREATE TABLE` the table location SHALL contain exactly one metadata file under\n"
        "`metadata/`, and the catalog's `metadata_location` for the table SHALL point at it. The file\n"
        "SHALL be a valid Iceberg table metadata document with:\n"
        "\n"
        "* the requested `format-version` (the default when none is requested);\n"
        "* a single schema whose fields match RQ.Iceberg.NativeCreateDrop.Schema.Columns;\n"
        "* a single partition spec and a single sort order matching the `PARTITION BY` and `ORDER BY`;\n"
        "* no snapshots, no current snapshot, and an empty metadata log.\n"
        "\n"
        "On the explicit engine path with a transactional (REST) catalog the file SHALL be named\n"
        "`v1-<table-uuid>.metadata.json`; with a non-transactional catalog and on the engine-less Glue path\n"
        "it SHALL be named `v1.metadata.json`; on the engine-less REST path the catalog server names it.\n"
        "When `iceberg_use_version_hint` is enabled on the explicit engine path, `metadata/version-hint.text`\n"
        "SHALL be written with content `1`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.1",
)

RQ_Iceberg_NativeCreateDrop_Metadata_Compression = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Metadata.Compression",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL honour `iceberg_metadata_compression_method` on every path where it writes the\n"
        "initial metadata file itself (the explicit engine path, and the engine-less Glue path). With\n"
        "`iceberg_metadata_compression_method = 'gzip'` the registered `metadata_location` SHALL end in\n"
        "`.gzip.metadata.json` and the object's content SHALL be a gzip stream, and the table SHALL be\n"
        "readable and writable afterwards through the database.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.2",
)

RQ_Iceberg_NativeCreateDrop_Metadata_FirstCommit = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Metadata.FirstCommit",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The first `INSERT` into a natively created table SHALL produce a snapshot that carries no\n"
        "`parent-snapshot-id` field (rather than a null one), SHALL set `current-snapshot-id`, and SHALL\n"
        "add a `metadata-log` entry that references the previous metadata file, the one written at\n"
        "`CREATE`. Subsequent inserts SHALL chain to the previous snapshot as parent. An external reader\n"
        "SHALL load the table after each commit and see exactly the rows inserted.\n"
        "\n"
        "Reasoning: an empty table has no current snapshot, and a writer that assumes one existed emits\n"
        "metadata that strict readers reject as malformed.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.3",
)

RQ_Iceberg_NativeCreateDrop_Metadata_ExternalReader = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Metadata.ExternalReader",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "A table created by [ClickHouse] on either path SHALL be a first-class Iceberg table to external\n"
        "clients attached to the same catalog:\n"
        "\n"
        "* PyIceberg `load_table` succeeds and reports the same schema, partition spec, sort order, and\n"
        "  location that [ClickHouse] wrote;\n"
        "* after [ClickHouse] inserts rows, PyIceberg and Spark scans return exactly those rows;\n"
        "* after Spark inserts rows into the table, [ClickHouse] returns them.\n"
        "\n"
        "Regression scenarios SHALL use both PyIceberg and the Spark container where the catalog is\n"
        "reachable from both; Spark reads the REST catalog only.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.4",
)

RQ_Iceberg_NativeCreateDrop_IfNotExists = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.IfNotExists",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `CREATE TABLE IF NOT EXISTS` in a `DataLakeCatalog` database:\n"
        "\n"
        "* when the table is not in the catalog it is created normally;\n"
        "* when the table is already in the catalog the statement succeeds, creates nothing, and leaves\n"
        "  the existing table's schema, data, and metadata location unchanged, whichever client created\n"
        "  it;\n"
        "* without `IF NOT EXISTS` the same situation fails with `TABLE_ALREADY_EXISTS`.\n"
        "\n"
        "`CREATE TABLE IF NOT EXISTS ... AS SELECT` SHALL NOT insert into a table that already existed.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_Iceberg_NativeCreateDrop_IfNotExists_ConcurrentCreate = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.IfNotExists.ConcurrentCreate",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When several clients race to create the same `<namespace>.<table>` (two [ClickHouse] nodes, or a\n"
        "[ClickHouse] node and an external writer through the same catalog), exactly one SHALL win:\n"
        "\n"
        "* the catalog ends with one table whose metadata location belongs to the winner;\n"
        "* a loser that used `IF NOT EXISTS` reports success and creates nothing;\n"
        "* a loser without `IF NOT EXISTS` fails with `TABLE_ALREADY_EXISTS`;\n"
        "* the loser SHALL remove any initial metadata file it staged before it learned it lost, so the\n"
        "  table location holds only the winner's files;\n"
        "* a loser's `AS SELECT` SHALL NOT fill the winner's table.\n"
        "\n"
        "The lost race SHALL be detected on every path: the catalog answering conflict (`409` from REST,\n"
        "`AlreadyExists` from Glue), and the `If-None-Match: *` guarded metadata write answering\n"
        "`PreconditionFailed`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.2",
)

RQ_Iceberg_NativeCreateDrop_LeftoverMetadata = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.LeftoverMetadata",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the catalog has no table registered under `<namespace>.<table>` but Iceberg metadata files\n"
        "already exist at the location the new table would use (typically left behind by an earlier\n"
        "`DROP TABLE` without `data_lake_delete_data_on_drop`), [ClickHouse] SHALL NOT overwrite them and\n"
        "SHALL NOT register a table over them:\n"
        "\n"
        "* without `IF NOT EXISTS` the statement fails with `TABLE_ALREADY_EXISTS` and a message that\n"
        "  names `data_lake_delete_data_on_drop` and tells the user to remove the leftover files or use a\n"
        "  different location;\n"
        "* with `IF NOT EXISTS` the statement succeeds, creates nothing, and the table stays absent from\n"
        "  the catalog (a success that reports a table the catalog cannot see is not acceptable).\n"
        "\n"
        "This differs from a path-based `ENGINE = IcebergS3` table outside any catalog, where\n"
        "`IF NOT EXISTS` attaches to the existing metadata; inside a catalog, attaching would silently\n"
        "adopt files of unknown provenance.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.3",
)

RQ_Iceberg_NativeCreateDrop_FailedCreateLeavesNoTrace = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.FailedCreateLeavesNoTrace",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "A `CREATE TABLE` that fails for any reason before the catalog acknowledges the registration\n"
        "SHALL leave no trace: no catalog entry, no new namespace (RQ.Iceberg.NativeCreateDrop.Namespace.AutoCreate),\n"
        "and no object under the table location, including a staged initial metadata file and\n"
        "`version-hint.text`. In particular:\n"
        "\n"
        "* a failure while writing `version-hint.text` after the metadata file was written SHALL remove\n"
        "  the metadata file before the error propagates;\n"
        "* a Glue `CreateTable` failure after the metadata file was staged SHALL remove the staged file;\n"
        "* a rejected transform, clause, modifier, or location SHALL fail before any object is written.\n"
        "\n"
        "Reasoning: the initial metadata write is guarded by `If-None-Match: *`, so a leftover from a\n"
        "failed attempt would make every retry of the same `CREATE` report an existing table.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.4",
)

RQ_Iceberg_NativeCreateDrop_Drop = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Drop",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `DROP TABLE` for a table in a `DataLakeCatalog` database, whichever\n"
        "client created it. After the statement the table SHALL be absent from the catalog (an external\n"
        "client listing the namespace does not see it), absent from `SHOW TABLES`, and a `SELECT` against\n"
        "it SHALL fail with `UNKNOWN_TABLE`. The drop SHALL work for a table that was never read through\n"
        "this [ClickHouse] node before the `DROP`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_Iceberg_NativeCreateDrop_Drop_KeepData = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Drop.KeepData",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "By default (`data_lake_delete_data_on_drop = 0`) `DROP TABLE` SHALL only unregister the table:\n"
        "every data file and metadata file under the table location SHALL still exist afterwards, and for a\n"
        "REST catalog the request SHALL carry `purgeRequested=false`. The kept files remain a valid Iceberg\n"
        "table that can be re-registered by an external client.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.2",
)

RQ_Iceberg_NativeCreateDrop_Drop_Purge = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Drop.Purge",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "With `data_lake_delete_data_on_drop = 1`, `DROP TABLE` SHALL ask the catalog to purge the table:\n"
        "for a REST catalog the request SHALL carry `purgeRequested=true`. When the catalog honours the\n"
        "request, no object SHALL remain under the table location (data files, manifests, manifest lists,\n"
        "metadata files, and the version hint). Whether data is actually removed is the catalog's decision;\n"
        "[ClickHouse] SHALL report success when the catalog acknowledges the drop, and SHALL fail with\n"
        "`DATALAKE_DATABASE_ERROR` when the catalog rejects it.\n"
        "\n"
        "```sql\n"
        "DROP TABLE lake.`analytics.scratch` SETTINGS data_lake_delete_data_on_drop = 1;\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.3",
)

RQ_Iceberg_NativeCreateDrop_Drop_Setting = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Drop.Setting",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide the query setting `data_lake_delete_data_on_drop` (`Bool`, default\n"
        "`false`). The previously released `iceberg_delete_data_on_drop` SHALL remain accepted as an alias\n"
        "with identical effect, so that setting either name enables the purge and `system.settings` reports\n"
        "the new name. The setting SHALL be listed in the settings changes history for the release that\n"
        "introduces it.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.4",
)

RQ_Iceberg_NativeCreateDrop_Drop_QueryLevelSetting = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Drop.QueryLevelSetting",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "A `data_lake_delete_data_on_drop` value given at query level (`DROP TABLE ... SETTINGS ...`) or\n"
        "session level SHALL be the value the drop acts on, even though the storage-level drop runs in a\n"
        "background thread after the query has finished. This SHALL hold for catalog tables and for\n"
        "path-based Iceberg tables (`ENGINE = IcebergS3(...)` and `ENGINE = IcebergLocal(...)` outside a\n"
        "catalog), where [ClickHouse] deletes the files itself:\n"
        "\n"
        "* `DROP TABLE t SYNC SETTINGS data_lake_delete_data_on_drop = 1` leaves zero objects under the\n"
        "  table path;\n"
        "* `DROP TABLE t SYNC SETTINGS data_lake_delete_data_on_drop = 0` leaves every object in place,\n"
        "  regardless of a server-wide default of `1`.\n"
        "\n"
        "When no query carried the setting to the table (the table was never loaded before a drop that\n"
        "did not come from `DROP TABLE`), [ClickHouse] SHALL keep the data and log a warning rather than\n"
        "delete on a fallback path.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.5",
)

RQ_Iceberg_NativeCreateDrop_Drop_IfExists = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Drop.IfExists",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support `DROP TABLE IF EXISTS` in a `DataLakeCatalog` database: when the table\n"
        "is not in the catalog the statement succeeds and does nothing, and when another client removes the\n"
        "table between the existence check and the catalog call (REST `404`, Glue `EntityNotFound`) the\n"
        "statement still succeeds. Without `IF EXISTS` dropping a table that is not in the catalog SHALL\n"
        "fail with `UNKNOWN_TABLE`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.6",
)

RQ_Iceberg_NativeCreateDrop_Drop_Glue = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Drop.Glue",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "For a Glue catalog, `DROP TABLE` SHALL remove only the Glue catalog entry and SHALL keep the data\n"
        "files. Because a purge cannot be honoured, `DROP TABLE ... SETTINGS data_lake_delete_data_on_drop = 1`\n"
        "SHALL fail with `NOT_IMPLEMENTED`, the message SHALL say that the setting is not supported for the\n"
        "Glue catalog, and the table SHALL remain registered and readable. `DROP TABLE IF EXISTS` with the\n"
        "purge setting on a table that is not in Glue SHALL succeed as a no-op.\n"
        "\n"
        "Reasoning: silently dropping the entry while the user asked for a purge would orphan the data\n"
        "with no indication that it was kept.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.7",
)

RQ_Iceberg_NativeCreateDrop_Drop_S3Tables = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Drop.S3Tables",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "For an S3 Tables catalog, whose API only offers a purging delete, `DROP TABLE` without\n"
        "`data_lake_delete_data_on_drop = 1` SHALL fail with `SUPPORT_IS_DISABLED` and a message telling\n"
        "the user to enable the setting, so that data the statement asked to keep is never deleted.\n"
        "`DROP TABLE IF EXISTS` on a table that is not in the catalog SHALL still succeed as a no-op.\n"
        "\n"
        "Note: the regression environment has no S3 Tables service; this requirement carries that branch\n"
        "so the REST and Glue drop coverage stands on its own.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.8",
)

RQ_Iceberg_NativeCreateDrop_OnCluster_Rejected = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.OnCluster.Rejected",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject `ON CLUSTER` for DDL whose target table is in a `DataLakeCatalog`\n"
        "database. `CREATE TABLE ... ON CLUSTER`, `DROP TABLE ... ON CLUSTER`, `ALTER TABLE ... ON CLUSTER`,\n"
        "and `RENAME TABLE ... ON CLUSTER` SHALL fail with `NOT_IMPLEMENTED` on the initiator, the message\n"
        "SHALL explain that the catalog is shared and the query should run without `ON CLUSTER`, and the\n"
        "query SHALL NOT be enqueued to the distributed DDL queue, so no node creates, drops, or alters the\n"
        "table.\n"
        "\n"
        "Reasoning: the catalog is the shared state. Running the same `CREATE` on every node would make\n"
        "the nodes race against each other for one table.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_Iceberg_NativeCreateDrop_OnCluster_WorkerGuard = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.OnCluster.WorkerGuard",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When the initiator does not have the `DataLakeCatalog` database locally and therefore cannot\n"
        "detect the target, the `ON CLUSTER` query is enqueued, and every worker that does have the\n"
        "database SHALL reject it with `NOT_IMPLEMENTED` when executing its task, so that the table is\n"
        "still not created on any node. A plain `ON CLUSTER` query against an ordinary database issued from\n"
        "the same initiator SHALL still reach and run on the workers, proving the rejection is specific to\n"
        "the catalog database.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.2",
)

RQ_Iceberg_NativeCreateDrop_SharedCatalogVisibility = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.SharedCatalogVisibility",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "A table created on one [ClickHouse] node SHALL be visible and readable on every other node that\n"
        "has a `DataLakeCatalog` database attached to the same catalog, without any DDL on those nodes.\n"
        "Cluster reads of the created table through `icebergS3Cluster` or the database with\n"
        "`parallel_replicas_for_cluster_engines` SHALL return the same rows as a single-node read. A table\n"
        "dropped on one node SHALL disappear from the other nodes' `SHOW TABLES` on their next listing.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.3",
)

RQ_Iceberg_NativeCreateDrop_Lifecycle_InsertAlterSelect = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Lifecycle.InsertAlterSelect",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "A natively created table SHALL support the full set of operations the database already supports\n"
        "for externally created tables: `INSERT` (with `allow_experimental_insert_into_iceberg`),\n"
        "`ALTER TABLE ... ADD COLUMN`, `DROP COLUMN`, `MODIFY COLUMN`, and `RENAME COLUMN`, `SELECT` with\n"
        "predicate pushdown and partition pruning, `ALTER TABLE ... DELETE` where the format version\n"
        "allows it, and `TRUNCATE`. After each operation the catalog's `metadata_location` SHALL advance\n"
        "and an external reader SHALL observe the change.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.1",
)

RQ_Iceberg_NativeCreateDrop_Lifecycle_Recreate = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Lifecycle.Recreate",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "After `DROP TABLE ... SETTINGS data_lake_delete_data_on_drop = 1`, creating a table with the same\n"
        "`<namespace>.<table>` and the same resolved location SHALL succeed and yield an empty table.\n"
        "After `DROP TABLE` without the purge, creating the same table at the same location SHALL be\n"
        "refused per RQ.Iceberg.NativeCreateDrop.LeftoverMetadata, while creating it under a different\n"
        "`default_base_location` SHALL succeed, and the kept files of the dropped table SHALL be untouched\n"
        "by either attempt.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.2",
)

RQ_Iceberg_NativeCreateDrop_Lifecycle_ExportPartitionDestination = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.Lifecycle.ExportPartitionDestination",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "On builds that support `ALTER TABLE ... EXPORT PARTITION ... TO TABLE ...`, a table created on the\n"
        "engine-less path in a `DataLakeCatalog` database SHALL be a valid export destination: an export\n"
        "from a `MergeTree` source whose partition key matches the destination's Iceberg partition spec\n"
        "SHALL complete, the exported rows SHALL be readable through the catalog table, and an external\n"
        "reader SHALL see them.\n"
        "\n"
        "Note: `EXPORT PARTITION` is an Altinity Antalya feature (SRS-047); scenarios for this requirement\n"
        "are skipped on builds without it.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.3",
)

RQ_Iceberg_NativeCreateDrop_RBAC = Requirement(
    name="RQ.Iceberg.NativeCreateDrop.RBAC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Native `CREATE TABLE` and `DROP TABLE` in a `DataLakeCatalog` database SHALL be governed by the\n"
        "standard `CREATE TABLE` and `DROP TABLE` privileges on that database: a user without\n"
        "`CREATE TABLE ON catalog_db.*` SHALL get `ACCESS_DENIED` and nothing SHALL be registered in the\n"
        "catalog; a user without `DROP TABLE ON catalog_db.*` SHALL get `ACCESS_DENIED` and the table SHALL\n"
        "stay registered. A user granted the privileges SHALL be able to create and drop tables without\n"
        "holding the object storage credentials, which stay inside the database definition.\n"
    ),
    link=None,
    level=2,
    num="11.1",
)

SRS_049_ClickHouse_Native_CREATE_TABLE_and_DROP_TABLE_for_DataLakeCatalog = Specification(
    name="SRS-049 ClickHouse Native CREATE TABLE and DROP TABLE for DataLakeCatalog",
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
        Heading(name="Terminology", level=2, num="1.1"),
        Heading(name="Feature Scope", level=1, num="2"),
        Heading(name="RQ.Iceberg.NativeCreateDrop.CreateTable", level=2, num="2.1"),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.CreateTable.ExplicitEngine",
            level=2,
            num="2.2",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.CreateTable.AsSource", level=2, num="2.3"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.SupportedCatalogs", level=2, num="2.4"
        ),
        Heading(name="Table Definition", level=1, num="3"),
        Heading(name="RQ.Iceberg.NativeCreateDrop.Schema.Columns", level=2, num="3.1"),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy", level=2, num="3.2"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy.RejectedExpressions",
            level=2,
            num="3.3",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy.TransformParameters",
            level=2,
            num="3.4",
        ),
        Heading(name="RQ.Iceberg.NativeCreateDrop.Schema.OrderBy", level=2, num="3.5"),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedStorageClauses",
            level=2,
            num="3.6",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedColumnModifiers",
            level=2,
            num="3.7",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedTableElements",
            level=2,
            num="3.8",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Schema.NonTableObjects",
            level=2,
            num="3.9",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Schema.EngineSettings",
            level=2,
            num="3.10",
        ),
        Heading(name="Table Location and Namespaces", level=1, num="4"),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Location.Resolution", level=2, num="4.1"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Location.DefaultBaseLocation",
            level=2,
            num="4.2",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Location.DerivedFromStorageEndpoint",
            level=2,
            num="4.3",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Location.VirtualHostedStyle",
            level=2,
            num="4.4",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Location.BackendConsistency",
            level=2,
            num="4.5",
        ),
        Heading(name="RQ.Iceberg.NativeCreateDrop.Location.Azure", level=2, num="4.6"),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Namespace.AutoCreate", level=2, num="4.7"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Namespace.DefaultLocation",
            level=2,
            num="4.8",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Namespace.Nested", level=2, num="4.9"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Namespace.Filtered", level=2, num="4.10"
        ),
        Heading(name="Explicit Engine Path", level=1, num="5"),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.ExplicitEngine.IcebergFamilyOnly",
            level=2,
            num="5.1",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.ExplicitEngine.BackendMismatch",
            level=2,
            num="5.2",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.ExplicitEngine.GenericIcebergEngine",
            level=2,
            num="5.3",
        ),
        Heading(name="Written Metadata", level=1, num="6"),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Metadata.InitialFile", level=2, num="6.1"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Metadata.Compression", level=2, num="6.2"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Metadata.FirstCommit", level=2, num="6.3"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Metadata.ExternalReader",
            level=2,
            num="6.4",
        ),
        Heading(name="Concurrency and Idempotency", level=1, num="7"),
        Heading(name="RQ.Iceberg.NativeCreateDrop.IfNotExists", level=2, num="7.1"),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.IfNotExists.ConcurrentCreate",
            level=2,
            num="7.2",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.LeftoverMetadata", level=2, num="7.3"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.FailedCreateLeavesNoTrace",
            level=2,
            num="7.4",
        ),
        Heading(name="DROP TABLE", level=1, num="8"),
        Heading(name="RQ.Iceberg.NativeCreateDrop.Drop", level=2, num="8.1"),
        Heading(name="RQ.Iceberg.NativeCreateDrop.Drop.KeepData", level=2, num="8.2"),
        Heading(name="RQ.Iceberg.NativeCreateDrop.Drop.Purge", level=2, num="8.3"),
        Heading(name="RQ.Iceberg.NativeCreateDrop.Drop.Setting", level=2, num="8.4"),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Drop.QueryLevelSetting",
            level=2,
            num="8.5",
        ),
        Heading(name="RQ.Iceberg.NativeCreateDrop.Drop.IfExists", level=2, num="8.6"),
        Heading(name="RQ.Iceberg.NativeCreateDrop.Drop.Glue", level=2, num="8.7"),
        Heading(name="RQ.Iceberg.NativeCreateDrop.Drop.S3Tables", level=2, num="8.8"),
        Heading(name="Distributed DDL and Visibility", level=1, num="9"),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.OnCluster.Rejected", level=2, num="9.1"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.OnCluster.WorkerGuard", level=2, num="9.2"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.SharedCatalogVisibility",
            level=2,
            num="9.3",
        ),
        Heading(name="Lifecycle After Creation", level=1, num="10"),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Lifecycle.InsertAlterSelect",
            level=2,
            num="10.1",
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Lifecycle.Recreate", level=2, num="10.2"
        ),
        Heading(
            name="RQ.Iceberg.NativeCreateDrop.Lifecycle.ExportPartitionDestination",
            level=2,
            num="10.3",
        ),
        Heading(name="Access Control", level=1, num="11"),
        Heading(name="RQ.Iceberg.NativeCreateDrop.RBAC", level=2, num="11.1"),
    ),
    requirements=(
        RQ_Iceberg_NativeCreateDrop_CreateTable,
        RQ_Iceberg_NativeCreateDrop_CreateTable_ExplicitEngine,
        RQ_Iceberg_NativeCreateDrop_CreateTable_AsSource,
        RQ_Iceberg_NativeCreateDrop_SupportedCatalogs,
        RQ_Iceberg_NativeCreateDrop_Schema_Columns,
        RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy,
        RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy_RejectedExpressions,
        RQ_Iceberg_NativeCreateDrop_Schema_PartitionBy_TransformParameters,
        RQ_Iceberg_NativeCreateDrop_Schema_OrderBy,
        RQ_Iceberg_NativeCreateDrop_Schema_UnsupportedStorageClauses,
        RQ_Iceberg_NativeCreateDrop_Schema_UnsupportedColumnModifiers,
        RQ_Iceberg_NativeCreateDrop_Schema_UnsupportedTableElements,
        RQ_Iceberg_NativeCreateDrop_Schema_NonTableObjects,
        RQ_Iceberg_NativeCreateDrop_Schema_EngineSettings,
        RQ_Iceberg_NativeCreateDrop_Location_Resolution,
        RQ_Iceberg_NativeCreateDrop_Location_DefaultBaseLocation,
        RQ_Iceberg_NativeCreateDrop_Location_DerivedFromStorageEndpoint,
        RQ_Iceberg_NativeCreateDrop_Location_VirtualHostedStyle,
        RQ_Iceberg_NativeCreateDrop_Location_BackendConsistency,
        RQ_Iceberg_NativeCreateDrop_Location_Azure,
        RQ_Iceberg_NativeCreateDrop_Namespace_AutoCreate,
        RQ_Iceberg_NativeCreateDrop_Namespace_DefaultLocation,
        RQ_Iceberg_NativeCreateDrop_Namespace_Nested,
        RQ_Iceberg_NativeCreateDrop_Namespace_Filtered,
        RQ_Iceberg_NativeCreateDrop_ExplicitEngine_IcebergFamilyOnly,
        RQ_Iceberg_NativeCreateDrop_ExplicitEngine_BackendMismatch,
        RQ_Iceberg_NativeCreateDrop_ExplicitEngine_GenericIcebergEngine,
        RQ_Iceberg_NativeCreateDrop_Metadata_InitialFile,
        RQ_Iceberg_NativeCreateDrop_Metadata_Compression,
        RQ_Iceberg_NativeCreateDrop_Metadata_FirstCommit,
        RQ_Iceberg_NativeCreateDrop_Metadata_ExternalReader,
        RQ_Iceberg_NativeCreateDrop_IfNotExists,
        RQ_Iceberg_NativeCreateDrop_IfNotExists_ConcurrentCreate,
        RQ_Iceberg_NativeCreateDrop_LeftoverMetadata,
        RQ_Iceberg_NativeCreateDrop_FailedCreateLeavesNoTrace,
        RQ_Iceberg_NativeCreateDrop_Drop,
        RQ_Iceberg_NativeCreateDrop_Drop_KeepData,
        RQ_Iceberg_NativeCreateDrop_Drop_Purge,
        RQ_Iceberg_NativeCreateDrop_Drop_Setting,
        RQ_Iceberg_NativeCreateDrop_Drop_QueryLevelSetting,
        RQ_Iceberg_NativeCreateDrop_Drop_IfExists,
        RQ_Iceberg_NativeCreateDrop_Drop_Glue,
        RQ_Iceberg_NativeCreateDrop_Drop_S3Tables,
        RQ_Iceberg_NativeCreateDrop_OnCluster_Rejected,
        RQ_Iceberg_NativeCreateDrop_OnCluster_WorkerGuard,
        RQ_Iceberg_NativeCreateDrop_SharedCatalogVisibility,
        RQ_Iceberg_NativeCreateDrop_Lifecycle_InsertAlterSelect,
        RQ_Iceberg_NativeCreateDrop_Lifecycle_Recreate,
        RQ_Iceberg_NativeCreateDrop_Lifecycle_ExportPartitionDestination,
        RQ_Iceberg_NativeCreateDrop_RBAC,
    ),
    content=r"""
# SRS-049 ClickHouse Native CREATE TABLE and DROP TABLE for DataLakeCatalog
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
    * 1.1 [Terminology](#terminology)
* 2 [Feature Scope](#feature-scope)
    * 2.1 [RQ.Iceberg.NativeCreateDrop.CreateTable](#rqicebergnativecreatedropcreatetable)
    * 2.2 [RQ.Iceberg.NativeCreateDrop.CreateTable.ExplicitEngine](#rqicebergnativecreatedropcreatetableexplicitengine)
    * 2.3 [RQ.Iceberg.NativeCreateDrop.CreateTable.AsSource](#rqicebergnativecreatedropcreatetableassource)
    * 2.4 [RQ.Iceberg.NativeCreateDrop.SupportedCatalogs](#rqicebergnativecreatedropsupportedcatalogs)
* 3 [Table Definition](#table-definition)
    * 3.1 [RQ.Iceberg.NativeCreateDrop.Schema.Columns](#rqicebergnativecreatedropschemacolumns)
    * 3.2 [RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy](#rqicebergnativecreatedropschemapartitionby)
    * 3.3 [RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy.RejectedExpressions](#rqicebergnativecreatedropschemapartitionbyrejectedexpressions)
    * 3.4 [RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy.TransformParameters](#rqicebergnativecreatedropschemapartitionbytransformparameters)
    * 3.5 [RQ.Iceberg.NativeCreateDrop.Schema.OrderBy](#rqicebergnativecreatedropschemaorderby)
    * 3.6 [RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedStorageClauses](#rqicebergnativecreatedropschemaunsupportedstorageclauses)
    * 3.7 [RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedColumnModifiers](#rqicebergnativecreatedropschemaunsupportedcolumnmodifiers)
    * 3.8 [RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedTableElements](#rqicebergnativecreatedropschemaunsupportedtableelements)
    * 3.9 [RQ.Iceberg.NativeCreateDrop.Schema.NonTableObjects](#rqicebergnativecreatedropschemanontableobjects)
    * 3.10 [RQ.Iceberg.NativeCreateDrop.Schema.EngineSettings](#rqicebergnativecreatedropschemaenginesettings)
* 4 [Table Location and Namespaces](#table-location-and-namespaces)
    * 4.1 [RQ.Iceberg.NativeCreateDrop.Location.Resolution](#rqicebergnativecreatedroplocationresolution)
    * 4.2 [RQ.Iceberg.NativeCreateDrop.Location.DefaultBaseLocation](#rqicebergnativecreatedroplocationdefaultbaselocation)
    * 4.3 [RQ.Iceberg.NativeCreateDrop.Location.DerivedFromStorageEndpoint](#rqicebergnativecreatedroplocationderivedfromstorageendpoint)
    * 4.4 [RQ.Iceberg.NativeCreateDrop.Location.VirtualHostedStyle](#rqicebergnativecreatedroplocationvirtualhostedstyle)
    * 4.5 [RQ.Iceberg.NativeCreateDrop.Location.BackendConsistency](#rqicebergnativecreatedroplocationbackendconsistency)
    * 4.6 [RQ.Iceberg.NativeCreateDrop.Location.Azure](#rqicebergnativecreatedroplocationazure)
    * 4.7 [RQ.Iceberg.NativeCreateDrop.Namespace.AutoCreate](#rqicebergnativecreatedropnamespaceautocreate)
    * 4.8 [RQ.Iceberg.NativeCreateDrop.Namespace.DefaultLocation](#rqicebergnativecreatedropnamespacedefaultlocation)
    * 4.9 [RQ.Iceberg.NativeCreateDrop.Namespace.Nested](#rqicebergnativecreatedropnamespacenested)
    * 4.10 [RQ.Iceberg.NativeCreateDrop.Namespace.Filtered](#rqicebergnativecreatedropnamespacefiltered)
* 5 [Explicit Engine Path](#explicit-engine-path)
    * 5.1 [RQ.Iceberg.NativeCreateDrop.ExplicitEngine.IcebergFamilyOnly](#rqicebergnativecreatedropexplicitengineicebergfamilyonly)
    * 5.2 [RQ.Iceberg.NativeCreateDrop.ExplicitEngine.BackendMismatch](#rqicebergnativecreatedropexplicitenginebackendmismatch)
    * 5.3 [RQ.Iceberg.NativeCreateDrop.ExplicitEngine.GenericIcebergEngine](#rqicebergnativecreatedropexplicitenginegenericicebergengine)
* 6 [Written Metadata](#written-metadata)
    * 6.1 [RQ.Iceberg.NativeCreateDrop.Metadata.InitialFile](#rqicebergnativecreatedropmetadatainitialfile)
    * 6.2 [RQ.Iceberg.NativeCreateDrop.Metadata.Compression](#rqicebergnativecreatedropmetadatacompression)
    * 6.3 [RQ.Iceberg.NativeCreateDrop.Metadata.FirstCommit](#rqicebergnativecreatedropmetadatafirstcommit)
    * 6.4 [RQ.Iceberg.NativeCreateDrop.Metadata.ExternalReader](#rqicebergnativecreatedropmetadataexternalreader)
* 7 [Concurrency and Idempotency](#concurrency-and-idempotency)
    * 7.1 [RQ.Iceberg.NativeCreateDrop.IfNotExists](#rqicebergnativecreatedropifnotexists)
    * 7.2 [RQ.Iceberg.NativeCreateDrop.IfNotExists.ConcurrentCreate](#rqicebergnativecreatedropifnotexistsconcurrentcreate)
    * 7.3 [RQ.Iceberg.NativeCreateDrop.LeftoverMetadata](#rqicebergnativecreatedropleftovermetadata)
    * 7.4 [RQ.Iceberg.NativeCreateDrop.FailedCreateLeavesNoTrace](#rqicebergnativecreatedropfailedcreateleavesnotrace)
* 8 [DROP TABLE](#drop-table)
    * 8.1 [RQ.Iceberg.NativeCreateDrop.Drop](#rqicebergnativecreatedropdrop)
    * 8.2 [RQ.Iceberg.NativeCreateDrop.Drop.KeepData](#rqicebergnativecreatedropdropkeepdata)
    * 8.3 [RQ.Iceberg.NativeCreateDrop.Drop.Purge](#rqicebergnativecreatedropdroppurge)
    * 8.4 [RQ.Iceberg.NativeCreateDrop.Drop.Setting](#rqicebergnativecreatedropdropsetting)
    * 8.5 [RQ.Iceberg.NativeCreateDrop.Drop.QueryLevelSetting](#rqicebergnativecreatedropdropquerylevelsetting)
    * 8.6 [RQ.Iceberg.NativeCreateDrop.Drop.IfExists](#rqicebergnativecreatedropdropifexists)
    * 8.7 [RQ.Iceberg.NativeCreateDrop.Drop.Glue](#rqicebergnativecreatedropdropglue)
    * 8.8 [RQ.Iceberg.NativeCreateDrop.Drop.S3Tables](#rqicebergnativecreatedropdrops3tables)
* 9 [Distributed DDL and Visibility](#distributed-ddl-and-visibility)
    * 9.1 [RQ.Iceberg.NativeCreateDrop.OnCluster.Rejected](#rqicebergnativecreatedroponclusterrejected)
    * 9.2 [RQ.Iceberg.NativeCreateDrop.OnCluster.WorkerGuard](#rqicebergnativecreatedroponclusterworkerguard)
    * 9.3 [RQ.Iceberg.NativeCreateDrop.SharedCatalogVisibility](#rqicebergnativecreatedropsharedcatalogvisibility)
* 10 [Lifecycle After Creation](#lifecycle-after-creation)
    * 10.1 [RQ.Iceberg.NativeCreateDrop.Lifecycle.InsertAlterSelect](#rqicebergnativecreatedroplifecycleinsertalterselect)
    * 10.2 [RQ.Iceberg.NativeCreateDrop.Lifecycle.Recreate](#rqicebergnativecreatedroplifecyclerecreate)
    * 10.3 [RQ.Iceberg.NativeCreateDrop.Lifecycle.ExportPartitionDestination](#rqicebergnativecreatedroplifecycleexportpartitiondestination)
* 11 [Access Control](#access-control)
    * 11.1 [RQ.Iceberg.NativeCreateDrop.RBAC](#rqicebergnativecreatedroprbac)

## Introduction

A `DataLakeCatalog` database exposes the tables registered in an external Iceberg catalog
(Iceberg REST, AWS Glue, and others) as ClickHouse tables. Until now the catalog was a read-mostly
window: tables were created by an external engine (Spark, Trino, PyIceberg), or from ClickHouse
only by spelling out a full storage engine clause such as `ENGINE = IcebergS3(url, key, secret)`
inside the catalog database. That form duplicates the endpoint and credentials the database
definition already holds, leaks them into query logs, and is not portable between environments.

This specification covers **native table management** in a `DataLakeCatalog` database:

* `CREATE TABLE` with only columns, `PARTITION BY`, and `ORDER BY`, without an engine clause;
* `CREATE TABLE ... AS source_table`, inheriting the schema and, where representable, the
  partition and sorting keys of an existing table;
* `CREATE TABLE ... ENGINE = Iceberg*(...)`, the pre-existing explicit engine form, now sharing
  the same validation, namespace handling, and idempotency rules;
* `DROP TABLE`, which unregisters the table from the catalog and optionally asks the catalog to
  purge the data through the new `data_lake_delete_data_on_drop` setting.

The realistic setup is a shared lakehouse: ClickHouse creates a table, other engines attached to
the same catalog read and write it, and any of them may drop it. Every behaviour below is judged
by what an external Iceberg client observes in the catalog and in object storage, not only by
what ClickHouse itself reports.

Table names inside a `DataLakeCatalog` database are quoted with backticks and carry the namespace
separated by a dot:

```sql
CREATE TABLE catalog_db.`namespace.table_name`
(
    id Int64,
    name String,
    value Float64
)
PARTITION BY id
ORDER BY name;
```

The database engine gates (`allow_database_iceberg`, `allow_experimental_database_iceberg`,
`allow_database_glue_catalog`, `allow_experimental_database_glue_catalog`) apply as for any use of
the database. Writing rows into a created table additionally requires
`allow_experimental_insert_into_iceberg`.

Negative requirements name the expected error code, because several rejection paths are
distinguishable only by their code:

| Code | Meaning |
|---|---|
| `BAD_ARGUMENTS` | The statement asks for something Iceberg or the catalog cannot represent, or the location cannot be derived. |
| `NOT_IMPLEMENTED` | A valid ClickHouse construct that catalog-managed tables do not support (non-table objects, `ON CLUSTER`, unsupported catalog type, Glue purge). |
| `TABLE_ALREADY_EXISTS` | The catalog already has the table, or metadata files already occupy its location. |
| `SUPPORT_IS_DISABLED` | The catalog can only perform the operation with a setting the query did not enable. |
| `DATALAKE_DATABASE_ERROR` | The catalog service rejected or failed the request. |
| `CATALOG_NAMESPACE_DISABLED` | The namespace is excluded by the database's `namespaces` parameter. |

Regression tests live under the TestFlows package `iceberg.tests.iceberg_engine.native_create`.
The environment provides an Iceberg REST catalog (`altinity/ice-rest-catalog`) and a Glue catalog
(LocalStack), both over an S3-compatible warehouse, plus PyIceberg and a Spark container as
external readers. Backends that the environment cannot provide (Azure, HDFS, S3 Tables) are carried
by dedicated requirements so that a skipped scenario does not mark the shared behaviour unsatisfied.

Out of scope: creating or dropping the `DataLakeCatalog` database itself, `ALTER TABLE` semantics
beyond confirming they keep working on a natively created table, and writing to catalog types that
this feature does not support.

[ClickHouse]: https://clickhouse.com

### Terminology

| Term | Meaning |
|---|---|
| catalog | The external Iceberg catalog service a `DataLakeCatalog` database is attached to. In the tests: `ice-rest-catalog` (REST) or LocalStack Glue. |
| engine-less path | `CREATE TABLE` inside a `DataLakeCatalog` database with no `ENGINE` clause. [ClickHouse] builds the initial Iceberg metadata from the column list and asks the catalog to register the table. |
| explicit engine path | `CREATE TABLE ... ENGINE = IcebergS3(...)` (or another `Iceberg*` engine) inside a `DataLakeCatalog` database. [ClickHouse] writes the initial metadata file itself and then registers the table. |
| table location | The object storage URI under which the table's `metadata/` and `data/` directories live, e.g. `s3://warehouse/data/ns/tbl`. |
| base location | The prefix under which new tables are placed as `<base>/<namespace>/<table>`. |
| fixed-backend catalog | A catalog whose tables can live on exactly one storage type: Glue (S3), OneLake (Azure), BigLake (S3 API), or a REST catalog that reports a `default-base-location`. |
| purge | A `DROP TABLE` that asks the catalog to delete the table's data and metadata files, not only the catalog entry. |
| external reader | PyIceberg or Spark loading the table through the same catalog, used to confirm what [ClickHouse] wrote is a valid Iceberg table. |

## Feature Scope

### RQ.Iceberg.NativeCreateDrop.CreateTable
version: 1.0

[ClickHouse] SHALL support `CREATE TABLE` inside a `DataLakeCatalog` database without an `ENGINE`
clause. The statement SHALL:

* build a valid Iceberg table from the declared columns, `PARTITION BY`, and `ORDER BY`;
* register the table in the catalog under `<namespace>.<table>`;
* make the table immediately visible in `SHOW TABLES`, `system.tables`, and to an external
  reader attached to the same catalog;
* leave the table empty and readable (`SELECT count()` returns `0`);
* accept `INSERT` and return the inserted rows on `SELECT`.

Nothing in the statement carries a storage endpoint or credentials; both come from the database
definition.

```sql
CREATE TABLE lake.`analytics.daily_revenue`
(
    day Date,
    region String,
    revenue Float64
)
PARTITION BY toRelativeDayNum(day)
ORDER BY region;

INSERT INTO lake.`analytics.daily_revenue` VALUES ('2026-01-01', 'eu', 10.5)
SETTINGS allow_experimental_insert_into_iceberg = 1;

SELECT count() FROM lake.`analytics.daily_revenue`;
```

```text
count()
1
```

### RQ.Iceberg.NativeCreateDrop.CreateTable.ExplicitEngine
version: 1.0

[ClickHouse] SHALL continue to support `CREATE TABLE ... ENGINE = IcebergS3(url, key, secret)`
(and the other `Iceberg*` engines) inside a `DataLakeCatalog` database. On this path
[ClickHouse] writes the initial metadata file to the engine's location and registers the table in
the catalog, and the resulting table SHALL be indistinguishable from an engine-less one to every
reader: it appears in the catalog, reads back through the database, and loads in an external
reader.

The explicit engine path SHALL obey the same validation rules as the engine-less path for column
modifiers, storage clauses, non-table objects, and namespace handling, so a statement that is
rejected on one path for a schema reason is rejected on the other.

### RQ.Iceberg.NativeCreateDrop.CreateTable.AsSource
version: 1.0

[ClickHouse] SHALL support `CREATE TABLE catalog_db.\`ns.t\` AS source_db.source_table` inside a
`DataLakeCatalog` database:

* the column names and types of the source are copied into the Iceberg schema;
* the source's `PARTITION BY` is copied when every expression in it is one of the accepted
  Iceberg transforms (RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy);
* the source's `ORDER BY` is copied under the same condition;
* `PARTITION BY` and `ORDER BY` written explicitly on the new table take precedence over the
  source's;
* the source's engine, engine `SETTINGS`, `PRIMARY KEY`, `SAMPLE BY`, `TTL`, and table comment
  are NOT carried over, and if any of them is written explicitly on the new statement it is
  rejected (RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedStorageClauses);
* a source column carrying a modifier Iceberg cannot store (`DEFAULT`, `MATERIALIZED`, `ALIAS`,
  `EPHEMERAL`, `COMMENT`, `CODEC`, `TTL`, `STATISTICS`, column `SETTINGS`) causes the statement
  to be rejected with `BAD_ARGUMENTS` rather than silently creating a weaker table.

The source may be a `MergeTree` table with a functional partition key, which is the migration
case this form exists for.

```sql
CREATE TABLE lake.`migrated.events` AS default.events;
INSERT INTO lake.`migrated.events` SELECT * FROM default.events
SETTINGS allow_experimental_insert_into_iceberg = 1;
```

### RQ.Iceberg.NativeCreateDrop.SupportedCatalogs
version: 1.0

[ClickHouse] SHALL support native `CREATE TABLE` and `DROP TABLE` for Iceberg REST catalogs
(including OneLake, BigLake, and Delta Sharing variants) and for the AWS Glue catalog. For any
other catalog type of a `DataLakeCatalog` database (Unity, Hive Metastore, Paimon REST) both
statements SHALL fail with `NOT_IMPLEMENTED` and an error message that names the supported
catalog types, and SHALL NOT partially register or partially delete anything.

The regression environment exercises the REST (`ice-rest-catalog`) and Glue (LocalStack)
branches; every requirement in this specification applies to both unless it says otherwise.

## Table Definition

### RQ.Iceberg.NativeCreateDrop.Schema.Columns
version: 1.0

[ClickHouse] SHALL persist every declared column into the Iceberg schema with a stable field id
and the Iceberg type that corresponds to the ClickHouse type, such that:

* a non-`Nullable` column becomes a required Iceberg field and a `Nullable` column an optional
  one;
* nested types (`Array`, `Map`, `Tuple`) become `list`, `map`, and `struct` with their element
  fields assigned ids;
* an external reader reports the same column names, order, and types that [ClickHouse] reports
  in `DESCRIBE TABLE`;
* a value written by [ClickHouse] round-trips unchanged through `SELECT` and through the
  external reader for every supported primitive and nested type.

A `CREATE TABLE` with no columns SHALL be rejected with `BAD_ARGUMENTS`.

### RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy
version: 1.0

[ClickHouse] SHALL translate the `PARTITION BY` clause into the Iceberg partition spec using only
the transforms Iceberg defines:

| Expression | Iceberg transform |
|---|---|
| `<column>` | `identity` |
| `toYearNumSinceEpoch(<col>)` | `year` |
| `toMonthNumSinceEpoch(<col>)` | `month` |
| `toRelativeDayNum(<col>)` | `day` |
| `toRelativeHourNum(<col>)` | `hour` |
| `icebergTruncate(N, <col>)` | `truncate[N]` |
| `icebergBucket(N, <col>)` | `bucket[N]` |

Composite partitioning `PARTITION BY (expr1, expr2, ...)` SHALL produce one partition field per
expression, in order. A table created without `PARTITION BY` SHALL have an empty (unpartitioned)
spec. The spec written SHALL be the one an external reader loads, and rows inserted by
[ClickHouse] SHALL land under partition paths that reader agrees with.

### RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy.RejectedExpressions
version: 1.0

[ClickHouse] SHALL reject with `BAD_ARGUMENTS` a `PARTITION BY` expression that is not one of the
accepted transforms, for example `toYYYYMM(col)`, `intDiv(col, 10)`, `col % 7`, or an arbitrary
function call. The rejection SHALL happen before any request reaches the catalog: after the
failed statement the table SHALL NOT exist in the catalog and no metadata file SHALL exist at
the location the table would have used.

### RQ.Iceberg.NativeCreateDrop.Schema.PartitionBy.TransformParameters
version: 1.0

[ClickHouse] SHALL require the width of `icebergTruncate(N, col)` and the bucket count of
`icebergBucket(N, col)` to be a positive integer. `N = 0` or a negative `N` SHALL be rejected with
`BAD_ARGUMENTS` before the table is registered, so the catalog never holds a table whose
partition spec serialises as `bucket[0]`, `bucket[-1]`, or `truncate[0]` and cannot be read.

Reasoning: an invalid transform parameter is not caught by the catalog; it produces a registered
table every reader fails on, and the only remedy is a manual drop.

### RQ.Iceberg.NativeCreateDrop.Schema.OrderBy
version: 1.0

[ClickHouse] SHALL translate the `ORDER BY` clause into the Iceberg sort order:

* each column in `ORDER BY` becomes a sort field, in order;
* a table created without `ORDER BY` SHALL have the unsorted order (`order-id` 0, no fields);
* a non-empty sort order SHALL carry a non-zero `order-id` and SHALL be the order an external
  reader loads as the table's default sort order.

### RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedStorageClauses
version: 1.0

[ClickHouse] SHALL reject with `BAD_ARGUMENTS` a `CREATE TABLE` in a `DataLakeCatalog` database
that carries any storage clause Iceberg cannot persist: `PRIMARY KEY`, `SAMPLE BY`, `TTL`, and
`UNIQUE KEY`. On the engine-less path engine `SETTINGS` SHALL also be rejected, because there is no
engine to receive them. The error message SHALL name the offending clause.

The rule applies to clauses written explicitly on a `CREATE TABLE ... AS` statement as well; a
clause inherited from the source table is dropped, an explicit one is rejected.

### RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedColumnModifiers
version: 1.0

[ClickHouse] SHALL reject with `BAD_ARGUMENTS` any column declaration carrying a modifier the
Iceberg schema cannot store: `DEFAULT`, `MATERIALIZED`, `ALIAS`, `EPHEMERAL`, `COMMENT`, `CODEC`,
`TTL`, `STATISTICS`, column-level `SETTINGS`, and column-level `PRIMARY KEY`. The error message
SHALL name the column. The rule SHALL hold on the engine-less path, on the explicit engine path,
and for columns inherited through `CREATE TABLE ... AS`.

Reasoning: a `DataLakeCatalog` table is re-instantiated from the catalog on every access, so any
property that is not in the Iceberg metadata would silently disappear after the `CREATE`.
Rejecting is the only way the user learns that the table does not have the semantics they wrote.

### RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedTableElements
version: 1.0

[ClickHouse] SHALL reject with `BAD_ARGUMENTS` a `CREATE TABLE` in a `DataLakeCatalog` database
that declares data-skipping indices, constraints, projections, or a table-level `PRIMARY KEY`
(whether written in the column list or as a storage clause), and a `CREATE TABLE` that carries a
table `COMMENT`. Since `CREATE TABLE ... AS` inherits the source's comment, a source with a comment
SHALL be rejected the same way.

### RQ.Iceberg.NativeCreateDrop.Schema.NonTableObjects
version: 1.0

[ClickHouse] SHALL support only plain `CREATE TABLE` in a `DataLakeCatalog` database. The
following SHALL fail with `NOT_IMPLEMENTED` and leave nothing in the catalog:

* `CREATE VIEW` and `CREATE MATERIALIZED VIEW`;
* `CREATE DICTIONARY`;
* `ATTACH TABLE`;
* `CREATE TABLE ... CLONE AS`;
* `CREATE OR REPLACE TABLE` and `REPLACE TABLE`.

### RQ.Iceberg.NativeCreateDrop.Schema.EngineSettings
version: 1.0

On the explicit engine path [ClickHouse] SHALL accept engine `SETTINGS` and apply them as the
engine's data lake storage settings during creation, for example `iceberg_format_version`. This is
the positive control for RQ.Iceberg.NativeCreateDrop.Schema.UnsupportedStorageClauses: the same
`SETTINGS` clause that is rejected without an engine is honoured with one, and the resulting
metadata reflects the setting's value.

```sql
CREATE TABLE lake.`ns.v2_table` (id Int64)
ENGINE = IcebergS3('http://minio:9000/warehouse/data/ns/v2_table/', 'admin', 'password')
SETTINGS iceberg_format_version = 2;
```

## Table Location and Namespaces

### RQ.Iceberg.NativeCreateDrop.Location.Resolution
version: 1.0

On the engine-less path [ClickHouse] SHALL place a new table at `<base>/<namespace>/<table>`,
where `<base>` is resolved in this order:

1. the `default-base-location` the catalog reports, when the catalog reports one;
2. otherwise the database setting `default_base_location`;
3. otherwise a location derived from the database setting `storage_endpoint`
   (RQ.Iceberg.NativeCreateDrop.Location.DerivedFromStorageEndpoint).

When none of the three is available the statement SHALL fail with `BAD_ARGUMENTS` and a message
naming `default_base_location` and `storage_endpoint`. The resolved location SHALL be the
`location` an external reader sees on the loaded table, and the `metadata/` and `data/`
directories SHALL be created directly under it.

### RQ.Iceberg.NativeCreateDrop.Location.DefaultBaseLocation
version: 1.0

[ClickHouse] SHALL support the `DataLakeCatalog` database setting `default_base_location`, a full
URI such as `s3://warehouse/data`, as the base under which engine-less `CREATE TABLE` places
tables when the catalog does not report a base location itself. Trailing slashes SHALL be
ignored, so `s3://warehouse/data/` and `s3://warehouse/data` place tables identically. The setting
SHALL be visible in `SHOW CREATE DATABASE`.

```sql
CREATE DATABASE lake
ENGINE = DataLakeCatalog('http://ice-rest-catalog:5000', 'admin', 'password')
SETTINGS catalog_type = 'rest', storage_endpoint = 'http://minio:9000/warehouse',
         default_base_location = 's3://warehouse/data';
```

### RQ.Iceberg.NativeCreateDrop.Location.DerivedFromStorageEndpoint
version: 1.0

When neither the catalog nor `default_base_location` supplies a base, [ClickHouse] SHALL derive
the S3 location from the path component of `storage_endpoint`: for
`storage_endpoint = 'http://minio:9000/warehouse'` a table `ns.tbl` is placed at
`s3://warehouse/ns/tbl`, and for `http://minio:9000/warehouse/prefix` at
`s3://warehouse/prefix/ns/tbl`. A `storage_endpoint` whose path is empty (`http://minio:9000/`)
carries no bucket and SHALL cause `CREATE TABLE` to fail with `BAD_ARGUMENTS`.

### RQ.Iceberg.NativeCreateDrop.Location.VirtualHostedStyle
version: 1.0

When the database uses `storage_uri_style = 'virtual_hosted'`, [ClickHouse] SHALL NOT attempt to
derive the bucket from `storage_endpoint`, because a virtual-hosted host (`bucket.minio.example`,
`s3.us-east-1.amazonaws.com`, an IP address) cannot be split into bucket and service
unambiguously. An engine-less `CREATE TABLE` on such a database SHALL fail with `BAD_ARGUMENTS`
telling the user to set `default_base_location`, and SHALL succeed once `default_base_location`
is set.

### RQ.Iceberg.NativeCreateDrop.Location.BackendConsistency
version: 1.0

For a fixed-backend catalog, [ClickHouse] SHALL reject with `BAD_ARGUMENTS` a
`default_base_location` whose URI scheme names a different storage backend than the catalog's
(for example an `abfss://` base on a Glue database), because the catalog would reopen the table
with its own backend and the table would be unreadable immediately after creation. The check
SHALL run before anything is written or registered.

### RQ.Iceberg.NativeCreateDrop.Location.Azure
version: 1.0

For an Azure-backed catalog [ClickHouse] SHALL derive the table location in the `abfss` form
`abfss://<container>@<account-host>/<sub-path>/<namespace>/<table>` from either a
`https://<account-host>/<container>[/<sub-path>]` or an
`abfss://<container>@<account-host>[/<sub-path>]` storage endpoint, and SHALL reject with
`BAD_ARGUMENTS` an endpoint that lacks the account host or the container.

Note: the regression environment has no Azure service; this requirement carries the Azure branch
of location resolution so that the S3 coverage stands on its own.

### RQ.Iceberg.NativeCreateDrop.Namespace.AutoCreate
version: 1.0

[ClickHouse] SHALL create the target namespace in the catalog when it does not exist yet, before
registering the table, so that `CREATE TABLE lake.\`new_ns.t\`` succeeds against a catalog that
has never seen `new_ns`. When the namespace already exists it SHALL be reused unchanged, and
[ClickHouse] SHALL NOT issue a create request for it (a principal that may create tables but not
namespaces stays able to create tables in a pre-provisioned namespace).

The namespace SHALL be created only after all local validation has passed: a `CREATE TABLE`
rejected for a schema, clause, or location reason SHALL leave no new namespace behind.

### RQ.Iceberg.NativeCreateDrop.Namespace.DefaultLocation
version: 1.0

When [ClickHouse] creates a namespace it SHALL register the namespace base
(`<base>/<namespace>`) as the namespace's default location, never the first table's own
directory. Consequently a second table created later in the same namespace without an explicit
location SHALL land beside the first table, not inside it.

On the explicit engine path the namespace base is known only when the engine's path follows the
`<base>/<namespace>/<table>` layout; when it does not, [ClickHouse] SHALL register the namespace
with no default location rather than with the table's directory.

### RQ.Iceberg.NativeCreateDrop.Namespace.Nested
version: 1.0

[ClickHouse] SHALL support multi-level namespaces written with dots, such as
`lake.\`a.b.c.table\``: the namespace SHALL be sent to a REST catalog as the segment list
`["a", "b", "c"]`, the table SHALL be created at `<base>/a.b.c/table` or an equivalent the
catalog resolves, and `INSERT` and `ALTER TABLE ... ADD COLUMN` on the created table SHALL
succeed, since both update the catalog through the same identifier.

### RQ.Iceberg.NativeCreateDrop.Namespace.Filtered
version: 1.0

When a `DataLakeCatalog` database restricts visibility with its `namespaces` parameter,
[ClickHouse] SHALL reject both `CREATE TABLE` and `DROP TABLE` targeting a namespace outside the
allowed set with `CATALOG_NAMESPACE_DISABLED`, and SHALL NOT contact the catalog for the table.

## Explicit Engine Path

### RQ.Iceberg.NativeCreateDrop.ExplicitEngine.IcebergFamilyOnly
version: 1.0

[ClickHouse] SHALL reject with `BAD_ARGUMENTS` a `CREATE TABLE` inside a `DataLakeCatalog`
database whose explicit engine is not an `Iceberg*` engine (for example `MergeTree`, `Memory`,
`S3`, `DeltaLake`). The message SHALL name the engine that was given.

### RQ.Iceberg.NativeCreateDrop.ExplicitEngine.BackendMismatch
version: 1.0

For a fixed-backend catalog, [ClickHouse] SHALL reject with `BAD_ARGUMENTS` an explicit engine
that pins a different backend: `IcebergAzure`, `IcebergHDFS`, or `IcebergLocal` on a Glue
database, for example. The error SHALL explain that the table would be reopened with the
catalog's backend and become unreadable, and SHALL name the backend the catalog stores tables on.
The matching engine (`IcebergS3` on Glue) SHALL be accepted. A catalog with no fixed backend
SHALL accept any `Iceberg*` engine.

### RQ.Iceberg.NativeCreateDrop.ExplicitEngine.GenericIcebergEngine
version: 1.0

[ClickHouse] SHALL reject with `BAD_ARGUMENTS` the generic `ENGINE = Iceberg(...)` inside a
`DataLakeCatalog` database attached to a fixed-backend catalog, because that engine chooses its
backend from a `disk` setting that is resolved only after database-level validation. The message
SHALL direct the user to the backend-specific engine.

## Written Metadata

### RQ.Iceberg.NativeCreateDrop.Metadata.InitialFile
version: 1.0

After a successful `CREATE TABLE` the table location SHALL contain exactly one metadata file under
`metadata/`, and the catalog's `metadata_location` for the table SHALL point at it. The file
SHALL be a valid Iceberg table metadata document with:

* the requested `format-version` (the default when none is requested);
* a single schema whose fields match RQ.Iceberg.NativeCreateDrop.Schema.Columns;
* a single partition spec and a single sort order matching the `PARTITION BY` and `ORDER BY`;
* no snapshots, no current snapshot, and an empty metadata log.

On the explicit engine path with a transactional (REST) catalog the file SHALL be named
`v1-<table-uuid>.metadata.json`; with a non-transactional catalog and on the engine-less Glue path
it SHALL be named `v1.metadata.json`; on the engine-less REST path the catalog server names it.
When `iceberg_use_version_hint` is enabled on the explicit engine path, `metadata/version-hint.text`
SHALL be written with content `1`.

### RQ.Iceberg.NativeCreateDrop.Metadata.Compression
version: 1.0

[ClickHouse] SHALL honour `iceberg_metadata_compression_method` on every path where it writes the
initial metadata file itself (the explicit engine path, and the engine-less Glue path). With
`iceberg_metadata_compression_method = 'gzip'` the registered `metadata_location` SHALL end in
`.gzip.metadata.json` and the object's content SHALL be a gzip stream, and the table SHALL be
readable and writable afterwards through the database.

### RQ.Iceberg.NativeCreateDrop.Metadata.FirstCommit
version: 1.0

The first `INSERT` into a natively created table SHALL produce a snapshot that carries no
`parent-snapshot-id` field (rather than a null one), SHALL set `current-snapshot-id`, and SHALL
add a `metadata-log` entry that references the previous metadata file, the one written at
`CREATE`. Subsequent inserts SHALL chain to the previous snapshot as parent. An external reader
SHALL load the table after each commit and see exactly the rows inserted.

Reasoning: an empty table has no current snapshot, and a writer that assumes one existed emits
metadata that strict readers reject as malformed.

### RQ.Iceberg.NativeCreateDrop.Metadata.ExternalReader
version: 1.0

A table created by [ClickHouse] on either path SHALL be a first-class Iceberg table to external
clients attached to the same catalog:

* PyIceberg `load_table` succeeds and reports the same schema, partition spec, sort order, and
  location that [ClickHouse] wrote;
* after [ClickHouse] inserts rows, PyIceberg and Spark scans return exactly those rows;
* after Spark inserts rows into the table, [ClickHouse] returns them.

Regression scenarios SHALL use both PyIceberg and the Spark container where the catalog is
reachable from both; Spark reads the REST catalog only.

## Concurrency and Idempotency

### RQ.Iceberg.NativeCreateDrop.IfNotExists
version: 1.0

[ClickHouse] SHALL support `CREATE TABLE IF NOT EXISTS` in a `DataLakeCatalog` database:

* when the table is not in the catalog it is created normally;
* when the table is already in the catalog the statement succeeds, creates nothing, and leaves
  the existing table's schema, data, and metadata location unchanged, whichever client created
  it;
* without `IF NOT EXISTS` the same situation fails with `TABLE_ALREADY_EXISTS`.

`CREATE TABLE IF NOT EXISTS ... AS SELECT` SHALL NOT insert into a table that already existed.

### RQ.Iceberg.NativeCreateDrop.IfNotExists.ConcurrentCreate
version: 1.0

When several clients race to create the same `<namespace>.<table>` (two [ClickHouse] nodes, or a
[ClickHouse] node and an external writer through the same catalog), exactly one SHALL win:

* the catalog ends with one table whose metadata location belongs to the winner;
* a loser that used `IF NOT EXISTS` reports success and creates nothing;
* a loser without `IF NOT EXISTS` fails with `TABLE_ALREADY_EXISTS`;
* the loser SHALL remove any initial metadata file it staged before it learned it lost, so the
  table location holds only the winner's files;
* a loser's `AS SELECT` SHALL NOT fill the winner's table.

The lost race SHALL be detected on every path: the catalog answering conflict (`409` from REST,
`AlreadyExists` from Glue), and the `If-None-Match: *` guarded metadata write answering
`PreconditionFailed`.

### RQ.Iceberg.NativeCreateDrop.LeftoverMetadata
version: 1.0

When the catalog has no table registered under `<namespace>.<table>` but Iceberg metadata files
already exist at the location the new table would use (typically left behind by an earlier
`DROP TABLE` without `data_lake_delete_data_on_drop`), [ClickHouse] SHALL NOT overwrite them and
SHALL NOT register a table over them:

* without `IF NOT EXISTS` the statement fails with `TABLE_ALREADY_EXISTS` and a message that
  names `data_lake_delete_data_on_drop` and tells the user to remove the leftover files or use a
  different location;
* with `IF NOT EXISTS` the statement succeeds, creates nothing, and the table stays absent from
  the catalog (a success that reports a table the catalog cannot see is not acceptable).

This differs from a path-based `ENGINE = IcebergS3` table outside any catalog, where
`IF NOT EXISTS` attaches to the existing metadata; inside a catalog, attaching would silently
adopt files of unknown provenance.

### RQ.Iceberg.NativeCreateDrop.FailedCreateLeavesNoTrace
version: 1.0

A `CREATE TABLE` that fails for any reason before the catalog acknowledges the registration
SHALL leave no trace: no catalog entry, no new namespace (RQ.Iceberg.NativeCreateDrop.Namespace.AutoCreate),
and no object under the table location, including a staged initial metadata file and
`version-hint.text`. In particular:

* a failure while writing `version-hint.text` after the metadata file was written SHALL remove
  the metadata file before the error propagates;
* a Glue `CreateTable` failure after the metadata file was staged SHALL remove the staged file;
* a rejected transform, clause, modifier, or location SHALL fail before any object is written.

Reasoning: the initial metadata write is guarded by `If-None-Match: *`, so a leftover from a
failed attempt would make every retry of the same `CREATE` report an existing table.

## DROP TABLE

### RQ.Iceberg.NativeCreateDrop.Drop
version: 1.0

[ClickHouse] SHALL support `DROP TABLE` for a table in a `DataLakeCatalog` database, whichever
client created it. After the statement the table SHALL be absent from the catalog (an external
client listing the namespace does not see it), absent from `SHOW TABLES`, and a `SELECT` against
it SHALL fail with `UNKNOWN_TABLE`. The drop SHALL work for a table that was never read through
this [ClickHouse] node before the `DROP`.

### RQ.Iceberg.NativeCreateDrop.Drop.KeepData
version: 1.0

By default (`data_lake_delete_data_on_drop = 0`) `DROP TABLE` SHALL only unregister the table:
every data file and metadata file under the table location SHALL still exist afterwards, and for a
REST catalog the request SHALL carry `purgeRequested=false`. The kept files remain a valid Iceberg
table that can be re-registered by an external client.

### RQ.Iceberg.NativeCreateDrop.Drop.Purge
version: 1.0

With `data_lake_delete_data_on_drop = 1`, `DROP TABLE` SHALL ask the catalog to purge the table:
for a REST catalog the request SHALL carry `purgeRequested=true`. When the catalog honours the
request, no object SHALL remain under the table location (data files, manifests, manifest lists,
metadata files, and the version hint). Whether data is actually removed is the catalog's decision;
[ClickHouse] SHALL report success when the catalog acknowledges the drop, and SHALL fail with
`DATALAKE_DATABASE_ERROR` when the catalog rejects it.

```sql
DROP TABLE lake.`analytics.scratch` SETTINGS data_lake_delete_data_on_drop = 1;
```

### RQ.Iceberg.NativeCreateDrop.Drop.Setting
version: 1.0

[ClickHouse] SHALL provide the query setting `data_lake_delete_data_on_drop` (`Bool`, default
`false`). The previously released `iceberg_delete_data_on_drop` SHALL remain accepted as an alias
with identical effect, so that setting either name enables the purge and `system.settings` reports
the new name. The setting SHALL be listed in the settings changes history for the release that
introduces it.

### RQ.Iceberg.NativeCreateDrop.Drop.QueryLevelSetting
version: 1.0

A `data_lake_delete_data_on_drop` value given at query level (`DROP TABLE ... SETTINGS ...`) or
session level SHALL be the value the drop acts on, even though the storage-level drop runs in a
background thread after the query has finished. This SHALL hold for catalog tables and for
path-based Iceberg tables (`ENGINE = IcebergS3(...)` and `ENGINE = IcebergLocal(...)` outside a
catalog), where [ClickHouse] deletes the files itself:

* `DROP TABLE t SYNC SETTINGS data_lake_delete_data_on_drop = 1` leaves zero objects under the
  table path;
* `DROP TABLE t SYNC SETTINGS data_lake_delete_data_on_drop = 0` leaves every object in place,
  regardless of a server-wide default of `1`.

When no query carried the setting to the table (the table was never loaded before a drop that
did not come from `DROP TABLE`), [ClickHouse] SHALL keep the data and log a warning rather than
delete on a fallback path.

### RQ.Iceberg.NativeCreateDrop.Drop.IfExists
version: 1.0

[ClickHouse] SHALL support `DROP TABLE IF EXISTS` in a `DataLakeCatalog` database: when the table
is not in the catalog the statement succeeds and does nothing, and when another client removes the
table between the existence check and the catalog call (REST `404`, Glue `EntityNotFound`) the
statement still succeeds. Without `IF EXISTS` dropping a table that is not in the catalog SHALL
fail with `UNKNOWN_TABLE`.

### RQ.Iceberg.NativeCreateDrop.Drop.Glue
version: 1.0

For a Glue catalog, `DROP TABLE` SHALL remove only the Glue catalog entry and SHALL keep the data
files. Because a purge cannot be honoured, `DROP TABLE ... SETTINGS data_lake_delete_data_on_drop = 1`
SHALL fail with `NOT_IMPLEMENTED`, the message SHALL say that the setting is not supported for the
Glue catalog, and the table SHALL remain registered and readable. `DROP TABLE IF EXISTS` with the
purge setting on a table that is not in Glue SHALL succeed as a no-op.

Reasoning: silently dropping the entry while the user asked for a purge would orphan the data
with no indication that it was kept.

### RQ.Iceberg.NativeCreateDrop.Drop.S3Tables
version: 1.0

For an S3 Tables catalog, whose API only offers a purging delete, `DROP TABLE` without
`data_lake_delete_data_on_drop = 1` SHALL fail with `SUPPORT_IS_DISABLED` and a message telling
the user to enable the setting, so that data the statement asked to keep is never deleted.
`DROP TABLE IF EXISTS` on a table that is not in the catalog SHALL still succeed as a no-op.

Note: the regression environment has no S3 Tables service; this requirement carries that branch
so the REST and Glue drop coverage stands on its own.

## Distributed DDL and Visibility

### RQ.Iceberg.NativeCreateDrop.OnCluster.Rejected
version: 1.0

[ClickHouse] SHALL reject `ON CLUSTER` for DDL whose target table is in a `DataLakeCatalog`
database. `CREATE TABLE ... ON CLUSTER`, `DROP TABLE ... ON CLUSTER`, `ALTER TABLE ... ON CLUSTER`,
and `RENAME TABLE ... ON CLUSTER` SHALL fail with `NOT_IMPLEMENTED` on the initiator, the message
SHALL explain that the catalog is shared and the query should run without `ON CLUSTER`, and the
query SHALL NOT be enqueued to the distributed DDL queue, so no node creates, drops, or alters the
table.

Reasoning: the catalog is the shared state. Running the same `CREATE` on every node would make
the nodes race against each other for one table.

### RQ.Iceberg.NativeCreateDrop.OnCluster.WorkerGuard
version: 1.0

When the initiator does not have the `DataLakeCatalog` database locally and therefore cannot
detect the target, the `ON CLUSTER` query is enqueued, and every worker that does have the
database SHALL reject it with `NOT_IMPLEMENTED` when executing its task, so that the table is
still not created on any node. A plain `ON CLUSTER` query against an ordinary database issued from
the same initiator SHALL still reach and run on the workers, proving the rejection is specific to
the catalog database.

### RQ.Iceberg.NativeCreateDrop.SharedCatalogVisibility
version: 1.0

A table created on one [ClickHouse] node SHALL be visible and readable on every other node that
has a `DataLakeCatalog` database attached to the same catalog, without any DDL on those nodes.
Cluster reads of the created table through `icebergS3Cluster` or the database with
`parallel_replicas_for_cluster_engines` SHALL return the same rows as a single-node read. A table
dropped on one node SHALL disappear from the other nodes' `SHOW TABLES` on their next listing.

## Lifecycle After Creation

### RQ.Iceberg.NativeCreateDrop.Lifecycle.InsertAlterSelect
version: 1.0

A natively created table SHALL support the full set of operations the database already supports
for externally created tables: `INSERT` (with `allow_experimental_insert_into_iceberg`),
`ALTER TABLE ... ADD COLUMN`, `DROP COLUMN`, `MODIFY COLUMN`, and `RENAME COLUMN`, `SELECT` with
predicate pushdown and partition pruning, `ALTER TABLE ... DELETE` where the format version
allows it, and `TRUNCATE`. After each operation the catalog's `metadata_location` SHALL advance
and an external reader SHALL observe the change.

### RQ.Iceberg.NativeCreateDrop.Lifecycle.Recreate
version: 1.0

After `DROP TABLE ... SETTINGS data_lake_delete_data_on_drop = 1`, creating a table with the same
`<namespace>.<table>` and the same resolved location SHALL succeed and yield an empty table.
After `DROP TABLE` without the purge, creating the same table at the same location SHALL be
refused per RQ.Iceberg.NativeCreateDrop.LeftoverMetadata, while creating it under a different
`default_base_location` SHALL succeed, and the kept files of the dropped table SHALL be untouched
by either attempt.

### RQ.Iceberg.NativeCreateDrop.Lifecycle.ExportPartitionDestination
version: 1.0

On builds that support `ALTER TABLE ... EXPORT PARTITION ... TO TABLE ...`, a table created on the
engine-less path in a `DataLakeCatalog` database SHALL be a valid export destination: an export
from a `MergeTree` source whose partition key matches the destination's Iceberg partition spec
SHALL complete, the exported rows SHALL be readable through the catalog table, and an external
reader SHALL see them.

Note: `EXPORT PARTITION` is an Altinity Antalya feature (SRS-047); scenarios for this requirement
are skipped on builds without it.

## Access Control

### RQ.Iceberg.NativeCreateDrop.RBAC
version: 1.0

Native `CREATE TABLE` and `DROP TABLE` in a `DataLakeCatalog` database SHALL be governed by the
standard `CREATE TABLE` and `DROP TABLE` privileges on that database: a user without
`CREATE TABLE ON catalog_db.*` SHALL get `ACCESS_DENIED` and nothing SHALL be registered in the
catalog; a user without `DROP TABLE ON catalog_db.*` SHALL get `ACCESS_DENIED` and the table SHALL
stay registered. A user granted the privileges SHALL be able to create and drop tables without
holding the object storage credentials, which stay inside the database definition.
""",
)
