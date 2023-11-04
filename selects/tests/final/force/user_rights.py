import tests.steps as select
from helpers.common import check_clickhouse_version
from selects.requirements import *
from tests.steps.main_steps import *
import rbac.helper.errors as errors


@TestScenario
@Requirements()
def test_alias_columns(self, node=None):
    """Check for user rights `GRANT` and `REVOKE` options on `ALIAS` table for some
    columns with force finale enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    for table in self.context.tables:
        with Example(f"{table.name}", flags=TE):
            with Given("I make select as user without rights"):
                exitcode, message = errors.not_enough_privileges("some_user")
                node.query(
                    f"SELECT * FROM default.{table.name}",
                    settings=[("user", "some_user"), ("final", 1)],
                    message=message,
                    exitcode=exitcode
                )

            with And("I give rights"):
                node.query(
                    f"GRANT SELECT ON default.{table.name} TO some_user",
                    settings=[("final", 1)],
                )

            with Then("I check select is passing"):
                tmp = node.query(f"SELECT * FROM default.{table.name}", settings=[("user", "some_user"), ("final", 1)]).output
                note(tmp)
                node.query(
                    f"SELECT id,x FROM default.{table.name} FORMAT JSONEachRow;",
                    settings=[("user", "some_user"), ("final", 1)],
                    message='{"id":"1","x":"2"}',
                )

            with And("I revoke rights"):
                node.query(
                    f"REVOKE SELECT(id,x) ON default.{table.name} FROM some_user",
                    settings=[("final", 1)],
                )


@TestScenario
@Requirements()
def test_alias_columns_alias_column(self, node=None):
    """Check for user rights `GRANT` and `REVOKE` options on `ALIAS` table for alias
    columns with force finale enabled."""

    if node is None:
        node = self.context.cluster.node("clickhouse1")

    for table in self.context.tables:
        with Example(f"{table.name}", flags=TE):
            with Given("I make select as user without rights"):
                node.query(
                    f"SELECT(s) FROM default.{table.name}",
                    settings=[("user", "some_user"), ("final", 1)],
                    message="Not enough privileges",
                )

            with And("I give privileges to some_user"):
                node.query(
                    f"GRANT SELECT(s) ON default.{table.name} TO some_user",
                    settings=[("final", 1)],
                )

            with Then("I check select is passing"):
                node.query(
                    f"SELECT(s) FROM default.{table.name} FORMAT JSONEachRow;",
                    settings=[("user", "some_user"), ("final", 1)],
                    message='{"s":3}',
                )

            with And("I revoke privileges from some_user"):
                node.query(
                    f"REVOKE SELECT(s) ON default.{table.name} FROM some_user",
                    settings=[("final", 1)],
                )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_AutomaticFinalModifier_UserRights("1.0"))
@Name("user rights")
def feature(self, node=None):
    """User rights."""
    if check_clickhouse_version("<23.2")(self):
        skip(
            reason="force_select_final is only supported on ClickHouse version >= 23.2"
        )

    if node is None:
        node = self.context.cluster.node("clickhouse1")
    try:
        with Given("I create new user"):
            node.query("CREATE USER OR REPLACE some_user")

        with Then("I check user was created"):
            node.query("SHOW USERS", message="some_user")

        with And("I chose tables for testing"):
            self.context.tables = define(
                "tables",
                [
                    table
                    for table in self.context.tables
                    if table.name.startswith("alias")
                ],
                encoder=lambda tables: ", ".join([table.name for table in tables]),
            )

        for scenario in loads(current_module(), Scenario):
            scenario()

    finally:
        with Finally("I drop user"):
            node.query("DROP USER IF EXISTS some_user")
