import os
import tempfile
from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.steps.cas_log import dump_cas_logs


class _Script:
    """Fake HTTP endpoint. The first ``fail_selects`` table reads fail."""

    def __init__(self, body, fail_selects=0):
        self.body = body
        self.fail_selects = fail_selects
        self.selects = 0
        self.calls = []

    def __call__(self, port, sql, timeout, dest):
        self.calls.append((port, sql, dest))
        if dest is None:
            return
        self.selects += 1
        if self.selects <= self.fail_selects:
            raise RuntimeError(f"down {port}")
        with open(dest, "wb") as out:
            out.write(self.body)


@TestScenario
@Name("cas_log dump writes both replicas")
def dump_writes_both_replicas(self):
    body = b"event_type\nref_resolve\n"
    script = _Script(body)
    dest = tempfile.mkdtemp()
    statuses = dump_cas_logs(
        dest,
        nodes={"clickhouse1": 8123, "clickhouse2": 8124},
        post=script,
        attempts=2,
        pause_s=0,
    )
    assert statuses == [
        ("clickhouse1", f"ok {len(body)} bytes"),
        ("clickhouse2", f"ok {len(body)} bytes"),
    ], error(statuses)
    for name in ("clickhouse1", "clickhouse2"):
        path = os.path.join(dest, f"{name}.cas_log.log")
        with open(path, "rb") as f:
            assert f.read() == body, error(name)
        assert not os.path.exists(path + ".tmp"), error(name)
        assert not os.path.exists(os.path.join(dest, f"{name}.cas_log.err.log")), error(name)
    selects = [sql for _port, sql, dest in script.calls if dest is not None]
    assert selects == ["SELECT * FROM system.cas_log FORMAT TSVWithNames"] * 2, error(selects)
    flushes = [sql for _port, sql, dest in script.calls if dest is None]
    assert flushes == ["SYSTEM FLUSH LOGS"] * 2, error(flushes)


@TestScenario
@Name("cas_log dump records a replica that stays down")
def dump_records_a_down_replica(self):
    script = _Script(b"event_type\n", fail_selects=5)
    dest = tempfile.mkdtemp()
    statuses = dump_cas_logs(
        dest,
        nodes={"clickhouse1": 8123},
        post=script,
        attempts=2,
        pause_s=0,
    )
    assert statuses[0][0] == "clickhouse1", error(statuses)
    assert statuses[0][1].startswith("failed:"), error(statuses)
    assert not os.path.exists(os.path.join(dest, "clickhouse1.cas_log.log")), error()
    err = os.path.join(dest, "clickhouse1.cas_log.err.log")
    with open(err, encoding="utf-8") as f:
        assert "down 8123" in f.read(), error()


@TestScenario
@Name("cas_log dump retries then keeps the table")
def dump_retries_then_keeps_the_table(self):
    body = b"event_type\nok\n"
    script = _Script(body, fail_selects=1)
    dest = tempfile.mkdtemp()
    statuses = dump_cas_logs(
        dest,
        nodes={"clickhouse1": 8123},
        post=script,
        attempts=3,
        pause_s=0,
    )
    assert statuses == [("clickhouse1", f"ok {len(body)} bytes")], error(statuses)
    with open(os.path.join(dest, "clickhouse1.cas_log.log"), "rb") as f:
        assert f.read() == body, error()
    assert not os.path.exists(os.path.join(dest, "clickhouse1.cas_log.err.log")), error()


@TestFeature
@Name("cas_log")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
