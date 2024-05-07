from itertools import combinations

from testflows.core import *
from testflows.combinatorics import product

import rbac.helper.errors as errors
from rbac.requirements import *
from rbac.helper.common import *
from rbac.tests.sql_security.common import *
from helpers.common import getuid


@TestStep
def check_select_from_view(
    self,
    view_definer_source_table_privilege,
    view_definer_target_table_privilege,
    view_user_privilege,
    user_name_definer,
    user_name_two,
    view_name,
    node,
):
    """Check select from view with given privileges."""
    if (
        "SELECT" in view_user_privilege
        and "SELECT" in view_definer_source_table_privilege
        and "SELECT" in view_definer_target_table_privilege
    ):
        node.query(f"SELECT * FROM {view_name}", settings=[("user", user_name_two)])
    else:
        if "SELECT" not in view_user_privilege:
            exitcode, message = errors.not_enough_privileges(name=f"{user_name_two}")
            node.query(
                f"SELECT * FROM {view_name}",
                settings=[("user", user_name_two)],
                exitcode=exitcode,
                message=message,
            )
        else:
            exitcode, message = errors.not_enough_privileges(
                name=f"{user_name_definer}"
            )
            node.query(
                f"SELECT * FROM {view_name}",
                settings=[("user", user_name_two)],
                exitcode=exitcode,
                message=message,
            )


@TestStep
def check_insert_into_view(
    self,
    view_definer_target_table_privilege,
    view_user_privilege,
    user_name_definer,
    user_name_two,
    view_name,
    node,
):
    """Check insert into view with given privileges."""
    if (
        "INSERT" in view_user_privilege
        and "INSERT" in view_definer_target_table_privilege
    ):
        node.query(
            f"INSERT INTO {view_name} VALUES (1)", settings=[("user", user_name_two)]
        )
    else:
        if "INSERT" not in view_user_privilege:
            exitcode, message = errors.not_enough_privileges(name=f"{user_name_two}")
            node.query(
                f"INSERT INTO {view_name} VALUES (1)",
                settings=[("user", user_name_two)],
                exitcode=exitcode,
                message=message,
            )
        else:
            exitcode, message = errors.not_enough_privileges(
                name=f"{user_name_definer}"
            )
            node.query(
                f"INSERT INTO {view_name} VALUES (1)",
                settings=[("user", user_name_two)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def check_materialized_view_with_definer(
    self,
    view_definer_source_table_privilege,
    view_definer_target_table_privilege,
    view_user_privilege,
):
    """Check materialized view with definers."""
    node = self.context.node
    with Given("I create user"):
        user_name_definer = "definer_user_" + getuid()
        create_user(node=node, user_name=user_name_definer)

    with And("I create table"):
        table_name = "table_one_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=table_name)

    with And("I insert data in table"):
        insert_data_from_numbers(node=node, table_name=table_name)

    with And("I create mv table"):
        mv_table_name = "mv_table_one_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=mv_table_name)

    with And("I create materialized view and populate it"):
        view_name = "view_" + getuid()
        create_materialized_view(
            node=node,
            view_name=view_name,
            mv_table_name=mv_table_name,
            table_name=table_name,
            definer=user_name_definer,
            sql_security="DEFINER",
        )
        populate_mv_table(node=node, mv_table_name=mv_table_name, table_name=table_name)

    with And("I grant privileges to user"):
        for privilege in view_definer_source_table_privilege:
            grant_privilege(
                node=node,
                privilege=privilege,
                object=table_name,
                user=user_name_definer,
            )
        for privilege in view_definer_target_table_privilege:
            grant_privilege(
                node=node,
                privilege=privilege,
                object=mv_table_name,
                user=user_name_definer,
            )

    with When("I create second user"):
        user_name_two = "user_two_" + getuid()
        create_user(node=node, user_name=user_name_two)

    with And("I grant privilege on view to second user"):
        for privilege in view_user_privilege:
            grant_privilege(
                node=node, privilege=privilege, object=view_name, user=user_name_two
            )

    with Then("I try to select from materialized view with second user"):
        check_select_from_view(
            node=node,
            view_user_privilege=view_user_privilege,
            view_definer_source_table_privilege=view_definer_source_table_privilege,
            view_definer_target_table_privilege=view_definer_target_table_privilege,
            user_name_definer=user_name_definer,
            user_name_two=user_name_two,
            view_name=view_name,
        )

    with And("I try to insert into materialized view with second user"):
        check_insert_into_view(
            node=node,
            view_user_privilege=view_user_privilege,
            view_definer_target_table_privilege=view_definer_target_table_privilege,
            user_name_definer=user_name_definer,
            user_name_two=user_name_two,
            view_name=view_name,
        )


@TestScenario
@Flags(TE)
@Name("definers")
def definers(self):
    """Definers grants: SELECT, INSERT, ALTER, CREATE, DROP, TRUNCATE, OPTIMIZE, ACCESS MANAGEMENT."""
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node_2, self.context.node_3]

    view_definer_source_table_privileges = [
        "NONE",
        "SELECT",
        "INSERT",
        "ALTER",
        "CREATE",
    ]
    view_definer_target_table_privileges = [
        "NONE",
        "SELECT",
        "INSERT",
        "ALTER",
        "CREATE",
    ]
    view_user_privileges = [
        "NONE",
        "SELECT",
        "INSERT",
        "ALTER",
        "CREATE",
    ]

    view_definer_source_table_privileges_combinations = list(
        combinations(view_definer_source_table_privileges, 2)
    ) + [["NONE"]]
    view_definer_target_table_privileges_combinations = (
        list(combinations(view_definer_target_table_privileges, 2))
    ) + [["NONE"]]
    view_user_privileges_combinations = (
        list(combinations(view_user_privileges, 2))
    ) + [["NONE"]]

    with Pool(10) as executor:
        for (
            view_definer_source_table_privilege,
            view_definer_target_table_privilege,
            view_user_privilege,
        ) in product(
            view_definer_source_table_privileges_combinations,
            view_definer_target_table_privileges_combinations,
            view_user_privileges_combinations,
        ):
            Scenario(
                name=f"{view_definer_source_table_privilege}, {view_definer_target_table_privilege}, {view_user_privilege}",
                test=check_materialized_view_with_definer,
                parallel=True,
                executor=executor,
            )(
                view_definer_source_table_privilege=view_definer_source_table_privilege,
                view_definer_target_table_privilege=view_definer_target_table_privilege,
                view_user_privilege=view_user_privilege,
            )
        join()
