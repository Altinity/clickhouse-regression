"""How an armed allocation-fault workload classifies a failed statement.

The fault aborts the query with Code 241. The HTTP client often sees the
connection die instead, because the server closes the response while writing
that exception (Code 71, reset, or a read timeout). Those deaths are the
same fault. A ClickHouse exception with any other code is still a failure.
"""

from cas.soak_tests.oracle.lease import is_mount_lease_drop
from cas.soak_tests.steps.http import QueryError, is_socket_timeout, is_transport_error

_INJECTED = ("fault injected", "MEMORY_LIMIT_EXCEEDED", "Code: 241")
_RETRY_LATER = ("could not be committed", "retrying later")
# The server logs this when it cannot finish writing the fault exception.
_RESPONSE_CLOSED = ("Code: 71", "CANNOT_WRITE_AFTER_END_OF_BUFFER")


def classify_armed_exception(exc) -> str:
    """Return injected, retry_later, lease, transport, or other."""
    body = str(exc)
    if any(needle in body for needle in _INJECTED):
        return "injected"
    if any(needle in body for needle in _RETRY_LATER):
        return "retry_later"
    if is_mount_lease_drop(body):
        return "lease"
    if _response_closed_under_fault(exc, body):
        return "transport"
    return "other"


def _response_closed_under_fault(exc, body: str) -> bool:
    if isinstance(exc, QueryError):
        return any(needle in body for needle in _RESPONSE_CLOSED)
    if is_transport_error(exc) or is_socket_timeout(exc):
        return True
    return type(exc).__name__ in ("IncompleteRead", "BadStatusLine")
