"""Manual CAS garbage-collection helpers."""

from testflows.core import *


@TestStep(When)
@Name("run garbage collection on a CAS pool")
def collect_garbage(self, disk, nodes=None, rounds=4):
    """Run garbage collection on ``disk`` from every server mounting the pool.

    Reclamation is staged — a round condemns what it found unreachable and a
    later round deletes it — and only one server holds the collection lease at
    a time, so a single round on a single server proves nothing either way.
    """
    if nodes is None:
        nodes = self.context.nodes

    for _ in range(rounds):
        for node in nodes:
            node.query(f"SYSTEM CAS GC RUN '{disk}'")


@TestStep(Given)
@Name("stop background garbage collection")
def stop_garbage_collection(self, disk, nodes=None):
    """Pause the background GC scheduler on ``disk`` on every given server.

    STOP is process-local and does not survive restart. Manual
    ``SYSTEM CAS GC RUN`` still runs. The scheduler is started again on
    every given node when this step finishes.
    """
    if nodes is None:
        nodes = self.context.nodes

    for node in nodes:
        node.query(f"SYSTEM CAS GC STOP '{disk}'")

    try:
        yield
    finally:
        with Finally("resume background garbage collection"):
            start_garbage_collection(disk=disk, nodes=nodes)


@TestStep(When)
@Name("start background garbage collection")
def start_garbage_collection(self, disk, nodes=None):
    """Resume the background GC scheduler on ``disk`` on every given server."""
    if nodes is None:
        nodes = self.context.nodes

    for node in nodes:
        node.query(f"SYSTEM CAS GC START '{disk}'")
