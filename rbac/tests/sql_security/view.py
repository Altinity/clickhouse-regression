from itertools import combinations

from testflows.core import *
from testflows.combinatorics import product

import rbac.helper.errors as errors
from rbac.requirements import *
from rbac.helper.common import *
from rbac.tests.sql_security.common import *
from helpers.common import getuid, get_settings_value


@TestStep(Then)
def check_query(
    self,
    view_definer_source_table_privilege,
    view_user_privilege,
    definer_user,
    user_name,
    view_name,
    node=None,
):
    """Check select from (insert into) view with given privileges."""
    if node is None:
        node = self.context.node

    query = f"SELECT * FROM {view_name}"

    if (
        "SELECT" in view_user_privilege
        and "SELECT" in view_definer_source_table_privilege
    ):
        node.query(query, settings=[("user", user_name)])
    else:
        if "SELECT" not in view_user_privilege:
            exitcode, message = errors.not_enough_privileges(name=f"{user_name}")
        else:
            exitcode, message = errors.not_enough_privileges(name=f"{definer_user}")
        node.query(
            query,
            settings=[("user", user_name)],
            exitcode=exitcode,
            message=message,
        )


@TestScenario
def check_view_with_definer(
    self,
    view_definer_source_table_privilege,
    view_user_privilege,
    grant_privilege,
):
    """Check that I can perform `create` and `insert` operations as a
    user with privileges limited to a view. The view must have been created
    with a definer who has sufficient privileges for these operations."""

    node = self.context.node

    with Given("I create user"):
        user_name_definer = "definer_user_" + getuid()
        create_user(node=node, user_name=user_name_definer)

    with And("I create table and insert data"):
        table_name = "table_one_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=table_name)
        insert_data_from_numbers(node=node, table_name=table_name)

    with And("I create view and populate it"):
        view_name = "view_" + getuid()
        create_view(
            node=node,
            view_name=view_name,
            select_table_name=table_name,
            definer=user_name_definer,
            sql_security="DEFINER",
        )

    with And("I grant privileges to source table to user either directly or via role"):
        grant_privilege(
            node=node,
            privileges=view_definer_source_table_privilege,
            object=table_name,
            user=user_name_definer,
        )

    with When("I create second user"):
        user_name_two = "user_two_" + getuid()
        create_user(node=node, user_name=user_name_two)

    with And("I grant privilege on view to second user either directly or via role"):
        grant_privilege(
            node=node,
            privileges=view_user_privilege,
            object=view_name,
            user=user_name_two,
        )

    with Then("I try to select from view with second user"):
        check_query(
            view_definer_source_table_privilege=view_definer_source_table_privilege,
            view_user_privilege=view_user_privilege,
            definer_user=user_name_definer,
            user_name=user_name_two,
            view_name=view_name,
        )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_Definer_Select("1.0"),
)
@Flags(TE)
def view_with_definer(self):
    """Check that user can only select from view if definer
    has enough privileges: definer should have SELECT on source table,
    user should have SELECT on view.
    """
    privileges = [
        "NONE",
        "SELECT",
        "INSERT",
        "ALTER",
        "CREATE",
    ]
    grant_privileges = [
        grant_privileges_directly,
        grant_privileges_via_role,
    ]

    view_definer_source_table_privileges_combinations = list(
        combinations(privileges, 2)
    ) + [["NONE"]]
    view_user_privileges_combinations = (list(combinations(privileges, 2))) + [["NONE"]]

    with Pool(10) as executor:
        for (
            view_definer_source_table_privilege,
            view_user_privilege,
            grant_privilege,
        ) in product(
            view_definer_source_table_privileges_combinations,
            view_user_privileges_combinations,
            grant_privileges,
        ):
            Scenario(
                name=f"{view_definer_source_table_privilege},{view_user_privilege}",
                test=check_view_with_definer,
                parallel=True,
                executor=executor,
            )(
                view_definer_source_table_privilege=view_definer_source_table_privilege,
                view_user_privilege=view_user_privilege,
                grant_privilege=grant_privilege,
            )
        join()


@TestScenario
def check_view_with_invoker(
    self,
    view_user_source_table_privilege,
    view_user_privilege,
    grant_privilege,
):
    """Check that user can only select from view or insert into view
    if he has enough privileges."""

    node = self.context.node

    with Given("I create table and insert data"):
        table_name = "table_one_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=table_name)
        insert_data_from_numbers(node=node, table_name=table_name)

    with And("I create view"):
        view_name = "view_" + getuid()
        create_view(
            node=node,
            view_name=view_name,
            select_table_name=table_name,
            sql_security="INVOKER",
        )

    with And("I create user"):
        user_name = "user_" + getuid()
        create_user(node=node, user_name=user_name)

    with And("I grant privileges to source table to user either directly or via role"):
        grant_privilege(
            node=node,
            privileges=view_user_source_table_privilege,
            object=table_name,
            user=user_name,
        )
        grant_privilege(
            node=node,
            privileges=view_user_privilege,
            object=view_name,
            user=user_name,
            grant_privilege=grant_privilege,
        )

    with Then("I try to select from view with second user"):
        exitcode, message = errors.not_enough_privileges(name=f"{user_name}")
        if (
            "SELECT" in view_user_privilege
            and "SELECT" in view_user_source_table_privilege
        ):
            exitcode, message = None, None

        node.query(
            f"SELECT * FROM {view_name}",
            settings=[("user", user_name)],
            exitcode=exitcode,
            message=message,
        )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_Invoker_Select("1.0"),
)
@Flags(TE)
def view_with_invoker(self):
    """Check that user can only select from view with
    `INVOKER` SQL SECURITY if user has enough privileges:
    `SELECT` on view and `SELECT` on source table.
    """
    privileges = [
        "NONE",
        "SELECT",
        "INSERT",
        "ALTER",
        "CREATE",
    ]
    grant_privileges = [
        grant_privileges_directly,
        grant_privileges_via_role,
    ]

    view_user_source_table_privileges_combinations = list(
        combinations(privileges, 2)
    ) + [["NONE"]]
    view_user_privileges_combinations = (list(combinations(privileges, 2))) + [["NONE"]]

    with Pool(10) as executor:
        for (
            view_user_source_table_privilege,
            view_user_privilege,
            grant_privilege,
        ) in product(
            view_user_source_table_privileges_combinations,
            view_user_privileges_combinations,
            grant_privileges,
        ):
            Scenario(
                name=f"{view_user_source_table_privilege}, {view_user_privilege}",
                test=check_view_with_definer,
                parallel=True,
                executor=executor,
            )(
                view_definer_source_table_privilege=view_user_source_table_privilege,
                view_user_privilege=view_user_privilege,
                grant_privilege=grant_privilege,
            )
        join()


@TestScenario
def definer_with_less_privileges(self):
    """Check that user can not select from view
    if definer does not have enough privileges."""

    node = self.context.node
    view_definer_source_table_privilege = "INSERT"

    with Given("I create user"):
        user_name_definer = "definer_user_" + getuid()
        create_user(node=node, user_name=user_name_definer)

    with And("I create table and insert data"):
        table_name = "table_one_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=table_name)
        insert_data_from_numbers(node=node, table_name=table_name)

    with And("I create view"):
        view_name = "view_" + getuid()
        create_view(
            node=node,
            view_name=view_name,
            select_table_name=table_name,
            definer=user_name_definer,
            sql_security="DEFINER",
        )

    with And("I grant privileges to user"):
        grant_privilege(
            node=node,
            privilege=view_definer_source_table_privilege,
            object=table_name,
            user=user_name_definer,
        )

    with Then("I try to select from view"):
        exitcode, message = errors.not_enough_privileges(name=f"{user_name_definer}")
        node.query(f"SELECT * FROM {view_name}", exitcode=exitcode, message=message)


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_Default("1.0"),
)
def check_default_values(self):
    """Check that default SQL SECURITY value is INVOKER."""
    node = self.context.node

    with Given("I check default value for SQL SECURITY in system.settings"):
        assert (
            get_settings_value(
                node=node, setting_name="default_normal_view_sql_security"
            )
            == "INVOKER"
        )

    with And("I create table and insert data"):
        table_name = "table_one_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=table_name)
        insert_data_from_numbers(node=node, table_name=table_name)

    with And("I create view"):
        view_name = "view_" + getuid()
        create_view(node=node, view_name=view_name, select_table_name=table_name)

    with Then("I check how the view was created"):
        node.query(f"SHOW CREATE VIEW {view_name}")

    with And("I create user and grant privileges to user"):
        user_name = "user_" + getuid()
        create_user(node=node, user_name=user_name)
        grant_privilege(node=node, privilege="SELECT", object=view_name, user=user_name)

    with And("I try to select from view with user"):
        exitcode, message = errors.not_enough_privileges(name=f"{user_name}")
        node.query(
            f"SELECT * FROM {view_name}",
            settings=[("user", user_name)],
            exitcode=exitcode,
            message=message,
        )

    with And("I add `SELECT` privilege to view source table"):
        grant_privilege(
            node=node, privilege="SELECT", object=table_name, user=user_name
        )

    with And("I should be able to select from view"):
        node.query(f"SELECT * FROM {view_name}", settings=[("user", user_name)])


@TestFeature
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_CreateView("1.0"),
)
@Name("view with definer")
def feature(self, node="clickhouse1"):
    """Check usage views that were created with definers."""
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node_2, self.context.node_3]

    Scenario(run=view_with_definer)
    Scenario(run=definer_with_less_privileges)
    Scenario(run=check_default_values)
    Scenario(run=view_with_invoker)
