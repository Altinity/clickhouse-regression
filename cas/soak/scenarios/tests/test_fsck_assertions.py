"""Missing fsck summaries must be inconclusive, never FAIL via `dangling == 0` on None.

ARM 2026-08-21: docker exec `ca-soak-ch1-1` failed (compose project was `soak`), so fsck returned
`{exit_code: 1, stderr: No such container}` with no `dangling` key. Card-local `dangling == 0`
then FAIL-closed a dozen P0 cards.
"""
from scenarios.framework.assertions import assert_fsck_clean, assert_fsck_count
from scenarios.framework.report import ScenarioResult


def _result():
    return ScenarioResult("X", "x", "P0", 1)


def test_docker_miss_is_inconclusive_not_fail():
    r = _result()
    v = assert_fsck_clean(r, {
        "exit_code": 1, "stdout": "",
        "stderr": "Error response from daemon: No such container: ca-soak-ch1-1",
    })[0]
    assert v.status == "inconclusive"


def test_empty_fsck_is_inconclusive():
    r = _result()
    v = assert_fsck_clean(r, {})[0]
    assert v.status == "inconclusive"


def test_dangling_none_is_inconclusive():
    r = _result()
    v = assert_fsck_clean(r, {"dangling": None, "exit_code": 0})[0]
    assert v.status == "inconclusive"


def test_dangling_zero_passes():
    r = _result()
    v = assert_fsck_clean(r, {"dangling": 0})[0]
    assert v.status == "pass"


def test_dangling_nonzero_fails():
    r = _result()
    v = assert_fsck_clean(r, {"dangling": 2})[0]
    assert v.status == "fail"


def test_custom_name_is_kept():
    r = _result()
    v = assert_fsck_clean(r, {"dangling": 0}, name="no dangling after drain")[0]
    assert v.name == "no dangling after drain"
    assert v.status == "pass"


def test_unreachable_missing_is_inconclusive():
    r = _result()
    v = assert_fsck_count(
        r, {"exit_code": 1}, "unreachable",
        name="drop created unreachable backlog", expected=">0",
        ok_fn=lambda n: n > 0)[0]
    assert v.status == "inconclusive"


def test_unreachable_positive_passes():
    r = _result()
    v = assert_fsck_count(
        r, {"unreachable": 12}, "unreachable",
        name="drop created unreachable backlog", expected=">0",
        ok_fn=lambda n: n > 0)[0]
    assert v.status == "pass"
