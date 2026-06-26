from helpers.common import getuid
from jwt_authentication.tests.steps import create_static_jwt
from oauth.tests.steps.clikhouse import *
from oauth.tests.steps.common import *
from testflows.asserts import *
from oauth.requirements.requirements import *

_SECRET = "log_hygiene_test_secret_hs256"


@TestScenario
def newline_in_claim_does_not_inject_log_lines(self):
    """A newline embedded in a claim value SHALL be escaped so it cannot
    forge an independent log line (log-injection guard).
    """
    marker = "MARKER_" + getuid()[:8]
    node = self.context.node

    with Given("a static-key processor"):
        configure_static_key_processor(secret=_SECRET)

    with When("I authenticate with a newline-laden sub claim"):
        token = create_static_jwt(
            payload={"sub": f"alice\n{marker}"},
            secret=_SECRET,
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token)

    with Then("the marker never appears at the start of its own log line"):
        found = search_server_log(node, marker, lines=2000)
        forged = [
            line for line in found.splitlines() if line.lstrip().startswith(marker)
        ]
        assert not forged, error(
            "newline in claim value injected a forged log line: " f"{forged[:3]}"
        )


@TestScenario
def username_not_logged_at_default_level(self):
    """At the default log level, decoded usernames SHALL NOT be written
    to the server log (PII hygiene).
    """
    client = self.context.provider_client

    with Given("a provider OpenID processor"):
        configure_openid_token_processor(token_cache_lifetime=0)

    with And("I authenticate as 'demo'"):
        token = client.OAuthProvider.get_oauth_token().access_token
        access_clickhouse(token=token, status_code=200)

    with Then("the username does not appear in recent server log lines"):
        found = search_server_log(self.context.node, "demo", lines=1000)
        assert "demo" not in found, error(
            "username leaked into the server log at the default level"
        )


@TestScenario
def unknown_kid_not_reflected_in_logs(self):
    """Unknown ``kid`` header values SHALL NOT be echoed into the server
    log, preventing enumeration / log-flooding noise.
    """
    node = self.context.node
    kid_prefix = "probe_" + getuid()[:6] + "_"

    with Given("a static-key processor"):
        configure_static_key_processor(secret=_SECRET)

    with When("I send several requests each with a unique kid header"):
        for i in range(8):
            token = create_static_jwt(
                user_name="alice",
                secret=_SECRET,
                algorithm="HS256",
                key_id=f"{kid_prefix}{i}",
                expiration_minutes=5,
            )
            access_clickhouse(token=token)

    with Then("the kid values are not reflected into the server log"):
        found = search_server_log(node, kid_prefix, lines=2000)
        distinct = {
            line.split(kid_prefix)[1].split()[0]
            for line in found.splitlines()
            if kid_prefix in line
        }
        distinct.discard("")
        note(f"Distinct kids observed in log: {sorted(distinct)}")
        assert len(distinct) == 0, error(
            "unknown kid values were reflected into the server log"
        )


@TestScenario
def control_chars_in_sub_rejected(self):
    """A ``sub`` carrying shell/SQL metacharacters SHALL be sanitised so
    it does not create a dynamic user verbatim.
    """
    sentinel = "alice;DROP_" + getuid()[:6]

    with Given("a static-key processor"):
        configure_static_key_processor(secret=_SECRET)

    with When("I authenticate with a sub containing metacharacters"):
        token = create_static_jwt(
            user_name=sentinel,
            secret=_SECRET,
            algorithm="HS256",
            expiration_minutes=5,
        )

    with Then("the token is rejected (name sanitisation)"):
        assert_token_rejected(token=token)


@TestScenario
def processor_names_not_leaked_in_logs(self):
    """At the default log level, token-processor dispatch SHALL NOT leak
    internal processor names into the server log for an authenticated
    token. Processor names appearing only at <Debug>/<Trace> verbosity
    are operator-controlled diagnostic detail and are out of scope here
    (see ``username_not_logged_at_default_level`` for the same
    default-level scoping).
    """
    secret_a = "log_proc_secret_a"
    secret_b = "log_proc_secret_b"
    secret_c = "log_proc_secret_c"
    node = self.context.node

    with Given("three static-key processors all accepting HS256"):
        change_token_processors(
            processor_name="proc_a",
            processor_type="jwt_static_key",
            algo="HS256",
            static_key=secret_a,
            token_cache_lifetime=0,
            replace_section=True,
        )
        change_token_processors(
            processor_name="proc_b",
            processor_type="jwt_static_key",
            algo="HS256",
            static_key=secret_b,
            token_cache_lifetime=0,
        )
        change_token_processors(
            processor_name="proc_c",
            processor_type="jwt_static_key",
            algo="HS256",
            static_key=secret_c,
            token_cache_lifetime=0,
        )
        change_user_directories_config(
            processor="proc_a",
            common_roles=["general-role"],
        )

    marker = "mp_" + getuid()[:6]

    with When("I authenticate with a token signed by the wired processor's secret"):
        token = create_static_jwt(
            user_name=marker,
            secret=secret_a,
            algorithm="HS256",
            expiration_minutes=5,
        )
        access_clickhouse(token=token, status_code=200)

    with Then("no processor names appear in default-level log lines"):
        found = search_server_log(node, marker, lines=2000)
        verbose_levels = ("<Debug>", "<Trace>", "<Test>")
        hits = [
            line
            for line in found.splitlines()
            if ("proc_a" in line or "proc_b" in line or "proc_c" in line)
            and not any(level in line for level in verbose_levels)
        ]
        assert not hits, error(
            "processor names leaked into the server log at the default level"
        )


@TestFeature
@Name("log hygiene")
def feature(self):
    """Server-log hygiene tests: no log injection, no PII at default
    level, no kid/processor-name reflection, and sanitised principal
    names.
    """
    Scenario(run=newline_in_claim_does_not_inject_log_lines)
    Scenario(run=username_not_logged_at_default_level)
    Scenario(run=unknown_kid_not_reflected_in_logs)
    Scenario(run=control_chars_in_sub_rejected)
    Scenario(run=processor_names_not_leaked_in_logs)
