"""CAS ProfileEvents / system.events helpers for relink proofs."""

from testflows.core import *
from testflows.asserts import error

BLOB_PUT = "CASBlobPut"


def cas_events_snapshot(node):
    """Snapshot cumulative CAS* counters from system.events on one node."""
    result = node.query(
        "SELECT event, value FROM system.events "
        "WHERE event LIKE 'CAS%' FORMAT TabSeparated"
    )
    out = {}
    for line in result.output.splitlines():
        if "\t" not in line:
            continue
        name, value = line.split("\t", 1)
        try:
            out[name] = int(value)
        except ValueError:
            pass
    return out


def cas_events_delta(before, after):
    """Positive deltas of CAS counters between two snapshots."""
    delta = {}
    for name, value in after.items():
        change = value - before.get(name, 0)
        if change > 0:
            delta[name] = change
    return delta


def blob_body_puts(delta):
    """Large blob body uploads in a CAS events delta."""
    return int(delta.get(BLOB_PUT, 0))


def blob_puts_avoided_or_deduped(delta):
    """Dedup / body-put-avoided signal that a fetch reused existing blobs."""
    return int(delta.get("CASBlobPutDeduplicated", 0)) + int(
        delta.get("CASBlobBodyPutAvoided", 0)
    )


@TestStep(Then)
@Name("assert the writer uploaded blob bodies")
def assert_blob_bodies_were_uploaded(self, delta):
    """Assert a writer's delta shows real blob uploads.

    This is the control for the relink proof: if the build never reports
    ``CASBlobPut`` then a flat counter on the reader proves nothing, so the
    absence of uploads on the writer is a harness failure, not a pass.
    """
    puts = blob_body_puts(delta)
    note(f"writer {BLOB_PUT}={puts}")
    assert puts > 0, error(
        f"expected blob bodies to be published but {BLOB_PUT}={puts}. Either the "
        f"payload was too small to create blob bodies or this build does not "
        f"report {BLOB_PUT}, in which case counter-based proofs are not "
        f"meaningful here. Observed CAS counters: {sorted(delta)}"
    )
    return puts


@TestStep(Then)
@Name("assert the reader did not re-upload blob bodies")
def assert_no_blob_reupload_on_fetch(self, delta, writer_puts, tolerance=0.25):
    """Assert a reader's delta looks like relink/dedup rather than re-upload.

    The bound is relative to what the writer actually uploaded: a byte fetch
    that re-published the same content would approach ``writer_puts``.
    """
    puts = blob_body_puts(delta)
    avoided = blob_puts_avoided_or_deduped(delta)
    limit = max(1, int(writer_puts * tolerance))
    note(f"reader {BLOB_PUT}={puts} (limit {limit}), avoided/deduped={avoided}")
    assert puts <= limit, error(
        f"reader re-uploaded blob bodies during fetch: {BLOB_PUT}={puts} "
        f"against a writer that uploaded {writer_puts}; fetch should relink "
        f"shared content instead of copying it. Reader delta: {delta}"
    )
