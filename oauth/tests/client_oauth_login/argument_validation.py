"""Tests for ``--login`` argument-validation rules."""

from testflows.core import *
from testflows.asserts import error

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_Conflict_JWT,
    RQ_SRS_042_OAuth_Client_Login_Conflict_User,
    RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication,
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

    with Given("I reset the client state"):
        reset_client_state()

    with When("I run clickhouse-client with --login=banana"):
        exit_code, output = run_clickhouse_client(
            args=["--host", "clickhouse1", "--login=banana"],
            query="SELECT 1",
            timeout=10,
            expect_error=True,
        )

    with Then("the client exits with BAD_ARGUMENTS"):
        assert exit_code != 0, error()
        assert (
            "BAD_ARGUMENTS" in output or "must be 'browser' or 'device'" in output
        ), f"Expected BAD_ARGUMENTS for --login=banana, got:\n---\n{output}\n---"

    with And("the client did not crash"):
        assert_no_segfault(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Conflict_User("1.0"))
@Name("login conflicts with --user")
def login_conflicts_with_user(self):
    """Check that ``--login`` and ``--user`` cannot be specified together."""

    with Given("I reset the client state"):
        reset_client_state()

    with When("I run clickhouse-client with both --login and --user"):
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

    with Then("the client exits with BAD_ARGUMENTS"):
        assert exit_code != 0, error()
        assert (
            "BAD_ARGUMENTS" in output or "cannot both be specified" in output
        ), f"Expected BAD_ARGUMENTS for --user + --login, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Conflict_JWT("1.0"))
@Name("login conflicts with --jwt")
def login_conflicts_with_jwt(self):
    """Check that ``--login`` and ``--jwt`` cannot be specified together."""

    with Given("I reset the client state"):
        reset_client_state()

    with When("I run clickhouse-client with both --login and --jwt"):
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

    with Then("the client exits with BAD_ARGUMENTS"):
        assert exit_code != 0, error()
        assert (
            "BAD_ARGUMENTS" in output or "cannot be combined with a JWT" in output
        ), f"Expected BAD_ARGUMENTS for --jwt + --login, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_OAuthCredentials_RequiresLogin("1.0"))
@Name("--oauth-credentials without --login is rejected")
def oauth_credentials_requires_login(self):
    """Check that ``--oauth-credentials`` requires ``--login=browser|device``."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a valid OAuth credentials file"):
        write_oauth_credentials_file()

    with When("I run clickhouse-client with --oauth-credentials but no --login"):
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

    with Then("the client exits with BAD_ARGUMENTS"):
        assert exit_code != 0, error()
        assert "BAD_ARGUMENTS" in output or "requires --login" in output, (
            "Expected BAD_ARGUMENTS for bare --oauth-credentials, got:\n"
            f"---\n{output}\n---"
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Mode("1.0"))
@Name("bare --login= behaves like cloud auto-login probe")
def bare_login_equals_empty_targets_cloud_logic(self):
    """``--login=`` follows the same hostname rules as bare ``--login``."""

    with Given("I reset the client state"):
        reset_client_state()

    with When("I run clickhouse-client with --login="):
        exit_code, output = run_clickhouse_client(
            args=["--host", "clickhouse1", "--login="],
            query="SELECT 1",
            timeout=8,
            expect_error=True,
        )

    with Then("non-cloud hosts still require explicit OAuth configuration"):
        assert_no_segfault(output=output, exit_code=exit_code)
        assert exit_code != 0, error()
        ol = output.strip()
        assert (
            "oauth" in ol or "Bad arguments" in ol or "authentication_failed" in ol
        ), f"Expected OAuth requirement on non-cloud host:\n{output}"


@TestScenario
@Name("login conflicts with --password")
def login_conflicts_with_password(self):
    """``--login`` cannot be combined with ``--password``."""

    with Given("I reset the client state"):
        reset_client_state()

    with When("I pass both flags"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--password",
                "s3cr3t",
            ],
            query="SELECT 1",
            timeout=10,
            expect_error=True,
        )

    with Then("the client rejects the combination"):
        assert exit_code != 0, error()
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            "bad_arguments" in ol or "cannot" in ol or "conflict" in ol
        ), f"Expected BAD_ARGUMENTS/conflict, got:\n{output}"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Mode("1.0"))
@Name("capitalised login modes are rejected")
def login_mode_capitalisation_rejected(self):
    """Modes other than exact ``browser`` / ``device`` SHALL fail before OAuth."""

    for variant in ("BROWSER", "Browser", "DEVICE", "Device"):
        with Given(f"I reset state for {variant!r}"):
            reset_client_state()

        with When(f"I run clickhouse-client with --login={variant}"):
            exit_code, output = run_clickhouse_client(
                args=[
                    "--host",
                    "clickhouse1",
                    f"--login={variant}",
                ],
                query="SELECT 1",
                timeout=10,
                expect_error=True,
            )

        with Then(f"{variant} is rejected with a browser-or-device hint"):
            assert exit_code != 0, error()
            assert_no_segfault(output=output, exit_code=exit_code)
            assert (
                "BAD_ARGUMENTS" in output
                or "must be 'browser' or 'device'" in output
                or 'must be "browser" or "device"' in output
            ), f"Expected mode rejection for {variant}, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device login without --query still enters OAuth")
def device_login_interactive_without_query(self):
    """Interactive sessions must still start OAuth instead of crashing."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write OAuth credentials"):
        write_oauth_credentials_file()

    with When("I invoke clickhouse-client without --query"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query=None,
            timeout=10,
            expect_error=True,
        )

    with Then("timeout kills the waiter without segfault"):
        assert_no_segfault(output=output, exit_code=exit_code)


@TestFeature
@Name("argument validation")
def feature(self):
    """Tests for ``--login`` argument-validation rules."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
