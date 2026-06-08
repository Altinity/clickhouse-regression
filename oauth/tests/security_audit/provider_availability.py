"""[H-19] See ``oauth/new_audit_review/combined-issues.md``.

Since antalya-26.3 (PR #1799), the OpenID processor no longer accepts
``jwks_uri``. Validation goes through ``userinfo_endpoint`` /
``token_introspection_endpoint``. These scenarios now test provider
availability when those endpoints are unreachable.
"""

import time

from testflows.core import *

from helpers.common import getuid
from oauth.tests.steps.clikhouse import (
    change_token_processors,
    change_user_directories_config,
    check_clickhouse_is_alive,
)


MAX_REASONABLE_AUTH_TIMEOUT = 30


@TestScenario
@Name("H-19 / 1")
def scenario_1(self):
    """[H-19] ClickHouse does not hang indefinitely when the
    introspection endpoint is non-routable."""
    client = self.context.provider_client

    with Given(
        "I configure OpenID with a non-routable introspection endpoint "
        "and valid userinfo_endpoint"
    ):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint="http://10.255.255.1:9999/hang",
            introspection_client_id=self.context.introspection_client_id,
            introspection_client_secret=self.context.introspection_client_secret,
            replace=True,
        )

    with And("I configure user directories"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("I send an auth request and measure how long it takes"):
        start = time.time()
        node = self.context.bash_tools
        port = 8123
        uid = getuid()[:8]
        tmp_file = f"/tmp/ch_{uid}.txt"
        curl_command = (
            f'curl -s -o {tmp_file} -w "%{{http_code}}" '
            f"--max-time 120 "
            f"--location 'http://clickhouse1:{port}/?query=SELECT%201' "
            f"--header 'Authorization: Bearer {token}'"
        )
        node.command(command=curl_command, timeout=180000)
        elapsed = time.time() - start
        note(f"Auth request completed in {elapsed:.1f}s")

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Name("H-19 / 2")
def scenario_2(self):
    """[H-19] ClickHouse does not hang indefinitely when the
    userinfo endpoint is non-routable."""
    client = self.context.provider_client

    with Given(
        "I configure OpenID with a non-routable userinfo_endpoint "
        "and valid introspection endpoint"
    ):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            userinfo_endpoint="http://10.255.255.1:9999/hang",
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            introspection_client_id=self.context.introspection_client_id,
            introspection_client_secret=self.context.introspection_client_secret,
            replace=True,
        )

    with And("I configure user directories"):
        change_user_directories_config(
            processor="keycloak",
            common_roles=["general-role"],
        )

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with Then("I send an auth request and measure how long it takes"):
        start = time.time()
        node = self.context.bash_tools
        port = 8123
        uid = getuid()[:8]
        tmp_file = f"/tmp/ch_{uid}.txt"
        curl_command = (
            f'curl -s -o {tmp_file} -w "%{{http_code}}" '
            f"--max-time 120 "
            f"--location 'http://clickhouse1:{port}/?query=SELECT%201' "
            f"--header 'Authorization: Bearer {token}'"
        )
        node.command(command=curl_command, timeout=180000)
        elapsed = time.time() - start
        note(f"Auth request completed in {elapsed:.1f}s")

    with And("the server is still responsive to normal queries"):
        check_clickhouse_is_alive()


@TestFeature
@Name("H-19")
def feature(self):
    """[H-19]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
