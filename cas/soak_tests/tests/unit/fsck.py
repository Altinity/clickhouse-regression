from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle.fsck import (
    parse_dryrun,
    parse_fsck_stdout,
    parse_fsck_summary,
    stale_edge_verdict,
)

SUMMARY_LINE = (
    "reachable=120 dangling=0 unreachable=7 pending_gc=3 awaiting_gc=4 unaccounted=0 "
    "stale_edge=0 physical_bytes=4096 "
    "referenced_logical_bytes=8192 distinct_blobs=120 total_blob_refs=456 dedup_ratio=3.8"
)


@TestScenario
@Name("parse fsck summary")
def parse_fsck_summary_integers_and_ratio(self):
    line = (
        "reachable=18432 dangling=0 unreachable=211 physical_bytes=5500000000 "
        "referenced_logical_bytes=8200000000 distinct_blobs=12000 total_blob_refs=18000 "
        "dedup_ratio=1.5"
    )
    r = parse_fsck_summary(line)
    assert r["dangling"] == 0 and r["unreachable"] == 211 and r["reachable"] == 18432, error()
    assert r["distinct_blobs"] == 12000, error()


@TestScenario
@Name("parse fsck summary partial reason")
def parse_fsck_summary_partial(self):
    line = (
        "reachable=100 dangling=0 unreachable=0 pending_gc=0 awaiting_gc=0 unaccounted=0 "
        "physical_bytes=0 referenced_logical_bytes=0 distinct_blobs=0 total_blob_refs=0 "
        "dedup_ratio=0 partial=1 reason='fsck: exceeded the deadline during "
        "'walking refs' — run against a QUIESCED pool or raise --timeout.'"
    )
    r = parse_fsck_summary(line)
    assert r["partial"] == 1, error()
    assert r["reachable"] == 100, error()
    assert "exceeded the deadline" in r["reason"], error()


@TestScenario
@Name("parse dryrun")
def parse_dryrun_entries(self):
    out = (
        "preview_deletes=2\n"
        "unreachable\tpool/blobs/ab/abcd\t100\n"
        "unreachable\tpool/trees/cd/cdef\t40\n"
    )
    r = parse_dryrun(out)
    assert r["count"] == 2, error()
    assert {e["key"] for e in r["entries"]} == {
        "pool/blobs/ab/abcd",
        "pool/trees/cd/cdef",
    }, error()


@TestScenario
@Name("parse fsck summary ignores cursor color")
def parse_fsck_summary_ignores_cursor_color(self):
    colored = (
        "\x1b[01;31m\x1b[Kreachable=\x1b[m\x1b[K120 dangling=\x1b[m\x1b[K0 "
        "unreachable=7 pending_gc=3\n"
    )
    r = parse_fsck_stdout(colored, exit_code=0, detail=False)
    assert r["reachable"] == 120 and r["dangling"] == 0 and r["unreachable"] == 7, error()


@TestScenario
@Name("parse fsck stdout collects detail rows")
def parse_fsck_stdout_detail(self):
    stdout = (
        f"{SUMMARY_LINE}\n"
        "reachable\tpool/blobs/aa/aaa\t10\n"
        "unreachable\tpool/blobs/bb/bbb\t20\n"
    )
    r = parse_fsck_stdout(stdout, exit_code=0, detail=True)
    assert r["dangling"] == 0, error()
    assert r["exit_code"] == 0, error()
    classes = {row["class"] for row in r["detail"]}
    assert classes == {"reachable", "unreachable"}, error()


@TestScenario
@Name("summary line carries stale_edge")
def summary_line_carries_stale_edge(self):
    parsed = parse_fsck_summary(SUMMARY_LINE)
    assert parsed["stale_edge"] == 0, error()
    assert parsed["unreachable"] == 7, error()


@TestScenario
@Name("missing stale_edge key fails closed")
def missing_key_fails_closed(self):
    verdict, why = stale_edge_verdict(
        {"reachable": 1, "unreachable": 0, "dangling": 0}, detail=True
    )
    assert verdict == "absent", error()
    assert "predates" in why, error()


@TestScenario
@Name("missing key fails closed even on a clean summary")
def missing_key_fails_closed_even_on_a_clean_summary(self):
    verdict, _ = stale_edge_verdict({"unreachable": 0, "dangling": 0}, detail=False)
    assert verdict == "absent", error()


@TestScenario
@Name("nonzero stale_edge on a detail scan is a hard finding")
def nonzero_on_a_detail_scan_is_a_hard_finding(self):
    parsed = parse_fsck_summary(SUMMARY_LINE.replace("stale_edge=0", "stale_edge=5"))
    verdict, why = stale_edge_verdict(parsed, detail=True)
    assert verdict == "found", error()
    assert "5" in why, error()


@TestScenario
@Name("zero stale_edge on a detail scan is clean")
def zero_on_a_detail_scan_is_clean(self):
    verdict, _ = stale_edge_verdict(parse_fsck_summary(SUMMARY_LINE), detail=True)
    assert verdict == "clean", error()


@TestScenario
@Name("summary zero with unreferenced blobs is unchecked")
def summary_zero_with_unreferenced_blobs_is_unchecked_not_clean(self):
    verdict, why = stale_edge_verdict(parse_fsck_summary(SUMMARY_LINE), detail=False)
    assert verdict == "unchecked", error()
    assert "structural" in why, error()


@TestScenario
@Name("summary zero with no unreferenced blobs is clean")
def summary_zero_with_no_unreferenced_blobs_is_genuinely_clean(self):
    line = SUMMARY_LINE.replace("unreachable=7", "unreachable=0")
    verdict, _ = stale_edge_verdict(parse_fsck_summary(line), detail=False)
    assert verdict == "clean", error()


@TestFeature
@Name("fsck")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
