import tests.select_steps as select
from helpers.common import check_clickhouse_version
from tests.concurrent_query_steps import *
from tests.steps import *


@TestOutline
@Requirements()
def test_alias(self, table_name, node=None):
    """
    Creating `ALIAS` table.
    """
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    try:
        with Given("I create table"):
            node.query(f"CREATE TABLE IF NOT EXISTS {table_name}(x Int32, y Int32, s Int32 ALIAS x + y) "
                       "ENGINE = MergeTree ORDER BY tuple()")
        yield
    finally:
        with Finally("I drop table"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")


@TestScenario
@Requirements()
def test_alias_columns(self, node=None):
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    table_name = f"user_rights_{getuid()}"

    test_alias(table_name=table_name)

    with Given("I make select as user without rights"):
        node.query(f"SELECT * FROM default.{table_name}", settings=[("user", "some_user")], message="Received from localhost:9000."
                                                                                     " DB::Exception: some_user: "
                                                                                     "Not enough privileges. To execute"
                                                                                     " this query it's necessary")

    with And("I give rights"):
        node.query(f"GRANT SELECT(x,y) ON default.{table_name} TO some_user")

    with Then("I check select is passing"):
        node.query(f"SELECT * FROM default.{table_name}", settings=[("user", "some_user")])

    with And("I give rights"):
        node.query(f"REVOKE SELECT(x,y) ON default.{table_name} FROM some_user")


@TestScenario
@Requirements()
def test_alias_columns_alias_column(self, node=None):
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    table_name = f"user_rights_{getuid()}"

    test_alias(table_name=table_name)

    with Given("I make select as user without rights"):
        node.query(f"SELECT(s) FROM default.{table_name}", settings=[("user", "some_user")], message="Received from localhost:9000."
                                                                                     " DB::Exception: some_user: "
                                                                                     "Not enough privileges. To execute"
                                                                                     " this query it's necessary")

    with And("I give rights"):
        node.query(f"GRANT SELECT(s) ON default.{table_name} TO some_user")

    with Then("I check select is passing"):
        node.query(f"SELECT(s) FROM default.{table_name}", settings=[("user", "some_user")])

    with And("I give rights"):
        node.query(f"REVOKE SELECT(s) ON default.{table_name} FROM some_user")


@TestModule
@Requirements()
@Name("force modifier user rights")
def feature(self, node=None):
    """User rights."""
    if check_clickhouse_version("<22.11")(self):
        skip(
            reason="force_select_final is only supported on ClickHouse version >= 22.11"
        )

    if node is None:
        node = self.context.cluster.node("clickhouse1")
    try:
        with Given("I create new user"):
            node.query("CREATE USER OR REPLACE some_user")

        with Then("I check user was created"):
            node.query("SHOW USERS", message="some_user")

        for scenario in loads(current_module(), Scenario):
            scenario()

    finally:
        with Finally("I drop user"):
            node.query("DROP USER IF EXISTS some_user")

