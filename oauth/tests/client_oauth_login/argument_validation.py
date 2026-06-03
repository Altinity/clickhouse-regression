from testflows.core import *
from testflows.combinatorics import CoveringArray

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_Conflict_JWT,
    RQ_SRS_042_OAuth_Client_Login_Conflict_User,
    RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication,
    RQ_SRS_042_OAuth_Client_Login_Mode,
    RQ_SRS_042_OAuth_Client_Login_OAuthCredentials_RequiresLogin,
)
from oauth.tests.steps.client_login import (
    DEFAULT_CREDS_PATH,
    assert_client_rejected,
    assert_no_segfault,
    reset_client_state,
    run_clickhouse_client,
    write_oauth_credentials_file,
)


_LOGIN_VALUE_PAYLOADS = {
    # --- whitespace and empty-ish ----------------------------------------
    "single_space": " ",
    "tab": "\t",
    "newline": "\n",
    "leading_space_browser": " browser",
    "trailing_newline_device": "device\n",
    # --- case and near-match variants beyond BROWSER / DEVICE ------------
    "mixed_case_browser": "BrOwSeR",
    "upper_padded_device": " DEVICE ",
    "browsers": "browsers",
    "both_csv": "browser,device",
    # --- punctuation and symbols -----------------------------------------
    "dash_prefix": "-browser",
    "equals_inside": "browser=device",
    "single_quoted": "'browser'",
    "brackets": "[device]",
    # --- numeric / boolean-looking ---------------------------------------
    "zero": "0",
    "true": "true",
    "null_word": "null",
    # --- shell / SQL injection shapes (must stay inert) ------------------
    "sql_comment": "browser'; --",
    "shell_subst": "$(whoami)",
    "semicolon_chain": "browser; echo PWNED",
    "pipe_chain": "browser | cat",
    # --- path-like -------------------------------------------------------
    "dotdot": "../browser",
    "absolute": "/etc/passwd",
    # --- non-NUL control bytes -------------------------------------------
    "ansi_color": "\x1b[31mdevice\x1b[0m",
    "del_byte": "browser\x7f",
    "soh_byte": "\x01browser",
    # --- unicode ---------------------------------------------------------
    "cyrillic": "браузер",
    "japanese": "ブラウザ",
    "fullwidth_browser": "ＢＲＯＷＳＥＲ",
    "emoji": "browser🚀",
    "rtl_override": "\u202ebrowser",
    "zero_width_space": "bro\u200bwser",
    "combining_accent": "bro\u0301wser",
    "byte_order_mark": "\ufeffbrowser",
    # --- boundary lengths ------------------------------------------------
    "long_garbage_1k": "x" * 1024,
    "long_browser_suffix": "browser" + "x" * 256,
}


# Secondary flag mixed in alongside ``--login=<payload>``. Each entry
# exercises a different validation surface: the bare case hits the
# mode-value check; the user/jwt/password cases additionally hit the
# flag-conflict check; the oauth-credentials case verifies that mode-value
# validation still fires when credentials-file processing is also in play.
# The combinatorial scenario verifies that none of these interactions
# crashes the client.
_EXTRA_FLAGS = {
    "none": [],
    "with_user": ["--user", "default"],
    "with_jwt": ["--jwt", "dummy.jwt.token"],
    "with_password": ["--password", "s3cr3t"],
    "with_oauth_credentials": ["--oauth-credentials", DEFAULT_CREDS_PATH],
}


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Mode("1.0"))
@Name("login mode validation rejects unknown values")
def login_mode_validation(self):
    """clickhouse-client SHALL reject unknown ``--login`` values with BAD_ARGUMENTS."""

    with Given("I reset the client state"):
        reset_client_state()

    with When("I run clickhouse-client with --login=banana"):
        exit_code, output = run_clickhouse_client(
            args=["--host", "clickhouse1", "--login=banana"],
            query="SELECT 1",
            timeout=10,
            expect_error=True,
        )

    with Then("the client rejects --login=banana without crashing"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("BAD_ARGUMENTS", "must be 'browser' or 'device'"),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Conflict_User("1.0"))
@Name("login conflicts with --user")
def login_conflicts_with_user(self):
    """clickhouse-client SHALL reject ``--login`` together with ``--user``."""

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

    with Then("the client rejects --login + --user without crashing"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("BAD_ARGUMENTS", "cannot both be specified"),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Conflict_JWT("1.0"))
@Name("login conflicts with --jwt")
def login_conflicts_with_jwt(self):
    """clickhouse-client SHALL reject ``--login`` together with ``--jwt``."""

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

    with Then("the client rejects --login + --jwt without crashing"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("BAD_ARGUMENTS", "cannot be combined with a JWT"),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_OAuthCredentials_RequiresLogin("1.0"))
@Name("--oauth-credentials without --login is rejected")
def oauth_credentials_requires_login(self):
    """``--oauth-credentials`` SHALL require ``--login=browser`` or ``--login=device``."""

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

    with Then("the client rejects bare --oauth-credentials without crashing"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("BAD_ARGUMENTS", "requires --login"),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Mode("1.0"))
@Name("bare --login= behaves like cloud auto-login probe")
def bare_login_equals_empty_targets_cloud_logic(self):
    """``--login=`` on a non-cloud host SHALL require explicit OAuth configuration."""

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
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("oauth", "Bad arguments", "authentication_failed"),
        )


@TestScenario
@Name("login conflicts with --password")
def login_conflicts_with_password(self):
    """clickhouse-client SHALL reject ``--login`` together with ``--password``."""

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
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("bad_arguments", "cannot", "conflict"),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Mode("1.0"))
@Name("capitalised login modes are rejected")
def login_mode_capitalisation_rejected(self):
    """Capitalised login modes SHALL be rejected before OAuth starts."""

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
            assert_client_rejected(
                output=output,
                exit_code=exit_code,
                markers=(
                    "BAD_ARGUMENTS",
                    "must be 'browser' or 'device'",
                    'must be "browser" or "device"',
                ),
            )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_DeviceFlow_Authentication("1.0"))
@Name("device login without --query still enters OAuth")
def device_login_interactive_without_query(self):
    """Device login without ``--query`` SHALL start OAuth without crashing."""

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


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_Mode("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_User("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_JWT("1.0"),
)
@Name("login value combinatorial fuzz")
def login_value_combinatorial_fuzz(self):
    """Invalid ``--login`` values with mixed flags SHALL exit with a validation hint, not a crash."""

    combinations_dict = {
        "payload": list(_LOGIN_VALUE_PAYLOADS.keys()),
        "extra": list(_EXTRA_FLAGS.keys()),
    }

    accepted_markers = (
        "bad_arguments",
        "must be 'browser' or 'device'",
        'must be "browser" or "device"',
        "cannot be specified together",
        "cannot be combined with a jwt",
        "cannot",
        "conflict",
        "requires --login",
        "authentication_failed",
        "unknown option",
    )

    for combo in CoveringArray(combinations_dict, strength=2):
        payload_name = combo["payload"]
        extra_name = combo["extra"]
        payload_value = _LOGIN_VALUE_PAYLOADS[payload_name]
        extra_args = _EXTRA_FLAGS[extra_name]

        with Check(f"payload={payload_name} extra={extra_name}"):
            with Given("I reset the client state"):
                reset_client_state()

            # ``reset_client_state`` wipes ~/.clickhouse-client so the
            # credentials file must be (re-)materialised inside every
            # iteration that needs it.
            if extra_name == "with_oauth_credentials":
                with And("I write a valid OAuth credentials file"):
                    write_oauth_credentials_file()

            with When(
                f"I run clickhouse-client with --login={payload_value!r} "
                f"and extra args {extra_args!r}"
            ):
                exit_code, output = run_clickhouse_client(
                    args=[
                        "--host",
                        "clickhouse1",
                        f"--login={payload_value}",
                        *extra_args,
                    ],
                    query="SELECT 1",
                    timeout=8,
                    expect_error=True,
                )

            with Then("the client is rejected with a validation hint and no crash"):
                assert_client_rejected(
                    output=output,
                    exit_code=exit_code,
                    markers=accepted_markers,
                )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_Mode("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_User("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_JWT("1.0"),
)
@Name("login split form behaves like equals form")
def login_split_vs_equals_form_equivalence(self):
    """``--login <v>`` and ``--login=<v>`` SHALL get identical validation."""

    cases = [
        (
            "unknown_mode",
            "banana",
            [],
            (
                "bad_arguments",
                "must be 'browser' or 'device'",
                'must be "browser" or "device"',
            ),
        ),
        (
            "conflict_user",
            "device",
            ["--user", "default"],
            ("bad_arguments", "cannot", "conflict"),
        ),
        (
            "conflict_jwt",
            "device",
            ["--jwt", "dummy.jwt.token"],
            (
                "bad_arguments",
                "cannot be combined with a jwt",
                "cannot",
                "conflict",
            ),
        ),
    ]

    for case_name, value, extra_args, markers in cases:
        for form_label, login_argv in (
            ("equals", [f"--login={value}"]),
            ("split", ["--login", value]),
        ):
            with Check(f"{case_name} / {form_label}"):
                with Given("I reset the client state"):
                    reset_client_state()

                with When(
                    f"I run clickhouse-client with --login form={form_label} "
                    f"value={value!r} extras={extra_args!r}"
                ):
                    exit_code, output = run_clickhouse_client(
                        args=[
                            "--host",
                            "clickhouse1",
                            *login_argv,
                            *extra_args,
                        ],
                        query="SELECT 1",
                        timeout=10,
                        expect_error=True,
                    )

                with Then("the client is rejected with a validation hint and no crash"):
                    assert_client_rejected(
                        output=output, exit_code=exit_code, markers=markers
                    )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_Mode("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_User("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_JWT("1.0"),
)
@Name("login multi-conflict combinations are rejected without crashing")
def login_multi_conflict_combinations(self):
    """Multiple conflicting flags SHALL exit with a validation hint, not a crash."""

    cases = [
        (
            "user_plus_jwt_plus_bad_mode",
            [
                "--login=banana",
                "--user",
                "default",
                "--jwt",
                "dummy.jwt.token",
            ],
        ),
        (
            "user_plus_jwt_plus_device",
            [
                "--login=device",
                "--user",
                "default",
                "--jwt",
                "dummy.jwt.token",
            ],
        ),
        (
            "user_plus_password_plus_device",
            [
                "--login=device",
                "--user",
                "default",
                "--password",
                "s3cr3t",
            ],
        ),
        (
            "jwt_plus_password_plus_bad_mode",
            [
                "--login=banana",
                "--jwt",
                "dummy.jwt.token",
                "--password",
                "s3cr3t",
            ],
        ),
        (
            "user_plus_jwt_plus_password_plus_bad_mode",
            [
                "--login=banana",
                "--user",
                "default",
                "--jwt",
                "dummy.jwt.token",
                "--password",
                "s3cr3t",
            ],
        ),
        (
            "user_plus_oauth_credentials_plus_bad_mode",
            [
                "--login=banana",
                "--user",
                "default",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
        ),
    ]

    markers = (
        "bad_arguments",
        "must be 'browser' or 'device'",
        'must be "browser" or "device"',
        "cannot be specified together",
        "cannot be combined with a jwt",
        "cannot",
        "conflict",
        "requires --login",
    )

    for name, extra in cases:
        with Check(name):
            with Given("I reset the client state"):
                reset_client_state()

            # Materialise the credentials file when the case references it,
            # so we exercise the credentials-processing branch rather than
            # the "file not found" branch.
            if "--oauth-credentials" in extra:
                with And("I write a valid OAuth credentials file"):
                    write_oauth_credentials_file()

            with When(f"I run clickhouse-client with {extra!r}"):
                exit_code, output = run_clickhouse_client(
                    args=["--host", "clickhouse1", *extra],
                    query="SELECT 1",
                    timeout=10,
                    expect_error=True,
                )

            with Then("the client is rejected with a validation hint and no crash"):
                assert_client_rejected(
                    output=output, exit_code=exit_code, markers=markers
                )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Mode("1.0"))
@Name("duplicate --login flags do not crash and resolve safely")
def login_duplicate_flag_precedence(self):
    """Duplicate ``--login`` flags SHALL be rejected without crashing."""

    pairs = [
        # (name, login args)
        ("bad_then_device", ["--login=banana", "--login=device"]),
        ("device_then_bad", ["--login=device", "--login=banana"]),
        ("bad_then_bad_different", ["--login=banana", "--login=apple"]),
        ("bad_then_bad_same", ["--login=banana", "--login=banana"]),
        ("equals_and_split_mixed", ["--login=device", "--login", "banana"]),
        ("split_and_equals_mixed", ["--login", "banana", "--login=device"]),
    ]

    duplicate_markers = (
        "cannot be specified more than once",
        "bad_arguments",
        "bad arguments",
        "must be 'browser' or 'device'",
        'must be "browser" or "device"',
        "cannot",
        "conflict",
    )

    for name, login_args in pairs:
        with Check(name):
            with Given("I reset the client state"):
                reset_client_state()

            with When(f"I run clickhouse-client with {login_args!r}"):
                exit_code, output = run_clickhouse_client(
                    args=["--host", "clickhouse1", *login_args],
                    query="SELECT 1",
                    timeout=8,
                    expect_error=True,
                )

            note(f"{name}: exit_code={exit_code}")

            with Then("the client is rejected without crashing"):
                assert_client_rejected(
                    output=output, exit_code=exit_code, markers=duplicate_markers
                )


@TestFeature
@Name("argument validation")
def feature(self):
    """Tests for ``--login`` argument-validation rules."""

    Scenario(run=login_mode_validation)
    Scenario(run=login_conflicts_with_user)
    Scenario(run=login_conflicts_with_jwt)
    Scenario(run=oauth_credentials_requires_login)
    Scenario(run=bare_login_equals_empty_targets_cloud_logic)
    Scenario(run=login_conflicts_with_password)
    Scenario(run=login_mode_capitalisation_rejected)
    Scenario(run=device_login_interactive_without_query)
    Scenario(run=login_value_combinatorial_fuzz)
    Scenario(run=login_split_vs_equals_form_equivalence)
    Scenario(run=login_multi_conflict_combinations)
    Scenario(run=login_duplicate_flag_precedence)
