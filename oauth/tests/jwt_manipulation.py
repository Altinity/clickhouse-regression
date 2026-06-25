import datetime

from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import configure_static_key_processor
from testflows.asserts import *
from oauth.requirements.requirements import *

_TAMPERING_SECRET = "jwt_tampering_test_secret_hs256"


def _split_jwt(token):
    """Return ``(header, payload, signature)`` segments of a JWT.

    String-only split — does NOT base64-decode.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError(f"Expected a 3-part JWT, got {len(parts)} parts")
    return parts[0], parts[1], parts[2]


def _swap_jwt_segment(token, index, new_segment):
    """Replace one of the three JWT segments by index (no re-signing)."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError(f"Expected a 3-part JWT, got {len(parts)} parts")
    parts[index] = new_segment
    return ".".join(parts)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Alg("1.0"),
)
def modify_alg_to_none(self):
    """ClickHouse SHALL reject a token with alg changed to 'none'."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When("I change alg to 'none'"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, header_changes={"alg": "none"}
        )

    with Then("ClickHouse rejects the token"):
        access_clickhouse(token=modified, status_code=403)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Alg("1.0"),
)
def modify_alg_to_hs256(self):
    """ClickHouse SHALL reject a token with alg changed to HS256 (algorithm confusion)."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When("I change alg to 'HS256'"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, header_changes={"alg": "HS256"}
        )

    with Then("ClickHouse rejects the token"):
        assert_token_rejected(token=modified)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Typ("1.0"),
)
def modify_typ_to_invalid(self):
    """ClickHouse SHALL reject a token with typ changed to an invalid value."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When("I change typ to 'INVALID'"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, header_changes={"typ": "INVALID"}
        )

    with Then("ClickHouse rejects the token"):
        assert_token_rejected(token=modified)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
)
def modify_kid_to_invalid(self):
    """ClickHouse SHALL reject a token with kid changed to an unknown key ID."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When("I change kid to a non-existent key ID"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, header_changes={"kid": "non-existent-key-id"}
        )

    with Then("ClickHouse rejects the token"):
        assert_token_rejected(token=modified)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Exp("1.0"),
)
def modify_exp_to_past(self):
    """ClickHouse SHALL reject a token with exp set to a past timestamp."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When("I set exp to epoch 1000000000 (2001)"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, payload_changes={"exp": 1000000000}
        )

    with Then("ClickHouse rejects the expired token"):
        assert_token_rejected(token=modified)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Sub("1.0"),
)
def modify_sub_to_invalid(self):
    """ClickHouse SHALL reject a token with sub changed (signature mismatch)."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When("I change the sub claim"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, payload_changes={"sub": "invalid-subject-id"}
        )

    with Then("ClickHouse rejects the token"):
        assert_token_rejected(token=modified)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Aud("1.0"),
)
def modify_azp_to_invalid(self):
    """ClickHouse SHALL reject a token with azp changed (signature mismatch)."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When("I change the azp claim"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, payload_changes={"azp": "invalid-client-id"}
        )

    with Then("ClickHouse rejects the token"):
        assert_token_rejected(token=modified)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
)
def replace_signature_entirely(self):
    """ClickHouse SHALL reject a token with a completely replaced signature.

    The replacement is base64url-valid so we exercise the
    signature-verification path rather than a decoding error.
    """
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When(
        "I replace the signature with base64url-valid garbage of "
        "matching length (decodes cleanly, but verifies to nothing)"
    ):
        _, _, original_signature = _split_jwt(token)
        garbage = "A" * len(original_signature)
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, signature_change=garbage
        )

    with Then("ClickHouse rejects the token"):
        assert_token_rejected(token=modified)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
)
def remove_signature(self):
    """ClickHouse SHALL reject a token with an empty signature."""
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When("I remove the signature"):
        modified = client.OAuthProvider.modify_jwt_token(
            token=token, signature_change=""
        )

    with Then("ClickHouse rejects the token"):
        assert_token_rejected(token=modified)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_TokenHandling_EmptyString("1.0"),
)
def empty_token(self):
    """ClickHouse SHALL reject an empty token with HTTP 403."""
    with Then("ClickHouse rejects the empty token"):
        access_clickhouse(token="", status_code=403)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_TokenHandling_Incorrect("1.0"),
)
def malformed_token_string(self):
    """ClickHouse SHALL reject a garbage string that is not a valid JWT."""
    with Then("ClickHouse rejects the garbage token"):
        assert_token_rejected(token="not.a.valid-jwt")


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
)
def malformed_base64_signature_rejected_gracefully(self):
    """A token whose signature segment is base64url-malformed SHALL be
    rejected through the normal authentication-failed path, not by
    leaking an uncaught decode exception (HTTP 500 / Code 1001).
    """
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When("I replace the signature with a base64url-malformed value"):
        modified = _swap_jwt_segment(token, 2, "totally-invalid-signature")

    with Then("ClickHouse rejects the token gracefully"):
        assert_token_rejected(token=modified)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
)
def non_base64_signature_rejected_gracefully(self):
    """A token whose signature segment contains characters outside the
    base64url alphabet SHALL be rejected gracefully (no leaked
    ``std::runtime_error``).
    """
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When("I replace the signature with non-base64url characters"):
        modified = _swap_jwt_segment(token, 2, "$$$$$$$$")

    with Then("ClickHouse rejects the token gracefully"):
        assert_token_rejected(token=modified)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Typ("1.0"),
)
def mismatched_typ_rejected(self):
    """When the processor pins ``expected_typ``, a token whose ``typ``
    header does not match SHALL be rejected, preventing ID-token /
    wrong-token-class substitution.
    """
    with Given("I configure a static-key processor that requires typ=JWT"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="HS256",
            static_key=_TAMPERING_SECRET,
            token_cache_lifetime=0,
            expected_typ="JWT",
            replace_section=True,
        )
        change_user_directories_config(
            processor="proc_a",
            common_roles=["general-role"],
        )

    with When("I mint a token with the matching typ=JWT"):
        good_token = create_static_jwt(
            user_name="alice",
            secret=_TAMPERING_SECRET,
            algorithm="HS256",
            headers={"typ": "JWT"},
            expiration_minutes=5,
        )

    with And("I mint a token with a mismatched typ=id+jwt"):
        id_token = create_static_jwt(
            user_name="alice",
            secret=_TAMPERING_SECRET,
            algorithm="HS256",
            headers={"typ": "id+jwt"},
            expiration_minutes=5,
        )

    with Then("ClickHouse accepts the matching typ"):
        access_clickhouse(token=good_token, status_code=200)

    with And("ClickHouse rejects the mismatched typ"):
        assert_token_rejected(token=id_token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Exp("1.0"),
)
def future_iat_rejected(self):
    """A token whose ``iat`` is set well into the future SHALL be
    rejected (no replay-before-issue window).
    """
    with Given("I configure a static-key processor"):
        configure_static_key_processor(secret=_TAMPERING_SECRET)

    with When("I mint a token with iat 5 minutes in the future"):
        future_iat = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=5
        )
        token = create_static_jwt(
            payload={"sub": "alice", "iat": future_iat},
            secret=_TAMPERING_SECRET,
            algorithm="HS256",
            expiration_minutes=15,
        )

    with Then("ClickHouse rejects the future-iat token"):
        assert_token_rejected(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Typ("1.0"),
)
def unknown_crit_header_rejected(self):
    """A token carrying an unrecognised ``crit`` header extension SHALL
    be rejected (RFC 7515 critical-extension handling).
    """
    with Given("I configure a static-key processor"):
        configure_static_key_processor(secret=_TAMPERING_SECRET)

    with When("I mint a token with an unknown crit extension"):
        token = create_static_jwt(
            user_name="alice",
            secret=_TAMPERING_SECRET,
            algorithm="HS256",
            headers={"crit": ["urn:example:unknown-extension"]},
            expiration_minutes=5,
        )

    with Then("ClickHouse rejects the token"):
        assert_token_rejected(token=token)


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
    # Scenario(run=modify_alg_to_none)
    # Scenario(run=modify_alg_to_hs256)
    # Scenario(run=modify_typ_to_invalid)
    # Scenario(run=modify_kid_to_invalid)
    # Scenario(run=modify_exp_to_past)
    # Scenario(run=modify_sub_to_invalid)
    # Scenario(run=modify_azp_to_invalid)
    # Scenario(run=replace_signature_entirely)
    # Scenario(run=remove_signature)
    # Scenario(run=empty_token)
    # Scenario(run=malformed_token_string)
    Scenario(run=malformed_base64_signature_rejected_gracefully)
    Scenario(run=non_base64_signature_rejected_gracefully)
    Scenario(run=mismatched_typ_rejected)
    Scenario(run=future_iat_rejected)
    Scenario(run=unknown_crit_header_rejected)
