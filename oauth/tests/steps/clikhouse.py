import json
from helpers.common import getuid
from testflows.asserts import error
from testflows.core import *
from jwt_authentication.tests.steps import change_clickhouse_config
from oauth.requirements.requirements import *


@TestStep(Then)
def access_clickhouse(
    self, token, ip="clickhouse1", https=False, status_code=200, node=None, query=None
):
    """Execute a query to ClickHouse with JWT token authentication.

    Returns the response body string. Asserts the HTTP status code matches
    ``status_code`` (default 200).
    """
    if node is None:
        node = self.context.bash_tools

    http_prefix = "https" if https else "http"
    url = f"{http_prefix}://{ip}:8123/"

    if query is None:
        query = "SELECT currentUser()"

    uid = getuid()[:8]
    tmp_file = f"/tmp/ch_response_{uid}.txt"

    encoded_query = query.replace(" ", "%20")
    curl_command = (
        f'curl -s -o {tmp_file} -w "%{{http_code}}" '
        f"--location '{url}?query={encoded_query}' "
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
    access_clickhouse(token="", ip=ip, https=https, status_code=401)


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
    processor_type=None,
    config_d_dir="/etc/clickhouse-server/config.d",
    node=None,
):
    """Change ClickHouse token processor configuration."""

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
        proc["jwks_cache_lifetime"] = jwks_cache_lifetime

    if token_cache_lifetime is not None:
        proc["token_cache_lifetime"] = token_cache_lifetime

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

    entries = {"token_processor": {processor_name: proc}}

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
    node=None,
    config_d_dir="/etc/clickhouse-server/config.d",
):
    """Change ClickHouse user directories configuration."""

    token_section = {"processor": processor}

    if common_roles is not None:
        token_section["common_roles"] = common_roles

    if roles_filter is not None:
        token_section["roles_filter"] = roles_filter

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
def check_clickhouse_is_alive(self, node=None):
    """Check if ClickHouse server is alive."""
    node = self.context.node if node is None else node

    with When("I check if ClickHouse is alive"):
        request = node.query("SELECT 1").output.strip()

    with Then("ClickHouse is alive"):
        assert request == "1", error()
