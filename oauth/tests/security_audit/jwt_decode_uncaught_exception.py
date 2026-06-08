"""[H-16] Uncaught std::runtime_error from jwt::decode.

See ``oauth/new_audit_review/all-issues.md`` (Series A, H-16) and
``DEFECT_H16`` in ``oauth/tests/defects_catalogue.py``. Legacy aliases:
F20 / TOKEN-06 used in earlier drafts of this suite — same defect.

Fixed in antalya-26.3 (PR #1777): ``JwksJwtProcessor::resolveAndValidate``
now wraps its entire body in a ``try { } catch (const std::exception &)``
block, mirroring ``StaticKeyJwtProcessor``. Malformed-token exceptions are
caught, logged at TRACE level, and the processor returns ``false`` so the
iterator can try the next processor. No more HTTP 500 / Code 1001 leakage.
"""

from testflows.core import *

from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    assert_token_rejected,
)


def _swap_jwt_segment(token, index, new_segment):
    """Replace one of the three JWT segments by index. No re-signing."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError(f"Expected 3-part JWT, got {len(parts)}")
    parts[index] = new_segment
    return ".".join(parts)


@TestScenario
@Name("H-16 / 2 malformed signature base64 leaks runtime_error")
def malformed_signature_leaks_runtime_error(self):
    """[H-16]
    A token with a signature segment that is base64url-shaped but has a
    length that ``jwt-cpp``'s ``jwt::base::pad`` /
    ``jwt::base::decode<base64url>`` rejects with
    ``std::runtime_error("Invalid input: too much fill")`` SHALL be
    rejected by ClickHouse as ``AUTHENTICATION_FAILED`` (HTTP 403).
    Currently the exception escapes uncaught from
    ``JwksJwtProcessor::resolveAndValidate``, surfacing as HTTP 500
    with ``Code: 1001`` and a leaked library error message.
    """
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When(
        "I replace the signature segment with a 25-char base64url-clean "
        "value (length 25 + 3 padding chars = 28; jwt-cpp's pad routine "
        "still produces an invalid frame and the decoder raises "
        "'Invalid input: too much fill')"
    ):
        # Same trigger as the original (pre-fix) replace_signature_entirely
        # scenario, kept here intentionally to pin the bug.
        modified = _swap_jwt_segment(token, 2, "totally-invalid-signature")

    with Then(
        "ClickHouse SHALL reject the token through the regular "
        "AUTHENTICATION_FAILED path, not by leaking std::runtime_error"
    ):
        assert_token_rejected(token=modified)


@TestScenario
@Name("H-16 / 3 non-base64 signature leaks runtime_error")
def non_base64_signature_leaks_runtime_error(self):
    """[H-16]
    Variant of H-16 / 2 that uses obvious non-base64 characters in the
    signature segment (``$`` is not in the base64url alphabet). The
    ``jwt::base::decode<base64url>`` call raises
    ``std::runtime_error("Invalid input")``, which escapes
    ``JwksJwtProcessor::resolveAndValidate`` for the same reason: no
    top-level catch.
    """
    client = self.context.provider_client

    with Given("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When(
        "I replace the signature with a string containing characters "
        "that are not in the base64url alphabet"
    ):
        modified = _swap_jwt_segment(token, 2, "$$$$$$$$")

    with Then(
        "ClickHouse SHALL reject the token through the regular "
        "AUTHENTICATION_FAILED path, not by leaking std::runtime_error"
    ):
        assert_token_rejected(token=modified)


@TestFeature
@Name("H-16 jwt decode uncaught")
def feature(self):
    """[H-16] Uncaught std::runtime_error from jwt::decode in
    JwksJwtProcessor::resolveAndValidate.

    Distinct feature name from ``fail_closed_config.py``'s feature
    (which also covers H-16 from the iteration-abort angle) so
    testflows can host both at the same level.
    """
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
