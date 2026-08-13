"""Byte-level corruption of the two file kinds a deletion vector depends
on: the Puffin file holding the blob, and the Avro delete manifest /
manifest list pointing at it.

Unlike error_handling.py, which injects one structured field-level defect
into an otherwise valid file, these scenarios damage raw bytes —
truncations, corrupted magic, hostile footer sizes, garbage, bit flips —
and assert the fail-closed contract: an explicit exception (or, for flips
landing in non-load-bearing bytes, the exact correct rows), a server that
stays responsive, and never a silent wrong row set. Each scenario restores
the original bytes on cleanup, so every case starts from a healthy chain."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects
import iceberg.tests.deletion_vectors.steps.manifest as manifest
import iceberg.tests.deletion_vectors.steps.corruption as corruption

ROWS = 100
DELETED = list(range(0, ROWS, 10))
FLIP_COUNT = 12


@TestStep(Given)
def fixture_table(self):
    """One shared table with a deletion vector, plus the object keys and
    pristine bytes of its Puffin file, delete manifest, and manifest
    list."""
    table = common.table_with_deletion_vectors(
        rows=ROWS, delete_condition="id % 10 = 0"
    )

    puffin_keys = s3_objects.find_puffin_keys(table.namespace, table.table_name)
    assert len(puffin_keys) == 1, error(
        f"expected one Puffin file, found {puffin_keys}"
    )
    dv_entries = manifest.find_dv_entries(table.namespace, table.table_name)
    assert len(dv_entries) == 1, error(
        f"expected one deletion-vector entry, found {len(dv_entries)}"
    )

    ctx = self.context
    ctx.table = table
    ctx.expected = common.expected_ids(ROWS, DELETED)
    ctx.keys = {
        "puffin": puffin_keys[0],
        "delete manifest": dv_entries[0]["manifest_key"],
        "manifest list": s3_objects.manifest_list_key(
            table.namespace, table.table_name
        ),
    }
    ctx.originals = {
        name: s3_objects.get_object_bytes(key) for name, key in ctx.keys.items()
    }

    with And("the healthy baseline returns the expected rows"):
        common.assert_visible_ids(table=table, ids=ctx.expected)

    return table


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_CorruptPuffinFile("1.0"))
def puffin_defect(self, name, data):
    """One structurally damaged Puffin file fails the query with an
    explicit exception and no crash."""
    ctx = self.context

    with Given(f"the Puffin file damaged: {name}"):
        corruption.corrupted_object(
            key=ctx.keys["puffin"], data=data, original=ctx.originals["puffin"]
        )

    with Then("the read fails explicitly and the server stays responsive"):
        common.assert_fails_without_crash(table=ctx.table)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_CorruptPuffinFile("1.0"))
def puffin_byte_flip(self, name, offset):
    """One flipped byte in the Puffin file either fails explicitly or
    leaves the result byte-for-byte correct — never a wrong row set."""
    ctx = self.context
    note(f"flipping byte at offset {offset} of {len(ctx.originals['puffin'])}")

    with Given(f"the Puffin file with {name}"):
        corruption.corrupted_object(
            key=ctx.keys["puffin"],
            data=corruption.flip_byte(offset)(ctx.originals["puffin"]),
            original=ctx.originals["puffin"],
        )

    with Then("the result is exactly correct or an explicit error"):
        common.assert_correct_or_explicit_error(
            table=ctx.table, expected_ids=ctx.expected
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_CorruptPuffinFile("1.0"))
def corrupt_puffin_file(self):
    """Byte-level damage to the Puffin file fails closed without a crash;
    single-byte flips can never produce a wrong row set."""
    with Given("a table with a deletion vector and its pristine file bytes"):
        fixture_table()

    original = self.context.originals["puffin"]

    for name, data in corruption.puffin_structural_cases(original).items():
        Scenario(test=puffin_defect, name=name)(name=name, data=data)

    for index, offset in enumerate(corruption.flip_offsets(len(original), FLIP_COUNT)):
        name = f"byte flip {index}"
        Scenario(test=puffin_byte_flip, name=name)(name=name, offset=offset)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_CorruptManifest("1.0"))
def avro_defect(self, target, name, data):
    """One structurally damaged Avro metadata object fails the query with
    an explicit exception and no crash — a silently dropped delete entry
    would resurrect deleted rows."""
    ctx = self.context

    with Given(f"the {target} damaged: {name}"):
        corruption.corrupted_object(
            key=ctx.keys[target], data=data, original=ctx.originals[target]
        )

    with Then("the read fails explicitly and the server stays responsive"):
        common.assert_fails_without_crash(table=ctx.table)


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_CorruptManifest("1.0"))
def corrupt_delete_manifest(self):
    """Byte-level damage to the Avro delete manifest fails closed without
    a crash."""
    with Given("a table with a deletion vector and its pristine file bytes"):
        fixture_table()

    cases = corruption.avro_structural_cases(self.context.originals["delete manifest"])
    for name, data in cases.items():
        Scenario(test=avro_defect, name=name)(
            target="delete manifest", name=name, data=data
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_ErrorHandling_CorruptManifest("1.0"))
def corrupt_manifest_list(self):
    """Byte-level damage to the Avro manifest list fails closed without a
    crash."""
    with Given("a table with a deletion vector and its pristine file bytes"):
        fixture_table()

    cases = corruption.avro_structural_cases(self.context.originals["manifest list"])
    for name, data in cases.items():
        Scenario(test=avro_defect, name=name)(
            target="manifest list", name=name, data=data
        )


@TestFeature
@Name("file corruption")
def feature(self, minio_root_user, minio_root_password):
    """Byte-level corruption of Puffin files and Avro delete metadata."""
    Suite(run=corrupt_puffin_file)
    Suite(run=corrupt_delete_manifest)
    Suite(run=corrupt_manifest_list)
