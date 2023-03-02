import time

from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *
from rbac.helper.common import *


@TestFeature
@Requirements()
@Name("orphaned role")
def feature(self, stress=None, node="clickhouse1"):
    """Check that roles are being promoted correctly."""
    node = self.context.cluster.node(node)

    role_name = f"role_{getuid()}"
    user_name = f"user_{getuid()}"
    table_name = f"table_{getuid()}"

    if stress is not None:
        self.context.stress = stress

    with role(node, role_name):
        with user(node, user_name):
            with Given("The user has no privileges"):
                node.query(f"REVOKE ALL ON *.* FROM {user_name}")

            with And(f"I grant {role_name} to {user_name}"):
                node.query(f"GRANT {role_name} TO {user_name}")

            with And(f"I have a table {table_name}"):
                node.query(f"CREATE TABLE {table_name} (n int) engine=Memory")

            with When(
                f"I login as {user_name}",
            ):
                node.command("apt install -y screen")
                node.command(f"screen -d -m bash -c 'clickhouse client -u {user_name}'")

            with When("I want for 10 min 30sec"):
                time.sleep(630)

            with And(f"I GRANT SELECT ON {table_name} TO {role_name}"):
                node.query(f"GRANT SELECT ON {table_name} TO {role_name}")

            with Then(f"I try to SELECT from {table_name} as {user_name}"):
                node.query(
                    f"SELECT * FROM {table_name}", settings=[("user", user_name)]
                )

    with Finally(f"I remove {table_name}"):
        node.query(f"DROP TABLE IF EXISTS {table_name}")
