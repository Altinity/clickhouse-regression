"""Step helpers for the ``clickhouse-client --login`` OAuth flow.

These helpers drive client-side OAuth: ``--login=device|browser``,
``--oauth-credentials``, ``connections_credentials``, and the
on-disk ``oauth_cache.json`` refresh-token cache.

Helpers run ``clickhouse-client`` inside the ClickHouse container
(not bash-tools). Every invocation uses ``--query`` and a wall-clock
timeout to prevent hangs from browser callbacks or device-code polling.
"""

import json
import re
import shlex
import time
from pathlib import Path

from helpers.common import getuid
from testflows.core import *

from oauth.tests.steps.clikhouse import without_command_logging
from oauth.tests.steps.provider_protocol import mask_secret, mask_token_response


CLIENT_HOME = "/root"
"""HOME inside the ClickHouse server containers."""

CLIENT_CONFIG_DIR = f"{CLIENT_HOME}/.clickhouse-client"
DEFAULT_CREDS_PATH = f"{CLIENT_CONFIG_DIR}/oauth_client.json"
DEFAULT_CACHE_PATH = f"{CLIENT_CONFIG_DIR}/oauth_cache.json"
DEFAULT_CONFIG_PATH = f"{CLIENT_CONFIG_DIR}/config.xml"

DEVICE_FLOW_BG_LOG = "/tmp/ch_oauth_device_flow.log"
DEVICE_FLOW_BG_PID = "/tmp/ch_oauth_device_flow.pid"


# Anchored pattern for RFC 8628 user_code next to known label keywords.
_DEVICE_USER_CODE_ANCHOR_RE = re.compile(
    r"(?:user[_\- ]?code|verification_uri_complete|verification[_\- ]?url)"
    r"[^A-Za-z0-9]{0,40}"
    r"([A-Z0-9]{4}-[A-Z0-9]{4})",
    flags=re.IGNORECASE,
)

# Fallback: bare XXXX-XXXX pattern (the dash disambiguates from random substrings).
_DEVICE_USER_CODE_DASHED_RE = re.compile(
    r"\b([A-Z0-9]{4}-[A-Z0-9]{4})\b", flags=re.IGNORECASE
)


def extract_device_user_code_from_client_output(text):
    """Extract an RFC 8628 user code from ``clickhouse-client`` output.

    Two-stage match: first an anchored search keyed on marker words
    (``user_code``, ``verification_uri_complete``), then a fallback to
    the bare ``XXXX-XXXX`` dashed pattern.
    """

    m = _DEVICE_USER_CODE_ANCHOR_RE.search(text)
    if m:
        return m.group(1).upper()
    m = _DEVICE_USER_CODE_DASHED_RE.search(text)
    if m:
        return m.group(1).upper()
    return None


# Markers indicating the background client has terminally failed.
_DEVICE_FLOW_TERMINAL_MARKERS = (
    "__EXIT__=",
    "AUTHENTICATION_FAILED",
    "Stack trace:",
)
_DEVICE_FLOW_EXCEPTION_RE = re.compile(r"\bCode:\s*\d+\.\s*DB::Exception")


def device_flow_terminal_failure_reason(text):
    """Return a failure reason if the device flow has terminally failed, or ``None``."""

    for marker in _DEVICE_FLOW_TERMINAL_MARKERS:
        if marker in text:
            return marker
    m = _DEVICE_FLOW_EXCEPTION_RE.search(text)
    if m:
        return m.group(0)
    return None


def _shell_quote(value):
    """Quote ``value`` for safe inclusion in a shell command."""

    return shlex.quote(value)


@TestStep(Given)
def reset_client_state(self, node=None):
    """Wipe ``~/.clickhouse-client`` and any saved OAuth artefacts.

    Ensures each scenario starts from a consistent state.
    """

    if node is None:
        node = self.context.node

    node.command(command=f"rm -rf {CLIENT_CONFIG_DIR}")
    node.command(command=f"mkdir -p {CLIENT_CONFIG_DIR}")
    node.command(command=f"chmod 700 {CLIENT_CONFIG_DIR}")


@TestStep(Given)
def write_oauth_credentials_file(
    self,
    client_id="grafana-client",
    client_secret="grafana-secret",
    auth_uri="http://keycloak:8080/realms/grafana/protocol/openid-connect/auth",
    token_uri="http://keycloak:8080/realms/grafana/protocol/openid-connect/token",
    device_authorization_uri="http://keycloak:8080/realms/grafana/protocol/openid-connect/auth/device",
    issuer=None,
    redirect_uris=None,
    top_level_key="installed",
    extra=None,
    path=DEFAULT_CREDS_PATH,
    raw_contents=None,
    node=None,
):
    """Write a Google-Cloud-Console-shaped OAuth credentials JSON file.

    Expects the ``{"installed": {...}}`` or ``{"web": {...}}`` shape.
    ``raw_contents`` overrides all other arguments and writes verbatim.
    """

    if node is None:
        node = self.context.node

    if raw_contents is None:
        inner = {
            "client_id": client_id,
            "auth_uri": auth_uri,
            "token_uri": token_uri,
        }
        if client_secret is not None:
            inner["client_secret"] = client_secret
        if device_authorization_uri is not None:
            inner["device_authorization_uri"] = device_authorization_uri
        if issuer is not None:
            inner["issuer"] = issuer
        if redirect_uris is not None:
            inner["redirect_uris"] = redirect_uris
        if extra:
            inner.update(extra)

        contents = json.dumps({top_level_key: inner})
    else:
        contents = raw_contents

    node.command(command=f"mkdir -p {CLIENT_CONFIG_DIR}")
    node.command(
        command=(
            f"cat > {_shell_quote(path)} <<'__OAUTH_CREDS_EOF__'\n"
            f"{contents}\n"
            f"__OAUTH_CREDS_EOF__"
        )
    )
    node.command(command=f"chmod 600 {_shell_quote(path)}")


def write_keycloak_device_credentials(
    client_id="grafana-client",
    client_secret="grafana-secret",
    token_uri="http://keycloak:8080/realms/grafana/protocol/openid-connect/token",
    device_authorization_uri=(
        "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth/device"
    ),
    node=None,
):
    """Write the default Keycloak-grafana device-flow credentials file.

    Plain function (not a ``@TestStep``) — callers provide their own
    ``with And("…"):`` framing.
    """

    write_oauth_credentials_file(
        client_id=client_id,
        client_secret=client_secret,
        token_uri=token_uri,
        device_authorization_uri=device_authorization_uri,
        node=node,
    )


@TestStep(Given)
def write_client_config_xml(self, contents, path=DEFAULT_CONFIG_PATH, node=None):
    """Write ``~/.clickhouse-client/config.xml`` inside the container."""

    if node is None:
        node = self.context.node

    node.command(command=f"mkdir -p {CLIENT_CONFIG_DIR}")
    node.command(
        command=(
            f"cat > {_shell_quote(path)} <<'__CH_CLIENT_CFG_EOF__'\n"
            f"{contents}\n"
            f"__CH_CLIENT_CFG_EOF__"
        )
    )


@TestStep(Given)
def write_oauth_cache(self, mapping=None, raw_contents=None, mode="600", node=None):
    """Pre-populate ``~/.clickhouse-client/oauth_cache.json``.

    ``mapping`` is the cache dict. ``raw_contents`` writes a literal string.
    ``mode`` controls on-disk permissions.
    """

    if node is None:
        node = self.context.node

    if raw_contents is None:
        contents = json.dumps(mapping or {})
    else:
        contents = raw_contents

    node.command(command=f"mkdir -p {CLIENT_CONFIG_DIR}")
    node.command(
        command=(
            f"cat > {DEFAULT_CACHE_PATH} <<'__OAUTH_CACHE_EOF__'\n"
            f"{contents}\n"
            f"__OAUTH_CACHE_EOF__"
        )
    )
    node.command(command=f"chmod {mode} {DEFAULT_CACHE_PATH}")


@TestStep(Given)
def approve_keycloak_device_user_code_via_bash_tools(
    self,
    user_code,
    username=None,
    password=None,
    node=None,
):
    """Complete Keycloak device authorization for ``user_code`` (runs on bash-tools)."""

    if node is None:
        node = self.context.bash_tools
    if username is None:
        username = self.context.username
    if password is None:
        password = self.context.password

    ku = self.context.keycloak_url
    realm = self.context.realm_name
    src_path = Path(__file__).resolve().parent / "keycloak_device_flow.py"
    src = src_path.read_text(encoding="utf-8")
    tail = (
        "\n\napprove_keycloak_device_user_code("
        f"{ku!r}, {realm!r}, {user_code!r}, {username!r}, {password!r})\n"
    )
    bundle = src + tail
    tag = f"_OAuthKeycloakDevice_{getuid()}_"
    node.command(command=f"python3 <<'{tag}'\n{bundle}\n{tag}")


@TestStep(When)
def start_clickhouse_oauth_client_background(
    self,
    args,
    query,
    log_path=DEVICE_FLOW_BG_LOG,
    pid_path=DEVICE_FLOW_BG_PID,
    wall_timeout=120,
    node=None,
):
    """Run ``clickhouse-client`` in the background inside the ClickHouse container."""

    if node is None:
        node = self.context.node

    cmd_parts = ["clickhouse-client"]
    cmd_parts.extend(args)
    if query is not None:
        cmd_parts.extend(["--query", query])

    inner = " ".join(_shell_quote(p) for p in cmd_parts)
    log_q = _shell_quote(log_path)
    pid_q = _shell_quote(pid_path)
    wrapped_shell = (
        f"timeout {wall_timeout} {inner} >{log_q} 2>&1; " f"echo __EXIT__=$? >>{log_q}"
    )
    node.command(command=f"rm -f {log_q} {pid_q}")
    node.command(
        command=(
            f"nohup sh -c {_shell_quote(wrapped_shell)} >/dev/null 2>&1 & "
            f"echo $! > {pid_q}"
        )
    )


def parse_background_client_exit_code(log_text):
    """Return exit code from trailing ``__EXIT__=`` line or ``None``."""

    for line in log_text.strip().splitlines()[::-1]:
        if line.startswith("__EXIT__="):
            try:
                return int(line.split("=", 1)[1])
            except ValueError:
                return None
    return None


@TestStep(Then)
def read_clickhouse_oauth_background_log(self, log_path=DEVICE_FLOW_BG_LOG, node=None):
    """Return the current contents of a background clickhouse-client log file."""

    if node is None:
        node = self.context.node

    result = node.command(
        command=f"cat {_shell_quote(log_path)} 2>/dev/null || true",
        no_checks=True,
    )
    return result.output


@TestStep(When)
def wait_for_device_user_code(
    self,
    poll_iters=50,
    poll_interval_sec=1,
    log_path=DEVICE_FLOW_BG_LOG,
    node=None,
):
    """Poll the background client log until a user code appears.

    Returns the extracted user code string. Fails early if the client
    has exited or logged a ClickHouse exception.
    """

    if node is None:
        node = self.context.node

    last_log = ""
    for _ in range(poll_iters):
        last_log = node.command(
            command=f"cat {_shell_quote(log_path)} 2>/dev/null || true",
            no_checks=True,
        ).output

        user_code = extract_device_user_code_from_client_output(last_log)
        if user_code:
            return user_code

        reason = device_flow_terminal_failure_reason(last_log)
        assert reason is None, (
            "Background clickhouse-client failed before emitting a device "
            f"user_code (saw {reason!r} in the log). This usually means the "
            "device-authorization request itself was rejected by the IdP. "
            f"Captured log:\n---\n{last_log}\n---"
        )

        time.sleep(poll_interval_sec)

    raise AssertionError(
        f"Timed out after ~{poll_iters * poll_interval_sec}s waiting for a "
        "device user_code in clickhouse-client output. Captured log:\n"
        f"---\n{last_log}\n---"
    )


@TestStep(Then)
def wait_clickhouse_oauth_background_finished(
    self,
    pid_path=DEVICE_FLOW_BG_PID,
    timeout_sec=120,
    node=None,
):
    """Wait until the background ``clickhouse-client`` process exits."""

    if node is None:
        node = self.context.node

    for _ in range(timeout_sec):
        result = node.command(
            command=(
                f"if kill -0 $(cat {_shell_quote(pid_path)} 2>/dev/null) "
                f"2>/dev/null; then echo RUNNING; else echo DONE; fi"
            ),
            no_checks=True,
        )
        if "DONE" in result.output:
            return
        time.sleep(1)

    raise AssertionError(
        "Background clickhouse-client still running after "
        f"{timeout_sec}s (pid file {_shell_quote(pid_path)})"
    )


@TestStep(Finally)
def kill_clickhouse_oauth_background_if_alive(
    self, pid_path=DEVICE_FLOW_BG_PID, node=None
):
    """Best-effort SIGTERM for a background clickhouse-client PID."""

    if node is None:
        node = self.context.node

    node.command(
        command=(
            f"PID=$(cat {_shell_quote(pid_path)} 2>/dev/null); "
            f'if [ -n "$PID" ]; then '
            f'disown "$PID" 2>/dev/null || true; '
            f'kill "$PID" 2>/dev/null || true; '
            f"fi"
        ),
        no_checks=True,
    )


@TestStep(Then)
def read_oauth_cache(self, path=DEFAULT_CACHE_PATH, node=None):
    """Parse ``oauth_cache.json`` as a dict, or return ``None`` if missing/invalid."""

    if node is None:
        node = self.context.node

    # Suppress log forwarding: the cache file holds the refresh/access
    # tokens clickhouse-client persisted.
    with without_command_logging(node):
        result = node.command(
            command=f"cat {_shell_quote(path)} 2>/dev/null || true",
            no_checks=True,
        )
    raw = result.output.strip()
    if not raw:
        return None
    try:
        cache = json.loads(raw)
    except json.JSONDecodeError:
        return None

    # Mask any cached token values (at any nesting depth) so subsequent
    # references to them are redacted. Only token-named fields are masked
    # to avoid clobbering benign values (timestamps, URLs) in the log.
    def _mask_tokens(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ("access_token", "refresh_token", "id_token") and isinstance(
                    value, str
                ):
                    mask_secret(value)
                else:
                    _mask_tokens(value)
        elif isinstance(obj, list):
            for item in obj:
                _mask_tokens(item)

    _mask_tokens(cache)
    return cache


def _run_clickhouse_client_core(node, args, query, timeout, expect_error):
    """Shared core for ``run_clickhouse_client`` and ``_no_host`` variant.

    Runs ``timeout(1) clickhouse-client <args>``, parses the trailing
    ``__EXIT__=<rc>`` marker, and enforces ``expect_error``.
    Plain function (no ``@TestStep``).
    """

    cmd_parts = ["timeout", str(timeout), "clickhouse-client"]
    cmd_parts.extend(args)
    if query is not None:
        cmd_parts.extend(["--query", query])

    cmd = " ".join(_shell_quote(p) for p in cmd_parts) + " 2>&1; echo __EXIT__=$?"
    # no_checks so the helper itself owns the exit-code policy: scenarios
    # pin specific success/failure modes via ``expect_error`` and the parsed
    # trailing __EXIT__= line, rather than letting node.command() abort with
    # the default exitcode=0 expectation when (e.g.) arg-validation fails.
    result = node.command(command=cmd, no_checks=True)

    output = result.output
    exit_code = None
    for line in output.strip().splitlines()[::-1]:
        if line.startswith("__EXIT__="):
            try:
                exit_code = int(line.split("=", 1)[1])
            except ValueError:
                exit_code = None
            output = output.replace(line, "").rstrip()
            break

    if not expect_error:
        assert exit_code == 0, (
            f"clickhouse-client failed (exit={exit_code}) for args={args!r}\n"
            f"---\n{output}\n---"
        )

    return exit_code, output


@TestStep(Then)
def run_clickhouse_client(
    self,
    args,
    query=None,
    timeout=15,
    node=None,
    expect_error=False,
):
    """Run ``clickhouse-client`` inside ``node`` and return ``(exitcode, output)``.

    ``args`` is a list of CLI flags. ``timeout`` caps wall-clock time.
    ``expect_error=True`` skips the exit-code-zero assertion.
    """

    if node is None:
        node = self.context.node

    return _run_clickhouse_client_core(
        node=node,
        args=args,
        query=query,
        timeout=timeout,
        expect_error=expect_error,
    )


@TestStep(Then)
def run_clickhouse_client_no_host(
    self,
    args,
    query=None,
    timeout=15,
    node=None,
    expect_error=True,
):
    """Like ``run_clickhouse_client`` but defaults to ``expect_error=True``.

    Used when the scenario omits ``--host`` so the host comes from config
    rather than the CLI.
    """

    if node is None:
        node = self.context.node

    return _run_clickhouse_client_core(
        node=node,
        args=args,
        query=query,
        timeout=timeout,
        expect_error=expect_error,
    )


@TestStep(Then)
def assert_no_segfault(self, output, exit_code):
    """Assert the client did not abort via SIGSEGV/SIGABRT.

    Checks for libc++ hardening traps and signal markers in output.
    ``timeout(1)`` exit codes (124/137/143) are not flagged.
    """

    fatal_markers = [
        "libc++ Hardening assertion",
        "Received signal 6",
        "Received signal 11",
        "Received signal Segmentation",
        "Received signal Abort",
        "Stack trace:",
    ]
    for marker in fatal_markers:
        assert marker not in output, (
            f"clickhouse-client crashed (exit={exit_code}); "
            f"found marker {marker!r} in output:\n---\n{output}\n---"
        )


@TestStep(When)
def complete_keycloak_device_login_via_background(
    self,
    args=None,
    query="SELECT currentUser()",
    wall_timeout=120,
    user_code_poll_iters=50,
    finish_timeout_sec=90,
):
    """Drive one successful Keycloak device-flow login end-to-end.

    Starts the client in the background, polls for the user code,
    approves it via Keycloak, waits for completion, and asserts
    exit code 0. ``args`` defaults to the standard device-flow invocation.
    """

    if args is None:
        args = [
            "--host",
            "clickhouse1",
            "--login=device",
            "--oauth-credentials",
            DEFAULT_CREDS_PATH,
        ]

    start_clickhouse_oauth_client_background(
        args=args,
        query=query,
        wall_timeout=wall_timeout,
    )

    user_code = wait_for_device_user_code(poll_iters=user_code_poll_iters)

    approve_keycloak_device_user_code_via_bash_tools(user_code=user_code)
    wait_clickhouse_oauth_background_finished(timeout_sec=finish_timeout_sec)

    full_log = read_clickhouse_oauth_background_log()
    ec = parse_background_client_exit_code(full_log)
    assert (
        ec == 0
    ), f"Expected exit 0 after device approval, got {ec!r}:\n---\n{full_log}\n---"


@TestStep(Given)
def create_directory(self, path, node=None):
    """Create ``path`` (with parents) inside ``node``. Idempotent."""

    if node is None:
        node = self.context.node

    node.command(command=f"mkdir -p {_shell_quote(path)}")


@TestStep(Given)
def set_immutable(self, path, node=None):
    """Mark ``path`` as immutable via ``chattr +i``.

    Always pair with ``unset_immutable`` in a ``Finally`` block.
    """

    if node is None:
        node = self.context.node

    node.command(command=f"chattr +i {_shell_quote(path)}")


@TestStep(Finally)
def unset_immutable(self, path, node=None):
    """Clear the immutable bit set by ``set_immutable``."""

    if node is None:
        node = self.context.node

    node.command(command=f"chattr -i {_shell_quote(path)}", no_checks=True)


@TestStep(Then)
def wait_for_http_response(self, url, max_wait=15, poll_interval=1, node=None):
    """Poll ``curl -sSI <url>`` until an HTTP response arrives or ``max_wait`` elapses.

    Returns the final response output. Callers should assert ``"HTTP/" in result``
    to detect timeout.
    """

    if node is None:
        node = self.context.node

    deadline = time.time() + max_wait
    probe = ""
    while time.time() < deadline:
        result = node.command(
            command=f"(curl -sSI {_shell_quote(url)} || true) 2>&1",
            no_checks=True,
        )
        probe = result.output
        if "HTTP/" in probe:
            return probe
        time.sleep(poll_interval)
    return probe


@TestStep(Then)
def curl_head(self, url, node=None):
    """Run ``curl -sSI <url>`` inside ``node`` and return the raw response.

    Tolerates connection failures — returns empty output if nothing is listening.
    """

    if node is None:
        node = self.context.node

    result = node.command(
        command=f"(curl -sSI {_shell_quote(url)} || true) 2>&1",
        no_checks=True,
    )
    return result.output


@TestStep(Given)
def start_mock_oidc_server(
    self,
    script,
    pid_file,
    log_file=None,
    node=None,
):
    """Start a Python HTTP mock on ``node``.

    ``script`` is the Python source to run. ``pid_file`` is where the PID lands.
    Defaults to bash-tools node.
    """

    if node is None:
        node = self.context.bash_tools

    if log_file is None:
        log_file = pid_file.rsplit(".", 1)[0] + ".log"

    script_path = pid_file.rsplit(".", 1)[0] + ".py"
    tag = f"_MockOIDC_{getuid()}_"
    node.command(
        command=(
            f"cat > {_shell_quote(script_path)} <<'{tag}'\n"
            f"{script}\n"
            f"{tag}\n"
            f"nohup python3 -u {_shell_quote(script_path)} "
            f">{_shell_quote(log_file)} 2>&1 & "
            f"echo $! > {_shell_quote(pid_file)}"
        )
    )


@TestStep(Finally)
def stop_mock_oidc_server(self, pid_file, node=None):
    """SIGTERM the mock server started by ``start_mock_oidc_server``. Best-effort."""

    if node is None:
        node = self.context.bash_tools

    node.command(
        command=(
            f"PID=$(cat {_shell_quote(pid_file)} 2>/dev/null); "
            f'if [ -n "$PID" ]; then kill "$PID" 2>/dev/null || true; fi'
        ),
        no_checks=True,
    )


@TestStep(Given)
def start_oversized_oidc_discovery_mock(
    self,
    port=18080,
    padding_bytes=8_000_000,
    pid_file=None,
    node=None,
):
    """Start the oversized OIDC discovery mock and return its pid_file.

    Returns the pid_file path for use with ``stop_mock_oidc_server``.
    """

    if pid_file is None:
        pid_file = f"/tmp/mock_oidc_oversized_{port}.pid"

    src_path = Path(__file__).resolve().parent / "mock_oidc_oversized.py"
    src = src_path.read_text(encoding="utf-8")
    tail = f"\n\nrun_oversized_oidc_discovery_mock({int(port)}, {int(padding_bytes)})\n"
    start_mock_oidc_server(script=src + tail, pid_file=pid_file, node=node)
    return pid_file


@TestStep(Then)
def file_exists(self, path, node=None):
    """Return True if ``path`` exists inside ``node``."""

    if node is None:
        node = self.context.node

    # ``test -f`` exits 1 on missing file, which would trip the default
    # exitcode=0 assertion; ``no_checks`` defers the decision to the caller.
    result = node.command(
        command=f"test -f {_shell_quote(path)}; echo $?", no_checks=True
    )
    return result.output.strip().endswith("0")


@TestStep(Then)
def stat_file_mode(self, path, node=None):
    """Return the octal mode of ``path`` (e.g. ``"600"``) or ``None``."""

    if node is None:
        node = self.context.node

    # ``|| true`` tames stat's nonzero exit so the default exitcode=0 check
    # passes even on missing files; the caller treats empty output as "no file".
    result = node.command(
        command=f"stat -c %a {_shell_quote(path)} 2>/dev/null || true",
        no_checks=True,
    )
    out = result.output.strip()
    return out if out else None


@TestStep(Given)
def keycloak_enable_optional_scope(
    self,
    scope_name="offline_access",
    client_id="grafana-client",
    realm=None,
    keycloak_url=None,
    node=None,
):
    """Add ``scope_name`` to the optional client scopes of ``client_id``.

    Idempotent. Runs the implementation from ``keycloak_optional_scope.py``
    inside the bash-tools container.
    """

    if node is None:
        node = self.context.bash_tools
    if realm is None:
        realm = self.context.realm_name
    if keycloak_url is None:
        keycloak_url = self.context.keycloak_url

    src_path = Path(__file__).resolve().parent / "keycloak_optional_scope.py"
    src = src_path.read_text(encoding="utf-8")
    tail = (
        "\n\nenable_optional_scope_and_assign_role("
        f"{keycloak_url!r}, {realm!r}, {client_id!r}, {scope_name!r})\n"
    )
    tag = f"_KcScope_{getuid()}_"
    node.command(command=f"python3 <<'{tag}'\n{src}{tail}\n{tag}")


@TestStep(Given)
def get_keycloak_token_via_curl(
    self,
    username="demo",
    password="demo",
    client_id="grafana-client",
    client_secret="grafana-secret",
    realm=None,
    keycloak_url=None,
    node=None,
    grant_type="password",
    extra_data=None,
):
    """Obtain an access token from Keycloak via password or refresh-token grant.

    Allows overriding the grant type and adding extra form fields.
    Returns the parsed JSON response.
    """

    if node is None:
        node = self.context.bash_tools
    if realm is None:
        realm = self.context.realm_name
    if keycloak_url is None:
        keycloak_url = self.context.keycloak_url

    data_pairs = [
        f"--data-urlencode 'client_id={client_id}'",
        f"--data-urlencode 'grant_type={grant_type}'",
    ]
    if client_secret is not None:
        data_pairs.append(f"--data-urlencode 'client_secret={client_secret}'")

    if grant_type == "password":
        data_pairs.append(f"--data-urlencode 'username={username}'")
        data_pairs.append(f"--data-urlencode 'password={password}'")
        data_pairs.append("--data-urlencode 'scope=openid offline_access'")
    if extra_data:
        for key, value in extra_data.items():
            data_pairs.append(f"--data-urlencode '{key}={value}'")

    curl_command = (
        "curl -s --location "
        f"'{keycloak_url}/realms/{realm}/protocol/openid-connect/token' "
        "--header 'Content-Type: application/x-www-form-urlencoded' "
        + " ".join(data_pairs)
    )
    # Suppress log forwarding: the response body carries the tokens.
    with without_command_logging(node):
        result = node.command(command=curl_command)

    try:
        response = json.loads(result.output)
    except json.JSONDecodeError as exc:
        raise Exception(
            f"Failed to parse Keycloak token response: {exc}. "
            f"Raw: {result.output[:500]}"
        )

    if "error" in response:
        raise Exception(
            f"Keycloak token request failed: {response.get('error')} — "
            f"{response.get('error_description', '')}"
        )

    # Mask the tokens so any later reference to them (cache reads,
    # background-client logs) is redacted.
    return mask_token_response(response)
