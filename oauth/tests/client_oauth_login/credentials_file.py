"""Tests for ``--oauth-credentials`` file loading and validation."""

import json

from testflows.core import *
from testflows.combinatorics import CoveringArray

from oauth.requirements.requirements import (
    RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Format,
    RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Malformed,
    RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Missing,
    RQ_SRS_042_OAuth_Client_Login_CredentialsFile_MissingClientId,
)
from oauth.tests.steps.client_login import (
    CLIENT_CONFIG_DIR,
    DEFAULT_CREDS_PATH,
    assert_client_rejected,
    assert_no_segfault,
    create_directory,
    reset_client_state,
    run_clickhouse_client,
    write_oauth_credentials_file,
)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Missing("1.0"))
@Name("login with missing credentials file produces actionable error")
def missing_credentials_file(self):
    """Missing ``--oauth-credentials`` file SHALL produce a clear not-found error."""

    with Given("I reset the client state"):
        reset_client_state()

    missing_path = "/root/.clickhouse-client/does-not-exist.json"

    with When("I run clickhouse-client pointing at a missing credentials file"):
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

    with Then("the client exits with a file-not-found diagnostic"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=(missing_path, "open", "BAD_ARGUMENTS"),
        )

    with And("the diagnostic names the missing path"):
        assert (
            missing_path in output
        ), f"Expected missing path in output:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Malformed("1.0"))
@Name("login with malformed credentials JSON fails cleanly")
def malformed_credentials_json(self):
    """Malformed credentials JSON SHALL produce a parse error without crashing."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file containing malformed JSON"):
        write_oauth_credentials_file(raw_contents="{ this is not json")

    with When("I run clickhouse-client with the malformed credentials file"):
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

    with Then("the client exits with a parse diagnostic and no crash"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("BAD_ARGUMENTS", "JSON", "parse"),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_MissingClientId("1.0"))
@Name("login with credentials missing client_id is rejected")
def credentials_missing_client_id(self):
    """Credentials without ``client_id`` SHALL be rejected."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file missing client_id"):
        write_oauth_credentials_file(
            raw_contents='{"installed":{"auth_uri":"http://x","token_uri":"http://x"}}'
        )

    with When("I run clickhouse-client with the incomplete credentials file"):
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

    with Then("the client exits naming the missing client_id"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("client_id", "BAD_ARGUMENTS"),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Format("1.0"))
@Name("login top-level key 'web' accepted alongside 'installed'")
def credentials_top_level_web(self):
    """Top-level ``web`` key SHALL be accepted alongside ``installed``."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a credentials file with top-level 'web' key"):
        write_oauth_credentials_file(
            client_id="grafana-client",
            client_secret="grafana-secret",
            top_level_key="web",
        )

    with When("I run clickhouse-client with the 'web'-keyed credentials file"):
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

    with Then("the client did not reject the top-level 'web' key"):
        assert_client_rejected(output=output, exit_code=exit_code)
        assert (
            "missing 'installed' or 'web'" not in output
        ), f"Top-level 'web' key was rejected unexpectedly:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Malformed("1.0"))
@Name("credentials JSON empty object is rejected")
def credentials_empty_top_level_object(self):
    """Empty top-level ``{}`` SHALL be rejected."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write an empty JSON object"):
        write_oauth_credentials_file(raw_contents="{}")

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
            timeout=10,
            expect_error=True,
        )

    with Then("the client rejects the file"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("installed", "web", "bad_arguments"),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Malformed("1.0"))
@Name("credentials JSON top-level array is rejected")
def credentials_top_level_array_rejected(self):
    """Top-level JSON array SHALL be rejected."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write a JSON array"):
        write_oauth_credentials_file(raw_contents="[1,2,3]")

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
            timeout=10,
            expect_error=True,
        )

    with Then("the client fails without crashing"):
        assert_client_rejected(output=output, exit_code=exit_code)


@TestScenario
@Name("credentials missing auth_uri is rejected")
def credentials_missing_auth_uri(self):
    """Missing ``auth_uri`` SHALL be rejected."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I omit auth_uri"):
        write_oauth_credentials_file(
            raw_contents=(
                '{"installed":{"client_id":"x","token_uri":"http://localhost/x"}}'
            )
        )

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
            timeout=10,
            expect_error=True,
        )

    with Then("the client names auth_uri or BAD_ARGUMENTS"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("auth_uri", "bad_arguments"),
        )


@TestScenario
@Name("credentials missing token_uri is rejected")
def credentials_missing_token_uri(self):
    """Missing ``token_uri`` SHALL be rejected."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I omit token_uri"):
        write_oauth_credentials_file(
            raw_contents=(
                '{"installed":{"client_id":"x",' '"auth_uri":"http://localhost/auth"}}'
            )
        )

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
            timeout=10,
            expect_error=True,
        )

    with Then("the client names token_uri or BAD_ARGUMENTS"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("token_uri", "bad_arguments"),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_MissingClientId("1.0"))
@Name("credentials with empty client_id are rejected at OAuth")
def credentials_empty_client_id(self):
    """Empty ``client_id`` SHALL not succeed silently."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I write client_id as empty string"):
        write_oauth_credentials_file(client_id="")

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
            timeout=10,
            expect_error=True,
        )

    with Then("the flow fails without crashing"):
        assert_no_segfault(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Missing("1.0"))
@Name("--oauth-credentials pointing at directory fails")
def credentials_path_is_directory(self):
    """Directory path for ``--oauth-credentials`` SHALL fail."""

    with Given("I reset the client state"):
        reset_client_state()

    dir_path = f"{CLIENT_CONFIG_DIR}/not_a_file"

    with And("I create a directory at the credentials path"):
        create_directory(path=dir_path)

    with When("I pass that directory as --oauth-credentials"):
        exit_code, output = run_clickhouse_client(
            args=[
                "--host",
                "clickhouse1",
                "--login=device",
                "--oauth-credentials",
                dir_path,
            ],
            query="SELECT 1",
            timeout=10,
            expect_error=True,
        )

    with Then("the client errors without crashing"):
        assert_client_rejected(output=output, exit_code=exit_code)


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Format("1.0"))
@Name("credentials without client_secret document current behaviour")
def credentials_without_client_secret(self):
    """Missing ``client_secret`` SHALL surface a load or OAuth error."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I omit client_secret from JSON"):
        write_oauth_credentials_file(client_secret=None)

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
            timeout=10,
            expect_error=True,
        )

    with Then("the client refuses or fails OAuth without crashing"):
        assert_client_rejected(
            output=output,
            exit_code=exit_code,
            markers=("secret", "bad_arguments", "oauth"),
        )


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Format("1.0"))
@Name("extra fields in credentials JSON are ignored")
def credentials_unknown_extra_fields_are_ignored(self):
    """Unknown JSON fields SHALL be ignored."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I add unrelated inner keys"):
        write_oauth_credentials_file(
            extra={"unknown_field": "value", "another_key": 42},
        )

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

    with Then("OAuth starts instead of failing on unknown JSON keys"):
        assert_no_segfault(output=output, exit_code=exit_code)
        ol = output.lower()
        assert (
            "unknown field" not in ol and "unexpected property" not in ol
        ), f"Unexpected schema rejection:\n---\n{output}\n---"


@TestScenario
@Requirements(RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Format("1.0"))
@Name("unicode in client_id does not crash the loader")
def credentials_unicode_client_id(self):
    """Unicode ``client_id`` SHALL not crash the loader."""

    with Given("I reset the client state"):
        reset_client_state()

    with And("I use a unicode client_id"):
        write_oauth_credentials_file(client_id="client-id-with-\u00fcnic\u00f6d\u00eb")

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
            timeout=10,
            expect_error=True,
        )

    with Then("the client stays up"):
        assert_no_segfault(output=output, exit_code=exit_code)


_TOP_LEVEL_KEYS = {
    "installed": "installed",
    "web": "web",
    "unknown": "bogus_key",
}

_FIELD_VALUES = {
    "client_id": {
        "valid": "grafana-client",
        "empty": "",
        "number": 42,
        "object": {"nested": True},
    },
    "auth_uri": {
        "valid": "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth",
        "empty": "",
        "number": 9999,
        "object": {"url": "http://x"},
    },
    "token_uri": {
        "valid": "http://keycloak:8080/realms/grafana/protocol/openid-connect/token",
        "empty": "",
        "number": 9999,
        "object": {"url": "http://x"},
    },
    "client_secret": {
        "valid": "grafana-secret",
        "empty": "",
        "number": 12345,
    },
    "redirect_uris": {
        "valid": ["http://localhost"],
        "string": "http://localhost",
    },
    "device_authorization_uri": {
        "valid": "http://keycloak:8080/realms/grafana/protocol/openid-connect/auth/device",
        "empty": "",
        "number": 9999,
    },
}

_CREDS_DIMENSIONS = {
    "top_level_key": ["installed", "web", "unknown", "empty_object", "array"],
    "client_id": ["valid", "empty", "absent", "number", "object"],
    "auth_uri": ["valid", "empty", "absent", "number", "object"],
    "token_uri": ["valid", "empty", "absent", "number", "object"],
    "client_secret": ["valid", "absent", "empty", "number"],
    "redirect_uris": ["valid", "absent", "string"],
    "device_authorization_uri": ["valid", "absent", "empty", "number"],
}

_STRUCTURAL_DIAGNOSTIC_MARKERS = ("installed", "web", "bad_arguments", "missing")
_FIELD_DIAGNOSTIC_MARKERS = ("bad_arguments", "client_id", "auth_uri", "token_uri")


def _build_credentials_raw_json(combo):
    """Assemble the raw JSON credentials string for a CoveringArray combo."""
    top_name = combo["top_level_key"]

    if top_name == "array":
        return "[1, 2, 3]"
    if top_name == "empty_object":
        return "{}"

    top_key = _TOP_LEVEL_KEYS[top_name]
    inner = {}
    for field in (
        "client_id",
        "auth_uri",
        "token_uri",
        "client_secret",
        "redirect_uris",
        "device_authorization_uri",
    ):
        state = combo[field]
        if state != "absent":
            inner[field] = _FIELD_VALUES[field][state]

    return json.dumps({top_key: inner})


def _combo_expects_structural_rejection(combo):
    """True when the top-level JSON shape is wrong (array, empty, unknown key)."""
    return combo["top_level_key"] in ("array", "empty_object", "unknown")


def _combo_expects_field_rejection(combo):
    """True when a required field is absent, empty, or has the wrong type."""
    if _combo_expects_structural_rejection(combo):
        return False
    for field in ("client_id", "auth_uri", "token_uri"):
        if combo[field] != "valid":
            return True
    return False


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Format("1.0"),
    RQ_SRS_042_OAuth_Client_Login_CredentialsFile_Malformed("1.0"),
    RQ_SRS_042_OAuth_Client_Login_CredentialsFile_MissingClientId("1.0"),
)
@Name("credentials file combinatorial validation")
def credentials_combinatorial_validation(self):
    """Pairwise combinations of top-level key, required/optional field
    presence, and value types SHALL be validated without crashing."""

    for combo in CoveringArray(_CREDS_DIMENSIONS, strength=2):
        label = " ".join(f"{k}={v}" for k, v in combo.items())

        with Check(label):
            with Given("I reset the client state"):
                reset_client_state()

            raw_json = _build_credentials_raw_json(combo)

            with And(f"I write credentials JSON: {raw_json[:80]}"):
                write_oauth_credentials_file(raw_contents=raw_json)

            with When("I run clickhouse-client with the credentials file"):
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

            with Then("the client is rejected without crashing"):
                assert_client_rejected(output=output, exit_code=exit_code)

            if _combo_expects_structural_rejection(combo):
                with And("the output contains a structural diagnostic"):
                    assert_client_rejected(
                        output=output,
                        exit_code=exit_code,
                        markers=_STRUCTURAL_DIAGNOSTIC_MARKERS,
                    )

            elif _combo_expects_field_rejection(combo):
                with And("the output contains a field-validation diagnostic"):
                    assert_client_rejected(
                        output=output,
                        exit_code=exit_code,
                        markers=_FIELD_DIAGNOSTIC_MARKERS,
                    )


@TestFeature
@Name("credentials file")
def feature(self):
    """Tests for ``--oauth-credentials`` file loading and validation."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
