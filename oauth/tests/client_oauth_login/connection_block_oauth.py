"""Tests for ``connections_credentials`` OAuth fields and ``--oauth-*`` CLI flags."""

from testflows.core import *

from oauth.tests.client_oauth_login.common import oauth_connection_config_xml
from oauth.tests.steps.client_login import (
    DEFAULT_CONFIG_PATH,
    assert_no_segfault,
    reset_client_state,
    run_clickhouse_client_no_host,
    write_client_config_xml,
)


@TestScenario
@Name("connection block configures device-flow OAuth")
def connection_block_oauth_device(self):
    """Check that a ``<connection>`` with ``<login>device</login>`` drives device flow."""

    reset_client_state()
    write_client_config_xml(
        contents=oauth_connection_config_xml(login_mode="device")
    )

    exit_code, output = run_clickhouse_client_no_host(
        args=[
            "--config",
            DEFAULT_CONFIG_PATH,
            "--connection",
            "ch_oauth",
        ],
        query="SELECT 1",
        timeout=10,
    )

    assert_no_segfault(output=output, exit_code=exit_code)


@TestScenario
@Name("--oauth-* CLI flags override connection block")
def cli_overrides_connection_block(self):
    """Check that CLI ``--oauth-client-id`` overrides ``<oauth-client-id>`` from the block."""

    reset_client_state()
    write_client_config_xml(
        contents=oauth_connection_config_xml(
            login_mode="device",
            oauth_client_id="block-id",
        )
    )

    exit_code, output = run_clickhouse_client_no_host(
        args=[
            "--config",
            DEFAULT_CONFIG_PATH,
            "--connection",
            "ch_oauth",
            "--oauth-client-id",
            "cli-id",
        ],
        query="SELECT 1",
        timeout=10,
    )

    assert_no_segfault(output=output, exit_code=exit_code)


@TestScenario
@Name("connection block with invalid oauth-callback-port is rejected")
def invalid_callback_port_rejected(self):
    """Check that an out-of-range ``<oauth-callback-port>`` fails fast without crashing."""

    reset_client_state()
    write_client_config_xml(
        contents=oauth_connection_config_xml(
            login_mode="browser",
            oauth_callback_port="999999",
        )
    )

    exit_code, output = run_clickhouse_client_no_host(
        args=[
            "--config",
            DEFAULT_CONFIG_PATH,
            "--connection",
            "ch_oauth",
        ],
        query="SELECT 1",
        timeout=10,
    )

    assert_no_segfault(output=output, exit_code=exit_code)


@TestFeature
@Name("connection block oauth")
def feature(self):
    """Tests for ``connections_credentials`` OAuth fields and ``--oauth-*`` CLI flags."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
