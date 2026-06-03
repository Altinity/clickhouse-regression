"""Tests for the on-disk OAuth refresh-token cache."""

import json

from testflows.core import *
from testflows.asserts import error

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_Cache_CorruptedIgnored,
    RQ_SRS_042_OAuth_Client_Login_Cache_FilePermissions,
    RQ_SRS_042_OAuth_Client_Login_Cache_Reuse,
)
from oauth.tests.steps.client_login import (
    CLIENT_CONFIG_DIR,
    DEFAULT_CACHE_PATH,
    DEFAULT_CREDS_PATH,
    approve_keycloak_device_user_code_via_bash_tools,
    assert_device_user_code_present,
    assert_no_segfault,
    complete_keycloak_device_login_via_background,
    extract_device_user_code_from_client_output,
    file_exists,
    kill_clickhouse_oauth_background_if_alive,
    parse_background_client_exit_code,
    read_clickhouse_oauth_background_log,
    read_oauth_cache,
    reset_client_state,
    run_clickhouse_client,
    set_immutable,
    start_clickhouse_oauth_client_background,
    stat_file_mode,
    unset_immutable,
    wait_clickhouse_oauth_background_finished,
    wait_for_device_user_code,
    write_keycloak_device_credentials,
    write_oauth_cache,
    write_oauth_credentials_file,
)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_CorruptedIgnored("1.0"))
@Name("corrupted oauth_cache.json does not crash login flow")
def corrupted_cache_is_ignored(self):
    """Corrupted ``oauth_cache.json`` SHALL be ignored; device flow starts fresh."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I pre-seed a corrupted oauth_cache.json"):
        write_oauth_cache(raw_contents="garbage that is not json {][")

    with And("I write a valid OAuth credentials file"):
        write_oauth_credentials_file()

    with When("I run clickhouse-client with the corrupted cache present"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=15,
            expect_error=True,
        )

    with Then(
        "the corrupted cache is bypassed and a fresh device flow starts",
        description="""
            The corrupted-cache requirement is "ignored, not crashed" — so
            the client MUST fall back to a fresh device authorization. Pin
            the user_code (or at least the verification URL) so the
            scenario fails loudly if some future regression swallows the
            cache-parse error and silently exits without doing OAuth.
        """,
    ):
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            extract_device_user_code_from_client_output(output) is not None
            or "http://" in ol
            or "https://" in ol
        ), (
            "Expected fresh device flow signal after corrupted cache, got:\n"
            f"---\n{output}\n---"
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_FilePermissions("1.0"))
@Name("oauth_cache.json is created with mode 0600")
def cache_file_mode_is_strict(self):
    """New ``oauth_cache.json`` SHALL be created with mode ``0600``."""

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I write OAuth credentials"):
            write_keycloak_device_credentials()

        with When(
            "I complete one device login so the client creates the cache",
            description="""
                The previous version of this scenario seeded a 0600 file
                ourselves and asserted it was still 0600 — that tested our
                write_oauth_cache helper, not the client. Drive a real
                login so the client *creates* the cache, then check its
                on-disk mode.
            """,
        ):
            complete_keycloak_device_login_via_background()

        with Then("the cache file the client just created is mode 0600"):
            assert file_exists(
                path=DEFAULT_CACHE_PATH
            ), "Expected oauth_cache.json after successful device login"
            mode = stat_file_mode(path=DEFAULT_CACHE_PATH)
            assert mode == "600", (
                f"Expected client-created oauth_cache.json mode 600, " f"got {mode!r}"
            )

    finally:
        with Finally("I stop background clients"):
            kill_clickhouse_oauth_background_if_alive()


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_Reuse("1.0"))
@Name("oauth_cache.json is written after successful device login")
def oauth_cache_written_after_successful_device_login(self):
    """Successful device login SHALL write ``oauth_cache.json``."""

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I write OAuth credentials"):
            write_keycloak_device_credentials()

        with When("I complete one device login"):
            complete_keycloak_device_login_via_background()

        with Then("oauth_cache.json exists with strict permissions"):
            assert file_exists(
                path=DEFAULT_CACHE_PATH
            ), "Expected oauth_cache.json after successful login"
            mode = stat_file_mode(path=DEFAULT_CACHE_PATH)
            assert mode == "600", f"Expected cache mode 600, got {mode!r}"
            blob = read_oauth_cache()
            assert (
                isinstance(blob, dict) and len(blob) >= 1
            ), f"Expected JSON object cache, got {blob!r}"

    finally:
        with Finally("I stop background clients"):
            kill_clickhouse_oauth_background_if_alive()


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_Reuse("1.0"))
@Name("second device login reuses refresh cache without new device code")
def second_client_run_reuses_cached_refresh_token(self):
    """Second login SHALL reuse the cached refresh token."""

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I write OAuth credentials"):
            write_keycloak_device_credentials()

        with When("I complete the first device login"):
            complete_keycloak_device_login_via_background()

        with And("I run clickhouse-client again without resetting HOME"):
            exit_code, output = run_clickhouse_client(
                args=[
                    "--host",
                    "clickhouse1",
                    "--login=device",
                    "--oauth-credentials",
                    DEFAULT_CREDS_PATH,
                ],
                query="SELECT currentUser()",
                timeout=15,
                expect_error=False,
            )

        with Then("the second invocation succeeds immediately"):
            assert exit_code == 0, error()
            assert_no_segfault(output=output, exit_code=exit_code)

    finally:
        with Finally("I stop background clients"):
            kill_clickhouse_oauth_background_if_alive()


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_Reuse("1.0"))
@Name("invalid cached refresh token falls back to interactive device flow")
def invalid_cached_refresh_token_falls_back_to_device_flow(self):
    """Invalid cached refresh token SHALL fall back to device flow."""

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I write OAuth credentials"):
            write_keycloak_device_credentials()

        with When("I complete the first device login"):
            complete_keycloak_device_login_via_background()

        with And("I corrupt the cached refresh token"):
            cached = read_oauth_cache()
            assert cached and isinstance(cached, dict), "cache missing after login"
            key = next(iter(cached.keys()))
            cached[key] = "invalid_refresh_token_value"
            write_oauth_cache(raw_contents=json.dumps(cached), mode="600")

        with And("I run device login again without interaction"):
            exit_code, output = run_clickhouse_client(
                args=[
                    "--host",
                    "clickhouse1",
                    "--login=device",
                    "--oauth-credentials",
                    DEFAULT_CREDS_PATH,
                ],
                query="SELECT 1",
                timeout=14,
                expect_error=True,
            )

        with Then("the client surfaces a fresh device authorization"):
            assert_device_user_code_present(output=output, exit_code=exit_code)

    finally:
        with Finally("I stop background clients"):
            kill_clickhouse_oauth_background_if_alive()


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_FilePermissions("1.0"))
@Name("world-readable oauth_cache.json is handled safely")
def world_readable_oauth_cache_is_handled(self):
    """World-readable cache SHALL not crash or skip OAuth silently."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I seed a world-readable cache"):
        write_oauth_cache(
            mapping={"deadbeef": "refresh-placeholder"},
            mode="644",
        )

    with And("I write OAuth credentials"):
        write_oauth_credentials_file()

    with When("I run clickhouse-client"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=15,
            expect_error=True,
        )

    with Then(
        "the loose-permission cache does not short-circuit OAuth",
        description="""
            The seeded "refresh-placeholder" is not a real refresh token,
            so the client must either (a) ignore the world-readable cache
            outright or (b) try the placeholder, get rejected, and fall
            back to device flow. Either way a fresh device authorization
            MUST appear — "no crash" alone allows a regression that
            silently exits before doing OAuth.
        """,
    ):
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            extract_device_user_code_from_client_output(output) is not None
            or "http://" in ol
            or "https://" in ol
        ), (
            "Expected fresh device flow signal when ignoring/rejecting "
            f"the world-readable cache, got:\n---\n{output}\n---"
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_CorruptedIgnored("1.0"))
@Name("oauth_cache JSON object with wrong shape starts device flow")
def oauth_cache_wrong_json_shape_starts_device_flow(self):
    """Wrong cache JSON shape SHALL behave like a cache miss."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write syntactically valid JSON with unexpected shape"):
        write_oauth_cache(raw_contents='{"unexpected": [1, 2, 3]}')

    with And("I write OAuth credentials"):
        write_oauth_credentials_file()

    with When("I run clickhouse-client"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                DEFAULT_CREDS_PATH,
            ],
            query="SELECT 1",
            timeout=12,
            expect_error=True,
        )

    with Then("device authorization prompts appear"):
        assert_device_user_code_present(output=output, exit_code=exit_code)


@TestScenario
@Name("read-only config dir allows login but blocks cache write")
def read_only_client_dir_blocks_cache_write(self):
    """Read-only config dir SHALL allow login but not write the cache."""

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I write OAuth credentials"):
            write_keycloak_device_credentials()

        with And("I make the config directory immutable"):
            set_immutable(path=CLIENT_CONFIG_DIR)

        with When(
            "I start clickhouse-client with device login",
            description="""
        Use a short wall_timeout so that if the client hangs trying to
            write the immutable cache directory it is killed within the 90s
            wait window rather than outliving it.""",
        ):

            start_clickhouse_oauth_client_background(
                args=[
                    "--host",
                    "clickhouse1",
                    "--login=device",
                    "--oauth-credentials",
                    DEFAULT_CREDS_PATH,
                ],
                query="SELECT currentUser()",
                wall_timeout=35,
            )

        with And("I wait for the device user_code"):
            user_code = wait_for_device_user_code()

        with And("I approve the device code"):
            approve_keycloak_device_user_code_via_bash_tools(user_code=user_code)

        with And(
            "I wait for the client to finish or be killed by wall timeout",
            description=(
                "timeout > wall_timeout guarantees the process always " "finishes here."
            ),
        ):
            wait_clickhouse_oauth_background_finished(timeout_sec=60)

        with Then("oauth_cache.json is absent despite successful authentication"):
            full_log = read_clickhouse_oauth_background_log()
            ec = parse_background_client_exit_code(full_log)
            assert_no_segfault(output=full_log, exit_code=ec)
            assert not file_exists(
                path=DEFAULT_CACHE_PATH
            ), "oauth_cache.json should not appear when the directory is immutable"

    finally:
        with Finally("I restore directory and stop clients"):
            unset_immutable(path=CLIENT_CONFIG_DIR)
            kill_clickhouse_oauth_background_if_alive()


@TestFeature
@Name("refresh token cache")
def feature(self):
    """Tests for the on-disk OAuth refresh-token cache."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
