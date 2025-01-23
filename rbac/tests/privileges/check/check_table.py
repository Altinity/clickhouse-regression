from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *
from rbac.helper.common import *
import rbac.helper.errors as errors


@TestSuite
def table_privileges_granted_directly(self, node=None):
    """Check that a user is able to execute `CHECK TABLE` command on a table
    if and only if he has CHECK privilege on that table granted directly.
    """

    user_name = f"user_{getuid()}"

    if node is None:
        node = self.context.node

    with user(node, f"{user_name}"):
        table_name = f"table_name_{getuid()}"

        Suite(
            run=check_privilege,
            examples=Examples(
                "privilege on grant_target_name user_name table_name",
                [
                    tuple(list(row) + [user_name, user_name, table_name])
                    for row in check_privilege.examples
                ],
                args=Args(name="check privilege={privilege}", format_name=True),
            ),
        )


@TestSuite
def table_privileges_granted_via_role(self, node=None):
    """Check that a user is able to execute `CHECK TABLE` command on a table
    if and only if he has CHECK privilege on that table granted via role.
    """

    user_name = f"user_{getuid()}"
    role_name = f"role_{getuid()}"

    if node is None:
        node = self.context.node

    with user(node, f"{user_name}"), role(node, f"{role_name}"):
        table_name = f"table_name_{getuid()}"

        with When("I grant the role to the user"):
            node.query(f"GRANT {role_name} TO {user_name}")

        Suite(
            run=check_privilege,
            examples=Examples(
                "privilege on grant_target_name user_name table_name",
                [
                    tuple(list(row) + [role_name, user_name, table_name])
                    for row in check_privilege.examples
                ],
                args=Args(name="check privilege={privilege}", format_name=True),
            ),
        )


@TestOutline(Suite)
@Examples(
    "privilege on",
    [
        ("ALL", "*.*"),
        ("CHECK", "*.*"),
        ("CHECK", "table"),
    ],
)
def check_privilege(
    self, privilege, on, grant_target_name, user_name, table_name, node=None
):
    """Run checks for commands that require CHECK privilege."""

    if node is None:
        node = self.context.node

    Suite(test=check)(
        privilege=privilege,
        on=on,
        grant_target_name=grant_target_name,
        user_name=user_name,
        table_name=table_name,
    )


@TestSuite
@Requirements(
    RQ_SRS_006_RBAC_CheckTable_RequiredPrivilege("1.0"),
)
def check(self, privilege, on, grant_target_name, user_name, table_name, node=None):
    """Check that user is able to execute CHECK on a table if and only if the
    user has CHECK TABLE privilege on that table.
    """
    exitcode, message = errors.not_enough_privileges(name=user_name)

    if node is None:
        node = self.context.node

    if on == "table":
        on = f"{table_name}"

    with table(node, table_name):
        with Scenario("CHECK without privilege"):
            with When("I grant the user NONE privilege"):
                node.query(f"GRANT NONE TO {grant_target_name}")

            with And("I grant the user USAGE privilege"):
                node.query(f"GRANT USAGE ON *.* TO {grant_target_name}")

            with Then(f"I CHECK {table_name}"):
                node.query(
                    f"CHECK TABLE {table_name}",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )

        with Scenario("CHECK with privilege"):
            with When(f"I grant {privilege} on the table"):
                node.query(f"GRANT {privilege} ON {on} TO {grant_target_name}")

            with Then(f"I CHECK {table_name}"):
                node.query(f"CHECK TABLE {table_name}", settings=[("user", user_name)])

        with Scenario("CHECK with revoked privilege"):
            with When(f"I grant {privilege} on the table"):
                node.query(f"GRANT {privilege} ON {on} TO {grant_target_name}")

            with And(f"I revoke {privilege} on the table"):
                node.query(f"REVOKE {privilege} ON {on} FROM {grant_target_name}")

            with Then(f"I CHECK {table_name}"):
                node.query(
                    f"CHECK TABLE {table_name}",
                    settings=[("user", user_name)],
                    exitcode=exitcode,
                    message=message,
                )


@TestFeature
@Name("check table")
def feature(self, node="clickhouse1"):
    """Check the RBAC functionality of SHOW TABLES."""
    self.context.node = self.context.cluster.node(node)

    Suite(run=table_privileges_granted_directly, setup=instrument_clickhouse_server_log)
    Suite(run=table_privileges_granted_via_role, setup=instrument_clickhouse_server_log)
