from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.tests.iceberg_engine.token_forwarding.steps import *


def commit_requests(namespace, table):
    """`POST .../namespaces/<ns>/tables/<table>` (Iceberg commitTable)."""
    return [
        r
        for r in catalog_requests()
        if r["method"] == "POST"
        and r["path"].endswith(f"/namespaces/{namespace}/tables/{table}")
    ]


@TestScenario
def insert_commits_as_the_querying_user(self):
    """Check that an INSERT into a forwarding database SHALL commit to the
    catalog with the inserting user's token."""
    writer = make_token("writer")

    with Given("an empty table and a forwarding database"):
        clean_mocks()
        namespace, table, _ = catalog_table(rows=[])
        database = forwarding_database()

    with When("writer inserts a row"):
        jwt_query(
            sql=f"INSERT INTO {table_identifier(database, namespace, table)} (name, double, integer) "
            f"VALUES ('written', 1.0, 7)",
            token=writer,
            settings=INSERT_SETTINGS,
        )

    with Then("the commit carried writer's token"):
        commits = commit_requests(namespace, table)
        assert commits, error("no commit request was recorded")
        assert tokens_presented(commits) == {("user", "writer")}, error()

    with And("the row is readable"):
        result = jwt_query(
            sql=select_rows_sql(database, namespace, table), token=writer
        )
        assert result.output.strip() == "written\t7", error()


@TestScenario
def async_insert_keeps_the_querying_user_token(self):
    """Check that an asynchronous INSERT SHALL commit with the inserting
    user's token even when the queue is flushed by a session without a token."""
    node = self.context.node
    writer = make_token("writer")
    query_id = f"async_insert_{getuid()}"

    with Given("an empty table and a forwarding database"):
        clean_mocks()
        namespace, table, _ = catalog_table(rows=[])
        database = forwarding_database()

    with When("writer sends an asynchronous insert that does not wait"):
        status, body = http_query(
            sql=f"INSERT INTO {http_table_identifier(database, namespace, table)} (name, double, integer) "
            f"VALUES ('async', 1.0, 9)",
            token=writer,
            params={
                "query_id": query_id,
                "async_insert": 1,
                "wait_for_async_insert": 0,
                "async_insert_use_adaptive_busy_timeout": 0,
                "async_insert_busy_timeout_ms": 600000,
                **dict(INSERT_SETTINGS),
            },
        )
        assert status == 200, error(body)

    with And("the default user flushes the queue"):
        node.query("SYSTEM FLUSH ASYNC INSERT QUEUE")

    with Then("the commit carried writer's token"):
        commits = commit_requests(namespace, table)
        assert commits, error("no commit request was recorded")
        assert tokens_presented(commits) == {("user", "writer")}, error()

    with And("the row is readable"):
        result = jwt_query(
            sql=select_rows_sql(database, namespace, table), token=writer
        )
        assert result.output.strip() == "async\t9", error()


@TestScenario
def async_inserts_of_different_users_are_not_merged(self):
    """Check that asynchronous INSERTs from different users SHALL NOT be
    flushed together under one user's token."""
    node = self.context.node
    users = ["alice", "bob"]

    with Given("an empty table and a forwarding database"):
        clean_mocks()
        namespace, table, _ = catalog_table(rows=[])
        database = forwarding_database()

    for user in users:
        with When(f"{user} sends an asynchronous insert that does not wait"):
            status, body = http_query(
                sql=f"INSERT INTO {http_table_identifier(database, namespace, table)} (name, double, integer) "
                f"VALUES ('{user}', 1.0, 1)",
                token=make_token(user),
                params={
                    "async_insert": 1,
                    "wait_for_async_insert": 0,
                    "async_insert_use_adaptive_busy_timeout": 0,
                    "async_insert_busy_timeout_ms": 600000,
                    **dict(INSERT_SETTINGS),
                },
            )
            assert status == 200, error(body)

    with And("the default user flushes the queue"):
        node.query("SYSTEM FLUSH ASYNC INSERT QUEUE")

    with Then("each user's rows were committed with their own token"):
        commits = commit_requests(namespace, table)
        assert tokens_presented(commits) == {
            ("user", "alice"),
            ("user", "bob"),
        }, error()

    with And("both rows are readable"):
        result = jwt_query(
            sql=select_rows_sql(database, namespace, table), token=make_token("alice")
        )
        assert result.output.strip() == "alice\t1\nbob\t1", error()


@TestScenario
def drop_table_reaches_the_catalog_as_the_querying_user(self):
    """Check that DROP TABLE in a forwarding database SHALL reach the catalog
    with the querying user's token and SHALL NOT request a service token."""
    node = self.context.node
    query_id = f"drop_{getuid()}"

    with Given("a table and a forwarding database that also has a catalog credential"):
        clean_mocks()
        namespace, table, _ = catalog_table()
        database = forwarding_database(catalog_credential=SERVICE_CREDENTIAL)

    with When("dropper drops the table"):
        jwt_query(
            sql=f"DROP TABLE {table_identifier(database, namespace, table)}",
            token=make_token("dropper"),
            settings=[("query_id", query_id)],
        )

    with Then("the catalog delete carried dropper's token"):
        deletes = [r for r in catalog_requests() if r["method"] == "DELETE"]
        assert deletes, error("no DELETE request was recorded")
        assert tokens_presented(deletes) == {("user", "dropper")}, error()

    with And("no service token was retrieved"):
        assert service_token_requests() == [], error()
        assert (
            query_log_profile_event(
                node, query_id, "DataLakeRestCatalogAuthTokenRetrieve"
            )
            == 0
        ), error()

    with And("the table is gone from the catalog"):
        result = jwt_query(
            sql=f"SHOW TABLES FROM {database}", token=make_token("dropper")
        )
        assert table not in result.output, error()


@TestFeature
@Name("writes")
def feature(self):
    """Writes and DDL reach the catalog as the querying user."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
