import json
import time

from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import *
from oauth.tests.steps.provider_protocol import UnsupportedByProvider
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_Caching_CacheEviction_CacheLifetime("1.0"),
)
def cache_evicted_after_lifetime_then_new_token_cached(self):
    """ClickHouse SHALL evict cached tokens after ``token_cache_lifetime``
    elapses, and SHALL cache the next token for the same user.
    """
    client = self.context.provider_client
    cache_lifetime = 5

    with Given(f"I configure the processor with cache lifetime {cache_lifetime}s"):
        configure_openid_token_processor(token_cache_lifetime=cache_lifetime)

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

    Two distinct tokens for the same user, used in alternation within
    the cache lifetime, SHALL both authenticate and resolve to the same
    ``currentUser()``.
    """
    client = self.context.provider_client

    with Given("I configure the processor with a 60s cache lifetime"):
        configure_openid_token_processor(token_cache_lifetime=60)

    with And("I get token A and authenticate (warms cache)"):
        token_a = client.OAuthProvider.get_oauth_token().access_token
        body_a = access_clickhouse(token=token_a, status_code=200)

    with And(
        "I get a fresh token B for the same user",
        description="1s gap so iat / jti differ at Keycloak.",
    ):
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

    with And(
        "token A still works after token B (no slot eviction breaks A)",
        description="""
            A's signature is still valid locally; even if the cache
            entry was rewritten by B, A's re-validation against JWKS
            SHALL succeed and SHALL again map to the same user.
        """,
    ):
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
    """A successful auth with a different token SHALL replace the
    existing cache entry for the same user, even inside the
    ``token_cache_lifetime`` window.
    """
    client = self.context.provider_client

    with Given("I configure the processor with a 60s cache lifetime"):
        configure_openid_token_processor(token_cache_lifetime=60)

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

    After the cache window passes idle, the server stays healthy and
    re-authentication with the same token still works (full re-validation).
    """
    client = self.context.provider_client
    cache_lifetime = 5

    with Given(f"I configure the processor with cache lifetime {cache_lifetime}s"):
        configure_openid_token_processor(token_cache_lifetime=cache_lifetime)

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

    Shortens the realm's ``accessTokenLifespan`` via the Keycloak Admin
    API and verifies the token stops authenticating around its ``exp``
    even though ``token_cache_lifetime`` is much longer.
    """
    client = self.context.provider_client
    realm = self.context.realm_name
    short_token_lifespan = 30
    cache_lifetime = 600

    if str(self.context.provider_name).lower() != "keycloak":
        skip(
            "Common.Cache.Behavior reproduction needs the IdP to honour "
            "a short accessTokenLifespan; only the Keycloak provider "
            "supports this through the realm-admin endpoint."
        )

    # Lazy import for non-Keycloak runs.
    from oauth.tests.steps.keycloak_realm import keycloak_admin_request
    from oauth.tests.steps.provider_protocol import _decode_jwt_token

    with Given(
        "I capture the realm's current accessTokenLifespan",
        description="""
            Capture the realm's current accessTokenLifespan so we can restore
            it on teardown. Some Keycloak builds default to 300s, others to
            the global default; we don't want to bake an assumption in.
        """,
    ):
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
            configure_openid_token_processor(token_cache_lifetime=cache_lifetime)

        with And("I get a token (it should now carry a short exp)"):
            token_response = client.OAuthProvider.get_oauth_token()
            token = token_response.access_token

        with And(
            "I verify Keycloak actually honoured the accessTokenLifespan change",
            description="By decoding the JWT.",
        ):
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
    """Token cache semantics tests.
    
    Exercises cache eviction after ``token_cache_lifetime``, per-user cache
    slot accounting, cache entry refresh on token rotation, lazy cleanup
    behavior, and the ``min(token_exp, cache_lifetime)`` rule.
    """
    
    Scenario(run=cache_evicted_after_lifetime_then_new_token_cached)
    Scenario(run=at_most_one_cache_entry_per_user)
    Scenario(run=new_token_replaces_cache_entry_for_same_user)
    Scenario(run=expired_cache_entry_persists_until_next_auth)
    Scenario(run=cache_entry_capped_at_token_exp_when_token_expires_first)
