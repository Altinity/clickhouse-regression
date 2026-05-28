"""Token cache semantics tests.

These scenarios exercise the cache rules in SRS section 14.3:

- ``CacheEviction.CacheLifetime`` — cached entries are evicted after
  ``token_cache_lifetime`` seconds; the next request SHALL re-validate
  and re-cache.
- ``TokensPerUser`` — ClickHouse SHALL keep at most one cache entry per
  user. Two distinct tokens for the same user authenticate, but they
  share a single cache slot.
- ``CacheEntryRefresh`` — a successful auth with a different token
  SHALL replace the existing cache entry for the same user, even
  while the old entry is still inside its ``token_cache_lifetime``
  window.
- ``LazyCleanup`` — ClickHouse SHALL NOT proactively sweep expired
  entries. They persist until the user authenticates again.
- ``Common.Cache.Behavior`` — when a token's ``exp`` is sooner than
  ``token_cache_lifetime``, the cache entry SHALL only be valid until
  the token's ``exp`` (the shorter of the two limits).

All scenarios are provider-agnostic: tokens are obtained via
``client.OAuthProvider.get_oauth_token(...)`` so swapping
``--identity-provider`` keeps them running.
"""

import json
import time

from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.provider_protocol import UnsupportedByProvider
from testflows.asserts import *
from oauth.requirements.requirements import *


def _configure_cache(self, *, token_cache_lifetime):
    """Apply the standard Keycloak processor with a custom cache lifetime.

    Centralised so each scenario doesn't repeat the same boilerplate.
    """
    client = self.context.provider_client
    endpoints = client.OAuthProvider.openid_endpoints()

    change_token_processors(
        processor_name="keycloak",
        processor_type="OpenID",
        userinfo_endpoint=endpoints.userinfo_endpoint,
        token_introspection_endpoint=endpoints.token_introspection_endpoint,
        introspection_client_id=self.context.introspection_client_id,
        introspection_client_secret=self.context.introspection_client_secret,
        token_cache_lifetime=token_cache_lifetime,
        replace=True,
    )
    change_user_directories_config(
        processor="keycloak",
        common_roles=["general-role"],
    )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_Caching_CacheEviction_CacheLifetime("1.0"),
)
def cache_evicted_after_lifetime_then_new_token_cached(self):
    """ClickHouse SHALL evict cached tokens after ``token_cache_lifetime``
    elapses, and SHALL cache the next token presented for the same user.

    Maps to SRS 14.3.3.1. Observable as: after the eviction window, a
    second (different) token still authenticates correctly — proving
    the eviction did not break re-authentication and that the cache
    refilled with the new token rather than serving a stale entry.
    """
    client = self.context.provider_client
    cache_lifetime = 5

    with Given(f"I configure the processor with cache lifetime {cache_lifetime}s"):
        _configure_cache(self, token_cache_lifetime=cache_lifetime)

    with And("I get token A"):
        token_a = client.OAuthProvider.get_oauth_token().access_token

    with When("I authenticate with token A (warms the cache)"):
        access_clickhouse(token=token_a, status_code=200)

    with And(f"I wait {cache_lifetime + 2}s for the cache entry to expire"):
        time.sleep(cache_lifetime + 2)

    with And("I get a fresh token B for the same user"):
        token_b = client.OAuthProvider.get_oauth_token().access_token
        assert token_b != token_a, error(
            "Keycloak returned the same token on the second call; "
            "eviction-then-refill cannot be observed on identical tokens"
        )

    with Then(
        "ClickHouse re-validates and accepts token B (cache "
        "evicted, new entry created)"
    ):
        access_clickhouse(token=token_b, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_Caching_TokensPerUser("1.0"),
)
def at_most_one_cache_entry_per_user(self):
    """ClickHouse SHALL keep no more than one cache entry per user.

    Maps to SRS 14.3.4.1. We can't introspect the cache directly, so
    we observe the behavioural consequence: two distinct tokens for
    the same user, used in alternation within the cache lifetime,
    SHALL both authenticate and SHALL resolve to the same
    ``currentUser()`` (no cross-user contamination, no separate slot
    silently mis-attributed).
    """
    client = self.context.provider_client

    with Given("I configure the processor with a 60s cache lifetime"):
        _configure_cache(self, token_cache_lifetime=60)

    with And("I get token A and authenticate (warms cache)"):
        token_a = client.OAuthProvider.get_oauth_token().access_token
        body_a = access_clickhouse(token=token_a, status_code=200)

    with And("I get a fresh token B for the same user"):
        # 1s gap so iat / jti differ at Keycloak.
        time.sleep(1)
        token_b = client.OAuthProvider.get_oauth_token().access_token
        assert token_b != token_a, error(
            "Keycloak returned the same token; cannot prove "
            "TokensPerUser without two distinct tokens"
        )

    with When("I authenticate with token B"):
        body_b = access_clickhouse(token=token_b, status_code=200)

    with Then("both tokens resolve to the same currentUser()"):
        assert body_a == body_b, error(
            f"Expected both tokens to map to the same user; got "
            f"A={body_a!r} B={body_b!r}"
        )

    with And("token A still works after token B (no slot eviction breaks A)"):
        # A's signature is still valid locally; even if the cache
        # entry was rewritten by B, A's re-validation against JWKS
        # SHALL succeed and SHALL again map to the same user.
        body_a_again = access_clickhouse(token=token_a, status_code=200)
        assert body_a_again == body_a, error(
            f"After token B, token A no longer resolves to the same "
            f"user: was {body_a!r}, now {body_a_again!r}"
        )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_Caching_CacheEntryRefresh("1.0"),
)
def new_token_replaces_cache_entry_for_same_user(self):
    """A successful authentication with a different token SHALL
    replace the existing cache entry for the same user, even while
    the old entry is still inside its ``token_cache_lifetime``.

    Maps to SRS 14.3.4.2. Observable: after token B's success, both
    A and B continue to authenticate (re-validation works for either
    token regardless of which one currently owns the cache slot).
    The "old entry was removed" property is internal; what we can
    pin is "the system continues to behave correctly when a same-user
    token rotation happens inside the cache window".
    """
    client = self.context.provider_client

    with Given("I configure the processor with a 60s cache lifetime"):
        _configure_cache(self, token_cache_lifetime=60)

    with And("I get token A and authenticate (populates cache for the user)"):
        token_a = client.OAuthProvider.get_oauth_token().access_token
        access_clickhouse(token=token_a, status_code=200)

    with And("I get a fresh token B for the same user (still inside cache window)"):
        time.sleep(1)
        token_b = client.OAuthProvider.get_oauth_token().access_token
        assert token_b != token_a, error(
            "Keycloak returned the same token on the second call"
        )

    with When("I authenticate with token B"):
        access_clickhouse(token=token_b, status_code=200)

    with Then(
        "token A continues to authenticate (re-validation handles "
        "either token regardless of cache ownership)"
    ):
        access_clickhouse(token=token_a, status_code=200)

    with And("token B continues to authenticate"):
        access_clickhouse(token=token_b, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_Caching_LazyCleanup("1.0"),
)
def expired_cache_entry_persists_until_next_auth(self):
    """ClickHouse SHALL NOT proactively sweep expired cache entries.
    They persist (or are at least observable as non-blocking) until
    the next successful authentication for that user.

    Maps to SRS 14.3.4.3. The "persistence" property is internal;
    what we observe is the absence of any side-effect during the idle
    window (no spurious failures, no log spam, no resource exhaustion)
    and that the next auth after the window completes the normal
    re-validation path. We pin those two: idle window passes
    uneventfully, then a fresh auth still works.
    """
    client = self.context.provider_client
    cache_lifetime = 5

    with Given(f"I configure the processor with cache lifetime {cache_lifetime}s"):
        _configure_cache(self, token_cache_lifetime=cache_lifetime)

    with And("I get a token and authenticate (populates cache)"):
        token = client.OAuthProvider.get_oauth_token().access_token
        access_clickhouse(token=token, status_code=200)

    with When(
        f"I idle for {cache_lifetime * 3}s — well past the cache "
        f"lifetime, no other auth happens during this window"
    ):
        time.sleep(cache_lifetime * 3)

    with Then("ClickHouse is still alive (no cleanup-thread crash)"):
        check_clickhouse_is_alive()

    with And(
        "the original token still authenticates — it goes through "
        "full re-validation since the previous cache entry expired "
        "without being touched"
    ):
        access_clickhouse(token=token, status_code=200)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Common_Cache_Behavior("1.0"),
)
def cache_entry_capped_at_token_exp_when_token_expires_first(self):
    """When a token's ``exp`` is sooner than ``token_cache_lifetime``,
    the cache entry SHALL only be valid until the token's ``exp``.

    Maps to SRS 13.1.5 / "Common.Cache.Behavior" (scenario 1):
    *Token expiration: 30 minutes, Cache lifetime: 60 minutes →
    Token cached for 30 minutes (until token expires)*.

    Observable: with ``token_cache_lifetime`` configured well above
    the IdP-issued ``exp``, the token SHALL stop authenticating
    around its ``exp`` — i.e. the cache does not extend the token's
    lifetime past its own ``exp``.

    Setup: shorten the realm's ``accessTokenLifespan`` to 30s via the
    Keycloak Admin API, configure ClickHouse with
    ``token_cache_lifetime=600`` (well above 30s), get a token, use
    it, wait past 30s but well below 600s, retry — SHALL fail.
    """
    client = self.context.provider_client
    realm = self.context.realm_name
    short_token_lifespan = 30
    cache_lifetime = 600

    # The accessTokenLifespan tweak below uses the Keycloak Admin
    # REST API directly. Other providers (Azure / Google) don't expose
    # an equivalent knob through the protocol, and the scenario only
    # makes sense when we can pin the IdP-issued token's exp to a
    # known value, so we skip rather than xfail.
    if str(self.context.provider_name).lower() != "keycloak":
        skip(
            "Common.Cache.Behavior reproduction needs the IdP to honour "
            "a short accessTokenLifespan; only the Keycloak provider "
            "supports this through the realm-admin endpoint."
        )

    # Imported lazily so non-Keycloak runs don't pay the import cost
    # (and so the module remains importable even if the Keycloak
    # provider module ever moves).
    from oauth.tests.steps.keycloak_realm import keycloak_admin_request
    from oauth.tests.steps.provider_protocol import _decode_jwt_token

    # Capture the realm's current accessTokenLifespan so we can restore
    # it on teardown. Some Keycloak builds default to 300s, others to
    # the global default; we don't want to bake an assumption in.
    with Given("I capture the realm's current accessTokenLifespan"):
        status, body = keycloak_admin_request(
            method="GET",
            path=f"/admin/realms/{realm}",
        )
        if status != 200:
            skip(
                f"Keycloak admin GET realm returned {status}: {body[:200]} — "
                f"cannot configure short accessTokenLifespan"
            )
        original = json.loads(body)
        original_lifespan = original.get("accessTokenLifespan")

    try:
        with And(
            f"I shorten the realm's accessTokenLifespan to " f"{short_token_lifespan}s"
        ):
            status, body = keycloak_admin_request(
                method="PUT",
                path=f"/admin/realms/{realm}",
                json_data={"accessTokenLifespan": short_token_lifespan},
            )
            assert status in (200, 204), error(
                f"Keycloak admin PUT realm returned {status}: {body[:200]}"
            )

        with And(
            f"I configure the processor with cache lifetime {cache_lifetime}s "
            f"(>> the {short_token_lifespan}s token lifespan)"
        ):
            _configure_cache(self, token_cache_lifetime=cache_lifetime)

        with And("I get a token (it should now carry a short exp)"):
            token_response = client.OAuthProvider.get_oauth_token()
            token = token_response.access_token

        with And("I verify Keycloak actually honoured the accessTokenLifespan change"):
            # Keycloak's Admin REST API silently ignores accessTokenLifespan
            # on PUT /admin/realms/{realm} — see
            # oauth/requirements/keycloak_actions.md ("Not Configurable via
            # REST"). The PUT returns 204 even though no value changes.
            # ``expires_in`` from the OAuth response can also drift from
            # the token's actual ``exp`` claim (Keycloak computes it from
            # several lifespan settings), so the only fully reliable
            # signal is the JWT itself. Decode it and compare ``exp - iat``
            # against what we asked for.
            _, payload, _ = _decode_jwt_token(token)
            jwt_lifespan = None
            if "exp" in payload and "iat" in payload:
                jwt_lifespan = int(payload["exp"]) - int(payload["iat"])
            if jwt_lifespan is None or jwt_lifespan > short_token_lifespan + 5:
                skip(
                    f"Keycloak issued a token with exp-iat={jwt_lifespan!r} "
                    f"after we requested accessTokenLifespan="
                    f"{short_token_lifespan}s (expires_in="
                    f"{token_response.expires_in!r}). The Admin REST API "
                    f"cannot modify accessTokenLifespan via PUT "
                    f"/admin/realms/{{realm}} — see "
                    f"oauth/requirements/keycloak_actions.md. Reproducing "
                    f"this scenario requires the realm-import workaround, "
                    f"which is not yet wired up."
                )
            wait_seconds = jwt_lifespan + 5

        with When("I authenticate with the token (warms cache)"):
            access_clickhouse(token=token, status_code=200)

        with And(
            f"I wait {wait_seconds}s — past the token's exp but well "
            f"below cache_lifetime"
        ):
            time.sleep(wait_seconds)

        with Then(
            "ClickHouse refuses the token (the cache entry SHALL "
            "have been capped at the token's exp, not extended to "
            "cache_lifetime)"
        ):
            assert_token_rejected(token=token)

    finally:
        with Finally("I restore the original accessTokenLifespan"):
            restore_payload = (
                {"accessTokenLifespan": original_lifespan}
                if original_lifespan is not None
                # If the field was unset originally, send 0 to clear
                # the override; Keycloak treats 0 / -1 as "use realm
                # default".
                else {"accessTokenLifespan": 0}
            )
            try:
                keycloak_admin_request(
                    method="PUT",
                    path=f"/admin/realms/{realm}",
                    json_data=restore_payload,
                )
            except Exception as e:  # noqa: BLE001 — best-effort teardown
                note(f"could not restore accessTokenLifespan: {e}")


@TestFeature
@Name("cache semantics")
@Requirements(
    RQ_SRS_042_OAuth_Authentication_Caching("1.0"),
)
def feature(self):
    """Token cache semantics — eviction, per-user accounting, refresh,
    lazy cleanup, and the min(token_exp, cache_lifetime) rule."""
    Scenario(run=cache_evicted_after_lifetime_then_new_token_cached)
    Scenario(run=at_most_one_cache_entry_per_user)
    Scenario(run=new_token_replaces_cache_entry_for_same_user)
    Scenario(run=expired_cache_entry_persists_until_next_auth)
    Scenario(run=cache_entry_capped_at_token_exp_when_token_expires_first)
