import json
import urllib.parse
from helpers.common import getuid, KeyWithAttributes
from testflows.asserts import error
from testflows.core import *
from jwt_authentication.tests.steps import change_clickhouse_config
from oauth.requirements.requirements import *


@TestStep(Then)
def access_clickhouse(
    self, token, ip="clickhouse1", https=False, status_code=200, node=None, query=None
):
    """Execute a query against ClickHouse with bearer-token auth.

    Returns the response body string. Asserts the HTTP status code matches
    ``status_code`` (default 200). The query is sent in the request body
    (POST) so quoting / special characters are safe — earlier versions
    used ad-hoc URL escaping that broke on any query containing ``&``,
    ``+``, ``#`` or quotes.
    """
    if node is None:
        node = self.context.bash_tools

    port = 8443 if https else 8123
    http_prefix = "https" if https else "http"
    url = f"{http_prefix}://{ip}:{port}/"

    if query is None:
        query = "SELECT currentUser()"

    uid = getuid()[:8]
    tmp_file = f"/tmp/ch_response_{uid}.txt"

    safe_query = query.replace("'", "'\\''")
    curl_command = (
        f'curl -s -o {tmp_file} -w "%{{http_code}}" '
        f"--location -X POST '{url}' "
        f"--data-binary '{safe_query}' "
        f"--header 'Authorization: Bearer {token}'"
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
    response = access_clickhouse(token=token, ip=ip, https=https, status_code=500)
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

    "Rejected" can surface as either:

    - HTTP 403 (``AUTHENTICATION_FAILED``) — token validated against
      JWKS but the audience/issuer/etc. didn't match what the
      processor expected, or
    - HTTP 500 with ``token_verification_exception`` — the JWT
      structure itself was rejected (missing required claim, bad
      signature, unknown ``kid``, etc.).

    Use this when the *exact* failure code depends on which claim is
    wrong / missing, but the test only cares that ClickHouse said no.
    For tests that want to pin a specific status, call
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
    processor_type=None,
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
    node=None,
    config_d_dir="/etc/clickhouse-server/config.d",
):
    """Change ClickHouse user directories configuration.

    The config.d file merges with the base ``<user_directories>`` section.
    For positive tests (overriding the processor or roles on the existing
    token directory) this is sufficient because ClickHouse merges children
    by element name.

    ``roles_transform`` accepts a sed-style regex (e.g. ``s/^grafana-//``)
    used by the M-13 audit scenario; the helper writes it verbatim into
    ``<roles_transform>``.
    """

    token_section = {"processor": processor}

    if common_roles is not None:
        token_section["common_roles"] = {role: {} for role in common_roles}

    if roles_filter is not None:
        token_section["roles_filter"] = roles_filter

    if roles_transform is not None:
        token_section["roles_transform"] = roles_transform

    entries = {"user_directories": {"token": token_section}}

    change_clickhouse_config(
        entries=entries,
        config_d_dir=config_d_dir,
        preprocessed_name="config.xml",
        restart=True,
        config_file=f"user_directory_{processor}.xml",
        node=node,
    )


@TestStep(Then)
def access_clickhouse_connection_refused(
    self, token, ip="clickhouse1", https=False, node=None
):
    """Assert that a TCP connection to ClickHouse is refused.

    Used when the target port (HTTP or HTTPS) has been disabled via config.
    curl returns exit code 7 when the connection is refused.
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
    """Pin a ClickHouse user to a specific JWT processor (and optional claims).

    Writes ``users.d/<user>_jwt_auth.xml`` of the form

        <users>
            <${username}>
                <jwt>
                    <processor>${processor}</processor>
                    <claims>{...}</claims>
                </jwt>
            </${username}>
        </users>

    Used by the ``processor_pin_bypass`` and ``quota_binding`` audit
    scenarios. Cleanup is handled automatically by the underlying
    ``change_clickhouse_config`` helper at scenario teardown.
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
def change_user_directories_order(
    self,
    entries_in_order,
    node=None,
    config_d_dir="/etc/clickhouse-server/config.d",
):
    """Write a ``<user_directories>`` section with a specific child order.

    ``change_user_directories_config`` merges by element name and
    therefore can't reorder children. The H-25 scenario specifically
    needs ``<token>`` to come before ``<users_xml>`` to exercise the
    storage-chain-lockout code path, so we write a ``replace="replace"``
    section here.

    ``entries_in_order`` is a list of ``(element_name, child_dict)`` so
    duplicate keys at the same level are also accepted (Python dicts
    can't represent that, but the underlying ``KeyWithAttributes``
    convention used elsewhere in the helpers does).
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

    Currently exposes only ``failed_sequential_authentications`` because
    that's what the L-08/L-17 audit scenarios need. The XML written is::

        <quotas>
            <${username}_quota>
                <interval>
                    <duration>3600</duration>
                    <failed_sequential_authentications>${N}</failed_sequential_authentications>
                </interval>
            </${username}_quota>
        </quotas>
        <users><${username}><quota>${username}_quota</quota></${username}></users>
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

    Used by the H-05 / M-28 audit scenarios that need to assert the
    behaviour of an established native-protocol session when the token
    expires or the validating processor is replaced server-side.

    Implementation status: the original pexpect-based implementation
    was reverted (see ``audit-automation-progress.md``) and a new one
    has not landed yet. The dependent scenarios should be ``Skip``-ped
    until then. We import it as a real symbol so downstream imports
    work; calling it surfaces a clear ``NotImplementedError`` instead
    of an ``ImportError`` that breaks the whole ``security_audit``
    package.
    """
    raise NotImplementedError(
        "open_native_jwt_session is not yet re-implemented; H-05 / M-28 "
        "scenarios should Skip until the pexpect-backed helper lands. "
        "See oauth/audit-automation-progress.md for context."
    )


@TestStep(Given)
def reload_clickhouse_config(self, node=None):
    """Force ClickHouse to re-read its configuration.

    Some scenarios mutate config.d/users.d files via filesystem-level
    helpers (not via ``change_clickhouse_config``) and need ClickHouse
    to pick up the new files without a restart. ``SYSTEM RELOAD CONFIG``
    is the correct hook.
    """
    if node is None:
        node = self.context.node
    node.query("SYSTEM RELOAD CONFIG")
