"""Tests for ``--login`` argument-validation rules."""

from testflows.core import *
from testflows.asserts import error

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_Conflict_JWT,
    RQ_SRS_042_OAuth_Client_Login_Conflict_User,
    RQ_SRS_042_OAuth_Client_Login_Mode,
    RQ_SRS_042_OAuth_Client_Login_OAuthCredentials_RequiresLogin,
)
from oauth.tests.steps.client_login import (
    DEFAULT_CREDS_PATH,
    assert_no_segfault,
    reset_client_state,
    run_clickhouse_client,
    write_oauth_credentials_file,
)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Mode("1.0"))
@Name("login mode validation rejects unknown values")
def login_mode_validation(self):
    """Check that an unknown ``--login=<mode>`` value is rejected with BAD_ARGUMENTS."""

    reset_client_state()

    exit_code, output = run_clickhouse_client(
        args=["--host", "clickhouse1", "--login=banana"],
        query="SELECT 1",
        timeout=10,
        expect_error=True,
    )

    assert exit_code != 0, error()
    assert (
        "BAD_ARGUMENTS" in output
        or "must be 'browser' or 'device'" in output
    ), f"Expected BAD_ARGUMENTS for --login=banana, got:\n---\n{output}\n---"
    assert_no_segfault(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Conflict_User("1.0"))
@Name("login conflicts with --user")
def login_conflicts_with_user(self):
    """Check that ``--login`` and ``--user`` cannot be specified together."""

    reset_client_state()

    exit_code, output = run_clickhouse_client(
        args=[
            "--host",
            "clickhouse1",
            "--login=device",
            "--user",
            "default",
        ],
        query="SELECT 1",
        timeout=10,
        expect_error=True,
    )

    assert exit_code != 0, error()
    assert "BAD_ARGUMENTS" in output or "cannot both be specified" in output, (
        f"Expected BAD_ARGUMENTS for --user + --login, got:\n---\n{output}\n---"
    )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Conflict_JWT("1.0"))
@Name("login conflicts with --jwt")
def login_conflicts_with_jwt(self):
    """Check that ``--login`` and ``--jwt`` cannot be specified together."""

    reset_client_state()

    exit_code, output = run_clickhouse_client(
        args=[
            "--host",
            "clickhouse1",
            "--login=device",
            "--jwt",
            "dummy.jwt.token",
        ],
        query="SELECT 1",
        timeout=10,
        expect_error=True,
    )

    assert exit_code != 0, error()
    assert "BAD_ARGUMENTS" in output or "cannot be combined with a JWT" in output, (
        f"Expected BAD_ARGUMENTS for --jwt + --login, got:\n---\n{output}\n---"
    )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_OAuthCredentials_RequiresLogin("1.0"))
@Name("--oauth-credentials without --login is rejected")
def oauth_credentials_requires_login(self):
    """Check that ``--oauth-credentials`` requires ``--login=browser|device``."""

    reset_client_state()
    write_oauth_credentials_file()

    exit_code, output = run_clickhouse_client(
        args=[
            "--host",
            "clickhouse1",
            "--oauth-credentials",
            DEFAULT_CREDS_PATH,
        ],
        query="SELECT 1",
        timeout=10,
        expect_error=True,
    )

    assert exit_code != 0, error()
    assert "BAD_ARGUMENTS" in output or "requires --login" in output, (
        "Expected BAD_ARGUMENTS for bare --oauth-credentials, got:\n"
        f"---\n{output}\n---"
    )


@TestFeature
@Name("argument validation")
def feature(self):
    """Tests for ``--login`` argument-validation rules."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
