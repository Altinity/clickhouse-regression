from urllib.parse import urlparse

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.create import partitioned_replicated_merge_tree_table
from helpers.queries import select_all_ordered
from s3.requirements.export_partition import *
from s3.tests.export_partition.steps import (
    create_s3_table,
    default_columns,
    export_partitions,
    wait_for_export_to_complete,
)

# Altinity/ClickHouse#2311 / PR #2294: a multi-file part export that dies after the
# first destination file is written must not be treated as complete under the
# default `skip` policy. Completeness is the per-part commit marker, not the
# existence of the first split file.


def _minio():
    cluster = current().context.cluster
    return cluster.minio_client, cluster.minio_bucket


def _normalize_key(key):
    """Collapse duplicate slashes. The partition commit path is built as
    ``raw_path + '/commit_…'``; when ``raw_path`` already ends with ``/``
    the recorded key contains ``//``, but MinIO stores a single slash.
    """
    while "//" in key:
        key = key.replace("//", "/")
    return key.lstrip("/")


def _object_key(path):
    """Turn a destination path (object key or URL) into a bucket-relative key."""
    path = path.strip()
    if "://" not in path:
        return _normalize_key(path)
    parsed = urlparse(path)
    rest = parsed.path.lstrip("/")
    bucket = current().context.cluster.minio_bucket
    prefix = f"{bucket}/"
    if rest.startswith(prefix):
        rest = rest[len(prefix) :]
    return _normalize_key(rest)


def _find_object(key, objects):
    """Resolve *key* against listed object names, allowing slash-normalization.

    The recorded commit path can differ from the stored key only in redundant
    slashes.
    """
    normalized = _normalize_key(key)
    if normalized in objects:
        return normalized
    basename = normalized.rsplit("/", 1)[-1]
    matches = [
        obj
        for obj in objects
        if _normalize_key(obj) == normalized or obj.endswith("/" + basename)
    ]
    assert matches, error(
        f"object {key!r} (normalized {normalized!r}) not found: {objects}"
    )
    return matches[0]


def _uri_object_prefix():
    """Object-key prefix of the current destination URI (inside the MinIO bucket)."""
    parsed = urlparse(current().context.uri)
    rest = parsed.path.lstrip("/")
    bucket = current().context.cluster.minio_bucket
    prefix = f"{bucket}/"
    if rest.startswith(prefix):
        return rest[len(prefix) :]
    return rest


def _list_objects(prefix):
    client, bucket = _minio()
    return sorted(
        obj.object_name
        for obj in client.list_objects(bucket, prefix=prefix, recursive=True)
    )


def _resolve_keys(recorded_paths):
    """Map recorded destination_file_paths onto MinIO object keys."""
    objects = _list_objects(_uri_object_prefix())
    return [_find_object(_object_key(path), objects) for path in recorded_paths]


def _list_partition_directory(data_key):
    """Data files and per-part commit markers sitting next to *data_key*.

    ``MultiFileStorageObjectStorageSink::commit`` writes ``commit_<part name>``
    in the same hive directory as the split parquet files. The partition-level
    marker lives one directory up and is not included here.
    """
    directory = data_key.rsplit("/", 1)[0] + "/"
    names = _list_objects(directory)
    data_files = [n for n in names if not n.rsplit("/", 1)[-1].startswith("commit_")]
    markers = [n for n in names if n.rsplit("/", 1)[-1].startswith("commit_")]
    return data_files, markers


def _split_export_settings(force=False, policy=None):
    settings = [("export_merge_tree_part_max_rows_per_file", "1")]
    if force:
        settings.append(("export_merge_tree_partition_force_export", "1"))
    if policy is not None:
        settings.append(
            ("export_merge_tree_part_file_already_exists_policy", policy)
        )
    return settings


@TestStep(Given)
def split_export_tables(self):
    """Create a source whose single part splits into one destination file per row.

    ``export_merge_tree_part_max_rows_per_file`` is evaluated once per chunk, and
    ``MergeTreeSequentialSource`` emits one chunk per index granule, so a part
    can only split at granule boundaries. Default granularity keeps a small part
    as a single granule; ``index_granularity = 1`` plus
    ``index_granularity_bytes = 0`` (disable adaptive granularity) is required.
    """
    source_table = f"source_{getuid()}"
    columns = default_columns()
    node = self.context.node

    with By("creating a replicated source with one granule per row"):
        partitioned_replicated_merge_tree_table(
            table_name=source_table,
            partition_by="p",
            columns=columns,
            stop_merges=True,
            cluster="replicated_cluster",
            populate=False,
            query_settings="index_granularity = 1, index_granularity_bytes = 0",
        )

    with And("I stop merges on every replica so part names stay stable"):
        for replica in self.context.nodes:
            replica.query(f"SYSTEM STOP MERGES {source_table}", exitcode=0)

    with And("I insert three rows into one partition as a single part"):
        node.query(f"INSERT INTO {source_table} VALUES (1, 1), (1, 2), (1, 3)")

    with And("I create an empty S3 destination"):
        s3_table = create_s3_table(
            table_name="s3", create_new_bucket=True, columns=columns
        )
    return source_table, s3_table, "1"


@TestStep(When)
def export_split_partition(
    self,
    source_table,
    destination_table,
    partition_id,
    force=False,
    policy=None,
    previous_transaction_id=None,
):
    """Export the partition with one row per destination file and wait for COMPLETED.

    A force re-export replaces the previous entry. Waiting for COMPLETED alone
    can succeed immediately on the old in-memory row, so a previous transaction
    id is required to observe the new attempt.
    """
    node = self.context.node
    export_partitions(
        source_table=source_table,
        destination_table=destination_table,
        node=node,
        partitions=[partition_id],
        settings=_split_export_settings(force=force, policy=policy),
        force_export=force,
        check_export=previous_transaction_id is None,
    )

    if previous_transaction_id is not None:
        with And("I wait for a new export transaction to replace the previous one"):
            last = None
            for attempt in retries(timeout=60, delay=0.5):
                with attempt:
                    last = node.query(
                        "SELECT transaction_id FROM system.replicated_partition_exports "
                        f"WHERE source_table = '{source_table}' "
                        f"AND destination_table = '{destination_table}' "
                        f"AND partition_id = '{partition_id}'",
                        exitcode=0,
                    ).output.strip()
                    assert last and last != previous_transaction_id, error(
                        f"transaction_id still {last!r}, wanted a value other than "
                        f"{previous_transaction_id!r}"
                    )
        wait_for_export_to_complete(
            source_table=source_table, partition_id=partition_id, node=node
        )


@TestStep(When)
def export_transaction_id(
    self, source_table, destination_table, partition_id, node=None
):
    """Return the current export transaction_id, or empty string if none."""
    if node is None:
        node = self.context.node
    return node.query(
        "SELECT transaction_id FROM system.replicated_partition_exports "
        f"WHERE source_table = '{source_table}' "
        f"AND destination_table = '{destination_table}' "
        f"AND partition_id = '{partition_id}'",
        exitcode=0,
    ).output.strip()


@TestStep(Then)
def recorded_export_paths(
    self, source_table, destination_table, partition_id, expected_count=None
):
    """Destination file paths recorded for the exported parts, in write order.

    Mirrors ``<export-entry>/processed/<part>/paths_in_destination`` in Keeper,
    which the commit phase turns into the partition commit marker.
    """
    node = self.context.node
    paths = []
    for attempt in retries(timeout=30, delay=1):
        with attempt:
            output = node.query(
                "SELECT arrayJoin(arrayFlatten(mapValues(destination_file_paths))) "
                "FROM system.replicated_partition_exports "
                f"WHERE source_table = '{source_table}' "
                f"AND destination_table = '{destination_table}' "
                f"AND partition_id = '{partition_id}'",
                exitcode=0,
            ).output
            paths = [line.strip() for line in output.splitlines() if line.strip()]
            if expected_count is not None:
                assert len(paths) == expected_count, error(
                    f"expected {expected_count} destination files, got {paths}"
                )
            else:
                assert paths, error("destination_file_paths is empty")
    return paths


@TestStep(Then)
def partition_commit_marker_lines(
    self, source_table, destination_table, partition_id, expected_count=None
):
    """Data-file paths listed inside the partition-level commit marker."""
    node = self.context.node
    marker = node.query(
        "SELECT committed_marker_file FROM system.replicated_partition_exports "
        f"WHERE source_table = '{source_table}' "
        f"AND destination_table = '{destination_table}' "
        f"AND partition_id = '{partition_id}'",
        exitcode=0,
    ).output.strip()
    assert marker, error("committed_marker_file is empty")

    client, bucket = _minio()
    objects = _list_objects(_uri_object_prefix())
    key = _find_object(_object_key(marker), objects)

    response = client.get_object(bucket, key)
    try:
        body = response.read().decode()
    finally:
        response.close()
        response.release_conn()

    lines = [line for line in body.splitlines() if line]
    if expected_count is not None:
        assert len(lines) == expected_count, error(
            f"partition commit marker listed {len(lines)} path(s), "
            f"expected {expected_count}: {lines}"
        )
    return lines


@TestScenario
@Name("skip re-export records every split file")
@Requirements(
    RQ_ClickHouse_ExportPartition_Idempotency("1.0"),
    RQ_ClickHouse_ExportPartition_ResumeAfterFailure("1.0"),
)
def skip_reports_every_split_file(self):
    """A `skip` re-export of an already-exported multi-file part must record
    every destination file, not just the first one.

    The recorded list is what the commit phase turns into the partition commit
    marker, so dropping the later split files from it misrepresents the export
    even though the data is all there.
    """
    with Given("a source part that splits into three destination files"):
        source_table, s3_table, partition_id = split_export_tables()

    with When("I export the partition"):
        export_split_partition(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
        )

    with Then("the export recorded three split files"):
        first_transaction_id = export_transaction_id(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
        )
        exported_paths = recorded_export_paths(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
            expected_count=3,
        )
        partition_commit_marker_lines(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
            expected_count=3,
        )

    with When("I force re-export with file_already_exists_policy=skip"):
        export_split_partition(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
            force=True,
            policy="skip",
            previous_transaction_id=first_transaction_id,
        )

    with Then("the skipped re-export recorded every split file"):
        skipped_paths = recorded_export_paths(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
            expected_count=3,
        )
        assert sorted(skipped_paths) == sorted(exported_paths), error(
            f"skipped re-export recorded {skipped_paths} instead of all split "
            f"files {exported_paths}"
        )

    with And("the partition commit marker still lists every split file"):
        partition_commit_marker_lines(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
            expected_count=3,
        )


@TestScenario
@Name("skip re-exports an incomplete multi-file part")
@Requirements(
    RQ_ClickHouse_ExportPartition_ResumeAfterFailure("1.0"),
    RQ_ClickHouse_ExportPartition_PartialProgress("1.0"),
)
def skip_reexports_incomplete_part(self):
    """A part whose multi-file export was interrupted must be re-exported in
    full under `skip`.

    The first split file existing proves nothing on its own: only the per-part
    commit marker, written after the last file is finalized, proves the part
    was fully exported. Removing the trailing files together with that marker
    reproduces what an attempt that died mid-part leaves behind
    (Altinity/ClickHouse#2311). The retry has to rewrite the missing files —
    those rows are produced by no other attempt.
    """
    node = self.context.node

    with Given("a source part that splits into three destination files"):
        source_table, s3_table, partition_id = split_export_tables()

    with When("I export the partition"):
        export_split_partition(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
        )

    with Then("the export wrote three split files and a per-part commit marker"):
        first_transaction_id = export_transaction_id(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
        )
        written_in_order = recorded_export_paths(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
            expected_count=3,
        )
        written_keys = _resolve_keys(written_in_order)

        data_files, markers = _list_partition_directory(written_keys[0])
        assert sorted(data_files) == sorted(written_keys), error(
            f"objects in the partition directory {data_files} do not match the "
            f"recorded paths {written_keys}"
        )
        assert len(markers) == 1, error(
            f"expected one per-part commit marker, got {markers}"
        )

    with And("I roll the destination back to first file finalized, nothing else"):
        client, bucket = _minio()
        for key in written_keys[1:] + markers:
            client.remove_object(bucket, key)

        surviving_data, surviving_markers = _list_partition_directory(written_keys[0])
        assert surviving_data == [written_keys[0]], error(
            f"expected only the first split file to remain, got {surviving_data}"
        )
        assert surviving_markers == [], error(
            f"expected the per-part commit marker to be gone, got {surviving_markers}"
        )

    with When("I force re-export with file_already_exists_policy=skip"):
        export_split_partition(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
            force=True,
            policy="skip",
            previous_transaction_id=first_transaction_id,
        )

    with Then("the retry rewrote the missing split files"):
        data_files_after, markers_after = _list_partition_directory(written_keys[0])
        assert len(data_files_after) == 3, error(
            f"retry left the part partially exported: {data_files_after}"
        )
        assert len(markers_after) == 1, error(
            f"retry did not rewrite the per-part commit marker: {markers_after}"
        )

    with And("the destination has every source row"):
        source_rows = select_all_ordered(table_name=source_table, node=node)
        for attempt in retries(timeout=30, delay=2):
            with attempt:
                dest_rows = select_all_ordered(table_name=s3_table, node=node)
                assert dest_rows == source_rows, error(
                    "rows from the split files the interrupted attempt never "
                    f"wrote are missing: source={source_rows} dest={dest_rows}"
                )

    with And("the partition commit marker lists every split file"):
        partition_commit_marker_lines(
            source_table=source_table,
            destination_table=s3_table,
            partition_id=partition_id,
            expected_count=3,
        )


@TestFeature
@Name("skip policy")
@Requirements(RQ_ClickHouse_ExportPartition_ResumeAfterFailure("1.0"))
def feature(self):
    """Check that `export_merge_tree_part_file_already_exists_policy=skip`
    does not drop split files of a multi-file part export
    (Altinity/ClickHouse#2311, PR #2294)."""

    Scenario(run=skip_reports_every_split_file)
    Scenario(run=skip_reexports_incomplete_part)
