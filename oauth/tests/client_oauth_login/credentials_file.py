"""Tests for ``--oauth-credentials`` file loading and validation."""

from testflows.core import *
from testflows.asserts import error

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Format,
    RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Malformed,
    RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Missing,
    RQ_SRS_042_OAuth_Client_Login_CredentialsFile_MissingClientId,
)
from oauth.tests.steps.client_login import (
    DEFAULT_CREDS_PATH,
    assert_no_segfault,
    reset_client_state,
    run_clickhouse_client,
    write_oauth_credentials_file,
)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Missing("1.0"))
@Name("login with missing credentials file produces actionable error")
def missing_credentials_file(self):
    """Check that a missing ``--oauth-credentials`` file produces a clear error."""

    reset_client_state()
    missing_path = "/root/.clickhouse-client/does-not-exist.json"

    exit_code, output = run_clickhouse_client(
        args=[
            "--host",
            "clickhouse1",
            "--login=device",
            "--oauth-credentials",
            missing_path,
        ],
        query="SELECT 1",
        timeout=10,
        expect_error=True,
    )

    assert exit_code != 0, error()
    assert (
        missing_path in output
        or "open" in output.lower()
        or "BAD_ARGUMENTS" in output
    ), f"Expected file-not-found diagnostic, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Malformed("1.0"))
@Name("login with malformed credentials JSON fails cleanly")
def malformed_credentials_json(self):
    """Check that malformed credentials JSON produces a clean parse error."""

    reset_client_state()
    write_oauth_credentials_file(raw_contents="{ this is not json")

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

    assert exit_code != 0, error()
    assert_no_segfault(output=output, exit_code=exit_code)
    assert (
        "BAD_ARGUMENTS" in output
        or "JSON" in output
        or "parse" in output.lower()
    ), f"Expected JSON-parse diagnostic, got:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_MissingClientId("1.0"))
@Name("login with credentials missing client_id is rejected")
def credentials_missing_client_id(self):
    """Check that a credentials file without ``client_id`` is rejected."""

    reset_client_state()
    write_oauth_credentials_file(
        raw_contents='{"installed":{"auth_uri":"http://x","token_uri":"http://x"}}'
    )

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

    assert exit_code != 0, error()
    assert_no_segfault(output=output, exit_code=exit_code)
    assert "client_id" in output or "BAD_ARGUMENTS" in output, (
        f"Expected 'client_id' diagnostic, got:\n---\n{output}\n---"
    )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Format("1.0"))
@Name("login top-level key 'web' accepted alongside 'installed'")
def credentials_top_level_web(self):
    """Check that the ``web`` top-level key is accepted alongside ``installed``."""

    reset_client_state()
    write_oauth_credentials_file(
        client_id="grafana-client",
        client_secret="grafana-secret",
        top_level_key="web",
    )

    exit_code, output = run_clickhouse_client(
        args=[
            "--host",
            "clickhouse1",
            "--login=device",
            "--oauth-credentials",
            DEFAULT_CREDS_PATH,
        ],
        query="SELECT 1",
        timeout=8,
        expect_error=True,
    )

    assert exit_code != 0, error()
    assert "missing 'installed' or 'web'" not in output, (
        f"Top-level 'web' key was rejected unexpectedly:\n---\n{output}\n---"
    )
    assert_no_segfault(output=output, exit_code=exit_code)


@TestFeature
@Name("credentials file")
def feature(self):
    """Tests for ``--oauth-credentials`` file loading and validation."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
