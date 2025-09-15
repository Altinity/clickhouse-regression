from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *
import json
import time
import base64


def _base64url_encode_json(data: dict) -> str:
    """Encode a dict to base64url without padding."""
    json_bytes = json.dumps(data, separators=(",", ":"), sort_keys=True).encode()
    b64 = base64.urlsafe_b64encode(json_bytes).decode().rstrip("=")
    return b64


def _build_jwt(header: dict, payload: dict, signature: str = "invalid") -> str:
    """Compose a JWT string with provided header, payload and dummy signature."""
    return f"{_base64url_encode_json(header)}.{_base64url_encode_json(payload)}.{signature}"


def _default_payload(
    sub: str = "demo", aud: str = "clickhouse", exp: int | None = None
) -> dict:
    now = int(time.time())
    return {
        "sub": sub,
        "aud": aud,
        "iat": now,
        "exp": now + 3600 if exp is None else exp,
    }


@TestCheck
def verify_keycloak_tokens_flow(self, config_step):
    """Verify Keycloak token processing behavior."""

    with Given("I set Keycloak token-related configuration"):
        config_step()

    with When("I get an OAuth token from the provider"):
        client = self.context.provider_client
        token = client.OAuthProvider.get_oauth_token()

    with Then("I try to access ClickHouse with the token"):
        # response = access_clickhouse(token=token)
        # assert response.status_code == 200, error()
        pass

    with And("I check that the ClickHouse server is still alive"):
        check_clickhouse_is_alive()


@TestSketch(Scenario)
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_AccessTokenSupport("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes_Fallback("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Tokens_Configuration_Validation("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Tokens_Operational_ProviderType("1.0"),
)
def tokens_scenarios(self):
    """Check Keycloak token requirements."""
    client = self.context.provider_client

    configurations = [
        client.OAuthProvider.access_token_support,
        client.OAuthProvider.tokens_operation_modes,
        client.OAuthProvider.tokens_operation_modes_fallback,
        client.OAuthProvider.tokens_configuration_validation,
        client.OAuthProvider.tokens_operational_provider_type,
    ]

    for i in configurations:
        verify_keycloak_tokens_flow(config_step=i)


# Incorrect token generators


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Alg("1.0"))
def token_with_unsupported_alg(self) -> str:
    header = {"alg": "HS1024", "typ": "JWT"}
    payload = _default_payload()
    return _build_jwt(header, payload, signature="sig")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Typ("1.0"))
def token_with_unsupported_typ(self) -> str:
    header = {"alg": "HS256", "typ": "JWE"}
    payload = _default_payload()
    return _build_jwt(header, payload, signature="sig")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"))
def token_with_invalid_signature(self) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = _default_payload()
    return _build_jwt(header, payload, signature="invalid-signature")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Sub("1.0"))
def token_with_unknown_sub(self) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = _default_payload(sub="nonexistent-user")
    return _build_jwt(header, payload, signature="sig")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Aud("1.0"))
def token_with_invalid_aud(self) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = _default_payload(aud="unexpected-audience")
    return _build_jwt(header, payload, signature="sig")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Exp("1.0"))
def token_with_expired_exp(self) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    expired_ts = int(time.time()) - 3600
    payload = _default_payload(exp=expired_ts)
    return _build_jwt(header, payload, signature="sig")


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_TokenHandling_Incorrect("1.0"))
def token_malformed(self) -> str:
    return "not.a.valid-jwt"


@TestStep(Given)
@Requirements(RQ_SRS_042_OAuth_Authentication_TokenHandling_EmptyString("1.0"))
def token_empty_string(self) -> str:
    return ""


@TestCheck
def try_access_with_incorrect_token(self, token_step):
    """Obtain incorrect token and try to access ClickHouse (no real request)."""

    with Given("I generate an incorrect token"):
        token = token_step()
        note(token)

    with Then("I try to access ClickHouse with the token"):
        # response = access_clickhouse(token=token)
        # assert response.status_code == 401, error()
        pass

    with And("I check that the ClickHouse server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
def incorrect_tokens(self):
    """Check ClickHouse behavior with incorrect access tokens."""
    generators = [
        token_with_unsupported_alg,
        token_with_unsupported_typ,
        token_with_invalid_signature,
        token_with_unknown_sub,
        token_with_invalid_aud,
        token_with_expired_exp,
        token_malformed,
        token_empty_string,
    ]

    for i in generators:
        try_access_with_incorrect_token(token_step=i)


@TestFeature
@Name("tokens")
@Requirements(
    RQ_SRS_042_OAuth_Keycloak_AccessTokenSupport("1.0"),
    RQ_SRS_042_OAuth_Keycloak_Tokens_OperationModes("1.0"),
    RQ_SRS_042_OAuth_IdentityProviders_AccessTokenProcessors("1.0"),
)
def feature(self):
    """Feature to test Keycloak token requirements."""

    Scenario(run=tokens_scenarios)
    Scenario(run=incorrect_tokens)
