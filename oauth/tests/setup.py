from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestCheck
def verify_keycloak_realm_setup(self, realm_setup_step):
    """Verify Keycloak realm setup support."""

    with Given("I prepare Keycloak realm setup"):
        realm_setup_step()

    with When("I get an OAuth token from the provider"):
        client = self.context.provider_client
        token = client.OAuthProvider.get_oauth_token()

    with Then("I try to access ClickHouse with the token"):
        response = access_clickhouse(token=token)
        assert response.status_code == 200, error()

    with And("I check that the ClickHouse server is still alive"):
        check_clickhouse_is_alive()


@TestSketch(Scenario)
@Requirements(RQ_SRS_042_OAuth_Keycloak_RealmSetup("1.0"))
def realm_setup_scenarios(self):
    """Check Keycloak realm setup."""
    client = self.context.provider_client

    verify_keycloak_realm_setup(realm_setup_step=client.OAuthProvider.realm_setup)


@TestFeature
@Name("setup")
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_RealmSetup("1.0"),
)
def feature(self):
    """Feature to test Keycloak setup requirements."""

    Scenario(run=realm_setup_scenarios)
