"""Error handling: every structural defect in a Puffin file, deletion-vector
blob, or the surrounding manifest metadata fails the query with an explicit
error code and a distinguishing message — never a silent partial result.

Payload- and footer-level defects reuse one fixture table per scenario:
:func:`manifest.replace_deletion_vector` rewrites the whole Puffin file and
re-synchronizes the manifest entry on every cycle, so each defect starts
from a consistent chain with exactly the injected fault."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.steps.spark as spark
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects
import iceberg.tests.deletion_vectors.steps.puffin as puffin
import iceberg.tests.deletion_vectors.steps.manifest as manifest

ROWS = 100
POSITIONS = list(range(0, ROWS, 10))  # the healthy vector: 10 positions
CARDINALITY = len(POSITIONS)


def valid_bitmap32():
    return puffin.build_bitmap32(POSITIONS)


def unsorted_container_bitmap():
    """A structurally parseable bitmap whose array container values are not
    sorted — must fail the roaring library's internal validation."""
    data = bytearray(puffin.build_bitmap32(POSITIONS))
    # array container values are the trailing 2*cardinality bytes;
    # swapping the first two u16 values breaks the sorted invariant
    tail = len(data) - 2 * CARDINALITY
    data[tail : tail + 2], data[tail + 2 : tail + 4] = (
        data[tail + 2 : tail + 4],
        data[tail : tail + 2],
    )
    return puffin.build_roaring64(buckets=[(0, bytes(data))])


# name → (payload bytes, declared cardinality, expected message fragment)
MALFORMED_BLOBS = {
    "crc mismatch": (
        puffin.build_dv_payload(positions=POSITIONS, crc=0xDEADBEEF),
        CARDINALITY,
        "Deletion vector CRC mismatch",
    ),
    "wrong magic": (
        puffin.build_dv_payload(positions=POSITIONS, magic=b"\x00\x01\x02\x03"),
        CARDINALITY,
        "Invalid deletion vector magic",
    ),
    "combined length mismatch": (
        puffin.build_dv_payload(
            positions=POSITIONS,
            combined_length=len(puffin.build_roaring64(positions=POSITIONS)) + 9,
        ),
        CARDINALITY,
        "does not match combined length",
    ),
    "blob shorter than 12 bytes": (
        puffin.build_dv_payload(raw=b"\x00" * 8),
        CARDINALITY,
        "Deletion vector blob is too small",
    ),
    "bitmap header shorter than 8 bytes": (
        puffin.build_dv_payload(vector=b"\x01\x02\x03"),
        CARDINALITY,
        "Deletion vector bitmap is too small",
    ),
    "bitmap truncated mid-key": (
        puffin.build_dv_payload(
            vector=puffin.build_roaring64(
                buckets=[(0, valid_bitmap32())],
                bucket_count=2,
                trailing=b"\x00\x00",
            )
        ),
        CARDINALITY,
        "truncated while reading key",
    ),
    "container extends past the blob": (
        puffin.build_dv_payload(
            vector=puffin.build_roaring64(
                buckets=[
                    (0, puffin.build_bitmap32(POSITIONS, cardinality_overrides={0: 1000}))
                ]
            )
        ),
        CARDINALITY,
        "exceeds blob size",
    ),
    "roaring bitmap fails internal validation": (
        puffin.build_dv_payload(vector=unsorted_container_bitmap()),
        CARDINALITY,
        "failed internal validation",
    ),
    "bitmap keys not strictly ascending": (
        puffin.build_dv_payload(
            vector=puffin.build_roaring64(
                buckets=[
                    (1, puffin.build_bitmap32([1])),
                    (0, puffin.build_bitmap32([2])),
                ]
            )
        ),
        2,
        "must be sorted in ascending order",
    ),
    "bitmap key above INT32_MAX - 1": (
        puffin.build_dv_payload(
            vector=puffin.build_roaring64(
                buckets=[(0xFFFFFFFF, puffin.build_bitmap32([1]))]
            )
        ),
        1,
        "Invalid deletion vector bitmap key",
    ),
    "bitmap count above INT32_MAX": (
        puffin.build_dv_payload(
            vector=puffin.build_roaring64(
                buckets=[(0, valid_bitmap32())], bucket_count=1 << 33
            )
        ),
        CARDINALITY,
        "Invalid deletion vector bitmap count",
    ),
    "trailing bytes after the last container": (
        puffin.build_dv_payload(
            vector=puffin.build_roaring64(positions=POSITIONS, trailing=b"\x00\x00")
        ),
        CARDINALITY,
        "trailing bytes",
    ),
    "cardinality does not match deserialized row count": (
        puffin.build_dv_payload(positions=POSITIONS),
        CARDINALITY + 1,
        "does not match deserialized row count",
    ),
    "running cardinality exceeds the declared one": (
        puffin.build_dv_payload(positions=POSITIONS),
        CARDINALITY - 5,
        "exceeds declared cardinality",
    ),
    # maximal position encodable with a valid bitmap key: the parser must
    # reject it before the manifest-level position/record_count checks run
    "position out of supported range": (
        puffin.build_dv_payload(
            vector=puffin.build_roaring64(
                buckets=[(0x7FFFFFFE, puffin.build_bitmap32([0xFFFFFFFF]))]
            )
        ),
        1,
        "is out of supported range",
    ),
}


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_MalformedBlob("1.0"))
def malformed_blob(self):
    """Every structurally invalid blob payload fails with BAD_ARGUMENTS and
    its specific message."""
    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition="id % 10 = 0"
        )

    for name, (payload, cardinality, fragment) in MALFORMED_BLOBS.items():
        with Check(name):
            with When(f"the vector is replaced with one whose {name}"):
                manifest.replace_deletion_vector(
                    namespace=table.namespace,
                    table_name=table.table_name,
                    payload=payload,
                    declared_cardinality=cardinality,
                )
            with Then(f"the read fails with BAD_ARGUMENTS: {fragment!r}"):
                common.assert_table_read_fails(
                    table=table,
                    error_name="BAD_ARGUMENTS",
                    message_fragment=fragment,
                )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_BlobMetadata("1.0"))
def blob_metadata(self):
    """Invalid Puffin footer metadata of a deletion-vector blob is rejected
    with BAD_ARGUMENTS and a specific message."""
    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition="id % 10 = 0"
        )
        referenced = manifest.find_dv_entries(table.namespace, table.table_name)[0][
            "entry"
        ]["data_file"]["referenced_data_file"]

    valid_payload = puffin.build_dv_payload(positions=POSITIONS)

    # name → (blob descriptor overrides, footer blobs mutator, fragment)
    defects = {
        "blob type is not deletion-vector-v1": (
            {"type": "unknown-blob-v9"},
            None,
            "expected deletion-vector-v1",
        ),
        "compression-codec present": (
            {"compression_codec": "zstd"},
            None,
            "must omit compression-codec",
        ),
        "referenced-data-file missing": (
            {"properties": {"cardinality": str(CARDINALITY)}},
            None,
            "missing required property 'referenced-data-file'",
        ),
        "referenced-data-file mismatch": (
            {
                "properties": {
                    "referenced-data-file": "s3://warehouse/other/file.parquet",
                    "cardinality": str(CARDINALITY),
                }
            },
            None,
            "does not match expected data file",
        ),
        "cardinality missing": (
            {"properties": {"referenced-data-file": referenced}},
            None,
            "missing required property 'cardinality'",
        ),
        "cardinality not an unsigned integer": (
            {
                "properties": {
                    "referenced-data-file": referenced,
                    "cardinality": "ten",
                }
            },
            None,
            "must be an unsigned integer",
        ),
        "cardinality does not match the manifest": (
            {
                "properties": {
                    "referenced-data-file": referenced,
                    "cardinality": str(CARDINALITY - 3),
                }
            },
            None,
            "does not match expected cardinality",
        ),
        "no blob at the manifest offset": (
            {"offset": 987654},
            None,
            "No Puffin footer blob at offset",
        ),
        "two blobs claim the same offset": (
            None,
            lambda blobs: blobs + [dict(blobs[0])],
            "Multiple Puffin blobs claim offset",
        ),
    }

    for name, (overrides, blobs_mutator, fragment) in defects.items():
        with Check(name):
            with When(f"the Puffin footer is rebuilt with {name}"):
                manifest.replace_deletion_vector(
                    namespace=table.namespace,
                    table_name=table.table_name,
                    payload=valid_payload,
                    declared_cardinality=CARDINALITY,
                    blob_overrides=overrides,
                    footer_blobs_mutator=blobs_mutator,
                )
            with Then(f"the read fails with BAD_ARGUMENTS: {fragment!r}"):
                common.assert_table_read_fails(
                    table=table,
                    error_name="BAD_ARGUMENTS",
                    message_fragment=fragment,
                )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_BlobBounds("1.0"))
def blob_bounds(self):
    """A manifest-declared blob location that does not fit in the Puffin
    file is rejected with BAD_ARGUMENTS."""
    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition="id % 10 = 0"
        )
        puffin_key = s3_objects.find_puffin_keys(
            table.namespace, table.table_name
        )[0]
        file_size = s3_objects.object_size(puffin_key)

    valid_payload = puffin.build_dv_payload(positions=POSITIONS)

    def set_fields(**fields):
        def mutator(entry):
            entry["data_file"].update(fields)

        return mutator

    defects = {
        "negative offset": set_fields(content_offset=-1),
        "negative length": set_fields(content_size_in_bytes=-5),
        "offset beyond the file size": set_fields(content_offset=file_size + 100),
        "length beyond the file size": set_fields(
            content_size_in_bytes=file_size + 100
        ),
        "offset plus length overflowing": set_fields(
            content_offset=2**62, content_size_in_bytes=2**62
        ),
    }

    for name, entry_mutator in defects.items():
        with Check(name):
            with When(f"the manifest declares a blob location with {name}"):
                manifest.replace_deletion_vector(
                    namespace=table.namespace,
                    table_name=table.table_name,
                    payload=valid_payload,
                    declared_cardinality=CARDINALITY,
                    entry_mutator=entry_mutator,
                )
            with Then("the read fails with BAD_ARGUMENTS"):
                common.assert_table_read_fails(
                    table=table, error_name="BAD_ARGUMENTS"
                )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ManifestConsistency("1.0"))
def manifest_consistency(self):
    """Internally inconsistent Iceberg metadata is rejected with
    ICEBERG_SPECIFICATION_VIOLATION."""

    with Check("deletion-vector entry without referenced_data_file"):
        with Given("a table with a deletion vector"):
            table = common.table_with_deletion_vectors(rows=ROWS)
        with When("the entry's referenced_data_file is removed"):

            def clear_reference(entry):
                entry["data_file"]["referenced_data_file"] = None

            manifest.replace_deletion_vector(
                namespace=table.namespace,
                table_name=table.table_name,
                entry_mutator=clear_reference,
            )
        with Then("the read fails"):
            common.assert_table_read_fails(
                table=table, error_name="ICEBERG_SPECIFICATION_VIOLATION"
            )

    with Check("deletion-vector entry with negative record_count"):
        with Given("a table with a deletion vector"):
            table = common.table_with_deletion_vectors(rows=ROWS)
        with When("the entry's record_count is made negative"):
            manifest.replace_deletion_vector(
                namespace=table.namespace,
                table_name=table.table_name,
                declared_cardinality=-5,
            )
        with Then("the read fails"):
            common.assert_table_read_fails(
                table=table, error_name="ICEBERG_SPECIFICATION_VIOLATION"
            )

    with Check("data-file entry missing record_count"):
        with Given("a table with a deletion vector"):
            table = common.table_with_deletion_vectors(rows=ROWS)
        with When("the data file's record_count is removed"):

            def clear_record_count(entry):
                entry["data_file"]["record_count"] = None

            manifest.mutate_manifest_entries_with_nullable_field(
                namespace=table.namespace,
                table_name=table.table_name,
                field_name="record_count",
                mutator=clear_record_count,
                content=manifest.MANIFEST_LIST_DATA,
            )
        with Then("the read fails"):
            common.assert_table_read_fails(
                table=table, error_name="ICEBERG_SPECIFICATION_VIOLATION"
            )

    with Check("data-file entry with negative record_count"):
        with Given("a table with a deletion vector"):
            table = common.table_with_deletion_vectors(rows=ROWS)
        with When("the data file's record_count is made negative"):

            def negative_record_count(entry):
                entry["data_file"]["record_count"] = -1
                return entry

            manifest.mutate_manifest_entries(
                namespace=table.namespace,
                table_name=table.table_name,
                mutator=negative_record_count,
                content=manifest.MANIFEST_LIST_DATA,
            )
        with Then("the read fails"):
            common.assert_table_read_fails(
                table=table, error_name="ICEBERG_SPECIFICATION_VIOLATION"
            )

    with Check("vector record_count above the data file's record_count"):
        with Given("a table with a deletion vector"):
            table = common.table_with_deletion_vectors(rows=ROWS)
        with When("the vector's record_count exceeds the data file's"):
            manifest.replace_deletion_vector(
                namespace=table.namespace,
                table_name=table.table_name,
                declared_cardinality=ROWS + 50,
            )
        with Then("the read fails before any Puffin I/O"):
            log_comment = common.unique_log_comment("mc_card")
            common.assert_table_read_fails(
                table=table,
                error_name="ICEBERG_SPECIFICATION_VIOLATION",
                log_comment=log_comment,
            )
            reads = common.get_profile_event_of_failed_query(
                event="PuffinFilesRead", log_comment=log_comment
            )
            assert reads == 0, error(f"PuffinFilesRead = {reads}")

    with Check("two deletion vectors referencing the same data file"):
        with Given("a table with a deletion vector"):
            table = common.table_with_deletion_vectors(rows=ROWS)
        with When("the vector's manifest entry is duplicated"):
            manifest.duplicate_dv_entry(
                namespace=table.namespace, table_name=table.table_name
            )
        with Then("the read fails"):
            common.assert_table_read_fails(
                table=table,
                error_name="ICEBERG_SPECIFICATION_VIOLATION",
                message_fragment="Multiple deletion vectors match data file",
            )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ResourceLimits("1.0"))
def resource_limits(self):
    """Hard resource limits: blob length above 2 GiB and cardinality above
    100,000,000 fail with BAD_ARGUMENTS, the latter before the Puffin file
    is even opened."""

    with Check("blob length above the absolute limit"):
        with Given("a table with a deletion vector"):
            table = common.table_with_deletion_vectors(rows=ROWS)
        with When("the manifest declares a blob length above 2 GiB"):

            def huge_length(entry):
                entry["data_file"]["content_size_in_bytes"] = 3 * 2**30

            manifest.replace_deletion_vector(
                namespace=table.namespace,
                table_name=table.table_name,
                entry_mutator=huge_length,
            )
        with Then("the read fails with BAD_ARGUMENTS: exceeds absolute limit"):
            common.assert_table_read_fails(
                table=table,
                error_name="BAD_ARGUMENTS",
                message_fragment="exceeds absolute limit",
            )

    with Check("declared cardinality above the materialization limit"):
        with Given(
            "a table whose data file pretends to be large enough for a "
            "vector of 100,000,001 positions"
        ):
            table = common.table_with_deletion_vectors(rows=ROWS)

            def inflate_record_count(entry):
                entry["data_file"]["record_count"] = 200_000_000
                return entry

            manifest.mutate_manifest_entries(
                namespace=table.namespace,
                table_name=table.table_name,
                mutator=inflate_record_count,
                content=manifest.MANIFEST_LIST_DATA,
            )

        with When("the vector declares cardinality above 100,000,000"):
            manifest.replace_deletion_vector(
                namespace=table.namespace,
                table_name=table.table_name,
                declared_cardinality=100_000_001,
            )

        with Then("the read fails before the Puffin file is opened"):
            log_comment = common.unique_log_comment("rl_card")
            common.assert_table_read_fails(
                table=table,
                error_name="BAD_ARGUMENTS",
                message_fragment="exceeds materialization limit",
                log_comment=log_comment,
            )
            reads = common.get_profile_event_of_failed_query(
                event="PuffinFilesRead", log_comment=log_comment
            )
            assert reads == 0, error(
                f"PuffinFilesRead = {reads}: the hostile manifest forced "
                f"Puffin I/O"
            )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_NonParquetDataFiles("1.0"))
def non_parquet_data_files(self):
    """A deletion vector attached to a non-Parquet data file fails with
    NOT_IMPLEMENTED naming the feature and the actual format."""
    with Given("a v3 merge-on-read table with ORC data files"):
        table = common.table_with_deletion_vectors(
            rows=0,
            extra_properties={"write.format.default": "orc"},
            setup_statements=[common.insert_range_statement(50)],
            verify_puffin=False,
        )

    with When("Spark deletes rows, producing a vector over an ORC file"):
        spark.delete_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            condition="id < 5",
        )

    if not s3_objects.find_puffin_keys(table.namespace, table.table_name):
        with When(
            "the writer did not produce a vector for ORC — falling back to "
            "declaring a Parquet file's format as ORC in the manifest"
        ):
            table = common.table_with_deletion_vectors(rows=50)

            def orc_format(entry):
                entry["data_file"]["file_format"] = "ORC"
                return entry

            manifest.mutate_manifest_entries(
                namespace=table.namespace,
                table_name=table.table_name,
                mutator=orc_format,
                content=manifest.MANIFEST_LIST_DATA,
            )

    with Then("the read fails with NOT_IMPLEMENTED naming both sides"):
        common.assert_table_read_fails(
            table=table,
            error_name="NOT_IMPLEMENTED",
            message_fragment="only supported for data files of Parquet format",
        )


@TestFeature
@Name("error handling")
def feature(self, minio_root_user, minio_root_password):
    """Error handling for corrupt Puffin files and inconsistent metadata."""
    Scenario(test=malformed_blob, flags=TE)()
    Scenario(test=blob_metadata, flags=TE)()
    Scenario(test=blob_bounds, flags=TE)()
    Scenario(test=manifest_consistency, flags=TE)()
    Scenario(test=resource_limits, flags=TE)()
    Scenario(test=non_parquet_data_files, flags=TE)()
