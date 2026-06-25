import json
import time
import urllib.parse
from contextlib import contextmanager
from helpers.common import (
    getuid,
    KeyWithAttributes,
    create_xml_config_content,
)
from testflows.asserts import error
from testflows.core import *
from jwt_authentication.tests.steps import change_clickhouse_config
from oauth.requirements.requirements import *


@contextmanager
def without_command_logging(node=None):
    """Mute live forwarding of a node's bash output to the test log.

    Commands executed inside this context still run and their captured
    ``output`` is returned to the caller exactly as usual — only the
    streaming of that output into the on-disk/console log is suppressed.

    Use it to run commands whose *output* contains secrets that cannot be
    pre-registered (e.g. a raw OAuth token-endpoint response, or the
    contents of ``oauth_cache.json``), so the token never reaches the log
    in the first place. After parsing, register the obtained values via
    ``mask_secret`` so any *later* reference to them is redacted too.
    """
    if node is None:
        node = current().context.bash_tools

    bash = node.cluster.bash(node.name)
    child = bash.child

    # ``Command`` re-attaches a logger on every invocation, so we override
    # the bound ``logger`` method to keep output unlogged for the duration
    # rather than just clearing ``_logger`` once.
    original_logger = child.__dict__.get("logger", None)

    def _suppressed_logger(logger=None, prefix=""):
        child._logger = None
        return None

    child._logger = None
    child.logger = _suppressed_logger
    try:
        yield
    finally:
        if original_logger is not None:
            child.logger = original_logger
        else:
            child.__dict__.pop("logger", None)
        child._logger = None


@TestStep(Then)
def access_clickhouse(
    self,
    token,
    ip="clickhouse1",
    https=False,
    status_code=200,
    node=None,
    query=None,
    query_params=None,
    header=None,
):
    """Execute a query against ClickHouse with bearer-token auth.

    Returns the response body. Asserts HTTP status matches ``status_code``
    (default 200). The query is sent as POST body for safe quoting.

    ``query_params`` is an optional ``{key: value}`` dict appended to the
    request URL as query-string parameters.
    """
    if node is None:
        node = self.context.bash_tools

    if header is None:
        header = f"Authorization: Bearer {token}"

    port = 8443 if https else 8123
    http_prefix = "https" if https else "http"
    url = f"{http_prefix}://{ip}:{port}/"

    if query_params:
        url = f"{url}?{urllib.parse.urlencode(query_params)}"

    if query is None:
        query = "SELECT currentUser()"

    uid = getuid()[:8]
    tmp_file = f"/tmp/ch_response_{uid}.txt"

    safe_query = query.replace("'", "'\\''")
    curl_command = (
        f'curl -s -o {tmp_file} -w "%{{http_code}}" '
        f"--location -X POST '{url}' "
        f"--data-binary '{safe_query}' "
        f"--header '{header}'"
    )

    if https:
        curl_command += " -k"

    result = node.command(command=curl_command)

    output = result.output.strip()
    http_code = output[-3:]
    try:
        http_code = int(http_code)
    except ValueError:
        http_code = None

    body_result = node.command(command=f"cat {tmp_file}")
    response_body = body_result.output.strip()

    assert http_code == status_code, error(
        f"Expected HTTP status code {status_code}, but got {http_code}. "
        f"Response body: {response_body}"
    )

    return response_body


@TestStep(Then)
def access_clickhouse_when_forbidden(self, token, ip="clickhouse1", https=False):
    """Execute a query to ClickHouse with an invalid JWT token.

    Expects HTTP 500 with a signature-verification failure message.
    """
    response = access_clickhouse(token=token, ip=ip, https=https, status_code=403)
    assert (
        "failed to verify signature" in response or "AUTHENTICATION_FAILED" in response
    ), error()


@TestStep(Then)
def access_clickhouse_unauthenticated(self, ip="clickhouse1", https=False):
    """Execute a query to ClickHouse without authentication."""
    access_clickhouse(token="", ip=ip, https=https, status_code=403)


@TestStep(Then)
def assert_token_rejected(self, token, ip="clickhouse1", https=False, node=None):
    """Assert ClickHouse refuses ``token`` for any credential-validity reason.

    Accepts HTTP 403 (``AUTHENTICATION_FAILED``) or HTTP 500
    (``token_verification_exception``). For a specific status code, use
    ``access_clickhouse(..., status_code=...)`` directly.
    """
    if node is None:
        node = self.context.bash_tools

    port = 8443 if https else 8123
    http_prefix = "https" if https else "http"
    url = f"{http_prefix}://{ip}:{port}/"

    uid = getuid()[:8]
    tmp_file = f"/tmp/ch_response_{uid}.txt"

    curl_command = (
        f'curl -s -o {tmp_file} -w "%{{http_code}}" '
        f"--location -X POST '{url}' "
        f"--data-binary 'SELECT currentUser()' "
        f"--header 'Authorization: Bearer {token}'"
    )
    if https:
        curl_command += " -k"

    result = node.command(command=curl_command)
    output = result.output.strip()
    try:
        http_code = int(output[-3:])
    except ValueError:
        http_code = None

    body = node.command(command=f"cat {tmp_file}").output.strip()

    rejected_markers = (
        "AUTHENTICATION_FAILED",
        "token_verification_exception",
        "failed to verify signature",
        "missing required claim",
        "ACCESS_DENIED",
    )
    matched_marker = next((m for m in rejected_markers if m in body), None)

    assert http_code in (401, 403, 500) and matched_marker is not None, error(
        f"Expected token rejection (HTTP 401/403/500 with a rejection "
        f"marker), got HTTP {http_code}. "
        f"Body: {body[:500]}"
    )

    return http_code, body


@TestStep(Given)
def change_token_processors(
    self,
    processor_name,
    algo=None,
    static_key=None,
    static_jwks=None,
    jwks_uri=None,
    jwks_cache_lifetime=None,
    token_cache_lifetime=None,
    username_claim=None,
    groups_claim=None,
    configuration_endpoint=None,
    userinfo_endpoint=None,
    token_introspection_endpoint=None,
    expected_issuer=None,
    expected_audience=None,
    expected_typ=None,
    allow_no_expiration=None,
    processor_type=None,
    tenant_id=None,
    introspection_client_id=None,
    introspection_client_secret=None,
    verifier_leeway=None,
    allow_http_discovery_urls=None,
    config_d_dir="/etc/clickhouse-server/config.d",
    node=None,
    replace=False,
    replace_section=False,
):
    """Change ClickHouse token processor configuration.

    When ``replace=True``, the processor element gets ``replace="replace"``
    so that it fully replaces the base processor definition.

    When ``replace_section=True``, the entire ``<token_processors>`` section
    gets ``replace="replace"`` so that ALL base processors are removed and
    only the ones defined here remain.
    """

    proc = {}

    if processor_type is not None:
        proc["type"] = processor_type

    if algo is not None:
        proc["algo"] = algo

    if static_key is not None:
        proc["static_key"] = static_key

    if static_jwks is not None:
        proc["static_jwks"] = static_jwks

    if jwks_uri is not None:
        proc["jwks_uri"] = jwks_uri

    if jwks_cache_lifetime is not None:
        proc["jwks_cache_lifetime"] = str(jwks_cache_lifetime)

    if token_cache_lifetime is not None:
        proc["token_cache_lifetime"] = str(token_cache_lifetime)

    if username_claim is not None:
        proc["username_claim"] = username_claim

    if groups_claim is not None:
        proc["groups_claim"] = groups_claim

    if configuration_endpoint is not None:
        proc["configuration_endpoint"] = configuration_endpoint

    if userinfo_endpoint is not None:
        proc["userinfo_endpoint"] = userinfo_endpoint

    if token_introspection_endpoint is not None:
        proc["token_introspection_endpoint"] = token_introspection_endpoint

    if expected_issuer is not None:
        proc["expected_issuer"] = expected_issuer

    if expected_audience is not None:
        proc["expected_audience"] = expected_audience

    if expected_typ is not None:
        proc["expected_typ"] = expected_typ

    if allow_no_expiration is not None:
        if isinstance(allow_no_expiration, bool):
            proc["allow_no_expiration"] = "true" if allow_no_expiration else "false"
        else:
            proc["allow_no_expiration"] = str(allow_no_expiration)

    if tenant_id is not None:
        proc["tenant_id"] = tenant_id

    if introspection_client_id is not None:
        proc["introspection_client_id"] = introspection_client_id

    if introspection_client_secret is not None:
        proc["introspection_client_secret"] = introspection_client_secret

    if verifier_leeway is not None:
        proc["verifier_leeway"] = str(verifier_leeway)

    if allow_http_discovery_urls is not None:
        if isinstance(allow_http_discovery_urls, bool):
            proc["allow_http_discovery_urls"] = (
                "true" if allow_http_discovery_urls else "false"
            )
        else:
            proc["allow_http_discovery_urls"] = str(allow_http_discovery_urls)

    if replace:
        proc_key = KeyWithAttributes(processor_name, {"replace": "replace"})
    else:
        proc_key = processor_name

    if replace_section:
        tp_key = KeyWithAttributes("token_processors", {"replace": "replace"})
    else:
        tp_key = "token_processors"

    entries = {tp_key: {proc_key: proc}}

    change_clickhouse_config(
        entries=entries,
        config_d_dir=config_d_dir,
        preprocessed_name="config.xml",
        restart=True,
        config_file=f"{processor_name}_config.xml",
        node=node,
    )


@TestStep(Given)
def change_user_directories_config(
    self,
    processor,
    common_roles=None,
    roles_filter=None,
    roles_transform=None,
    roles_mapping=None,
    default_profile=None,
    node=None,
    config_d_dir="/etc/clickhouse-server/config.d",
):
    """Change ClickHouse user directories configuration.

    ``roles_transform`` accepts a sed-style regex (e.g. ``s/^grafana-//``).
    ``default_profile`` names a settings profile for auto-provisioned token users.
    """

    token_section = {"processor": processor}

    if common_roles is not None:
        token_section["common_roles"] = {role: {} for role in common_roles}

    if roles_filter is not None:
        token_section["roles_filter"] = roles_filter

    if roles_transform is not None:
        token_section["roles_transform"] = roles_transform

    if roles_mapping is not None:
        maps = [{"from": m["from"], "to": m["to"]} for m in roles_mapping]
        token_section["roles_mapping"] = {"map": maps}

    if default_profile is not None:
        token_section["default_profile"] = default_profile

    entries = {"user_directories": {"token": token_section}}

    change_clickhouse_config(
        entries=entries,
        config_d_dir=config_d_dir,
        preprocessed_name="config.xml",
        restart=True,
        config_file=f"user_directory_{processor}.xml",
        node=node,
    )


@TestStep(Given)
def apply_fatal_user_directories_config(
    self,
    entries,
    expected_message,
    config_file="user_directory_fatal.xml",
    config_d_dir="/etc/clickhouse-server/config.d",
    timeout=120,
    tail=200,
    node=None,
):
    """Write a config overlay that ClickHouse SHALL reject at startup,
    and verify the rejection message.

    Writes the bad config inside the container (not on the host), verifies
    the expected error appears in the log, then removes the config and
    double-restarts to recover.
    """
    if node is None:
        node = self.context.node

    config = create_xml_config_content(
        entries,
        config_file=config_file,
        config_d_dir=config_d_dir,
        preprocessed_name="config.xml",
    )

    try:
        with Given("I prepare the error log so the message check can grep cleanly"):
            node.command(
                'echo -e "%s" > /var/log/clickhouse-server/clickhouse-server.err.log'
                % ("-\\n" * tail)
            )

        with When(f"I write the bad config to {config.path}"):
            node.command(
                f"cat <<HEREDOC > {config.path}\n{config.content}\nHEREDOC",
                steps=False,
                exitcode=0,
            )

        with And(
            "I restart ClickHouse without waiting for healthy "
            "(the server is supposed to fail to start)"
        ):
            node.restart_clickhouse(safe=False, wait_healthy=False)

        with Then(
            "the error log should contain the expected rejection message",
            description=f"timeout {timeout}",
        ):
            started = time.time()
            grep_command = (
                f"tail -n {tail} /var/log/clickhouse-server/clickhouse-server.err.log "
                f'| grep -F "{expected_message}"'
            )
            exitcode = 1
            while time.time() - started < timeout:
                exitcode = node.command(
                    grep_command, steps=False, no_checks=True
                ).exitcode
                if exitcode == 0:
                    break
                time.sleep(1)
            assert exitcode == 0, error(
                f"Expected error message {expected_message!r} not found in "
                f"clickhouse-server.err.log within {timeout}s"
            )

    finally:
        with Finally(f"I remove {config.path} and restart ClickHouse"):
            with By("removing the bad config file from inside the container"):
                node.command(f"rm -rf {config.path}", steps=False, exitcode=0)

            with And(
                "restarting ClickHouse to recover from the failed start",
                description="""
                    Two restarts mirrors ``helpers.common.add_invalid_config``:
                    the first kicks any wedged process / clears stale pid
                    state, the second comes up healthy now that the bad
                    overlay is gone.
                """,
            ):
                node.restart_clickhouse(safe=False)
                node.restart_clickhouse(safe=False)


@TestStep(Then)
def access_clickhouse_connection_refused(
    self, token, ip="clickhouse1", https=False, node=None
):
    """Assert that a TCP connection to ClickHouse is refused.

    Expects curl exit code 7 (connection refused) or 28 (timeout).
    """
    if node is None:
        node = self.context.bash_tools

    port = 8443 if https else 8123
    http_prefix = "https" if https else "http"
    url = f"{http_prefix}://{ip}:{port}/"

    curl_command = (
        f"curl -s -o /dev/null -w '%{{http_code}}' "
        f"--connect-timeout 5 "
        f"--location '{url}?query=SELECT%201' "
        f"--header 'Authorization: Bearer {token}'"
    )

    if https:
        curl_command += " -k"

    curl_command += "; echo exit_code=$?"

    result = node.command(command=curl_command)
    output = result.output.strip()

    assert "exit_code=7" in output or "exit_code=28" in output, error(
        f"Expected connection refused (exit code 7 or 28), got: {output}"
    )


@TestStep(Given)
def change_ports_config(
    self,
    http_port=None,
    https_port=None,
    remove_http=False,
    node=None,
    config_d_dir="/etc/clickhouse-server/config.d",
):
    """Override ClickHouse listening ports via config.d.

    When ``remove_http=True`` the HTTP port is removed so that only
    HTTPS is available.
    """
    entries = {}

    if remove_http:
        entries[KeyWithAttributes("http_port", {"remove": "remove"})] = ""
    elif http_port is not None:
        entries["http_port"] = str(http_port)

    if https_port is not None:
        entries["https_port"] = str(https_port)

    change_clickhouse_config(
        entries=entries,
        config_d_dir=config_d_dir,
        preprocessed_name="config.xml",
        restart=True,
        config_file="ports_override.xml",
        node=node,
    )


@TestStep(Then)
def check_clickhouse_is_alive(self, node=None):
    """Check if ClickHouse server is alive."""
    node = self.context.node if node is None else node

    with When("I check if ClickHouse is alive"):
        request = node.query("SELECT 1").output.strip()

    with Then("ClickHouse is alive"):
        assert request == "1", error()


@TestStep(Given)
def change_user_jwt_auth(
    self,
    username,
    processor=None,
    claims=None,
    node=None,
    config_d_dir="/etc/clickhouse-server/users.d",
):
    """Pin a ClickHouse user to a specific JWT processor and optional claims.

    Writes ``users.d/<user>_jwt_auth.xml``. Cleanup is automatic at
    scenario teardown.
    """
    jwt_section = {}
    if processor is not None:
        jwt_section["processor"] = processor
    if claims is not None:
        jwt_section["claims"] = json.dumps(claims, separators=(",", ":"))

    entries = {"users": {username: {"jwt": jwt_section}}}

    change_clickhouse_config(
        entries=entries,
        config_d_dir=config_d_dir,
        preprocessed_name="users.xml",
        restart=False,
        config_file=f"{username}_jwt_auth.xml",
        node=node,
    )


@TestStep(Given)
def create_sql_jwt_user(
    self,
    username,
    processor=None,
    claims=None,
    node=None,
):
    """Create a user via ``CREATE USER ... IDENTIFIED WITH jwt``.

    Accepts optional ``PROCESSOR`` and ``CLAIMS`` clauses.
    Drops the user in a ``Finally`` block at scenario teardown.
    """
    if node is None:
        node = self.context.node

    stmt = f"CREATE USER OR REPLACE {username} IDENTIFIED WITH jwt"
    if processor is not None:
        stmt += f" PROCESSOR '{processor}'"
    if claims is not None:
        if isinstance(claims, dict):
            claims = json.dumps(claims, separators=(",", ":"))
        stmt += f" CLAIMS '{claims.replace(chr(34), chr(92) + chr(34))}'"

    node.query(stmt)

    try:
        yield username
    finally:
        with Finally(f"I drop user {username}"):
            node.query(f"DROP USER IF EXISTS {username}", no_checks=True)


@TestStep(When)
def alter_sql_jwt_user(
    self,
    username,
    processor=None,
    claims=None,
    node=None,
):
    """ALTER a user's JWT authentication via SQL."""
    if node is None:
        node = self.context.node

    stmt = f"ALTER USER {username} IDENTIFIED WITH jwt"
    if processor is not None:
        stmt += f" PROCESSOR '{processor}'"
    if claims is not None:
        if isinstance(claims, dict):
            claims = json.dumps(claims, separators=(",", ":"))
        stmt += f" CLAIMS '{claims.replace(chr(34), chr(92) + chr(34))}'"

    node.query(stmt)


def show_create_user(username, node=None):
    """Return the ``SHOW CREATE USER`` output for a user."""
    if node is None:
        node = current().context.node
    return node.query(f"SHOW CREATE USER {username}").output.strip()


@TestStep(Given)
def change_user_directories_order(
    self,
    entries_in_order,
    node=None,
    config_d_dir="/etc/clickhouse-server/config.d",
):
    """Write a ``<user_directories>`` section with a specific child order.

    Uses ``replace="replace"`` to fully replace the section, allowing
    control over element ordering that merge-based helpers cannot provide.

    ``entries_in_order`` is a list of ``(element_name, child_dict)`` tuples.
    """
    children = {}
    for name, value in entries_in_order:
        # If the same name appears twice, suffix to preserve order; the
        # underlying writer collapses by name otherwise.
        key = name if name not in children else KeyWithAttributes(name, {})
        children[key] = value

    section_key = KeyWithAttributes("user_directories", {"replace": "replace"})
    entries = {section_key: children}

    change_clickhouse_config(
        entries=entries,
        config_d_dir=config_d_dir,
        preprocessed_name="config.xml",
        restart=True,
        config_file="user_directories_order.xml",
        node=node,
    )


@TestStep(Given)
def change_user_quota(
    self,
    username,
    failed_sequential_authentications=None,
    node=None,
    config_d_dir="/etc/clickhouse-server/users.d",
):
    """Apply a per-user ClickHouse quota.

    Currently exposes only ``failed_sequential_authentications``.
    """
    quota_name = f"{username}_quota"
    interval = {"duration": "3600"}
    if failed_sequential_authentications is not None:
        interval["failed_sequential_authentications"] = str(
            failed_sequential_authentications
        )

    entries = {
        "quotas": {quota_name: {"interval": interval}},
        "users": {username: {"quota": quota_name}},
    }

    change_clickhouse_config(
        entries=entries,
        config_d_dir=config_d_dir,
        preprocessed_name="users.xml",
        restart=False,
        config_file=f"{username}_quota.xml",
        node=node,
    )


def open_native_jwt_session(
    token,
    container_node="clickhouse1",
    target_host="clickhouse1",
    target_port=9000,
):
    """Open a long-lived ``clickhouse-client --jwt`` TCP session.

    Not yet re-implemented; callers should ``Skip`` until the
    replacement helper lands.
    """
    raise NotImplementedError(
        "open_native_jwt_session is not yet re-implemented; "
        "dependent scenarios should Skip until the replacement helper lands."
    )


@TestStep(Given)
def reload_clickhouse_config(self, node=None):
    """Force ClickHouse to re-read its configuration via ``SYSTEM RELOAD CONFIG``."""
    if node is None:
        node = self.context.node
    node.query("SYSTEM RELOAD CONFIG")


def search_server_log(node, pattern, lines=500):
    """Grep the recent ``clickhouse-server.log`` lines for a literal pattern.

    Returns the matching lines as a single newline-joined string (empty
    string if no matches). Plain function so it can be called from
    anywhere to read state.
    """
    cmd = (
        f"tail -n {lines} /var/log/clickhouse-server/clickhouse-server.log "
        f"| grep -F -- '{pattern}' || true"
    )
    return node.command(cmd, steps=False).output.strip()


@TestStep(Then)
def assert_auth_request_completes(
    self,
    token,
    ip="clickhouse1",
    max_time=120,
    node=None,
):
    """Assert a bearer-auth request returns instead of hanging forever.

    Used by availability scenarios where a provider endpoint is
    unreachable: ClickHouse SHALL NOT block the request thread
    indefinitely. ``curl --max-time`` bounds the wait; if the request
    is still pending at ``max_time`` the helper fails because the auth
    path hung. Returns the elapsed seconds.
    """
    if node is None:
        node = self.context.bash_tools

    uid = getuid()[:8]
    tmp_file = f"/tmp/ch_avail_{uid}.txt"
    curl_command = (
        f'curl -s -o {tmp_file} -w "%{{http_code}}" '
        f"--max-time {max_time} "
        f"--location 'http://{ip}:8123/?query=SELECT%201' "
        f"--header 'Authorization: Bearer {token}'"
    )

    start = time.time()
    node.command(command=curl_command, timeout=(max_time + 60) * 1000)
    elapsed = time.time() - start

    note(f"Auth request completed in {elapsed:.1f}s")
    assert elapsed < max_time, error(
        f"Auth request did not complete within {max_time}s — the auth "
        f"path appears to hang on the unreachable endpoint"
    )
    return elapsed


@TestStep(Then)
def basic_auth_request(self, user, password="", ip="clickhouse1", node=None):
    """Send a Basic-auth HTTP request and return the 3-char HTTP status code.

    Used to assert that ClickHouse returns a clean auth decision for a
    non-token credential (rather than aborting the access-storage chain).
    """
    if node is None:
        node = self.context.bash_tools

    uid = getuid()[:8]
    tmp_file = f"/tmp/ch_basic_{uid}.txt"
    url = f"http://{ip}:8123/?query=SELECT%20currentUser()"
    curl_command = (
        f"curl -s -o {tmp_file} -w '%{{http_code}}' "
        f"--location '{url}' "
        f"--user '{user}:{password}'"
    )
    result = node.command(command=curl_command)
    return result.output.strip()[-3:]
