"""Disk/pool cap policy for the scenario suite (no docker)."""
from pathlib import Path

from scenarios.framework.disk_cap import GB, prune_host_logs, trip_reason


def test_under_budget_is_none():
    assert trip_reason(10 * GB, 50 * GB, 40 * GB, 25 * GB) is None


def test_pool_over_cap_trips():
    reason = trip_reason(41 * GB, 100 * GB, 40 * GB, 25 * GB)
    assert reason is not None
    assert "max-pool-gb" in reason


def test_low_free_disk_trips():
    reason = trip_reason(1 * GB, 10 * GB, 40 * GB, 25 * GB)
    assert reason is not None
    assert "min-free-disk-gb" in reason


def test_zero_budget_disables_that_side():
    assert trip_reason(100 * GB, 5 * GB, 0, 0) is None
    assert trip_reason(100 * GB, 50 * GB, 0, 25 * GB) is None
    assert trip_reason(1 * GB, 5 * GB, 40 * GB, 0) is None


def test_missing_pool_probe_does_not_false_trip():
    assert trip_reason(None, 50 * GB, 40 * GB, 25 * GB) is None


def test_prune_drops_prev_and_old_predown(tmp_path: Path):
    logs = tmp_path / "logs"
    (logs / "prev_old" / "ch1").mkdir(parents=True)
    (logs / "prev_old" / "ch1" / "clickhouse-server.log").write_text("x" * 100)
    pre = logs / "predown" / "ch1"
    for lab in ("S01_a", "S02_b", "S03_c"):
        d = pre / lab
        d.mkdir(parents=True)
        (d / "cas_log.tsv").write_text("rows")
    (logs / "_archive_old_ch1.tgz").write_bytes(b"old")
    (logs / "_archive_mid_ch1.tgz").write_bytes(b"mid")
    newer = logs / "_archive_new_ch1.tgz"
    newer.write_bytes(b"new")
    import os
    os.utime(logs / "_archive_old_ch1.tgz", (1, 1))
    os.utime(logs / "_archive_mid_ch1.tgz", (2, 2))
    os.utime(newer, (3, 3))

    removed = prune_host_logs(logs, keep_predown=2, keep_archive=2)
    assert removed["prev"] == 1
    assert not (logs / "prev_old").exists()
    assert not (pre / "S01_a").exists()
    assert (pre / "S02_b").exists()
    assert (pre / "S03_c").exists()
    assert not (logs / "_archive_old_ch1.tgz").exists()
    assert (logs / "_archive_new_ch1.tgz").exists()
