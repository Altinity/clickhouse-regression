"""The filed mount-lease drop: Code 210, 'mount lease not held' (#2431)."""

from cas.soak_tests.oracle.verdict import Verdict

_NEEDLE = "mount lease not held"


def is_mount_lease_drop(exc) -> bool:
    return _NEEDLE in str(exc)


def mount_lease_verdict(count, samples=()):
    """Fail when a write was refused because the server no longer held the mount lease."""
    shown = [str(s)[:240] for s in samples[:3]]
    observed = str(count) if not shown else f"{count} | " + " | ".join(shown)
    return Verdict.check(
        "mount lease held",
        "0 writes failed with 'mount lease not held' (#2431)",
        observed,
        count == 0,
    )
