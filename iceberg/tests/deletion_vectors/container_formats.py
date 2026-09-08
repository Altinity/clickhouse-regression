"""The container seam: deletion vectors stored in a Databricks/Delta ``.bin``
rather than a Puffin file.

Everything below the seam — the roaring bitmap, the CRC, the position
arithmetic — is shared with the Puffin path and is covered by re-running the
container-agnostic suites under a ``.bin`` (see ``delta_feature.py``). What is
*only* testable here is the seam itself: which container the reader decides an
object is, from what evidence, and what it does when the answer is neither.

The reader identifies the container from the object's bytes, because nothing in
the metadata distinguishes them — Databricks writes ``file_format = PUFFIN``
for a ``.bin``. So these scenarios vary the bytes and the manifest's
description of them independently, which no writer would ever do and no
container-agnostic scenario can reach.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects
import iceberg.tests.deletion_vectors.steps.puffin as puffin
import iceberg.tests.deletion_vectors.steps.manifest as manifest
import iceberg.tests.deletion_vectors.steps.databricks_fixture as databricks_fixture

ROWS = 100
DELETE_CONDITION = "id % 10 = 0"
POSITIONS = list(range(0, ROWS, 10))
DELETED_IDS = list(range(0, ROWS, 10))
# distinct from the fixture's every-10th-row delete, so a no-op install
# cannot satisfy assert_visible_positions
CRAFTED_POSITIONS = [1, 3, 7]

UNKNOWN_CONTAINER_FRAGMENT = "is neither a Puffin container"

# the content_offset a reader would declare if it believed the blob began at
# the deletion-vector magic rather than at the four-byte length prefix
MISREAD_CONTENT_OFFSET = 5


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def delta_container_nests_iceberg_blob(self):
    """A Delta container is one version byte followed by the byte-identical
    Iceberg blob, so ``content_offset`` is 1 and ``content_size_in_bytes`` is
    everything after it.

    Pure bytes, no server: this pins the layout our whole Delta harness
    assumes, and it is the cheapest place for a misreading of the convention
    to surface. The arithmetic matters because the reader validates
    ``content_size_in_bytes == combined_length + 8``, which only holds when
    the offset addresses the length prefix rather than the magic."""
    with Given("a deletion-vector blob and a Delta container around it"):
        blob = puffin.build_dv_payload(positions=POSITIONS)
        container, ranges = puffin.build_delta_bin(positions=POSITIONS)

    with Then("the container nests the blob unchanged after one version byte"):
        assert container[:1] == bytes([puffin.DELTA_VERSION_BYTE]), error(
            f"unexpected leading byte {container[:1]!r}"
        )
        assert container[1:] == blob, error(
            "the container altered the blob it wraps: "
            f"{len(container) - 1} bytes vs {len(blob)}"
        )

    with And("the blob region is (1, size - 1), the Databricks convention"):
        assert ranges == [(1, len(blob))], error(f"unexpected blob ranges {ranges}")
        assert puffin.delta_bin_blob_range(container) == (1, len(container) - 1), error(
            "delta_bin_blob_range disagrees with the built layout"
        )

    with And("the declared size equals the envelope's combined length plus 8"):
        combined_length = int.from_bytes(container[1:5], "big")
        assert len(blob) == combined_length + 8, error(
            f"envelope predicate broken: size {len(blob)} != "
            f"combined_length {combined_length} + 8"
        )

    with And("the container does not look like a Puffin file"):
        assert puffin.container_of(container) == manifest.DELTA_BIN_CONTAINER, error(
            f"container_of misidentified the container: {container[:4]!r}"
        )


# the deletion-vector blobs ClickHouse's own unit tests are built on
# (gtest_delta_bin_deletion_vector.cpp): positions {2, 5} and {7, 9}, each
# with cardinality 2. A third independent anchor besides Spark's writer and
# the Databricks fixture — and the only one that states what the
# implementation itself considers a well-formed blob.
UPSTREAM_BLOB_TWO_FIVE = bytes(
    [
        0x00,
        0x00,
        0x00,
        0x24,
        0xD1,
        0xD3,
        0x39,
        0x64,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x3A,
        0x30,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x01,
        0x00,
        0x10,
        0x00,
        0x00,
        0x00,
        0x02,
        0x00,
        0x05,
        0x00,
        0x2C,
        0xDB,
        0x9F,
        0xC1,
    ]
)
UPSTREAM_BLOB_SEVEN_NINE = bytes(
    [
        0x00,
        0x00,
        0x00,
        0x24,
        0xD1,
        0xD3,
        0x39,
        0x64,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x3A,
        0x30,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x01,
        0x00,
        0x10,
        0x00,
        0x00,
        0x00,
        0x07,
        0x00,
        0x09,
        0x00,
        0xB7,
        0xB0,
        0x20,
        0xFF,
    ]
)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def matches_upstream_container_fixtures(self):
    """Our container is byte-identical to the ones ClickHouse's own unit
    tests are built on.

    Nothing here talks to a server: it compares our builder against the
    fixtures in ``gtest_delta_bin_deletion_vector.cpp``, including the
    two-blob container whose second slice starts at ``1 + len(first blob)``.
    A roaring bitmap has several valid encodings, so agreement is not
    guaranteed a priori — which is exactly why pinning it is worth doing.
    When this fails, our serialization drifted from what the implementation
    is tested against, and every crafted Delta scenario is suspect."""
    with When("the harness builds blobs for the same two vectors"):
        first = puffin.build_dv_payload(positions=[2, 5])
        second = puffin.build_dv_payload(positions=[7, 9])

    with Then("each blob matches the upstream fixture byte for byte"):
        assert first == UPSTREAM_BLOB_TWO_FIVE, error(
            f"blob for {{2, 5}} drifted from the upstream fixture:\n"
            f"  ours     {first.hex()}\n  upstream {UPSTREAM_BLOB_TWO_FIVE.hex()}"
        )
        assert second == UPSTREAM_BLOB_SEVEN_NINE, error(
            f"blob for {{7, 9}} drifted from the upstream fixture:\n"
            f"  ours     {second.hex()}\n  upstream {UPSTREAM_BLOB_SEVEN_NINE.hex()}"
        )

    with And("a single-blob container is the version byte plus that blob"):
        container, ranges = puffin.build_delta_bin(positions=[2, 5])
        assert container == bytes([1]) + UPSTREAM_BLOB_TWO_FIVE, error(
            "single-blob container drifted from version byte + blob"
        )
        assert ranges == [(1, len(UPSTREAM_BLOB_TWO_FIVE))], error(
            f"unexpected single-blob ranges {ranges}"
        )

    with And("a two-blob container concatenates them after one version byte"):
        shared, shared_ranges = puffin.build_delta_bin(payloads=[first, second])
        assert shared == bytes([1]) + first + second, error(
            "two-blob container is not the blobs concatenated after the version byte"
        )
        assert shared_ranges == [(1, len(first)), (1 + len(first), len(second))], error(
            f"unexpected slice ranges for a shared container: {shared_ranges}"
        )

    with And("our decoder reads the upstream bytes back to the same positions"):
        assert puffin.dv_positions_of_payload(UPSTREAM_BLOB_TWO_FIVE) == [2, 5], error(
            "decoder did not recover positions {2, 5} from the upstream fixture"
        )
        assert puffin.dv_positions_of_payload(UPSTREAM_BLOB_SEVEN_NINE) == [7, 9], error(
            "decoder did not recover positions {7, 9} from the upstream fixture"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def golden_databricks_table(self):
    """Read the customer's Databricks UniForm table — the one Delta container
    in this suite that the harness did not write.

    Every other scenario here builds its container from our own writer, so a
    shared misreading of the format between that writer and ClickHouse's
    reader would satisfy both and go unnoticed. This table removes that
    freedom: the ``.bin``, the Parquet data file and the Avro manifests are the
    customer's own bytes and only path strings were rewritten. It is also the
    case upstream shipped without ever running — its integration test was
    never selected in CI — so failures here are the ones nothing else catches.

    It carries coverage no crafted vector does: Databricks run-length-encoded
    the roaring containers, an encoding the harness' own writer never emits, so
    this is the suite's only exercise of that decode path."""
    with Given("the Databricks UniForm table installed on the warehouse"):
        table = databricks_fixture.databricks_uniform_table()

    with Then(f"{databricks_fixture.LIVE_ROWS} of the rows are visible"):
        rows = common.count_rows(table=table, settings=common.FRESH_READ_SETTINGS)
        assert rows == databricks_fixture.LIVE_ROWS, error(
            f"read {rows} rows, expected {databricks_fixture.LIVE_ROWS} "
            f"({databricks_fixture.TOTAL_ROWS} written, "
            f"{databricks_fixture.DELETED_ROWS} deleted)"
        )

    with And("the surviving ids are exactly the ones the DELETE spared"):
        result = common.read_result(
            table=table,
            columns="toInt64(Id)",
            order_by="toInt64(Id)",
            settings=common.FRESH_READ_SETTINGS,
        )
        ids = [int(line) for line in result.output.splitlines() if line.strip()]
        expected = list(
            range(databricks_fixture.FIRST_LIVE_ID, databricks_fixture.TOTAL_ROWS + 1)
        )
        assert ids == expected, error(
            f"expected ids {expected[0]}..{expected[-1]} "
            f"({len(expected)} rows), got {len(ids)} rows"
            + (f" spanning {ids[0]}..{ids[-1]}" if ids else "")
        )

    with And("a trivial count is answered from the same vector"):
        # the count path reads record_count off the manifest and subtracts the
        # vector's cardinality, so it can disagree with the row-by-row read
        trivial = common.count_rows(
            table=table,
            settings=common.FRESH_READ_SETTINGS
            + [("optimize_trivial_count_query", "1")],
        )
        assert trivial == databricks_fixture.LIVE_ROWS, error(
            f"trivial count returned {trivial}, "
            f"expected {databricks_fixture.LIVE_ROWS}"
        )

    with And("the vector was applied rather than skipped"):
        # a table read as if it had no deletes would still return rows, so the
        # deleted range has to be checked explicitly
        deleted = common.read_result(
            table=table,
            columns=f"countIf(toInt64(Id) < {databricks_fixture.FIRST_LIVE_ID})",
            settings=common.FRESH_READ_SETTINGS,
        )
        assert deleted.output.strip() == "0", error(
            f"{deleted.output.strip()} deleted row(s) are still visible"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def crafted_delta_bin_conformance(self):
    """The Delta container our harness builds wraps exactly the bytes a
    compliant writer produced.

    The Puffin counterpart of this scenario (``sanity.crafted_writer_conformance``)
    guards the crafted *footer* against Spark's. This one guards the crafted
    *container*: it takes the blob Spark actually serialized, wraps it, and
    checks that the wrapper adds nothing but the version byte and that the
    offsets we would declare describe it correctly. Without this, our two
    synthetic routes are only self-consistent — they could share a misreading
    of the layout and both pass."""
    with Given("a Spark-written Puffin file and the blob it embeds"):
        # explicitly Puffin even inside the Delta feature: the whole point is
        # to compare our container against a compliant writer's bytes
        common.use_container(container=manifest.PUFFIN_CONTAINER)
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )
        dv_entries = manifest.find_dv_entries(table.namespace, table.table_name)
        data_file = dv_entries[0]["entry"]["data_file"]
        writer_bytes = s3_objects.get_object_bytes(data_file["file_path"])
        assert puffin.container_of(writer_bytes) == manifest.PUFFIN_CONTAINER, error(
            f"expected a writer-produced Puffin file, got {writer_bytes[:4]!r}"
        )

    with When("the writer's blob is sliced out by its declared location"):
        writer_blob = writer_bytes[
            data_file["content_offset"] : data_file["content_offset"]
            + data_file["content_size_in_bytes"]
        ]

    with And("the harness wraps that exact blob in a Delta container"):
        container, ranges = puffin.build_delta_bin(payload=writer_blob)

    with Then("the wrapper adds only the version byte"):
        assert len(container) == len(writer_blob) + 1, error(
            f"wrapper added {len(container) - len(writer_blob)} bytes, expected 1"
        )
        assert container[1:] == writer_blob, error("wrapper altered the writer's blob")

    with And("the declared location satisfies the reader's envelope predicate"):
        content_offset, content_size = ranges[0]
        combined_length = int.from_bytes(
            container[content_offset : content_offset + 4], "big"
        )
        assert container[content_offset + 4 : content_offset + 8] == puffin.DV_MAGIC, (
            error("no deletion-vector magic where the reader will look")
        )
        assert content_size == combined_length + 8, error(
            f"declared size {content_size} != combined_length {combined_length} + 8"
        )
        assert content_offset + content_size == len(container), error(
            "the declared region does not cover the rest of the container"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def delta_bin_replaces_writer_vector(self):
    """A Delta ``.bin`` written over the vector object reads correctly — the
    customer case, and the positive counterpart of
    ``delta_bin_offset_past_envelope``, which installs the same bytes with a
    misdeclared offset."""
    with Given("a table with a writer-produced deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )
        ids_in_order = common.parquet_column_values(table=table)

    with When("the vector object is replaced with a Delta .bin"):
        common.install_delta_bin(table=table, positions=POSITIONS)

    with Then("the object really is a Delta container now"):
        common.assert_container(table=table, container=manifest.DELTA_BIN_CONTAINER)

    with And("the vector applies exactly as it would from a Puffin file"):
        common.assert_visible_positions(
            table=table, ids_in_order=ids_in_order, deleted_positions=POSITIONS
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def converted_writer_vectors_read_identically(self):
    """Converting a writer-produced Puffin to a ``.bin`` in place changes the
    rows not at all.

    This is the scenario that validates the conversion the whole Delta feature
    depends on: the same table is read before and after, so the blob bytes are
    provably identical and only the wrapper differs. If this passes and a
    reused suite still fails under Delta, the fault is the container, not our
    conversion."""
    with Given("a table with a writer-produced Puffin deletion vector"):
        # the conversion is the subject, so the fixture must not have been
        # converted already by the Delta feature's chokepoint
        common.use_container(container=manifest.PUFFIN_CONTAINER)
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )
        expected = common.expected_ids(ROWS, DELETED_IDS)

    with And("the rows it exposes through the writer's own container"):
        before = common.select_ids(table=table, settings=common.FRESH_READ_SETTINGS)
        assert before == sorted(expected), error(
            f"fixture is wrong before conversion: {len(before)} rows"
        )

    with When("every vector is rewritten as a Delta .bin in place"):
        converted = manifest.convert_dvs_to_delta_bin(
            namespace=table.namespace, table_name=table.table_name
        )
        note(f"converted {converted} container(s)")

    with Then("the objects are Delta containers"):
        common.assert_container(table=table, container=manifest.DELTA_BIN_CONTAINER)

    with And("the same rows are visible"):
        common.drop_iceberg_metadata_cache()
        common.drop_puffin_cache()
        common.assert_visible_ids(
            table=table, ids=expected, settings=common.FRESH_READ_SETTINGS
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def bare_envelope_no_version_byte(self):
    """A container with no version byte at all — the blob alone, at
    ``content_offset = 0`` — is read.

    Accepted by the current implementation. Pinned so that tightening the
    accepted set later shows up as a deliberate change rather than a
    regression in someone's Delta table. The installed positions are not
    the fixture's, and the stored object is checked, so a no-op install
    cannot pass."""
    with Given("a table with a writer-produced deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )
        ids_in_order = common.parquet_column_values(table=table)

    with When("the vector object is replaced with a bare envelope at offset 0"):
        container = common.install_delta_bin(
            table=table,
            positions=CRAFTED_POSITIONS,
            version_byte=None,
            declared_cardinality=len(CRAFTED_POSITIONS),
        )

    with Then("the stored object is the bare envelope, declared at offset 0"):
        assert container[:4] != puffin.PUFFIN_MAGIC, error(
            "a bare envelope must not begin with the Puffin magic"
        )
        common.assert_stored_deletion_vector(
            table=table, expected_bytes=container, content_offset=0
        )

    with And("the crafted vector applies"):
        common.assert_visible_positions(
            table=table,
            ids_in_order=ids_in_order,
            deleted_positions=CRAFTED_POSITIONS,
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def unexpected_version_byte_accepted(self):
    """An unexpected Delta version byte is read, not rejected, as long as
    a valid envelope sits at the declared offset."""
    with Given("a table with a writer-produced deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )
        ids_in_order = common.parquet_column_values(table=table)

    with When("the container is prefixed with an unexpected version byte"):
        container = common.install_delta_bin(
            table=table,
            positions=CRAFTED_POSITIONS,
            version_byte=0x7F,
            declared_cardinality=len(CRAFTED_POSITIONS),
        )

    with Then("the stored object carries that version byte at offset 0"):
        common.assert_stored_deletion_vector(
            table=table,
            expected_bytes=container,
            expected_prefix=b"\x7f",
            content_offset=1,
        )

    with And("the crafted vector applies"):
        common.assert_visible_positions(
            table=table,
            ids_in_order=ids_in_order,
            deleted_positions=CRAFTED_POSITIONS,
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def unknown_four_byte_wrapper_accepted(self):
    """A four-byte wrapper that is not Puffin magic is read, not rejected,
    as long as a valid envelope sits at the declared offset."""
    with Given("a table with a writer-produced deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )
        ids_in_order = common.parquet_column_values(table=table)

    with When("the container is prefixed with four bytes that are not Puffin magic"):
        container = common.install_delta_bin(
            table=table,
            positions=CRAFTED_POSITIONS,
            prefix=b"DVX\x00",
            declared_cardinality=len(CRAFTED_POSITIONS),
        )

    with Then("the stored object starts with that wrapper"):
        common.assert_stored_deletion_vector(
            table=table,
            expected_bytes=container,
            expected_prefix=b"DVX\x00",
            content_offset=4,
        )

    with And("the crafted vector applies"):
        common.assert_visible_positions(
            table=table,
            ids_in_order=ids_in_order,
            deleted_positions=CRAFTED_POSITIONS,
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def retargeted_bin_path(self):
    """The delete manifest points at a sibling ``deletion_vector_*.bin``
    rather than at the writer's object — the file layout Databricks actually
    leaves behind — and the vector applies."""
    with Given("a table with a writer-produced deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )
        ids_in_order = common.parquet_column_values(table=table)

    with When("the entry is retargeted at a sibling deletion_vector_*.bin"):
        common.install_delta_bin(table=table, positions=POSITIONS, retarget_path=True)

    with Then("the vector applies from the .bin path"):
        common.assert_visible_positions(
            table=table, ids_in_order=ids_in_order, deleted_positions=POSITIONS
        )

    with And("the entry really points at a .bin object"):
        containers = common.assert_container(
            table=table, container=manifest.DELTA_BIN_CONTAINER
        )
        assert all(path.endswith(".bin") for path in containers), error(
            f"expected the entry to reference a .bin object, got {list(containers)}"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def declared_format_mismatch(self):
    """An entry whose declared ``file_format`` disagrees with the object is
    still recognized as a deletion vector.

    The manifest's format field is not evidence about the container —
    Databricks says ``PUFFIN`` for a ``.bin`` — so the reader classifies an
    entry as a deletion vector from the presence of ``content_offset`` and
    ``content_size_in_bytes`` alone. This exercises that end to end, where
    upstream pins it only as a unit test."""
    with Given("a table with a writer-produced deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )
        ids_in_order = common.parquet_column_values(table=table)

    with When("the vector is installed as a .bin declaring file_format PARQUET"):
        container = common.install_delta_bin(
            table=table,
            positions=CRAFTED_POSITIONS,
            declared_cardinality=len(CRAFTED_POSITIONS),
        )

        def relabel_format(entry):
            if manifest.is_dv_entry(entry):
                entry["data_file"]["file_format"] = "PARQUET"
            return entry

        manifest.mutate_manifest_entries(
            namespace=table.namespace,
            table_name=table.table_name,
            mutator=relabel_format,
            content=manifest.MANIFEST_LIST_DELETES,
        )
        common.drop_iceberg_metadata_cache()
        common.drop_puffin_cache()

    with Then("the stored object is the crafted .bin, still declared PARQUET"):
        _, data_file = common.assert_stored_deletion_vector(
            table=table, expected_bytes=container
        )
        assert data_file["file_format"] == "PARQUET", error(
            f"entry declares file_format {data_file['file_format']}, expected PARQUET"
        )

    with And("the crafted vector applies"):
        common.assert_visible_positions(
            table=table,
            ids_in_order=ids_in_order,
            deleted_positions=CRAFTED_POSITIONS,
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer_FailClosed("1.0"))
def envelope_length_mismatch(self):
    """A declared ``content_size_in_bytes`` that disagrees with the
    envelope's own combined length fails closed.

    The offset is right and the bytes are well-formed; only the declared size
    is wrong, so the reader's ``size == combined_length + 8`` check is the one
    thing rejecting it. On the Puffin path this defect names itself
    (``does not match combined length``); in a Delta container it fails
    container detection instead, which is the coarser error the seam can give
    and worth pinning as such."""
    with Given("a table with a writer-produced deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )

    with When("the .bin declares a size one byte short of the envelope"):
        true_size = len(puffin.build_dv_payload(positions=POSITIONS))
        common.install_delta_bin(
            table=table, positions=POSITIONS, content_size=true_size - 1
        )

    with Then("the read fails closed rather than trusting either number"):
        common.assert_table_read_fails(
            table=table,
            error_name="BAD_ARGUMENTS",
            message_fragment=UNKNOWN_CONTAINER_FRAGMENT,
        )

    with And("the server is still responsive"):
        common.assert_server_alive()


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer_FailClosed("1.0"))
def delta_bin_offset_past_envelope(self):
    """A well-formed Delta ``.bin`` whose manifest declares an offset past
    the start of the blob fails closed.

    ``content_offset = 5`` points at the deletion-vector magic instead of the
    four-byte length prefix that precedes it — the plausible misreading of
    the layout — so no envelope is found and the object is rejected as
    neither container."""
    with Given("a table with a writer-produced deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )

    with When("a Delta .bin is installed with content_offset past the envelope"):
        # the declared region has to stay inside the object: an offset plus
        # length running past the end is rejected by the bounds check *before*
        # container detection, which would prove something else entirely. A
        # reader that believed the blob began at the magic would declare
        # exactly this pair — offset 5, and the rest of the container.
        payload = puffin.build_dv_payload(positions=POSITIONS)
        container, _ = puffin.build_delta_bin(payload=payload)
        common.install_delta_bin(
            table=table,
            payload=payload,
            content_offset=MISREAD_CONTENT_OFFSET,
            content_size=len(container) - MISREAD_CONTENT_OFFSET,
        )

    with Then("the stored object is the .bin we installed"):
        common.assert_stored_deletion_vector(
            table=table,
            expected_bytes=container,
            content_offset=MISREAD_CONTENT_OFFSET,
        )

    with And("the read fails closed"):
        result = common.assert_table_read_fails(
            table=table,
            error_name="BAD_ARGUMENTS",
            message_fragment=UNKNOWN_CONTAINER_FRAGMENT,
        )

    with And("the error names the offset it probed, proving which one was used"):
        assert f"envelope at offset {MISREAD_CONTENT_OFFSET}" in result.output, error(
            f"error did not name the declared offset:\n{result.output[:2000]}"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer_FailClosed("1.0"))
def delta_bin_offset_past_envelope_retargeted_path(self):
    """The same misdeclared offset on a sibling ``deletion_vector_*.bin``
    the manifest ``file_path`` points at, rather than on the writer's own
    object — the file layout Databricks leaves after a ``DELETE``."""
    with Given("a table with a writer-produced deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )

    with When("the DV entry is retargeted at a sibling .bin with a bad offset"):
        payload = puffin.build_dv_payload(positions=POSITIONS)
        container, _ = puffin.build_delta_bin(payload=payload)
        common.install_delta_bin(
            table=table,
            payload=payload,
            content_offset=MISREAD_CONTENT_OFFSET,
            content_size=len(container) - MISREAD_CONTENT_OFFSET,
            retarget_path=True,
        )

    with Then("the entry points at the sibling .bin we installed"):
        _, data_file = common.assert_stored_deletion_vector(
            table=table,
            expected_bytes=container,
            content_offset=MISREAD_CONTENT_OFFSET,
        )
        assert data_file["file_path"].endswith(".bin"), error(
            f"expected a .bin path, got {data_file['file_path']}"
        )

    with And("the read fails closed"):
        result = common.assert_table_read_fails(
            table=table,
            error_name="BAD_ARGUMENTS",
            message_fragment=UNKNOWN_CONTAINER_FRAGMENT,
        )

    with And("the error names the offset it probed"):
        assert f"envelope at offset {MISREAD_CONTENT_OFFSET}" in result.output, error(
            f"error did not name the declared offset:\n{result.output[:2000]}"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer_FailClosed("1.0"))
def object_too_small_for_either_container(self):
    """An object that is large enough to pass the blob-size floor and the
    bounds check, but whose bytes are not a Puffin header and not an
    envelope, fails closed at container detection.

    A three-byte object cannot reach this message: ``content_size < 12``
    is rejected earlier as ``Deletion vector blob is too small``. The
    smallest seam-reachable case is a version byte plus twelve zero bytes,
    declared as ``(1, 12)`` — in bounds, past the floor, and not an
    envelope."""
    with Given("a table with a writer-produced deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition=DELETE_CONDITION
        )

    with When("the vector object is replaced with twelve zero bytes after 0x01"):
        # 13 bytes: not PFA1, content_size 12 passes the floor, 1+12 fits,
        # envelope probe sees zeros and rejects at the seam
        tiny = common.install_delta_bin(
            table=table,
            payload=b"\x00" * 12,
            version_byte=puffin.DELTA_VERSION_BYTE,
        )

    with Then("the stored object is those 13 bytes"):
        common.assert_stored_deletion_vector(
            table=table, expected_bytes=tiny, content_offset=1
        )

    with And("the read fails closed at container detection"):
        common.assert_table_read_fails(
            table=table,
            error_name="BAD_ARGUMENTS",
            message_fragment=UNKNOWN_CONTAINER_FRAGMENT,
        )

    with And("the server is still responsive"):
        common.assert_server_alive()


@TestFeature
@Name("container formats")
@Requirements(RQ_Iceberg_DeletionVectors_DeltaContainer("1.0"))
def feature(self, minio_root_user, minio_root_password):
    """Deletion vectors in a Databricks/Delta ``.bin`` container."""
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password

    Scenario(run=delta_container_nests_iceberg_blob)
    Scenario(run=matches_upstream_container_fixtures)
    Scenario(run=golden_databricks_table)
    Scenario(run=crafted_delta_bin_conformance)
    Scenario(run=delta_bin_replaces_writer_vector)
    Scenario(run=converted_writer_vectors_read_identically)
    Scenario(run=bare_envelope_no_version_byte)
    Scenario(run=unexpected_version_byte_accepted)
    Scenario(run=unknown_four_byte_wrapper_accepted)
    Scenario(run=retargeted_bin_path)
    Scenario(run=declared_format_mismatch)
    Scenario(run=envelope_length_mismatch)
    Scenario(run=delta_bin_offset_past_envelope)
    Scenario(run=delta_bin_offset_past_envelope_retargeted_path)
    Scenario(run=object_too_small_for_either_container)
