# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.0.250110.1002922.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_Iceberg_DeletionVectors_Read = Requirement(
    name="RQ.Iceberg.DeletionVectors.Read",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support reading Iceberg format version 3 tables whose row-level deletes are\n"
        "stored as deletion vectors (`deletion-vector-v1` blobs in `Puffin` files). For every data file,\n"
        "[ClickHouse] SHALL exclude exactly the row positions recorded in that file's deletion vector, so\n"
        "the query result matches the logical table state committed by the writer.\n"
        "\n"
        "```sql\n"
        "SELECT * FROM icebergS3('http://minio:9000/warehouse/data/', 'minio', 'minio123');\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.1",
)

RQ_Iceberg_DeletionVectors_ReadOnly = Requirement(
    name="RQ.Iceberg.DeletionVectors.ReadOnly",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Deletion vector support SHALL be read-only. [ClickHouse] SHALL NOT produce, modify, or delete\n"
        "deletion vectors or `Puffin` files under any operation.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.2",
)

RQ_Iceberg_DeletionVectors_AccessForms = Requirement(
    name="RQ.Iceberg.DeletionVectors.AccessForms",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL apply deletion vectors identically across all Iceberg access forms:\n"
        "\n"
        "* Table functions: `icebergS3`, `icebergAzure`, `icebergLocal`\n"
        "* The `Iceberg` table engine\n"
        "* Tables from an Iceberg REST-catalog database (`DataLakeCatalog` engine)\n"
        "\n"
        "The same table read through any form SHALL return the same logical row set.\n"
        "\n"
        "For example, if the writer inserted ids `1..5` and deleted ids `2` and `4`, each access form can\n"
        "be compared using the same projection and ordering:\n"
        "\n"
        "```sql\n"
        "SELECT id FROM icebergS3('http://minio:9000/warehouse/t/', 'minio', 'minio123') ORDER BY id;\n"
        "SELECT id FROM iceberg_engine_table ORDER BY id;\n"
        "SELECT id FROM rest_catalog_db.t ORDER BY id;\n"
        "```\n"
        "\n"
        "```text\n"
        "id\n"
        "1\n"
        "3\n"
        "5\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.3",
)

RQ_Iceberg_DeletionVectors_StorageBackends = Requirement(
    name="RQ.Iceberg.DeletionVectors.StorageBackends",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support deletion vectors on tables stored in S3, Azure, and local filesystem\n"
        "storage. Correctness SHALL NOT depend on the storage backend. Cache-related requirements\n"
        "(section 12) apply only to S3 and Azure, because the `Puffin` cache is keyed partly on the object\n"
        "etag and local filesystem objects have none.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="2.4",
)

RQ_Iceberg_DeletionVectors_WriterOperations = Requirement(
    name="RQ.Iceberg.DeletionVectors.WriterOperations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL correctly read deletion vectors regardless of which external SQL operation\n"
        "produced them: `DELETE`, `UPDATE`, or `MERGE` (including `MERGE` statements combining\n"
        "`WHEN MATCHED THEN UPDATE`, `WHEN MATCHED THEN DELETE`, and `WHEN NOT MATCHED THEN INSERT`).\n"
        "Once a snapshot with valid metadata is committed, the producing operation is irrelevant to the\n"
        "read path: row counts, exact surviving rows, updated values, and inserted rows SHALL match the\n"
        "writer engine's own result.\n"
        "\n"
        "For example, given `(1, 'old')`, `(2, 'remove')`, and `(3, 'keep')`, an external writer could\n"
        "produce deletion vectors through operations such as:\n"
        "\n"
        "```sql\n"
        "DELETE FROM t WHERE id = 2;\n"
        "UPDATE t SET value = 'new' WHERE id = 1;\n"
        "MERGE INTO t USING changes c ON t.id = c.id\n"
        "WHEN MATCHED AND c.action = 'delete' THEN DELETE\n"
        "WHEN MATCHED THEN UPDATE SET value = c.value\n"
        "WHEN NOT MATCHED THEN INSERT (id, value) VALUES (c.id, c.value);\n"
        "```\n"
        "\n"
        "After an update of id `1`, deletion of id `2`, and insertion of id `4`, an illustrative\n"
        "ClickHouse read is:\n"
        "\n"
        "```sql\n"
        "SELECT id, value FROM iceberg_table ORDER BY id;\n"
        "```\n"
        "\n"
        "```text\n"
        "id  value\n"
        "1   new\n"
        "3   keep\n"
        "4   inserted\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="3.1",
)

RQ_Iceberg_DeletionVectors_EmptyVector = Requirement(
    name="RQ.Iceberg.DeletionVectors.EmptyVector",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL accept a deletion vector with `cardinality = 0` and no positions as valid.\n"
        "The referenced data file SHALL contribute all of its rows; the empty vector SHALL NOT hide the\n"
        "file and SHALL NOT fail the query. Repeated reads SHALL neither fail nor re-fetch the `Puffin`\n"
        "file when the cache is enabled.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.1",
)

RQ_Iceberg_DeletionVectors_AllRowsDeleted = Requirement(
    name="RQ.Iceberg.DeletionVectors.AllRowsDeleted",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support a deletion vector that deletes every row of its data file. The file\n"
        "SHALL contribute zero rows without being physically removed, and the query SHALL remain valid:\n"
        "\n"
        "```text\n"
        "file A → 100 rows, deletion vector deletes positions 0..99 → contributes 0 rows\n"
        "file B → 50 rows,  no deletion vector                      → contributes 50 rows\n"
        "table  → 50 rows visible\n"
        "```\n"
        "\n"
        "`SELECT *`, `SELECT count()`, aggregates, and filtered reads SHALL all reflect the empty\n"
        "contribution.\n"
        "\n"
        "Note: writers turn a `DELETE` whose predicate provably covers a whole data file into a\n"
        "metadata-only file drop (the file leaves the snapshot and no vector is written), so a\n"
        "full-file vector arises from position-level writes rather than from a file-aligned writer\n"
        "`DELETE`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.2",
)

RQ_Iceberg_DeletionVectors_BoundaryPositions = Requirement(
    name="RQ.Iceberg.DeletionVectors.BoundaryPositions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Deletion-vector positions are zero-based within the referenced data file. For a data file with\n"
        "`record_count = N`, [ClickHouse] SHALL:\n"
        "\n"
        "* apply position `0` (first row) and position `N - 1` (last row) correctly;\n"
        "* reject a position `>= N` with `ICEBERG_SPECIFICATION_VIOLATION`;\n"
        "* reject a declared cardinality `> N` with `ICEBERG_SPECIFICATION_VIOLATION`, before any\n"
        "  `Puffin` I/O is performed.\n"
        "\n"
        "For example, for rows with ids `10`, `20`, and `30` stored in that physical order, a vector\n"
        "containing positions `{0, 2}` produces:\n"
        "\n"
        "```sql\n"
        "SELECT id FROM iceberg_table ORDER BY id;\n"
        "```\n"
        "\n"
        "```text\n"
        "id\n"
        "20\n"
        "```\n"
        "\n"
        "A vector containing position `3` for the same three-row file fails instead of returning rows.\n"
        "\n"
        "Note: rejecting out-of-bounds positions and cardinalities is a [ClickHouse] fail-closed\n"
        "contract; the Iceberg specification does not define reader behavior for such metadata.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.3",
)

RQ_Iceberg_DeletionVectors_RowGroupBoundaries = Requirement(
    name="RQ.Iceberg.DeletionVectors.RowGroupBoundaries",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL interpret deletion-vector positions as absolute row numbers within the\n"
        "referenced Parquet file, never relative to a row group. For a file with row groups of 100 rows\n"
        "each and a vector deleting `{99, 100, 199, 200}`, exactly those four rows SHALL disappear —\n"
        "when all row groups are read, when some are pruned by a predicate, and when row groups are\n"
        "processed by parallel readers.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.4",
)

RQ_Iceberg_DeletionVectors_SharedPuffinFile = Requirement(
    name="RQ.Iceberg.DeletionVectors.SharedPuffinFile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "One `Puffin` file may hold several `deletion-vector-v1` blobs, each bound by its own\n"
        "`content_offset` / `content_size_in_bytes` from the manifest and carrying its own\n"
        "`referenced-data-file` property. [ClickHouse] SHALL apply to each data file only its own blob —\n"
        "no union and no cross-file contamination — both when all referenced files are read together and\n"
        "when a filter causes only one of them to be read.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.5",
)

RQ_Iceberg_DeletionVectors_SupportedPositionRange = Requirement(
    name="RQ.Iceberg.DeletionVectors.SupportedPositionRange",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The `deletion-vector-v1` format supports positive 64-bit row positions (the most significant\n"
        "bit must be 0): a position is split into a 32-bit key (the most significant 4 bytes) and a\n"
        "32-bit sub-position (the least significant 4 bytes), with one 32-bit roaring bitmap per key,\n"
        "bitmaps ordered by unsigned comparison of their keys.\n"
        "\n"
        "[ClickHouse] SHALL parse and apply valid vectors with bitmap keys in `[0, INT32_MAX - 1]` and\n"
        "positions up to the maximum supported position `(INT32_MAX - 1) * 2^32 + 2^31`\n"
        "(`0x7FFFFFFE80000000` — the Iceberg Java `RoaringPositionBitmap.MAX_POSITION`). A bitmap key\n"
        "or position beyond these limits SHALL be rejected with `BAD_ARGUMENTS`\n"
        "(`Invalid deletion vector bitmap key` / `is out of supported range`, see\n"
        "RQ.Iceberg.DeletionVectors.ErrorHandling.MalformedBlob).\n"
        "\n"
        "Note: the supported range is narrower than the literal `Puffin` spec, which allows any\n"
        "positive 64-bit position (most significant bit 0); both caps mirror the Iceberg Java\n"
        "reference implementation and are a deliberate [ClickHouse] contract.\n"
        "\n"
        "Position arithmetic SHALL be 64-bit throughout: a position in a high-key bucket SHALL NOT be\n"
        "truncated to its low 32 bits. For example, for a vector containing position `2^32 + 2`\n"
        "(key `1`, sub-position `2`) over a data file whose manifest `record_count` admits that\n"
        "position, the physical row at position `2` SHALL remain visible — a reader that truncates\n"
        "positions to 32 bits would wrongly delete it.\n"
        "\n"
        "Because a valid position must be below the data file's `record_count`\n"
        "(RQ.Iceberg.DeletionVectors.BoundaryPositions), a vector with a key `>= 1` can only reference\n"
        "a data file with more than `2^32` rows; this requirement is therefore verified with crafted\n"
        "vectors and manifest metadata rather than a multi-billion-row data file.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="4.6",
)

RQ_Iceberg_DeletionVectors_Coexistence_AcrossDataFiles = Requirement(
    name="RQ.Iceberg.DeletionVectors.Coexistence.AcrossDataFiles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Within one snapshot, different data files may independently use a deletion vector, a Parquet\n"
        "position delete, an equality delete, or no delete at all. [ClickHouse] SHALL compute each data\n"
        "file's result from its own delete metadata only.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.1",
)

RQ_Iceberg_DeletionVectors_Coexistence_SupersedesPositionDeletes = Requirement(
    name="RQ.Iceberg.DeletionVectors.Coexistence.SupersedesPositionDeletes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a deletion vector matches a data file, [ClickHouse] SHALL NOT apply Parquet position-delete\n"
        "files for that same data file (the Iceberg v3 supersession rule). Consequently:\n"
        "\n"
        "* a row present both in an old position-delete file and in a newer deletion vector SHALL be\n"
        "  removed exactly once;\n"
        "* a row present only in a superseded position-delete file SHALL remain visible unless the\n"
        "  deletion vector also covers it.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.2",
)

RQ_Iceberg_DeletionVectors_Coexistence_EqualityDeletes = Requirement(
    name="RQ.Iceberg.DeletionVectors.Coexistence.EqualityDeletes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Equality deletes SHALL apply independently of, and in addition to, a deletion vector on the same\n"
        "data file. The final result SHALL be as if the deletion-vector filter ran first (on absolute row\n"
        "positions) and the equality-delete predicate ran on the surviving rows.\n"
        "\n"
        "For example, given physical rows `(1, 'keep')`, `(2, 'dv')`, `(3, 'eq')`, and `(4, 'keep')`, a\n"
        "deletion vector for position `1` plus an equality delete for `id = 3` produces:\n"
        "\n"
        "```sql\n"
        "SELECT id, value FROM iceberg_table ORDER BY id;\n"
        "```\n"
        "\n"
        "```text\n"
        "id  value\n"
        "1   keep\n"
        "4   keep\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.3",
)

RQ_Iceberg_DeletionVectors_Coexistence_MultipleVectorsError = Requirement(
    name="RQ.Iceberg.DeletionVectors.Coexistence.MultipleVectorsError",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "If more than one live deletion-vector manifest entry references the same data file in one\n"
        "snapshot, [ClickHouse] SHALL fail the query with `ICEBERG_SPECIFICATION_VIOLATION`\n"
        '("Multiple deletion vectors match data file ..."). It SHALL NOT pick one of them and SHALL NOT\n'
        "union them.\n"
        "\n"
        'Note: the Iceberg specification only constrains writers ("at most one deletion vector is\n'
        'allowed per data file in a snapshot") and leaves reader behavior on a violation undefined;\n'
        "failing the query is a [ClickHouse] fail-closed contract.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.4",
)

RQ_Iceberg_DeletionVectors_Coexistence_FormatVersionUpgrade = Requirement(
    name="RQ.Iceberg.DeletionVectors.Coexistence.FormatVersionUpgrade",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "For an Iceberg v2 table with Parquet position deletes that is upgraded to format version 3:\n"
        "\n"
        "* the query result SHALL be identical immediately before and after the upgrade — previously\n"
        "  deleted rows SHALL NOT resurface;\n"
        "* after the first v3 delete produces a deletion vector, rows deleted before the upgrade SHALL\n"
        "  remain absent and newly deleted rows SHALL become absent, regardless of whether the writer\n"
        "  removed the superseded position-delete files or kept them alongside the vector. Writers are\n"
        "  required by the Iceberg spec to fold existing position deletes into a new vector, and the\n"
        "  supersession rule of RQ.Iceberg.DeletionVectors.Coexistence.SupersedesPositionDeletes\n"
        "  guarantees the folded vector is applied instead of the old files — so rows are neither\n"
        "  resurfaced nor double-deleted either way.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="5.5",
)

RQ_Iceberg_DeletionVectors_QuerySemantics_OperatorIndependence = Requirement(
    name="RQ.Iceberg.DeletionVectors.QuerySemantics.OperatorIndependence",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Deletion vectors SHALL be applied at the source, before any SQL operator runs, so the visible row\n"
        "set is fixed for the whole query. Every relational operator SHALL observe exactly that set,\n"
        "including:\n"
        "\n"
        "* `ORDER BY ... LIMIT n` (deleted rows straddling the limit boundary must not shrink the result)\n"
        "* `DISTINCT` (a value whose only occurrence is deleted disappears; a value with a deleted\n"
        "  duplicate remains)\n"
        "* `JOIN` against non-Iceberg tables (a deleted row must not join or affect join cardinality)\n"
        "* subqueries, CTEs, and derived tables (identical to a direct read)\n"
        "* `PREWHERE` (rows filtered before the deletion-vector transform must still map back to correct\n"
        "  absolute file row positions)\n"
        "\n"
        "For example, if id `3` is deleted from ids `1..5`, all of these queries observe the same visible\n"
        "row set before applying their own operators:\n"
        "\n"
        "```sql\n"
        "SELECT id FROM iceberg_table ORDER BY id LIMIT 3;       -- 1, 2, 4\n"
        "SELECT count() FROM iceberg_table PREWHERE id >= 3;     -- 2\n"
        "SELECT id FROM iceberg_table WHERE id IN (2, 3, 4)\n"
        "ORDER BY id;                                             -- 2, 4\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.1",
)

RQ_Iceberg_DeletionVectors_QuerySemantics_ProjectionIndependence = Requirement(
    name="RQ.Iceberg.DeletionVectors.QuerySemantics.ProjectionIndependence",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Row visibility SHALL be independent of the projected column list, because a deletion vector\n"
        "addresses physical row positions, not predicate values. When the writer executed\n"
        "`DELETE FROM t WHERE customer_id = 100`, a ClickHouse query selecting only other columns\n"
        "(`SELECT amount FROM ...`) SHALL still exclude the deleted rows without re-evaluating the\n"
        "original predicate.\n"
        "\n"
        "For example, if the writer deleted the physical row `(100, 42.50, 'paid')`, neither of these\n"
        "projections may expose it:\n"
        "\n"
        "```sql\n"
        "SELECT customer_id, amount, status FROM iceberg_table ORDER BY customer_id;\n"
        "SELECT amount FROM iceberg_table ORDER BY amount;\n"
        "```\n"
        "\n"
        "The second query does not need to project `customer_id` to apply the deletion vector.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.2",
)

RQ_Iceberg_DeletionVectors_QuerySemantics_CombinedFilters = Requirement(
    name="RQ.Iceberg.DeletionVectors.QuerySemantics.CombinedFilters",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a user predicate is combined with a deletion vector and an equality delete, the result SHALL\n"
        "be equivalent to applying, in order:\n"
        "\n"
        "```text\n"
        "physical data → deletion-vector visibility → other Iceberg delete semantics → user predicate\n"
        "```\n"
        "\n"
        "A row removed by any one of the three SHALL be absent; a row matched by several SHALL be absent\n"
        "exactly once; a row matched by none SHALL survive. The same result SHALL hold when the user\n"
        "predicate is expressed as `WHERE` and as `PREWHERE`.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.3",
)

RQ_Iceberg_DeletionVectors_QuerySemantics_SchemaEvolution = Requirement(
    name="RQ.Iceberg.DeletionVectors.QuerySemantics.SchemaEvolution",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "A deletion vector attached to a data file SHALL remain valid after schema evolution of the table,\n"
        "including `ADD COLUMN`, column rename, and column drop (both resolved by field id in Iceberg).\n"
        "Row visibility SHALL be identical for any projection over old or new columns, and values of a\n"
        "column added after the data file was written SHALL follow normal Iceberg schema-evolution\n"
        "semantics (`NULL` unless a default is defined) for the surviving rows.\n"
        "\n"
        "For example, after deleting id `2`, renaming `value` to `description`, and adding nullable column\n"
        "`category`, an old data file can be read as:\n"
        "\n"
        "```sql\n"
        "SELECT id, description, category FROM iceberg_table ORDER BY id;\n"
        "```\n"
        "\n"
        "```text\n"
        "id  description  category\n"
        "1   alpha        NULL\n"
        "3   gamma        NULL\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.4",
)

RQ_Iceberg_DeletionVectors_QuerySemantics_IOReductionOptimizations = Requirement(
    name="RQ.Iceberg.DeletionVectors.QuerySemantics.IOReductionOptimizations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL return an identical post-vector row set with any Parquet I/O-reducing read\n"
        "optimization enabled or disabled — including predicate push-down into the Parquet reader,\n"
        "page- and row-group-level pruning, and constant-value column detection that elides reads of\n"
        "column data whose value is identical across the file (derivable from column statistics).\n"
        "Deletion-vector positions are absolute row numbers of the data file; an optimization that\n"
        "skips reading part of the file SHALL NOT shift, drop, or resurrect rows, and counts and\n"
        "aggregates over a column whose read was elided SHALL still reflect only surviving rows.\n"
        "\n"
        "For example, for a table with a constant column `label = 'batch-1'` in every row and a\n"
        "deletion vector hiding 10 of 100 rows, both of the following SHALL return `90`:\n"
        "\n"
        "```sql\n"
        "SELECT count() FROM iceberg_table WHERE label = 'batch-1'\n"
        "SETTINGS input_format_parquet_filter_push_down = 0;\n"
        "\n"
        "SELECT count() FROM iceberg_table WHERE label = 'batch-1'\n"
        "SETTINGS input_format_parquet_filter_push_down = 1;\n"
        "```\n"
        "\n"
        "```text\n"
        "count()\n"
        "90\n"
        "```\n"
        "\n"
        "The same holds for any pairing of such optimizations, and for projections that read only the\n"
        "constant column:\n"
        "\n"
        "```sql\n"
        "SELECT label, count() FROM iceberg_table GROUP BY label;\n"
        "```\n"
        "\n"
        "```text\n"
        "label    count()\n"
        "batch-1  90\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.5",
)

RQ_Iceberg_DeletionVectors_QuerySemantics_ComplexSchemas = Requirement(
    name="RQ.Iceberg.DeletionVectors.QuerySemantics.ComplexSchemas",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Deletion vectors delete whole rows by position, independently of the schema's shape.\n"
        "[ClickHouse] SHALL apply deletion vectors correctly on tables with nested and complex column\n"
        "types — Iceberg `struct` (Tuple), `list` (Array), and `map` (Map), including nested\n"
        "combinations and `Nullable` fields — and on wide schemas. Reading any subset of nested\n"
        "fields SHALL exclude deleted rows, and counts and aggregates over nested fields SHALL\n"
        "reflect only surviving rows.\n"
        "\n"
        "For example, for an Iceberg schema\n"
        "\n"
        "```text\n"
        "id      BIGINT\n"
        "payload STRUCT<a: INT, tags: ARRAY<STRING>>\n"
        "attrs   MAP<STRING, STRING>\n"
        "```\n"
        "\n"
        "with rows `1`, `2`, `3` and a deletion vector hiding the row with `id = 2`:\n"
        "\n"
        "```sql\n"
        "SELECT id, payload.a, attrs['k'] FROM iceberg_table ORDER BY id;\n"
        "```\n"
        "\n"
        "```text\n"
        "id  payload.a  attrs['k']\n"
        "1   10         v1\n"
        "3   30         v3\n"
        "```\n"
        "\n"
        "```sql\n"
        "SELECT sum(length(payload.tags)) FROM iceberg_table;\n"
        "```\n"
        "\n"
        "returns the sum over rows `1` and `3` only.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="6.6",
)

RQ_Iceberg_DeletionVectors_TimeTravel = Requirement(
    name="RQ.Iceberg.DeletionVectors.TimeTravel",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Deletion vectors SHALL be discovered from the manifests of the selected snapshot only. A vector\n"
        "introduced in snapshot B SHALL be invisible when reading an earlier snapshot A, for both\n"
        "time-travel forms:\n"
        "\n"
        "```sql\n"
        "SELECT count() FROM iceberg_table SETTINGS iceberg_snapshot_id = <snapshot_a_id>;\n"
        "SELECT count() FROM iceberg_table SETTINGS iceberg_timestamp_ms = <before_delete_ms>;\n"
        "```\n"
        "\n"
        "With 100 rows inserted in snapshot A and 5 rows deleted via a deletion vector in snapshot B: the\n"
        "current read SHALL return 95 rows, snapshot A SHALL return the original 100 rows, and snapshot B\n"
        "read explicitly SHALL return 95 — as exact row sets, not merely counts.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.1",
)

RQ_Iceberg_DeletionVectors_TimeTravel_MultipleGenerations = Requirement(
    name="RQ.Iceberg.DeletionVectors.TimeTravel.MultipleGenerations",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Across several snapshots whose deletion-vector state differs (for example A: no vector,\n"
        "B: deletes `{1, 5}`, C: deletes `{1, 5, 9}`), each snapshot SHALL expose its own logical state\n"
        "regardless of the order in which snapshots are queried and regardless of caching: a vector\n"
        "cached while reading one snapshot SHALL never affect the result of another.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.2",
)

RQ_Iceberg_DeletionVectors_SnapshotRefresh = Requirement(
    name="RQ.Iceberg.DeletionVectors.SnapshotRefresh",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "After an external engine commits a `DELETE` producing a deletion vector, the next ClickHouse\n"
        "query SHALL observe the new snapshot without a server restart, without\n"
        "`SYSTEM DROP PUFFIN FILES CACHE`, and without dropping any other cache — with all caches at\n"
        "their default settings. This SHALL hold for both the table function and the `Iceberg` table\n"
        "engine.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.3",
)

RQ_Iceberg_DeletionVectors_SnapshotRefresh_QueryCache = Requirement(
    name="RQ.Iceberg.DeletionVectors.SnapshotRefresh.QueryCache",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "With the query result cache enabled (`use_query_cache = 1`), staleness across external\n"
        "Iceberg commits SHALL be bounded by the cache's own entry lifetime and never extended by\n"
        "deletion-vector state:\n"
        "\n"
        "* a cached result SHALL correspond to one committed snapshot — never a mix of pre- and\n"
        "  post-commit deletion-vector state;\n"
        "* after the cache entry expires (`query_cache_ttl`) or `SYSTEM DROP QUERY CACHE` is issued,\n"
        "  the next execution SHALL observe the current snapshot, including deletion vectors committed\n"
        "  since the entry was cached;\n"
        "* rows deleted by a committed deletion vector SHALL NOT be served from the query cache beyond\n"
        "  the entry lifetime.\n"
        "\n"
        "For example, for a 100-row table where an external `DELETE` later hides 10 rows:\n"
        "\n"
        "```sql\n"
        "SELECT count() FROM iceberg_table\n"
        "SETTINGS use_query_cache = 1, query_cache_ttl = 1;\n"
        "```\n"
        "\n"
        "```text\n"
        "count()\n"
        "100\n"
        "```\n"
        "\n"
        "```sql\n"
        "-- external writer commits a DELETE producing a deletion vector;\n"
        "-- after the 1-second entry lifetime has passed:\n"
        "SELECT count() FROM iceberg_table\n"
        "SETTINGS use_query_cache = 1, query_cache_ttl = 1;\n"
        "```\n"
        "\n"
        "```text\n"
        "count()\n"
        "90\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.4",
)

RQ_Iceberg_DeletionVectors_SequenceNumbers = Requirement(
    name="RQ.Iceberg.DeletionVectors.SequenceNumbers",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL honor Iceberg sequence-number rules when matching deletion vectors to data\n"
        "files:\n"
        "\n"
        "* a deletion vector committed at sequence number `N` SHALL NOT affect data files added after `N`,\n"
        "  even when the newer files contain rows with the same values;\n"
        "* a deletion vector referencing a data file no longer present in the snapshot SHALL be ignored,\n"
        "  not treated as an error.\n"
        "\n"
        "Note: writers are required to remove a vector when removing its data file, so an orphan entry\n"
        "indicates a non-compliant writer; ignoring it mirrors the Iceberg scan-planning rules (the\n"
        "vector matches no data file in the snapshot) and is a deliberate leniency, not an oversight.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.5",
)

RQ_Iceberg_DeletionVectors_SequenceNumbers_SameCommit = Requirement(
    name="RQ.Iceberg.DeletionVectors.SequenceNumbers.SameCommit",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Position deletes — deletion vectors included — apply to data files from the same commit: per\n"
        "the Iceberg scan-planning rules, a deletion vector SHALL be applied to a data file whose data\n"
        "sequence number is *equal* to the vector's own data sequence number, so that rows added and\n"
        "deleted in a single commit stay deleted. [ClickHouse] SHALL hide such rows exactly as it does\n"
        "when the vector's sequence number is strictly greater than the data file's.\n"
        "\n"
        "(Equality deletes differ: they apply only to data files with a *strictly older* data sequence\n"
        "number and never to files from their own commit.)\n"
        "\n"
        "For example, a single writer commit that adds a data file with ids `1..10` and, in the same\n"
        "commit, a deletion vector for positions `{0, 1}` of that file (as a `MERGE` rewriting and\n"
        "deleting rows it just inserted can produce) reads as:\n"
        "\n"
        "```sql\n"
        "SELECT count() FROM iceberg_table;\n"
        "```\n"
        "\n"
        "```text\n"
        "count()\n"
        "8\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.6",
)

RQ_Iceberg_DeletionVectors_Compaction = Requirement(
    name="RQ.Iceberg.DeletionVectors.Compaction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "After external data-file compaction (for example Spark's `rewrite_data_files`), deletion vectors\n"
        "that referenced the pre-compaction files SHALL NOT be applied to the rewritten files, and the\n"
        "logical query result SHALL be identical before and after the compaction.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="7.7",
)

RQ_Iceberg_DeletionVectors_Partitioning = Requirement(
    name="RQ.Iceberg.DeletionVectors.Partitioning",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL apply deletion vectors correctly on partitioned tables, including identity,\n"
        "bucket, and other transform partitioning. A query touching only a deletion-vector-bearing\n"
        "partition SHALL have the vector applied to it.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.1",
)

RQ_Iceberg_DeletionVectors_Partitioning_PruningSkipsVectorLoad = Requirement(
    name="RQ.Iceberg.DeletionVectors.Partitioning.PruningSkipsVectorLoad",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When partition pruning eliminates a data file from a query, [ClickHouse] SHALL also skip loading\n"
        "that file's deletion vector — no `Puffin` read SHALL occur for a pruned file (observable via the\n"
        "`PuffinFilesRead` profile event). Min/max pruning of delete files SHALL never prune a delete file\n"
        "that is actually needed for a data file being read.\n"
        "\n"
        "For example, if only partition `p = 2026` has a deletion vector, execute a query restricted to\n"
        "`p = 2025` with the client-supplied query id `dv_partition_pruning`, then check that query id:\n"
        "\n"
        "```sql\n"
        "SELECT count()\n"
        "FROM iceberg_table\n"
        "WHERE p = 2025\n"
        "SETTINGS log_profile_events = 1;\n"
        "\n"
        "SYSTEM FLUSH LOGS;\n"
        "\n"
        "SELECT ProfileEvents['PuffinFilesRead']\n"
        "FROM system.query_log\n"
        "WHERE type = 'QueryFinish' AND query_id = 'dv_partition_pruning';\n"
        "```\n"
        "\n"
        "```text\n"
        "0\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.2",
)

RQ_Iceberg_DeletionVectors_Partitioning_PartitionMatching = Requirement(
    name="RQ.Iceberg.DeletionVectors.Partitioning.PartitionMatching",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Per the Iceberg scan-planning rules, a deletion vector SHALL be matched to a data file only\n"
        "when all of the following hold:\n"
        "\n"
        "* the data file's `file_path` equals the vector's `referenced_data_file`;\n"
        "* the data file's data sequence number is less than or equal to the vector's data sequence\n"
        "  number (RQ.Iceberg.DeletionVectors.SequenceNumbers,\n"
        "  RQ.Iceberg.DeletionVectors.SequenceNumbers.SameCommit);\n"
        "* the data file's partition — both the partition spec and the partition values — is equal to\n"
        "  the deletion vector's partition.\n"
        "\n"
        "A deletion vector SHALL never be applied to a data file in a different partition. In\n"
        "particular, a vector manifest entry whose partition tuple does not match the partition of the\n"
        "data file named by its `referenced_data_file` — possible only through corrupted or\n"
        "hand-crafted metadata, since writers record a vector under the partition of the file it\n"
        "references — SHALL NOT be applied to that data file.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="8.3",
)

RQ_Iceberg_DeletionVectors_Count_TrivialCountOptimization = Requirement(
    name="RQ.Iceberg.DeletionVectors.Count.TrivialCountOptimization",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The metadata count shortcut SHALL fail closed in the presence of any live delete entries\n"
        "(a `Puffin` deletion vector is a position-delete entry): [ClickHouse] SHALL fall back to a real\n"
        "scan rather than answering from manifest sums. `SELECT count()` SHALL return the same value with\n"
        "`optimize_trivial_count_query = 1` and `= 0`, and both SHALL equal\n"
        "`SELECT count() FROM (SELECT * FROM table)`.\n"
        "\n"
        "For example, after 5 of 100 rows are deleted, the comparison is:\n"
        "\n"
        "```sql\n"
        "SELECT count() FROM iceberg_table SETTINGS optimize_trivial_count_query = 1; -- 95\n"
        "SELECT count() FROM iceberg_table SETTINGS optimize_trivial_count_query = 0; -- 95\n"
        "SELECT count() FROM (SELECT * FROM iceberg_table);                            -- 95\n"
        "```\n"
        "\n"
        "When the snapshot summary's `total-records` disagrees with the manifest sum on a table without\n"
        "deletes, the manifest sum SHALL win and a warning SHALL be logged.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.1",
)

RQ_Iceberg_DeletionVectors_Count_CountOnlyFastPath = Requirement(
    name="RQ.Iceberg.DeletionVectors.Count.CountOnlyFastPath",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The count-only fast path (`need_only_count`) SHALL be disabled for any data file with an attached\n"
        "deletion vector, position delete, or equality delete. Counts SHALL be identical with and without\n"
        "`PREWHERE`, with and without a filter, and for data files split across multiple row groups.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.2",
)

RQ_Iceberg_DeletionVectors_Count_CountFromFilesCache = Requirement(
    name="RQ.Iceberg.DeletionVectors.Count.CountFromFilesCache",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The count-from-files cache (`use_cache_for_count_from_files`) SHALL NOT be used or populated for\n"
        "data files that have delete entries attached, because its key (file path + modification time)\n"
        "does not change when a delete file is added or compacted away. In particular:\n"
        "\n"
        "```text\n"
        "1. SET use_cache_for_count_from_files = 1\n"
        "2. SELECT count() → N\n"
        "3. external DELETE producing a deletion vector\n"
        "4. SELECT count() → must be N - deleted, not the cached N\n"
        "```\n"
        "\n"
        "The reverse direction SHALL also hold: a count taken while deletes exist SHALL NOT be served\n"
        "stale after the deletes are compacted away.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="9.3",
)

RQ_Iceberg_DeletionVectors_ErrorHandling_MalformedBlob = Requirement(
    name="RQ.Iceberg.DeletionVectors.ErrorHandling.MalformedBlob",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject a structurally invalid deletion-vector blob payload with\n"
        "`BAD_ARGUMENTS` and a specific message, including at least:\n"
        "\n"
        "| Defect | Expected message fragment |\n"
        "|---|---|\n"
        "| CRC32 does not match the payload | `Deletion vector CRC mismatch` |\n"
        "| wrong 4-byte magic | `Invalid deletion vector magic` |\n"
        "| declared combined length inconsistent with the blob length | `does not match combined length` |\n"
        "| blob shorter than 12 bytes | `Deletion vector blob is too small` |\n"
        "| bitmap header shorter than 8 bytes | `Deletion vector bitmap is too small` |\n"
        "| bitmap truncated mid-key | `truncated while reading key` |\n"
        "| roaring container extends past the blob | `failed alloc while reading` (bounds-checked roaring deserializer, wrapped as `Failed to deserialize deletion vector roaring bitmap`) |\n"
        "| roaring bitmap fails internal validation | `failed internal validation` |\n"
        "| bitmap keys not strictly ascending | `must be sorted in ascending order` |\n"
        "| bitmap key negative or `> INT32_MAX - 1` | `Invalid deletion vector bitmap key` |\n"
        "| bitmap count negative or `> INT32_MAX` | `Invalid deletion vector bitmap count` |\n"
        "| trailing bytes after the last container | `trailing bytes` |\n"
        "| deserialized cardinality ≠ declared cardinality | `does not match deserialized row count` |\n"
        "| running cardinality exceeds the declared one mid-parse | `exceeds declared cardinality` |\n"
        "| a position exceeds the maximum representable position | `is out of supported range` |\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.1",
)

RQ_Iceberg_DeletionVectors_ErrorHandling_BlobMetadata = Requirement(
    name="RQ.Iceberg.DeletionVectors.ErrorHandling.BlobMetadata",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL validate the `Puffin` footer metadata of a deletion-vector blob and reject\n"
        "invalid metadata with `BAD_ARGUMENTS`, including at least:\n"
        "\n"
        "| Defect | Expected message fragment |\n"
        "|---|---|\n"
        "| blob `type` is not `deletion-vector-v1` | `unsupported blob type` |\n"
        "| `compression-codec` present and non-empty | `must omit 'compression-codec'` |\n"
        "| `referenced-data-file` missing or empty | `missing required property 'referenced-data-file'` |\n"
        "| `referenced-data-file` ≠ the data file being read | `does not match expected data file` |\n"
        "| `cardinality` missing or empty | `missing required property 'cardinality'` |\n"
        "| `cardinality` not an unsigned integer | `must be an unsigned integer` |\n"
        "| `cardinality` ≠ the manifest `record_count` | `does not match expected cardinality` |\n"
        "| footer-declared `offset`/`length` outside the blob payload region | `offset/length out of bounds` |\n"
        "| no in-bounds blob at the manifest's `(offset, length)` | `No Puffin footer blob at offset` |\n"
        "| two blobs at the same `(offset, length)` | `Multiple Puffin blobs claim offset` |\n"
        "\n"
        "Footer blob descriptors are bounds-validated against the blob payload region before the\n"
        "manifest's `(content_offset, content_size_in_bytes)` pair is matched against them, so an\n"
        "out-of-bounds footer declaration fails as `offset/length out of bounds` and never reaches the\n"
        "matching step.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.2",
)

RQ_Iceberg_DeletionVectors_ErrorHandling_BlobBounds = Requirement(
    name="RQ.Iceberg.DeletionVectors.ErrorHandling.BlobBounds",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject with `BAD_ARGUMENTS` a manifest-declared blob location that does not\n"
        "fit inside the `Puffin` file: negative offset or length, offset or length beyond the file size,\n"
        "and `offset + length` overflowing or exceeding the file size.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.3",
)

RQ_Iceberg_DeletionVectors_ErrorHandling_ManifestConsistency = Requirement(
    name="RQ.Iceberg.DeletionVectors.ErrorHandling.ManifestConsistency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL reject internally inconsistent Iceberg metadata with\n"
        "`ICEBERG_SPECIFICATION_VIOLATION`, including at least:\n"
        "\n"
        "* a deletion-vector manifest entry without `referenced_data_file` (position-delete lower/upper\n"
        "  bounds SHALL NOT be used as a fallback for deletion vectors);\n"
        "* a deletion-vector manifest entry with a negative `record_count`;\n"
        "* a data-file manifest entry missing `record_count` (required to bound vector positions) or with\n"
        "  a negative `record_count`;\n"
        "* a deletion-vector `record_count` greater than the data file's `record_count` (rejected before\n"
        "  any I/O);\n"
        "* two deletion vectors referencing the same data file (see\n"
        "  RQ.Iceberg.DeletionVectors.Coexistence.MultipleVectorsError).\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.4",
)

RQ_Iceberg_DeletionVectors_ErrorHandling_ResourceLimits = Requirement(
    name="RQ.Iceberg.DeletionVectors.ErrorHandling.ResourceLimits",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL enforce hard resource limits on deletion vectors, failing with\n"
        "`BAD_ARGUMENTS`:\n"
        "\n"
        "```text\n"
        'blob length > 2 GiB                → "exceeds absolute limit"\n'
        'declared cardinality > 100,000,000 → "exceeds materialization limit"\n'
        "```\n"
        "\n"
        "Validation is layered: for a fully buffered `Puffin` file, a hostile manifest length above\n"
        "2 GiB is rejected earlier, by the footer bounds/matching checks (the error names the hostile\n"
        "length, e.g. `No Puffin footer blob at offset 4 length 3221225472`) — the dedicated\n"
        "`exceeds absolute limit` message guards the unbuffered large-file path.\n"
        "\n"
        "The cardinality ceiling compares against the footer's `cardinality` property, so one `Puffin`\n"
        "read (the footer) is inherent; the ceiling SHALL reject before the vector payload is\n"
        "deserialized or allocated — `PuffinFilesRead` SHALL NOT exceed the single footer read for such\n"
        "a query.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.5",
)

RQ_Iceberg_DeletionVectors_ErrorHandling_NonParquetDataFiles = Requirement(
    name="RQ.Iceberg.DeletionVectors.ErrorHandling.NonParquetDataFiles",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Deletion vectors require file-relative row numbers, which only the Parquet readers provide. A\n"
        "deletion vector attached to a data file in any other format (ORC, Avro) SHALL fail with\n"
        '`NOT_IMPLEMENTED` and a message naming both the feature and the actual format: "Deletion vectors\n'
        'are only supported for data files of Parquet format in Iceberg, but got <format>".\n'
        "\n"
    ),
    link=None,
    level=2,
    num="10.6",
)

RQ_Iceberg_DeletionVectors_ErrorHandling_CompressedFooter = Requirement(
    name="RQ.Iceberg.DeletionVectors.ErrorHandling.CompressedFooter",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The `Puffin` format allows the footer payload to be LZ4-compressed (footer `Flags`, byte 0,\n"
        "bit 0; a single LZ4 frame with the content size present). Iceberg reference writers emit\n"
        "uncompressed footers, but a compressed footer is spec-legal.\n"
        "\n"
        "[ClickHouse] SHALL decompress an LZ4-compressed footer payload and return exactly the same\n"
        "result as for an equivalent file with an uncompressed footer. It SHALL fail closed on any\n"
        "footer flag construct it cannot interpret:\n"
        "\n"
        "* a compressed footer frame that does not declare its content size SHALL be rejected\n"
        "  (`LZ4_DECODER_FAILED`, `must declare content size`);\n"
        "* reserved footer flag bits set SHALL be rejected with `BAD_ARGUMENTS`\n"
        "  (`Unknown Puffin footer flags`).\n"
        "\n"
        "It SHALL NOT parse the compressed bytes as plain JSON, silently skip the deletion vectors, or\n"
        "return rows as if no vector existed.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="10.7",
)

RQ_Iceberg_DeletionVectors_Distributed_ClusterFunctions = Requirement(
    name="RQ.Iceberg.DeletionVectors.Distributed.ClusterFunctions",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "For every single-node requirement in this specification, the corresponding `*Cluster` table\n"
        "function read (for example `icebergS3Cluster`) SHALL return an identical result. Deletion-vector\n"
        "positions are resolved on the initiator and shipped to workers as part of the cluster read task.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.1",
)

RQ_Iceberg_DeletionVectors_Distributed_ProtocolFailClosed = Requirement(
    name="RQ.Iceberg.DeletionVectors.Distributed.ProtocolFailClosed",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "A cluster worker whose protocol version is too old to carry the deletion state SHALL cause an\n"
        "explicit `UNKNOWN_PROTOCOL` failure with no rows returned — never a silent read without deletes:\n"
        "\n"
        "* a worker without `excluded_rows` support (protocol < 5) would otherwise drop deletion vectors\n"
        "  and return deleted rows;\n"
        "* a worker without `iceberg_info` support (protocol < 3) would otherwise skip position/equality\n"
        "  delete transforms;\n"
        "* a worker without `file_bucket_info` support (protocol < 4) would otherwise read whole files\n"
        "  per bucket task and duplicate rows.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.2",
)

RQ_Iceberg_DeletionVectors_Distributed_SplitDataFile = Requirement(
    name="RQ.Iceberg.DeletionVectors.Distributed.SplitDataFile",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "When a single Parquet data file is split by row group across parallel threads or cluster nodes,\n"
        "each read task SHALL apply the deletion vector to the correct absolute positions in its range.\n"
        "For a file with deletions in every row group:\n"
        "\n"
        "```text\n"
        "single-threaded read == multi-threaded read == cluster read == count()\n"
        "```\n"
        "\n"
        "and all of them SHALL equal the writer-engine result, for any `max_threads` value and cluster\n"
        "size.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.3",
)

RQ_Iceberg_DeletionVectors_Distributed_SnapshotRefresh = Requirement(
    name="RQ.Iceberg.DeletionVectors.Distributed.SnapshotRefresh",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "After an external engine commits a `DELETE` producing a deletion vector, the next cluster\n"
        "read SHALL observe the new snapshot on **every** worker — without restarts and without\n"
        "dropping any cache — even though each node holds its own `Puffin` files cache and Iceberg\n"
        "metadata cache, including nodes whose caches were warmed on the previous snapshot. The\n"
        "cluster result SHALL equal the single-node result taken after the same commit.\n"
        "\n"
        "For example, for a 100-row table read through the cluster function, warmed on all nodes,\n"
        "where an external `DELETE` then hides 10 rows:\n"
        "\n"
        "```sql\n"
        "SELECT count() FROM icebergS3Cluster('cluster', 'http://minio:9000/warehouse/ns/tbl', ...);\n"
        "```\n"
        "\n"
        "```text\n"
        "count()   -- before the commit, caches warmed on every node\n"
        "100\n"
        "```\n"
        "\n"
        "```sql\n"
        "-- external writer commits the DELETE; very next cluster query:\n"
        "SELECT count() FROM icebergS3Cluster('cluster', 'http://minio:9000/warehouse/ns/tbl', ...);\n"
        "```\n"
        "\n"
        "```text\n"
        "count()\n"
        "90\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="11.4",
)

RQ_Iceberg_DeletionVectors_Cache_Setting = Requirement(
    name="RQ.Iceberg.DeletionVectors.Cache.Setting",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide the session setting `use_puffin_files_cache`, default `1`. With the\n"
        "cache enabled, a repeated query SHALL be served from cache (`PuffinFilesCacheHits` increases,\n"
        "`PuffinFilesRead` stays at 0). With `use_puffin_files_cache = 0`, every read SHALL re-fetch and\n"
        "re-parse the vector (`PuffinFilesRead` increases on every query) and results SHALL remain\n"
        "correct.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.1",
)

RQ_Iceberg_DeletionVectors_Cache_ServerSettings = Requirement(
    name="RQ.Iceberg.DeletionVectors.Cache.ServerSettings",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL provide the server settings `puffin_files_cache_policy` (default `SLRU`),\n"
        "`puffin_files_cache_size` (default 512 MiB, `0` disables), `puffin_files_cache_max_entries`\n"
        "(default 5000, `0` disables), and `puffin_files_cache_size_ratio` (default 0.5). Results SHALL\n"
        "remain correct with the cache disabled by server setting even when `use_puffin_files_cache = 1`,\n"
        "and `puffin_files_cache_size` SHALL be changeable without a restart with the live value\n"
        "reported.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.2",
)

RQ_Iceberg_DeletionVectors_Cache_Invalidation = Requirement(
    name="RQ.Iceberg.DeletionVectors.Cache.Invalidation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The cache SHALL never serve a stale deletion vector across Iceberg commits:\n"
        "\n"
        "* a new commit produces a new `Puffin` path → new cache key → new load; a previously cached\n"
        "  vector for the old path SHALL NOT be consulted;\n"
        "* if a `Puffin` object at the same path is replaced with different content, the changed etag\n"
        "  SHALL produce a different cache key;\n"
        "* `SYSTEM DROP PUFFIN FILES CACHE` SHALL never be required for correctness after a normal\n"
        "  Iceberg commit.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.3",
)

RQ_Iceberg_DeletionVectors_Cache_EtagBypass = Requirement(
    name="RQ.Iceberg.DeletionVectors.Cache.EtagBypass",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The absence of an etag SHALL NOT break the cache. When the storage object has no etag (for\n"
        "example local filesystem), [ClickHouse] SHALL build the cache key from the remaining components\n"
        "(storage identity, object path, blob offset and length, referenced data file, cardinalities):\n"
        "repeated reads of the same local table are served from the cache (`PuffinFilesCacheHits`\n"
        "increases) and results SHALL remain correct.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.4",
)

RQ_Iceberg_DeletionVectors_Cache_Eviction = Requirement(
    name="RQ.Iceberg.DeletionVectors.Cache.Eviction",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "With a cache deliberately smaller than the working set, [ClickHouse] SHALL evict entries\n"
        "(`PuffinFilesCacheWeightLost` increases) while query results remain correct. Empty deletion\n"
        "vectors SHALL be cached as explicit entries with minimal weight.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.5",
)

RQ_Iceberg_DeletionVectors_Cache_DropStatement = Requirement(
    name="RQ.Iceberg.DeletionVectors.Cache.DropStatement",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL support the statement:\n"
        "\n"
        "```sql\n"
        "SYSTEM DROP PUFFIN FILES CACHE;\n"
        "```\n"
        "\n"
        "It SHALL clear the cache so the next query records misses and re-reads the `Puffin` files, with\n"
        "an unchanged logical result.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.6",
)

RQ_Iceberg_DeletionVectors_Cache_RBAC = Requirement(
    name="RQ.Iceberg.DeletionVectors.Cache.RBAC",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "`SYSTEM DROP PUFFIN FILES CACHE` SHALL require the `SYSTEM DROP PUFFIN FILES CACHE` privilege\n"
        "(`GLOBAL` level, child of `SYSTEM DROP CACHE`). A user without it SHALL be denied; a user with\n"
        "the parent `SYSTEM DROP CACHE` privilege SHALL be allowed; `SHOW PRIVILEGES` SHALL list the\n"
        "privilege.\n"
        "\n"
        "An illustrative privilege check is:\n"
        "\n"
        "```sql\n"
        "CREATE USER cache_operator;\n"
        "GRANT SYSTEM DROP PUFFIN FILES CACHE ON *.* TO cache_operator;\n"
        "SHOW GRANTS FOR cache_operator;\n"
        "```\n"
        "\n"
        "```text\n"
        "GRANT SYSTEM DROP PUFFIN FILES CACHE ON *.* TO cache_operator\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.7",
)

RQ_Iceberg_DeletionVectors_Cache_Observability = Requirement(
    name="RQ.Iceberg.DeletionVectors.Cache.Observability",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "[ClickHouse] SHALL expose cache state via the `system.metrics` current metrics\n"
        "`PuffinFilesCacheBytes` and\n"
        "`PuffinFilesCacheFiles`, and per-query activity via the profile events `PuffinFilesRead`,\n"
        "`PuffinFileReadMicroseconds`, `PuffinFilesCacheHits`, `PuffinFilesCacheMisses`, and\n"
        "`PuffinFilesCacheWeightLost`. After a cold read of a table with deletion vectors: misses and\n"
        "reads increase, read time is non-zero, and the metrics reflect the resident entries. On a warm\n"
        "read: hits increase and `PuffinFilesRead` stays at 0.\n"
        "\n"
        "```sql\n"
        "SELECT ProfileEvents['PuffinFilesCacheHits'], ProfileEvents['PuffinFilesRead']\n"
        "FROM system.query_log\n"
        "WHERE type = 'QueryFinish' AND query_id = '...';\n"
        "```\n"
        "\n"
        "For a warm read, an illustrative result is:\n"
        "\n"
        "```text\n"
        "ProfileEvents['PuffinFilesCacheHits']  ProfileEvents['PuffinFilesRead']\n"
        "1                                      0\n"
        "```\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.8",
)

RQ_Iceberg_DeletionVectors_Cache_Concurrency = Requirement(
    name="RQ.Iceberg.DeletionVectors.Cache.Concurrency",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Two concurrent queries over the same cold deletion vector SHALL both return correct results, and\n"
        "the vector SHALL be loaded once (`PuffinFilesRead` totals 1 for that blob across both queries).\n"
        "A `SYSTEM DROP PUFFIN FILES CACHE` racing with an in-flight load SHALL NOT produce a wrong\n"
        "result — the load is discarded and recorded as a miss rather than being served stale.\n"
        "\n"
    ),
    link=None,
    level=2,
    num="12.9",
)

RQ_Iceberg_DeletionVectors_Cache_EntryIsolation = Requirement(
    name="RQ.Iceberg.DeletionVectors.Cache.EntryIsolation",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "A cache hit SHALL return a copy of the stored bitmap so that no query can mutate another query's\n"
        "cached state. Many concurrent queries with different filters over the same deletion vector SHALL\n"
        "each return the same result as the equivalent single query.\n"
    ),
    link=None,
    level=2,
    num="12.10",
)

SRS_048_ClickHouse_Iceberg_v3_Deletion_Vectors_Read_Support = Specification(
    name="SRS-048 ClickHouse Iceberg v3 Deletion Vectors Read Support",
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
        Heading(name="RQ.Iceberg.DeletionVectors.Read", level=2, num="2.1"),
        Heading(name="RQ.Iceberg.DeletionVectors.ReadOnly", level=2, num="2.2"),
        Heading(name="RQ.Iceberg.DeletionVectors.AccessForms", level=2, num="2.3"),
        Heading(name="RQ.Iceberg.DeletionVectors.StorageBackends", level=2, num="2.4"),
        Heading(name="Producing Operations", level=1, num="3"),
        Heading(name="RQ.Iceberg.DeletionVectors.WriterOperations", level=2, num="3.1"),
        Heading(name="Vector Content Shapes", level=1, num="4"),
        Heading(name="RQ.Iceberg.DeletionVectors.EmptyVector", level=2, num="4.1"),
        Heading(name="RQ.Iceberg.DeletionVectors.AllRowsDeleted", level=2, num="4.2"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.BoundaryPositions", level=2, num="4.3"
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.RowGroupBoundaries", level=2, num="4.4"
        ),
        Heading(name="RQ.Iceberg.DeletionVectors.SharedPuffinFile", level=2, num="4.5"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.SupportedPositionRange", level=2, num="4.6"
        ),
        Heading(name="Coexistence With Other Delete Formats", level=1, num="5"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Coexistence.AcrossDataFiles",
            level=2,
            num="5.1",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Coexistence.SupersedesPositionDeletes",
            level=2,
            num="5.2",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Coexistence.EqualityDeletes",
            level=2,
            num="5.3",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Coexistence.MultipleVectorsError",
            level=2,
            num="5.4",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Coexistence.FormatVersionUpgrade",
            level=2,
            num="5.5",
        ),
        Heading(name="Query Semantics", level=1, num="6"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.QuerySemantics.OperatorIndependence",
            level=2,
            num="6.1",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.QuerySemantics.ProjectionIndependence",
            level=2,
            num="6.2",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.QuerySemantics.CombinedFilters",
            level=2,
            num="6.3",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.QuerySemantics.SchemaEvolution",
            level=2,
            num="6.4",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.QuerySemantics.IOReductionOptimizations",
            level=2,
            num="6.5",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.QuerySemantics.ComplexSchemas",
            level=2,
            num="6.6",
        ),
        Heading(name="Snapshots and Time Travel", level=1, num="7"),
        Heading(name="RQ.Iceberg.DeletionVectors.TimeTravel", level=2, num="7.1"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.TimeTravel.MultipleGenerations",
            level=2,
            num="7.2",
        ),
        Heading(name="RQ.Iceberg.DeletionVectors.SnapshotRefresh", level=2, num="7.3"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.SnapshotRefresh.QueryCache",
            level=2,
            num="7.4",
        ),
        Heading(name="RQ.Iceberg.DeletionVectors.SequenceNumbers", level=2, num="7.5"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.SequenceNumbers.SameCommit",
            level=2,
            num="7.6",
        ),
        Heading(name="RQ.Iceberg.DeletionVectors.Compaction", level=2, num="7.7"),
        Heading(name="Partitioning and Pruning", level=1, num="8"),
        Heading(name="RQ.Iceberg.DeletionVectors.Partitioning", level=2, num="8.1"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Partitioning.PruningSkipsVectorLoad",
            level=2,
            num="8.2",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Partitioning.PartitionMatching",
            level=2,
            num="8.3",
        ),
        Heading(name="Count Paths", level=1, num="9"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Count.TrivialCountOptimization",
            level=2,
            num="9.1",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Count.CountOnlyFastPath",
            level=2,
            num="9.2",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Count.CountFromFilesCache",
            level=2,
            num="9.3",
        ),
        Heading(name="Error Handling", level=1, num="10"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.ErrorHandling.MalformedBlob",
            level=2,
            num="10.1",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.ErrorHandling.BlobMetadata",
            level=2,
            num="10.2",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.ErrorHandling.BlobBounds",
            level=2,
            num="10.3",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.ErrorHandling.ManifestConsistency",
            level=2,
            num="10.4",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.ErrorHandling.ResourceLimits",
            level=2,
            num="10.5",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.ErrorHandling.NonParquetDataFiles",
            level=2,
            num="10.6",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.ErrorHandling.CompressedFooter",
            level=2,
            num="10.7",
        ),
        Heading(name="Distributed Reads", level=1, num="11"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Distributed.ClusterFunctions",
            level=2,
            num="11.1",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Distributed.ProtocolFailClosed",
            level=2,
            num="11.2",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Distributed.SplitDataFile",
            level=2,
            num="11.3",
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Distributed.SnapshotRefresh",
            level=2,
            num="11.4",
        ),
        Heading(name="Puffin Files Cache", level=1, num="12"),
        Heading(name="RQ.Iceberg.DeletionVectors.Cache.Setting", level=2, num="12.1"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Cache.ServerSettings", level=2, num="12.2"
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Cache.Invalidation", level=2, num="12.3"
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Cache.EtagBypass", level=2, num="12.4"
        ),
        Heading(name="RQ.Iceberg.DeletionVectors.Cache.Eviction", level=2, num="12.5"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Cache.DropStatement", level=2, num="12.6"
        ),
        Heading(name="RQ.Iceberg.DeletionVectors.Cache.RBAC", level=2, num="12.7"),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Cache.Observability", level=2, num="12.8"
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Cache.Concurrency", level=2, num="12.9"
        ),
        Heading(
            name="RQ.Iceberg.DeletionVectors.Cache.EntryIsolation", level=2, num="12.10"
        ),
    ),
    requirements=(
        RQ_Iceberg_DeletionVectors_Read,
        RQ_Iceberg_DeletionVectors_ReadOnly,
        RQ_Iceberg_DeletionVectors_AccessForms,
        RQ_Iceberg_DeletionVectors_StorageBackends,
        RQ_Iceberg_DeletionVectors_WriterOperations,
        RQ_Iceberg_DeletionVectors_EmptyVector,
        RQ_Iceberg_DeletionVectors_AllRowsDeleted,
        RQ_Iceberg_DeletionVectors_BoundaryPositions,
        RQ_Iceberg_DeletionVectors_RowGroupBoundaries,
        RQ_Iceberg_DeletionVectors_SharedPuffinFile,
        RQ_Iceberg_DeletionVectors_SupportedPositionRange,
        RQ_Iceberg_DeletionVectors_Coexistence_AcrossDataFiles,
        RQ_Iceberg_DeletionVectors_Coexistence_SupersedesPositionDeletes,
        RQ_Iceberg_DeletionVectors_Coexistence_EqualityDeletes,
        RQ_Iceberg_DeletionVectors_Coexistence_MultipleVectorsError,
        RQ_Iceberg_DeletionVectors_Coexistence_FormatVersionUpgrade,
        RQ_Iceberg_DeletionVectors_QuerySemantics_OperatorIndependence,
        RQ_Iceberg_DeletionVectors_QuerySemantics_ProjectionIndependence,
        RQ_Iceberg_DeletionVectors_QuerySemantics_CombinedFilters,
        RQ_Iceberg_DeletionVectors_QuerySemantics_SchemaEvolution,
        RQ_Iceberg_DeletionVectors_QuerySemantics_IOReductionOptimizations,
        RQ_Iceberg_DeletionVectors_QuerySemantics_ComplexSchemas,
        RQ_Iceberg_DeletionVectors_TimeTravel,
        RQ_Iceberg_DeletionVectors_TimeTravel_MultipleGenerations,
        RQ_Iceberg_DeletionVectors_SnapshotRefresh,
        RQ_Iceberg_DeletionVectors_SnapshotRefresh_QueryCache,
        RQ_Iceberg_DeletionVectors_SequenceNumbers,
        RQ_Iceberg_DeletionVectors_SequenceNumbers_SameCommit,
        RQ_Iceberg_DeletionVectors_Compaction,
        RQ_Iceberg_DeletionVectors_Partitioning,
        RQ_Iceberg_DeletionVectors_Partitioning_PruningSkipsVectorLoad,
        RQ_Iceberg_DeletionVectors_Partitioning_PartitionMatching,
        RQ_Iceberg_DeletionVectors_Count_TrivialCountOptimization,
        RQ_Iceberg_DeletionVectors_Count_CountOnlyFastPath,
        RQ_Iceberg_DeletionVectors_Count_CountFromFilesCache,
        RQ_Iceberg_DeletionVectors_ErrorHandling_MalformedBlob,
        RQ_Iceberg_DeletionVectors_ErrorHandling_BlobMetadata,
        RQ_Iceberg_DeletionVectors_ErrorHandling_BlobBounds,
        RQ_Iceberg_DeletionVectors_ErrorHandling_ManifestConsistency,
        RQ_Iceberg_DeletionVectors_ErrorHandling_ResourceLimits,
        RQ_Iceberg_DeletionVectors_ErrorHandling_NonParquetDataFiles,
        RQ_Iceberg_DeletionVectors_ErrorHandling_CompressedFooter,
        RQ_Iceberg_DeletionVectors_Distributed_ClusterFunctions,
        RQ_Iceberg_DeletionVectors_Distributed_ProtocolFailClosed,
        RQ_Iceberg_DeletionVectors_Distributed_SplitDataFile,
        RQ_Iceberg_DeletionVectors_Distributed_SnapshotRefresh,
        RQ_Iceberg_DeletionVectors_Cache_Setting,
        RQ_Iceberg_DeletionVectors_Cache_ServerSettings,
        RQ_Iceberg_DeletionVectors_Cache_Invalidation,
        RQ_Iceberg_DeletionVectors_Cache_EtagBypass,
        RQ_Iceberg_DeletionVectors_Cache_Eviction,
        RQ_Iceberg_DeletionVectors_Cache_DropStatement,
        RQ_Iceberg_DeletionVectors_Cache_RBAC,
        RQ_Iceberg_DeletionVectors_Cache_Observability,
        RQ_Iceberg_DeletionVectors_Cache_Concurrency,
        RQ_Iceberg_DeletionVectors_Cache_EntryIsolation,
    ),
    content=r"""
# SRS-048 ClickHouse Iceberg v3 Deletion Vectors Read Support
# Software Requirements Specification

## Table of Contents

* 1 [Introduction](#introduction)
    * 1.1 [Terminology](#terminology)
* 2 [Feature Scope](#feature-scope)
    * 2.1 [RQ.Iceberg.DeletionVectors.Read](#rqicebergdeletionvectorsread)
    * 2.2 [RQ.Iceberg.DeletionVectors.ReadOnly](#rqicebergdeletionvectorsreadonly)
    * 2.3 [RQ.Iceberg.DeletionVectors.AccessForms](#rqicebergdeletionvectorsaccessforms)
    * 2.4 [RQ.Iceberg.DeletionVectors.StorageBackends](#rqicebergdeletionvectorsstoragebackends)
* 3 [Producing Operations](#producing-operations)
    * 3.1 [RQ.Iceberg.DeletionVectors.WriterOperations](#rqicebergdeletionvectorswriteroperations)
* 4 [Vector Content Shapes](#vector-content-shapes)
    * 4.1 [RQ.Iceberg.DeletionVectors.EmptyVector](#rqicebergdeletionvectorsemptyvector)
    * 4.2 [RQ.Iceberg.DeletionVectors.AllRowsDeleted](#rqicebergdeletionvectorsallrowsdeleted)
    * 4.3 [RQ.Iceberg.DeletionVectors.BoundaryPositions](#rqicebergdeletionvectorsboundarypositions)
    * 4.4 [RQ.Iceberg.DeletionVectors.RowGroupBoundaries](#rqicebergdeletionvectorsrowgroupboundaries)
    * 4.5 [RQ.Iceberg.DeletionVectors.SharedPuffinFile](#rqicebergdeletionvectorssharedpuffinfile)
    * 4.6 [RQ.Iceberg.DeletionVectors.SupportedPositionRange](#rqicebergdeletionvectorssupportedpositionrange)
* 5 [Coexistence With Other Delete Formats](#coexistence-with-other-delete-formats)
    * 5.1 [RQ.Iceberg.DeletionVectors.Coexistence.AcrossDataFiles](#rqicebergdeletionvectorscoexistenceacrossdatafiles)
    * 5.2 [RQ.Iceberg.DeletionVectors.Coexistence.SupersedesPositionDeletes](#rqicebergdeletionvectorscoexistencesupersedespositiondeletes)
    * 5.3 [RQ.Iceberg.DeletionVectors.Coexistence.EqualityDeletes](#rqicebergdeletionvectorscoexistenceequalitydeletes)
    * 5.4 [RQ.Iceberg.DeletionVectors.Coexistence.MultipleVectorsError](#rqicebergdeletionvectorscoexistencemultiplevectorserror)
    * 5.5 [RQ.Iceberg.DeletionVectors.Coexistence.FormatVersionUpgrade](#rqicebergdeletionvectorscoexistenceformatversionupgrade)
* 6 [Query Semantics](#query-semantics)
    * 6.1 [RQ.Iceberg.DeletionVectors.QuerySemantics.OperatorIndependence](#rqicebergdeletionvectorsquerysemanticsoperatorindependence)
    * 6.2 [RQ.Iceberg.DeletionVectors.QuerySemantics.ProjectionIndependence](#rqicebergdeletionvectorsquerysemanticsprojectionindependence)
    * 6.3 [RQ.Iceberg.DeletionVectors.QuerySemantics.CombinedFilters](#rqicebergdeletionvectorsquerysemanticscombinedfilters)
    * 6.4 [RQ.Iceberg.DeletionVectors.QuerySemantics.SchemaEvolution](#rqicebergdeletionvectorsquerysemanticsschemaevolution)
    * 6.5 [RQ.Iceberg.DeletionVectors.QuerySemantics.IOReductionOptimizations](#rqicebergdeletionvectorsquerysemanticsioreductionoptimizations)
    * 6.6 [RQ.Iceberg.DeletionVectors.QuerySemantics.ComplexSchemas](#rqicebergdeletionvectorsquerysemanticscomplexschemas)
* 7 [Snapshots and Time Travel](#snapshots-and-time-travel)
    * 7.1 [RQ.Iceberg.DeletionVectors.TimeTravel](#rqicebergdeletionvectorstimetravel)
    * 7.2 [RQ.Iceberg.DeletionVectors.TimeTravel.MultipleGenerations](#rqicebergdeletionvectorstimetravelmultiplegenerations)
    * 7.3 [RQ.Iceberg.DeletionVectors.SnapshotRefresh](#rqicebergdeletionvectorssnapshotrefresh)
    * 7.4 [RQ.Iceberg.DeletionVectors.SnapshotRefresh.QueryCache](#rqicebergdeletionvectorssnapshotrefreshquerycache)
    * 7.5 [RQ.Iceberg.DeletionVectors.SequenceNumbers](#rqicebergdeletionvectorssequencenumbers)
    * 7.6 [RQ.Iceberg.DeletionVectors.SequenceNumbers.SameCommit](#rqicebergdeletionvectorssequencenumberssamecommit)
    * 7.7 [RQ.Iceberg.DeletionVectors.Compaction](#rqicebergdeletionvectorscompaction)
* 8 [Partitioning and Pruning](#partitioning-and-pruning)
    * 8.1 [RQ.Iceberg.DeletionVectors.Partitioning](#rqicebergdeletionvectorspartitioning)
    * 8.2 [RQ.Iceberg.DeletionVectors.Partitioning.PruningSkipsVectorLoad](#rqicebergdeletionvectorspartitioningpruningskipsvectorload)
    * 8.3 [RQ.Iceberg.DeletionVectors.Partitioning.PartitionMatching](#rqicebergdeletionvectorspartitioningpartitionmatching)
* 9 [Count Paths](#count-paths)
    * 9.1 [RQ.Iceberg.DeletionVectors.Count.TrivialCountOptimization](#rqicebergdeletionvectorscounttrivialcountoptimization)
    * 9.2 [RQ.Iceberg.DeletionVectors.Count.CountOnlyFastPath](#rqicebergdeletionvectorscountcountonlyfastpath)
    * 9.3 [RQ.Iceberg.DeletionVectors.Count.CountFromFilesCache](#rqicebergdeletionvectorscountcountfromfilescache)
* 10 [Error Handling](#error-handling)
    * 10.1 [RQ.Iceberg.DeletionVectors.ErrorHandling.MalformedBlob](#rqicebergdeletionvectorserrorhandlingmalformedblob)
    * 10.2 [RQ.Iceberg.DeletionVectors.ErrorHandling.BlobMetadata](#rqicebergdeletionvectorserrorhandlingblobmetadata)
    * 10.3 [RQ.Iceberg.DeletionVectors.ErrorHandling.BlobBounds](#rqicebergdeletionvectorserrorhandlingblobbounds)
    * 10.4 [RQ.Iceberg.DeletionVectors.ErrorHandling.ManifestConsistency](#rqicebergdeletionvectorserrorhandlingmanifestconsistency)
    * 10.5 [RQ.Iceberg.DeletionVectors.ErrorHandling.ResourceLimits](#rqicebergdeletionvectorserrorhandlingresourcelimits)
    * 10.6 [RQ.Iceberg.DeletionVectors.ErrorHandling.NonParquetDataFiles](#rqicebergdeletionvectorserrorhandlingnonparquetdatafiles)
    * 10.7 [RQ.Iceberg.DeletionVectors.ErrorHandling.CompressedFooter](#rqicebergdeletionvectorserrorhandlingcompressedfooter)
* 11 [Distributed Reads](#distributed-reads)
    * 11.1 [RQ.Iceberg.DeletionVectors.Distributed.ClusterFunctions](#rqicebergdeletionvectorsdistributedclusterfunctions)
    * 11.2 [RQ.Iceberg.DeletionVectors.Distributed.ProtocolFailClosed](#rqicebergdeletionvectorsdistributedprotocolfailclosed)
    * 11.3 [RQ.Iceberg.DeletionVectors.Distributed.SplitDataFile](#rqicebergdeletionvectorsdistributedsplitdatafile)
    * 11.4 [RQ.Iceberg.DeletionVectors.Distributed.SnapshotRefresh](#rqicebergdeletionvectorsdistributedsnapshotrefresh)
* 12 [Puffin Files Cache](#puffin-files-cache)
    * 12.1 [RQ.Iceberg.DeletionVectors.Cache.Setting](#rqicebergdeletionvectorscachesetting)
    * 12.2 [RQ.Iceberg.DeletionVectors.Cache.ServerSettings](#rqicebergdeletionvectorscacheserversettings)
    * 12.3 [RQ.Iceberg.DeletionVectors.Cache.Invalidation](#rqicebergdeletionvectorscacheinvalidation)
    * 12.4 [RQ.Iceberg.DeletionVectors.Cache.EtagBypass](#rqicebergdeletionvectorscacheetagbypass)
    * 12.5 [RQ.Iceberg.DeletionVectors.Cache.Eviction](#rqicebergdeletionvectorscacheeviction)
    * 12.6 [RQ.Iceberg.DeletionVectors.Cache.DropStatement](#rqicebergdeletionvectorscachedropstatement)
    * 12.7 [RQ.Iceberg.DeletionVectors.Cache.RBAC](#rqicebergdeletionvectorscacherbac)
    * 12.8 [RQ.Iceberg.DeletionVectors.Cache.Observability](#rqicebergdeletionvectorscacheobservability)
    * 12.9 [RQ.Iceberg.DeletionVectors.Cache.Concurrency](#rqicebergdeletionvectorscacheconcurrency)
    * 12.10 [RQ.Iceberg.DeletionVectors.Cache.EntryIsolation](#rqicebergdeletionvectorscacheentryisolation)

## Introduction

Apache Iceberg tables are built on immutable data files in object storage, so a row can never be
deleted in place. In **merge-on-read** (MoR) mode, a writer records deleted rows in small side
files instead of rewriting data files, and every reader must apply those side files to
reconstruct the logical table. **Deletion vectors** are the Iceberg v3 replacement for position
delete files: the deleted row positions of one data file are stored as a compressed roaring
bitmap blob inside a `Puffin` file, with at most one deletion vector per data file per snapshot.

This specification covers ClickHouse **read** support for Iceberg v3 deletion vectors. The
realistic setup is a lakehouse where an external engine (Spark, Trino, Flink, or a
catalog-managed service) is the writer: it commits `DELETE` / `UPDATE` / `MERGE` operations that
produce deletion vectors, and ClickHouse must return exactly the rows the writer's own engine
would return. ClickHouse never produces deletion vectors itself.

For a writer to produce deletion vectors, the table must be Iceberg format version 3 with
merge-on-read write modes:

```sql
CREATE TABLE catalog.db.table (...)
TBLPROPERTIES (
    'format-version' = '3',
    'write.delete.mode' = 'merge-on-read',
    'write.update.mode' = 'merge-on-read',
    'write.merge.mode'  = 'merge-on-read'
)
```

Without these properties the writer silently uses copy-on-write, no deletion vector is produced,
and a test exercises nothing. Tests relying on writer-produced vectors must verify that at least
one `*.puffin` file exists under the table location before asserting results.

Negative requirements in this specification name the expected error code, because several failure
paths are distinguishable only by their code:

| Code | Meaning |
|---|---|
| `ICEBERG_SPECIFICATION_VIOLATION` | The Iceberg metadata layer is internally inconsistent (manifest ↔ data file ↔ deletion vector). |
| `BAD_ARGUMENTS` | The `Puffin` file or the deletion-vector blob inside it is malformed. |
| `NOT_IMPLEMENTED` | A valid Iceberg construct that this implementation does not support. |
| `UNKNOWN_PROTOCOL` | A cluster worker is too old to receive the deletion state safely. |

Out of scope: writing deletion vectors from ClickHouse, blob types other than
`deletion-vector-v1`, and the standalone `Puffin` input format (`SELECT ... FROM file(...,
Puffin)`), which belongs to format-level requirements rather than Iceberg table reads.

### Terminology

Terms used throughout this specification:

| Term                 | Meaning                                                                                                                                                                                                                                       |
|----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| writer               | The external engine (Spark in our tests) that changes the table: inserts, deletes, updates, compaction. ClickHouse is never the writer.                                                                                                       |
| reader               | ClickHouse, reading the table and applying deletion vectors.                                                                                                                                                                                  |
| data file            | A Parquet file holding table rows. Data files are never edited in place.                                                                                                                                                                      |
| position             | The row number of a row inside one data file, counted from 0.                                                                                                                                                                                 |
| deletion vector (DV) | A compressed bitmap listing the deleted row positions of one data file. At most one vector per data file per snapshot.                                                                                                                        |
| `Puffin` file        | The container file (`*.puffin`) that stores deletion vectors as blobs.                                                                                                                                                                        |
| blob                 | One stored item inside a `Puffin` file — here always a `deletion-vector-v1` bitmap.                                                                                                                                                           |
| footer               | The index at the end of a `Puffin` file. It lists every blob with its offset, length, and properties.                                                                                                                                         |
| snapshot             | One committed version of the table. Every query reads exactly one snapshot.                                                                                                                                                                   |
| manifest             | An Avro metadata file listing the data files and delete files of a snapshot. A deletion vector's manifest entry records which `Puffin` file holds it, where inside that file (offset, length), and how many rows it deletes (`record_count`). |
| sequence number      | A commit-order number. A deletion vector applies only to data files committed at or before its own sequence number.                                                                                                                           |
| merge-on-read (MoR)  | The write mode where deletes are recorded in small side files (such as deletion vectors) instead of rewriting data files. The reader merges them at query time.                                                                               |
| position delete file | The older (v2) way to record deleted rows: a Parquet file listing (data file, position) pairs. Replaced by deletion vectors in v3.                                                                                                            |
| cardinality          | The number of deleted rows a vector declares.                                                                                                                                                                                                 |
| etag                 | A fingerprint that object storage (S3, Azure) assigns to an object's content; it changes whenever the object's content changes. Local files have none.                                                                                        |
| access form          | The way ClickHouse reaches the table: a table function (`icebergS3`), the `Iceberg` table engine, or a database connected to a REST catalog.                                                                                                  |
| cold / warm read     | A cold read fetches and parses the `Puffin` file from storage; a warm read is served from the `Puffin` files cache.                                                                                                                           |
| fail closed          | When correctness cannot be guaranteed, return an error — never a possibly wrong row set.                                                                                                                                                      |

[ClickHouse]: https://clickhouse.com

## Feature Scope

### RQ.Iceberg.DeletionVectors.Read
version: 1.0

[ClickHouse] SHALL support reading Iceberg format version 3 tables whose row-level deletes are
stored as deletion vectors (`deletion-vector-v1` blobs in `Puffin` files). For every data file,
[ClickHouse] SHALL exclude exactly the row positions recorded in that file's deletion vector, so
the query result matches the logical table state committed by the writer.

```sql
SELECT * FROM icebergS3('http://minio:9000/warehouse/data/', 'minio', 'minio123');
```

### RQ.Iceberg.DeletionVectors.ReadOnly
version: 1.0

Deletion vector support SHALL be read-only. [ClickHouse] SHALL NOT produce, modify, or delete
deletion vectors or `Puffin` files under any operation.

### RQ.Iceberg.DeletionVectors.AccessForms
version: 1.0

[ClickHouse] SHALL apply deletion vectors identically across all Iceberg access forms:

* Table functions: `icebergS3`, `icebergAzure`, `icebergLocal`
* The `Iceberg` table engine
* Tables from an Iceberg REST-catalog database (`DataLakeCatalog` engine)

The same table read through any form SHALL return the same logical row set.

For example, if the writer inserted ids `1..5` and deleted ids `2` and `4`, each access form can
be compared using the same projection and ordering:

```sql
SELECT id FROM icebergS3('http://minio:9000/warehouse/t/', 'minio', 'minio123') ORDER BY id;
SELECT id FROM iceberg_engine_table ORDER BY id;
SELECT id FROM rest_catalog_db.t ORDER BY id;
```

```text
id
1
3
5
```

### RQ.Iceberg.DeletionVectors.StorageBackends
version: 1.0

[ClickHouse] SHALL support deletion vectors on tables stored in S3, Azure, and local filesystem
storage. Correctness SHALL NOT depend on the storage backend. Cache-related requirements
(section 12) apply only to S3 and Azure, because the `Puffin` cache is keyed partly on the object
etag and local filesystem objects have none.

## Producing Operations

### RQ.Iceberg.DeletionVectors.WriterOperations
version: 1.0

[ClickHouse] SHALL correctly read deletion vectors regardless of which external SQL operation
produced them: `DELETE`, `UPDATE`, or `MERGE` (including `MERGE` statements combining
`WHEN MATCHED THEN UPDATE`, `WHEN MATCHED THEN DELETE`, and `WHEN NOT MATCHED THEN INSERT`).
Once a snapshot with valid metadata is committed, the producing operation is irrelevant to the
read path: row counts, exact surviving rows, updated values, and inserted rows SHALL match the
writer engine's own result.

For example, given `(1, 'old')`, `(2, 'remove')`, and `(3, 'keep')`, an external writer could
produce deletion vectors through operations such as:

```sql
DELETE FROM t WHERE id = 2;
UPDATE t SET value = 'new' WHERE id = 1;
MERGE INTO t USING changes c ON t.id = c.id
WHEN MATCHED AND c.action = 'delete' THEN DELETE
WHEN MATCHED THEN UPDATE SET value = c.value
WHEN NOT MATCHED THEN INSERT (id, value) VALUES (c.id, c.value);
```

After an update of id `1`, deletion of id `2`, and insertion of id `4`, an illustrative
ClickHouse read is:

```sql
SELECT id, value FROM iceberg_table ORDER BY id;
```

```text
id  value
1   new
3   keep
4   inserted
```

## Vector Content Shapes

### RQ.Iceberg.DeletionVectors.EmptyVector
version: 1.0

[ClickHouse] SHALL accept a deletion vector with `cardinality = 0` and no positions as valid.
The referenced data file SHALL contribute all of its rows; the empty vector SHALL NOT hide the
file and SHALL NOT fail the query. Repeated reads SHALL neither fail nor re-fetch the `Puffin`
file when the cache is enabled.

### RQ.Iceberg.DeletionVectors.AllRowsDeleted
version: 1.0

[ClickHouse] SHALL support a deletion vector that deletes every row of its data file. The file
SHALL contribute zero rows without being physically removed, and the query SHALL remain valid:

```text
file A → 100 rows, deletion vector deletes positions 0..99 → contributes 0 rows
file B → 50 rows,  no deletion vector                      → contributes 50 rows
table  → 50 rows visible
```

`SELECT *`, `SELECT count()`, aggregates, and filtered reads SHALL all reflect the empty
contribution.

Note: writers turn a `DELETE` whose predicate provably covers a whole data file into a
metadata-only file drop (the file leaves the snapshot and no vector is written), so a
full-file vector arises from position-level writes rather than from a file-aligned writer
`DELETE`.

### RQ.Iceberg.DeletionVectors.BoundaryPositions
version: 1.0

Deletion-vector positions are zero-based within the referenced data file. For a data file with
`record_count = N`, [ClickHouse] SHALL:

* apply position `0` (first row) and position `N - 1` (last row) correctly;
* reject a position `>= N` with `ICEBERG_SPECIFICATION_VIOLATION`;
* reject a declared cardinality `> N` with `ICEBERG_SPECIFICATION_VIOLATION`, before any
  `Puffin` I/O is performed.

For example, for rows with ids `10`, `20`, and `30` stored in that physical order, a vector
containing positions `{0, 2}` produces:

```sql
SELECT id FROM iceberg_table ORDER BY id;
```

```text
id
20
```

A vector containing position `3` for the same three-row file fails instead of returning rows.

Note: rejecting out-of-bounds positions and cardinalities is a [ClickHouse] fail-closed
contract; the Iceberg specification does not define reader behavior for such metadata.

### RQ.Iceberg.DeletionVectors.RowGroupBoundaries
version: 1.0

[ClickHouse] SHALL interpret deletion-vector positions as absolute row numbers within the
referenced Parquet file, never relative to a row group. For a file with row groups of 100 rows
each and a vector deleting `{99, 100, 199, 200}`, exactly those four rows SHALL disappear —
when all row groups are read, when some are pruned by a predicate, and when row groups are
processed by parallel readers.

### RQ.Iceberg.DeletionVectors.SharedPuffinFile
version: 1.0

One `Puffin` file may hold several `deletion-vector-v1` blobs, each bound by its own
`content_offset` / `content_size_in_bytes` from the manifest and carrying its own
`referenced-data-file` property. [ClickHouse] SHALL apply to each data file only its own blob —
no union and no cross-file contamination — both when all referenced files are read together and
when a filter causes only one of them to be read.

### RQ.Iceberg.DeletionVectors.SupportedPositionRange
version: 1.0

The `deletion-vector-v1` format supports positive 64-bit row positions (the most significant
bit must be 0): a position is split into a 32-bit key (the most significant 4 bytes) and a
32-bit sub-position (the least significant 4 bytes), with one 32-bit roaring bitmap per key,
bitmaps ordered by unsigned comparison of their keys.

[ClickHouse] SHALL parse and apply valid vectors with bitmap keys in `[0, INT32_MAX - 1]` and
positions up to the maximum supported position `(INT32_MAX - 1) * 2^32 + 2^31`
(`0x7FFFFFFE80000000` — the Iceberg Java `RoaringPositionBitmap.MAX_POSITION`). A bitmap key
or position beyond these limits SHALL be rejected with `BAD_ARGUMENTS`
(`Invalid deletion vector bitmap key` / `is out of supported range`, see
RQ.Iceberg.DeletionVectors.ErrorHandling.MalformedBlob).

Note: the supported range is narrower than the literal `Puffin` spec, which allows any
positive 64-bit position (most significant bit 0); both caps mirror the Iceberg Java
reference implementation and are a deliberate [ClickHouse] contract.

Position arithmetic SHALL be 64-bit throughout: a position in a high-key bucket SHALL NOT be
truncated to its low 32 bits. For example, for a vector containing position `2^32 + 2`
(key `1`, sub-position `2`) over a data file whose manifest `record_count` admits that
position, the physical row at position `2` SHALL remain visible — a reader that truncates
positions to 32 bits would wrongly delete it.

Because a valid position must be below the data file's `record_count`
(RQ.Iceberg.DeletionVectors.BoundaryPositions), a vector with a key `>= 1` can only reference
a data file with more than `2^32` rows; this requirement is therefore verified with crafted
vectors and manifest metadata rather than a multi-billion-row data file.

## Coexistence With Other Delete Formats

Iceberg v3 tables may simultaneously carry deletion vectors, Parquet position-delete files
(inherited from v2), and equality-delete files. ClickHouse already reads the two older formats;
this section defines how the three interact.

### RQ.Iceberg.DeletionVectors.Coexistence.AcrossDataFiles
version: 1.0

Within one snapshot, different data files may independently use a deletion vector, a Parquet
position delete, an equality delete, or no delete at all. [ClickHouse] SHALL compute each data
file's result from its own delete metadata only.

### RQ.Iceberg.DeletionVectors.Coexistence.SupersedesPositionDeletes
version: 1.0

When a deletion vector matches a data file, [ClickHouse] SHALL NOT apply Parquet position-delete
files for that same data file (the Iceberg v3 supersession rule). Consequently:

* a row present both in an old position-delete file and in a newer deletion vector SHALL be
  removed exactly once;
* a row present only in a superseded position-delete file SHALL remain visible unless the
  deletion vector also covers it.

### RQ.Iceberg.DeletionVectors.Coexistence.EqualityDeletes
version: 1.0

Equality deletes SHALL apply independently of, and in addition to, a deletion vector on the same
data file. The final result SHALL be as if the deletion-vector filter ran first (on absolute row
positions) and the equality-delete predicate ran on the surviving rows.

For example, given physical rows `(1, 'keep')`, `(2, 'dv')`, `(3, 'eq')`, and `(4, 'keep')`, a
deletion vector for position `1` plus an equality delete for `id = 3` produces:

```sql
SELECT id, value FROM iceberg_table ORDER BY id;
```

```text
id  value
1   keep
4   keep
```

### RQ.Iceberg.DeletionVectors.Coexistence.MultipleVectorsError
version: 1.0

If more than one live deletion-vector manifest entry references the same data file in one
snapshot, [ClickHouse] SHALL fail the query with `ICEBERG_SPECIFICATION_VIOLATION`
("Multiple deletion vectors match data file ..."). It SHALL NOT pick one of them and SHALL NOT
union them.

Note: the Iceberg specification only constrains writers ("at most one deletion vector is
allowed per data file in a snapshot") and leaves reader behavior on a violation undefined;
failing the query is a [ClickHouse] fail-closed contract.

### RQ.Iceberg.DeletionVectors.Coexistence.FormatVersionUpgrade
version: 1.0

For an Iceberg v2 table with Parquet position deletes that is upgraded to format version 3:

* the query result SHALL be identical immediately before and after the upgrade — previously
  deleted rows SHALL NOT resurface;
* after the first v3 delete produces a deletion vector, rows deleted before the upgrade SHALL
  remain absent and newly deleted rows SHALL become absent, regardless of whether the writer
  removed the superseded position-delete files or kept them alongside the vector. Writers are
  required by the Iceberg spec to fold existing position deletes into a new vector, and the
  supersession rule of RQ.Iceberg.DeletionVectors.Coexistence.SupersedesPositionDeletes
  guarantees the folded vector is applied instead of the old files — so rows are neither
  resurfaced nor double-deleted either way.

## Query Semantics

### RQ.Iceberg.DeletionVectors.QuerySemantics.OperatorIndependence
version: 1.0

Deletion vectors SHALL be applied at the source, before any SQL operator runs, so the visible row
set is fixed for the whole query. Every relational operator SHALL observe exactly that set,
including:

* `ORDER BY ... LIMIT n` (deleted rows straddling the limit boundary must not shrink the result)
* `DISTINCT` (a value whose only occurrence is deleted disappears; a value with a deleted
  duplicate remains)
* `JOIN` against non-Iceberg tables (a deleted row must not join or affect join cardinality)
* subqueries, CTEs, and derived tables (identical to a direct read)
* `PREWHERE` (rows filtered before the deletion-vector transform must still map back to correct
  absolute file row positions)

For example, if id `3` is deleted from ids `1..5`, all of these queries observe the same visible
row set before applying their own operators:

```sql
SELECT id FROM iceberg_table ORDER BY id LIMIT 3;       -- 1, 2, 4
SELECT count() FROM iceberg_table PREWHERE id >= 3;     -- 2
SELECT id FROM iceberg_table WHERE id IN (2, 3, 4)
ORDER BY id;                                             -- 2, 4
```

### RQ.Iceberg.DeletionVectors.QuerySemantics.ProjectionIndependence
version: 1.0

Row visibility SHALL be independent of the projected column list, because a deletion vector
addresses physical row positions, not predicate values. When the writer executed
`DELETE FROM t WHERE customer_id = 100`, a ClickHouse query selecting only other columns
(`SELECT amount FROM ...`) SHALL still exclude the deleted rows without re-evaluating the
original predicate.

For example, if the writer deleted the physical row `(100, 42.50, 'paid')`, neither of these
projections may expose it:

```sql
SELECT customer_id, amount, status FROM iceberg_table ORDER BY customer_id;
SELECT amount FROM iceberg_table ORDER BY amount;
```

The second query does not need to project `customer_id` to apply the deletion vector.

### RQ.Iceberg.DeletionVectors.QuerySemantics.CombinedFilters
version: 1.0

When a user predicate is combined with a deletion vector and an equality delete, the result SHALL
be equivalent to applying, in order:

```text
physical data → deletion-vector visibility → other Iceberg delete semantics → user predicate
```

A row removed by any one of the three SHALL be absent; a row matched by several SHALL be absent
exactly once; a row matched by none SHALL survive. The same result SHALL hold when the user
predicate is expressed as `WHERE` and as `PREWHERE`.

### RQ.Iceberg.DeletionVectors.QuerySemantics.SchemaEvolution
version: 1.0

A deletion vector attached to a data file SHALL remain valid after schema evolution of the table,
including `ADD COLUMN`, column rename, and column drop (both resolved by field id in Iceberg).
Row visibility SHALL be identical for any projection over old or new columns, and values of a
column added after the data file was written SHALL follow normal Iceberg schema-evolution
semantics (`NULL` unless a default is defined) for the surviving rows.

For example, after deleting id `2`, renaming `value` to `description`, and adding nullable column
`category`, an old data file can be read as:

```sql
SELECT id, description, category FROM iceberg_table ORDER BY id;
```

```text
id  description  category
1   alpha        NULL
3   gamma        NULL
```

### RQ.Iceberg.DeletionVectors.QuerySemantics.IOReductionOptimizations
version: 1.0

[ClickHouse] SHALL return an identical post-vector row set with any Parquet I/O-reducing read
optimization enabled or disabled — including predicate push-down into the Parquet reader,
page- and row-group-level pruning, and constant-value column detection that elides reads of
column data whose value is identical across the file (derivable from column statistics).
Deletion-vector positions are absolute row numbers of the data file; an optimization that
skips reading part of the file SHALL NOT shift, drop, or resurrect rows, and counts and
aggregates over a column whose read was elided SHALL still reflect only surviving rows.

For example, for a table with a constant column `label = 'batch-1'` in every row and a
deletion vector hiding 10 of 100 rows, both of the following SHALL return `90`:

```sql
SELECT count() FROM iceberg_table WHERE label = 'batch-1'
SETTINGS input_format_parquet_filter_push_down = 0;

SELECT count() FROM iceberg_table WHERE label = 'batch-1'
SETTINGS input_format_parquet_filter_push_down = 1;
```

```text
count()
90
```

The same holds for any pairing of such optimizations, and for projections that read only the
constant column:

```sql
SELECT label, count() FROM iceberg_table GROUP BY label;
```

```text
label    count()
batch-1  90
```

### RQ.Iceberg.DeletionVectors.QuerySemantics.ComplexSchemas
version: 1.0

Deletion vectors delete whole rows by position, independently of the schema's shape.
[ClickHouse] SHALL apply deletion vectors correctly on tables with nested and complex column
types — Iceberg `struct` (Tuple), `list` (Array), and `map` (Map), including nested
combinations and `Nullable` fields — and on wide schemas. Reading any subset of nested
fields SHALL exclude deleted rows, and counts and aggregates over nested fields SHALL
reflect only surviving rows.

For example, for an Iceberg schema

```text
id      BIGINT
payload STRUCT<a: INT, tags: ARRAY<STRING>>
attrs   MAP<STRING, STRING>
```

with rows `1`, `2`, `3` and a deletion vector hiding the row with `id = 2`:

```sql
SELECT id, payload.a, attrs['k'] FROM iceberg_table ORDER BY id;
```

```text
id  payload.a  attrs['k']
1   10         v1
3   30         v3
```

```sql
SELECT sum(length(payload.tags)) FROM iceberg_table;
```

returns the sum over rows `1` and `3` only.

## Snapshots and Time Travel

### RQ.Iceberg.DeletionVectors.TimeTravel
version: 1.0

Deletion vectors SHALL be discovered from the manifests of the selected snapshot only. A vector
introduced in snapshot B SHALL be invisible when reading an earlier snapshot A, for both
time-travel forms:

```sql
SELECT count() FROM iceberg_table SETTINGS iceberg_snapshot_id = <snapshot_a_id>;
SELECT count() FROM iceberg_table SETTINGS iceberg_timestamp_ms = <before_delete_ms>;
```

With 100 rows inserted in snapshot A and 5 rows deleted via a deletion vector in snapshot B: the
current read SHALL return 95 rows, snapshot A SHALL return the original 100 rows, and snapshot B
read explicitly SHALL return 95 — as exact row sets, not merely counts.

### RQ.Iceberg.DeletionVectors.TimeTravel.MultipleGenerations
version: 1.0

Across several snapshots whose deletion-vector state differs (for example A: no vector,
B: deletes `{1, 5}`, C: deletes `{1, 5, 9}`), each snapshot SHALL expose its own logical state
regardless of the order in which snapshots are queried and regardless of caching: a vector
cached while reading one snapshot SHALL never affect the result of another.

### RQ.Iceberg.DeletionVectors.SnapshotRefresh
version: 1.0

After an external engine commits a `DELETE` producing a deletion vector, the next ClickHouse
query SHALL observe the new snapshot without a server restart, without
`SYSTEM DROP PUFFIN FILES CACHE`, and without dropping any other cache — with all caches at
their default settings. This SHALL hold for both the table function and the `Iceberg` table
engine.

### RQ.Iceberg.DeletionVectors.SnapshotRefresh.QueryCache
version: 1.0

With the query result cache enabled (`use_query_cache = 1`), staleness across external
Iceberg commits SHALL be bounded by the cache's own entry lifetime and never extended by
deletion-vector state:

* a cached result SHALL correspond to one committed snapshot — never a mix of pre- and
  post-commit deletion-vector state;
* after the cache entry expires (`query_cache_ttl`) or `SYSTEM DROP QUERY CACHE` is issued,
  the next execution SHALL observe the current snapshot, including deletion vectors committed
  since the entry was cached;
* rows deleted by a committed deletion vector SHALL NOT be served from the query cache beyond
  the entry lifetime.

For example, for a 100-row table where an external `DELETE` later hides 10 rows:

```sql
SELECT count() FROM iceberg_table
SETTINGS use_query_cache = 1, query_cache_ttl = 1;
```

```text
count()
100
```

```sql
-- external writer commits a DELETE producing a deletion vector;
-- after the 1-second entry lifetime has passed:
SELECT count() FROM iceberg_table
SETTINGS use_query_cache = 1, query_cache_ttl = 1;
```

```text
count()
90
```

### RQ.Iceberg.DeletionVectors.SequenceNumbers
version: 1.0

[ClickHouse] SHALL honor Iceberg sequence-number rules when matching deletion vectors to data
files:

* a deletion vector committed at sequence number `N` SHALL NOT affect data files added after `N`,
  even when the newer files contain rows with the same values;
* a deletion vector referencing a data file no longer present in the snapshot SHALL be ignored,
  not treated as an error.

Note: writers are required to remove a vector when removing its data file, so an orphan entry
indicates a non-compliant writer; ignoring it mirrors the Iceberg scan-planning rules (the
vector matches no data file in the snapshot) and is a deliberate leniency, not an oversight.

### RQ.Iceberg.DeletionVectors.SequenceNumbers.SameCommit
version: 1.0

Position deletes — deletion vectors included — apply to data files from the same commit: per
the Iceberg scan-planning rules, a deletion vector SHALL be applied to a data file whose data
sequence number is *equal* to the vector's own data sequence number, so that rows added and
deleted in a single commit stay deleted. [ClickHouse] SHALL hide such rows exactly as it does
when the vector's sequence number is strictly greater than the data file's.

(Equality deletes differ: they apply only to data files with a *strictly older* data sequence
number and never to files from their own commit.)

For example, a single writer commit that adds a data file with ids `1..10` and, in the same
commit, a deletion vector for positions `{0, 1}` of that file (as a `MERGE` rewriting and
deleting rows it just inserted can produce) reads as:

```sql
SELECT count() FROM iceberg_table;
```

```text
count()
8
```

### RQ.Iceberg.DeletionVectors.Compaction
version: 1.0

After external data-file compaction (for example Spark's `rewrite_data_files`), deletion vectors
that referenced the pre-compaction files SHALL NOT be applied to the rewritten files, and the
logical query result SHALL be identical before and after the compaction.

## Partitioning and Pruning

### RQ.Iceberg.DeletionVectors.Partitioning
version: 1.0

[ClickHouse] SHALL apply deletion vectors correctly on partitioned tables, including identity,
bucket, and other transform partitioning. A query touching only a deletion-vector-bearing
partition SHALL have the vector applied to it.

### RQ.Iceberg.DeletionVectors.Partitioning.PruningSkipsVectorLoad
version: 1.0

When partition pruning eliminates a data file from a query, [ClickHouse] SHALL also skip loading
that file's deletion vector — no `Puffin` read SHALL occur for a pruned file (observable via the
`PuffinFilesRead` profile event). Min/max pruning of delete files SHALL never prune a delete file
that is actually needed for a data file being read.

For example, if only partition `p = 2026` has a deletion vector, execute a query restricted to
`p = 2025` with the client-supplied query id `dv_partition_pruning`, then check that query id:

```sql
SELECT count()
FROM iceberg_table
WHERE p = 2025
SETTINGS log_profile_events = 1;

SYSTEM FLUSH LOGS;

SELECT ProfileEvents['PuffinFilesRead']
FROM system.query_log
WHERE type = 'QueryFinish' AND query_id = 'dv_partition_pruning';
```

```text
0
```

### RQ.Iceberg.DeletionVectors.Partitioning.PartitionMatching
version: 1.0

Per the Iceberg scan-planning rules, a deletion vector SHALL be matched to a data file only
when all of the following hold:

* the data file's `file_path` equals the vector's `referenced_data_file`;
* the data file's data sequence number is less than or equal to the vector's data sequence
  number (RQ.Iceberg.DeletionVectors.SequenceNumbers,
  RQ.Iceberg.DeletionVectors.SequenceNumbers.SameCommit);
* the data file's partition — both the partition spec and the partition values — is equal to
  the deletion vector's partition.

A deletion vector SHALL never be applied to a data file in a different partition. In
particular, a vector manifest entry whose partition tuple does not match the partition of the
data file named by its `referenced_data_file` — possible only through corrupted or
hand-crafted metadata, since writers record a vector under the partition of the file it
references — SHALL NOT be applied to that data file.

## Count Paths

`SELECT count()` on an Iceberg table can be answered three ways: a metadata shortcut that sums
manifest row counts, a count-only fast path that skips column decoding, and a full scan. All
three must agree in the presence of deletion vectors.

### RQ.Iceberg.DeletionVectors.Count.TrivialCountOptimization
version: 1.0

The metadata count shortcut SHALL fail closed in the presence of any live delete entries
(a `Puffin` deletion vector is a position-delete entry): [ClickHouse] SHALL fall back to a real
scan rather than answering from manifest sums. `SELECT count()` SHALL return the same value with
`optimize_trivial_count_query = 1` and `= 0`, and both SHALL equal
`SELECT count() FROM (SELECT * FROM table)`.

For example, after 5 of 100 rows are deleted, the comparison is:

```sql
SELECT count() FROM iceberg_table SETTINGS optimize_trivial_count_query = 1; -- 95
SELECT count() FROM iceberg_table SETTINGS optimize_trivial_count_query = 0; -- 95
SELECT count() FROM (SELECT * FROM iceberg_table);                            -- 95
```

When the snapshot summary's `total-records` disagrees with the manifest sum on a table without
deletes, the manifest sum SHALL win and a warning SHALL be logged.

### RQ.Iceberg.DeletionVectors.Count.CountOnlyFastPath
version: 1.0

The count-only fast path (`need_only_count`) SHALL be disabled for any data file with an attached
deletion vector, position delete, or equality delete. Counts SHALL be identical with and without
`PREWHERE`, with and without a filter, and for data files split across multiple row groups.

### RQ.Iceberg.DeletionVectors.Count.CountFromFilesCache
version: 1.0

The count-from-files cache (`use_cache_for_count_from_files`) SHALL NOT be used or populated for
data files that have delete entries attached, because its key (file path + modification time)
does not change when a delete file is added or compacted away. In particular:

```text
1. SET use_cache_for_count_from_files = 1
2. SELECT count() → N
3. external DELETE producing a deletion vector
4. SELECT count() → must be N - deleted, not the cached N
```

The reverse direction SHALL also hold: a count taken while deletes exist SHALL NOT be served
stale after the deletes are compacted away.

## Error Handling

Any structural defect in a `Puffin` file or deletion-vector blob must fail the query with an
explicit error. It must never be silently ignored or partially applied — a silently dropped
vector would make deleted rows reappear. Tests SHALL assert both the error code and a
distinguishing fragment of the message, since a bare "query failed" can pass for the wrong
reason.

### RQ.Iceberg.DeletionVectors.ErrorHandling.MalformedBlob
version: 1.0

[ClickHouse] SHALL reject a structurally invalid deletion-vector blob payload with
`BAD_ARGUMENTS` and a specific message, including at least:

| Defect | Expected message fragment |
|---|---|
| CRC32 does not match the payload | `Deletion vector CRC mismatch` |
| wrong 4-byte magic | `Invalid deletion vector magic` |
| declared combined length inconsistent with the blob length | `does not match combined length` |
| blob shorter than 12 bytes | `Deletion vector blob is too small` |
| bitmap header shorter than 8 bytes | `Deletion vector bitmap is too small` |
| bitmap truncated mid-key | `truncated while reading key` |
| roaring container extends past the blob | `failed alloc while reading` (bounds-checked roaring deserializer, wrapped as `Failed to deserialize deletion vector roaring bitmap`) |
| roaring bitmap fails internal validation | `failed internal validation` |
| bitmap keys not strictly ascending | `must be sorted in ascending order` |
| bitmap key negative or `> INT32_MAX - 1` | `Invalid deletion vector bitmap key` |
| bitmap count negative or `> INT32_MAX` | `Invalid deletion vector bitmap count` |
| trailing bytes after the last container | `trailing bytes` |
| deserialized cardinality ≠ declared cardinality | `does not match deserialized row count` |
| running cardinality exceeds the declared one mid-parse | `exceeds declared cardinality` |
| a position exceeds the maximum representable position | `is out of supported range` |

### RQ.Iceberg.DeletionVectors.ErrorHandling.BlobMetadata
version: 1.0

[ClickHouse] SHALL validate the `Puffin` footer metadata of a deletion-vector blob and reject
invalid metadata with `BAD_ARGUMENTS`, including at least:

| Defect | Expected message fragment |
|---|---|
| blob `type` is not `deletion-vector-v1` | `unsupported blob type` |
| `compression-codec` present and non-empty | `must omit 'compression-codec'` |
| `referenced-data-file` missing or empty | `missing required property 'referenced-data-file'` |
| `referenced-data-file` ≠ the data file being read | `does not match expected data file` |
| `cardinality` missing or empty | `missing required property 'cardinality'` |
| `cardinality` not an unsigned integer | `must be an unsigned integer` |
| `cardinality` ≠ the manifest `record_count` | `does not match expected cardinality` |
| footer-declared `offset`/`length` outside the blob payload region | `offset/length out of bounds` |
| no in-bounds blob at the manifest's `(offset, length)` | `No Puffin footer blob at offset` |
| two blobs at the same `(offset, length)` | `Multiple Puffin blobs claim offset` |

Footer blob descriptors are bounds-validated against the blob payload region before the
manifest's `(content_offset, content_size_in_bytes)` pair is matched against them, so an
out-of-bounds footer declaration fails as `offset/length out of bounds` and never reaches the
matching step.

### RQ.Iceberg.DeletionVectors.ErrorHandling.BlobBounds
version: 1.0

[ClickHouse] SHALL reject with `BAD_ARGUMENTS` a manifest-declared blob location that does not
fit inside the `Puffin` file: negative offset or length, offset or length beyond the file size,
and `offset + length` overflowing or exceeding the file size.

### RQ.Iceberg.DeletionVectors.ErrorHandling.ManifestConsistency
version: 1.0

[ClickHouse] SHALL reject internally inconsistent Iceberg metadata with
`ICEBERG_SPECIFICATION_VIOLATION`, including at least:

* a deletion-vector manifest entry without `referenced_data_file` (position-delete lower/upper
  bounds SHALL NOT be used as a fallback for deletion vectors);
* a deletion-vector manifest entry with a negative `record_count`;
* a data-file manifest entry missing `record_count` (required to bound vector positions) or with
  a negative `record_count`;
* a deletion-vector `record_count` greater than the data file's `record_count` (rejected before
  any I/O);
* two deletion vectors referencing the same data file (see
  RQ.Iceberg.DeletionVectors.Coexistence.MultipleVectorsError).

### RQ.Iceberg.DeletionVectors.ErrorHandling.ResourceLimits
version: 1.0

[ClickHouse] SHALL enforce hard resource limits on deletion vectors, failing with
`BAD_ARGUMENTS`:

```text
blob length > 2 GiB                → "exceeds absolute limit"
declared cardinality > 100,000,000 → "exceeds materialization limit"
```

Validation is layered: for a fully buffered `Puffin` file, a hostile manifest length above
2 GiB is rejected earlier, by the footer bounds/matching checks (the error names the hostile
length, e.g. `No Puffin footer blob at offset 4 length 3221225472`) — the dedicated
`exceeds absolute limit` message guards the unbuffered large-file path.

The cardinality ceiling compares against the footer's `cardinality` property, so one `Puffin`
read (the footer) is inherent; the ceiling SHALL reject before the vector payload is
deserialized or allocated — `PuffinFilesRead` SHALL NOT exceed the single footer read for such
a query.

### RQ.Iceberg.DeletionVectors.ErrorHandling.NonParquetDataFiles
version: 1.0

Deletion vectors require file-relative row numbers, which only the Parquet readers provide. A
deletion vector attached to a data file in any other format (ORC, Avro) SHALL fail with
`NOT_IMPLEMENTED` and a message naming both the feature and the actual format: "Deletion vectors
are only supported for data files of Parquet format in Iceberg, but got <format>".

### RQ.Iceberg.DeletionVectors.ErrorHandling.CompressedFooter
version: 1.0

The `Puffin` format allows the footer payload to be LZ4-compressed (footer `Flags`, byte 0,
bit 0; a single LZ4 frame with the content size present). Iceberg reference writers emit
uncompressed footers, but a compressed footer is spec-legal.

[ClickHouse] SHALL decompress an LZ4-compressed footer payload and return exactly the same
result as for an equivalent file with an uncompressed footer. It SHALL fail closed on any
footer flag construct it cannot interpret:

* a compressed footer frame that does not declare its content size SHALL be rejected
  (`LZ4_DECODER_FAILED`, `must declare content size`);
* reserved footer flag bits set SHALL be rejected with `BAD_ARGUMENTS`
  (`Unknown Puffin footer flags`).

It SHALL NOT parse the compressed bytes as plain JSON, silently skip the deletion vectors, or
return rows as if no vector existed.

## Distributed Reads

### RQ.Iceberg.DeletionVectors.Distributed.ClusterFunctions
version: 1.0

For every single-node requirement in this specification, the corresponding `*Cluster` table
function read (for example `icebergS3Cluster`) SHALL return an identical result. Deletion-vector
positions are resolved on the initiator and shipped to workers as part of the cluster read task.

### RQ.Iceberg.DeletionVectors.Distributed.ProtocolFailClosed
version: 1.0

A cluster worker whose protocol version is too old to carry the deletion state SHALL cause an
explicit `UNKNOWN_PROTOCOL` failure with no rows returned — never a silent read without deletes:

* a worker without `excluded_rows` support (protocol < 5) would otherwise drop deletion vectors
  and return deleted rows;
* a worker without `iceberg_info` support (protocol < 3) would otherwise skip position/equality
  delete transforms;
* a worker without `file_bucket_info` support (protocol < 4) would otherwise read whole files
  per bucket task and duplicate rows.

### RQ.Iceberg.DeletionVectors.Distributed.SplitDataFile
version: 1.0

When a single Parquet data file is split by row group across parallel threads or cluster nodes,
each read task SHALL apply the deletion vector to the correct absolute positions in its range.
For a file with deletions in every row group:

```text
single-threaded read == multi-threaded read == cluster read == count()
```

and all of them SHALL equal the writer-engine result, for any `max_threads` value and cluster
size.

### RQ.Iceberg.DeletionVectors.Distributed.SnapshotRefresh
version: 1.0

After an external engine commits a `DELETE` producing a deletion vector, the next cluster
read SHALL observe the new snapshot on **every** worker — without restarts and without
dropping any cache — even though each node holds its own `Puffin` files cache and Iceberg
metadata cache, including nodes whose caches were warmed on the previous snapshot. The
cluster result SHALL equal the single-node result taken after the same commit.

For example, for a 100-row table read through the cluster function, warmed on all nodes,
where an external `DELETE` then hides 10 rows:

```sql
SELECT count() FROM icebergS3Cluster('cluster', 'http://minio:9000/warehouse/ns/tbl', ...);
```

```text
count()   -- before the commit, caches warmed on every node
100
```

```sql
-- external writer commits the DELETE; very next cluster query:
SELECT count() FROM icebergS3Cluster('cluster', 'http://minio:9000/warehouse/ns/tbl', ...);
```

```text
count()
90
```

## Puffin Files Cache

Parsed deletion vectors are cached in memory so repeated queries do not re-fetch and re-decode
`Puffin` blobs. The cache entry key includes the storage identity, the `Puffin` object path and
etag (when the storage provides one), the blob offset and length, the referenced data file, and
the expected cardinalities — so a new Iceberg commit (new `Puffin` path) or replaced object
content (new etag) can never be served a stale vector. Objects without an etag (for example
local filesystem) are cached as well, keyed by the remaining components.

Cache requirements SHALL be verified on S3 or Azure storage, and profile events SHALL be read
from `system.query_log` per `query_id` so concurrent tests cannot perturb the counts.

### RQ.Iceberg.DeletionVectors.Cache.Setting
version: 1.0

[ClickHouse] SHALL provide the session setting `use_puffin_files_cache`, default `1`. With the
cache enabled, a repeated query SHALL be served from cache (`PuffinFilesCacheHits` increases,
`PuffinFilesRead` stays at 0). With `use_puffin_files_cache = 0`, every read SHALL re-fetch and
re-parse the vector (`PuffinFilesRead` increases on every query) and results SHALL remain
correct.

### RQ.Iceberg.DeletionVectors.Cache.ServerSettings
version: 1.0

[ClickHouse] SHALL provide the server settings `puffin_files_cache_policy` (default `SLRU`),
`puffin_files_cache_size` (default 512 MiB, `0` disables), `puffin_files_cache_max_entries`
(default 5000, `0` disables), and `puffin_files_cache_size_ratio` (default 0.5). Results SHALL
remain correct with the cache disabled by server setting even when `use_puffin_files_cache = 1`,
and `puffin_files_cache_size` SHALL be changeable without a restart with the live value
reported.

### RQ.Iceberg.DeletionVectors.Cache.Invalidation
version: 1.0

The cache SHALL never serve a stale deletion vector across Iceberg commits:

* a new commit produces a new `Puffin` path → new cache key → new load; a previously cached
  vector for the old path SHALL NOT be consulted;
* if a `Puffin` object at the same path is replaced with different content, the changed etag
  SHALL produce a different cache key;
* `SYSTEM DROP PUFFIN FILES CACHE` SHALL never be required for correctness after a normal
  Iceberg commit.

### RQ.Iceberg.DeletionVectors.Cache.EtagBypass
version: 1.0

The absence of an etag SHALL NOT break the cache. When the storage object has no etag (for
example local filesystem), [ClickHouse] SHALL build the cache key from the remaining components
(storage identity, object path, blob offset and length, referenced data file, cardinalities):
repeated reads of the same local table are served from the cache (`PuffinFilesCacheHits`
increases) and results SHALL remain correct.

### RQ.Iceberg.DeletionVectors.Cache.Eviction
version: 1.0

With a cache deliberately smaller than the working set, [ClickHouse] SHALL evict entries
(`PuffinFilesCacheWeightLost` increases) while query results remain correct. Empty deletion
vectors SHALL be cached as explicit entries with minimal weight.

### RQ.Iceberg.DeletionVectors.Cache.DropStatement
version: 1.0

[ClickHouse] SHALL support the statement:

```sql
SYSTEM DROP PUFFIN FILES CACHE;
```

It SHALL clear the cache so the next query records misses and re-reads the `Puffin` files, with
an unchanged logical result.

### RQ.Iceberg.DeletionVectors.Cache.RBAC
version: 1.0

`SYSTEM DROP PUFFIN FILES CACHE` SHALL require the `SYSTEM DROP PUFFIN FILES CACHE` privilege
(`GLOBAL` level, child of `SYSTEM DROP CACHE`). A user without it SHALL be denied; a user with
the parent `SYSTEM DROP CACHE` privilege SHALL be allowed; `SHOW PRIVILEGES` SHALL list the
privilege.

An illustrative privilege check is:

```sql
CREATE USER cache_operator;
GRANT SYSTEM DROP PUFFIN FILES CACHE ON *.* TO cache_operator;
SHOW GRANTS FOR cache_operator;
```

```text
GRANT SYSTEM DROP PUFFIN FILES CACHE ON *.* TO cache_operator
```

### RQ.Iceberg.DeletionVectors.Cache.Observability
version: 1.0

[ClickHouse] SHALL expose cache state via the `system.metrics` current metrics
`PuffinFilesCacheBytes` and
`PuffinFilesCacheFiles`, and per-query activity via the profile events `PuffinFilesRead`,
`PuffinFileReadMicroseconds`, `PuffinFilesCacheHits`, `PuffinFilesCacheMisses`, and
`PuffinFilesCacheWeightLost`. After a cold read of a table with deletion vectors: misses and
reads increase, read time is non-zero, and the metrics reflect the resident entries. On a warm
read: hits increase and `PuffinFilesRead` stays at 0.

```sql
SELECT ProfileEvents['PuffinFilesCacheHits'], ProfileEvents['PuffinFilesRead']
FROM system.query_log
WHERE type = 'QueryFinish' AND query_id = '...';
```

For a warm read, an illustrative result is:

```text
ProfileEvents['PuffinFilesCacheHits']  ProfileEvents['PuffinFilesRead']
1                                      0
```

### RQ.Iceberg.DeletionVectors.Cache.Concurrency
version: 1.0

Two concurrent queries over the same cold deletion vector SHALL both return correct results, and
the vector SHALL be loaded once (`PuffinFilesRead` totals 1 for that blob across both queries).
A `SYSTEM DROP PUFFIN FILES CACHE` racing with an in-flight load SHALL NOT produce a wrong
result — the load is discarded and recorded as a miss rather than being served stale.

### RQ.Iceberg.DeletionVectors.Cache.EntryIsolation
version: 1.0

A cache hit SHALL return a copy of the stored bitmap so that no query can mutate another query's
cached state. Many concurrent queries with different filters over the same deletion vector SHALL
each return the same result as the equivalent single query.
""",
)
