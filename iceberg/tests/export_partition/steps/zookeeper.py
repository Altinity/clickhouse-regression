"""Thin helpers for mutating the ZooKeeper state from export tests.

The regression image does not ship the ``kazoo`` client, but every
cluster we target for this suite already runs a ``zookeeper1``
container with ``zkCli.sh`` on its ``PATH``. Exec-ing into that
container through the cluster handle is the lightest-weight way to
drop / inspect znodes in-test without adding a Python dependency.

This helper is intentionally narrow: it only exposes the operations
the ``zk_compat`` scenarios need (exists / deleteall). The split
between "read" and "write" on the ZooKeeper control plane stays
firmly on the test side, not the SUT — we run the commands inside the
ZK container itself, not from inside ClickHouse.

Looking for the full multi-replica / restart flows? Those live in
``multi_replica_recovery.py`` — it talks to the same container
through ``cluster.node("zookeeper1")`` but uses ``zkServer.sh`` for
lifecycle rather than ``zkCli.sh`` for data-plane reads.
"""

from testflows.core import *
from testflows.asserts import error


ZOOKEEPER_SERVICE = "zookeeper1"

# ``zkCli.sh`` prints its JVM banner to stdout, then the actual response
# from the server, then "WATCHER" events, etc. We need a deterministic
# marker that tells us "the node is missing". ``stat``, ``ls`` and
# ``delete`` all surface the plain ``Node does not exist: <path>``
# line; ``get`` (and a few other commands we do not use) emit the
# exception form ``KeeperErrorCode = NoNode``. Match either so the
# helper stays correct if callers add ``get``-based probes later —
# matching only the latter was the reason an earlier revision
# reported every existence check as "present" regardless of reality.
_NONODE_TOKENS = ("Node does not exist", "KeeperErrorCode = NoNode")


def _output_says_nonode(output):
    """Return True when ``zkCli.sh`` stdout reports the target is missing."""
    output = output or ""
    return any(token in output for token in _NONODE_TOKENS)


def _zk_node(self):
    """Return the ``zookeeper1`` cluster Node handle."""
    return self.context.cluster.node(ZOOKEEPER_SERVICE)


def _zkcli(self, command):
    """Run ``zkCli.sh -server localhost:2181 <command>`` inside the ZK container.

    Returns the ``Result`` from ``node.command`` so callers can grep
    stdout for success/error tokens. ``no_checks=True`` is mandatory
    here: ``zkCli.sh`` exits 1 on common benign conditions (e.g.
    ``stat`` on a missing node, ``deleteall`` on a missing path),
    and we want the caller — not the cluster wrapper — to decide
    whether the error string in stdout matters.
    """
    zk = _zk_node(self)
    return zk.command(
        f"zkCli.sh -server localhost:2181 {command}",
        steps=False,
        no_checks=True,
    )


def _tail_lines(output, n=10):
    """Return the last ``n`` non-empty lines of ``output`` joined with newlines.

    ``zkCli.sh`` prints a huge JVM banner to stdout before the actual
    result of the command; forwarding the tail is enough to diagnose
    failures without drowning the test log in env info.
    """
    lines = [line for line in (output or "").splitlines() if line.strip()]
    return "\n".join(lines[-n:])


def _zkcli_children(self, path):
    """Return the children of ``path`` as a list, or ``None`` if the
    path is missing.

    ``ls`` in ``zkCli.sh`` prints a single ``[a, b, c]``-style line for
    the result (or ``Node does not exist`` on a missing path). We scan
    the tail of the output for the bracketed line so JVM banner noise
    above it does not confuse the parse.
    """
    result = _zkcli(self, f"ls {path}")
    if _output_says_nonode(result.output):
        return None
    for line in reversed((result.output or "").splitlines()):
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            inner = line[1:-1].strip()
            if not inner:
                return []
            return [child.strip() for child in inner.split(",") if child.strip()]
    return []


@TestStep(When)
def zk_node_exists(self, path):
    """Return ``True`` when ``path`` exists in ZooKeeper."""
    result = _zkcli(self, f"stat {path}")
    # ``stat`` on a missing node prints ``Node does not exist: <path>``
    # to stdout and exits 1. On success it prints the Stat struct
    # (cZxid, mZxid, ...) and still exits 0, so scanning stdout for
    # the NoNode markers is the single source of truth.
    return not _output_says_nonode(result.output)


@TestStep(Given)
def ensure_zk_path_absent(self, path):
    """Guarantee ``path`` does not exist in ZooKeeper after this step.

    Recursively removes the path (children first, then itself) so the
    scenario enters the legacy pre-EXPORT-feature ZK layout regardless
    of whether ClickHouse created the znode at table-registration time
    (see ``StorageReplicatedMergeTree.cpp`` line 1131 — ``/exports`` is
    part of the atomic CREATE TABLE multi-op).

    Implementation: explicit ``ls`` + child-by-child ``delete`` loop.
    ``zkCli.sh deleteall`` would also work on the 3.8.x image the
    suite uses, but stepping through the subtree one level at a time
    makes the failure mode self-diagnosing — if a delete is rejected
    or a re-create races us, the final assertion can point at the
    exact surviving subtree.

    If the deletion cannot converge (e.g. ClickHouse reinstates the
    znode through a watch faster than we can remove it), the final
    assertion emits the residual ``ls`` / ``stat`` output so the fail
    traces back to a concrete ZK state rather than a generic "still
    present".
    """

    def _recursive_delete(target):
        children = _zkcli_children(self, target)
        if children is None:
            return
        for child in children:
            _recursive_delete(f"{target.rstrip('/')}/{child}")
        result = _zkcli(self, f"delete {target}")
        # ``delete`` on a missing node is fine; propagate any other
        # error tail through the eventual assertion below.
        if _output_says_nonode(result.output):
            return

    with By(f"recursively removing {path} via zkCli.sh on {ZOOKEEPER_SERVICE}"):
        _recursive_delete(path)

    with And(f"verify ZK path {path!r} is absent"):
        if zk_node_exists(path=path):
            # Snapshot the residual subtree (one level is enough to
            # tell us whether CH re-created ``/exports`` unprompted,
            # or whether our delete never made it through at all).
            residual_children = _zkcli_children(self, path)
            ls_result = _zkcli(self, f"ls {path}")
            stat_result = _zkcli(self, f"stat {path}")
            assert False, error(
                f"ZK path {path!r} still present after recursive delete.\n"
                f"children: {residual_children!r}\n"
                f"ls tail:\n{_tail_lines(ls_result.output)}\n"
                f"stat tail:\n{_tail_lines(stat_result.output)}"
            )
