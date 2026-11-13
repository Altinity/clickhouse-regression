import socket
import urllib.error

from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle.alloc_fault import classify_armed_exception
from cas.soak_tests.steps.http import QueryError


def _query_error(body):
    return QueryError("HttpNode(x:1)", 500, body, "INSERT INTO s42_alloc")


@TestScenario
@Name("injected allocation error")
def injected_allocation_error(self):
    body = "Code: 241. DB::Exception: Query memory tracker: fault injected. (MEMORY_LIMIT_EXCEEDED)"
    assert classify_armed_exception(_query_error(body)) == "injected", error()


@TestScenario
@Name("retry later stays retry later")
def retry_later_stays_retry_later(self):
    body = "Code: 210. DB::Exception: CAS write could not be committed (x); retrying later"
    assert classify_armed_exception(_query_error(body)) == "retry_later", error()


@TestScenario
@Name("mount lease drop stays a lease failure")
def mount_lease_drop_stays_a_lease_failure(self):
    body = "Code: 210. DB::Exception: mount lease not held"
    assert classify_armed_exception(_query_error(body)) == "lease", error()


@TestScenario
@Name("connection reset while the fault is armed is transport")
def connection_reset_is_transport(self):
    err = urllib.error.URLError(ConnectionResetError(104, "Connection reset by peer"))
    assert classify_armed_exception(err) == "transport", error()
    assert classify_armed_exception(TimeoutError("timed out")) == "transport", error()
    assert classify_armed_exception(socket.timeout("timed out")) == "transport", error()


@TestScenario
@Name("code 71 delivering the fault is transport")
def code_71_is_transport(self):
    body = "Code: 71. DB::Exception: Write buffer has been finalized. (CANNOT_WRITE_AFTER_END_OF_BUFFER)"
    assert classify_armed_exception(_query_error(body)) == "transport", error()


@TestScenario
@Name("a real server exception stays other")
def real_server_exception_stays_other(self):
    body = (
        "Code: 107. DB::Exception: live ref names manifest at soak_pool/cas/manifests/x "
        "but its object is missing. (FILE_DOESNT_EXIST)"
    )
    assert classify_armed_exception(_query_error(body)) == "other", error()


@TestFeature
@Name("alloc fault")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
