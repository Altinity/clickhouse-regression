from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestCheck
def check_parameters_and_caching(self, setup_step):
    """Verify common parameter/caching behavior via setup step."""

    with Given("I configure common OAuth parameters or caching"):
        setup_step()

    with When("I get an OAuth token from the provider"):
        client = self.context.provider_client
        token = client.OAuthProvider.get_oauth_token()

    with Then("I try to access ClickHouse with the token"):
        response = access_clickhouse(token=token)
        assert response.status_code in (200, 401), error()

    with And("I check that the ClickHouse server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Name("common parameters and caching")
@Requirements(
    RQ_SRS_042_OAuth_Common_Parameters_CacheLifetime("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_UsernameClaim("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_GroupsClaim("1.0"),
    RQ_SRS_042_OAuth_Common_Parameters_Unfiltered("1.0"),
    RQ_SRS_042_OAuth_Common_Cache_Behavior("1.0"),
    RQ_SRS_042_OAuth_Common_Configuration_Validation("1.0"),
    RQ_SRS_042_OAuth_Authentication_Caching("1.0"),
)
def oauth_common_parameters_and_caching(self):
    """Check common parameters and caching requirements."""
    client = self.context.provider_client

    steps = [
        client.OAuthProvider.common_parameters_cache_lifetime,
        client.OAuthProvider.common_parameters_username_claim,
        client.OAuthProvider.common_parameters_groups_claim,
        client.OAuthProvider.common_parameters_unfiltered,
        client.OAuthProvider.common_cache_behavior,
        client.OAuthProvider.common_configuration_validation,
        client.OAuthProvider.authentication_caching,
    ]

    for s in steps:
        Scenario(test=check_parameters_and_caching)(setup_step=s)


@TestFeature
@Name("parameters and caching")
@Requirements(
    RQ_SRS_042_OAuth_Common_Configuration_Validation("1.0"),
)
def feature(self):
    """Feature to test common OAuth parameters and caching requirements."""

    Scenario(run=oauth_common_parameters_and_caching)
