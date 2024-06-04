from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product

from itertools import combinations

from helpers.common import *
from rbac.requirements import *
from rbac.helper.common import *
from rbac.tests.sql_security.common import *


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_CreateMaterializedView("1.0"),
)
def check_create_mv(self):
    """Check that SQL SECURITY and DEFINER clauses are supported when
    creating materialized views.
    """
    with Given("I create source table for materialized view"):
        source_table_name = create_simple_MergeTree_table(rows=10, column_name="x")

    with And("I create materialized view using SQL SECURITY option"):
        mv_name = create_materialized_view(
            source_table_name=source_table_name,
            engine="MergeTree",
            order_by="x",
            sql_security="DEFINER",
            definer="CURRENT_USER",
            populate=True,
        )

    with Then("I check that I can select from materialized view"):
        output = self.context.node.query(f"SELECT sum(x) FROM {mv_name}").output
        assert output == "45", error()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_DefaultValues("1.0"),
)
def check_default_values(self):
    """Check that default values of SQL SECURITY settings are correct."""
    assert (
        get_settings_value(
            node=self.context.node,
            setting_name="default_materialized_view_sql_security",
        )
        == "DEFINER"
    ), error()
    assert (
        get_settings_value(node=self.context.node, setting_name="default_view_definer")
        == "CURRENT_USER"
    ), error()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_OnCluster("1.0"),
)
def create_mv_on_cluster(self):
    """Check that SQL security and definer clauses are supported when
    creating materialized views on a cluster.
    """
    with Given("I create source table for materialized view"):
        source_table_name = create_simple_MergeTree_table(
            rows=10, column_name="x", cluster="replicated_cluster"
        )

    with And("I create materialized view using SQL SECURITY option"):
        mv_name = create_materialized_view(
            source_table_name=source_table_name,
            engine="ReplicatedMergeTree",
            order_by="x",
            cluster="replicated_cluster",
            sql_security="DEFINER",
            definer="CURRENT_USER",
            populate=True,
            node=self.context.node,
        )

    with Then("I check that I can select from materialized view"):
        for node in self.context.nodes:
            output = node.query(f"SELECT sum(x) FROM {mv_name}").output
            assert output == "45", error()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_DefinerNotSpecified("1.0"),
)
def definer_not_specified(
    self,
):
    """
    =======      | =======
    SQL security | Definer
    =======      | =======
    DEFINER      | not specified
    =======      | =======

    Check that definer is set to CURRENT_USER if definer was not specified and
    SQL security was set to DEFINER by changing default_view_definer setting to
    user without any privileges and checking that default user is used as definer.
    """
    node = self.context.node
    default_default_view_definer = get_settings_value(
        node=node, setting_name="default_view_definer"
    )
    try:
        with Given("I create view's source and target tables"):
            source_table_name = create_simple_MergeTree_table(column_name="x")
            target_table_name = create_simple_MergeTree_table(column_name="x")
            insert_data_from_numbers(table_name=target_table_name)

        with And("I create user that will be set as default view definer"):
            new_default_user_name = "new_default_user_" + getuid()
            create_user(user_name=new_default_user_name)

        with And(
            "I change default_view_definer setting to new_default_user_name for default user"
        ):
            entries = {
                "profiles": {
                    "default": {
                        "default_view_definer": f"{new_default_user_name}",
                    }
                }
            }
            change_core_settings(modify=True, restart=True, entries=entries)

        with And("I check that setting was changed"):
            assert (
                get_settings_value(node=node, setting_name="default_view_definer")
                == f"{new_default_user_name}"
            )

        with And("I create materialized view only specifying SQL SECURITY"):
            mv_name = create_materialized_view(
                source_table_name=source_table_name,
                target_table_name=target_table_name,
                sql_security="DEFINER",
            )

        with When("I create user and grant select privilege for mv"):
            user_name = "user_" + getuid()
            create_user(user_name=user_name)
            grant_privileges_directly(
                user=user_name,
                object=mv_name,
                privileges=["SELECT"],
            )

        with Then("I check if user can select from mv"):
            output = node.query(
                f"SELECT sum(x) FROM {mv_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()

        with Then(
            "I check that DEFINER = default(CURRENT_USER) was used while creating mv"
        ):
            output = node.query(f"SHOW CREATE TABLE {mv_name}").output
            assert "DEFINER = default" in output, error()

    finally:
        with Finally("I restore default_view_definer setting"):
            entries = {
                "profiles": {
                    "default": {
                        "default_view_definer": f"{default_default_view_definer}",
                    }
                }
            }
            change_core_settings(modify=True, restart=True, entries=entries)

        with And("I check that setting was restored"):
            assert (
                get_settings_value(node=node, setting_name="default_view_definer")
                == f"{default_default_view_definer}"
            )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_SqlSecurityNotSpecified("1.0"),
)
def sql_security_not_specified(
    self,
):
    """
    =======       | =======
    SQL security  | Definer
    =======       | =======
    not specified | alice
    =======       | =======

    Check that SQL security is set to DEFINER if SQL security was not specified and
    definer was specified by changing default_materialized_view_sql_security setting to
    INVOKER and checking that SQL security DEFINER was used.
    """
    node = self.context.node
    default_default_mv_sql_security = get_settings_value(
        node=node, setting_name="default_materialized_view_sql_security"
    )
    try:
        with Given("I create view's source and target tables"):
            source_table_name = create_simple_MergeTree_table(column_name="x")
            target_table_name = create_simple_MergeTree_table(column_name="x")
            insert_data_from_numbers(table_name=target_table_name)

        with And(
            "I change default_materialized_view_sql_security setting to INVOKER for default user"
        ):
            entries = {
                "profiles": {
                    "default": {
                        "default_materialized_view_sql_security": "INVOKER",
                    }
                }
            }
            change_core_settings(modify=True, restart=True, entries=entries)

        with And("I check that setting was changed"):
            assert (
                get_settings_value(
                    node=node, setting_name="default_materialized_view_sql_security"
                )
                == "INVOKER"
            )

        with And("I create definer user and grant privileges"):
            definer_user = "alice_" + getuid()
            create_user(user_name=definer_user)
            grant_privileges_directly(
                privileges=["SELECT"], user=definer_user, object=source_table_name
            )
            grant_privileges_directly(
                privileges=["SELECT"], user=definer_user, object=target_table_name
            )

        with And("I create materialized view only specifying definer"):
            mv_name = create_materialized_view(
                source_table_name=source_table_name,
                target_table_name=target_table_name,
                definer=definer_user,
            )

        with When("I create user and grant select privilege for mv"):
            user_name = "user_" + getuid()
            create_user(user_name=user_name)
            grant_privileges_directly(
                user=user_name,
                object=mv_name,
                privileges=["SELECT"],
            )

        with Then("I check if user can select from mv"):
            output = node.query(
                f"SELECT sum(x) FROM {mv_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()

        with Then("I check that SQL SECURITY DEFINER was used while creating mv"):
            output = node.query(f"SHOW CREATE TABLE {mv_name}").output
            assert "SQL SECURITY DEFINER" in output, error()

    finally:
        with Finally("I restore default_materialized_view_sql_security setting"):
            entries = {
                "profiles": {
                    "default": {
                        "default_materialized_view_sql_security": f"{default_default_mv_sql_security}",
                    }
                }
            }
            change_core_settings(modify=True, restart=True, entries=entries)

        with And("I check that setting was restored"):
            assert (
                get_settings_value(
                    node=node, setting_name="default_materialized_view_sql_security"
                )
                == f"{default_default_mv_sql_security}"
            )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_Select_SqlSecurityDefiner_Definer(
        "1.0"
    ),
)
def check_select_sql_security_definer_definer(
    self,
    user_view_privilege,
    user_source_table_privilege,
    user_target_table_privilege,
    definer_source_table_privilege,
    definer_target_table_privilege,
    grant_privilege,
):
    """
    =======      | =======
    SQL security | Definer
    =======      | =======
    DEFINER      | alice
    =======      | =======

    Check that user can select from materialized view with given SQL SECURITY
    options when user has SELECT privilege for mv and definer user has SELECT
    privilege for mv's source and target tables.
    """
    node = self.context.node

    with Given("I create view's source and target tables"):
        source_table_name = create_simple_MergeTree_table(column_name="x")
        target_table_name = create_simple_MergeTree_table(column_name="x")
        insert_data_from_numbers(table_name=target_table_name)

    with And(
        "I create definer user and grant him privileges to mv's source and target tables"
    ):
        definer_user = "alice_" + getuid()
        create_user(user_name=definer_user)
        grant_privilege(
            user=definer_user,
            object=source_table_name,
            privileges=definer_source_table_privilege,
        )
        grant_privilege(
            user=definer_user,
            object=target_table_name,
            privileges=definer_target_table_privilege,
        )

    with And("I create materialized view specifying SQL security and definer"):
        mv_name = create_materialized_view(
            source_table_name=source_table_name,
            target_table_name=target_table_name,
            sql_security="DEFINER",
            definer=definer_user,
        )

    with When(
        "I create user and grant privileges to mv and mv's source and target tables"
    ):
        user_name = "user_" + getuid()
        create_user(user_name=user_name)
        grant_privilege(
            user=user_name,
            object=mv_name,
            privileges=user_view_privilege,
        )
        grant_privilege(
            user=user_name,
            object=source_table_name,
            privileges=user_source_table_privilege,
        )
        grant_privilege(
            user=user_name,
            object=target_table_name,
            privileges=user_target_table_privilege,
        )

    with Then(
        """I check that user can select from mv if he has SELECT privilege for mv and
            definer user has SELECT for mv's source and target tables"""
    ):
        if (
            "SELECT" in user_view_privilege
            and "SELECT" in definer_source_table_privilege
            and "SELECT" in definer_target_table_privilege
        ):
            output = node.query(
                f"SELECT sum(x) FROM {mv_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()
        else:
            if "SELECT" not in user_view_privilege:
                exitcode, message = errors.not_enough_privileges(name=user_name)
            else:
                exitcode, message = errors.not_enough_privileges(name=definer_user)
            node.query(
                f"SELECT sum(x) FROM {mv_name}",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def select_sql_security_definer_definer(self):
    """Run test with different privileges for definer and user."""
    grant_privileges = [grant_privileges_directly, grant_privileges_via_role]
    privileges = ["SELECT", "INSERT", "ALTER", "CREATE", "NONE"]

    if not self.context.stress:
        privileges = ["SELECT", "INSERT", "NONE"]
        grant_privileges = [grant_privileges_directly]

    privileges_combinations = list(combinations(privileges, 2)) + [["NONE"]]

    with Pool(5) as executor:
        for (
            user_view_privilege,
            user_source_table_privilege,
            user_target_table_privilege,
            definer_source_table_privilege,
            definer_target_table_privilege,
            grant_privilege,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
        ):
            test_name = f"{user_view_privilege}_{user_source_table_privilege}_{user_target_table_privilege}_{definer_source_table_privilege}_{definer_target_table_privilege}_{grant_privilege.__name__}"
            test_name = (
                test_name.replace("[", "_")
                .replace("]", "_")
                .replace(")", "/")
                .replace("(", "/")
            )
            Scenario(
                test_name,
                test=check_select_sql_security_definer_definer,
                parallel=True,
                executor=executor,
            )(
                user_view_privilege=user_view_privilege,
                user_source_table_privilege=user_source_table_privilege,
                user_target_table_privilege=user_target_table_privilege,
                definer_source_table_privilege=definer_source_table_privilege,
                definer_target_table_privilege=definer_target_table_privilege,
                grant_privilege=grant_privilege,
            )
        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_Select_SqlSecurityDefiner_DefinerNotSpecified(
        "1.0"
    ),
)
def check_select_sql_security_definer_definer_not_specified(
    self,
    user_view_privilege,
    user_source_table_privilege,
    user_target_table_privilege,
    grant_privilege,
):
    """
    =======      | =======
    SQL security | Definer
    =======      | =======
    DEFINER      | not specified
    =======      | =======

    Check that user can select from materialized view with given SQL SECURITY
    options when user has SELECT privilege for mv and definer user has SELECT
    privilege for mv's source and target tables. If definer is not specified
    then it should be set to CURRENT_USER.
    """
    node = self.context.node

    with Given("I create view's source and target tables"):
        source_table_name = create_simple_MergeTree_table(column_name="x")
        target_table_name = create_simple_MergeTree_table(column_name="x")
        insert_data_from_numbers(table_name=target_table_name)

    with And("I create materialized view only specifying SQL SECURITY"):
        mv_name = create_materialized_view(
            source_table_name=source_table_name,
            target_table_name=target_table_name,
            sql_security="DEFINER",
        )

    with When(
        "I create user and grant him privileges to mv and mv's source and target tables"
    ):
        user_name = "user_" + getuid()
        create_user(user_name=user_name)
        grant_privilege(
            user=user_name,
            object=mv_name,
            privileges=user_view_privilege,
        )
        grant_privilege(
            user=user_name,
            object=source_table_name,
            privileges=user_source_table_privilege,
        )
        grant_privilege(
            user=user_name,
            object=target_table_name,
            privileges=user_target_table_privilege,
        )

    with Then("I check if user can select from mv if he has SELECT privilege for mv"):
        if "SELECT" in user_view_privilege:
            output = node.query(
                f"SELECT sum(x) FROM {mv_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()
        else:
            exitcode, message = errors.not_enough_privileges(name=user_name)
            node.query(
                f"SELECT sum(x) FROM {mv_name}",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def select_sql_security_definer_definer_not_specified(self):
    """Run check_select_sql_security_definer_definer_not_specified
    with different privileges for user.
    """
    grant_privileges = [grant_privileges_directly, grant_privileges_via_role]
    privileges = ["SELECT", "INSERT", "ALTER", "CREATE", "NONE"]

    if not self.context.stress:
        privileges = ["SELECT", "INSERT", "NONE"]
        grant_privileges = [grant_privileges_directly]

    privileges_combinations = list(combinations(privileges, 2)) + [["NONE"]]

    with Pool(5) as executor:
        for (
            user_view_privilege,
            user_source_table_privilege,
            user_target_table_privilege,
            grant_privilege,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
        ):
            test_name = f"{user_view_privilege}_{user_source_table_privilege}_{user_target_table_privilege}_{grant_privilege.__name__}"
            test_name = (
                test_name.replace("[", "_")
                .replace("]", "_")
                .replace(")", "/")
                .replace("(", "/")
            )
            Scenario(
                test_name,
                test=check_select_sql_security_definer_definer_not_specified,
                parallel=True,
                executor=executor,
            )(
                user_view_privilege=user_view_privilege,
                user_source_table_privilege=user_source_table_privilege,
                user_target_table_privilege=user_target_table_privilege,
                grant_privilege=grant_privilege,
            )
        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_Select_SqlSecurityInvoker_Definer(
        "1.0"
    ),
)
def check_select_sql_security_invoker_definer(self):
    """
    =======      | =======
    SQL security | Definer
    =======      | =======
    INVOKER      | alice
    =======      | =======

    Check that SQL security INVOKER is not allowed for materialized views.
    """
    with Given("I create view's source and target tables"):
        source_table_name = create_simple_MergeTree_table(column_name="x")
        target_table_name = create_simple_MergeTree_table(column_name="x")

    with And("I create definer user and grant privileges"):
        definer_user = "alice_" + getuid()
        create_user(user_name=definer_user)

    with And("I create materialized view with INVOKER SQL SECURITY"):
        exitcode, message = errors.invoker_not_allowed()
        mv_name = create_materialized_view(
            source_table_name=source_table_name,
            target_table_name=target_table_name,
            sql_security="INVOKER",
            definer=definer_user,
            exitcode=exitcode,
            message=message,
        )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_Select_SqlSecurityInvoker_DefinerNotSpecified(
        "1.0"
    ),
)
def check_select_sql_security_invoker_definer_not_specified(self):
    """
    =======      | =======
    SQL security | Definer
    =======      | =======
    INVOKER      | not specified
    =======      | =======

    Check that SQL security INVOKER is not allowed for materialized views.
    """
    with Given("I create view's source and target tables"):
        source_table_name = create_simple_MergeTree_table(column_name="x")
        target_table_name = create_simple_MergeTree_table(column_name="x")

    with And("I create materialized view with INVOKER SQL SECURITY"):
        exitcode, message = errors.invoker_not_allowed()
        mv_name = create_materialized_view(
            source_table_name=source_table_name,
            target_table_name=target_table_name,
            sql_security="INVOKER",
            exitcode=exitcode,
            message=message,
        )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_Select_SqlSecurityNotSpecified_Definer(
        "1.0"
    ),
)
def check_select_sql_security_not_specified_definer(
    self,
    user_view_privilege,
    user_source_table_privilege,
    user_target_table_privilege,
    definer_source_table_privilege,
    definer_target_table_privilege,
    grant_privilege,
):
    """
    =======       | =======
    SQL security  | Definer
    =======       | =======
    not specified | alice
    =======       | =======

    Check that user can select from materialized view with given SQL SECURITY
    options when user has SELECT privilege for mv and definer user has SELECT
    privilege for mv's source and target tables. SQL security should be set to
    DEFINER by default.
    """
    node = self.context.node

    with Given("I create view's source and target tables"):
        source_table_name = create_simple_MergeTree_table(column_name="x")
        target_table_name = create_simple_MergeTree_table(column_name="x")
        insert_data_from_numbers(table_name=target_table_name)

    with And(
        "I create definer user and grant him privileges to mv's source and target tables"
    ):
        definer_user = "alice_" + getuid()
        create_user(user_name=definer_user)
        grant_privilege(
            user=definer_user,
            object=source_table_name,
            privileges=definer_source_table_privilege,
        )
        grant_privilege(
            user=definer_user,
            object=target_table_name,
            privileges=definer_target_table_privilege,
        )

    with And("I create materialized view only specifying DEFINER"):
        mv_name = create_materialized_view(
            source_table_name=source_table_name,
            target_table_name=target_table_name,
            definer=definer_user,
        )

    with When(
        "I create user and grant him privileges to mv and mv's source and target tables"
    ):
        user_name = "user_" + getuid()
        create_user(user_name=user_name)
        grant_privilege(
            user=user_name,
            object=mv_name,
            privileges=user_view_privilege,
        )
        grant_privilege(
            user=user_name,
            object=source_table_name,
            privileges=user_source_table_privilege,
        )
        grant_privilege(
            user=user_name,
            object=target_table_name,
            privileges=user_target_table_privilege,
        )

    with Then(
        """I check that user can select from mv if he has SELECT privilege for mv and
            definer user has SELECT for mv's source and target tables"""
    ):
        if (
            "SELECT" in user_view_privilege
            and "SELECT" in definer_source_table_privilege
            and "SELECT" in definer_target_table_privilege
        ):
            output = node.query(
                f"SELECT sum(x) FROM {mv_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()
        else:
            if "SELECT" not in user_view_privilege:
                exitcode, message = errors.not_enough_privileges(name=user_name)
            else:
                exitcode, message = errors.not_enough_privileges(name=definer_user)
            node.query(
                f"SELECT sum(x) FROM {mv_name}",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def select_sql_security_not_specified_definer(self):
    """Run check_select_sql_security_not_specified_definer
    with different privileges for user.
    """
    grant_privileges = [grant_privileges_directly, grant_privileges_via_role]
    privileges = ["SELECT", "INSERT", "ALTER", "CREATE", "NONE"]

    if not self.context.stress:
        privileges = ["SELECT", "INSERT", "NONE"]
        grant_privileges = [grant_privileges_directly]

    privileges_combinations = list(combinations(privileges, 2)) + [["NONE"]]

    with Pool(5) as executor:
        for (
            user_view_privilege,
            user_source_table_privilege,
            user_target_table_privilege,
            definer_source_table_privilege,
            definer_target_table_privilege,
            grant_privilege,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
        ):
            test_name = f"{user_view_privilege}_{user_source_table_privilege}_{user_target_table_privilege}_{definer_source_table_privilege}_{definer_target_table_privilege}_{grant_privilege.__name__}"
            test_name = (
                test_name.replace("[", "_")
                .replace("]", "_")
                .replace(")", "/")
                .replace("(", "/")
            )
            Scenario(
                test_name,
                test=check_select_sql_security_not_specified_definer,
                parallel=True,
                executor=executor,
            )(
                user_view_privilege=user_view_privilege,
                user_source_table_privilege=user_source_table_privilege,
                user_target_table_privilege=user_target_table_privilege,
                definer_source_table_privilege=definer_source_table_privilege,
                definer_target_table_privilege=definer_target_table_privilege,
                grant_privilege=grant_privilege,
            )
        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_Select_SqlSecurityNotSpecified_DefinerNotSpecified(
        "1.0"
    ),
)
def select_sql_security_not_specified_definer_not_specified(self):
    """
    =======       | =======
    SQL security  | Definer
    =======       | =======
    not specified | not specified
    =======       | =======

    Check that user can select from materialized view with given SQL SECURITY
    options when user has SELECT privilege for mv and definer user has SELECT
    privilege for mv's source and target tables. SQL security is set to the value
    from `default_materialized_view_sql_security` setting and definer to the value
    from `default_view_definer` setting.
    """
    node = self.context.node
    default_default_view_definer = get_settings_value(
        node=node, setting_name="default_view_definer"
    )
    default_ignore_empty_sql_security_in_create_view_query = node.query(
        f"SELECT value FROM system.server_settings WHERE name = 'ignore_empty_sql_security_in_create_view_query' FORMAT TabSeparated"
    ).output

    try:
        with Given("I create view's source and target tables"):
            source_table_name = create_simple_MergeTree_table(column_name="x")
            target_table_name = create_simple_MergeTree_table(column_name="x")
            insert_data_from_numbers(table_name=target_table_name)

        with And(
            "I create definer user and grant him privileges to mv's source and target tables"
        ):
            definer_user = "alice_" + getuid()
            create_user(user_name=definer_user)
            grant_privileges_directly(
                user=definer_user,
                object=source_table_name,
                privileges=["SELECT"],
            )
            grant_privileges_directly(
                user=definer_user,
                object=target_table_name,
                privileges=["SELECT"],
            )

        with And(
            "I change ignore_empty_sql_security_in_create_view_query to 0 so defaults will be used"
        ):
            if default_ignore_empty_sql_security_in_create_view_query == "1":
                entries = {"ignore_empty_sql_security_in_create_view_query": "0"}
                change_core_settings(
                    modify=True,
                    restart=True,
                    entries=entries,
                    config_d_dir="/etc/clickhouse-server/config.d",
                    preprocessed_name="config.xml",
                )

        with And(
            f"I change default_view_definer setting to definer_user for default user"
        ):
            entries = {
                "profiles": {
                    "default": {
                        "default_view_definer": f"{definer_user}",
                    }
                }
            }
            change_core_settings(modify=True, restart=True, entries=entries)

        with And("I check that setting was changed"):
            assert (
                get_settings_value(node=node, setting_name="default_view_definer")
                == f"{definer_user}"
            )

        with And("I check that default SQL security is DEFINER"):
            assert (
                get_settings_value(
                    node=node, setting_name="default_materialized_view_sql_security"
                )
                == "DEFINER"
            )

        with And(
            "I create materialized view without specifying definer and sql security"
        ):
            mv_name = create_materialized_view(
                source_table_name=source_table_name,
                target_table_name=target_table_name,
            )

        with And("I check that values from settings were used while creating mv"):
            output = node.query(f"SHOW CREATE TABLE {mv_name}").output
            assert f"DEFINER = {definer_user} SQL SECURITY DEFINER" in output, error()

        with When("I create user and grant him SELECT privilege for mv"):
            user_name = "user_" + getuid()
            create_user(user_name=user_name)
            grant_privileges_directly(
                user=user_name,
                object=mv_name,
                privileges=["SELECT"],
            )

        with Then(
            """I check that user can select from mv if he has SELECT privilege for mv and
            definer user has SELECT for mv's source and target tables"""
        ):
            output = node.query(
                f"SELECT sum(x) FROM {mv_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()

    finally:
        with Finally("I restore default_view_definer setting"):
            entries = {
                "profiles": {
                    "default": {
                        "default_view_definer": f"{default_default_view_definer}",
                    }
                }
            }
            change_core_settings(modify=True, restart=True, entries=entries)

        with And("I restore ignore_empty_sql_security_in_create_view_query setting"):
            changed = node.query(
                f"""SELECT changed FROM system.server_settings 
                    WHERE name = 'ignore_empty_sql_security_in_create_view_query' 
                    FORMAT TabSeparated
                """
            ).output
            if changed:
                entries = {
                    "ignore_empty_sql_security_in_create_view_query": f"{default_ignore_empty_sql_security_in_create_view_query}"
                }
                change_core_settings(
                    modify=True,
                    restart=True,
                    entries=entries,
                    config_d_dir="/etc/clickhouse-server/config.d",
                    preprocessed_name="config.xml",
                )

        with And("I check that settings were restored"):
            assert (
                get_settings_value(node=node, setting_name="default_view_definer")
                == f"{default_default_view_definer}"
            )
            assert (
                node.query(
                    f"SELECT value FROM system.server_settings WHERE name = 'ignore_empty_sql_security_in_create_view_query' FORMAT TabSeparated"
                ).output
                == f"{default_ignore_empty_sql_security_in_create_view_query}"
            )


@TestFeature
@Name("materialized view SQL security")
def feature(self):
    """Check SQL security functionality for materialized views."""
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node_2, self.context.node_3]

    with Pool(5) as executor:
        Scenario(test=check_create_mv, parallel=True, executor=executor)()
        Scenario(test=create_mv_on_cluster, parallel=True, executor=executor)()
        Scenario(test=check_default_values, parallel=True, executor=executor)()
        Scenario(
            test=select_sql_security_definer_definer,
            parallel=True,
            executor=executor,
        )()
        Scenario(
            test=select_sql_security_definer_definer_not_specified,
            parallel=True,
            executor=executor,
        )()
        Scenario(
            test=check_select_sql_security_invoker_definer,
            parallel=True,
            executor=executor,
        )()
        Scenario(
            test=check_select_sql_security_invoker_definer_not_specified,
            parallel=True,
            executor=executor,
        )()
        Scenario(
            test=select_sql_security_not_specified_definer,
            parallel=True,
            executor=executor,
        )()
        join()

    Scenario(run=definer_not_specified)
    Scenario(run=sql_security_not_specified)
    Scenario(run=check_default_values)
    Scenario(run=select_sql_security_not_specified_definer_not_specified)
    Scenario(run=check_default_values)
