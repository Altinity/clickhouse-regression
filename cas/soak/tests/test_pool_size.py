"""Unit tests for `pool_size`'s tolerance of `du`'s benign TOCTOU race.

`du -sb` over the live, actively-mutating CA pool directory can list a file that a concurrent
writer/GC then removes before `du` stats it -- `du` prints a "cannot access ... No such file or
directory" warning to stderr and exits nonzero, but STILL prints a valid (near-exact) recursive
byte total to stdout. `pool_size` must use that total rather than discarding it on returncode
alone (a real 5h soak run hit this on ~every other 60s tick, needlessly fail-closing the insert
throttle to its maximum every other tick with the pool at ~2% of budget)."""

import subprocess

from soak.pool import pool_size


class _FakeCompletedProcess:
    def __init__(self, returncode, stdout):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = ""


def test_pool_size_uses_stdout_total_despite_nonzero_returncode_from_toctou_race(monkeypatch):
    fake = _FakeCompletedProcess(
        returncode=1,
        stdout="1235253058\t/data/test/soak_pool\n",
    )
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: fake)
    objs, pbytes = pool_size()
    assert objs is None
    assert pbytes == 1235253058


def test_pool_size_returns_none_on_genuinely_empty_stdout(monkeypatch):
    fake = _FakeCompletedProcess(returncode=1, stdout="")
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: fake)
    assert pool_size() == (None, None)


def test_pool_size_returns_none_on_subprocess_exception(monkeypatch):
    def _raise(*a, **kw):
        raise subprocess.TimeoutExpired(cmd=["docker", "exec", "fake"], timeout=1.0)
    monkeypatch.setattr(subprocess, "run", _raise)
    assert pool_size() == (None, None)


def test_pool_size_happy_path_zero_returncode(monkeypatch):
    fake = _FakeCompletedProcess(returncode=0, stdout="42\t/data/test/soak_pool\n")
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: fake)
    objs, pbytes = pool_size()
    assert objs is None
    assert pbytes == 42


def test_pool_size_honors_ca_soak_env(monkeypatch):
    captured = {}

    def _run(*a, **kw):
        captured["cmd"] = a[0]
        return _FakeCompletedProcess(0, "7\t/data/warehouse/soak_pool\n")

    monkeypatch.setenv("CA_SOAK_RUSTFS_CONTAINER", "cas_soak_rustfs")
    monkeypatch.setenv("CA_SOAK_POOL_DIR", "/data/warehouse/soak_pool")
    monkeypatch.setattr(subprocess, "run", _run)
    objs, pbytes = pool_size()
    assert objs is None
    assert pbytes == 7
    assert captured["cmd"][2] == "cas_soak_rustfs"
    assert "/data/warehouse/soak_pool" in captured["cmd"][5]
