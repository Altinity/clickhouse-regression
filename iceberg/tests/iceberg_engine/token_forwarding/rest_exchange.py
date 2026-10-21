import time

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.tests.iceberg_engine.token_forwarding.steps import *


@TestScenario
def exchange_request_follows_rfc_8693(self):
    """Check that ClickHouse SHALL exchange the user token with an RFC 8693
    form POST carrying the token exchange grant, the user token as
    `subject_token`, the default subject token type and the catalog credential."""
    token = make_token("alice")

    with Given("a table and a forwarding database with token exchange"):
        clean_mocks()
        namespace, table, rows = catalog_table()
        database = forwarding_database(exchange=True)

    with When("alice reads the table"):
        result = jwt_query(sql=select_rows_sql(database, namespace, table), token=token)
        assert result.output.strip() == expected_rows(rows), error()

    with Then("exactly one exchange request was sent"):
        exchanges = token_requests()
        assert len(exchanges) == 1, error()
        exchange = exchanges[0]
        form = exchange["form"]

    with And("it is a form POST with the RFC 8693 fields"):
        assert exchange["method"] == "POST", error()
        assert exchange["content_type"].startswith(
            "application/x-www-form-urlencoded"
        ), error()
        assert form["grant_type"] == TOKEN_EXCHANGE_GRANT, error()
        assert form["subject_token"] == token, error()
        assert form["subject_token_type"] == ACCESS_TOKEN_TYPE, error()
        assert form.get("requested_token_type") == ACCESS_TOKEN_TYPE, error()
        assert "actor_token" not in form, error()
        assert form["client_id"] == SERVICE_CLIENT_ID, error()
        assert form["client_secret"] == SERVICE_CLIENT_SECRET, error()

    with And("it does not authenticate with a bearer token"):
        assert exchange["authorization"] is None, error()

    with And("the catalog only saw alice's exchanged token"):
        assert tokens_presented(catalog_requests()) == {("exchanged", "alice")}, error()


@TestScenario
def configured_token_types_and_scope_are_sent(self):
    """Check that `oauth_subject_token_type`, `oauth_requested_token_type` and
    `auth_scope` SHALL be sent as `subject_token_type`, `requested_token_type`
    and `scope` in the exchange request."""
    with Given("a forwarding database with custom token types and scope"):
        clean_mocks()
        catalog_table()
        database = forwarding_database(
            exchange=True,
            oauth_subject_token_type=JWT_TOKEN_TYPE,
            oauth_requested_token_type=ID_TOKEN_TYPE,
            auth_scope="catalog:read",
        )

    with When("alice lists the tables"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=make_token("alice"))

    with Then("the exchange request carries the configured values"):
        form = token_requests()[0]["form"]
        assert form["subject_token_type"] == JWT_TOKEN_TYPE, error()
        assert form["requested_token_type"] == ID_TOKEN_TYPE, error()
        assert form["scope"] == "catalog:read", error()


@TestScenario
def actor_token_is_the_service_principal_token(self):
    """Check that with `oauth_forward_actor_token = 1` ClickHouse SHALL obtain
    a service token with the catalog credential and send it as `actor_token`
    of type access_token."""
    with Given("a forwarding database with an actor token"):
        clean_mocks()
        catalog_table()
        database = forwarding_database(exchange=True, actor=True)

    with When("alice lists the tables"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=make_token("alice"))

    with Then("a service token was requested with the catalog credential"):
        grants = service_token_requests()
        assert grants, error("no client credentials grant was recorded")
        assert grants[0]["form"]["client_id"] == SERVICE_CLIENT_ID, error()

    with And("it was sent as the actor token"):
        form = token_requests()[0]["form"]
        assert form["actor_token_type"] == ACCESS_TOKEN_TYPE, error()
        assert form["actor_token"].count(".") == 2, error()

    with And("the service token was never used for catalog calls"):
        assert tokens_presented(catalog_requests()) == {("exchanged", "alice")}, error()


@TestScenario
def exchanged_token_is_cached_per_user_token(self):
    """Check that ClickHouse SHALL cache exchanged tokens per user token: the
    same token is exchanged once, while another user or another token of the
    same user gets its own exchange."""
    node = self.context.node
    alice = make_token("alice")

    with Given("a forwarding database with token exchange"):
        clean_mocks()
        catalog_table()
        database = forwarding_database(exchange=True)

    with When("alice lists the tables twice"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)
        query_id = f"cached_{getuid()}"
        jwt_query(
            sql=f"SHOW TABLES FROM {database}",
            token=alice,
            settings=[("query_id", query_id)],
        )

    with Then("her token was exchanged once"):
        assert [r["form"]["subject_token"] for r in token_requests()] == [
            alice
        ], error()

    with And("the second query hit the exchanged-token cache"):
        hits = query_log_profile_event(
            node, query_id, "DataLakeRestCatalogUserTokenCacheHits"
        )
        exchanges = query_log_profile_event(
            node, query_id, "DataLakeRestCatalogTokenExchange"
        )
        assert hits > 0, error()
        assert exchanges == 0, error()

    with When("bob and alice with a new token list the tables"):
        bob = make_token("bob")
        alice_again = make_token("alice", session=2)
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=bob)
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice_again)

    with Then("each new token was exchanged on its own"):
        subjects = [r["form"]["subject_token"] for r in token_requests()]
        assert subjects == [alice, bob, alice_again], error()


@TestScenario
def zero_cache_ttl_exchanges_every_time(self):
    """Check that `oauth_user_token_cache_ttl = 0` SHALL disable the
    exchanged-token cache."""
    alice = make_token("alice")

    with Given("a forwarding database with exchange and no token cache"):
        clean_mocks()
        catalog_table()
        database = forwarding_database(exchange=True, oauth_user_token_cache_ttl=0)

    with When("alice lists the tables twice"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)
        first = len(token_requests())
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)

    with Then("the second query exchanged the token again"):
        assert len(token_requests()) > first >= 1, error()


@TestScenario
def cache_ttl_bounds_the_exchanged_token_lifetime(self):
    """Check that an exchanged token SHALL NOT be reused after
    `oauth_user_token_cache_ttl` seconds even if the endpoint grants a longer lifetime.
    """
    alice = make_token("alice")

    with Given("a forwarding database with a 2 second token cache"):
        clean_mocks()
        catalog_table()
        database = forwarding_database(exchange=True, oauth_user_token_cache_ttl=2)

    with When("alice lists the tables, waits 4 seconds and lists them again"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)
        time.sleep(4)
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)

    with Then("the token was exchanged twice"):
        assert len(token_requests()) == 2, error()


@TestScenario
def expires_in_bounds_the_exchanged_token_lifetime(self):
    """Check that an exchanged token SHALL NOT be reused after the
    `expires_in` returned by the token endpoint."""
    alice = make_token("alice")

    with Given("a token endpoint that issues 3 second tokens"):
        clean_mocks()
        configure_mocks(token={"expires_in": 3})
        catalog_table()
        database = forwarding_database(exchange=True)

    with When("alice lists the tables, waits 5 seconds and lists them again"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)
        before = len(token_requests())
        time.sleep(5)
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)

    with Then("the second query exchanged the token again"):
        assert before >= 1, error()
        assert len(token_requests()) > before, error()


@TestScenario
def missing_expires_in_is_bounded_by_the_cache_ttl(self):
    """Check that when the token endpoint omits `expires_in` the exchanged
    token SHALL still expire after `oauth_user_token_cache_ttl`."""
    alice = make_token("alice")

    with Given("a token endpoint without expires_in and a 3 second cache"):
        clean_mocks()
        configure_mocks(token={"expires_in": None})
        catalog_table()
        database = forwarding_database(exchange=True, oauth_user_token_cache_ttl=3)

    with When("alice lists the tables, waits 5 seconds and lists them again"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)
        before = len(token_requests())
        time.sleep(5)
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)

    with Then("the second query exchanged the token again"):
        assert before >= 1, error()
        assert len(token_requests()) > before, error()


@TestScenario
def failed_exchange_does_not_fall_back(self):
    """Check that a failed exchange SHALL fail the query without contacting the
    catalog with the user token or the service credential, and SHALL count
    `DataLakeRestCatalogTokenExchangeFailures`."""
    node = self.context.node
    query_id = f"exchange_failure_{getuid()}"

    with Given("a token endpoint that rejects the next exchanges"):
        clean_mocks()
        configure_mocks(token={"fail_next": [400] * 5})
        namespace, table, _ = catalog_table()
        database = forwarding_database(exchange=True)
        failures = event_value(node, "DataLakeRestCatalogTokenExchangeFailures")

    with When("alice reads the table"):
        result = jwt_query(
            sql=select_rows_sql(database, namespace, table),
            token=make_token("alice"),
            settings=[("query_id", query_id)],
            no_checks=True,
        )

    with Then("the query fails and names the token endpoint"):
        assert result.exitcode != 0, error(result.output)
        assert "OAuth token endpoint" in result.output, error(result.output)

    with And("the catalog was not contacted"):
        assert catalog_requests() == [], error()
        assert service_token_requests() == [], error()

    with And("the failure was counted"):
        assert (
            event_value(node, "DataLakeRestCatalogTokenExchangeFailures") > failures
        ), error()


@TestScenario
def wrong_catalog_credential_fails_the_exchange(self):
    """Check that a catalog credential the token endpoint rejects SHALL fail
    the query and SHALL NOT expose the user token."""
    token = make_token("alice")

    with Given("a forwarding database with a wrong client secret"):
        clean_mocks()
        catalog_table()
        database = forwarding_database(
            exchange=True, catalog_credential="clickhouse:wrong"
        )

    with When("alice lists the tables"):
        result = jwt_query(
            sql=f"SHOW TABLES FROM {database}", token=token, no_checks=True
        )

    with Then("the query fails without revealing the token"):
        assert result.exitcode != 0, error(result.output)
        assert token not in result.output, error()
        assert catalog_requests() == [], error()


@TestScenario
def error_bodies_do_not_leak_the_subject_token(self):
    """Check that ClickHouse SHALL NOT include the token endpoint's error body
    in errors or logs, since it may echo the user token."""
    node = self.context.node
    token = make_token("alice", leak_probe=getuid())

    with Given("a token endpoint that echoes the subject token in its errors"):
        clean_mocks()
        configure_mocks(token={"fail_next": [400] * 5, "echo_subject_on_error": True})
        catalog_table()
        database = forwarding_database(exchange=True)

    with When("alice lists the tables over HTTP"):
        status, body = http_query(sql=f"SHOW TABLES FROM {database}", token=token)

    with Then("the query fails"):
        assert status != 200, error(body)
        assert token_requests(), error("the token endpoint was not called")

    with And("the error returned to the client does not contain the token"):
        assert token not in body, error()

    with And("the server logs do not contain the token"):
        assert_not_in_logs(node, token, "the user token")


@TestScenario
def unauthorized_catalog_response_triggers_a_new_exchange(self):
    """Check that when the catalog answers 401 to an exchanged token ClickHouse
    SHALL exchange the user token again and retry once."""
    alice = make_token("alice")

    with Given("a table and a forwarding database with token exchange"):
        clean_mocks()
        namespace, table, rows = catalog_table()
        database = forwarding_database(exchange=True)

    with And("alice already has a cached exchanged token"):
        jwt_query(sql=f"SHOW TABLES FROM {database}", token=alice)
        reset_recorded_requests()

    with And("the catalog rejects the next exchanged token with 401"):
        configure_mocks(catalog={"fail_next": [401], "fail_token_kind": "exchanged"})

    with When("alice reads the table"):
        result = jwt_query(sql=select_rows_sql(database, namespace, table), token=alice)

    with Then("the read succeeds"):
        assert result.output.strip() == expected_rows(rows), error()

    with And("the token was exchanged again"):
        assert len(token_requests()) == 1, error()
        assert token_requests()[0]["form"]["subject_token"] == alice, error()


@TestScenario
def exchange_metrics_and_profile_events(self):
    """Check that ClickHouse SHALL count exchanges in
    `DataLakeRestCatalogTokenExchange`, cache entries in
    `DataLakeCatalogUserTokenCacheEntries`, and SHALL NOT count service token
    retrievals for forwarded queries."""
    node = self.context.node
    query_id = f"exchange_events_{getuid()}"

    with Given("a forwarding database with token exchange"):
        clean_mocks()
        catalog_table()
        database = forwarding_database(exchange=True)
        before = metric_value(node, "DataLakeCatalogUserTokenCacheEntries")

    with When("a new user lists the tables"):
        jwt_query(
            sql=f"SHOW TABLES FROM {database}",
            token=make_token(f"user_{getuid()}"),
            settings=[("query_id", query_id)],
        )

    with Then("one exchange and no service token retrieval were counted"):
        assert (
            query_log_profile_event(node, query_id, "DataLakeRestCatalogTokenExchange")
            == 1
        ), error()
        assert (
            query_log_profile_event(
                node, query_id, "DataLakeRestCatalogTokenExchangeMicroseconds"
            )
            > 0
        ), error()
        assert (
            query_log_profile_event(
                node, query_id, "DataLakeRestCatalogAuthTokenRetrieve"
            )
            == 0
        ), error()

    with And("the cache entry metric grew"):
        assert (
            metric_value(node, "DataLakeCatalogUserTokenCacheEntries") > before
        ), error()


@TestFeature
@Name("rest exchange")
def feature(self):
    """`oauth_token_exchange_uri`: the user token is exchanged (RFC 8693) for a
    catalog session token."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
