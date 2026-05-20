"""[H-25] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *
from testflows.asserts import *

from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_token_processors,
    change_user_directories_order,
)


@TestScenario
@Name("H-25 / 1")
def scenario_1(self):
    """[H-25]"""
    client = self.context.provider_client

    with Given("a working provider token processor"):
        endpoints = client.OAuthProvider.openid_endpoints()
        change_token_processors(
            processor_name="keycloak",
            processor_type="OpenID",
            token_cache_lifetime=0,
            replace_section=True,
            userinfo_endpoint=endpoints.userinfo_endpoint,
            token_introspection_endpoint=endpoints.token_introspection_endpoint,
            jwks_uri=endpoints.jwks_uri,
        )

    with And("I reorder user_directories so <token> is first and <users_xml> second"):
        change_user_directories_order(
            entries_in_order=[
                (
                    "token",
                    {"processor": "keycloak", "common_roles": {"general-role": {}}},
                ),
                ("users_xml", {"path": "/etc/clickhouse-server/users.xml"}),
            ]
        )

    with When(
        "I attempt a Basic-auth request for the local 'default' user "
        "(empty password)"
    ):
        node = self.context.bash_tools
        url = "http://clickhouse1:8123/?query=SELECT%20currentUser()"
        curl = (
            "curl -s -o /tmp/h25_basic.txt -w '%{http_code}' "
            f"--location '{url}' "
            "--user 'default:'"
        )
        result = node.command(command=curl)
        http_code = result.output.strip()[-3:]

    with Then("[H-25]"):
        assert http_code in ("401", "403", "500"), error()


@TestFeature
@Name("H-25")
def feature(self):
    """[H-25]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
