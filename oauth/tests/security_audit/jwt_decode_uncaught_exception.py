"""[H-16] Uncaught std::runtime_error from jwt::decode.

See ``oauth/new_audit_review/all-issues.md`` (Series A, H-16) and
``DEFECT_H16`` in ``oauth/tests/defects_catalogue.py``. Legacy aliases:
F20 / TOKEN-06 used in earlier drafts of this suite — same defect.

``JwksJwtProcessor::resolveAndValidate``
(``src/Access/TokenProcessorsJWT.cpp`` in antalya-26.1) calls
``jwt::decode(credentials.getToken())`` as the very first line of its
body — without a top-level ``try { } catch (...)``. Any exception raised
by JWT parsing therefore propagates out of the processor and out of
``ExternalAuthenticators::checkCredentialsAgainstProcessor``,
ultimately surfacing in the HTTP response as a generic ``Code: 1001``
``std::runtime_error`` with the underlying library's error message.

H-16 in ``all-issues.md`` is framed around the iteration-abort
consequence (later processors never tried). The scenarios in this file
pin the *exception-leak* consequence (HTTP 500 + library detail
leakage) of the same root cause. Companion scenario in
``fail_closed_config.py`` (H-16 / 1) pins the iteration-abort angle.

Concrete consequences:

1. ClickHouse's HTTP layer returns 500 with no ``AUTHENTICATION_FAILED``
   marker — the response is indistinguishable from an unrelated server
   crash for any client logic that buckets errors by class.
2. The error body leaks JWT-library implementation detail to the
   client (e.g. the literal text ``"Invalid input: too much fill"``
   from the base64 decoder), which is mild information disclosure but
   undesirable for an authentication path.
3. Comparable code paths handle this correctly:
   ``StaticKeyJwtProcessor::resolveAndValidate`` wraps its body in a
   single ``try { ... } catch (const std::exception & ex) { LOG_TRACE...
   return false; }``; ``OpenIdTokenProcessor::resolveAndValidate`` does
   the same for its ``catch (...)`` fallback. ``JwksJwtProcessor`` only
   catches narrowly-scoped ``claim_not_present_exception`` /
   ``std::bad_cast`` deep inside the x5c block, so anything thrown by
   ``jwt::decode`` itself escapes.

These scenarios are expected to FAIL on current antalya-26.1
(``DEFECT_H16``). They are registered in ``oauth/regression.py`` under
``xfails`` so CI surfaces them as expected failures, not regressions.
Remove the xfail entries once the upstream fix lands — the fix is a
one-line ``try``/``catch`` wrapper around the body of
``JwksJwtProcessor::resolveAndValidate`` mirroring the
``StaticKeyJwtProcessor`` shape.
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
