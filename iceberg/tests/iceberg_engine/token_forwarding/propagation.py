from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.token_forwarding import *
from iceberg.tests.iceberg_engine.token_forwarding.steps import *


@TestStep(Given)
def impersonated_user(self, node=None):
    """Create a password user that token users may impersonate with EXECUTE AS."""
    if node is None:
        node = self.context.node
    name = f"impersonated_{getuid()}"
    try:
        node.query(f"CREATE USER {name} IDENTIFIED BY 'pw_{getuid()}'")
        node.query(f"GRANT {TOKEN_ROLE} TO {name}")
        node.query(f"GRANT IMPERSONATE ON {name} TO {TOKEN_ROLE}")
        yield name
    finally:
        with Finally(f"drop user {name}"):
            node.query(
                f"REVOKE IMPERSONATE ON {name} FROM {TOKEN_ROLE}", no_checks=True
            )
            node.query(f"DROP USER IF EXISTS {name}")


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_Propagation_ExecuteAs("1.0"))
def execute_as_does_not_carry_the_token(self):
    """Check that a query run with EXECUTE AS another user SHALL NOT use the
    caller's token for catalog access."""
    with Given("a forwarding database and a user alice may impersonate"):
        clean_mocks()
        namespace, table, _ = catalog_table()
        database = forwarding_database()
        target = impersonated_user()

    with When("alice reads the table as the other user"):
        result = jwt_query(
            sql=f"EXECUTE AS {target} {select_rows_sql(database, namespace, table)}",
            token=make_token("alice"),
            no_checks=True,
        )

    with Then("the read is refused because the impersonated session has no token"):
        assert result.exitcode == CATALOG_USER_TOKEN_NOT_AVAILABLE, error(result.output)
        assert NO_TOKEN_MESSAGE in result.output, error(result.output)

    with And("alice's token never reached the catalog"):
        assert catalog_requests() == [], error()


@TestStep(Given)
def database_on_two_nodes(self):
    """The same forwarding database on this node and on the second node."""
    other = self.context.nodes[1]
    namespace, table, _ = catalog_table()
    database = f"token_forwarding_{getuid()}"
    forwarding_database(database_name=database)
    forwarding_database(database_name=database, node=other)
    return other, database, namespace, table


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_Propagation_LocalNodeOnly("1.0"))
def token_does_not_leave_the_node(self):
    """Check that a query that reaches another node with `remote()` SHALL NOT
    send the user's token to that node, so the remote catalog access fails."""
    with Given("the same forwarding database on two nodes"):
        clean_mocks()
        other, database, namespace, table = database_on_two_nodes()

    with When("alice reads the table on the other node through remote()"):
        result = jwt_query(
            sql=f"SELECT count() FROM remote('{other.name}', {database}, '{namespace}.{table}')",
            token=make_token("alice"),
            no_checks=True,
        )

    with Then("the read fails"):
        assert result.exitcode != 0, error(result.output)

    with And("the catalog never received alice's token"):
        assert ("user", "alice") not in tokens_presented(catalog_requests()), error()


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_Propagation_RemoteNodeError("1.0"))
def remote_node_reports_the_missing_token(self):
    """Check that when a remote node cannot reach a forwarding catalog for
    lack of a token it SHALL report CATALOG_USER_TOKEN_NOT_AVAILABLE to the
    initiator instead of dropping the connection."""
    with Given("the same forwarding database on two nodes"):
        clean_mocks()
        other, database, namespace, table = database_on_two_nodes()

    with When("alice reads the table on the other node through remote()"):
        result = jwt_query(
            sql=f"SELECT count() FROM remote('{other.name}', {database}, '{namespace}.{table}')",
            token=make_token("alice"),
            no_checks=True,
        )

    with Then("the error names the missing token"):
        assert NOT_AVAILABLE in result.output, error(result.output)
        assert "ATTEMPT_TO_READ_AFTER_EOF" not in result.output, error(result.output)


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_Propagation_Confidentiality("1.0"))
def tokens_are_not_logged(self):
    """Check that neither the user token nor the exchanged token SHALL appear
    in server logs, `system.query_log` or `system.text_log`."""
    node = self.context.node
    token = make_token("alice", log_probe=getuid())

    with Given("a forwarding database with token exchange"):
        clean_mocks()
        namespace, table, _ = catalog_table()
        database = forwarding_database(exchange=True)

    with When("alice reads the table over HTTP and the native protocol"):
        http_query(
            sql=select_rows_sql(database, namespace, table, escaped=False),
            token=token,
            expected_status=200,
        )
        jwt_query(sql=select_rows_sql(database, namespace, table), token=token)

    with Then("the user token is not in the logs"):
        assert_not_in_logs(node, token, "the user token")

    with And("the exchanged token is not in the logs"):
        exchanged = {
            r["token"] for r in catalog_requests() if r["token_kind"] == "exchanged"
        }
        assert exchanged, error("no exchanged token was recorded")
        for value in exchanged:
            assert_not_in_logs(node, value, "the exchanged token")


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_Propagation_HTTPSession("1.0"))
def http_session_uses_the_current_token(self):
    """Check that within one named HTTP session ClickHouse SHALL forward the
    token presented with the current request."""
    session_id = f"session_{getuid()}"
    first, second = make_token("alice", session=1), make_token("alice", session=2)

    with Given("a table and a forwarding database"):
        clean_mocks()
        namespace, table, _ = catalog_table()
        database = forwarding_database()

    sql = select_rows_sql(database, namespace, table, escaped=False)

    with When("alice queries in a named session with her first token"):
        http_query(
            sql=sql, token=first, params={"session_id": session_id}, expected_status=200
        )

    with And("alice continues the session with a new token"):
        reset_recorded_requests()
        http_query(
            sql=sql,
            token=second,
            params={"session_id": session_id},
            expected_status=200,
        )

    with Then("only the new token reached the catalog"):
        assert {r["token"] for r in catalog_requests()} == {second}, error()


@TestFeature
@Name("propagation")
def feature(self):
    """Where the forwarded token travels and where it must not."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
