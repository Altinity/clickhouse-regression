"""Unit tests for scenario cluster bring-up helpers (no docker required).

Covers the 2026-08-21 AMD suite hang:
  * compose project must be pinned to `ca-soak` (directory name is `cas/soak` -> `soak`)
  * `_run` must not raise TimeoutExpired; it kills the process group and returns 124
"""
import time

from scenarios.framework.cluster_boot import _run, compose_cmd, compose_project, predown_dump


def test_compose_project_pinned_to_ca_soak():
    assert compose_project(None) == "ca-soak"
    assert compose_project("default") == "ca-soak"
    assert compose_project("tenreplicas") == "ca-soak"
    assert compose_project("s41") == "ca-s41"


def test_compose_cmd_includes_project_flag():
    cmd = compose_cmd(None, "up", "-d")
    assert cmd[:4] == ["docker", "compose", "-p", "ca-soak"]
    assert cmd[-2:] == ["up", "-d"]
    ten = compose_cmd("tenreplicas", "down", "-v", "--remove-orphans")
    assert ten[:4] == ["docker", "compose", "-p", "ca-soak"]
    assert "-f" in ten
    s41 = compose_cmd("s41", "up", "-d")
    assert s41[:4] == ["docker", "compose", "-p", "ca-s41"]


def test_run_timeout_returns_124_and_does_not_raise():
    t0 = time.monotonic()
    rc = _run(["/bin/sh", "-c", "sleep 30"], timeout=0.4, log_fn=lambda *_: None)
    elapsed = time.monotonic() - t0
    assert rc == 124
    assert elapsed < 5


def test_run_success_returns_zero():
    rc = _run(["/bin/true"], timeout=5, log_fn=lambda *_: None)
    assert rc == 0


def test_predown_dump_timeout_does_not_raise(monkeypatch):
    """reset_cluster / end-of-batch must keep going when the dump script hangs."""
    monkeypatch.setattr(
        "scenarios.framework.cluster_boot._run",
        lambda argv, timeout=600, log_fn=print: 124)
    rc = predown_dump("unit_test_label", log_fn=lambda *_: None, timeout=1)
    assert rc == 124
