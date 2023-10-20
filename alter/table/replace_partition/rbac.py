from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, create_user
from helpers.tables import (
    create_table_partitioned_by_column,
    insert_into_table_random_uint64,
)


@TestStep(Given)
def no_privileges(self, node, name, on):
    """Grant no privileges to a user."""
    with By("Granting the user no privileges"):
        node.query(f"GRANT NONE ON {on} TO {name}")


@TestStep(Given)
def select_privileges(self, node, name, on):
    """Grant only select privileges to a user."""
    with By("Granting the user only select privileges"):
        node.query(f"GRANT SELECT ON {on} TO {name}")


@TestStep(Given)
def insert_privileges(self, node, name, on):
    """Grant only insert privileges to a user."""
    with By("Granting the user only insert privileges"):
        node.query(f"GRANT INSERT ON {on} TO {name}")


@TestStep(Given)
def alter_privileges(self, node, name, on):
    """Grant only alter privileges to a user."""
    with By("Granting the user only alter privileges"):
        node.query(f"GRANT ALTER ON {on} TO {name}")


@TestStep(Given)
def alter_table_privileges(self, node, name, on):
    """Grant only alter table privileges to a user."""
    with By("Granting the user only alter table privileges"):
        node.query(f"GRANT ALTER TABLE ON {on} TO {name}")


@TestCheck
def user_replace_partition_with_privileges(
    self,
    privilege_destination_table,
    privilege_source_table,
):
    """A test check to grant a user a set of privileges on both destination and source tables to see if replace
    partition is possible with these privileges."""
    node = self.context.node
    user_name = f"user_{getuid()}"
    destination_table = f"destination_{getuid()}"
    source_table = f"source_{getuid()}"

    with Given(
        "I create a destination table and a source table that are partitioned by the same column"
    ):
        create_table_partitioned_by_column(table_name=source_table)
        create_table_partitioned_by_column(table_name=destination_table)

    with And("I insert data into both tables"):
        insert_into_table_random_uint64(
            table_name=destination_table, number_of_values=10
        )
        insert_into_table_random_uint64(table_name=source_table, number_of_values=10)

    with When(
        "I create s user with specific privileges for destination table and source table"
    ):
        create_user(node=node, name=user_name)

        privilege_destination_table(node=node, name=user_name, on=destination_table)
        privilege_source_table(node=node, name=user_name, on=source_table)

    with Check(
        f"That replacing partition is possible on the destination table with given privileges"
    ):
        node.query(
            f"ALTER TABLE {destination_table} REPLACE PARTITION 1 FROM {source_table}",
            settings=[("user", user_name)],
            exitcode=0,
        )


@TestSketch(Scenario)
@Flags(TE)
def check_replace_partition_with_privileges(self):
    """Run the test check with different privileges combinations."""
    values = {
        no_privileges,
        select_privileges,
        alter_privileges,
        alter_table_privileges,
        insert_privileges,
    }

    user_replace_partition_with_privileges(
        privilege_destination_table=either(*values, i="privilege_destination_table"),
        privilege_source_table=either(*values, i="privilege_source_table"),
    )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Alter_Table_ReplacePartition_RBAC("1.0"))
@Name("rbac")
def feature(self, node="clickhouse1"):
    """Check that it is possible to replace partition on a table as a user with given privileges."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=check_replace_partition_with_privileges)
