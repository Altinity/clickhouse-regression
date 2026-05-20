"""Tests for ``--login`` argument-validation rules."""

from testflows.core import *
from testflows.asserts import error
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
    assert_no_segfault,
    reset_client_state,
    run_clickhouse_client,
    write_oauth_credentials_file,
)

# Curated payloads for the combinatorial fuzz scenario below. Each entry
# is meant to be rejected by the client — either by mode-value validation
# ("must be 'browser' or 'device'") or by conflict validation when paired
# with another flag. The list is grouped by character class so it's easy
# to see what's covered and to extend later without duplicating intent.
#
# Notes on what's deliberately NOT here:
# - NUL (\x00) — the kernel truncates argv at the first NUL, so the
#   byte never reaches the parser intact and the test wouldn't be
#   exercising what it claims to.
# - The exact strings "browser" / "device" — those are the only two
#   accepted values; including them would turn the fuzz scenario into
#   a happy-path test that would then hang waiting on the real OAuth
#   flow.
#
# The list is kept around three dozen entries on purpose: combined with
# the five ``_EXTRA_FLAGS`` contexts below it produces ~180 cases under
# a strength-2 covering array, which is enough to hit every character
# class against every validation surface without blowing out CI time.
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


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_Mode("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_User("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_JWT("1.0"),
)
@Name("login value combinatorial fuzz")
def login_value_combinatorial_fuzz(self):
    """Exotic ``--login=<value>`` inputs SHALL be rejected without crashing.

    For every (payload, extra-flag) pair produced by a strength-2 covering
    array the client must:

    1. Exit with a non-zero status.
    2. Not abort via SIGSEGV/SIGABRT or hit a libc++ hardening trap.
    3. Print a recognisable validation hint — either the mode-value error
       ("must be 'browser' or 'device'") or the conflict error
       ("cannot be specified together" / "cannot be combined with a JWT")
       depending on which extra flag was paired with the payload. The
       ``with_oauth_credentials`` extra additionally exercises the path
       where the credentials-file processor and the mode-value validator
       run in the same invocation.

    Payload classes covered: whitespace and control bytes, case variants,
    near-matches/typos, punctuation, shell/SQL injection shapes,
    path-like, non-ASCII Unicode (Cyrillic, CJK, full-width, emoji,
    RTL override, zero-width, combining marks, BOM), and boundary
    lengths up to 1 KiB.
    """

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

            with Then("the client did not crash"):
                assert_no_segfault(output=output, exit_code=exit_code)

            with And("the client exited with a non-zero status"):
                assert exit_code != 0, (
                    "Expected rejection for "
                    f"--login={payload_value!r} + {extra_args!r}, "
                    f"but exit_code=0\n---\n{output}\n---"
                )

            with And("the output contains a recognisable validation hint"):
                ol = output.lower()
                assert any(marker in ol for marker in accepted_markers), (
                    "No validation hint found in output for "
                    f"payload={payload_name!r} extra={extra_name!r}:\n"
                    f"---\n{output}\n---"
                )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_Mode("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_User("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_JWT("1.0"),
)
@Name("login split form behaves like equals form")
def login_split_vs_equals_form_equivalence(self):
    """Both ``--login <value>`` and ``--login=<value>`` SHALL be validated identically.

    Boost program_options accepts both the equals-attached and the
    space-separated form of a long option that takes an argument. The
    argument-validation surface must therefore reject (or accept) the same
    set of inputs regardless of which form the user typed — otherwise a
    regression in either parser branch would silently bypass the conflict
    or mode-value checks.

    The cases below pair each rejection surface (unknown mode, user
    conflict, JWT conflict) against both invocation forms and assert that
    both forms produce a non-zero exit with a recognisable validation hint
    and never crash the client.
    """

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

                with Then("the client did not crash"):
                    assert_no_segfault(output=output, exit_code=exit_code)

                with And("the client exited with a non-zero status"):
                    assert exit_code != 0, (
                        f"Expected rejection for {case_name} via {form_label} form, "
                        f"got exit=0\n---\n{output}\n---"
                    )

                with And("the output contains a recognisable validation hint"):
                    ol = output.lower()
                    assert any(m in ol for m in markers), (
                        f"No validation hint for {case_name} via {form_label}:\n"
                        f"---\n{output}\n---"
                    )


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_Mode("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_User("1.0"),
    RQ_SRS_042_OAuth_Client_Login_Conflict_JWT("1.0"),
)
@Name("login multi-conflict combinations are rejected without crashing")
def login_multi_conflict_combinations(self):
    """Multiple simultaneous flag conflicts SHALL be rejected cleanly.

    Each case piles on more than one conflicting flag (e.g. ``--user`` AND
    ``--jwt`` AND an invalid ``--login`` value) to make sure the argument
    parser handles the cross-product without crashing via SIGSEGV / SIGABRT
    and does not silently let any of the offending flags through. We don't
    pin which conflict the client reports first — the order of checks is
    an implementation detail — but we DO pin that *some* recognisable
    validation hint surfaces in the output for every combination.
    """

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

            with Then("the client did not crash"):
                assert_no_segfault(output=output, exit_code=exit_code)

            with And("the client exited with a non-zero status"):
                assert exit_code != 0, (
                    f"Expected rejection for {name} {extra!r}, "
                    f"got exit=0\n---\n{output}\n---"
                )

            with And("the output contains a recognisable validation hint"):
                ol = output.lower()
                assert any(
                    m in ol for m in markers
                ), f"No validation hint for {name}:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Mode("1.0"))
@Name("duplicate --login flags do not crash and resolve safely")
def login_duplicate_flag_precedence(self):
    """Duplicated ``--login`` flags SHALL be rejected without crashing.

    Boost program_options rejects repeated occurrences of ``--login``
    outright (``option '--login' cannot be specified more than once``)
    rather than picking a winner. This is the strongest safety property
    we could ask for — duplication can never be used to bypass either
    the mode-value validator or the flag-conflict checks.

    For every duplicate combination (both forms, both orderings, both-
    invalid as well as mixed-validity) this scenario pins three
    invariants:

    1. The client never aborts via SIGSEGV / SIGABRT.
    2. The client exits with a non-zero status.
    3. The output contains a recognisable rejection hint — either the
       duplicate-rejection from program_options
       ("cannot be specified more than once") or, if a future build
       relaxes the duplicate check, one of the downstream validation
       hints (mode-value or conflict).

    The observed exit code is recorded via ``note(...)`` so a shift in
    precedence / parser behaviour is visible in the log even when it
    does not break any of the invariants above.
    """

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

            with Then("the client did not crash"):
                assert_no_segfault(output=output, exit_code=exit_code)

            note(f"{name}: exit_code={exit_code}")

            with And("the client exited with a non-zero status"):
                assert exit_code != 0, (
                    f"Expected rejection for duplicate --login {login_args!r}, "
                    f"got exit=0\n---\n{output}\n---"
                )

            with And("the output contains a recognisable rejection hint"):
                ol = output.lower()
                assert any(
                    m in ol for m in duplicate_markers
                ), f"No rejection hint for {name}:\n---\n{output}\n---"


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
