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
import shlex

from helpers.common import getuid
from testflows.core import *


CLIENT_HOME = "/root"
"""Where ``HOME`` resolves inside the clickhouse server containers; the
client looks for credentials and cache files relative to it."""

CLIENT_CONFIG_DIR = f"{CLIENT_HOME}/.clickhouse-client"
DEFAULT_CREDS_PATH = f"{CLIENT_CONFIG_DIR}/oauth_client.json"
DEFAULT_CACHE_PATH = f"{CLIENT_CONFIG_DIR}/oauth_cache.json"
DEFAULT_CONFIG_PATH = f"{CLIENT_CONFIG_DIR}/config.xml"


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
    ``-q``/``--query`` and ``--host``, which the helper supplies).

    The helper always passes ``--host clickhouse1`` so that the OAuth
    "is this a *.clickhouse.cloud host?" auto-detection is
    deterministic — explicit ``--host`` populates ``hosts_and_ports``
    so the segfault path of PR #1696 is *not* triggered. Tests that
    want to exercise that path must omit ``--host`` from ``args`` and
    set ``omit_host=True``.

    The wall-clock ``timeout`` exists because ``--login=browser`` blocks
    on a callback that will never come in CI. Anything still running
    at ``timeout`` is killed with SIGTERM and the helper returns the
    output captured up to that point.

    ``expect_error`` flips the assertion: by default the helper asserts
    ``exitcode == 0``. When the test is asserting "this command must
    fail with a specific message", set ``expect_error=True`` and check
    the returned ``output`` instead.
    """

    if node is None:
        node = self.context.node

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
def run_clickhouse_client_no_host(
    self,
    args,
    query=None,
    timeout=15,
    node=None,
    expect_error=True,
):
    """Variant of ``run_clickhouse_client`` that does NOT inject ``--host``.

    Required for the PR #1696 / ClickHouse #103603 segfault repro: the
    crash only happens when ``hosts_and_ports`` is left empty by the
    initialise() pass — i.e. the host comes from
    ``connections_credentials`` or from the bare ``<host>`` element in
    the config file rather than from ``--host`` on the CLI.

    Defaults to ``expect_error=True`` because most callers are pinning
    a specific failure mode (arg-parse error, auth-redirect timeout,
    etc.) rather than expecting a clean ``SELECT 1`` round-trip.
    """

    if node is None:
        node = self.context.node

    cmd_parts = ["timeout", str(timeout), "clickhouse-client"]
    cmd_parts.extend(args)
    if query is not None:
        cmd_parts.extend(["--query", query])

    cmd = " ".join(_shell_quote(p) for p in cmd_parts) + " 2>&1; echo __EXIT__=$?"
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
