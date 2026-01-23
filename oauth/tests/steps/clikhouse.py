import json
from testflows.asserts import error
from testflows.core import *
from jwt_authentication.tests.steps import change_clickhouse_config
from oauth.requirements.requirements import *


@TestStep(Then)
def access_clickhouse(
    self, token, ip="clickhouse1", https=False, status_code=200, node=None
):
    """Execute a query to ClickHouse with JWT token authentication and return both response and status code."""
    if node is None:
        node = self.context.bash_tools

    http_prefix = "https" if https else "http"
    url = f"{http_prefix}://{ip}:8123/"

    curl_command = f"""curl -s -o /tmp/ch_response.txt -w "%{{http_code}}" \
--location '{url}?query=SELECT%20currentUser()' \
--header 'Authorization: Bearer {token}'"""

    if https:
        curl_command += " -k"

    result = node.command(command=curl_command)

    output = result.output.strip()
    http_code = output[-3:]
    try:
        http_code = int(http_code)
    except ValueError:
        http_code = None

    body_result = node.command(command="cat /tmp/ch_response.txt")
    response_body = body_result.output.strip()

    assert http_code == status_code, error(
        f"Expected HTTP status code {status_code}, but got {http_code}. Response body: {response_body}"
    )

    return response_body


@TestStep(Then)
def access_clickhouse_when_forbidden(self, token, ip="clickhouse1", https=False):
    """Execute a query to ClickHouse with an invalid JWT token."""

    response = access_clickhouse(token=token, ip=ip, https=https, status_code=500)
    assert "failed to verify signature" in response, error()


@TestStep(Then)
def access_clickhouse_unauthenticated(self, ip="clickhouse1", https=False):
    """Execute a query to ClickHouse without authentication."""

    access_clickhouse(token="", ip=ip, https=https, status_code=401)


@TestStep(Given)
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_TokenProcessors_token_processor(
        "1.0"
    )
)
def change_token_processors(
    self,
    processor_name,
    algo=None,
    static_key=None,
    static_jwks=None,
    jwks_uri=None,
    jwks_cache_lifetime=None,
    token_cache_lifetime=None,
    claims=None,
    verifier_leeway=None,
    configuration_endpoint=None,
    userinfo_endpoint=None,
    token_introspection_endpoint=None,
    processor_type=None,
    config_d_dir="/etc/clickhouse-server/config.d",
    node=None,
):
    """Change ClickHouse token processor configuration."""

    entries = {"token_processor": {}}
    entries["token_processor"][processor_name] = {}

    if processor_type is not None:
        entries["token_processor"][processor_name]["type"] = processor_type

    if algo is not None:
        entries["token_processor"]["algo"] = algo

    if static_key is not None:
        entries["token_processor"][processor_name]["static_key"] = static_key

    if static_jwks is not None:
        entries["token_processor"][processor_name]["static_jwks"] = static_jwks

    if jwks_uri is not None:
        entries["token_processor"][processor_name]["jwks_uri"] = jwks_uri

    if jwks_cache_lifetime is not None:
        entries["token_processor"][processor_name][
            "jwks_cache_lifetime"
        ] = jwks_cache_lifetime

    if token_cache_lifetime is not None:
        entries["token_processor"][processor_name][
            "token_cache_lifetime"
        ] = token_cache_lifetime

    if claims is not None:
        entries["jwt_validators"][processor_name]["claims"] = claims

    if verifier_leeway is not None:
        entries["jwt_validators"][processor_name]["verifier_leeway"] = verifier_leeway

    if configuration_endpoint is not None:
        entries["token_processor"][processor_name][
            "configuration_endpoint"
        ] = configuration_endpoint

    if userinfo_endpoint is not None:
        entries["token_processor"][processor_name][
            "userinfo_endpoint"
        ] = userinfo_endpoint

    if token_introspection_endpoint is not None:
        entries["token_processor"][processor_name][
            "token_introspection_endpoint"
        ] = token_introspection_endpoint

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

    entries = {"user_directories": {}}
    entries["user_directories"]["token"] = {}

    entries["user_directories"]["token"]["processor"] = processor

    if common_roles is not None:
        entries["user_directories"]["token"]["common_roles"] = common_roles

    if roles_filter is not None:
        entries["user_directories"]["token"]["roles_filter"] = roles_filter

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
