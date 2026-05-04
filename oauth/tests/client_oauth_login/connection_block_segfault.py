"""Tests guarding against ``Client::login`` segfaults on empty ``hosts_and_ports``."""

from testflows.core import *

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_Connection_HostFallback,
    RQ_SRS_042_OAuth_Client_Login_Connection_NoSegfault,
)
from oauth.tests.client_oauth_login.common import connection_only_config_xml
from oauth.tests.steps.client_login import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_CREDS_PATH,
    assert_no_segfault,
    reset_client_state,
    run_clickhouse_client,
    run_clickhouse_client_no_host,
    write_client_config_xml,
    write_oauth_credentials_file,
)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Connection_NoSegfault("1.0"))
@Name("login with --connection does not segfault")
def login_with_connection_no_segfault(self):
    """Check that ``--login=device --connection X`` does not crash on empty hosts list."""

    reset_client_state()
    write_client_config_xml(contents=connection_only_config_xml())
    write_oauth_credentials_file()

    exit_code, output = run_clickhouse_client_no_host(
        args=[
            "--config",
            DEFAULT_CONFIG_PATH,
            "--connection",
            "ch_test",
            "--login=device",
            "--oauth-credentials",
            DEFAULT_CREDS_PATH,
        ],
        query="SELECT 1",
        timeout=10,
    )

    assert_no_segfault(output=output, exit_code=exit_code)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_Connection_NoSegfault("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Connection_HostFallback("1.0"),
)
@Name("bare --login + --connection (cloud path) does not segfault")
def bare_login_with_connection_no_segfault(self):
    """Check that bare ``--login`` with ``--connection`` does not crash."""

    reset_client_state()
    write_client_config_xml(contents=connection_only_config_xml())

    exit_code, output = run_clickhouse_client_no_host(
        args=[
            "--config",
            DEFAULT_CONFIG_PATH,
            "--connection",
            "ch_test",
            "--login",
            "--oauth-url=http://keycloak:8080/realms/grafana",
            "--oauth-client-id=grafana-client",
            "--oauth-audience=http://localhost",
        ],
        query="SELECT 1",
        timeout=10,
    )

    assert_no_segfault(output=output, exit_code=exit_code)


@TestScenario
@Name("login with explicit --host preserves existing behaviour")
def login_with_explicit_host_still_works(self):
    """Check that explicit ``--host`` still drives the original code path without crashing."""

    reset_client_state()
    write_oauth_credentials_file()

    exit_code, output = run_clickhouse_client(
        args=[
            "--host",
            "clickhouse1",
            "--login=device",
            "--oauth-credentials",
            DEFAULT_CREDS_PATH,
        ],
        query="SELECT 1",
        timeout=8,
        expect_error=True,
    )

    assert_no_segfault(output=output, exit_code=exit_code)


@TestFeature
@Name("connection block segfault")
def feature(self):
    """Tests guarding against ``Client::login`` segfaults on empty ``hosts_and_ports``."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
