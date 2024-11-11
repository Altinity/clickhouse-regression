from testflows.asserts import *

from alter.table.attach_partition.common import create_partitions_with_random_uint64
from alter.table.attach_partition.requirements.requirements import *
from helpers.common import (
    getuid,
    create_user,
    attach_partition,
    attach_partition_from,
    detach_partition,
    attach_part,
    detach_part,
)
from helpers.rbac import *
from helpers.tables import create_table_partitioned_by_column

from itertools import combinations_with_replacement


def get_privileges_as_list_of_strings(privileges):
    """The test check takes a list of privileges to assign to a specific table for a user.
    This test step takes the list of test steps that grant privilege and converts it to the list of privilege names as
    strings.
    """
    privilege_names = []
    for privilege in privileges:
        privilege_names.append(privilege.__name__)

    return privilege_names


@TestStep(Check)
def check_if_partition_values_on_destination_changed(
    self, source_table, destination_table, user_name, changed=True
):
    """Assert two possibilities:
    - When we expect that `attach partition from` was successful due to valid privileges.
    - When we expect that `attach partition from` was not successful due to invalid privileges.
    """
    node = self.context.node

    with By(
        "trying to attach partition on the destination table as a user with set privileges"
    ):
        if changed:
            attach_partition_from(
                destination_table=destination_table,
                source_table=source_table,
                user_name=user_name,
            )
        else:
            attach_partition_from(
                destination_table=destination_table,
                source_table=source_table,
                user_name=user_name,
                message=f"Exception: {user_name}: Not enough privileges.",
                exitcode=241,
            )

    with And("checking if the data on the specific partition was attached or not"):
        partition_values_source = node.query(
            f"SELECT * FROM {source_table} WHERE p == 1 ORDER BY tuple(*) FORMAT TabSeparated"
        )
        partition_values_destination = node.query(
            f"SELECT * FROM {destination_table} WHERE p == 1 ORDER BY tuple(*) FORMAT TabSeparated"
        )

        if changed:
            for retry in retries(count=5, delay=1):
                with retry:
                    assert (
                        partition_values_source.output.strip()
                        == partition_values_destination.output.strip()
                    ), error()
        else:
            assert (
                partition_values_source.output.strip()
                != partition_values_destination.output.strip()
            ), error()


@TestCheck
def user_attach_partition_from_with_privileges(
    self,
    destination_table_privileges,
    source_table_privileges,
):
    """A test check to grant a user a set of privileges on both destination and source tables to see if `attach
    partition from` is possible with these privileges."""
    node = self.context.node
    user_name = f"user_{getuid()}"
    destination_table = f"destination_{getuid()}"
    source_table = f"source_{getuid()}"

    with Given(
        "I create a destination table and a source table that are partitioned by the same column",
        description=f"""
        Privileges:
        Destination table: {get_privileges_as_list_of_strings(
            privileges=destination_table_privileges
        )}
        Source table: {get_privileges_as_list_of_strings(
            privileges=source_table_privileges
        )}
        """,
    ):
        create_table_partitioned_by_column(table_name=source_table)
        create_table_partitioned_by_column(table_name=destination_table)

    with And("I insert data into both tables"):
        create_partitions_with_random_uint64(
            table_name=destination_table, number_of_values=10, bias=6
        )
        create_partitions_with_random_uint64(
            table_name=source_table, number_of_values=10
        )

    with And("I create a user"):
        create_user(node=node, name=user_name)

    with When(
        "I grant specific privileges for destination table and source table to a created user"
    ):
        for grant_privilege in destination_table_privileges:
            grant_privilege(node=node, user=user_name, table=destination_table)

        for grant_privilege in source_table_privileges:
            grant_privilege(node=node, user=user_name, table=source_table)

    with And(
        "I determine the privileges needed to attach partition to the destination table"
    ):
        destination_privileges = get_privileges_as_list_of_strings(
            privileges=destination_table_privileges
        )
        source_privileges = get_privileges_as_list_of_strings(
            privileges=source_table_privileges
        )

        if ("select_privileges" in source_privileges) and (
            (
                "alter_privileges" in destination_privileges
                and "insert_privileges" in destination_privileges
            )
            or (
                "alter_table_privileges" in destination_privileges
                and "insert_privileges" in destination_privileges
            )
        ):
            with Then(
                f"I check that attaching partition is possible to the destination table when the user has enough privileges"
            ):
                check_if_partition_values_on_destination_changed(
                    destination_table=destination_table,
                    source_table=source_table,
                    user_name=user_name,
                )
        else:
            with Then(
                f"I check that attaching partition to the destination table outputs an error when the user does not "
                f"have enough privileges",
            ):
                check_if_partition_values_on_destination_changed(
                    destination_table=destination_table,
                    source_table=source_table,
                    user_name=user_name,
                    changed=False,
                )


@TestCheck
def user_attach_partition_with_privileges(
    self,
    table_privileges,
):
    """A test check to grant a user a set of privileges to see if `attach
    partition` is possible with these privileges."""

    node = self.context.node
    user_name = f"user_{getuid()}"
    table = f"{getuid()}"

    with Given(
        "I create a table",
        description=f"""
        Privileges: {get_privileges_as_list_of_strings(
            privileges=table_privileges
        )}
        """,
    ):
        create_table_partitioned_by_column(table_name=table)

    with And("I insert data into the table"):
        create_partitions_with_random_uint64(table_name=table, number_of_values=10)
        data_before_attach = node.query(
            f"SELECT * FROM {table} ORDER BY p,i,extra FORMAT TabSeparated"
        )

    with And("I detach a partition from the table"):
        detach_partition(table=table)

    with And("I create a user"):
        create_user(node=node, name=user_name)

    with When("I grant specific privileges for table to a created user"):
        for grant_privilege in table_privileges:
            grant_privilege(node=node, user=user_name, table=table)

    with And("I determine the privileges needed to attach partition to the table"):
        privileges = get_privileges_as_list_of_strings(privileges=table_privileges)

        if "insert_privileges" in privileges:
            with Then(
                f"I check that attaching partition is possible when the user has enough privileges"
            ):
                attach_partition(table=table, user_name=user_name)

            with Then("I check that data was attached"):
                data_after_attach = node.query(
                    f"SELECT * FROM {table} ORDER BY p,i,extra FORMAT TabSeparated"
                )
                for retry in retries(timeout=10, delay=2):
                    with retry:
                        assert data_after_attach.output == data_before_attach.output
        else:
            with Then(
                f"I check that attaching partition outputs an error when the user does not "
                f"have enough privileges",
            ):
                attach_partition(
                    table=table,
                    user_name=user_name,
                    message=f"Exception: {user_name}: Not enough privileges.",
                    exitcode=241,
                )


@TestCheck
def user_attach_part_with_privileges(
    self,
    table_privileges,
):
    """A test check to grant a user a set of privileges to see if `attach
    part` is possible with these privileges."""

    node = self.context.node
    user_name = f"user_{getuid()}"
    table = f"{getuid()}"

    with Given(
        "I create a table",
        description=f"""
        Privileges: {get_privileges_as_list_of_strings(
            privileges=table_privileges
        )}
        """,
    ):
        create_table_partitioned_by_column(table_name=table)

    with And("I insert data into the table"):
        create_partitions_with_random_uint64(table_name=table, number_of_values=10)
        data_before_attach = node.query(
            f"SELECT * FROM {table} ORDER BY p,i,extra FORMAT TabSeparated"
        )

    with And("I detach a part from the table"):
        detach_part(table=table, part="1_1_1_0")

    with And("I create a user"):
        create_user(node=node, name=user_name)

    with When("I grant specific privileges for table to a created user"):
        for grant_privilege in table_privileges:
            grant_privilege(node=node, user=user_name, table=table)

    with And("I determine the privileges needed to attach part to the table"):
        privileges = get_privileges_as_list_of_strings(privileges=table_privileges)

        if "insert_privileges" in privileges:
            with Then(
                f"I check that attaching part is possible when the user has enough privileges"
            ):
                attach_part(table=table, part="1_1_1_0", user_name=user_name)

            with Then("I check that data was attached"):
                data_after_attach = node.query(
                    f"SELECT * FROM {table} ORDER BY p,i,extra FORMAT TabSeparated"
                )
                for retry in retries(timeout=10, delay=2):
                    with retry:
                        assert data_after_attach.output == data_before_attach.output
        else:
            with Then(
                f"I check that attaching a part outputs an error when the user does not "
                f"have enough privileges",
            ):
                attach_part(
                    table=table,
                    part="1_1_1_0",
                    user_name=user_name,
                    message=f"Exception: {user_name}: Not enough privileges.",
                    exitcode=241,
                )


@TestSketch(Scenario)
@Flags(TE)
def check_attach_partition_from_with_privileges(self):
    """Check `attach partition from` with different combination of privileges on source and destination tables."""
    values = {
        no_privileges,
        select_privileges,
        alter_privileges,
        alter_table_privileges,
        insert_privileges,
    }

    values_combinations = list(combinations_with_replacement(values, 2))

    destination_table_privileges = either(*values_combinations)
    source_table_privileges = either(*values_combinations)

    user_attach_partition_from_with_privileges(
        destination_table_privileges=destination_table_privileges,
        source_table_privileges=source_table_privileges,
    )


@TestSketch(Scenario)
@Flags(TE)
def check_attach_partition_with_privileges(self):
    """Check `attach partition from` with different combination of privileges on a table."""
    values = {
        no_privileges,
        select_privileges,
        alter_privileges,
        alter_table_privileges,
        insert_privileges,
    }

    values_combinations = list(combinations_with_replacement(values, 2))
    table_privileges = either(*values_combinations)

    user_attach_partition_with_privileges(
        table_privileges=table_privileges,
    )


@TestSketch(Scenario)
@Flags(TE)
def check_attach_part_with_privileges(self):
    """Check `attach partition from` with different combination of privileges on a table."""
    values = {
        no_privileges,
        select_privileges,
        alter_privileges,
        alter_table_privileges,
        insert_privileges,
    }

    values_combinations = list(combinations_with_replacement(values, 2))
    table_privileges = either(*values_combinations)

    user_attach_part_with_privileges(
        table_privileges=table_privileges,
    )


@TestFeature
@Requirements(
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionOrPart_RBAC("1.0"),
    RQ_SRS_034_ClickHouse_Alter_Table_AttachPartitionFrom_RBAC,
)
@Name("rbac")
def feature(self, node="clickhouse1"):
    """Check that it is possible to use `attach partition` and `attach partition from`
       as a user with the given privileges.

    Privileges:
    * None
    * Select
    * Insert
    * Alter
    * Alter Table
    """
    self.context.node = self.context.cluster.node(node)

    Scenario(run=check_attach_partition_from_with_privileges)
    Scenario(run=check_attach_partition_with_privileges)
    Scenario(run=check_attach_part_with_privileges)
