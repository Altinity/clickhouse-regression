"""Shared P1 card helpers. No cas.soak imports."""

from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import observe as O


def scale_verdict(result, expected, observed, note="dev/ci are scaled down; only --scenario-scale full approaches the spec target"):
    result.add(Verdict("scale used", expected, observed, "pass", note))


def ca_since(ctx):
    return O.ca_event_counts_all(ctx.cluster, ctx.extra.get("since_event_time"))
