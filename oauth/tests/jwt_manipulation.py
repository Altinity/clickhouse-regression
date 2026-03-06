from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Alg("1.0"),
)
def modify_alg_to_none(self):
    """ClickHouse SHALL reject a token with alg changed to 'none'."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I change alg to 'none'"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, header_changes={"alg": "none"}
        )

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Alg("1.0"),
)
def modify_alg_to_hs256(self):
    """ClickHouse SHALL reject a token with alg changed to HS256 (algorithm confusion)."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I change alg to 'HS256'"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, header_changes={"alg": "HS256"}
        )

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Typ("1.0"),
)
def modify_typ_to_invalid(self):
    """ClickHouse SHALL reject a token with typ changed to an invalid value."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I change typ to 'INVALID'"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, header_changes={"typ": "INVALID"}
        )

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
)
def modify_kid_to_invalid(self):
    """ClickHouse SHALL reject a token with kid changed to an unknown key ID."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I change kid to a non-existent key ID"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, header_changes={"kid": "non-existent-key-id"}
        )

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Exp("1.0"),
)
def modify_exp_to_past(self):
    """ClickHouse SHALL reject a token with exp set to a past timestamp."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I set exp to epoch 1000000000 (2001)"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, payload_changes={"exp": 1000000000}
        )

    with Then("ClickHouse rejects the expired token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Sub("1.0"),
)
def modify_sub_to_invalid(self):
    """ClickHouse SHALL reject a token with sub changed (signature mismatch)."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I change the sub claim"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, payload_changes={"sub": "invalid-subject-id"}
        )

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Aud("1.0"),
)
def modify_azp_to_invalid(self):
    """ClickHouse SHALL reject a token with azp changed (signature mismatch)."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I change the azp claim"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, payload_changes={"azp": "invalid-client-id"}
        )

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
)
def replace_signature_entirely(self):
    """ClickHouse SHALL reject a token with a completely replaced signature."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I replace the signature with garbage"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, signature_change="totally-invalid-signature"
        )

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
)
def remove_signature(self):
    """ClickHouse SHALL reject a token with an empty signature."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token()["access_token"]

    with When("I remove the signature"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, signature_change=""
        )

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=modified, status_code=500)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_TokenHandling_EmptyString("1.0"),
)
def empty_token(self):
    """ClickHouse SHALL reject an empty token with HTTP 401."""
    with Then("ClickHouse rejects the empty token"):
        access_clickhouse(token="", status_code=401)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_TokenHandling_Incorrect("1.0"),
)
def malformed_token_string(self):
    """ClickHouse SHALL reject a garbage string that is not a valid JWT."""
    with Then("ClickHouse rejects the garbage token"):
        access_clickhouse(token="not.a.valid-jwt", status_code=500)


@TestFeature
@Name("jwt_manipulation")
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Alg("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Typ("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Sub("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Aud("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Exp("1.0"),
    RQ_SRS_042_OAuth_Authentication_TokenHandling_Incorrect("1.0"),
    RQ_SRS_042_OAuth_Authentication_TokenHandling_EmptyString("1.0"),
)
def feature(self):
    """Test OAuth authentication with manipulated JWT tokens."""
    Scenario(run=modify_alg_to_none)
    Scenario(run=modify_alg_to_hs256)
    Scenario(run=modify_typ_to_invalid)
    Scenario(run=modify_kid_to_invalid)
    Scenario(run=modify_exp_to_past)
    Scenario(run=modify_sub_to_invalid)
    Scenario(run=modify_azp_to_invalid)
    Scenario(run=replace_signature_entirely)
    Scenario(run=remove_signature)
    Scenario(run=empty_token)
    Scenario(run=malformed_token_string)
