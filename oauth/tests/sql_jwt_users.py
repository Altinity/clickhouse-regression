from helpers.common import getuid
from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import (
    access_clickhouse,
    alter_sql_jwt_user,
    assert_token_rejected,
    change_token_processors,
    change_user_directories_config,
    check_clickhouse_is_alive,
    create_sql_jwt_user,
    show_create_user,
)
from oauth.requirements.requirements import *
from testflows.asserts import error
from testflows.core import *

_PROC_A = "proc_a"
_SECRET_A = "sql_jwt_test_secret_a_hs256"
_PROC_B = "proc_b"
_SECRET_B = "sql_jwt_test_secret_b_hs256"


@TestStep(Given)
def two_static_key_processors(self):
    """Configure two ``jwt_static_key`` processors with different secrets
    and a token user-directory entry so the token-auth pipeline is fully
    wired.
    """
    with By(f"replacing all processors with '{_PROC_A}'"):
        change_token_processors(
            processor_name=_PROC_A,
            processor_type="jwt_static_key",
            algo="HS256",
            static_key=_SECRET_A,
            token_cache_lifetime=0,
            replace_section=True,
        )

    with And(f"adding '{_PROC_B}' alongside"):
        change_token_processors(
            processor_name=_PROC_B,
            processor_type="jwt_static_key",
            algo="HS256",
            static_key=_SECRET_B,
            token_cache_lifetime=0,
        )

    with And("pointing the token user-directory at proc_a"):
        change_user_directories_config(
            processor=_PROC_A,
            common_roles=["general-role"],
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_SQLJWTUsers_CreateUser("1.0"))
def create_bare_jwt_user(self):
    """``CREATE USER ... IDENTIFIED WITH jwt`` SHALL succeed without
    ``PROCESSOR`` or ``CLAIMS`` and the user SHALL authenticate with a
    token validated by any configured processor.
    """
    uid = getuid()[:8]
    username = f"jwt_bare_{uid}"

    with Given("two static-key processors are configured"):
        two_static_key_processors()

    with And(f"I create user {username} with bare jwt auth"):
        create_sql_jwt_user(username=username)

    with Then("SHOW CREATE USER reflects the jwt auth type"):
        ddl = show_create_user(username)
        assert "jwt" in ddl.lower(), error(f"Expected 'jwt' in: {ddl}")

    with And("a token signed by any configured processor authenticates"):
        token = create_static_jwt(
            user_name=username,
            secret=_SECRET_A,
            algorithm="HS256",
            expiration_minutes=5,
        )
        body = access_clickhouse(token=token, status_code=200)
        assert username in body, error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_SQLJWTUsers_CreateUser("1.0"),
    RQ_SRS_042_OAuth_SQLJWTUsers_ProcessorClause("1.0"),
)
def create_jwt_user_with_processor_roundtrip(self):
    """``PROCESSOR '<name>'`` SHALL round-trip through
    ``SHOW CREATE USER``.
    """
    uid = getuid()[:8]
    username = f"jwt_proc_rt_{uid}"

    with Given("two static-key processors are configured"):
        two_static_key_processors()

    with And(f"I create {username} pinned to {_PROC_A}"):
        create_sql_jwt_user(username=username, processor=_PROC_A)

    with Then("SHOW CREATE USER contains the PROCESSOR clause"):
        ddl = show_create_user(username)
        assert f"PROCESSOR \\'{_PROC_A}\\'" in ddl, error(
            f"Missing PROCESSOR in: {ddl}"
        )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_SQLJWTUsers_CreateUser("1.0"),
    RQ_SRS_042_OAuth_SQLJWTUsers_ClaimsClause("1.0"),
)
def create_jwt_user_with_claims_roundtrip(self):
    """``CLAIMS '<json>'`` SHALL round-trip through
    ``SHOW CREATE USER``.
    """
    uid = getuid()[:8]
    username = f"jwt_claims_rt_{uid}"

    with Given("two static-key processors are configured"):
        two_static_key_processors()

    with And(f"I create {username} with a claims requirement"):
        create_sql_jwt_user(username=username, claims={"role": "tester"})

    with Then("SHOW CREATE USER contains the CLAIMS clause"):
        ddl = show_create_user(username)
        assert "CLAIMS" in ddl, error(f"Missing CLAIMS in: {ddl}")


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_SQLJWTUsers_CreateUser("1.0"),
    RQ_SRS_042_OAuth_SQLJWTUsers_ProcessorClause("1.0"),
    RQ_SRS_042_OAuth_SQLJWTUsers_ClaimsClause("1.0"),
)
def create_jwt_user_with_processor_and_claims_roundtrip(self):
    """Both ``PROCESSOR`` and ``CLAIMS`` SHALL round-trip together."""
    uid = getuid()[:8]
    username = f"jwt_both_rt_{uid}"

    with Given("two static-key processors are configured"):
        two_static_key_processors()

    with And(f"I create {username} with processor pin and claims"):
        create_sql_jwt_user(
            username=username, processor=_PROC_A, claims={"department": "qa"}
        )

    with Then("SHOW CREATE USER contains both clauses"):
        ddl = show_create_user(username)
        assert f"PROCESSOR \\'{_PROC_A}\\'" in ddl, error(
            f"Missing PROCESSOR in: {ddl}"
        )
        assert "CLAIMS" in ddl, error(f"Missing CLAIMS in: {ddl}")


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_SQLJWTUsers_ProcessorClause("1.0"),
    RQ_SRS_042_OAuth_SQLJWTUsers_AuthenticationFlow("1.0"),
)
def processor_pin_accepts_correct_token(self):
    """A token signed by the pinned processor SHALL authenticate the
    SQL-declared user.
    """
    uid = getuid()[:8]
    username = f"jwt_pin_ok_{uid}"

    with Given("two static-key processors are configured"):
        two_static_key_processors()

    with And(f"I create {username} pinned to {_PROC_A}"):
        create_sql_jwt_user(username=username, processor=_PROC_A)

    with When(f"I mint a token for {username} signed with {_PROC_A}'s secret"):
        token = create_static_jwt(
            user_name=username,
            secret=_SECRET_A,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then("ClickHouse accepts the token"):
        body = access_clickhouse(token=token, status_code=200)
        assert username in body, error()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_SQLJWTUsers_ProcessorClause("1.0"),
    RQ_SRS_042_OAuth_SQLJWTUsers_AuthenticationFlow("1.0"),
)
def processor_pin_rejects_wrong_processor_token(self):
    """A token signed by a different processor SHALL be rejected when
    the SQL user is pinned to a specific processor.
    """
    uid = getuid()[:8]
    username = f"jwt_pin_bad_{uid}"

    with Given("two static-key processors are configured"):
        two_static_key_processors()

    with And(f"I create {username} pinned to {_PROC_A}"):
        create_sql_jwt_user(username=username, processor=_PROC_A)

    with When(f"I mint a token for {username} signed with {_PROC_B}'s secret"):
        token = create_static_jwt(
            user_name=username,
            secret=_SECRET_B,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then("ClickHouse rejects the token"):
        assert_token_rejected(token=token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_SQLJWTUsers_AlterUser("1.0"),
    RQ_SRS_042_OAuth_SQLJWTUsers_ProcessorClause("1.0"),
    RQ_SRS_042_OAuth_SQLJWTUsers_AuthenticationFlow("1.0"),
)
def alter_repin_changes_accepted_processor(self):
    """``ALTER USER ... IDENTIFIED WITH jwt PROCESSOR`` SHALL change
    which processor validates the user's token.
    """
    uid = getuid()[:8]
    username = f"jwt_repin_{uid}"

    with Given("two static-key processors are configured"):
        two_static_key_processors()

    with And(f"I create {username} pinned to {_PROC_A}"):
        create_sql_jwt_user(username=username, processor=_PROC_A)

    with When("I mint tokens signed by each processor"):
        token_a = create_static_jwt(
            user_name=username,
            secret=_SECRET_A,
            algorithm="HS256",
            expiration_minutes=5,
        )
        token_b = create_static_jwt(
            user_name=username,
            secret=_SECRET_B,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then(f"{_PROC_A} token works and {_PROC_B} token is rejected"):
        body = access_clickhouse(token=token_a, status_code=200)
        assert username in body, error()
        assert_token_rejected(token=token_b)

    with When(f"I re-pin {username} to {_PROC_B} via ALTER"):
        alter_sql_jwt_user(username=username, processor=_PROC_B)

    with Then(f"{_PROC_B} token now works and {_PROC_A} token is rejected"):
        body = access_clickhouse(token=token_b, status_code=200)
        assert username in body, error()
        assert_token_rejected(token=token_a)

    with And("SHOW CREATE USER reflects the new processor"):
        ddl = show_create_user(username)
        assert f"PROCESSOR \\'{_PROC_B}\\'" in ddl, error(
            f"Expected PROCESSOR '{_PROC_B}' in: {ddl}"
        )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_SQLJWTUsers_ClaimsClause("1.0"),
    RQ_SRS_042_OAuth_SQLJWTUsers_AuthenticationFlow("1.0"),
)
def claims_enforced_via_sql(self):
    """A SQL user with ``CLAIMS`` SHALL reject tokens that do not
    carry the required claim values.
    """
    uid = getuid()[:8]
    username = f"jwt_claims_{uid}"

    with Given("two static-key processors are configured"):
        two_static_key_processors()

    with And(f"I create {username} with a department claim requirement"):
        create_sql_jwt_user(
            username=username,
            processor=_PROC_A,
            claims={"department": "engineering"},
        )

    with When("I mint a token WITH the required claim"):
        good_token = create_static_jwt(
            payload={"sub": username, "department": "engineering"},
            secret=_SECRET_A,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with And("I mint a token with a WRONG claim value"):
        wrong_token = create_static_jwt(
            payload={"sub": username, "department": "marketing"},
            secret=_SECRET_A,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with And("I mint a token WITHOUT the required claim"):
        missing_token = create_static_jwt(
            user_name=username,
            secret=_SECRET_A,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then("the token with matching claims is accepted"):
        body = access_clickhouse(token=good_token, status_code=200)
        assert username in body, error()

    with And("the token with wrong claim value is rejected"):
        assert_token_rejected(token=wrong_token)

    with And("the token without the required claim is rejected"):
        assert_token_rejected(token=missing_token)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_SQLJWTUsers_ClaimsClause("1.0"),
    RQ_SRS_042_OAuth_SQLJWTUsers_AuthenticationFlow("1.0"),
)
def claim_mismatch_rejected_consistently(self):
    """A token that fails a SQL user's ``CLAIMS`` check SHALL be rejected,
    and resubmitting the same token SHALL be rejected again — a rejected
    claim check SHALL NOT prime the cache with the claimed identity.
    """
    uid = getuid()[:8]
    username = f"jwt_claim_cache_{uid}"

    with Given("two static-key processors are configured"):
        two_static_key_processors()

    with And(f"I create {username} requiring department=engineering"):
        create_sql_jwt_user(
            username=username,
            processor=_PROC_A,
            claims={"department": "engineering"},
        )

    with When("I mint a token for the user WITHOUT the required claim"):
        token = create_static_jwt(
            user_name=username,
            secret=_SECRET_A,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then("the token is rejected"):
        assert_token_rejected(token=token)

    with And(
        "resubmitting the same token is rejected again "
        "(the rejection did not prime the cache)"
    ):
        assert_token_rejected(token=token)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_SQLJWTUsers_Validation_EmptyProcessor("1.0"))
def empty_processor_name_rejected(self):
    """``CREATE USER ... IDENTIFIED WITH jwt PROCESSOR ''`` SHALL be
    rejected with ``BAD_ARGUMENTS``.
    """
    uid = getuid()[:8]
    username = f"jwt_empty_proc_{uid}"
    node = self.context.node

    with When("I try to create a user with an empty processor name"):
        result = node.query(
            f"CREATE USER {username} IDENTIFIED WITH jwt PROCESSOR ''",
            no_checks=True,
        )

    with Then("the statement is rejected"):
        assert result.exitcode != 0 or "BAD_ARGUMENTS" in result.output, error(
            f"Expected BAD_ARGUMENTS, got exitcode={result.exitcode}, "
            f"output={result.output[:500]}"
        )

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(RQ_SRS_042_OAuth_SQLJWTUsers_Validation_InvalidClaims("1.0"))
def invalid_claims_json_rejected(self):
    """``CREATE USER ... IDENTIFIED WITH jwt CLAIMS '<non-json>'``
    SHALL be rejected with ``BAD_ARGUMENTS``.
    """
    uid = getuid()[:8]
    username = f"jwt_bad_claims_{uid}"
    node = self.context.node

    for bad_claims, label in [
        ("not-json", "plain string"),
        ("[]", "JSON array instead of object"),
    ]:
        with When(f"I try to create a user with {label} claims"):
            result = node.query(
                f"CREATE USER {username} IDENTIFIED WITH jwt CLAIMS '{bad_claims}'",
                no_checks=True,
            )

        with Then("the statement is rejected"):
            assert result.exitcode != 0 or "BAD_ARGUMENTS" in result.output, error(
                f"Expected BAD_ARGUMENTS for CLAIMS '{bad_claims}', "
                f"got exitcode={result.exitcode}, output={result.output[:500]}"
            )

    with And("the server is still alive"):
        check_clickhouse_is_alive()


@TestFeature
@Name("sql jwt users")
@Requirements(RQ_SRS_042_OAuth_SQLJWTUsers_CreateUser("1.0"))
def feature(self):
    """SQL-declared JWT user tests.

    Verifies that ``CREATE USER ... IDENTIFIED WITH jwt`` supports the
    ``PROCESSOR`` and ``CLAIMS`` clauses and that ClickHouse enforces them
    at authentication time.  Prior to the fix, the SQL grammar accepted only
    ``CLAIMS`` and had no syntax for pinning ``token_processor_name``,
    leaving every SQL-declared JWT user unpinned.
    """

    Scenario(run=create_bare_jwt_user)
    Scenario(run=create_jwt_user_with_processor_roundtrip)
    Scenario(run=create_jwt_user_with_claims_roundtrip)
    Scenario(run=create_jwt_user_with_processor_and_claims_roundtrip)
    Scenario(run=processor_pin_accepts_correct_token)
    Scenario(run=processor_pin_rejects_wrong_processor_token)
    Scenario(run=alter_repin_changes_accepted_processor)
    Scenario(run=claims_enforced_via_sql)
    Scenario(run=claim_mismatch_rejected_consistently)
    Scenario(run=empty_processor_name_rejected)
    Scenario(run=invalid_claims_json_rejected)
