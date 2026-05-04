"""Tests for the on-disk OAuth refresh-token cache."""

from testflows.core import *

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_Cache_CorruptedIgnored,
    RQ_SRS_042_OAuth_Client_Login_Cache_FilePermissions,
)
from oauth.tests.steps.client_login import (
    DEFAULT_CACHE_PATH,
    DEFAULT_CREDS_PATH,
    assert_no_segfault,
    reset_client_state,
    run_clickhouse_client,
    stat_file_mode,
    write_oauth_cache,
    write_oauth_credentials_file,
)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_CorruptedIgnored("1.0"))
@Name("corrupted oauth_cache.json does not crash login flow")
def corrupted_cache_is_ignored(self):
    """Check that a corrupted ``oauth_cache.json`` is ignored rather than crashing the client."""

    reset_client_state()
    write_oauth_cache(raw_contents="garbage that is not json {][")
    write_oauth_credentials_file()

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

    assert_no_segfault(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_Cache_FilePermissions("1.0"))
@Name("oauth_cache.json is created with mode 0600")
def cache_file_mode_is_strict(self):
    """Check that ``oauth_cache.json`` ends up with mode 0600."""

    reset_client_state()
    write_oauth_cache(mapping={"abc123": "refresh-token-placeholder"}, mode="600")

    mode = stat_file_mode(path=DEFAULT_CACHE_PATH)
    assert mode == "600", f"Expected oauth_cache.json mode 600, got {mode!r}"


@TestFeature
@Name("refresh token cache")
def feature(self):
    """Tests for the on-disk OAuth refresh-token cache."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
