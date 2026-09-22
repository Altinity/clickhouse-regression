"""Thread-safe HTTP client for concurrent soak ops.

TestFlows ``node.query`` shares per-thread bash sessions and ``current()``
context, which is not usable from a ``ThreadPoolExecutor``. The original
harness POSTs SQL over HTTP; this is the same path, rewritten here so we
never import ``cas.soak``.
"""

import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request

ABORTED_CODE = 236
NETWORK_ERROR_CODE = 210
TABLE_IS_READ_ONLY_CODE = 242
KEEPER_EXCEPTION_CODE = 999
S3_ERROR_CODE = 499
NODE_DOWN_CODES = (394, 209, 210, 735)
_S3_TRANSIENT_FLAVORS = (
    "Timeout",
    "Connection refused",
    "Connection reset",
    "Broken pipe",
    "DNS error",
)
_S3_CORRECTNESS_MARKERS = (
    "NoSuchKey",
    "NO_SUCH_KEY",
    "AccessDenied",
    "ACCESS_DENIED",
    "PreconditionFailed",
    "LOGICAL_ERROR",
    "CORRUPTED_DATA",
)

# Host-mapped HTTP ports from soak_tests_env/docker-compose.yml.
_DEFAULT_PORTS = {
    "clickhouse1": 8123,
    "clickhouse2": 8124,
}


class QueryError(RuntimeError):
    """ClickHouse HTTP query failed; body carries the server exception text."""

    def __init__(self, node, code, body, sql):
        self.code = code
        self.body = body
        self.sql = sql
        snippet = sql if len(sql) <= 200 else sql[:200] + f"...({len(sql) - 200} more chars)"
        super().__init__(f"{node} HTTP {code}: {(body or '').strip()} | sql={snippet}")

    @property
    def is_aborted(self) -> bool:
        b = self.body or ""
        return f"Code: {ABORTED_CODE}" in b or "ABORTED" in b

    @property
    def is_readonly(self) -> bool:
        b = self.body or ""
        return f"Code: {TABLE_IS_READ_ONLY_CODE}" in b or "TABLE_IS_READ_ONLY" in b

    @property
    def is_keeper_transient(self) -> bool:
        b = self.body or ""
        if f"Code: {KEEPER_EXCEPTION_CODE}" not in b:
            return False
        return (
            "Session expired" in b
            or "Operation timeout" in b
            or "Coordination error" in b
        )

    is_keeper_session_expired = is_keeper_transient

    @property
    def is_s3_transient(self) -> bool:
        b = self.body or ""
        if f"Code: {S3_ERROR_CODE}" not in b and "S3_ERROR" not in b:
            return False
        if any(marker in b for marker in _S3_CORRECTNESS_MARKERS):
            return False
        return any(flavor in b for flavor in _S3_TRANSIENT_FLAVORS)

    @property
    def is_node_down(self) -> bool:
        b = self.body or ""
        if self.is_aborted:
            return False
        return any(f"Code: {c}." in b for c in NODE_DOWN_CODES)

    @property
    def is_mount_fenced(self) -> bool:
        b = self.body or ""
        if self.is_aborted:
            return (
                "mount lost" in b
                or "lease expired" in b
                or "refusing to mutate ref shard" in b
            )
        return f"Code: {NETWORK_ERROR_CODE}." in b and "mount lease not held" in b


def is_timeout(exc: BaseException) -> bool:
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return True
    if isinstance(exc, urllib.error.URLError):
        reason = getattr(exc, "reason", None)
        if isinstance(reason, (TimeoutError, socket.timeout)):
            return True
        return "timed out" in str(exc).lower()
    return False


class HttpNode:
    def __init__(self, host, port, timeout=300.0, database="default", name=None):
        self.host = host
        self.port = int(port)
        self.timeout = timeout
        self.database = database
        self.name = name or f"{host}:{port}"
        self.container = self.name

    @property
    def url(self):
        return f"http://{self.host}:{self.port}/"

    def __repr__(self):
        return f"HttpNode({self.host}:{self.port})"

    def query(self, sql, timeout=None, settings=None):
        params = {"database": self.database}
        if settings:
            for k, v in settings.items():
                params[str(k)] = str(v)
        url = self.url + "?" + urllib.parse.urlencode(params)
        data = sql.encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout or self.timeout) as resp:
                return resp.read().decode("utf-8").rstrip("\n")
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "replace")
            except Exception:
                pass
            raise QueryError(self, e.code, body, sql) from e

    def command(self, sql, timeout=None, settings=None):
        self.query(sql, timeout=timeout, settings=settings)

    def scalar(self, sql, timeout=None):
        txt = self.query(sql, timeout=timeout).strip()
        return txt.splitlines()[0] if txt else ""

    def ping(self, timeout=2.0):
        req = urllib.request.Request(f"http://{self.host}:{self.port}/ping", method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status == 200
        except Exception:
            return False


def is_transport_error(exc: BaseException) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        return False
    if isinstance(exc, QueryError):
        return False
    if isinstance(exc, urllib.error.URLError):
        reason = getattr(exc, "reason", None)
        if isinstance(reason, BaseException):
            return is_transport_error(reason)
        return True
    if isinstance(exc, (ConnectionError, socket.timeout, TimeoutError)):
        return True
    if isinstance(exc, OSError):
        return True
    return False


def is_node_down(exc: BaseException) -> bool:
    if is_transport_error(exc):
        return True
    if isinstance(exc, QueryError):
        return exc.is_node_down
    return False


def is_readonly(exc: BaseException) -> bool:
    return isinstance(exc, QueryError) and exc.is_readonly


def is_mount_fenced(exc: BaseException) -> bool:
    return isinstance(exc, QueryError) and exc.is_mount_fenced


def is_keeper_transient(exc: BaseException) -> bool:
    return isinstance(exc, QueryError) and exc.is_keeper_transient


def is_s3_transient(exc: BaseException) -> bool:
    return isinstance(exc, QueryError) and exc.is_s3_transient


def is_aborted(exc: BaseException) -> bool:
    return isinstance(exc, QueryError) and exc.is_aborted


def is_socket_timeout(exc: BaseException) -> bool:
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return True
    if isinstance(exc, urllib.error.URLError) and not isinstance(
        exc, urllib.error.HTTPError
    ):
        reason = getattr(exc, "reason", None)
        if isinstance(reason, BaseException):
            return is_socket_timeout(reason)
    return False


def retry_on_transport(
    fn,
    *,
    attempts,
    backoff_s=0.5,
    max_backoff_s=8.0,
    on_retry=None,
    sleep_fn=time.sleep,
    retry_timeouts=True,
):
    last = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as e:
            if is_socket_timeout(e) and not retry_timeouts:
                raise
            if not (
                is_node_down(e)
                or is_readonly(e)
                or is_mount_fenced(e)
                or is_keeper_transient(e)
                or is_s3_transient(e)
                or is_aborted(e)
            ):
                raise
            last = e
            if attempt < attempts:
                if on_retry is not None:
                    on_retry(attempt, e)
                sleep_fn(min(max_backoff_s, backoff_s * (2 ** (attempt - 1))))
    raise last


def retry_on_aborted(fn, *, attempts=6, backoff_s=0.05, on_retry=None):
    """Retry an INSERT on retryable ABORTED (code 236). Mount-fence ABORTED is not retried."""
    last = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except QueryError as e:
            if not e.is_aborted or e.is_mount_fenced:
                raise
            last = e
            if attempt < attempts:
                if on_retry is not None:
                    on_retry(attempt, e)
                if backoff_s:
                    time.sleep(backoff_s * attempt)
    raise last


def http_nodes_from_context(nodes):
    """Map TestFlows clickhouse1/clickhouse2 nodes to host-mapped HTTP endpoints."""
    out = []
    for i, node in enumerate(nodes):
        name = getattr(node, "name", None) or f"clickhouse{i + 1}"
        default_port = _DEFAULT_PORTS.get(name, 8123 + i)
        host = os.environ.get(f"CA_SOAK_TESTS_NODE{i + 1}_HOST", "localhost")
        port = int(os.environ.get(f"CA_SOAK_TESTS_NODE{i + 1}_PORT", default_port))
        out.append(HttpNode(host, port, name=name))
    return out
