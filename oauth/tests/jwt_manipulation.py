from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


def _split_jwt(token):
    """Return ``(header, payload, signature)`` segments of a JWT.

    Lightweight string-only split — does NOT base64-decode. Used by
    scenarios that need to look at or replace one segment with another
    string of the same length. Re-using
    ``provider_protocol._decode_jwt_token`` would force a base64 round
    trip we don't want here.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError(f"Expected a 3-part JWT, got {len(parts)} parts")
    return parts[0], parts[1], parts[2]


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
    """ClickHouse SHALL reject a token with alg changed to HS256 (algorithm confusion).

    Uses ``assert_token_rejected`` rather than a pinned status code: per
    ``oauth/KNOWLEDGE.md`` §"HTTP Status Codes" the JWT-rejection path
    consistently surfaces as ``AUTHENTICATION_FAILED`` → HTTP 403; the
    helper accepts any of 401/403/500 with a recognizable rejection
    marker so the test stays correct if upstream consolidates the
    mapping further. See also ``audit-suite-review.md`` §3.2.
    """
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

    The replacement must be **base64url-valid** so that we exercise the
    signature-verification path (which surfaces as
    ``AUTHENTICATION_FAILED`` → HTTP 403). Earlier versions of this
    scenario used the literal string ``"totally-invalid-signature"``;
    that is base64url-clean by alphabet but the wrong length-modulo-4
    after ``jwt-cpp`` pads it, which makes the underlying base64
    decoder throw ``std::runtime_error("Invalid input: too much
    fill")``. ``JwksJwtProcessor::resolveAndValidate`` does not wrap
    ``jwt::decode`` in a top-level ``try/catch`` (unlike
    ``StaticKeyJwtProcessor``), so the exception propagates out as
    ``Code: 1001`` with no rejection marker — the bug is tracked
    separately as ``DEFECT_H16`` (alias ``F20 / TOKEN-06``) in
    ``oauth/tests/defects_catalogue.py`` and
    ``security_audit/jwt_decode_uncaught_exception.py``. Using a
    base64url-clean replacement of correct length here keeps this
    scenario focused on its stated assertion (signature mismatch) and
    avoids accidentally testing the same bug twice.
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
    """ClickHouse SHALL reject a garbage string that is not a valid JWT.

    Currently expected to fail because ``"not.a.valid-jwt"`` triggers
    the same uncaught-exception bug pinned by ``H-16`` (alias
    ``F20 / TOKEN-06``): the second segment ``"a"`` is not a valid
    base64url frame, so ``jwt::decode`` raises
    ``std::runtime_error("Invalid input: too much fill")`` and
    ``JwksJwtProcessor::resolveAndValidate`` lets it leak as
    ``Code: 1001`` (HTTP 500) without an ``AUTHENTICATION_FAILED``
    marker.  Registered in ``oauth/regression.py`` ``xfails`` against
    ``DEFECT_H16``; pull the xfail entry once the fix lands.
    """
    with Then("ClickHouse rejects the garbage token"):
        assert_token_rejected(token="not.a.valid-jwt")


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
