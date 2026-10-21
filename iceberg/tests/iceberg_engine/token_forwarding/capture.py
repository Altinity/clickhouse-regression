from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.tests.iceberg_engine.token_forwarding.steps import *


@TestStep(Given)
def password_user(self, node=None):
    """Create a password user that has the same grants as token users."""
    if node is None:
        node = self.context.node
    name = f"password_user_{getuid()}"
    password = f"pw_{getuid()}"
    try:
        node.query(f"CREATE USER {name} IDENTIFIED BY '{password}'")
        node.query(f"GRANT {TOKEN_ROLE} TO {name}")
        yield name, password
    finally:
        with Finally(f"drop user {name}"):
            node.query(f"DROP USER IF EXISTS {name}")


@TestScenario
def native_jwt_is_forwarded(self):
    """Check that ClickHouse SHALL present the querying user's own token to
    the catalog when the user connects over the native protocol with `--jwt`."""
    token = make_token("alice")

    with Given("a table and a forwarding database"):
        clean_mocks()
        namespace, table, rows = catalog_table()
        database = forwarding_database()

    with When("alice reads the table over the native protocol"):
        result = jwt_query(sql=select_rows_sql(database, namespace, table), token=token)

    with Then("the rows are returned"):
        assert result.output.strip() == expected_rows(rows), error()

    with And("every catalog request carried alice's token"):
        requests_ = catalog_requests()
        assert requests_, error("no catalog requests were recorded")
        assert {r["token"] for r in requests_} == {token}, error()


@TestScenario
def http_bearer_is_forwarded(self):
    """Check that ClickHouse SHALL present the querying user's own token to
    the catalog when the user authenticates over HTTP with `Authorization: Bearer`."""
    token = make_token("alice")

    with Given("a table and a forwarding database"):
        clean_mocks()
        namespace, table, rows = catalog_table()
        database = forwarding_database()

    with When("alice reads the table over HTTP"):
        status, body = http_query(
            sql=select_rows_sql(database, namespace, table, escaped=False), token=token
        )

    with Then("the rows are returned"):
        assert status == 200, error(body)
        assert body.strip() == expected_rows(rows), error()

    with And("every catalog request carried alice's token"):
        assert {r["token"] for r in catalog_requests()} == {token}, error()


@TestScenario
def password_user_is_denied(self):
    """Check that ClickHouse SHALL refuse catalog access with
    CATALOG_USER_TOKEN_NOT_AVAILABLE for a user that authenticated with a
    password, and SHALL NOT contact the catalog at all."""
    with Given("a forwarding database and a password user"):
        clean_mocks()
        namespace, table, _ = catalog_table()
        database = forwarding_database()
        user, password = password_user()

    with When("the password user reads the table"):
        self.context.node.query(
            select_rows_sql(database, namespace, table),
            settings=[("user", user), ("password", password)],
            exitcode=CATALOG_USER_TOKEN_NOT_AVAILABLE,
            ignore_exception=True,
            message=NO_TOKEN_MESSAGE,
        )

    with And("the password user lists the tables over HTTP"):
        status, body = http_query(
            sql=f"SHOW TABLES FROM {database}", user=user, password=password
        )
        assert status != 200, error(body)
        assert NOT_AVAILABLE in body, error(body)

    with Then("the catalog was not contacted"):
        assert catalog_requests() == [], error()
        assert service_token_requests() == [], error()


@TestScenario
def default_user_is_denied(self):
    """Check that ClickHouse SHALL refuse catalog access for the passwordless
    `default` user instead of falling back to anonymous catalog requests."""
    with Given("a forwarding database"):
        clean_mocks()
        catalog_table()
        database = forwarding_database()

    with When("the default user lists the tables"):
        self.context.node.query(
            f"SHOW TABLES FROM {database}",
            exitcode=CATALOG_USER_TOKEN_NOT_AVAILABLE,
            ignore_exception=True,
            message=NO_TOKEN_MESSAGE,
        )

    with Then("the catalog was not contacted"):
        assert catalog_requests() == [], error()


@TestScenario
def invalid_token_never_reaches_the_catalog(self):
    """Check that ClickHouse SHALL only forward tokens it has verified: a
    token signed with an unknown key fails authentication before any catalog call."""
    forged = jwt.encode({"sub": "alice"}, "not_the_server_secret", algorithm="HS256")

    with Given("a forwarding database"):
        clean_mocks()
        database = forwarding_database()

    with When("a client presents a forged token over HTTP"):
        status, body = http_query(sql=f"SHOW TABLES FROM {database}", token=forged)

    with Then("authentication fails"):
        assert status in (401, 403, 500), error(body)
        assert (
            "AUTHENTICATION_FAILED" in body or "Authentication failed" in body
        ), error(body)

    with And("the catalog was not contacted"):
        assert catalog_requests() == [], error()


@TestScenario
def disabled_server_setting_denies_forwarding(self):
    """Check that with `enable_token_forwarding = 0` ClickHouse SHALL refuse
    catalog access for token users with CATALOG_USER_TOKEN_NOT_AVAILABLE and
    SHALL NOT contact the catalog."""
    with Given("a forwarding database"):
        clean_mocks()
        namespace, table, _ = catalog_table()
        database = forwarding_database()

    with And("token forwarding is disabled with SYSTEM RELOAD CONFIG"):
        token_forwarding_disabled()

    with When("alice reads the table"):
        jwt_query(
            sql=select_rows_sql(database, namespace, table),
            token=make_token("alice"),
            exitcode=CATALOG_USER_TOKEN_NOT_AVAILABLE,
            ignore_exception=True,
            message=FORWARDING_DISABLED_MESSAGE,
        )

    with Then("the catalog was not contacted"):
        assert catalog_requests() == [], error()


@TestScenario
def reenabled_server_setting_restores_forwarding(self):
    """Check that `enable_token_forwarding` SHALL be hot-reloadable: after it is
    turned back on, new connections forward their tokens again."""
    token = make_token("alice")

    with Given("a forwarding database"):
        clean_mocks()
        namespace, table, rows = catalog_table()
        database = forwarding_database()

    with When("token forwarding is turned off and back on"):
        set_token_forwarding(enabled=False)
        set_token_forwarding(enabled=True)

    with Then("a new connection reads the table with alice's token"):
        result = jwt_query(sql=select_rows_sql(database, namespace, table), token=token)
        assert result.output.strip() == expected_rows(rows), error()
        assert {r["token"] for r in catalog_requests()} == {token}, error()


@TestScenario
def server_setting_is_reported_as_hot_reloadable(self):
    """Check that `system.server_settings` SHALL report `enable_token_forwarding`
    as changeable without restart, matching its SYSTEM RELOAD CONFIG behaviour."""
    with When("reading the setting from system.server_settings"):
        result = self.context.node.query(
            "SELECT changeable_without_restart FROM system.server_settings "
            "WHERE name = 'enable_token_forwarding'"
        )

    with Then("it is not reported as requiring a restart"):
        assert result.output.strip() != "No", error(
            "enable_token_forwarding reloads with SYSTEM RELOAD CONFIG "
            "but system.server_settings says it needs a restart"
        )


@TestScenario
def databases_without_forwarding_are_unaffected(self):
    """Check that forwarding SHALL be opt-in per database: a REST database
    without `oauth_forward_user_token` never receives the user's token."""
    token = make_token("alice")
    database = f"no_forwarding_{getuid()}"

    with Given("a REST database that uses a static auth header"):
        clean_mocks()
        catalog_table()
        node = self.context.node
        try:
            node.query(
                create_database_query(
                    database,
                    s3_access_key_id=self.context.minio_root_user,
                    s3_secret_access_key=self.context.minio_root_password,
                    settings={
                        "catalog_type": "rest",
                        "warehouse": WAREHOUSE,
                        "storage_endpoint": STORAGE_ENDPOINT,
                        "auth_header": "Authorization: Bearer static-catalog-token",
                    },
                )
            )

            with When("alice lists its tables"):
                jwt_query(sql=f"SHOW TABLES FROM {database}", token=token)

            with Then("the catalog only saw the static token"):
                assert {r["token"] for r in catalog_requests()} == {
                    "static-catalog-token"
                }, error()
        finally:
            with Finally("drop the database"):
                node.query(f"DROP DATABASE IF EXISTS {database} SYNC")


@TestFeature
@Name("capture")
def feature(self):
    """Which sessions carry a forwardable token and what happens without one."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
