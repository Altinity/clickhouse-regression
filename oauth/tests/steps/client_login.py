"""Step helpers for the ``clickhouse-client --login`` OAuth flow.

These helpers drive the **client-side** OAuth surface added by
Altinity/ClickHouse PR #1606 (and the follow-up issues #1696 / #1697 /
#1698) — i.e. invocations of ``clickhouse-client --login=...`` along with
the ``--oauth-credentials`` flag, the ``~/.clickhouse-client/config.xml``
``connections_credentials`` block, and the on-disk
``oauth_cache.json`` refresh-token cache.

Tests run inside the Keycloak env which already provides:

* a ``clickhouse1`` node with the patched ``clickhouse-client`` binary
* a Keycloak instance reachable from the cluster network as
  ``http://keycloak:8080`` with realm ``grafana``, client
  ``grafana-client`` and a user ``demo``/``demo``

The helpers run ``clickhouse-client`` **inside the clickhouse1
container** (the bash-tools image does not ship the binary). The
client's ``$HOME`` lands at ``/root`` in that container, so
``/root/.clickhouse-client/`` is where the credentials and cache files
land.

Why so much explicit ``timeout=`` and explicit returncode handling: the
``--login=*`` paths can hang waiting for a browser callback or for the
device-code polling loop to time out. Every helper that invokes the
client therefore drives it with ``--query`` (so the client exits as
soon as auth is resolved) and a hard wall-clock cap.
"""

import json
import re
import shlex
import time
from pathlib import Path

from helpers.common import getuid
from testflows.core import *


CLIENT_HOME = "/root"
"""Where ``HOME`` resolves inside the clickhouse server containers; the
client looks for credentials and cache files relative to it."""

CLIENT_CONFIG_DIR = f"{CLIENT_HOME}/.clickhouse-client"
DEFAULT_CREDS_PATH = f"{CLIENT_CONFIG_DIR}/oauth_client.json"
DEFAULT_CACHE_PATH = f"{CLIENT_CONFIG_DIR}/oauth_cache.json"
DEFAULT_CONFIG_PATH = f"{CLIENT_CONFIG_DIR}/config.xml"

DEVICE_FLOW_BG_LOG = "/tmp/ch_oauth_device_flow.log"
DEVICE_FLOW_BG_PID = "/tmp/ch_oauth_device_flow.pid"


def extract_device_user_code_from_client_output(text):
    """Extract RFC 8628-shaped user code from clickhouse-client stderr/stdout."""

    m = re.search(r"\b([A-Z2-7]{4}-[A-Z2-7]{4})\b", text, flags=re.IGNORECASE)
    if m:
        return m.group(1).upper()
    m = re.search(r"\b([A-Z2-7]{8})\b", text, flags=re.IGNORECASE)
    if m:
        s = m.group(1).upper()
        return f"{s[:4]}-{s[4:]}"
    return None


def _shell_quote(value):
    """Quote ``value`` for safe inclusion in a shell command.

    ``shlex.quote`` handles every special character but produces single
    quotes that must round-trip through one more layer of quoting in the
    ``docker exec sh -c '...'`` chain. We wrap the call so callers can
    pass arbitrary strings (including JSON blobs and CLI args) without
    worrying about escaping rules.
    """

    return shlex.quote(value)


@TestStep(Given)
def reset_client_state(self, node=None):
    """Wipe ``~/.clickhouse-client`` and any saved OAuth artefacts.

    Used as a Given/Finally guard so each scenario starts from a
    consistent state — the cache file from a previous test must never
    influence the next one because that's exactly the persistence bug
    M1 of the audit fixed.
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

    PR #1606 expects ``--oauth-credentials`` to point at exactly this
    shape (``{"installed": {...}}`` or ``{"web": {...}}``). Tests use
    this helper to materialise the file inside the container before
    invoking the client.

    ``raw_contents`` overrides every other argument and writes the
    string verbatim — used by the "malformed JSON" / "missing required
    field" scenarios.
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

    Thin wrapper around :func:`write_oauth_credentials_file` that fills
    in the four fields every device-flow scenario in the suite was
    re-typing verbatim. Kept as a plain function (rather than a
    ``@TestStep``) so callers can keep their own ``with And("…"):``
    framing intact, matching the pre-existing convention used by
    helpers like ``_complete_device_login_via_background``.
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
    """Write ``~/.clickhouse-client/config.xml``.

    Used to drive the ``connections_credentials`` /
    ``--connection`` paths exercised by PRs #1696 and #1698.
    """

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

    ``mapping`` is the cache dict (``{cache_key_hex: refresh_token}``).
    ``raw_contents`` is a literal string (used to test parse-resilience
    against corrupted caches). ``mode`` controls the on-disk
    permissions so we can verify the client refuses to ingest a
    world-readable cache (a common audit ask).
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

    result = node.command(
        command=f"cat {_shell_quote(path)} 2>/dev/null || true",
        no_checks=True,
    )
    raw = result.output.strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _run_clickhouse_client_core(node, args, query, timeout, expect_error):
    """Shared implementation behind ``run_clickhouse_client[_no_host]``.

    Builds the ``timeout(1) clickhouse-client <args>`` command, runs it
    via ``node.command(no_checks=True)`` so the helper owns the
    exit-code policy, parses the trailing ``__EXIT__=<rc>`` marker, and
    enforces ``expect_error``.

    Kept as a plain function (no ``@TestStep`` decorator) so it can be
    called from inside the public ``@TestStep(Then)`` wrappers without
    re-entering the step machinery.
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

    ``args`` is a list of additional CLI flags (everything except
    ``-q``/``--query``, which the helper appends from the ``query``
    kwarg). Callers that want the ``--host clickhouse1`` shorthand
    must add it to ``args`` themselves — the helper does not inject
    it.

    The wall-clock ``timeout`` exists because ``--login=browser`` blocks
    on a callback that will never come in CI. Anything still running
    at ``timeout`` is killed with SIGTERM and the helper returns the
    output captured up to that point.

    ``expect_error`` flips the assertion: by default the helper asserts
    ``exitcode == 0``. When the test is asserting "this command must
    fail with a specific message", set ``expect_error=True`` and check
    the returned ``output`` instead.

    Use :func:`run_clickhouse_client_no_host` instead when the scenario
    must exercise the PR #1696 / ClickHouse #103603 codepath where
    ``hosts_and_ports`` is intentionally empty — the two helpers only
    differ in their default ``expect_error`` value (this one defaults
    to ``False`` because most callers expect a clean round-trip).
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
    """Variant of :func:`run_clickhouse_client` for the PR #1696 repro.

    The crash from ClickHouse #103603 only happens when
    ``hosts_and_ports`` is left empty by the ``initialise()`` pass —
    i.e. the host comes from ``connections_credentials`` or from the
    bare ``<host>`` element in the config file rather than from
    ``--host`` on the CLI. Callers therefore omit ``--host`` from
    ``args``.

    Mechanically identical to :func:`run_clickhouse_client`; the only
    difference is the default of ``expect_error=True`` because most
    callers are pinning a specific failure mode (arg-parse error,
    auth-redirect timeout, etc.) rather than expecting a clean
    ``SELECT 1`` round-trip.
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

    Direct evidence for ClickHouse #103603 / PR #1696. The libc++
    hardening trap (`front() called on an empty vector`) prints that
    exact phrase before raising SIGABRT, so we grep for both the
    message and the conventional "Received signal 6 / 11" lines.

    `timeout(1)` exits 124 on wall-clock kill and 137/143 when it has
    to SIGKILL the child — those are NOT the abort signals we're
    looking for and must not be flagged here.
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

    Starts ``clickhouse-client --login=device`` in the background,
    polls the log for the RFC 8628 user code, approves it through the
    Keycloak admin API, waits for the client to finish, and asserts a
    clean ``exit code 0``. Used by every refresh-token-cache scenario
    that needs a populated cache to test against.

    ``args`` defaults to the standard ``--host clickhouse1
    --login=device --oauth-credentials <DEFAULT_CREDS_PATH>``
    invocation. Override only when a scenario needs a non-default
    host / credentials path / extra flag — every existing caller
    relies on the default.

    Caller still owns ``reset_client_state()`` /
    ``write_keycloak_device_credentials()`` (these are scenario-level
    Givens) and the ``Finally`` that kills any leftover background
    client.
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

    user_code = None
    for _ in range(user_code_poll_iters):
        log_snippet = read_clickhouse_oauth_background_log()
        user_code = extract_device_user_code_from_client_output(log_snippet)
        if user_code:
            break
        time.sleep(1)
    assert user_code is not None, (
        "Timed out waiting for device user_code:\n"
        f"{read_clickhouse_oauth_background_log()}"
    )

    approve_keycloak_device_user_code_via_bash_tools(user_code=user_code)
    wait_clickhouse_oauth_background_finished(timeout_sec=finish_timeout_sec)

    full_log = read_clickhouse_oauth_background_log()
    ec = parse_background_client_exit_code(full_log)
    assert (
        ec == 0
    ), f"Expected exit 0 after device approval, got {ec!r}:\n---\n{full_log}\n---"


@TestStep(Given)
def create_directory(self, path, node=None):
    """Create ``path`` (with parents) inside ``node``.

    Thin wrapper around ``mkdir -p`` so scenarios don't reach into
    ``self.context.node.command(...)`` directly. Idempotent — calling
    twice is safe.
    """

    if node is None:
        node = self.context.node

    node.command(command=f"mkdir -p {_shell_quote(path)}")


@TestStep(Given)
def set_immutable(self, path, node=None):
    """Mark ``path`` as immutable via ``chattr +i``.

    ``chmod 555`` is insufficient when the binary under test runs as
    root (``chmod`` does not stop root); ``chattr +i`` does. Used by
    the "read-only ~/.clickhouse-client" cache-write scenarios.

    Always pair with :func:`unset_immutable` in a ``Finally`` block —
    otherwise the next scenario inherits a directory the cleanup
    helpers cannot wipe.
    """

    if node is None:
        node = self.context.node

    node.command(command=f"chattr +i {_shell_quote(path)}")


@TestStep(Finally)
def unset_immutable(self, path, node=None):
    """Clear the immutable bit set by :func:`set_immutable`.

    Uses ``no_checks`` so a stray cleanup on a path that no longer
    exists (or was never marked immutable) doesn't propagate a
    spurious failure out of ``Finally``.
    """

    if node is None:
        node = self.context.node

    node.command(command=f"chattr -i {_shell_quote(path)}", no_checks=True)


@TestStep(Then)
def wait_for_http_response(self, url, max_wait=15, poll_interval=1, node=None):
    """Poll ``curl -sSI <url>`` until it returns an HTTP response or
    ``max_wait`` elapses; return the final response output.

    Replaces the ``sleep N; curl …`` antipattern in the loopback-
    security scenarios, where a fixed sleep races against the
    background ``clickhouse-client`` finding a free port and binding
    its callback HTTP server. The poll loop terminates on the first
    ``HTTP/`` header line, so the scenario observes the *real* time
    to bind rather than a worst-case-padded guess.

    On timeout the helper returns whatever the last curl invocation
    produced (often an empty string when nothing is listening yet)
    — callers should assert ``"HTTP/" in result`` to fail loudly on
    timeout instead of silently accepting a no-bind.
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

    Used by the loopback-callback security probes that need to look at
    the response headers (e.g. checking the ``Location`` header for
    leaked OAuth ``state``). Tolerates connection failures with
    ``|| true`` so a not-yet-listening server surfaces as empty output
    rather than aborting the scenario; callers are expected to assert
    on what they actually need ("HTTP/" present, specific header
    absent, etc.).
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
    """Start a Python HTTP mock (e.g. for OIDC discovery) on ``node``.

    ``script`` is the full Python source to write into the container
    and run under ``nohup``. ``pid_file`` is where the PID lands —
    callers pass the same path to :func:`stop_mock_oidc_server` to
    tear it down. ``log_file`` defaults to a sibling of ``pid_file``
    if not supplied.

    Defaults to the bash-tools node because mock servers in this
    suite live on a separate container so the clickhouse-server
    sandbox stays clean.
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
    """SIGTERM the mock OIDC server started by :func:`start_mock_oidc_server`.

    Best-effort — runs with ``no_checks`` so a missing PID file (mock
    never started) does not propagate out of ``Finally``.
    """

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
    """Start the oversized OIDC discovery mock on ``node`` and return its pid_file.

    Loads the implementation from the sibling module
    ``mock_oidc_oversized.py`` so the test files don't carry a
    multi-line HTTP-server blob inline — same idiom as
    :func:`approve_keycloak_device_user_code_via_bash_tools` /
    ``keycloak_device_flow.py``.

    Returns the on-disk pid_file path so scenarios can pass it to
    :func:`stop_mock_oidc_server` in their ``Finally`` block. ``port``
    defaults to 18080 (matches the URLs the existing scenarios build).
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

    Idempotent — safe to call when the scope is already assigned.
    Implementation lives in the sibling module
    ``keycloak_optional_scope.py`` (loaded as text and executed
    inside the bash-tools container — same idiom as
    ``keycloak_device_flow.py`` and ``mock_oidc_oversized.py``) so
    the step file stays free of an inline Python blob driving the
    Keycloak admin REST API.
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
    """Obtain an access token from Keycloak via the password / refresh-token grant.

    A thin wrapper around the same direct-access-grant flow used by
    ``oauth.tests.steps.keycloak_realm.get_oauth_token`` but allowing
    the caller to override the grant type (e.g. ``refresh_token``)
    without going through bash-tools, since these tests run from a
    clickhouse-server container.

    Returns the parsed JSON response; raises with a descriptive error
    when Keycloak refuses (so failed setups don't surface as opaque
    KeyErrors deep in the scenario).
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

    return response
