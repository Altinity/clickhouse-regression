from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.steps.http import ABORTED_CODE, QueryError, retry_on_aborted


class FakeNode:
    def __init__(self, fail_with, fail_times):
        self.fail_with = fail_with
        self.fail_times = fail_times
        self.calls = 0

    def command(self, sql):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise self.fail_with
        return None


def aborted_error():
    body = "Code: 236. DB::Exception: ... ABORTED, retry the operation. (ABORTED)"
    return QueryError("HttpNode(x:1)", 500, body, "INSERT INTO t VALUES")


def other_error():
    body = "Code: 60. DB::Exception: Table t does not exist. (UNKNOWN_TABLE)"
    return QueryError("HttpNode(x:1)", 500, body, "INSERT INTO t VALUES")


def fence_error():
    body = (
        "Code: 236. DB::Exception: CAS mount lost / lease expired — refusing to "
        "mutate ref shard for server_root 'ca_soak_ch1'. (ABORTED)"
    )
    return QueryError("HttpNode(x:1)", 500, body, "INSERT INTO t VALUES")


@TestScenario
@Name("is_aborted detects code 236")
def is_aborted_detects_code_236(self):
    assert aborted_error().is_aborted is True, error()
    assert other_error().is_aborted is False, error()


@TestScenario
@Name("retry succeeds after two aborted")
def retry_succeeds_after_two_aborted(self):
    node = FakeNode(aborted_error(), fail_times=2)
    retries = []
    retry_on_aborted(
        lambda: node.command("INSERT INTO t VALUES"),
        backoff_s=0,
        on_retry=lambda attempt, err: retries.append(attempt),
    )
    assert node.calls == 3, error()
    assert retries == [1, 2], error()


@TestScenario
@Name("retry returns immediately on first success")
def retry_returns_immediately_on_first_success(self):
    node = FakeNode(aborted_error(), fail_times=0)
    retry_on_aborted(lambda: node.command("INSERT INTO t VALUES"), backoff_s=0)
    assert node.calls == 1, error()


@TestScenario
@Name("retry exhaustion raises aborted")
def retry_exhaustion_raises_aborted(self):
    node = FakeNode(aborted_error(), fail_times=99)
    try:
        retry_on_aborted(
            lambda: node.command("INSERT INTO t VALUES"), attempts=6, backoff_s=0
        )
        assert False, error("expected QueryError")
    except QueryError as e:
        assert e.is_aborted, error()
        assert node.calls == 6, error()


@TestScenario
@Name("non aborted error is not retried")
def non_aborted_error_is_not_retried(self):
    node = FakeNode(other_error(), fail_times=99)
    try:
        retry_on_aborted(
            lambda: node.command("INSERT INTO t VALUES"), attempts=6, backoff_s=0
        )
        assert False, error("expected QueryError")
    except QueryError as e:
        assert e.code == 500 and not e.is_aborted, error()
        assert node.calls == 1, error()


@TestScenario
@Name("mount fence aborted is not retried")
def mount_fence_aborted_is_not_retried(self):
    node = FakeNode(fence_error(), fail_times=99)
    try:
        retry_on_aborted(
            lambda: node.command("INSERT INTO t VALUES"), attempts=6, backoff_s=0
        )
        assert False, error("expected QueryError")
    except QueryError as e:
        assert e.is_aborted and e.is_mount_fenced, error()
        assert node.calls == 1, error()


@TestScenario
@Name("aborted code constant")
def aborted_code_constant(self):
    assert ABORTED_CODE == 236, error()


@TestFeature
@Name("http")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
