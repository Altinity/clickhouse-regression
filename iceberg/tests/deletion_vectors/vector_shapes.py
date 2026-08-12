"""Vector content shapes: empty vectors, all-rows-deleted vectors, boundary
positions, absolute positions across row groups, and shared Puffin files."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects
import iceberg.tests.deletion_vectors.steps.puffin as puffin
import iceberg.tests.deletion_vectors.steps.manifest as manifest


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_EmptyVector("1.0"))
def empty_vector(self):
    """A deletion vector with cardinality 0 is valid: the file contributes
    all rows, the query does not fail, and repeated reads are served from
    cache without re-fetching the Puffin file."""
    rows = 100

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(rows=rows)

    with When("the vector is replaced with an empty one (cardinality 0)"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=[]),
            declared_cardinality=0,
        )
        common.drop_iceberg_metadata_cache()
        common.drop_puffin_cache()

    with Then("every row of the data file is visible"):
        common.assert_visible_ids(
            table=table,
            ids=list(range(rows)),
            settings=[("use_iceberg_metadata_files_cache", "0")],
        )

    with And("a repeated read neither fails nor re-fetches the Puffin file"):
        log_comment = common.unique_log_comment("empty_dv_warm")
        common.assert_visible_ids(
            table=table,
            ids=list(range(rows)),
            settings=[
                ("use_iceberg_metadata_files_cache", "0"),
                ("log_comment", log_comment),
            ],
        )
        events = common.get_puffin_events(log_comment=log_comment)
        assert events["PuffinFilesRead"] == 0, error(
            f"warm read re-fetched the Puffin file: {events}"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_AllRowsDeleted("1.0"))
def all_rows_deleted(self):
    """A vector deleting every row of its file makes the file contribute
    zero rows while the file stays present and the query stays valid.

    The full vector is crafted: a writer-issued DELETE whose predicate
    covers a whole data file becomes a metadata-only file drop (the file
    leaves the snapshot, no vector is written), so the fixture's partial
    vector on file A is replaced with one deleting all of its positions —
    which needs no assumption about physical row order."""
    with Given(
        "a table with file A (ids 0..99, partial vector) and file B "
        "(ids 100..149, no deletes)"
    ):
        table = common.table_with_deletion_vectors(
            rows=0,
            setup_statements=[
                common.insert_range_statement(100),
                "INSERT INTO {table} SELECT /*+ COALESCE(1) */ id + 100, "
                "concat('row-', CAST(id + 100 AS STRING)) FROM range(50)",
                "DELETE FROM {table} WHERE id < 100 AND id % 10 = 0",
            ],
        )

    with And("both data files are live in the current snapshot"):
        common.assert_data_file_count(table=table, count=2)

    with When("file A's vector is replaced with one deleting every position"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=list(range(100))),
            declared_cardinality=100,
        )
        common.drop_iceberg_metadata_cache()
        common.drop_puffin_cache()

    expected = list(range(100, 150))
    fresh = [("use_iceberg_metadata_files_cache", "0")]

    with Then("SELECT * reflects the empty contribution"):
        common.assert_visible_ids(table=table, ids=expected, settings=fresh)

    with And("count() reflects it"):
        assert common.count_rows(table=table, settings=fresh) == 50, error()

    with And("aggregates reflect it"):
        result = common.read_result(
            table=table, columns="sum(id), min(id), max(id)", settings=fresh
        )
        assert result.output.split() == [
            str(sum(expected)),
            "100",
            "149",
        ], error(result.output)

    with And("filtered reads reflect it"):
        result = common.read_result(
            table=table, columns="count()", where_clause="id < 120", settings=fresh
        )
        assert int(result.output.strip()) == 20, error(result.output)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_BoundaryPositions("1.0"))
def first_and_last_positions(self):
    """Positions 0 and N-1 apply to the first and last rows exactly."""
    rows = 100

    with Given("a table where Spark deleted the first and last rows"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id IN (0, 99)"
        )

    with Then("only positions 0 and 99 disappeared"):
        common.assert_visible_ids(table=table, ids=list(range(1, 99)))


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_BoundaryPositions("1.0"))
def position_at_record_count(self):
    """A position >= the data file's record count is rejected as a
    specification violation."""
    rows = 100

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(rows=rows)

    with When(f"the vector is replaced with one deleting position {rows}"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=[rows]),
            declared_cardinality=1,
        )

    with Then("the read fails with ICEBERG_SPECIFICATION_VIOLATION"):
        common.assert_table_read_fails(
            table=table, error_name="ICEBERG_SPECIFICATION_VIOLATION"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_BoundaryPositions("1.0"))
def cardinality_above_record_count(self):
    """A declared cardinality above the data file's record count is
    rejected before any Puffin I/O."""
    rows = 100

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(rows=rows)

    with When(
        "the manifest declares a vector cardinality above the data "
        "file's record count"
    ):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            declared_cardinality=rows + 1,
        )

    with Then("the read fails with ICEBERG_SPECIFICATION_VIOLATION"):
        log_comment = common.unique_log_comment("card_gt_n")
        common.assert_table_read_fails(
            table=table,
            error_name="ICEBERG_SPECIFICATION_VIOLATION",
            log_comment=log_comment,
        )

    with And("no Puffin file was read"):
        reads = common.get_profile_event_of_failed_query(
            event="PuffinFilesRead", log_comment=log_comment
        )
        assert reads == 0, error(f"PuffinFilesRead = {reads}, expected 0")


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_BoundaryPositions("1.0"))
def boundary_positions(self):
    """Positions 0 and N-1 apply; a position >= N and a declared
    cardinality > N are rejected as specification violations."""
    Scenario(run=first_and_last_positions)
    Scenario(run=position_at_record_count)
    Scenario(run=cardinality_above_record_count)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_RowGroupBoundaries("1.0"))
def single_threaded_read(self):
    """Full single-threaded read applies boundary-straddling positions."""
    ctx = self.context
    with Then("the visible row set matches"):
        common.assert_visible_ids(
            table=ctx.table,
            ids=ctx.expected,
            settings=ctx.fresh + [("max_threads", "1")],
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_RowGroupBoundaries("1.0"))
def multi_threaded_read(self):
    """Full multi-threaded read applies boundary-straddling positions."""
    ctx = self.context
    with Then("the visible row set matches"):
        common.assert_visible_ids(
            table=ctx.table,
            ids=ctx.expected,
            settings=ctx.fresh + [("max_threads", "8")],
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_RowGroupBoundaries("1.0"))
def predicate_read(self):
    """A predicate read pruning some row groups still applies the vector
    at absolute positions."""
    ctx = self.context
    with Then("rows around the first boundary match"):
        boundary_id = ctx.ids_in_order[ctx.boundaries[0]]
        low, high = boundary_id - 10, boundary_id + 10
        result = common.read_result(
            table=ctx.table,
            columns="id",
            where_clause=f"id BETWEEN {low} AND {high}",
            order_by="id",
            settings=ctx.fresh + [("input_format_parquet_filter_push_down", "1")],
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == [i for i in ctx.expected if low <= i <= high], error(
            f"predicate read around the boundary id {boundary_id} returned {ids}"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_RowGroupBoundaries("1.0"))
def count_agrees(self):
    """count() agrees with the boundary-straddling row set."""
    ctx = self.context
    with Then("the count matches the expected row set"):
        assert common.count_rows(table=ctx.table, settings=ctx.fresh) == len(
            ctx.expected
        ), error()


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_RowGroupBoundaries("1.0"))
def row_group_boundaries(self):
    """Vector positions are absolute file row numbers, not row-group
    relative — under full reads, predicate pruning, and parallel readers.

    The straddling positions are not guessed: the actual row-group sizes
    are read from the Parquet footer and the vector is crafted to delete
    the last row of one row group and the first row of the next, for the
    first few real boundaries plus the file edges."""
    rows = 10000

    with Given("a table whose single data file has many small row groups"):
        table = common.table_with_deletion_vectors(
            rows=rows,
            delete_condition="id = 0",  # any delete, to obtain a vector entry
            extra_properties={
                "write.parquet.row-group-size-bytes": "4096",
                "write.parquet.page-size-bytes": "1024",
            },
        )
        common.assert_data_file_count(table=table, count=1)

    with And("the actual row-group boundary positions are derived"):
        sizes = common.parquet_row_group_sizes(table=table)
        assert len(sizes) >= 2, error(
            f"expected multiple row groups, got sizes {sizes}"
        )
        boundaries = []
        cumulative = 0
        for size in sizes[:-1]:
            cumulative += size
            boundaries.append(cumulative)  # first row of the next row group
        positions = sorted(
            {position for b in boundaries[:3] for position in (b - 1, b)}
            | {0, rows - 1}
        )

    with And("the ids physically stored at those positions are read back"):
        # positions address physical rows, so the expected id set must come
        # from the file itself, not from assuming rows are stored in id
        # order
        ids_in_order = common.parquet_column_values(table=table, column="id")
        assert len(ids_in_order) == rows, error(
            f"data file holds {len(ids_in_order)} rows, expected {rows}"
        )
        deleted_ids = {ids_in_order[position] for position in positions}
        note(
            f"row group sizes {sizes[:5]}..., deleting positions "
            f"{positions} holding ids {sorted(deleted_ids)}"
        )

    with When("the vector is replaced to delete exactly those positions"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=positions),
            declared_cardinality=len(positions),
        )
        common.drop_iceberg_metadata_cache()
        common.drop_puffin_cache()

    self.context.table = table
    self.context.boundaries = boundaries
    self.context.ids_in_order = ids_in_order
    self.context.expected = sorted(set(ids_in_order) - deleted_ids)
    self.context.fresh = [("use_iceberg_metadata_files_cache", "0")]

    Scenario(run=single_threaded_read)
    Scenario(run=multi_threaded_read)
    Scenario(run=predicate_read)
    Scenario(run=count_agrees)


# Iceberg Java RoaringPositionBitmap.MAX_POSITION: key INT32_MAX - 1,
# sub-position 2^31 — ClickHouse enforces the same cap
MAX_SUPPORTED_POSITION = 0x7FFFFFFE80000000


@TestStep(When)
def admit_high_positions(self, table, record_count):
    """Inflate the data file's manifest record_count so vector positions
    above the physical row count pass the position bound check — a valid
    position must be below record_count, and a real data file with more
    than 2^32 rows is impractical to write."""

    def inflate(entry):
        entry["data_file"]["record_count"] = record_count
        return entry

    manifest.mutate_manifest_entries(
        namespace=table.namespace,
        table_name=table.table_name,
        mutator=inflate,
        content=manifest.MANIFEST_LIST_DATA,
    )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_SupportedPositionRange("1.0"))
def high_key_positions(self):
    """A vector position above 2^32 (high bitmap key >= 1) parses and is
    applied with 64-bit arithmetic throughout: the high position must not be
    truncated to its low 32 bits (which would wrongly delete the row at that
    low position), and low-key positions in the same vector still apply."""
    rows = 100
    low_position = 2
    high_position = (1 << 32) + 7  # 32-bit truncation would give position 7

    with Given("a table with a deletion vector over a single data file"):
        table = common.table_with_deletion_vectors(rows=rows)
        common.assert_data_file_count(table=table, count=1)
        ids_in_order = common.parquet_column_values(table=table)

    with When("the manifest admits positions above 2^32"):
        admit_high_positions(table=table, record_count=1 << 33)

    with And(f"the vector deletes positions {{{low_position}, 2^32 + 7}}"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=[low_position, high_position]),
            declared_cardinality=2,
        )
        common.drop_iceberg_metadata_cache()
        common.drop_puffin_cache()

    with Then(
        "only the physical row at position 2 is hidden — the row at "
        "position 7 stays visible, proving no 32-bit truncation"
    ):
        expected = [
            value
            for position, value in enumerate(ids_in_order)
            if position != low_position
        ]
        common.assert_visible_ids(
            table=table,
            ids=expected,
            settings=[("use_iceberg_metadata_files_cache", "0")],
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_SupportedPositionRange("1.0"))
def position_range_boundary(self):
    """The maximum supported position (key INT32_MAX - 1, sub-position 2^31
    — the Iceberg Java RoaringPositionBitmap.MAX_POSITION) is accepted, and
    the next position is rejected with BAD_ARGUMENTS."""
    rows = 100

    with Given("a table with a deletion vector over a single data file"):
        table = common.table_with_deletion_vectors(rows=rows)

    with When("the manifest admits positions up to past the supported maximum"):
        admit_high_positions(table=table, record_count=MAX_SUPPORTED_POSITION + 2)

    with And("the vector deletes exactly the maximum supported position"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=[MAX_SUPPORTED_POSITION]),
            declared_cardinality=1,
        )
        common.drop_iceberg_metadata_cache()
        common.drop_puffin_cache()

    with Then(
        "the read succeeds and every physical row stays visible — the "
        "position addresses a row far beyond the physical file, so "
        "acceptance of the boundary value is the point"
    ):
        common.assert_visible_ids(
            table=table,
            ids=list(range(rows)),
            settings=[("use_iceberg_metadata_files_cache", "0")],
        )

    with When("the vector deletes one position above the maximum"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=[MAX_SUPPORTED_POSITION + 1]),
            declared_cardinality=1,
        )

    with Then("the read fails with BAD_ARGUMENTS naming the range"):
        common.assert_table_read_fails(
            table=table,
            error_name="BAD_ARGUMENTS",
            message_fragment="is out of supported range",
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_SupportedPositionRange("1.0"))
def supported_position_range(self):
    """64-bit positions: high-key vectors apply without 32-bit truncation
    and the supported position range boundary is enforced exactly."""
    Scenario(run=high_key_positions)
    Scenario(run=position_range_boundary)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_SharedPuffinFile("1.0"))
def shared_puffin_file(self):
    """One Puffin file holding several vectors applies each blob only to
    its own data file — no union, no cross-file contamination."""
    with Given(
        "a table with two data files and one DELETE producing vectors "
        "for both in a single commit"
    ):
        table = common.table_with_deletion_vectors(
            rows=0,
            setup_statements=[
                common.insert_range_statement(100),
                "INSERT INTO {table} SELECT /*+ COALESCE(1) */ id + 100, "
                "concat('row-', CAST(id + 100 AS STRING)) FROM range(100)",
                "DELETE FROM {table} WHERE id % 10 = 0",
            ],
        )

    deleted = list(range(0, 200, 10))
    expected = common.expected_ids(200, deleted)

    with And("both data files are live and share one Puffin file"):
        common.assert_data_file_count(table=table, count=2)
        puffin_keys = s3_objects.find_puffin_keys(
            namespace=table.namespace, table_name=table.table_name
        )
        assert len(puffin_keys) == 1, error(
            f"expected one shared Puffin file, found {puffin_keys}"
        )
        dv_entries = manifest.find_dv_entries(
            namespace=table.namespace, table_name=table.table_name
        )
        referenced = {
            entry["entry"]["data_file"]["referenced_data_file"] for entry in dv_entries
        }
        assert len(referenced) == 2, error(
            f"expected vectors for two data files, got {referenced}"
        )

    with Then("reading both files applies each blob to its own file only"):
        common.assert_visible_ids(table=table, ids=expected)

    with And("a filter touching only one file applies only that file's blob"):
        result = common.read_result(
            table=table, columns="id", where_clause="id >= 100", order_by="id"
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == [i for i in expected if i >= 100], error(
            f"filtered read returned {len(ids)} rows"
        )


@TestFeature
@Name("vector shapes")
def feature(self, minio_root_user, minio_root_password):
    """Deletion-vector content shapes."""
    Scenario(run=empty_vector)
    Scenario(run=all_rows_deleted)
    Suite(run=boundary_positions)
    Suite(run=row_group_boundaries)
    Suite(run=supported_position_range)
    Scenario(run=shared_puffin_file)
