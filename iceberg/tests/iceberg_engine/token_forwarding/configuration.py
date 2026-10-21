from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.tests.iceberg_engine.token_forwarding.steps import *

REST_INVALID = [
    (
        "auth header",
        {"auth_header": "Authorization: Bearer static"},
        "`oauth_forward_user_token` cannot be combined with `auth_header`",
    ),
    (
        "exchange without catalog credential",
        {"oauth_token_exchange_uri": TOKEN_EXCHANGE_URL},
        "`oauth_token_exchange_uri` requires a non-empty `catalog_credential`",
    ),
    (
        "actor token without exchange",
        {"catalog_credential": SERVICE_CREDENTIAL, "oauth_forward_actor_token": 1},
        "`oauth_forward_actor_token`",
    ),
    (
        "invalid subject token type",
        {
            "catalog_credential": SERVICE_CREDENTIAL,
            "oauth_token_exchange_uri": TOKEN_EXCHANGE_URL,
            "oauth_subject_token_type": "access_token",
        },
        "must be one of the token type URNs defined by RFC 8693",
    ),
    (
        "empty subject token type",
        {
            "catalog_credential": SERVICE_CREDENTIAL,
            "oauth_token_exchange_uri": TOKEN_EXCHANGE_URL,
            "oauth_subject_token_type": "",
        },
        "must be one of the token type URNs defined by RFC 8693",
    ),
    (
        "invalid requested token type",
        {
            "catalog_credential": SERVICE_CREDENTIAL,
            "oauth_token_exchange_uri": TOKEN_EXCHANGE_URL,
            "oauth_requested_token_type": "urn:example:custom",
        },
        "must be one of the token type URNs defined by RFC 8693",
    ),
    (
        "cache ttl without exchange",
        {"oauth_user_token_cache_ttl": 10},
        "`oauth_user_token_cache_ttl` has no effect without `oauth_token_exchange_uri`",
    ),
    (
        "subject token type without exchange",
        {"oauth_subject_token_type": JWT_TOKEN_TYPE},
        "`oauth_subject_token_type` has no effect without `oauth_token_exchange_uri`",
    ),
]

WITHOUT_FORWARDING_INVALID = [
    ("oauth_token_exchange_uri", TOKEN_EXCHANGE_URL),
    ("oauth_subject_token_type", JWT_TOKEN_TYPE),
    ("oauth_requested_token_type", JWT_TOKEN_TYPE),
    ("oauth_user_token_cache_ttl", 10),
    ("oauth_forward_actor_token", 1),
]

GLUE_INVALID = [
    (
        "missing role",
        {"aws_role_arn": None},
        "`oauth_forward_user_token` requires a non-empty `aws_role_arn` for a Glue catalog",
    ),
    (
        "static keys",
        {"aws_access_key_id": "test", "aws_secret_access_key": "test"},
        "`oauth_forward_user_token` cannot be combined with `aws_access_key_id`",
    ),
    (
        "token exchange",
        {"oauth_token_exchange_uri": TOKEN_EXCHANGE_URL},
        "`oauth_token_exchange_uri`",
    ),
    (
        "actor token",
        {"oauth_forward_actor_token": 1},
        "`oauth_forward_actor_token`",
    ),
]

TOKEN_TYPES = [
    "urn:ietf:params:oauth:token-type:access_token",
    "urn:ietf:params:oauth:token-type:refresh_token",
    "urn:ietf:params:oauth:token-type:id_token",
    "urn:ietf:params:oauth:token-type:saml1",
    "urn:ietf:params:oauth:token-type:saml2",
    "urn:ietf:params:oauth:token-type:jwt",
]


def create_and_expect_error(catalog, settings, message, forwarding=True):
    node = current().context.node
    database = f"invalid_{getuid()}"
    if forwarding:
        settings = forwarding_database_settings(catalog=catalog, **settings)
    try:
        node.query(
            create_database_query(database, catalog=catalog, settings=settings),
            exitcode=BAD_ARGUMENTS,
            ignore_exception=True,
            message=message,
        )
    finally:
        node.query(f"DROP DATABASE IF EXISTS {database} SYNC")


@TestScenario
def invalid_rest_settings_are_rejected(self):
    """Check that CREATE DATABASE SHALL reject invalid token forwarding
    settings for a REST catalog with BAD_ARGUMENTS."""
    for name, settings, message in REST_INVALID:
        with Check(name, flags=TE):
            create_and_expect_error("rest", settings, message)


@TestScenario
def exchange_settings_require_forwarding(self):
    """Check that CREATE DATABASE SHALL reject exchange-only settings when
    `oauth_forward_user_token` is not enabled."""
    for name, value in WITHOUT_FORWARDING_INVALID:
        with Check(name, flags=TE):
            create_and_expect_error(
                "rest",
                {
                    "catalog_type": "rest",
                    "warehouse": WAREHOUSE,
                    "catalog_credential": SERVICE_CREDENTIAL,
                    name: value,
                },
                f"`{name}`",
                forwarding=False,
            )


@TestScenario
def unsupported_catalog_type_is_rejected(self):
    """Check that `oauth_forward_user_token` SHALL be rejected for catalog
    types other than REST and Glue."""
    create_and_expect_error(
        "rest",
        {
            "catalog_type": "unity",
            "warehouse": "unity",
            "oauth_forward_user_token": 1,
        },
        "`oauth_forward_user_token` is only supported for `catalog_type = 'rest'`",
        forwarding=False,
    )


@TestScenario
def invalid_glue_settings_are_rejected(self):
    """Check that CREATE DATABASE SHALL reject invalid token forwarding
    settings for a Glue catalog with BAD_ARGUMENTS."""
    for name, settings, message in GLUE_INVALID:
        with Check(name, flags=TE):
            create_and_expect_error("glue", settings, message)


@TestScenario
def all_rfc_8693_token_types_are_accepted(self):
    """Check that every RFC 8693 token type URN SHALL be accepted as the
    subject and requested token type."""
    for token_type in TOKEN_TYPES:
        with Check(token_type.rsplit(":", 1)[-1], flags=TE):
            forwarding_database(
                exchange=True,
                oauth_subject_token_type=token_type,
                oauth_requested_token_type=token_type,
            )


@TestScenario
def sts_endpoint_must_pass_the_host_filter(self):
    """Check that `aws_sts_endpoint` SHALL be checked against
    `remote_url_allow_hosts`."""
    database = f"glue_{getuid()}"
    node = self.context.node
    try:
        node.query(
            create_database_query(
                database,
                catalog="glue",
                settings=forwarding_database_settings(
                    catalog="glue", aws_sts_endpoint="http://not-allowed-host:80"
                ),
            ),
            exitcode=UNACCEPTABLE_URL,
            ignore_exception=True,
            message="UNACCEPTABLE_URL",
        )
    finally:
        node.query(f"DROP DATABASE IF EXISTS {database} SYNC")


@TestScenario
def token_exchange_uri_must_pass_the_host_filter(self):
    """Check that ClickHouse SHALL NOT send user tokens to an
    `oauth_token_exchange_uri` host outside `remote_url_allow_hosts`."""
    node = self.context.node

    with Given("the token endpoint addressed by an IP that is not in the allow list"):
        clean_mocks()
        catalog_table()
        ip = node.command("getent hosts token-mocks | awk '{print $1}'").output.strip()
        assert ip, error("could not resolve token-mocks")

    with When("a database uses that endpoint for token exchange"):
        database = f"token_forwarding_{getuid()}"
        try:
            create = node.query(
                create_database_query(
                    database,
                    s3_access_key_id=self.context.minio_root_user,
                    s3_secret_access_key=self.context.minio_root_password,
                    settings=forwarding_database_settings(
                        exchange=True,
                        oauth_token_exchange_uri=f"http://{ip}:8190/token",
                    ),
                ),
                no_checks=True,
            )

            if create.exitcode == 0:
                with And("alice lists the tables"):
                    result = jwt_query(
                        sql=f"SHOW TABLES FROM {database}",
                        token=make_token("alice"),
                        no_checks=True,
                    )
                    assert result.exitcode != 0, error(result.output)

            with Then("the user token was never sent to it"):
                assert token_requests() == [], error()
        finally:
            node.query(f"DROP DATABASE IF EXISTS {database} SYNC")


@TestScenario
def catalog_url_must_pass_the_host_filter(self):
    """Check that a forwarding database SHALL NOT send user tokens to a catalog
    host outside `remote_url_allow_hosts`."""
    node = self.context.node

    with Given("the catalog addressed by an IP that is not in the allow list"):
        clean_mocks()
        ip = node.command("getent hosts token-mocks | awk '{print $1}'").output.strip()

    database = f"token_forwarding_{getuid()}"
    try:
        with When("a forwarding database points at that catalog"):
            create = node.query(
                create_database_query(
                    database,
                    url=f"http://{ip}:8181/v1",
                    s3_access_key_id=self.context.minio_root_user,
                    s3_secret_access_key=self.context.minio_root_password,
                    settings=forwarding_database_settings(),
                ),
                no_checks=True,
            )
            if create.exitcode == 0:
                jwt_query(
                    sql=f"SHOW TABLES FROM {database}",
                    token=make_token("alice"),
                    no_checks=True,
                )

        with Then("the catalog never received the user token"):
            assert ("user", "alice") not in tokens_presented(
                catalog_requests()
            ), error()
    finally:
        node.query(f"DROP DATABASE IF EXISTS {database} SYNC")


@TestScenario
def detach_and_attach_keep_forwarding(self):
    """Check that a forwarding database SHALL keep forwarding user tokens after
    DETACH DATABASE and ATTACH DATABASE."""
    node = self.context.node
    token = make_token("alice")

    with Given("a table and a forwarding database with token exchange"):
        clean_mocks()
        namespace, table, rows = catalog_table()
        database = forwarding_database(exchange=True)

    with When("the database is detached and attached"):
        node.query(f"DETACH DATABASE {database}")
        node.query(f"ATTACH DATABASE {database}")

    with Then("alice reads the table with her exchanged token"):
        result = jwt_query(sql=select_rows_sql(database, namespace, table), token=token)
        assert result.output.strip() == expected_rows(rows), error()
        assert tokens_presented(catalog_requests()) == {("exchanged", "alice")}, error()


@TestScenario
def credential_rotation_clears_the_token_cache(self):
    """Check that changing `catalog_credential` with ALTER DATABASE SHALL
    require a token, SHALL validate the new credential, and SHALL make later
    queries exchange user tokens with the new credential."""
    node = self.context.node
    alice = make_token("alice")
    alter = (
        "ALTER DATABASE {database} MODIFY SETTING catalog_credential = '{credential}'"
    )

    with Given("a forwarding database with token exchange"):
        clean_mocks()
        catalog_table()
        database = forwarding_database(exchange=True)

    with And("alice has a cached exchanged token"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)

    with When("the default user changes the credential"):
        result = node.query(
            alter.format(database=database, credential="clickhouse:rotated_secret"),
            no_checks=True,
        )

    with Then("the change is refused without a token"):
        assert result.exitcode != 0, error(result.output)
        assert NOT_AVAILABLE in result.output, error(result.output)

    with When("alice sets a credential the token endpoint rejects"):
        result = jwt_query(
            sql=alter.format(database=database, credential="clickhouse:rotated_secret"),
            token=alice,
            no_checks=True,
        )

    with Then("the change is refused"):
        assert result.exitcode != 0, error(result.output)

    with When("the token endpoint accepts the new secret and alice sets it"):
        configure_mocks(token={"client_secret": "rotated_secret"})
        reset_recorded_requests()
        jwt_query(
            sql=alter.format(database=database, credential="clickhouse:rotated_secret"),
            token=alice,
        )

    with And("alice lists the tables again"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)

    with Then("her token was exchanged with the new secret"):
        secrets = [r["form"]["client_secret"] for r in token_requests()]
        assert secrets, error("no exchange after the credential change")
        assert set(secrets) == {"rotated_secret"}, error()

    with And("the old cached exchanged token is no longer used"):
        assert tokens_presented(catalog_requests()) == {("exchanged", "alice")}, error()


@TestFeature
@Name("configuration")
def feature(self):
    """Create-time validation, host filtering and credential rotation."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
