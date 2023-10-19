from testflows.core import *
from testflows.asserts import *
from alter.table.replace_partition.requirements.requirements import *
from helpers.common import getuid, create_user
from helpers.tables import create_table, Column
from helpers.datatypes import *


@TestStep(Given)
def two_privileges(self, node, name, on, privilege1, privilege2):
    """Grant two privileges to a user."""
    with By(f"Granting the user {privilege1} and {privilege2} privileges"):
        node.query(f"GRANT {privilege1}, {privilege2} ON {on} TO {name}")


@TestStep(Given)
def all_privileges(self, node, name, on, privilege):
    """Grant all privileges to a user."""
    with By("Granting the user all privileges"):
        node.query(f"GRANT ALL ON {on} TO {name}")


@TestStep(Given)
def no_privileges(self, node, name, on):
    """Grant no privileges to a user."""
    with Given("I grant the user no privileges"):
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


@TestOutline
def create_tables_with_partitions(self, node, destination, source):
    """An outline to create two tables with partitions, with the same structure and insert values needed for test
    scenarios."""
    with By("Creating a MergeTree table partitioned by column p"):
        create_table(
            name=destination,
            engine="MergeTree",
            partition_by="p",
            order_by="tuple()",
            columns=[
                Column(name="p", datatype=UInt8()),
                Column(name="i", datatype=UInt64()),
            ],
        )
    with And("Creating a new table with the same structure as the destination"):
        node.query(f"CREATE TABLE {source} AS {destination}")

    with When("I insert the data into destination"):
        node.query(f"INSERT INTO {destination} VALUES (1, 1), (2, 2)")

    with And(
        "I insert the same data into source but with the different value for column i"
    ):
        node.query(f"INSERT INTO {source} VALUES (1, 1) (2, 3)")


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
    destination = f"destination_{getuid()}"
    source = f"source_{getuid()}"

    with Given("I create a destination table and a source table with partitions"):
        create_tables_with_partitions(node=node, destination=destination, source=source)

    with When(
        "I create s user with specific privileges for destination and source tables"
    ):
        create_user(node=node, name=user_name)

        privilege_destination_table(node=node, name=user_name, on=destination)
        privilege_source_table(node=node, name=user_name, on=source)

    with Check(
        f"Replace Partition when destination table has {privilege_destination_table.__name__} and source has {privilege_source_table.__name__}"
    ):
        node.query(
            f"ALTER TABLE {destination} REPLACE PARTITION 1 FROM {source}",
            settings=[("user", user_name)],
            exitcode=0,
        )


@TestSketch(Scenario)
@Flags(TE)
def check_replace_partition_with_privileges(self):
    """Run the test check with different privileges combinations."""
    values = {
        all_privileges,
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
    """Check that it is possible replace partition as a user with different privileges."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=check_replace_partition_with_privileges)
