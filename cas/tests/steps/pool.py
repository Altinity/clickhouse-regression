"""Direct inspection of the objects a CAS pool holds in object storage."""

import re
import time

from testflows.asserts import error
from testflows.core import *

BLOB_PREFIX = "blobs/"
MANIFEST_PREFIX = "cas/manifests/"
NS_PREFIX = "cas/ns/"

BLOB_KEY = re.compile(r"blobs/ch128/([0-9a-f]{2})/([0-9a-f]{32})$")
BLOB_META_KEY = re.compile(r"blobs/ch128/([0-9a-f]{2})/([0-9a-f]{32})\.meta$")
MANIFEST_KEY = re.compile(
    r"cas/manifests/.+/[0-9a-f]{16}-[0-9a-f]{16}/\d{6}\.zst$"
)


@TestStep(Then)
@Name("snapshot the objects stored in a CAS pool")
def pool_snapshot(self, pool_prefix, cluster=None):
    """Return every object in the pool as ``{key: size}``.

    Keys are relative to the pool prefix, so they read as ``blobs/...``,
    ``cas/manifests/...`` and ``cas/ns/...``. Sizes are part of the snapshot
    because a pool can change without gaining or losing a key — appending to a
    ref stream rewrites an object in place.
    """
    if cluster is None:
        cluster = self.context.cluster

    listing = cluster.command(
        "mc",
        f"mc --no-color find minio/warehouse/{pool_prefix} --print '{{}}\t{{size}}'",
    )

    # The mc container leaks terminal colour-query responses into stdout.
    output = re.sub(
        r"\x1b\](?:10|11|12);rgb:[0-9a-fA-F/]+(?:\x07|\x1b\\)", "", listing.output
    )
    output = re.sub(r"\x1b\[\d+;\d+R", "", output)

    pool_path = f"minio/warehouse/{pool_prefix}/"
    snapshot = {}

    for line in output.splitlines():
        if pool_path not in line or "\t" not in line:
            continue
        path, _, size = line.strip().rpartition("\t")
        snapshot[path.split(pool_path, 1)[1]] = size.strip()

    return snapshot


@TestStep(Then)
@Name("wait for a CAS pool to stop changing")
def settled_pool_snapshot(self, pool_prefix, attempts=15, delay=2):
    """Poll until two consecutive snapshots agree, and return the last one.

    Replication, merges and background CAS work keep writing after a query has
    returned, so a snapshot taken immediately is not a baseline that anything
    can be compared against.
    """
    previous = pool_snapshot(pool_prefix=pool_prefix)

    for _ in range(attempts):
        time.sleep(delay)
        current = pool_snapshot(pool_prefix=pool_prefix)
        if current == previous:
            return current
        previous = current

    fail(f"pool {pool_prefix} never stopped changing, nothing can be compared")


def pool_difference(before, after):
    """Return what changed between two pool snapshots.

    Reported as ``(added, removed, rewritten)`` lists of keys.
    """
    added = sorted(key for key in after if key not in before)
    removed = sorted(key for key in before if key not in after)
    rewritten = sorted(
        key for key in after if key in before and after[key] != before[key]
    )

    return added, removed, rewritten


def blob_keys(snapshot):
    """Return the content blobs in ``snapshot``, without their ``.meta`` sidecars."""
    return sorted(
        key
        for key in snapshot
        if key.startswith(BLOB_PREFIX) and not key.endswith(".meta")
    )


def namespaces_of(keys):
    """Return the ``cas/ns/<kind>/<digest>/`` prefixes covering ``keys``.

    A namespace owns several objects — a state checkpoint and a stream of log
    segments — and gains more of them over time, so a namespace is identified
    by its prefix rather than by the keys it happened to hold.
    """
    namespaces = set()

    for key in keys:
        parts = key.split("/")
        if key.startswith(NS_PREFIX) and len(parts) >= 4:
            namespaces.add("/".join(parts[:4]) + "/")

    return sorted(namespaces)


@TestStep(Then)
@Name("assert a CAS pool has blobs, manifests, and namespaces")
def assert_cas_pool_shape(self, snapshot):
    """Check the pool holds the object families a MergeTree write must publish."""
    keys = list(snapshot)
    blobs = blob_keys(snapshot)
    metas = sorted(
        key
        for key in keys
        if key.startswith(BLOB_PREFIX) and key.endswith(".meta")
    )
    manifests = sorted(key for key in keys if key.startswith(MANIFEST_PREFIX))
    namespaces = namespaces_of(keys)

    note(
        f"pool shape: {len(blobs)} blobs, {len(metas)} .meta, "
        f"{len(manifests)} manifests, namespaces={namespaces}"
    )

    assert blobs, error(f"no content blobs:\n{keys}")
    assert metas, error(f"no blob .meta sidecars:\n{keys}")
    assert manifests, error(f"no part manifests:\n{keys}")
    assert namespaces, error(f"no {NS_PREFIX} namespaces:\n{keys}")

    for key in blobs:
        match = BLOB_KEY.fullmatch(key)
        assert match is not None, error(f"invalid blob key: {key}")
        assert match.group(1) == match.group(2)[:2], error(
            f"blob shard does not match its hash: {key}"
        )

    for key in metas:
        match = BLOB_META_KEY.fullmatch(key)
        assert match is not None, error(f"invalid blob metadata key: {key}")
        assert match.group(1) == match.group(2)[:2], error(
            f"blob .meta shard does not match its hash: {key}"
        )

    assert {f"{key}.meta" for key in blobs} == set(metas), error(
        f"every content blob must have exactly one .meta sidecar: "
        f"blobs={blobs}, metas={metas}"
    )

    for key in manifests:
        assert MANIFEST_KEY.fullmatch(key), error(
            f"part manifest must use the expected .zst path: {key}"
        )

    assert not any(key.endswith(".parquet") for key in keys), error(
        f"CAS MergeTree objects must not be Parquet files:\n{keys}"
    )


def backup_manifest_keys(snapshot, backup_name):
    """Return the part manifests a FREEZE published for ``backup_name``.

    A manifest key spells out the namespace that owns it. Live parts land under
    ``cas/manifests/<server_root_id>/...``; frozen parts land under
    ``cas/manifests/shadow/<backup name>/...``, with no server in the path.
    """
    backup_path = f"{MANIFEST_PREFIX}shadow/{backup_name}/"

    return sorted(key for key in snapshot if key.startswith(backup_path))
