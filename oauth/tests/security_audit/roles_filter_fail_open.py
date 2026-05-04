"""[H-06] See ``oauth/new_audit_review/combined-issues.md``."""

from testflows.core import *

from helpers.common import getuid
from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    change_user_directories_config,
)
from oauth.tests.steps.provider_protocol import UnsupportedByProvider


@TestScenario
@Name("H-06 / 1")
def scenario_1(self):
    """[H-06]"""
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"u_{uid}"

    with Given(f"I create a user '{username}' with no groups"):
        try:
            client.OAuthProvider.create_user(
                username=username, password="testpass123"
            )
        except UnsupportedByProvider as e:
            skip(str(e))

    try:
        with And("I configure user directories with a malformed roles_filter regex"):
            change_user_directories_config(
                processor="keycloak",
                common_roles=["general-role"],
                roles_filter="[invalid-regex",
            )

        with And(f"I get a token for '{username}'"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            ).access_token

        with Then("[H-06]"):
            access_clickhouse(token=token, status_code=200)

    finally:
        with Finally("I clean up"):
            try:
                client.OAuthProvider.delete_user(username=username)
            except UnsupportedByProvider:
                pass


@TestScenario
@Name("H-06 / 2")
def scenario_2(self):
    """[H-06]"""
    client = self.context.provider_client
    uid = getuid()[:8]
    username = f"u_{uid}"

    with Given(f"I create a user '{username}'"):
        try:
            client.OAuthProvider.create_user(
                username=username, password="testpass123"
            )
        except UnsupportedByProvider as e:
            skip(str(e))

    try:
        with And(
            "I configure user directories with a filter that excludes the user's groups"
        ):
            change_user_directories_config(
                processor="keycloak",
                common_roles=["general-role"],
                roles_filter="^this-matches-nothing$",
            )

        with And(f"I get a token for '{username}'"):
            token = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            ).access_token

        with Then("baseline"):
            access_clickhouse(token=token, status_code=200)

        with When("I reconfigure with a malformed regex"):
            change_user_directories_config(
                processor="keycloak",
                common_roles=["general-role"],
                roles_filter="[broken",
            )

        with And("I get a fresh token"):
            token2 = client.OAuthProvider.get_oauth_token(
                username=username, password="testpass123"
            ).access_token

        with Then("[H-06]"):
            access_clickhouse(token=token2, status_code=200)

    finally:
        with Finally("I clean up"):
            try:
                client.OAuthProvider.delete_user(username=username)
            except UnsupportedByProvider:
                pass


@TestFeature
@Name("H-06")
def feature(self):
    """[H-06]"""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
