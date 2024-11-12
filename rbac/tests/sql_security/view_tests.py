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
    RQ_SRS_006_RBAC_SQLSecurity_View_CreateView("1.0"),
)
def check_create_view(self):
    """Check that SQL SECURITY and DEFINER clauses are supported when
    creating normal views.
    """
    with Given("I create view's source table and insert 10 rows in it"):
        source_table_name = create_simple_MergeTree_table(rows=10, column_name="x")

    with And("I create normal view using SQL SECURITY option"):
        view_name = create_view(
            source_table_name=source_table_name,
            sql_security="DEFINER",
            definer="CURRENT_USER",
        )

    with Then("I check that I can select from normal view"):
        output = self.context.node.query(f"SELECT sum(x) FROM {view_name}").output
        assert output == "45", error()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_OnCluster("1.0"),
)
def check_create_view_on_cluster(self):
    """Check that SQL SECURITY and DEFINER clauses are supported when
    creating normal views on a cluster.
    """
    with Given("I create view's source table and insert 10 rows in it"):
        source_table_name = create_simple_MergeTree_table(
            rows=10, column_name="x", cluster="replicated_cluster"
        )

    with And("I create normal view using SQL SECURITY option on a cluster"):
        view_name = create_view(
            source_table_name=source_table_name,
            sql_security="DEFINER",
            definer="CURRENT_USER",
            cluster="replicated_cluster",
        )

    with Then("I check that I can select from normal view on all nodes"):
        for node in self.context.nodes:
            output = node.query(f"SELECT sum(x) FROM {view_name}").output
            assert output == "45", error()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_DefaultValues("1.0"),
)
def check_default_values(self):
    """Check that default values of SQL SECURITY settings are correct."""
    assert (
        get_settings_value(setting_name="default_normal_view_sql_security") == "INVOKER"
    ), error()
    assert (
        get_settings_value(setting_name="default_view_definer") == "CURRENT_USER"
    ), error()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_DefinerNotSpecified("1.0"),
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
    SQL security was set to DEFINER when creating normal view by changing default_view_definer
    setting to user without any privileges and checking that default user is used as definer.
    """
    node = self.context.node
    default_default_view_definer = get_settings_value(
        setting_name="default_view_definer"
    )
    try:
        with Given("I create view's source table and insert 10 rows in it"):
            source_table_name = create_simple_MergeTree_table(column_name="x")
            insert_data_from_numbers(table_name=source_table_name)

        with And("I create user that will be set as default_view_definer"):
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
            change_core_settings(restart=True, entries=entries)

        with And("I check that setting was changed"):
            assert (
                get_settings_value(setting_name="default_view_definer")
                == f"{new_default_user_name}"
            ), error()

        with And("I create normal view only specifying SQL SECURITY"):
            view_name = create_view(
                source_table_name=source_table_name,
                sql_security="DEFINER",
            )

        with When("I create user and grant select privilege for view"):
            user_name = "user_" + getuid()
            create_user(user_name=user_name)
            grant_privileges_directly(
                user=user_name,
                object=view_name,
                privileges=["SELECT"],
            )

        with Then("I check if user can select from view"):
            output = node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()

        with Then(
            "I check that DEFINER = default(CURRENT_USER) was used while creating view"
        ):
            output = node.query(
                f"SHOW CREATE TABLE {view_name} FORMAT TabSeparated"
            ).output
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
            change_core_settings(restart=True, entries=entries)

        with And("I check that setting was restored"):
            assert (
                get_settings_value(setting_name="default_view_definer")
                == f"{default_default_view_definer}"
            ), error()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_SqlSecurityNotSpecified("1.0"),
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
    definer was specified when creating view.
    """
    node = self.context.node

    with Given("I create view's source table and insert 10 rows in it"):
        source_table_name = create_simple_MergeTree_table(column_name="x", rows=10)

    with And("I check that default_normal_view_sql_security setting is INVOKER"):
        assert (
            get_settings_value(setting_name="default_normal_view_sql_security")
            == "INVOKER"
        ), error()

    with And("I create definer user and grant SELECT privilege for source table"):
        definer_user = "alice_" + getuid()
        create_user(user_name=definer_user)
        grant_privileges_directly(
            privileges=["SELECT"], user=definer_user, object=source_table_name
        )

    with And("I create normal view only specifying definer"):
        view_name = create_view(
            source_table_name=source_table_name,
            definer=definer_user,
        )

    with When("I create user and grant him SELECT privilege for view"):
        user_name = "user_" + getuid()
        create_user(user_name=user_name)
        grant_privileges_directly(
            user=user_name,
            object=view_name,
            privileges=["SELECT"],
        )

    with Then("I check if user can select from view"):
        output = node.query(
            f"SELECT sum(x) FROM {view_name}",
            settings=[("user", user_name)],
        ).output
        assert output == "45", error()

    with Then("I check that SQL SECURITY DEFINER is in create view statement"):
        output = node.query(f"SHOW CREATE TABLE {view_name} FORMAT TabSeparated").output
        assert "SQL SECURITY DEFINER" in output, error()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_Select_SqlSecurityDefiner_Definer("1.0"),
)
def check_select_sql_security_definer_definer(
    self,
    user_view_privilege,
    user_source_table_privilege,
    definer_source_table_privilege,
    grant_privilege,
):
    """
    =======      | =======   | =======
    SQL security | Definer   | Operation
    =======      | =======   | =======
    DEFINER      | alice     | SELECT
    =======      | =======   | =======

    Check that user can select from normal view with given SQL SECURITY
    options when user has SELECT privilege for view and definer user has SELECT
    privilege for view's source table.
    """
    node = self.context.node

    with Given("I create view's source table and insert 10 rows in it"):
        source_table_name = create_simple_MergeTree_table(column_name="x", rows=10)

    with And("I create definer user and grant him privileges to view's source table"):
        definer_user = "alice_" + getuid()
        create_user(user_name=definer_user)
        grant_privilege(
            user=definer_user,
            object=source_table_name,
            privileges=definer_source_table_privilege,
        )

    with And("I create normal view specifying SQL security and definer"):
        view_name = create_view(
            source_table_name=source_table_name,
            sql_security="DEFINER",
            definer=definer_user,
        )

    with When("I create user and grant privileges to view and view's source table"):
        user_name = "user_" + getuid()
        create_user(user_name=user_name)
        grant_privilege(
            user=user_name,
            object=view_name,
            privileges=user_view_privilege,
        )
        grant_privilege(
            user=user_name,
            object=source_table_name,
            privileges=user_source_table_privilege,
        )

    with Then(
        """I check that user can select from view if he has SELECT privilege for view and
            definer user has SELECT for view's source table"""
    ):
        if (
            "SELECT" in user_view_privilege
            and "SELECT" in definer_source_table_privilege
        ):
            output = node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()
        else:
            if "SELECT" not in user_view_privilege:
                exitcode, message = errors.not_enough_privileges(name=user_name)
            else:
                exitcode, message = errors.not_enough_privileges(name=definer_user)
            node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def select_sql_security_definer_definer(self):
    """Run check_select_sql_security_definer_definer with different privileges for definer and user."""
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
            definer_source_table_privilege,
            grant_privilege,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
        ):
            test_name = f"{user_view_privilege}_{user_source_table_privilege}_{definer_source_table_privilege}_{grant_privilege.__name__}"
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
                definer_source_table_privilege=definer_source_table_privilege,
                grant_privilege=grant_privilege,
            )

        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_Select_SqlSecurityDefiner_DefinerNotSpecified(
        "1.0"
    ),
)
def check_select_sql_security_definer_definer_not_specified(
    self,
    user_view_privilege,
    user_source_table_privilege,
    grant_privilege,
):
    """
    =======      | =======       | =======
    SQL security | Definer       | Operation
    =======      | =======       | =======
    DEFINER      | not specified | SELECT
    =======      | =======       | =======

    If definer is not specified then it should be set to CURRENT_USER.
    Check that user can select from normal view with given SQL SECURITY
    options when user has SELECT privilege for view and definer user has SELECT
    privilege for view's source table.
    """
    node = self.context.node

    with Given("I create view's source table and insert 10 rows in it"):
        source_table_name = create_simple_MergeTree_table(column_name="x", rows=10)

    with And("I create normal view only specifying SQL SECURITY"):
        view_name = create_view(
            source_table_name=source_table_name,
            sql_security="DEFINER",
        )

    with When("I create user and grant him privileges to view and view's source table"):
        user_name = "user_" + getuid()
        create_user(user_name=user_name)
        grant_privilege(
            user=user_name,
            object=view_name,
            privileges=user_view_privilege,
        )
        grant_privilege(
            user=user_name,
            object=source_table_name,
            privileges=user_source_table_privilege,
        )

    with Then(
        "I check that user can select from view if he has SELECT privilege for view"
    ):
        if "SELECT" in user_view_privilege:
            output = node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()
        else:
            exitcode, message = errors.not_enough_privileges(name=user_name)
            node.query(
                f"SELECT sum(x) FROM {view_name}",
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
            grant_privilege,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
        ):
            test_name = f"{user_view_privilege}_{user_source_table_privilege}_{grant_privilege.__name__}"
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
                grant_privilege=grant_privilege,
            )
        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_Select_SqlSecurityInvoker_Definer("1.0"),
)
def check_select_sql_security_invoker_definer(
    self,
    user_view_privilege,
    user_source_table_privilege,
    definer_source_table_privilege,
    grant_privilege,
):
    """
    =======      | =======   | =======
    SQL security | Definer   | Operation
    =======      | =======   | =======
    INVOKER      | alice     | SELECT
    =======      | =======   | =======

    Check that user can select from normal view with given SQL SECURITY
    options when user has SELECT privilege for view and SELECT
    privilege for view's source table.
    """
    node = self.context.node

    with Given("I create view's source table and insert 10 rows in it"):
        source_table_name = create_simple_MergeTree_table(column_name="x", rows=10)

    with And("I create definer user and grant him privileges to view's source table"):
        definer_user = "alice_" + getuid()
        create_user(user_name=definer_user)
        grant_privilege(
            user=definer_user,
            object=source_table_name,
            privileges=definer_source_table_privilege,
        )

    with And("I create normal view specifying SQL security and definer"):
        view_name = create_view(
            source_table_name=source_table_name,
            sql_security="INVOKER",
            definer=definer_user,
        )

    with When("I create user and grant privileges to view and view's source table"):
        user_name = "user_" + getuid()
        create_user(user_name=user_name)
        grant_privilege(
            user=user_name,
            object=view_name,
            privileges=user_view_privilege,
        )
        grant_privilege(
            user=user_name,
            object=source_table_name,
            privileges=user_source_table_privilege,
        )

    with Then(
        """I check that user can select from view if he has SELECT privilege for
           view and SELECT privilege for view's source table"""
    ):
        if "SELECT" in user_view_privilege and "SELECT" in user_source_table_privilege:
            output = node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()
        else:
            exitcode, message = errors.not_enough_privileges(name=user_name)
            node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def select_sql_security_invoker_definer(self):
    """Run check_select_sql_security_invoker_definer with different privileges for definer and user."""
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
            definer_source_table_privilege,
            grant_privilege,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
        ):
            test_name = f"{user_view_privilege}_{user_source_table_privilege}_{definer_source_table_privilege}_{grant_privilege.__name__}"
            test_name = (
                test_name.replace("[", "_")
                .replace("]", "_")
                .replace(")", "/")
                .replace("(", "/")
            )
            Scenario(
                test_name,
                test=check_select_sql_security_invoker_definer,
                parallel=True,
                executor=executor,
            )(
                user_view_privilege=user_view_privilege,
                user_source_table_privilege=user_source_table_privilege,
                definer_source_table_privilege=definer_source_table_privilege,
                grant_privilege=grant_privilege,
            )

        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_Select_SqlSecurityInvoker_Definer("1.0"),
)
def check_select_sql_security_invoker_definer_not_specified(
    self,
    user_view_privilege,
    user_source_table_privilege,
    grant_privilege,
):
    """
    =======      | =======       | =======
    SQL security | Definer       | Operation
    =======      | =======       | =======
    INVOKER      | not specified | SELECT
    =======      | =======       | =======

    Check that user can select from normal view with given SQL SECURITY
    options when user has SELECT privilege for view and SELECT
    privilege for view's source table.
    """
    node = self.context.node

    with Given("I create view's source table and insert 10 rows in it"):
        source_table_name = create_simple_MergeTree_table(column_name="x", rows=10)

    with And("I create normal view specifying only SQL security INVOKER"):
        view_name = create_view(
            source_table_name=source_table_name,
            sql_security="INVOKER",
        )

    with When("I create user and grant privileges to view and view's source table"):
        user_name = "user_" + getuid()
        create_user(user_name=user_name)
        grant_privilege(
            user=user_name,
            object=view_name,
            privileges=user_view_privilege,
        )
        grant_privilege(
            user=user_name,
            object=source_table_name,
            privileges=user_source_table_privilege,
        )

    with Then(
        """I check that user can select from view if he has SELECT privilege for
           view and SELECT privilege for view's source table"""
    ):
        if "SELECT" in user_view_privilege and "SELECT" in user_source_table_privilege:
            output = node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()
        else:
            exitcode, message = errors.not_enough_privileges(name=user_name)
            node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def select_sql_security_invoker_definer_not_specified(self):
    """Run check_select_sql_security_invoker_definer_not_specified with different user privileges."""
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
            grant_privilege,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
        ):
            test_name = f"{user_view_privilege}_{user_source_table_privilege}_{grant_privilege.__name__}"
            test_name = (
                test_name.replace("[", "_")
                .replace("]", "_")
                .replace(")", "/")
                .replace("(", "/")
            )
            Scenario(
                test_name,
                test=check_select_sql_security_invoker_definer_not_specified,
                parallel=True,
                executor=executor,
            )(
                user_view_privilege=user_view_privilege,
                user_source_table_privilege=user_source_table_privilege,
                grant_privilege=grant_privilege,
            )

        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_Select_SqlSecurityNotSpecified_Definer("1.0"),
)
def check_select_sql_security_not_specified_definer(
    self,
    user_view_privilege,
    user_source_table_privilege,
    definer_source_table_privilege,
    grant_privilege,
):
    """
    =======       | =======       | =======
    SQL security  | Definer       | Operation
    =======       | =======       | =======
    not specified | alice         | SELECT
    =======       | =======       | =======

    SQL security should be set to DEFINER by default.
    Check that user can select from normal view with given SQL SECURITY
    options when user has SELECT privilege for view and definer user has SELECT
    privilege for views's source table.
    """
    node = self.context.node

    with Given("I create view's source table and insert 10 rows in it"):
        source_table_name = create_simple_MergeTree_table(column_name="x", rows=10)

    with And("I create definer user and grant him privileges to view's source table"):
        definer_user = "alice_" + getuid()
        create_user(user_name=definer_user)
        grant_privilege(
            user=definer_user,
            object=source_table_name,
            privileges=definer_source_table_privilege,
        )

    with And("I create normal view only specifying definer"):
        view_name = create_view(
            source_table_name=source_table_name,
            definer=definer_user,
        )

    with When("I create user and grant him privileges to view and view's source table"):
        user_name = "user_" + getuid()
        create_user(user_name=user_name)
        grant_privilege(
            user=user_name,
            object=view_name,
            privileges=user_view_privilege,
        )
        grant_privilege(
            user=user_name,
            object=source_table_name,
            privileges=user_source_table_privilege,
        )

    with Then(
        """I check that user can select from view if he has SELECT privilege for view and
            definer user has SELECT privilege for view's source table"""
    ):
        if (
            "SELECT" in user_view_privilege
            and "SELECT" in definer_source_table_privilege
        ):
            output = node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()
        else:
            if "SELECT" not in user_view_privilege:
                exitcode, message = errors.not_enough_privileges(name=user_name)
            else:
                exitcode, message = errors.not_enough_privileges(name=definer_user)
            node.query(
                f"SELECT sum(x) FROM {view_name}",
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
            definer_source_table_privilege,
            grant_privilege,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
        ):
            test_name = f"{user_view_privilege}_{user_source_table_privilege}_{definer_source_table_privilege}_{grant_privilege.__name__}"
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
                definer_source_table_privilege=definer_source_table_privilege,
                grant_privilege=grant_privilege,
            )
        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_Select_SqlSecurityNotSpecified_DefinerNotSpecified(
        "1.0"
    ),
)
def select_sql_security_not_specified_definer_not_specified(self):
    """
    =======       | =======       | =======
    SQL security  | Definer       | Operation
    =======       | =======       | =======
    not specified | not specified | SELECT
    =======       | =======       | =======

    SQL security is set to the value from `default_normal_view_sql_security`
    setting and definer is set to the value from `default_view_definer` setting.
    Check that user can select from normal view with given SQL SECURITY
    options when user has SELECT privilege for view and definer user has SELECT
    privilege for view's source table.
    """
    node = self.context.node
    default_default_view_definer = get_settings_value(
        setting_name="default_view_definer"
    )
    default_default_normal_view_sql_security = get_settings_value(
        setting_name="default_normal_view_sql_security"
    )
    default_ignore_empty_sql_security_in_create_view_query = get_settings_value(
        setting_name="ignore_empty_sql_security_in_create_view_query",
        table="system.server_settings",
    )

    try:
        with Given("I create view's source table and insert 10 rows in it"):
            source_table_name = create_simple_MergeTree_table(column_name="x", rows=10)

        with And(
            "I create definer user and grant him SELECT privilege for view's source table"
        ):
            definer_user = "alice_" + getuid()
            create_user(user_name=definer_user)
            grant_privileges_directly(
                user=definer_user,
                object=source_table_name,
                privileges=["SELECT"],
            )

        with And(
            """I set ignore_empty_sql_security_in_create_view_query to 0 to use values from 
            default_view_definer and default_normal_view_sql_security"""
        ):
            if default_ignore_empty_sql_security_in_create_view_query == "1":
                entries = {"ignore_empty_sql_security_in_create_view_query": "0"}
                change_core_settings(
                    restart=True,
                    entries=entries,
                    config_d_dir="/etc/clickhouse-server/config.d",
                    preprocessed_name="config.xml",
                )

        with And(
            f"""I change default_view_definer setting to {definer_user} and 
            default_normal_view_sql_security to DEFINER for default user"""
        ):
            entries = {
                "profiles": {
                    "default": {
                        "default_view_definer": f"{definer_user}",
                        "default_normal_view_sql_security": "DEFINER",
                    }
                }
            }
            change_core_settings(restart=True, entries=entries)

        with And(
            f"I check that default_view_definer setting was changed to {definer_user}"
        ):
            assert (
                get_settings_value(setting_name="default_view_definer")
                == f"{definer_user}"
            ), error()

        with And(
            "I check that default_normal_view_sql_security setting was changed to DEFINER"
        ):
            assert (
                get_settings_value(setting_name="default_normal_view_sql_security")
                == "DEFINER"
            ), error()

        with And("I create normal view without specifying definer and sql security"):
            view_name = create_view(
                source_table_name=source_table_name,
            )

        with And(
            "I check that values from default settings are in create view statement"
        ):
            output = node.query(
                f"SHOW CREATE TABLE {view_name} FORMAT TabSeparated"
            ).output
            assert f"DEFINER = {definer_user} SQL SECURITY DEFINER" in output, error()

        with When("I create user and grant him SELECT privilege for view"):
            user_name = "user_" + getuid()
            create_user(user_name=user_name)
            grant_privileges_directly(
                user=user_name,
                object=view_name,
                privileges=["SELECT"],
            )

        with Then(
            """I check that user can select from view if he has SELECT privilege for 
            view and definer user has SELECT privilege for view's source table"""
        ):
            output = node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()

    finally:
        with Finally(
            "I restore default_view_definer and default_normal_view_sql_security settings"
        ):
            entries = {
                "profiles": {
                    "default": {
                        "default_view_definer": f"{default_default_view_definer}",
                        "default_normal_view_sql_security": f"{default_default_normal_view_sql_security}",
                    }
                }
            }
            change_core_settings(restart=True, entries=entries)

        with And("I restore ignore_empty_sql_security_in_create_view_query setting"):
            changed = get_settings_value(
                setting_name="ignore_empty_sql_security_in_create_view_query",
                table="system.server_settings",
                column="changed",
            )
            if changed:
                entries = {
                    "ignore_empty_sql_security_in_create_view_query": f"{default_ignore_empty_sql_security_in_create_view_query}"
                }
                change_core_settings(
                    restart=True,
                    entries=entries,
                    config_d_dir="/etc/clickhouse-server/config.d",
                    preprocessed_name="config.xml",
                )

        with And("I check that all settings were restored"):
            assert (
                get_settings_value(setting_name="default_view_definer")
                == f"{default_default_view_definer}"
            ), error()
            assert (
                get_settings_value(
                    setting_name="ignore_empty_sql_security_in_create_view_query",
                    table="system.server_settings",
                )
                == f"{default_ignore_empty_sql_security_in_create_view_query}"
            ), error()
            assert (
                get_settings_value(setting_name="default_normal_view_sql_security")
                == f"{default_default_normal_view_sql_security}"
            ), error()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_Select_SqlSecurityNone_Definer("1.0"),
)
def check_select_sql_security_none_definer(
    self,
    user_view_privilege,
    user_source_table_privilege,
    definer_source_table_privilege,
    grant_privilege,
):
    """
    =======      | =======   | =======
    SQL security | Definer   | Operation
    =======      | =======   | =======
    NONE         | alice     | SELECT
    =======      | =======   | =======

    Check that user can select from normal view with given SQL SECURITY
    options when user has SELECT privilege for view.
    """
    node = self.context.node

    with Given("I create view's source table and insert 10 rows in it"):
        source_table_name = create_simple_MergeTree_table(column_name="x", rows=10)

    with And("I create definer user and grant him privileges to view's source table"):
        definer_user = "alice_" + getuid()
        create_user(user_name=definer_user)
        grant_privilege(
            user=definer_user,
            object=source_table_name,
            privileges=definer_source_table_privilege,
        )

    with And("I create normal view specifying SQL security NONE and definer"):
        view_name = create_view(
            source_table_name=source_table_name,
            sql_security="NONE",
            definer=definer_user,
        )

    with When("I create user and grant privileges to view"):
        user_name = "user_" + getuid()
        create_user(user_name=user_name)
        grant_privilege(
            user=user_name,
            object=view_name,
            privileges=user_view_privilege,
        )
        grant_privilege(
            user=user_name,
            object=source_table_name,
            privileges=user_source_table_privilege,
        )

    with Then(
        "I check that user can select from view if he has SELECT privilege for view"
    ):
        if "SELECT" in user_view_privilege:
            output = node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()
        else:
            exitcode, message = errors.not_enough_privileges(name=user_name)
            node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def select_sql_security_none_definer(self):
    """Run check_select_sql_security_none_definer with different privileges for definer and user."""
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
            definer_source_table_privilege,
            grant_privilege,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
        ):
            test_name = f"{user_view_privilege}_{user_source_table_privilege}_{definer_source_table_privilege}_{grant_privilege.__name__}"
            test_name = (
                test_name.replace("[", "_")
                .replace("]", "_")
                .replace(")", "/")
                .replace("(", "/")
            )
            Scenario(
                test_name,
                test=check_select_sql_security_none_definer,
                parallel=True,
                executor=executor,
            )(
                user_view_privilege=user_view_privilege,
                user_source_table_privilege=user_source_table_privilege,
                definer_source_table_privilege=definer_source_table_privilege,
                grant_privilege=grant_privilege,
            )
        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_Select_SqlSecurityNone_DefinerNotSpecified("1.0"),
)
def check_select_sql_security_none_definer_not_specified(
    self,
    user_view_privilege,
    user_source_table_privilege,
    grant_privilege,
):
    """
    =======      | =======       | =======
    SQL security | Definer       | Operation
    =======      | =======       | =======
    NONE         | not specified | SELECT
    =======      | =======       | =======

    Check that user can select from normal view with given SQL SECURITY
    options when user has SELECT privilege for view.
    """
    node = self.context.node

    with Given("I create view's source table and insert 10 rows in it"):
        source_table_name = create_simple_MergeTree_table(column_name="x", rows=10)

    with And("I create normal view specifying only SQL security NONE"):
        view_name = create_view(
            source_table_name=source_table_name,
            sql_security="NONE",
        )

    with When("I create user and grant privileges to view"):
        user_name = "user_" + getuid()
        create_user(user_name=user_name)
        grant_privilege(
            user=user_name,
            object=view_name,
            privileges=user_view_privilege,
        )
        grant_privilege(
            user=user_name,
            object=source_table_name,
            privileges=user_source_table_privilege,
        )

    with Then(
        "I check that user can select from view if he has SELECT privilege for view"
    ):
        if "SELECT" in user_view_privilege:
            output = node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
            ).output
            assert output == "45", error()
        else:
            exitcode, message = errors.not_enough_privileges(name=user_name)
            node.query(
                f"SELECT sum(x) FROM {view_name}",
                settings=[("user", user_name)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def select_sql_security_none_definer_not_specified(self):
    """Run check_select_sql_security_none_definer_not_specified with different user privileges."""
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
            grant_privilege,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
        ):
            test_name = f"{user_view_privilege}_{user_source_table_privilege}_{grant_privilege.__name__}"
            test_name = (
                test_name.replace("[", "_")
                .replace("]", "_")
                .replace(")", "/")
                .replace("(", "/")
            )
            Scenario(
                test_name,
                test=check_select_sql_security_none_definer_not_specified,
                parallel=True,
                executor=executor,
            )(
                user_view_privilege=user_view_privilege,
                user_source_table_privilege=user_source_table_privilege,
                grant_privilege=grant_privilege,
            )
        join()


@TestFeature
@Name("normal view SQL security")
def feature(self):
    """Check SQL security functionality for normal views."""
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node_2, self.context.node_3]

    with Pool(7) as executor:
        Scenario(run=check_create_view, parallel=True, executor=executor)
        Scenario(run=check_create_view_on_cluster, parallel=True, executor=executor)
        Scenario(run=check_default_values, parallel=True, executor=executor)
        Scenario(run=sql_security_not_specified, parallel=True, executor=executor)
        Scenario(
            run=select_sql_security_definer_definer, parallel=True, executor=executor
        )
        Scenario(
            run=select_sql_security_definer_definer_not_specified,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=select_sql_security_invoker_definer, parallel=True, executor=executor
        )
        Scenario(
            run=select_sql_security_invoker_definer_not_specified,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=select_sql_security_not_specified_definer,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=select_sql_security_none_definer,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=select_sql_security_none_definer_not_specified,
            parallel=True,
            executor=executor,
        )
        join()

    Scenario(run=definer_not_specified)
    Scenario(run=select_sql_security_not_specified_definer_not_specified)
    Scenario(run=check_default_values)
