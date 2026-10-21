from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.token_forwarding import *
from iceberg.tests.iceberg_engine.token_forwarding.steps import *


@TestScenario
@Requirements(
    RQ_Iceberg_TokenForwarding_REST_Passthrough("1.0"),
    RQ_Iceberg_TokenForwarding_Propagation_EveryCatalogRequest("1.0"),
)
def each_user_reaches_the_catalog_as_themselves(self):
    """Check that ClickHouse SHALL present each querying user's own token, so
    queries from different users on one database reach the catalog as different principals.
    """
    alice, bob = make_token("alice"), make_token("bob")

    with Given("a table and a forwarding database"):
        clean_mocks()
        namespace, table, rows = catalog_table()
        database = forwarding_database()

    with When("alice reads the table"):
        jwt_query(sql=select_rows_sql(database, namespace, table), token=alice)

    with Then("only alice's token reached the catalog"):
        assert tokens_presented(catalog_requests()) == {("user", "alice")}, error()

    with When("bob reads the same table"):
        reset_recorded_requests()
        jwt_query(sql=select_rows_sql(database, namespace, table), token=bob)

    with Then("only bob's token reached the catalog"):
        assert tokens_presented(catalog_requests()) == {("user", "bob")}, error()


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_REST_PerUserAuthorization("1.0"))
def catalog_authorization_applies_per_user(self):
    """Check that the catalog's per-principal authorization SHALL apply to
    each ClickHouse user: users see and read only the namespaces the catalog grants them.
    """
    alice, bob = make_token("alice"), make_token("bob")

    with Given("one table per user"):
        clean_mocks()
        ns_a, table_a, rows_a = catalog_table(rows=[("a", 1)])
        ns_b, table_b, rows_b = catalog_table(rows=[("b", 2)])
        database = forwarding_database()

    with And("the catalog lets alice see only her namespace and bob only his"):
        configure_mocks(
            catalog={"require_token": True, "allowed": {"alice": [ns_a], "bob": [ns_b]}}
        )

    with When("each user reads their own table"):
        a = jwt_query(sql=select_rows_sql(database, ns_a, table_a), token=alice)
        b = jwt_query(sql=select_rows_sql(database, ns_b, table_b), token=bob)

    with Then("both reads succeed"):
        assert a.output.strip() == expected_rows(rows_a), error()
        assert b.output.strip() == expected_rows(rows_b), error()

    with When("each user reads the other user's table"):
        a = jwt_query(
            sql=select_rows_sql(database, ns_b, table_b), token=alice, no_checks=True
        )
        b = jwt_query(
            sql=select_rows_sql(database, ns_a, table_a), token=bob, no_checks=True
        )

    with Then("both reads fail"):
        assert a.exitcode != 0, error(a.output)
        assert b.exitcode != 0, error(b.output)

    with When("alice lists the database tables"):
        listing = jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)

    with Then("only her namespace is listed"):
        assert f"{ns_a}.{table_a}" in listing.output, error()
        assert ns_b not in listing.output, error()


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_REST_NoServiceFallback("1.0"))
def no_fallback_to_the_service_credential(self):
    """Check that ClickHouse SHALL NOT fall back to `catalog_credential` when
    the session has no token, nor use it alongside a forwarded token."""
    with Given("a forwarding database that also has a catalog credential"):
        clean_mocks()
        namespace, table, rows = catalog_table()
        database = forwarding_database(catalog_credential=SERVICE_CREDENTIAL)

    with When("the default user reads the table"):
        self.context.node.query(
            select_rows_sql(database, namespace, table),
            exitcode=CATALOG_USER_TOKEN_NOT_AVAILABLE,
            ignore_exception=True,
            message=NO_TOKEN_MESSAGE,
        )

    with Then("no service token was requested and the catalog was not contacted"):
        assert service_token_requests() == [], error()
        assert catalog_requests() == [], error()

    with When("alice reads the table"):
        result = jwt_query(
            sql=select_rows_sql(database, namespace, table), token=make_token("alice")
        )
        assert result.output.strip() == expected_rows(rows), error()

    with Then("only alice's token was used"):
        assert service_token_requests() == [], error()
        assert tokens_presented(catalog_requests()) == {("user", "alice")}, error()


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_REST_Passthrough_NoRetry("1.0"))
def rejected_token_is_not_retried(self):
    """Check that in passthrough mode a catalog rejection SHALL be reported to
    the user without retrying with another credential."""
    with Given("a forwarding database that also has a catalog credential"):
        clean_mocks()
        namespace, table, _ = catalog_table()
        database = forwarding_database(catalog_credential=SERVICE_CREDENTIAL)

    with And("the catalog rejects the next requests with 401"):
        configure_mocks(catalog={"fail_next": [401] * 5})

    with When("alice reads the table"):
        result = jwt_query(
            sql=select_rows_sql(database, namespace, table),
            token=make_token("alice"),
            no_checks=True,
        )

    with Then("the query fails"):
        assert result.exitcode != 0, error(result.output)

    with And("ClickHouse sent one request and asked for no service token"):
        assert len(catalog_requests()) == 1, error()
        assert service_token_requests() == [], error()


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_REST_Config("1.0"))
def config_is_loaded_with_the_first_user_token(self):
    """Check that ClickHouse SHALL NOT call `/v1/config` when the database is
    created, and SHALL load it with the token of the first querying user."""
    token = make_token("alice")

    with Given("a forwarding database created by the default user"):
        clean_mocks()
        catalog_table()
        database = forwarding_database()

    with Then("the catalog was not contacted"):
        assert catalog_requests() == [], error()

    with When("alice lists its tables"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=token)

    with Then("`/v1/config` was requested with alice's token"):
        config = [r for r in catalog_requests() if r["path"].endswith("/config")]
        assert config, error("no /v1/config request was recorded")
        assert {r["token"] for r in config} == {token}, error()


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_REST_Passthrough("1.0"))
def a_new_token_replaces_the_old_one(self):
    """Check that in passthrough mode ClickHouse SHALL present the token of the
    current session, not one cached from an earlier session of the same user."""
    first = make_token("alice", session=1)
    second = make_token("alice", session=2)

    with Given("a table and a forwarding database"):
        clean_mocks()
        namespace, table, _ = catalog_table()
        database = forwarding_database()

    with When("alice reads the table with her first token"):
        jwt_query(sql=select_rows_sql(database, namespace, table), token=first)

    with And("alice reads it again with a new token"):
        reset_recorded_requests()
        jwt_query(sql=select_rows_sql(database, namespace, table), token=second)

    with Then("only the new token reached the catalog"):
        assert {r["token"] for r in catalog_requests()} == {second}, error()


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_Propagation_Concurrency("1.0"))
def concurrent_users_keep_their_identities(self):
    """Check that concurrent queries from different users SHALL each reach the
    catalog with their own token (no cross-user leakage under concurrency)."""
    import concurrent.futures

    users = ["alice", "bob", "carol", "dave"]
    iterations = 8

    with Given("one table per user, readable only by that user"):
        clean_mocks()
        tables = {user: catalog_table(rows=[(user, i)]) for i, user in enumerate(users)}
        database = forwarding_database()
        configure_mocks(
            catalog={
                "require_token": True,
                "allowed": {user: [tables[user][0]] for user in users},
            }
        )

    def read(user):
        namespace, table, _ = tables[user]
        result = mock_call(
            "POST",
            "/_mock/relay",
            {
                "url": f"http://{self.context.node.name}:8123/",
                "headers": {"Authorization": f"Bearer {make_token(user)}"},
                "body": select_rows_sql(database, namespace, table, escaped=False),
            },
        )
        return user, result["status"], result["body"]

    with When(
        f"{len(users)} users read their tables concurrently {iterations} times each"
    ):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(users) * 2) as pool:
            results = list(pool.map(read, users * iterations))

    with Then("every query succeeded with the user's own data"):
        failures = [(u, s, b[:300]) for u, s, b in results if s != 200]
        assert not failures, error(f"{len(failures)} queries failed: {failures[:3]}")
        for user, _, body in results:
            assert body.strip().split("\t")[0] == user, error(body)

    with And("the catalog never refused a request"):
        assert all(r["sub"] in users for r in catalog_requests()), error()


@TestFeature
@Name("rest passthrough")
def feature(self):
    """`oauth_forward_user_token = 1` without token exchange: the user token is
    sent to the REST catalog as is."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
