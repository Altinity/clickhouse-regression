"""Direct inspection of the objects a CAS pool holds in object storage."""

import time

from testflows.asserts import error
from testflows.core import *

BLOB_PREFIX = "blobs/"
MANIFEST_PREFIX = "cas/manifests/"
NS_PREFIX = "cas/ns/"

# ``mc find --print {size}`` uses IEC units for large objects and a bare ``B``
# for small ones. Decimal KB/MB/GB are accepted in case the client spelling
# changes.
_SIZE_UNITS = {
    "B": 1,
    "KiB": 1024,
    "MiB": 1024**2,
    "GiB": 1024**3,
    "KB": 1000,
    "MB": 1000**2,
    "GB": 1000**3,
}

def docker_exec(cluster, service, command):
    """Run ``command`` in ``service`` without a TTY.

    ``Cluster.command(service, ...)`` uses ``docker exec -it`` and opens
    bash. The RustFS image has no bash, and a TTY makes ``mc`` query the
    host terminal for colours and cursor position. Those replies
    (``11;rgb:...``, ``2;44R``) land in the user's shell after the test.
    """
    container_id = cluster.node_container_id(service)
    return cluster.command(
        None, f"docker exec {container_id} {command}", no_checks=True
    )


@TestStep(Then)
def pool_snapshot(self, pool_prefix, cluster=None):
    """Snapshot the objects stored in a CAS pool as ``{key: size}``.

    Keys are relative to the pool prefix, so they read as ``blobs/...``,
    ``cas/manifests/...`` and ``cas/ns/...``. Sizes are part of the snapshot
    because a pool can change without gaining or losing a key — appending to a
    ref stream rewrites an object in place.
    """
    if cluster is None:
        cluster = self.context.cluster

    # Alias ``minio`` is the RustFS S3 endpoint (compose service name).
    # Pipe, not tab: host bash is a pexpect Shell, and a tab is cursor motion.
    listing = docker_exec(
        cluster,
        "mc",
        f"mc --no-color find minio/warehouse/{pool_prefix} --print '{{}}|{{size}}'",
    )

    output = listing.output
    pool_path = f"minio/warehouse/{pool_prefix}/"
    snapshot = {}

    for line in output.splitlines():
        line = line.strip()
        if pool_path not in line or "|" not in line:
            continue
        path, _, size = line.rpartition("|")
        snapshot[path.split(pool_path, 1)[1]] = size.strip()

    if not snapshot and pool_path in output:
        fail(f"could not parse any keys from pool listing:\n{output}")

    return snapshot


@TestStep(Then)
def settled_pool_snapshot(self, pool_prefix, attempts=15, delay=2):
    """Wait for a CAS pool to stop changing, then return the last snapshot.

    Polls until two consecutive snapshots agree. Replication, merges and
    background CAS work keep writing after a query has returned, so a snapshot
    taken immediately is not a baseline that anything can be compared against.
    """
    previous = pool_snapshot(pool_prefix=pool_prefix)

    for _ in range(attempts):
        time.sleep(delay)
        current = pool_snapshot(pool_prefix=pool_prefix)
        if current == previous:
            return current
        previous = current

    fail(f"pool {pool_prefix} never stopped changing, nothing can be compared")


def size_in_bytes(size):
    """Parse one pool-snapshot size, which ``mc`` prints as ``1.0 MiB`` / ``542 B``."""
    number, _, unit = str(size).strip().partition(" ")
    return int(float(number) * _SIZE_UNITS[unit.strip() or "B"])


@TestStep(Then)
def pool_size_bytes(self, pool_prefix, cluster=None):
    """Measure the physical size of a CAS pool on the RustFS volume.

    ``du`` counts what the disk holds, including RustFS sidecars that an S3
    listing from ``mc`` does not show. The compose service is named ``minio``;
    its volume root is ``/data`` and the S3 bucket is ``warehouse``.
    """
    if cluster is None:
        cluster = self.context.cluster

    pool_dir = f"/data/warehouse/{pool_prefix}"
    listing = docker_exec(cluster, "minio", f"sh -c 'du -sb {pool_dir}'")
    first_line = (
        listing.output.strip().splitlines()[0] if listing.output.strip() else ""
    )
    total = first_line.split()[0] if first_line else ""
    assert total.isdigit(), error(
        f"could not read RustFS pool size for {pool_dir}: {listing.output}"
    )
    return int(total)


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


def backup_manifest_keys(snapshot, backup_name):
    """Return the part manifests a FREEZE published for ``backup_name``.

    A manifest key spells out the namespace that owns it. Live parts land under
    ``cas/manifests/<server_root_id>/...``; frozen parts land under
    ``cas/manifests/shadow/<backup name>/...``, with no server in the path.
    """
    backup_path = f"{MANIFEST_PREFIX}shadow/{backup_name}/"

    return sorted(key for key in snapshot if key.startswith(backup_path))
