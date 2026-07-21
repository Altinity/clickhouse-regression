from helpers.common import getuid
from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
def failed_auth_quota_not_burned_by_attacker_sub(self):
    """A victim's failed-auth quota SHALL NOT be consumed by an attacker
    who submits invalid tokens carrying the victim's ``sub``: the quota
    is keyed to the authenticated principal, not to the
    attacker-controlled claim.
    """
    uid = getuid()[:6]
    target_user = f"u_{uid}"
    processor_secret = "quota_test_processor_secret"
    other_secret = "quota_test_other_secret"

    with Given("a static-key processor"):
        configure_static_key_processor(secret=processor_secret)

    with And(f"a local user '{target_user}' pinned to the processor"):
        change_user_jwt_auth(username=target_user, processor="proc_a")

    with And(f"a quota limiting '{target_user}' to 3 failed auths per hour"):
        change_user_quota(username=target_user, failed_sequential_authentications=3)

    with When("an attacker sends 3 invalid tokens carrying that sub"):
        for _ in range(3):
            bad_token = create_static_jwt(
                user_name=target_user,
                secret=other_secret,
                algorithm="HS256",
                expiration_minutes=5,
            )
            access_clickhouse(token=bad_token, status_code=403)

    with Then("the victim's own valid token still authenticates (quota not burned)"):
        valid_token = create_static_jwt(
            user_name=target_user,
            secret=processor_secret,
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=valid_token, status_code=200)


@TestFeature
@Name("quotas")
def feature(self):
    """Quota-binding tests: failed-auth quota keyed to the authenticated
    principal rather than an attacker-controlled claim.
    """
    Scenario(run=failed_auth_quota_not_burned_by_attacker_sub)
