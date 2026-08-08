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
    zero rows while the file stays present and the query stays valid."""
    with Given(
        "a table with file A (ids 0..99) and file B (ids 100..149), "
        "where Spark deleted all of file A"
    ):
        table = common.table_with_deletion_vectors(
            rows=0,
            setup_statements=[
                common.insert_range_statement(100),
                "INSERT INTO {table} SELECT id + 100, "
                "concat('row-', CAST(id + 100 AS STRING)) FROM range(50)",
                "DELETE FROM {table} WHERE id < 100",
            ],
        )

    with And("the fully-deleted data file was not physically removed"):
        data_keys = [
            key
            for key in s3_objects.list_keys(f"{table.prefix}/data/")
            if key.endswith(".parquet")
        ]
        assert len(data_keys) >= 2, error(
            f"expected both data files to remain, found {data_keys}"
        )

    expected = list(range(100, 150))

    with Then("SELECT * reflects the empty contribution"):
        common.assert_visible_ids(table=table, ids=expected)

    with And("count() reflects it"):
        assert common.count_rows(table=table) == 50, error()

    with And("aggregates reflect it"):
        result = common.read_result(table=table, columns="sum(id), min(id), max(id)")
        assert result.output.split() == [
            str(sum(expected)),
            "100",
            "149",
        ], error(result.output)

    with And("filtered reads reflect it"):
        result = common.read_result(
            table=table, columns="count()", where_clause="id < 120"
        )
        assert int(result.output.strip()) == 20, error(result.output)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_BoundaryPositions("1.0"))
def boundary_positions(self):
    """Positions 0 and N-1 apply; a position >= N and a declared
    cardinality > N are rejected as specification violations."""
    rows = 100

    with Check("first and last row positions apply"):
        with Given("a table where Spark deleted the first and last rows"):
            table = common.table_with_deletion_vectors(
                rows=rows, delete_condition="id IN (0, 99)"
            )
        with Then("only positions 0 and 99 disappeared"):
            common.assert_visible_ids(table=table, ids=list(range(1, 99)))

    with Check("position >= record_count is rejected"):
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

    with Check("cardinality > record_count is rejected before Puffin I/O"):
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


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_RowGroupBoundaries("1.0"))
def row_group_boundaries(self):
    """Vector positions are absolute file row numbers, not row-group
    relative — under full reads, predicate pruning, and parallel readers."""
    rows = 10000
    deleted = [99, 100, 4999, 5000, 9998, 9999]
    expected = common.expected_ids(rows, deleted)

    with Given(
        "a table whose single data file has many small row groups and a "
        "vector deleting rows straddling row-group boundaries"
    ):
        table = common.table_with_deletion_vectors(
            rows=rows,
            delete_condition=f"id IN ({', '.join(str(i) for i in deleted)})",
            extra_properties={
                "write.parquet.row-group-size-bytes": "4096",
                "write.parquet.page-size-bytes": "1024",
            },
        )

    with Check("full single-threaded read"):
        common.assert_visible_ids(
            table=table, ids=expected, settings=[("max_threads", "1")]
        )

    with Check("full multi-threaded read"):
        common.assert_visible_ids(
            table=table, ids=expected, settings=[("max_threads", "8")]
        )

    with Check("predicate read pruning some row groups"):
        result = common.read_result(
            table=table,
            columns="id",
            where_clause="id BETWEEN 90 AND 110",
            order_by="id",
            settings=[("input_format_parquet_filter_push_down", "1")],
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == [i for i in range(90, 111) if i not in (99, 100)], error(
            f"predicate read returned {ids}"
        )

    with Check("count() agrees"):
        assert common.count_rows(table=table) == len(expected), error()


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
                "INSERT INTO {table} SELECT id + 100, "
                "concat('row-', CAST(id + 100 AS STRING)) FROM range(100)",
                "DELETE FROM {table} WHERE id % 10 = 0",
            ],
        )

    deleted = list(range(0, 200, 10))
    expected = common.expected_ids(200, deleted)

    with And("both vectors live in one shared Puffin file"):
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
            entry["entry"]["data_file"]["referenced_data_file"]
            for entry in dv_entries
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
    Scenario(test=empty_vector, flags=TE)()
    Scenario(test=all_rows_deleted, flags=TE)()
    Scenario(test=boundary_positions, flags=TE)()
    Scenario(test=row_group_boundaries, flags=TE)()
    Scenario(test=shared_puffin_file, flags=TE)()
