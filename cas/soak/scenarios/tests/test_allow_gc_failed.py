"""Injected-fault cards must not FAIL the common "0 Failed GC rounds" check.

S13 kills the GC leader; S39 holds PUT/POST 503s past the mount-lease TTL. Both produce real Error
finish rows that are the fault, not a CAS leak. `allow_gc_failed=True` records the count and leaves
fsck/leftovers as the safety net.
"""
from scenarios.framework.assertions import run_common_assertions
from scenarios.framework.report import ScenarioResult


def _result(name="S13"):
    return ScenarioResult(name, "x", "P0", 1)


def _clean(**extra):
    return dict(
        fsck_final={"dangling": 0, "unreachable": 0},
        fsck_detail_res={"detail": []},
        dryrun_res={"entries": []},
        ca_events={"rows_total": 1, "bad_total": {}},
        residual_after_gc=0,
        **extra,
    )


def _gc_verdicts(result):
    return [v for v in result.verdicts if "GC Failed" in v.name or v.name == "GC no Failed rounds"]


def test_allow_gc_failed_does_not_fail_on_error_rows():
    r = _result()
    run_common_assertions(
        r, gc_summary={"failed": 7, "rows_total": 10}, allow_gc_failed=True, **_clean())
    r.finalize()
    gc = _gc_verdicts(r)
    assert len(gc) == 1
    assert gc[0].status == "pass"
    assert gc[0].name == "GC Failed rounds (not asserted)"
    assert r.status != "fail"


def test_gc_failed_still_fails_by_default():
    r = _result("S01")
    run_common_assertions(
        r, gc_summary={"failed": 7, "rows_total": 10}, allow_gc_failed=False, **_clean())
    r.finalize()
    gc = _gc_verdicts(r)
    assert len(gc) == 1
    assert gc[0].status == "fail"
    assert gc[0].name == "GC no Failed rounds"
    assert r.status == "fail"
