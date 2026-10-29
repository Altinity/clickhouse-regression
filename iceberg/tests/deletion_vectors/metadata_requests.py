"""Object metadata (S3 ``HEAD``) requests of deletion-vector loads.

Looking a vector up in the Puffin files cache needs the etag of the object
holding it, so every load — warm or cold — pays one ``HEAD`` for it. A cold
load then opens the object for the blob and, for a Puffin file, again for
its footer; each of those opens must reuse the metadata the etag request
already returned (Altinity/ClickHouse#2419). Without that reuse, a cold load
costs one extra ``HEAD`` per vector plus one per Puffin footer.

Each scenario reads the same table three times — warm, cold, and with the
cache disabled — and compares the ``S3HeadObject`` profile event of the
three queries. Requests for data files and Iceberg metadata are identical
across the three reads, so only the vector loads can make them differ.

Reads scan (``sum(id)``) rather than ``count()``: the snapshot-summary count
shortcut can answer ``count()`` without opening any vector at all."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.steps.spark as spark
import iceberg.tests.steps.metrics as metrics
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.manifest as manifest

ROWS_PER_FILE = 100


def insert_file_statement(file_index):
    """Spark INSERT writing ids ``file_index*100 .. file_index*100+99`` into
    exactly one data file."""
    offset = file_index * ROWS_PER_FILE
    return (
        f"INSERT INTO {{table}} SELECT /*+ COALESCE(1) */ id + {offset}, "
        f"concat('row-', CAST(id + {offset} AS STRING)) FROM range({ROWS_PER_FILE})"
    )


@TestStep(When)
def scan_read(self, table, expected_sum, extra_settings=None):
    """Read the table with a scanning query, check the result, and return
    the query's log_comment."""
    log_comment = common.unique_log_comment("dv_head")
    settings = [("log_comment", log_comment)] + list(extra_settings or [])
    result = common.read_result(table=table, columns="sum(id)", settings=settings)
    assert int(result.output.strip()) == expected_sum, error(
        f"sum(id) = {result.output.strip()}, expected {expected_sum}"
    )
    return log_comment


@TestStep(Then)
def read_events(self, log_comment):
    """``S3HeadObject`` and the Puffin profile events of one read."""
    events = common.get_puffin_events(log_comment=log_comment)
    events["S3HeadObject"] = metrics.get_profile_event(
        event="S3HeadObject", log_comment=log_comment
    )
    return events


@TestStep(Then)
def assert_cold_load_reuses_metadata(self, table, expected_ids):
    """Warm, cold, and cache-disabled reads of *table* issue the same number
    of ``HEAD`` requests, and each read exercised the path it claims to."""
    vectors = len(manifest.find_dv_entries(table.namespace, table.table_name))
    expected_sum = sum(expected_ids)

    with By("verifying the visible rows"):
        common.assert_visible_ids(table=table, ids=expected_ids)

    with And("warming the metadata and Puffin caches"):
        scan_read(table=table, expected_sum=expected_sum)

    with When("the table is read with warm vectors"):
        warm = read_events(
            log_comment=scan_read(table=table, expected_sum=expected_sum)
        )

    with And("the table is read after dropping the Puffin cache"):
        common.drop_puffin_cache()
        cold = read_events(
            log_comment=scan_read(table=table, expected_sum=expected_sum)
        )

    with And("the table is read with the Puffin cache disabled"):
        disabled = read_events(
            log_comment=scan_read(
                table=table,
                expected_sum=expected_sum,
                extra_settings=[("use_puffin_files_cache", "0")],
            )
        )

    note(f"{vectors} vector(s); warm={warm}; cold={cold}; disabled={disabled}")

    with Then("the warm read was served from the cache"):
        assert warm["PuffinFilesCacheHits"] == vectors, error(f"warm: {warm}")
        assert warm["PuffinFilesRead"] == 0, error(f"warm: {warm}")

    with And("the cold read loaded every vector"):
        assert cold["PuffinFilesCacheMisses"] == vectors, error(f"cold: {cold}")
        assert cold["PuffinFilesRead"] > 0, error(f"cold: {cold}")

    with And("the cache-disabled read loaded the vectors without the cache"):
        assert disabled["PuffinFilesRead"] > 0, error(f"disabled: {disabled}")
        assert disabled["PuffinFilesCacheHits"] == 0, error(f"disabled: {disabled}")

    with And("the cold load issued no more HEAD requests than the warm read"):
        assert cold["S3HeadObject"] == warm["S3HeadObject"], error(
            f"cold read issued {cold['S3HeadObject']} HEAD request(s), warm read "
            f"{warm['S3HeadObject']}: {cold['S3HeadObject'] - warm['S3HeadObject']} "
            f"extra for {vectors} vector(s)"
        )

    with And("the cache-disabled read issued as many HEAD requests as the warm read"):
        assert disabled["S3HeadObject"] == warm["S3HeadObject"], error(
            f"cache-disabled read issued {disabled['S3HeadObject']} HEAD "
            f"request(s), warm read {warm['S3HeadObject']}"
        )


@TestScenario
def single_vector(self):
    """One data file with one deletion vector."""
    with Given("a table with one data file and one deletion vector"):
        table = common.table_with_deletion_vectors(rows=ROWS_PER_FILE)
        common.assert_data_file_count(table=table, count=1)

    assert_cold_load_reuses_metadata(
        table=table,
        expected_ids=common.expected_ids(ROWS_PER_FILE, range(0, ROWS_PER_FILE, 10)),
    )


@TestScenario
def shared_puffin_file(self):
    """Several vectors stored in one Puffin file: the footer is read once
    and every blob read reuses the same metadata."""
    files = 4
    rows = files * ROWS_PER_FILE

    with Given("a table with four data files and one DELETE touching all of them"):
        table = common.table_with_deletion_vectors(
            rows=0,
            setup_statements=[insert_file_statement(index) for index in range(files)]
            + ["DELETE FROM {table} WHERE id % 10 = 0"],
        )
        common.assert_data_file_count(table=table, count=files)

    with And("all four vectors live in one object"):
        entries = manifest.find_dv_entries(table.namespace, table.table_name)
        paths = {entry["entry"]["data_file"]["file_path"] for entry in entries}
        assert len(entries) == files, error(
            f"expected {files} vectors, found {len(entries)}"
        )
        assert len(paths) == 1, error(
            f"expected one shared object, found {sorted(paths)}"
        )

    assert_cold_load_reuses_metadata(
        table=table, expected_ids=common.expected_ids(rows, range(0, rows, 10))
    )


@TestScenario
def separate_puffin_files(self):
    """Vectors committed by separate DELETEs live in separate Puffin files,
    each with its own footer."""
    files = 2
    rows = files * ROWS_PER_FILE

    with Given("a table with two data files and one DELETE per file"):
        table = common.table_with_deletion_vectors(
            rows=0,
            setup_statements=[insert_file_statement(index) for index in range(files)]
            + [
                f"DELETE FROM {{table}} WHERE id < {ROWS_PER_FILE} AND id % 10 = 0",
                f"DELETE FROM {{table}} WHERE id >= {ROWS_PER_FILE} AND id % 10 = 0",
            ],
        )
        common.assert_data_file_count(table=table, count=files)

    with And("each vector lives in its own object"):
        entries = manifest.find_dv_entries(table.namespace, table.table_name)
        paths = {entry["entry"]["data_file"]["file_path"] for entry in entries}
        assert len(entries) == files, error(
            f"expected {files} vectors, found {len(entries)}"
        )
        assert len(paths) == files, error(
            f"expected {files} objects, found {sorted(paths)}"
        )

    assert_cold_load_reuses_metadata(
        table=table, expected_ids=common.expected_ids(rows, range(0, rows, 10))
    )


@TestScenario
def vector_after_later_delete(self):
    """A vector committed by a later writer DELETE, which replaces the
    file's previous vector, is loaded with the same number of requests."""
    rows = ROWS_PER_FILE

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(rows=rows)

    with When("Spark deletes more rows from the same data file"):
        spark.delete_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            condition="id IN (5, 15)",
        )
        common.assert_writer_produced_vectors(table=table)

    deleted = set(range(0, rows, 10)) | {5, 15}
    assert_cold_load_reuses_metadata(
        table=table, expected_ids=common.expected_ids(rows, deleted)
    )


@TestFeature
@Requirements(RQ_Iceberg_DeletionVectors_Cache_MetadataRequestReuse("1.0"))
@Name("metadata requests")
def feature(self, minio_root_user, minio_root_password):
    """A deletion-vector load reuses the object metadata of its cache-key
    etag request instead of issuing more HEAD requests."""
    Scenario(run=single_vector)
    Scenario(run=shared_puffin_file)
    Scenario(run=separate_puffin_files)
    Scenario(run=vector_after_later_delete)
