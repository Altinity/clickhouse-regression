from itertools import combinations

from testflows.core import *
from testflows.combinatorics import product

import rbac.helper.errors as errors
from rbac.requirements import *
from rbac.helper.common import *
from rbac.tests.sql_security.common import *
from helpers.common import getuid, get_settings_value


@TestStep(Then)
def check_select_from_mv(
    self,
    view_definer_source_table_privilege,
    view_definer_target_table_privilege,
    view_user_privilege,
    definer_user,
    user_name,
    view_name,
    node,
):
    """Check select from view with given privileges."""
    if (
        "SELECT" in view_user_privilege
        and "SELECT" in view_definer_source_table_privilege
        and "SELECT" in view_definer_target_table_privilege
    ):
        node.query(f"SELECT * FROM {view_name}", settings=[("user", user_name)])
    else:
        if "SELECT" not in view_user_privilege:
            exitcode, message = errors.not_enough_privileges(name=f"{user_name}")
        else:
            exitcode, message = errors.not_enough_privileges(name=f"{definer_user}")
        node.query(
            f"SELECT * FROM {view_name}",
            settings=[("user", user_name)],
            exitcode=exitcode,
            message=message,
        )


@TestStep(Then)
def check_insert_into_mv(
    self,
    view_definer_target_table_privilege,
    view_user_privilege,
    definer_user,
    user_name,
    view_name,
    node,
):
    """Check insert into view with given privileges."""
    if (
        "INSERT" in view_user_privilege
        and "INSERT" in view_definer_target_table_privilege
    ):
        node.query(
            f"INSERT INTO {view_name} VALUES (1)", settings=[("user", user_name)]
        )
    else:
        if "INSERT" not in view_user_privilege:
            exitcode, message = errors.not_enough_privileges(name=f"{user_name}")
        else:
            exitcode, message = errors.not_enough_privileges(name=f"{definer_user}")
        node.query(
            f"INSERT INTO {view_name} VALUES (1)",
            settings=[("user", user_name)],
            exitcode=exitcode,
            message=message,
        )


@TestScenario
def check_materialized_view_with_definer(
    self,
    view_definer_source_table_privilege,
    view_definer_target_table_privilege,
    view_user_privilege,
    grant_privilege,
):
    """Check that I can perform `create` and `insert` operations as a
    user with privileges limited to a materialized view. The materialized
    view must have been created with a definer who has sufficient
    privileges for these operations."""

    node = self.context.node

    with Given("I create user"):
        user_name_definer = "definer_user_" + getuid()
        create_user(node=node, user_name=user_name_definer)

    with And("I create table and insert data"):
        table_name = "table_one_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=table_name)
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
            select_table_name=table_name,
            definer=user_name_definer,
            sql_security="DEFINER",
        )
        populate_mv_table(node=node, mv_table_name=mv_table_name, table_name=table_name)

    with And(
        "I grant privileges to source and target tables to user either directly or via role"
    ):
        grant_privilege(
            node=node,
            privileges=view_definer_source_table_privilege,
            object=table_name,
            user=user_name_definer,
        )
        grant_privilege(
            node=node,
            privileges=view_definer_target_table_privilege,
            object=mv_table_name,
            user=user_name_definer,
        )

    with When("I create second user"):
        user_name_two = "user_two_" + getuid()
        create_user(node=node, user_name=user_name_two)

    with And(
        "I grant privilege on materialized view to second user either directly or via role"
    ):
        grant_privilege(
            node=node,
            privileges=view_user_privilege,
            object=view_name,
            user=user_name_two,
        )

    with Then("I try to select from materialized view with second user"):
        check_select_from_mv(
            node=node,
            view_user_privilege=view_user_privilege,
            view_definer_source_table_privilege=view_definer_source_table_privilege,
            view_definer_target_table_privilege=view_definer_target_table_privilege,
            definer_user=user_name_definer,
            user_name=user_name_two,
            view_name=view_name,
        )

    with And("I try to insert into materialized view with second user"):
        check_insert_into_mv(
            node=node,
            view_user_privilege=view_user_privilege,
            view_definer_target_table_privilege=view_definer_target_table_privilege,
            definer_user=user_name_definer,
            user_name=user_name_two,
            view_name=view_name,
        )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_Definer_Select("1.0"),
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_Definer_Insert("1.0"),
)
@Flags(TE)
def materialized_view_with_definer(self):
    """Check that user can only select from materialized view or
    insert into materialized view if definer has enough privileges.
    For select: definer should have SELECT on source table and target table,
    user should have SELECT on materialized view.
    For insert: definer should have INSERT on target table,
    user should have INSERT on materialized view.
    """
    privileges = [
        "NONE",
        "SELECT",
        "INSERT",
        "ALTER",
        "CREATE",
    ]

    if not self.context.stress:
        privileges = ["NONE", "SELECT", "INSERT"]

    grant_privileges = [grant_privileges_directly, grant_privileges_via_role]

    view_definer_source_table_privileges_combinations = list(
        combinations(privileges, 2)
    ) + [["NONE"]]
    view_definer_target_table_privileges_combinations = (
        list(combinations(privileges, 2))
    ) + [["NONE"]]
    view_user_privileges_combinations = (list(combinations(privileges, 2))) + [["NONE"]]

    with Pool(10) as executor:
        for (
            view_definer_source_table_privilege,
            view_definer_target_table_privilege,
            view_user_privilege,
            grant_privilege,
        ) in product(
            view_definer_source_table_privileges_combinations,
            view_definer_target_table_privileges_combinations,
            view_user_privileges_combinations,
            grant_privileges,
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
                grant_privilege=grant_privilege,
            )
        join()


@TestScenario
def definer_with_less_privileges(self):
    """Check that user can not select from materialized view
    if definer does not have enough privileges."""

    node = self.context.node
    view_definer_source_table_privilege = "SELECT"
    view_definer_target_table_privilege = "INSERT"

    with Given("I create user"):
        user_name_definer = "definer_user_" + getuid()
        create_user(node=node, user_name=user_name_definer)

    with And("I create table and insert data"):
        table_name = "table_one_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=table_name)
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
            select_table_name=table_name,
            definer=user_name_definer,
            sql_security="DEFINER",
        )
        populate_mv_table(node=node, mv_table_name=mv_table_name, table_name=table_name)

    with And("I grant privileges to user"):
        grant_privilege(
            node=node,
            privilege=view_definer_source_table_privilege,
            object=table_name,
            user=user_name_definer,
        )
        grant_privilege(
            node=node,
            privilege=view_definer_target_table_privilege,
            object=mv_table_name,
            user=user_name_definer,
        )

    with Then("I try to select from materialized view"):
        exitcode, message = errors.not_enough_privileges(name=f"{user_name_definer}")
        node.query(f"SELECT * FROM {view_name}", exitcode=exitcode, message=message)


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_Default("1.0"),
    RQ_SRS_006_RBAC_SQLSecurity_Default_Definer("1.0"),
)
def check_default_values(self):
    """Check that default sql security is DEFINER and default definer is CURRENT_USER."""
    node = self.context.node

    with Given("I create table and insert data"):
        table_name = create_simple_MergeTree_table(node=node)
        insert_data_from_numbers(node=node, table_name=table_name)

    with And("I create mv table"):
        mv_table_name = "mv_table_one_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=mv_table_name)

    with And("I check default settings"):
        assert (
            get_settings_value(node=node, setting_name="default_view_definer") == "CURRENT_USER"
        )
        assert (
            get_settings_value(node=node, setting_name="default_materialized_view_sql_security")
            == "DEFINER"
        )

    with And("I create materialized view with default user"):
        view_name = "view_" + getuid()
        create_materialized_view(
            node=node,
            view_name=view_name,
            mv_table_name=mv_table_name,
            select_table_name=table_name,
            # definer="default",
            # sql_security="DEFINER",
        )
        node.query(f"SHOW CREATE TABLE {view_name}")

    with And("I create user and grant SELECT privilege on materialized view"):
        select_user_name = create_user(node=node)
        grant_privilege(
            node=node, privilege="SELECT", object=view_name, user=select_user_name
        )

    with And("I try to select from materialized view with second user"):
        node.query(f"SELECT * FROM {view_name}", settings=[("user", select_user_name)])


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_Default("1.0"),
)
def check_change_default_values(self):
    """Check that I can change default SQL SECURITY settings for materialized views."""
    node = self.context.node

    with Given("I create user"):
        user_name_one = "user_one_" + getuid()
        create_user(node=node, user_name=user_name_one)

    with Given("I create table and insert data"):
        table_name = create_simple_MergeTree_table(node=node)
        insert_data_from_numbers(node=node, table_name=table_name)

    with And("I create mv table"):
        mv_table_name = "mv_table_one_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=mv_table_name)

    with And("I change user settings for default user"):
        entries = {
            "profiles": {
                "default": {
                    "default_materialized_view_sql_security": "INVOKER",
                    "default_view_definer": f"{user_name_one}",
                }
            }
        }
        change_core_settings(modify=True, restart=True, entries=entries)

    with And("I check that settings were changed"):
        assert (
            get_settings_value(node=node, settings_name="default_materialized_view_sql_security")
            == "INVOKER"
        )
        assert (
            get_settings_value(node=node, settings_name="default_view_definer")
            == f"{user_name_one}"
        )

    with And("I create materialized view with default values"):
        view_name = "view_" + getuid()
        create_materialized_view(
            node=node,
            view_name=view_name,
            mv_table_name=mv_table_name,
            select_table_name=table_name,
            # definer="default",
            sql_security="DEFINER",
        )
        node.query(f"SHOW CREATE TABLE {view_name}")

    with When("I create second user and grant SELECT privilege on materialized view"):
        user_name_two = "user_two_" + getuid()
        create_user(node=node, user_name=user_name_two)
        grant_privilege(
            node=node, privilege="SELECT", object=view_name, user=user_name_two
        )

    with Then("I try to select from materialized view with second user"):
        exitcode, message = errors.not_enough_privileges(name=f"{user_name_one}")
        node.query(
            f"SELECT * FROM {view_name}",
            settings=[("user", user_name_two)],
            exitcode=exitcode,
            message=message,
        )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_Invoker("1.0"),
)
def check_invoker_security(self):
    """Check that I can not create materialized view with `INVOKER` SQL security."""
    node = self.context.node

    with Given("I create table and insert data"):
        table_name = create_simple_MergeTree_table(node=node)
        insert_data_from_numbers(node=node, table_name=table_name)

    with And("I create mv table"):
        mv_table_name = "mv_table_one_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=mv_table_name)

    with When("I try to create materialized view with `INVOKER` SQL security"):
        create_materialized_view(
            node=node,
            view_name="view_" + getuid(),
            mv_table_name=mv_table_name,
            select_table_name=table_name,
            sql_security="INVOKER",
            exitcode=141,
            message="DB::Exception: SQL SECURITY INVOKER can't be specified for MATERIALIZED VIEW.",
        )


@TestFeature
@Name("materialized view with definer")
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_CreateMaterializedView("1.0"),
)
def feature(self, node="clickhouse1"):
    """Check usage of materialized views that were created with definers."""
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node_2, self.context.node_3]

    Scenario(run=materialized_view_with_definer)
    Scenario(run=definer_with_less_privileges)
    Scenario(run=check_default_values)
    Scenario(run=check_change_default_values)
    Scenario(run=check_invoker_security)
