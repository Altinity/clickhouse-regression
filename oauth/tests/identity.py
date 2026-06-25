from helpers.common import getuid
from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import *
from testflows.asserts import *
from oauth.requirements.requirements import *

_SECRET = "identity_test_secret_hs256"


@TestScenario
def same_sub_from_different_processors_maps_to_one_user(self):
    """Two token processors that each authenticate a token with the same
    ``sub`` claim SHALL map to a single ClickHouse user.

    Accepted finding H-23 (by design): the ``sub`` claim is the username
    identity in ClickHouse's token-user model, so identical ``sub``
    values from different IdPs intentionally resolve to the same user.
    Operators who need distinct users configure non-colliding ``sub``
    claims (or select a unique ``username_claim``).
    """
    secret_a = "identity_secret_a"
    secret_b = "identity_secret_b"
    node = self.context.node

    with Given("two static-key processors with different secrets"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="HS256",
            static_key=secret_a,
            token_cache_lifetime=0,
            replace_section=True,
        )
        change_token_processors(
            processor_name="proc_b",
            processor_type="jwt_static_key",
            algo="HS256",
            static_key=secret_b,
            token_cache_lifetime=0,
        )
        change_user_directories_config(
            processor="proc_a",
            common_roles=["general-role"],
        )

    with When("I mint an 'alice' token signed by each processor"):
        token_a = create_static_jwt(
            user_name="alice",
            secret=secret_a,
            algorithm="HS256",
            expiration_minutes=5,
        )
        token_b = create_static_jwt(
            user_name="alice",
            secret=secret_b,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with And("both tokens authenticate"):
        access_clickhouse(token=token_a, status_code=200)
        access_clickhouse(token=token_b, status_code=200)

    with Then("both tokens resolve to the same single ClickHouse user"):
        result = node.query("SELECT count() FROM system.users WHERE name = 'alice'")
        assert int(result.output.strip()) == 1, error(
            "expected the shared sub to map to exactly one ClickHouse user"
        )


@TestScenario
def empty_sub_claim_rejected(self):
    """A token whose username (``sub``) claim is empty SHALL be rejected,
    rather than collapsing many principals into one empty-named user.
    """
    with Given("a static-key processor"):
        configure_static_key_processor(secret=_SECRET)

    with When("I mint two tokens with an empty sub"):
        token_1 = create_static_jwt(
            payload={"sub": ""},
            secret=_SECRET,
            algorithm="HS256",
            expiration_minutes=5,
        )
        token_2 = create_static_jwt(
            payload={"sub": "", "nonce": "distinguisher"},
            secret=_SECRET,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then("both empty-sub tokens are rejected"):
        assert_token_rejected(token=token_1)
        assert_token_rejected(token=token_2)


@TestScenario
def unicode_homograph_sub_rejected(self):
    """A token whose ``sub`` is a Unicode homograph of an ASCII name
    (Cyrillic 'аlice', U+0430) SHALL NOT silently create a second,
    visually-identical principal.
    """
    with Given("a static-key processor"):
        configure_static_key_processor(secret=_SECRET)

    with When("I authenticate as ASCII 'alice'"):
        token_ascii = create_static_jwt(
            user_name="alice",
            secret=_SECRET,
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token_ascii, status_code=200)

    with And("I mint a token for Cyrillic 'аlice' (U+0430)"):
        token_cyrillic = create_static_jwt(
            user_name="аlice",
            secret=_SECRET,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then("the homograph principal is rejected (confusable-name guard)"):
        assert_token_rejected(token=token_cyrillic)


@TestFeature
@Name("identity")
def feature(self):
    """Principal-identity tests.

    Covers the accepted by-design behaviour that identical ``sub`` claims
    share one ClickHouse user (H-23), plus the empty-name and
    Unicode-homograph guards that are NOT accepted findings.
    """
    Scenario(run=same_sub_from_different_processors_maps_to_one_user)
    Scenario(run=empty_sub_claim_rejected)
    Scenario(run=unicode_homograph_sub_rejected)
