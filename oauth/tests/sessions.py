import time

from helpers.common import getuid
from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestScenario
def temp_table_scoped_to_session(self):
    """A temporary table created inside a named session SHALL be visible
    only within that session: a different ``session_id`` SHALL NOT see
    it, so a leaked token cannot ride a victim's live session state.
    """
    client = self.context.provider_client
    sid = "sess_" + getuid()[:8]
    other_sid = "sess_" + getuid()[:8]
    tbl = "t_" + getuid()[:8]

    with Given("a provider OpenID processor"):
        configure_openid_token_processor(token_cache_lifetime=60)

    with And("I get a valid token"):
        token = client.OAuthProvider.get_oauth_token().access_token

    with When(f"I create a temporary table under session_id={sid}"):
        access_clickhouse(
            token=token,
            query=f"CREATE TEMPORARY TABLE {tbl} (x UInt8) ENGINE = Memory",
            query_params={"session_id": sid},
            status_code=200,
        )

    with Then("the table is reachable within the same session"):
        body = access_clickhouse(
            token=token,
            query=f"SELECT count() FROM {tbl}",
            query_params={"session_id": sid},
            status_code=200,
        )
        assert body.strip() == "0", error()

    with And("the table is NOT reachable from a different session_id"):
        access_clickhouse(
            token=token,
            query=f"SELECT count() FROM {tbl}",
            query_params={"session_id": other_sid},
            status_code=500,
        )


@TestScenario
def native_session_revalidated_after_processor_removal(self):
    """An active native TCP session SHALL stop working once the processor
    that authenticated it is removed at config reload (no stale
    ride-through).
    """
    secret = "session_test_secret"

    with Given("a static-key processor"):
        configure_static_key_processor(secret=secret)

    with And("I mint an HS256 token for 'alice'"):
        token = create_static_jwt(
            user_name="alice",
            secret=secret,
            algorithm="HS256",
            expiration_minutes=15,
        )

    with When("I open a native TCP session with --jwt"):
        try:
            session = open_native_jwt_session(
                token=token, container_node="clickhouse1", target_host="clickhouse1"
            )
        except NotImplementedError as e:
            skip(str(e))

    with And("the session is live"):
        body = session.query("SELECT currentUser()")
        assert "alice" in body, error()

    with And("I replace the processors with one that cannot validate the token"):
        configure_static_key_processor(secret="completely_different_secret")

    with Then("the stale session no longer works"):
        try:
            body = session.query("SELECT 1")
        except Exception:
            body = ""
        assert "1" not in body, error("stale session survived processor removal")


@TestScenario
def native_session_bound_to_token_expiry(self):
    """A native TCP session SHALL NOT outlive the token's ``exp``: once
    the token expires, the session SHALL stop authenticating queries.
    """
    secret = "session_exp_test_secret"

    with Given("a static-key processor with token caching disabled"):
        configure_static_key_processor(secret=secret)

    with And("I mint a short-lived token (expires in 1 minute)"):
        token = create_static_jwt(
            user_name="alice",
            secret=secret,
            algorithm="HS256",
            expiration_minutes=1,
        )

    with When("I open a native TCP session with --jwt"):
        try:
            session = open_native_jwt_session(
                token=token, container_node="clickhouse1", target_host="clickhouse1"
            )
        except NotImplementedError as e:
            skip(str(e))

    with And("the session is live"):
        body = session.query("SELECT currentUser()")
        assert "alice" in body, error()

    with And("I sleep past the token's exp (~70s)"):
        time.sleep(70)

    with Then("the session no longer authenticates queries"):
        try:
            body = session.query("SELECT 1")
        except Exception:
            body = ""
        assert "1" not in body, error("session survived token expiration")


@TestFeature
@Name("sessions")
def feature(self):
    """Session-lifetime tests: temp-table isolation across sessions, and
    revalidation of long-lived native sessions on processor removal /
    token expiry.
    """
    Scenario(run=temp_table_scoped_to_session)
    Scenario(run=native_session_revalidated_after_processor_removal)
    Scenario(run=native_session_bound_to_token_expiry)
