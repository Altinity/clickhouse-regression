"""Error handling: every structural defect in a Puffin file, deletion-vector
blob, or the surrounding manifest metadata fails the query with an explicit
error code and a distinguishing message — never a silent partial result.

Payload- and footer-level defect suites reuse one fixture table:
:func:`manifest.replace_deletion_vector` rewrites the whole Puffin file and
re-synchronizes the manifest entry on every cycle, so each defect scenario
starts from a consistent chain with exactly the injected fault."""

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
    # the overrun is caught inside the roaring library's bounds-checked
    # deserializer ("failed alloc while reading"), wrapped with the vector
    # context — verified against the real build
    "container extends past the blob": (
        puffin.build_dv_payload(
            vector=puffin.build_roaring64(
                buckets=[
                    (
                        0,
                        puffin.build_bitmap32(
                            POSITIONS, cardinality_overrides={0: 1000}
                        ),
                    )
                ]
            )
        ),
        CARDINALITY,
        "failed alloc while reading",
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
def blob_defect(self, name, payload, cardinality, fragment):
    """One structurally invalid blob payload fails with BAD_ARGUMENTS and
    its specific message."""
    table = self.context.table

    with When(f"the vector is replaced with one whose {name}"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=payload,
            declared_cardinality=cardinality,
        )

    with Then(f"the read fails with BAD_ARGUMENTS: {fragment!r}"):
        common.assert_table_read_fails(
            table=table, error_name="BAD_ARGUMENTS", message_fragment=fragment
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_MalformedBlob("1.0"))
def malformed_blob(self):
    """Every structurally invalid blob payload fails with BAD_ARGUMENTS and
    its specific message."""
    with Given("a table with a deletion vector"):
        self.context.table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition="id % 10 = 0"
        )

    for name, (payload, cardinality, fragment) in MALFORMED_BLOBS.items():
        Scenario(test=blob_defect, name=name)(
            name=name, payload=payload, cardinality=cardinality, fragment=fragment
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_BlobMetadata("1.0"))
def metadata_defect(self, name, overrides, blobs_mutator, fragment):
    """One invalid Puffin footer metadata defect is rejected with
    BAD_ARGUMENTS and a specific message."""
    table = self.context.table

    with When(f"the Puffin footer is rebuilt with {name}"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=self.context.valid_payload,
            declared_cardinality=CARDINALITY,
            blob_overrides=overrides,
            footer_blobs_mutator=blobs_mutator,
        )

    with Then(f"the read fails with BAD_ARGUMENTS: {fragment!r}"):
        common.assert_table_read_fails(
            table=table, error_name="BAD_ARGUMENTS", message_fragment=fragment
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_BlobMetadata("1.0"))
def blob_metadata(self):
    """Invalid Puffin footer metadata of a deletion-vector blob is rejected
    with BAD_ARGUMENTS and a specific message."""
    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition="id % 10 = 0"
        )
        self.context.table = table
        self.context.valid_payload = puffin.build_dv_payload(positions=POSITIONS)
        referenced = manifest.find_dv_entries(table.namespace, table.table_name)[0][
            "entry"
        ]["data_file"]["referenced_data_file"]

    # name → (blob descriptor overrides, footer blobs mutator, fragment)
    defects = {
        "blob type is not deletion-vector-v1": (
            {"type": "unknown-blob-v9"},
            None,
            "expected deletion-vector-v1",
        ),
        # the Puffin spec requires -1 for both fields on deletion-vector-v1
        "snapshot-id is not -1": (
            {"snapshot_id": 7},
            None,
            "snapshot-id and sequence-number must be -1",
        ),
        "sequence-number is not -1": (
            {"sequence_number": 7},
            None,
            "snapshot-id and sequence-number must be -1",
        ),
        # the build has quoted and unquoted variants of this message;
        # "must omit" is the stable common part
        "compression-codec present": (
            {"compression_codec": "zstd"},
            None,
            "must omit",
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
        # footer descriptors are bounds-validated before the manifest offset
        # is matched against them (verified against the real build), so the
        # two failure modes need separate defects
        "footer blob offset out of bounds": (
            {"offset": 987654},
            None,
            "offset/length out of bounds",
        ),
        # the bounds check is against the blob payload region, so a shifted
        # offset with the true length always lands out of bounds; a
        # shortened length keeps the descriptor in-bounds but no footer
        # blob then matches the manifest's (content_offset, size) pair
        "no blob at the manifest offset": (
            {"length": len(puffin.build_dv_payload(positions=POSITIONS)) - 4},
            None,
            "No Puffin footer blob at offset",
        ),
        # the duplicate's offset must be pinned: build_puffin appends the
        # copy's payload and would otherwise declare it at its real (second)
        # position, giving two distinct valid blobs instead of a conflict
        "two blobs claim the same offset": (
            None,
            lambda blobs: blobs + [dict(blobs[0], offset=4)],
            "Multiple Puffin blobs claim offset",
        ),
    }

    for name, (overrides, blobs_mutator, fragment) in defects.items():
        Scenario(test=metadata_defect, name=name)(
            name=name,
            overrides=overrides,
            blobs_mutator=blobs_mutator,
            fragment=fragment,
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_BlobBounds("1.0"))
def bounds_defect(self, name, entry_mutator):
    """One manifest-declared blob location that does not fit in the Puffin
    file is rejected with BAD_ARGUMENTS."""
    table = self.context.table

    with When(f"the manifest declares a blob location with {name}"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=self.context.valid_payload,
            declared_cardinality=CARDINALITY,
            entry_mutator=entry_mutator,
        )

    with Then("the read fails with BAD_ARGUMENTS"):
        common.assert_table_read_fails(table=table, error_name="BAD_ARGUMENTS")


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_BlobBounds("1.0"))
def blob_bounds(self):
    """A manifest-declared blob location that does not fit in the Puffin
    file is rejected with BAD_ARGUMENTS."""
    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition="id % 10 = 0"
        )
        self.context.table = table
        self.context.valid_payload = puffin.build_dv_payload(positions=POSITIONS)
        puffin_key = s3_objects.find_puffin_keys(table.namespace, table.table_name)[0]
        file_size = s3_objects.object_size(puffin_key)

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
        Scenario(test=bounds_defect, name=name)(name=name, entry_mutator=entry_mutator)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ManifestConsistency("1.0"))
def missing_referenced_data_file(self):
    """A deletion-vector entry without referenced_data_file is rejected."""
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


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ManifestConsistency("1.0"))
def negative_vector_record_count(self):
    """A deletion-vector entry with a negative record_count is rejected."""
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


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ManifestConsistency("1.0"))
def missing_data_record_count(self):
    """A data-file entry missing record_count is rejected."""
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


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ManifestConsistency("1.0"))
def negative_data_record_count(self):
    """A data-file entry with a negative record_count is rejected."""
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


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ManifestConsistency("1.0"))
def vector_record_count_above_data_file(self):
    """A vector record_count above the data file's record count is rejected
    before any Puffin I/O."""
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


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ManifestConsistency("1.0"))
def duplicate_vector_entries(self):
    """Two deletion vectors referencing the same data file fail the query."""
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


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ManifestConsistency("1.0"))
def manifest_consistency(self):
    """Internally inconsistent Iceberg metadata is rejected with
    ICEBERG_SPECIFICATION_VIOLATION."""
    Scenario(run=missing_referenced_data_file)
    Scenario(run=negative_vector_record_count)
    Scenario(run=missing_data_record_count)
    Scenario(run=negative_data_record_count)
    Scenario(run=vector_record_count_above_data_file)
    Scenario(run=duplicate_vector_entries)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ResourceLimits("1.0"))
def blob_length_limit(self):
    """A blob length above 2 GiB fails with BAD_ARGUMENTS before any
    allocation.

    Validation is layered: manifest-to-footer matching (and, for footer
    declarations, the buffered-region bounds check) rejects the hostile
    length before the dedicated absolute-limit check is reached — that
    check guards the unbuffered large-file path, which cannot be
    synthesized without a real multi-GiB object. The assertion therefore
    pins fail-closed rejection naming the hostile length."""
    huge = 3 * 2**30

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(rows=ROWS)

    with When("the manifest declares a blob length above 2 GiB"):

        def huge_length(entry):
            entry["data_file"]["content_size_in_bytes"] = huge

        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            entry_mutator=huge_length,
        )

    with Then("the read fails with BAD_ARGUMENTS naming the hostile length"):
        common.assert_table_read_fails(
            table=table,
            error_name="BAD_ARGUMENTS",
            message_fragment=str(huge),
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ResourceLimits("1.0"))
def cardinality_materialization_limit(self):
    """A declared cardinality above 100,000,000 fails with BAD_ARGUMENTS
    before the vector is materialized (the footer read itself is inherent —
    the ceiling compares against the footer's cardinality property)."""
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
        # a payload is passed so the Puffin file is rebuilt and its footer
        # cardinality property agrees with the manifest — otherwise the
        # footer-vs-manifest consistency check fires before the ceiling
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=POSITIONS),
            declared_cardinality=100_000_001,
        )

    with Then("the read fails before the vector is materialized"):
        log_comment = common.unique_log_comment("rl_card")
        common.assert_table_read_fails(
            table=table,
            error_name="BAD_ARGUMENTS",
            message_fragment="exceeds materialization limit",
            log_comment=log_comment,
        )
        # the ceiling compares against the footer's cardinality property,
        # so the footer parse (1 event) is inherent, and the rejected
        # blob-read attempt still counts its event on entry — but the
        # guard rejects before the payload is deserialized or allocated,
        # which the error message itself names
        reads = common.get_profile_event_of_failed_query(
            event="PuffinFilesRead", log_comment=log_comment
        )
        assert reads <= 2, error(
            f"PuffinFilesRead = {reads}: expected at most the footer parse "
            f"and the rejected blob-read attempt"
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_ResourceLimits("1.0"))
def resource_limits(self):
    """Hard resource limits: blob length above 2 GiB and cardinality above
    100,000,000 fail with BAD_ARGUMENTS."""
    Scenario(run=blob_length_limit)
    Scenario(run=cardinality_materialization_limit)


NON_PARQUET_FRAGMENT = "only supported for data files of Parquet format"


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_NonParquetDataFiles("1.0"))
def real_orc_data_file(self):
    """A deletion vector the writer produced over a real ORC data file
    fails with NOT_IMPLEMENTED (skipped explicitly if the Spark version
    refuses to attach vectors to ORC)."""
    with Given("a v3 merge-on-read table with ORC data files"):
        table = common.table_with_deletion_vectors(
            rows=0,
            extra_properties={"write.format.default": "orc"},
            setup_statements=[common.insert_range_statement(50)],
            verify_puffin=False,
        )

    with When("Spark deletes rows over the ORC file"):
        spark.delete_rows(
            namespace=table.namespace,
            table_name=table.table_name,
            condition="id < 5",
        )

    if not s3_objects.find_puffin_keys(table.namespace, table.table_name):
        skip(
            "this Spark/Iceberg version does not produce deletion "
            "vectors for ORC data files (no Puffin file after the "
            "DELETE), so the real-ORC integration case cannot run"
        )

    with Then("the read fails with NOT_IMPLEMENTED naming both sides"):
        common.assert_table_read_fails(
            table=table,
            error_name="NOT_IMPLEMENTED",
            message_fragment=NON_PARQUET_FRAGMENT,
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_NonParquetDataFiles("1.0"))
def manifest_declares_orc(self):
    """A manifest that declares a Parquet data file's format as ORC fails
    with NOT_IMPLEMENTED before touching the file (pure metadata-level
    check, always runs)."""
    with Given("a Parquet table with a deletion vector"):
        table = common.table_with_deletion_vectors(rows=50)

    with When("the data manifest declares the file's format as ORC"):

        def orc_format(entry):
            entry["data_file"]["file_format"] = "ORC"
            return entry

        manifest.mutate_manifest_entries(
            namespace=table.namespace,
            table_name=table.table_name,
            mutator=orc_format,
            content=manifest.MANIFEST_LIST_DATA,
        )

    with Then("the read fails with NOT_IMPLEMENTED before touching the file"):
        common.assert_table_read_fails(
            table=table,
            error_name="NOT_IMPLEMENTED",
            message_fragment=NON_PARQUET_FRAGMENT,
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_NonParquetDataFiles("1.0"))
def non_parquet_data_files(self):
    """A deletion vector attached to a non-Parquet data file fails with
    NOT_IMPLEMENTED naming the feature and the actual format."""
    Scenario(run=real_orc_data_file)
    Scenario(run=manifest_declares_orc)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_CompressedFooter("1.0"))
def lz4_compressed_footer(self):
    """An LZ4-compressed footer payload (single frame with the content size
    declared, flag bit set) reads identically to an uncompressed footer —
    the vector is applied, not silently skipped."""
    table = self.context.table

    with When("the Puffin file is rebuilt with an LZ4-compressed footer"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=POSITIONS),
            declared_cardinality=CARDINALITY,
            puffin_kwargs={"compress_footer": True},
        )
        common.drop_iceberg_metadata_cache()
        common.drop_puffin_cache()

    with Then("the read applies the vector exactly as with an uncompressed footer"):
        ids_in_order = self.context.ids_in_order
        expected = sorted(
            set(ids_in_order) - {ids_in_order[position] for position in POSITIONS}
        )
        common.assert_visible_ids(
            table=table,
            ids=expected,
            settings=common.FRESH_READ_SETTINGS,
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_CompressedFooter("1.0"))
def footer_without_content_size(self):
    """A compressed footer frame that does not declare its content size is
    rejected (the Puffin spec requires the content size to be present)."""
    table = self.context.table

    with When("the footer frame is compressed without a declared content size"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=POSITIONS),
            declared_cardinality=CARDINALITY,
            puffin_kwargs={"compress_footer": True, "store_content_size": False},
        )

    with Then("the read fails naming the missing content size"):
        common.assert_table_read_fails(
            table=table,
            error_name="LZ4_DECODER_FAILED",
            message_fragment="must declare content size",
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_CompressedFooter("1.0"))
def unknown_footer_flags(self):
    """Reserved footer flag bits set are rejected with BAD_ARGUMENTS rather
    than interpreted as some other footer encoding."""
    table = self.context.table

    with When("a reserved footer flag bit is set"):
        manifest.replace_deletion_vector(
            namespace=table.namespace,
            table_name=table.table_name,
            payload=puffin.build_dv_payload(positions=POSITIONS),
            declared_cardinality=CARDINALITY,
            puffin_kwargs={"flags": b"\x02\x00\x00\x00"},
        )

    with Then("the read fails with BAD_ARGUMENTS"):
        common.assert_table_read_fails(
            table=table,
            error_name="BAD_ARGUMENTS",
            message_fragment="Unknown Puffin footer flags",
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_CompressedFooter("1.0"))
def compressed_footer(self):
    """A spec-legal LZ4-compressed Puffin footer reads identically to an
    uncompressed one, and uninterpretable footer flag constructs fail
    closed."""
    with Given("a table with a deletion vector over a single data file"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition="id % 10 = 0"
        )
        common.assert_data_file_count(table=table, count=1)
        self.context.table = table
        self.context.ids_in_order = common.parquet_column_values(table=table)

    Scenario(run=lz4_compressed_footer)
    Scenario(run=footer_without_content_size)
    Scenario(run=unknown_footer_flags)


@TestFeature
@Name("error handling")
def feature(self, minio_root_user, minio_root_password):
    """Error handling for corrupt Puffin files and inconsistent metadata."""
    Suite(run=malformed_blob)
    Suite(run=blob_metadata)
    Suite(run=blob_bounds)
    Suite(run=manifest_consistency)
    Suite(run=resource_limits)
    Suite(run=non_parquet_data_files)
    Suite(run=compressed_footer)
