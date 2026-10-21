import os
import re

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.tests.iceberg_engine.token_forwarding.steps import *

ROLE_SESSION_NAME = re.compile(r"^[\w+=,.@-]{2,64}$")


def glue_reachable():
    """Glue calls after STS succeed only when LocalStack (Pro) is running."""
    return bool(os.getenv("LOCALSTACK_AUTH_TOKEN"))


@TestScenario
def each_user_assumes_the_role_with_their_token(self):
    """Check that ClickHouse SHALL call AssumeRoleWithWebIdentity with the
    configured role, the querying user's token and a role session name derived
    from the user, once per user."""
    alice, bob = make_token("alice"), make_token("bob")

    with Given("a Glue forwarding database"):
        clean_mocks()
        database = forwarding_database(catalog="glue")

    with When("alice and bob list the tables"):
        for token in (alice, bob):
            result = jwt_query(
                sql=f"SHOW TABLES FROM {database}", token=token, no_checks=True
            )
            if glue_reachable():
                assert result.exitcode == 0, error(result.output)

    with Then("STS received one unsigned request per user with that user's token"):
        sessions = sts_requests()
        assert len(sessions) == 2, error()
        assert [r["action"] for r in sessions] == [
            "AssumeRoleWithWebIdentity"
        ] * 2, error()
        assert [r["role_arn"] for r in sessions] == [ROLE_ARN] * 2, error()
        assert [r["web_identity_token"] for r in sessions] == [alice, bob], error()
        assert [r["role_session_name"] for r in sessions] == ["alice", "bob"], error()
        assert all(r["authorization"] is None for r in sessions), error()


@TestScenario
def assumed_role_client_is_cached_per_token(self):
    """Check that ClickHouse SHALL reuse the assumed-role client for repeated
    queries with the same token and count `DataLakeGlueCatalogUserClientCacheHits`."""
    if not glue_reachable():
        skip("needs LocalStack (LOCALSTACK_AUTH_TOKEN) for successful Glue calls")

    node = self.context.node
    alice = make_token("alice")
    query_id = f"glue_cached_{getuid()}"

    with Given("a Glue forwarding database"):
        clean_mocks()
        database = forwarding_database(catalog="glue")

    with When("alice lists the tables twice"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)
        jwt_query(
            sql=f"SHOW TABLES FROM {database}",
            token=alice,
            settings=[("query_id", query_id)],
        )

    with Then("the role was assumed once"):
        assert len(sts_requests()) == 1, error()
        assert (
            query_log_profile_event(
                node, query_id, "DataLakeGlueCatalogUserClientCacheHits"
            )
            > 0
        ), error()


@TestScenario
def rejected_token_does_not_fall_back(self):
    """Check that when STS rejects the user's token ClickHouse SHALL fail with
    CATALOG_USER_TOKEN_NOT_AVAILABLE naming the role, SHALL NOT fall back to
    other credentials and SHALL count the failure."""
    node = self.context.node
    token = make_token("mallory")
    query_id = f"glue_rejected_{getuid()}"

    with Given("a Glue forwarding database and an STS that rejects mallory"):
        clean_mocks()
        configure_mocks(sts={"reject_subs": ["mallory"]})
        database = forwarding_database(catalog="glue")
        failures = event_value(
            node, "DataLakeGlueCatalogAssumeRoleWithWebIdentityFailures"
        )

    with When("mallory lists the tables"):
        result = jwt_query(
            sql=f"SHOW TABLES FROM {database}",
            token=token,
            settings=[("query_id", query_id)],
            no_checks=True,
        )

    with Then("the query fails with a role assumption error"):
        assert result.exitcode == CATALOG_USER_TOKEN_NOT_AVAILABLE, error(result.output)
        assert "Could not assume role" in result.output, error(result.output)
        assert ROLE_ARN in result.output, error(result.output)

    with And("the error does not contain the token"):
        assert token not in result.output, error()

    with And("STS was asked once and the failure was counted"):
        assert len(sts_requests()) == 1, error()
        assert (
            event_value(node, "DataLakeGlueCatalogAssumeRoleWithWebIdentityFailures")
            > failures
        ), error()


@TestScenario
def password_user_is_denied(self):
    """Check that a Glue forwarding database SHALL refuse users without a
    token and SHALL NOT call STS."""
    with Given("a Glue forwarding database"):
        clean_mocks()
        database = forwarding_database(catalog="glue")

    with When("the default user lists the tables"):
        self.context.node.query(
            f"SHOW TABLES FROM {database}",
            exitcode=CATALOG_USER_TOKEN_NOT_AVAILABLE,
            ignore_exception=True,
            message=NO_TOKEN_MESSAGE,
        )

    with Then("STS was not called"):
        assert sts_requests() == [], error()


@TestScenario
def role_session_name_is_sanitized(self):
    """Check that a user name with characters AWS does not allow SHALL be
    turned into a valid role session name that is unique per user."""
    subs = [
        "user name/with spaces",
        "user name/with:spaces",
        "u" * 80,
        "ключ",
    ]

    with Given("a Glue forwarding database"):
        clean_mocks()
        database = forwarding_database(catalog="glue")

    with When("users with unusual names list the tables"):
        for sub in subs:
            jwt_query(
                sql=f"SHOW TABLES FROM {database}",
                token=make_token(sub),
                no_checks=True,
            )

    with Then("every role session name is valid for AWS"):
        names = [r["role_session_name"] for r in sts_requests()]
        assert len(names) == len(subs), error()
        for name in names:
            assert ROLE_SESSION_NAME.match(name), error(name)

    with And("different users get different names"):
        assert len(set(names)) == len(names), error()


@TestFeature
@Name("glue")
def feature(self):
    """`oauth_forward_user_token` for Glue: AssumeRoleWithWebIdentity per user."""
    self.context.catalog = "glue"
    try:
        for scenario in loads(current_module(), Scenario):
            Scenario(run=scenario, flags=TE)
    finally:
        self.context.catalog = "rest"
