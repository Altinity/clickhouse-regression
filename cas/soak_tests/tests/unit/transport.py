import socket
import urllib.error

from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.steps.http import (
    ABORTED_CODE,
    KEEPER_EXCEPTION_CODE,
    NODE_DOWN_CODES,
    QueryError,
    is_aborted,
    is_keeper_transient,
    is_node_down,
    is_socket_timeout,
    is_transport_error,
    retry_on_transport,
)


def aborted_query_error():
    body = "Code: 236. DB::Exception: ... ABORTED, retry the operation. (ABORTED)"
    return QueryError("HttpNode(x:1)", 500, body, "INSERT INTO t VALUES")


def unknown_table_error():
    body = "Code: 60. DB::Exception: Table t does not exist. (UNKNOWN_TABLE)"
    return QueryError("HttpNode(x:1)", 500, body, "INSERT INTO t VALUES")


def query_cancelled_error():
    body = (
        "Code: 394. DB::Exception: Query was cancelled. (QUERY_WAS_CANCELLED) "
        "(version 26.6.1.1)"
    )
    return QueryError("HttpNode(localhost:8124)", 500, body, "INSERT INTO t VALUES")


def keeper_operation_timeout_error():
    body = (
        "Code: 999. Coordination::Exception: Coordination error: Operation timeout, "
        "path /clickhouse/tables/t/mutations. (KEEPER_EXCEPTION) (version 26.6.1.1)"
    )
    return QueryError("HttpNode(localhost:8123)", 500, body, "ALTER TABLE t DELETE WHERE 1")


@TestScenario
@Name("connection refused is transport")
def connection_refused_is_transport(self):
    err = urllib.error.URLError(ConnectionRefusedError(111, "Connection refused"))
    assert is_transport_error(err) is True, error()


@TestScenario
@Name("query error is not transport")
def query_error_is_not_transport(self):
    assert is_transport_error(aborted_query_error()) is False, error()
    assert is_transport_error(unknown_table_error()) is False, error()
    assert aborted_query_error().is_aborted is True, error()
    assert ABORTED_CODE == 236, error()


@TestScenario
@Name("query cancelled is node down but not transport")
def query_cancelled_is_node_down_but_not_transport(self):
    e = query_cancelled_error()
    assert is_transport_error(e) is False, error()
    assert e.is_node_down is True, error()
    assert is_node_down(e) is True, error()


@TestScenario
@Name("aborted is not node down")
def aborted_is_not_node_down(self):
    e = aborted_query_error()
    assert e.is_node_down is False, error()
    assert is_node_down(e) is False, error()


@TestScenario
@Name("node down codes include observed codes")
def node_down_codes_include_observed_codes(self):
    assert 394 in NODE_DOWN_CODES and 210 in NODE_DOWN_CODES, error()


@TestScenario
@Name("socket timeout classification")
def socket_timeout_classification(self):
    assert is_transport_error(socket.timeout("timed out")) is True, error()
    assert is_socket_timeout(socket.timeout("timed out")) is True, error()
    assert is_socket_timeout(ConnectionRefusedError(111, "Connection refused")) is False, error()


@TestScenario
@Name("retry recovers after node comes back")
def retry_recovers_after_node_comes_back(self):
    calls = {"n": 0}

    def attempt():
        calls["n"] += 1
        if calls["n"] <= 3:
            raise urllib.error.URLError(ConnectionRefusedError(111, "Connection refused"))
        return "ok"

    out = retry_on_transport(attempt, attempts=10, sleep_fn=lambda s: None)
    assert out == "ok", error()
    assert calls["n"] == 4, error()


@TestScenario
@Name("non transport error propagates immediately")
def non_transport_error_propagates_immediately(self):
    calls = {"n": 0}

    def attempt():
        calls["n"] += 1
        raise unknown_table_error()

    try:
        retry_on_transport(attempt, attempts=5, sleep_fn=lambda s: None)
        assert False, error("expected QueryError")
    except QueryError:
        assert calls["n"] == 1, error()


@TestScenario
@Name("query cancelled is retried and recovers")
def query_cancelled_is_retried_and_recovers(self):
    calls = {"n": 0}

    def attempt():
        calls["n"] += 1
        if calls["n"] <= 2:
            raise query_cancelled_error()
        return "ok"

    assert retry_on_transport(attempt, attempts=10, sleep_fn=lambda s: None) == "ok", error()
    assert calls["n"] == 3, error()


@TestScenario
@Name("retry timeouts false does not multiply")
def retry_timeouts_false_does_not_multiply(self):
    calls = {"n": 0}

    def attempt():
        calls["n"] += 1
        raise TimeoutError("timed out")

    try:
        retry_on_transport(
            attempt, attempts=5, sleep_fn=lambda s: None, retry_timeouts=False
        )
        assert False, error("expected TimeoutError")
    except TimeoutError:
        assert calls["n"] == 1, error()


@TestScenario
@Name("keeper operation timeout is retried")
def keeper_operation_timeout_is_retried(self):
    e = keeper_operation_timeout_error()
    assert e.is_keeper_transient is True, error()
    assert is_keeper_transient(e) is True, error()
    assert KEEPER_EXCEPTION_CODE == 999, error()
    calls = {"n": 0}

    def attempt():
        calls["n"] += 1
        if calls["n"] <= 2:
            raise e
        return "ok"

    assert retry_on_transport(attempt, attempts=10, sleep_fn=lambda s: None) == "ok", error()
    assert calls["n"] == 3, error()


@TestScenario
@Name("persistent aborted is absorbed by transport envelope")
def persistent_aborted_is_absorbed_by_transport_envelope(self):
    err = aborted_query_error()
    assert is_aborted(err), error()
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        if calls["n"] < 4:
            raise err
        return "ok"

    slept = []
    assert retry_on_transport(fn, attempts=10, sleep_fn=slept.append) == "ok", error()
    assert calls["n"] == 4, error()
    assert len(slept) == 3, error()


@TestScenario
@Name("backoff is bounded and capped")
def backoff_is_bounded_and_capped(self):
    sleeps = []

    def attempt():
        raise OSError("down")

    try:
        retry_on_transport(
            attempt,
            attempts=8,
            backoff_s=0.5,
            max_backoff_s=8.0,
            sleep_fn=sleeps.append,
        )
        assert False, error("expected OSError")
    except OSError:
        assert len(sleeps) == 7, error()
        assert all(s <= 8.0 for s in sleeps), error()
        assert sleeps[0] == 0.5 and sleeps[-1] == 8.0, error()


@TestFeature
@Name("transport")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
