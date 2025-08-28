import requests
from testflows.core import *
from jwt_authentication.tests.steps import change_clickhouse_config


@TestStep(Then)
def access_clickhouse(self, token, ip="clickhouse1", https=False):
    """Execute a query to ClickHouse with JWT token authentication."""
    http_prefix = "https" if https else "http"
    url = f"{http_prefix}://{ip}:8123/"

    headers = {"X-ClickHouse-JWT-Token": f"Bearer {token}"}

    params = {"query": "SELECT currentUser()"}

    verify = False if https else True

    response = requests.get(url, headers=headers, params=params, verify=verify)
    response.raise_for_status()

    return response


@TestStep(Given)
def change_token_processors(
    processor_name,
    algo=None,
    static_key=None,
    static_jwks=None,
    jwks_uri=None,
    jwks_cache_lifetime=None,
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
    entries["jwt_validators"][processor_name] = {}

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
        entires=entries,
        config_d_dir=config_d_dir,
        preprocessed_name="config.xml",
        restart=True,
        config_file=f"user_directory_{processor}.xml",
        node=node,
    )
