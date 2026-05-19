"""Tests for the on-disk OAuth refresh-token cache."""

import json
import time

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
    assert_no_segfault,
    extract_device_user_code_from_client_output,
    file_exists,
    kill_clickhouse_oauth_background_if_alive,
    parse_background_client_exit_code,
    read_clickhouse_oauth_background_log,
    read_oauth_cache,
    reset_client_state,
    run_clickhouse_client,
    start_clickhouse_oauth_client_background,
    stat_file_mode,
    wait_clickhouse_oauth_background_finished,
    write_oauth_cache,
    write_oauth_credentials_file,
)


def _standard_device_creds():
    write_oauth_credentials_file(
        client_id="grafana-client",
        client_secret="grafana-secret",
        token_uri="http://keycloak:8080/realms/grafana/protocol/openid-connect/token",
        device_authorization_uri=(
            "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth/device"
        ),
    )


def _complete_device_login_via_background():
    """Run one successful device login (caller manages reset/cleanup)."""

    start_clickhouse_oauth_client_background(
        args=[
            "--host",
            "clickhouse1",
            "--login=device",
            "--oauth-credentials",
            DEFAULT_CREDS_PATH,
        ],
        query="SELECT currentUser()",
        wall_timeout=120,
    )
    user_code = None
    for _ in range(50):
        log_snippet = read_clickhouse_oauth_background_log()
        user_code = extract_device_user_code_from_client_output(log_snippet)
        if user_code:
            break
        time.sleep(1)
    assert user_code is not None, (
        "Timed out waiting for device user_code:\n"
        f"{read_clickhouse_oauth_background_log()}"
    )
    approve_keycloak_device_user_code_via_bash_tools(user_code=user_code)
    wait_clickhouse_oauth_background_finished(timeout_sec=90)
    full_log = read_clickhouse_oauth_background_log()
    ec = parse_background_client_exit_code(full_log)
    assert (
        ec == 0
    ), f"Expected exit 0 after device approval, got {ec!r}:\n---\n{full_log}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_CorruptedIgnored("1.0"))
@Name("corrupted oauth_cache.json does not crash login flow")
def corrupted_cache_is_ignored(self):
    """Corrupted ``oauth_cache.json`` is ignored rather than crashing."""

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
            timeout=10,
            expect_error=True,
        )

    with Then("the client did not crash"):
        assert_no_segfault(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_FilePermissions("1.0"))
@Name("oauth_cache.json is created with mode 0600")
def cache_file_mode_is_strict(self):
    """Pre-existing strict cache keeps ``0600``."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I pre-seed an oauth_cache.json with mode 0600"):
        write_oauth_cache(mapping={"abc123": "refresh-token-placeholder"}, mode="600")

    with Then("the cache file mode is 0600"):
        mode = stat_file_mode(path=DEFAULT_CACHE_PATH)
        assert mode == "600", f"Expected oauth_cache.json mode 600, got {mode!r}"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_Reuse("1.0"))
@Name("oauth_cache.json is written after successful device login")
def oauth_cache_written_after_successful_device_login(self):
    """Happy-path login persists refresh metadata."""

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I write OAuth credentials"):
            _standard_device_creds()

        with When("I complete one device login"):
            _complete_device_login_via_background()

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
    """Follow-up queries reuse cached tokens without user interaction."""

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I write OAuth credentials"):
            _standard_device_creds()

        with When("I complete the first device login"):
            _complete_device_login_via_background()

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
    """Rejected refresh tokens trigger a fresh device cycle."""

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I write OAuth credentials"):
            _standard_device_creds()

        with When("I complete the first device login"):
            _complete_device_login_via_background()

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
            assert_no_segfault(output=output, exit_code=exit_code)
            assert (
                extract_device_user_code_from_client_output(output) is not None
            ), f"Expected new device user_code after invalid_grant fallback:\n{output}"

    finally:
        with Finally("I stop background clients"):
            kill_clickhouse_oauth_background_if_alive()


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_FilePermissions("1.0"))
@Name("world-readable oauth_cache.json is handled safely")
def world_readable_oauth_cache_is_handled(self):
    """Loosely permissioned cache must not crash the client."""

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
            timeout=12,
            expect_error=True,
        )

    with Then("the client survives"):
        assert_no_segfault(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_CorruptedIgnored("1.0"))
@Name("oauth_cache JSON object with wrong shape starts device flow")
def oauth_cache_wrong_json_shape_starts_device_flow(self):
    """Non-mapping entries must behave like a cache miss."""

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
        assert_no_segfault(output=output, exit_code=exit_code)
        assert (
            extract_device_user_code_from_client_output(output) is not None
        ), f"Expected interactive device flow:\n{output}"


@TestScenario
@Name("read-only config dir allows login but blocks cache write")
def read_only_client_dir_blocks_cache_write(self):
    """Non-writable ``~/.clickhouse-client`` cannot persist cache."""

    try:
        with Given("I reset the client state"):
            reset_client_state()

        with And("I write OAuth credentials"):
            _standard_device_creds()

        with And("I make the config directory immutable"):
            # chmod 555 is insufficient when clickhouse-client runs as root;
            # chattr +i enforces immutability even for root.
            self.context.node.command(command=f"chattr +i {CLIENT_CONFIG_DIR}")

        with When("I start clickhouse-client with device login"):
            # Use a short wall_timeout so that if the client hangs trying to
            # write the immutable cache directory it is killed within the 90s
            # wait window rather than outliving it.
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

        user_code = None
        with And("I wait for the device user_code"):
            for _ in range(50):
                log_snippet = read_clickhouse_oauth_background_log()
                user_code = extract_device_user_code_from_client_output(log_snippet)
                if user_code:
                    break
                time.sleep(1)
            assert user_code is not None, (
                "Timed out waiting for device user_code:\n"
                f"{read_clickhouse_oauth_background_log()}"
            )

        with And("I approve the device code"):
            approve_keycloak_device_user_code_via_bash_tools(user_code=user_code)

        with And("I wait for the client to finish or be killed by wall timeout"):
            # timeout > wall_timeout guarantees the process always finishes here.
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
            self.context.node.command(
                command=f"chattr -i {CLIENT_CONFIG_DIR}",
                no_checks=True,
            )
            kill_clickhouse_oauth_background_if_alive()


@TestFeature
@Name("refresh token cache")
def feature(self):
    """Tests for the on-disk OAuth refresh-token cache."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
