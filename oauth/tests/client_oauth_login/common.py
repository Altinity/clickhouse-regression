"""Shared helpers for client_oauth_login feature tests."""


def connection_only_config_xml(host="clickhouse1", port=9000, name="ch_test"):
    """Return a minimal ``connections_credentials`` config with no ``--host`` source."""

    return (
        "<clickhouse>\n"
        "    <connections_credentials>\n"
        f"        <connection>\n"
        f"            <name>{name}</name>\n"
        f"            <hostname>{host}</hostname>\n"
        f"            <port>{port}</port>\n"
        "            <database>default</database>\n"
        "        </connection>\n"
        "    </connections_credentials>\n"
        "</clickhouse>\n"
    )


def oauth_connection_config_xml(
    host="clickhouse1",
    port=9000,
    name="ch_oauth",
    login_mode="device",
    oauth_url="http://keycloak:8080/realms/grafana",
    oauth_client_id="grafana-client",
    oauth_audience=None,
    oauth_client_secret=None,
    oauth_callback_port=None,
):
    """Return a ``connections_credentials`` block with OAuth fields."""

    extra = ""
    if login_mode is not None:
        extra += f"            <login>{login_mode}</login>\n"
    if oauth_url is not None:
        extra += f"            <oauth-url>{oauth_url}</oauth-url>\n"
    if oauth_client_id is not None:
        extra += f"            <oauth-client-id>{oauth_client_id}</oauth-client-id>\n"
    if oauth_audience is not None:
        extra += f"            <oauth-audience>{oauth_audience}</oauth-audience>\n"
    if oauth_client_secret is not None:
        extra += (
            f"            <oauth-client-secret>{oauth_client_secret}"
            "</oauth-client-secret>\n"
        )
    if oauth_callback_port is not None:
        extra += (
            f"            <oauth-callback-port>{oauth_callback_port}"
            "</oauth-callback-port>\n"
        )

    return (
        "<clickhouse>\n"
        "    <connections_credentials>\n"
        f"        <connection>\n"
        f"            <name>{name}</name>\n"
        f"            <hostname>{host}</hostname>\n"
        f"            <port>{port}</port>\n"
        f"{extra}"
        "        </connection>\n"
        "    </connections_credentials>\n"
        "</clickhouse>\n"
    )
