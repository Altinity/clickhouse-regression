from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product, combinations

import rbac.helper.errors as errors
from rbac.requirements import *
from rbac.tests.sql_security.common import *

from helpers.common import getuid


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_MultipleSourceTables_Select_SqlSecurityDefiner_Definer(
        "1.0"
    ),
)
def check_select_from_mv_multiple_source_tables_with_join(
    self,
    definer_source_1_privileges,
    definer_source_2_privileges,
    definer_source_3_privileges,
    definer_target_privileges,
    grant_privilege,
    join_option,
):
    """
    =======      | =======   | =======
    SQL security | Definer   | Operation
    =======      | =======   | =======
    DEFINER      | alice     | SELECT
    =======      | =======   | =======

    Check that user can select from MV that was triggered at least
    once with given SQL SECURITY options when user has SELECT privilege for MV and
    definer user has SELECT privilege for all MV's source tables and target table.
    """
    node = self.context.node

    with Given("create three empty source tables"):
        source_table_1 = f"table_source1_{getuid()}"
        source_table_2 = f"table_source2_{getuid()}"
        source_table_3 = f"table_source3_{getuid()}"
        create_table_with_two_columns_with_data(table_name=source_table_1, rows=0)
        create_table_with_two_columns_with_data(table_name=source_table_2, rows=0)
        create_table_with_two_columns_with_data(table_name=source_table_3, rows=0)

    with And("create MV's target table and insert 10 rows"):
        target_table = f"table_target_{getuid()}"
        create_table_with_two_columns_with_data(table_name=target_table, rows=10)

    with And("create definer user"):
        definer = f"definer_{getuid()}"
        create_user(user_name=definer)

    with And("create MV specifying sql security DEFINER and definer user"):
        view = create_materialized_view_with_join(
            source_table_name_1=source_table_1,
            source_table_name_2=source_table_2,
            source_table_name_3=source_table_3,
            target_table_name=target_table,
            join_option=join_option,
            sql_security="DEFINER",
            definer=definer,
        )

    with And("create user to select from view and grant him SELECT privilege on MV"):
        user = f"user_{getuid()}"
        create_user(user_name=user)
        grant_privilege(user=user, object=view, privileges=["SELECT"])

    with And(
        "check that the user cannot select from the view unless the definer user has SELECT privileges for source and target tables"
    ):
        exitcode, message = errors.not_enough_privileges(name=definer)
        node.query(
            f"SELECT count() FROM {view} FORMAT TabSeparated",
            settings=[("user", user)],
            exitcode=exitcode,
            message=message,
        )

    with And(
        "grant privileges to definer user on source tables and target table",
    ):
        grant_privilege(
            user=definer, object=source_table_1, privileges=definer_source_1_privileges
        )
        grant_privilege(
            user=definer, object=source_table_2, privileges=definer_source_2_privileges
        )
        grant_privilege(
            user=definer, object=source_table_3, privileges=definer_source_3_privileges
        )
        grant_privilege(
            user=definer, object=target_table, privileges=definer_target_privileges
        )

    with And(
        "check that user can select from MV if definer has SELECT privilege for first source table in create MV statement and target table"
    ):
        if (
            "SELECT" in definer_source_1_privileges
            and "SELECT" in definer_target_privileges
        ):
            output = node.query(
                f"SELECT count() FROM {view} FORMAT TabSeparated",
                settings=[("user", user)],
            ).output
            assert "10" in output, error()
        else:
            exitcode, message = errors.not_enough_privileges(name=definer)
            node.query(
                f"SELECT count() FROM {view} FORMAT TabSeparated",
                settings=[("user", user)],
                exitcode=exitcode,
                message=message,
            )

    with And(
        "try to insert data to second and third source tables and to first source table that triggers MV's update"
    ):
        triggered = False
        condition = (
            "INSERT" in definer_target_privileges
            and "SELECT" in definer_source_1_privileges
            and "SELECT" in definer_source_2_privileges
            if join_option != "PASTE JOIN"
            else "INSERT" in definer_target_privileges
            and "SELECT" in definer_source_1_privileges
            and "SELECT" in definer_source_2_privileges
            and "SELECT" in definer_source_3_privileges
        )
        if condition:
            node.query(
                f"INSERT INTO {source_table_3} SELECT number%9, number%6 FROM numbers(20)"
            )
            node.query(
                f"INSERT INTO {source_table_2} SELECT number%10, number%6 FROM numbers(20)"
            )
            node.query(
                f"INSERT INTO {source_table_1} SELECT number, number%3 FROM numbers(20)"
            )
            triggered = True
        else:
            node.query(
                f"INSERT INTO {source_table_1} SELECT number, number%3 FROM numbers(20)",
                exitcode=exitcode,
                message=message,
            )

    with And(
        "check that user can select from view that was triggered when definer has SELECT privilege for all source tables and target table"
    ):
        condition = (
            "SELECT" in definer_target_privileges
            and "SELECT" in definer_source_1_privileges
            and "SELECT" in definer_source_2_privileges
            if join_option != "PASTE JOIN"
            else "SELECT" in definer_target_privileges
            and "SELECT" in definer_source_1_privileges
            and "SELECT" in definer_source_2_privileges
            and "SELECT" in definer_source_3_privileges
        )
        if condition:
            output = node.query(
                f"SELECT count() FROM {view} FORMAT TabSeparated",
                settings=[("user", user)],
            ).output
        elif triggered:
            exitcode, message = errors.not_enough_privileges(name=definer)
            node.query(
                f"SELECT count() FROM {view} FORMAT TabSeparated",
                settings=[("user", user)],
                exitcode=exitcode,
                message=message,
            )
        elif (
            "SELECT" in definer_source_1_privileges
            and "SELECT" in definer_target_privileges
        ):
            output = node.query(
                f"SELECT count() FROM {view} FORMAT TabSeparated",
                settings=[("user", user)],
            ).output
            assert "10" in output, error()
        else:
            exitcode, message = errors.not_enough_privileges(name=definer)
            node.query(
                f"SELECT count() FROM {view} FORMAT TabSeparated",
                settings=[("user", user)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_MultipleSourceTables_Insert_SqlSecurityDefiner_Definer(
        "1.0"
    ),
)
def check_insert_into_mv_multiple_source_tables_with_join(
    self,
    definer_source_1_privileges,
    definer_source_2_privileges,
    definer_source_3_privileges,
    definer_target_privileges,
    grant_privilege,
    join_option,
):
    """
    =======      | =======   | =======
    SQL security | Definer   | Operation
    =======      | =======   | =======
    DEFINER      | alice     | INSERT
    =======      | =======   | =======

    Check that user can insert into MV with given SQL SECURITY
    options when user has INSERT privilege for MV and definer user has INSERT
    privilege for MV's target table.
    """
    node = self.context.node

    with Given("create three source tables with data"):
        source_table_1 = f"table_source1_{getuid()}"
        source_table_2 = f"table_source2_{getuid()}"
        source_table_3 = f"table_source3_{getuid()}"
        create_table_with_two_columns_with_data(table_name=source_table_1)
        create_table_with_two_columns_with_data(table_name=source_table_2)
        create_table_with_two_columns_with_data(table_name=source_table_3)

    with And("create MV's target table"):
        target_table = f"table_target_{getuid()}"
        create_table_with_two_columns_with_data(table_name=target_table, rows=10)

    with And("create definer user"):
        definer = f"definer_{getuid()}"
        create_user(user_name=definer)

    with And("create MV specifying sql security DEFINER and definer user"):
        view = create_materialized_view_with_join(
            source_table_name_1=source_table_1,
            source_table_name_2=source_table_2,
            source_table_name_3=source_table_3,
            target_table_name=target_table,
            join_option=join_option,
            sql_security="DEFINER",
            definer=definer,
        )

    with And("create user and grant him SELECT and INSERT privileges on MV"):
        user = f"user_{getuid()}"
        create_user(user_name=user)
        grant_privilege(user=user, object=view, privileges=["SELECT", "INSERT"])

    with And(
        "check that user can not insert into view unless the definer user has INSERT privilege for MV's target table"
    ):
        exitcode, message = errors.not_enough_privileges(name=definer)
        node.query(
            f"INSERT INTO {view} SELECT number,number FROM numbers(10)",
            settings=[("user", user)],
            exitcode=exitcode,
            message=message,
        )

    with And(
        "grant privileges to definer user on source tables and target table",
    ):
        grant_privilege(
            user=definer, object=source_table_1, privileges=definer_source_1_privileges
        )
        grant_privilege(
            user=definer, object=source_table_2, privileges=definer_source_2_privileges
        )
        grant_privilege(
            user=definer, object=source_table_3, privileges=definer_source_3_privileges
        )
        grant_privilege(
            user=definer, object=target_table, privileges=definer_target_privileges
        )

    with And(
        "check that user can insert into MV if definer has INSERT privilege for target table"
    ):
        if "INSERT" in definer_target_privileges:
            node.query(
                f"INSERT INTO {view} SELECT number,number FROM numbers(10) FORMAT TabSeparated",
                settings=[("user", user)],
            )
            if (
                "SELECT" in definer_target_privileges
                and "SELECT" in definer_source_1_privileges
            ):
                output = node.query(
                    f"SELECT count() FROM {view} FORMAT TabSeparated",
                    settings=[("user", user)],
                ).output
                assert "20" in output, error()
        else:
            exitcode, message = errors.not_enough_privileges(name=definer)
            node.query(
                f"INSERT INTO {view} SELECT number,number FROM numbers(10) FORMAT TabSeparated",
                settings=[("user", user)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_MultipleSourceTables_Select_SqlSecurityDefiner_Definer(
        "1.0"
    ),
)
def check_select_from_view_multiple_source_tables_with_join_definer(
    self,
    definer_source_1_privileges,
    definer_source_2_privileges,
    definer_source_3_privileges,
    grant_privilege,
    join_option,
):
    """
    =======      | =======   | =======
    SQL security | Definer   | Operation
    =======      | =======   | =======
    DEFINER      | alice     | SELECT
    =======      | =======   | =======

    Check that user can select from normal view with given SQL SECURITY
    options when user has SELECT privilege for the view and definer user has SELECT
    privilege for all view's source tables.
    """
    node = self.context.node

    with Given("create three empty source tables"):
        source_table_1 = f"table_source1_{getuid()}"
        source_table_2 = f"table_source2_{getuid()}"
        source_table_3 = f"table_source3_{getuid()}"
        create_table_with_two_columns_with_data(table_name=source_table_1, rows=0)
        create_table_with_two_columns_with_data(table_name=source_table_2, rows=0)
        create_table_with_two_columns_with_data(table_name=source_table_3, rows=0)

    with And("create definer user"):
        definer = f"definer_{getuid()}"
        node.query(f"CREATE USER {definer}")

    with And("create normal view specifying sql security DEFINER and definer user"):
        view = create_normal_view_with_join(
            source_table_name_1=source_table_1,
            source_table_name_2=source_table_2,
            source_table_name_3=source_table_3,
            join_option=join_option,
            sql_security="DEFINER",
            definer=definer,
        )

    with And("create user to select from view and grant him SELECT privilege on MV"):
        user = f"user_{getuid()}"
        create_user(user_name=user)
        grant_privilege(user=user, object=view, privileges=["SELECT"])

    with And(
        "check that the user cannot select from the view unless the definer user has SELECT privileges for source tables"
    ):
        exitcode, message = errors.not_enough_privileges(name=definer)
        node.query(
            f"SELECT count() FROM {view} FORMAT TabSeparated",
            settings=[("user", user)],
            exitcode=exitcode,
            message=message,
        )

    with And(
        "grant privileges to definer user on source tables",
    ):
        grant_privilege(
            user=definer, object=source_table_1, privileges=definer_source_1_privileges
        )
        grant_privilege(
            user=definer, object=source_table_2, privileges=definer_source_2_privileges
        )
        grant_privilege(
            user=definer, object=source_table_3, privileges=definer_source_3_privileges
        )

    with And("insert data to source tables"):
        node.query(
            f"INSERT INTO {source_table_3} SELECT number%9, number%6 FROM numbers(20)"
        )
        node.query(
            f"INSERT INTO {source_table_2} SELECT number%10, number%6 FROM numbers(20)"
        )
        node.query(
            f"INSERT INTO {source_table_1} SELECT number, number%3 FROM numbers(20)"
        )

    with And(
        "check that user can select from view when definer has SELECT privilege for all source tables and target table"
    ):
        expected_output = {
            "INNER JOIN": "20",
            "CROSS JOIN": "400",
            "LEFT ASOF JOIN": "20",
            "PASTE JOIN": "12",
            "LEFT OUTER JOIN": "30",
            "RIGHT OUTER JOIN": "20",
            "FULL OUTER JOIN": "30",
            "LEFT SEMI JOIN": "10",
            "RIGHT SEMI JOIN": "20",
            "LEFT ANTI JOIN": "10",
            "RIGHT ANTI JOIN": "0",
            "LEFT ANY JOIN": "20",
            "RIGHT ANY JOIN": "20",
            "INNER ANY JOIN": "10",
            "ASOF JOIN": "10",
        }
        condition = (
            "SELECT" in definer_source_1_privileges
            and "SELECT" in definer_source_2_privileges
            if join_option != "PASTE JOIN"
            else "SELECT" in definer_source_1_privileges
            and "SELECT" in definer_source_2_privileges
            and "SELECT" in definer_source_3_privileges
        )
        if condition:
            output = node.query(
                f"SELECT count() FROM {view} FORMAT TabSeparated",
                settings=[("user", user)],
            ).output
            assert expected_output[join_option] in output, error()
        else:
            exitcode, message = errors.not_enough_privileges(name=definer)
            node.query(
                f"SELECT count() FROM {view} FORMAT TabSeparated",
                settings=[("user", user)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_View_MultipleSourceTables_Select_SqlSecurityInvoker(
        "1.0"
    ),
)
def check_select_from_view_multiple_source_tables_with_join_invoker(
    self,
    user_source_1_privileges,
    user_source_2_privileges,
    user_source_3_privileges,
    grant_privilege,
    join_option,
):
    """
    =======      | =======
    SQL security | Operation
    =======      | =======
    INVOKER      | SELECT
    =======      | =======

    Check that user can select from normal view with given SQL SECURITY
    options when user has SELECT privilege for the view and for all view's source tables.
    """
    node = self.context.node

    with Given("create three empty source tables"):
        source_table_1 = f"table_source1_{getuid()}"
        source_table_2 = f"table_source2_{getuid()}"
        source_table_3 = f"table_source3_{getuid()}"
        create_table_with_two_columns_with_data(table_name=source_table_1, rows=0)
        create_table_with_two_columns_with_data(table_name=source_table_2, rows=0)
        create_table_with_two_columns_with_data(table_name=source_table_3, rows=0)

    with And("create normal view specifying sql security DEFINER and definer user"):
        view = create_normal_view_with_join(
            source_table_name_1=source_table_1,
            source_table_name_2=source_table_2,
            source_table_name_3=source_table_3,
            join_option=join_option,
            sql_security="INVOKER",
        )

    with And("create user to select from view and grant him SELECT privilege on MV"):
        user = f"user_{getuid()}"
        create_user(user_name=user)
        grant_privilege(user=user, object=view, privileges=["SELECT"])

    with And(
        "check that the user cannot select from the view unless the he has SELECT privileges for source tables"
    ):
        exitcode, message = errors.not_enough_privileges(name=user)
        node.query(
            f"SELECT count() FROM {view} FORMAT TabSeparated",
            settings=[("user", user)],
            exitcode=exitcode,
            message=message,
        )

    with And(
        "grant privileges to definer user on source tables",
    ):
        grant_privilege(
            user=user, object=source_table_1, privileges=user_source_1_privileges
        )
        grant_privilege(
            user=user, object=source_table_2, privileges=user_source_2_privileges
        )
        grant_privilege(
            user=user, object=source_table_3, privileges=user_source_3_privileges
        )

    with And("insert data to source tables"):
        node.query(
            f"INSERT INTO {source_table_3} SELECT number%9, number%6 FROM numbers(20)"
        )
        node.query(
            f"INSERT INTO {source_table_2} SELECT number%10, number%6 FROM numbers(20)"
        )
        node.query(
            f"INSERT INTO {source_table_1} SELECT number, number%3 FROM numbers(20)"
        )

    with And(
        "check that user can select from view when definer has SELECT privilege for all source tables and target table"
    ):
        expected_output = {
            "INNER JOIN": "20",
            "CROSS JOIN": "400",
            "LEFT ASOF JOIN": "20",
            "PASTE JOIN": "12",
            "LEFT OUTER JOIN": "30",
            "RIGHT OUTER JOIN": "20",
            "FULL OUTER JOIN": "30",
            "LEFT SEMI JOIN": "10",
            "RIGHT SEMI JOIN": "20",
            "LEFT ANTI JOIN": "10",
            "RIGHT ANTI JOIN": "0",
            "LEFT ANY JOIN": "20",
            "RIGHT ANY JOIN": "20",
            "INNER ANY JOIN": "10",
            "ASOF JOIN": "10",
        }
        condition = (
            "SELECT" in user_source_1_privileges
            and "SELECT" in user_source_2_privileges
            if join_option != "PASTE JOIN"
            else "SELECT" in user_source_1_privileges
            and "SELECT" in user_source_2_privileges
            and "SELECT" in user_source_3_privileges
        )
        if condition:
            output = node.query(
                f"SELECT count() FROM {view} FORMAT TabSeparated",
                settings=[("user", user)],
            ).output
            assert expected_output[join_option] in output, error()
        else:
            exitcode, message = errors.not_enough_privileges(name=user)
            node.query(
                f"SELECT count() FROM {view} FORMAT TabSeparated",
                settings=[("user", user)],
                exitcode=exitcode,
                message=message,
            )


@TestFeature
@Name("joins")
def run_mv_with_joins(self):
    """Check privileges for operations on materialized views with multiple source tables
    combined with different joins and when different sql security options are set.
    """
    joins = [
        "INNER JOIN",
        # "LEFT OUTER JOIN",
        # "RIGHT OUTER JOIN",
        # "FULL OUTER JOIN",
        # "LEFT SEMI JOIN",
        # "RIGHT SEMI JOIN",
        # "LEFT ANTI JOIN",
        # "RIGHT ANTI JOIN",
        # "LEFT ANY JOIN",
        # "RIGHT ANY JOIN",
        # "INNER ANY JOIN",
        # "ASOF JOIN",
        # "CROSS JOIN",
        # "LEFT ASOF JOIN",
        # "PASTE JOIN",
    ]

    grant_privileges = [grant_privileges_directly, grant_privileges_via_role]
    privileges = ["SELECT", "INSERT", "ALTER", "CREATE", "NONE"]

    if not self.context.stress:
        privileges = ["SELECT", "INSERT", "NONE"]
        grant_privileges = [grant_privileges_directly]

    privileges_combinations = list(combinations(privileges, 2)) + [["NONE"]]

    with Pool(7) as executor:
        for (
            definer_source_1_privileges,
            definer_source_2_privileges,
            definer_source_3_privileges,
            definer_target_privileges,
            grant_privilege,
            join_option,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
            joins,
        ):
            test_name = f"definer_source1-_{definer_source_1_privileges}_definer_source2-_{definer_source_2_privileges}_definer_source3-_{definer_source_3_privileges}_definer_target-_{definer_target_privileges}_{join_option}_{grant_privilege.__name__}"
            test_name = (
                test_name.replace("[", "_")
                .replace("]", "_")
                .replace(")", "_")
                .replace("(", "_")
            )
            Scenario(
                test_name,
                test=check_select_from_mv_multiple_source_tables_with_join,
                parallel=True,
                executor=executor,
            )(
                definer_source_1_privileges=definer_source_1_privileges,
                definer_source_2_privileges=definer_source_2_privileges,
                definer_source_3_privileges=definer_source_3_privileges,
                definer_target_privileges=definer_target_privileges,
                grant_privilege=grant_privilege,
                join_option=join_option,
            )
            Scenario(
                test_name,
                test=check_insert_into_mv_multiple_source_tables_with_join,
                parallel=True,
                executor=executor,
            )(
                definer_source_1_privileges=definer_source_1_privileges,
                definer_source_2_privileges=definer_source_2_privileges,
                definer_source_3_privileges=definer_source_3_privileges,
                definer_target_privileges=definer_target_privileges,
                grant_privilege=grant_privilege,
                join_option=join_option,
            )
        join()


@TestFeature
@Name("joins")
def run_normal_view_with_joins(self):
    """Check privileges for operations on normal views with multiple source tables
    combined with different joins and when different sql security options are set.
    """
    joins = [
        "INNER JOIN",
        "LEFT OUTER JOIN",
        "RIGHT OUTER JOIN",
        "FULL OUTER JOIN",
        "LEFT SEMI JOIN",
        "RIGHT SEMI JOIN",
        "LEFT ANTI JOIN",
        "RIGHT ANTI JOIN",
        "LEFT ANY JOIN",
        "RIGHT ANY JOIN",
        "INNER ANY JOIN",
        "ASOF JOIN",
        "CROSS JOIN",
        "LEFT ASOF JOIN",
        "PASTE JOIN",
    ]

    grant_privileges = [grant_privileges_directly, grant_privileges_via_role]
    privileges = ["SELECT", "INSERT", "ALTER", "CREATE", "NONE"]

    if not self.context.stress:
        privileges = ["SELECT", "INSERT", "NONE"]
        grant_privileges = [grant_privileges_directly]

    privileges_combinations = list(combinations(privileges, 2)) + [["NONE"]]

    with Pool(7) as executor:
        for (
            definer_source_1_privileges,
            definer_source_2_privileges,
            definer_source_3_privileges,
            grant_privilege,
            join_option,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            grant_privileges,
            joins,
        ):
            test_name = f"definer_source1-_{definer_source_1_privileges}_definer_source2-_{definer_source_2_privileges}_definer_source3-_{definer_source_3_privileges}_definer_target-_{join_option}_{grant_privilege.__name__}"
            test_name = (
                test_name.replace("[", "_")
                .replace("]", "_")
                .replace(")", "_")
                .replace("(", "_")
            )
            Scenario(
                test_name,
                test=check_select_from_view_multiple_source_tables_with_join_definer,
                parallel=True,
                executor=executor,
            )(
                definer_source_1_privileges=definer_source_1_privileges,
                definer_source_2_privileges=definer_source_2_privileges,
                definer_source_3_privileges=definer_source_3_privileges,
                grant_privilege=grant_privilege,
                join_option=join_option,
            )
        join()

    with Pool(7) as executor:
        for (
            user_source_1_privileges,
            user_source_2_privileges,
            user_source_3_privileges,
            join_option,
            grant_privilege,
        ) in product(
            privileges_combinations,
            privileges_combinations,
            privileges_combinations,
            joins,
            grant_privileges,
        ):
            test_name = f"user_source1-_{user_source_1_privileges}_user_source2-_{user_source_2_privileges}_user_source3-_{user_source_3_privileges}_{join_option}_{grant_privilege.__name__}"
            test_name = (
                test_name.replace("[", "_")
                .replace("]", "_")
                .replace(")", "_")
                .replace("(", "_")
            )
            Scenario(
                test_name,
                test=check_select_from_view_multiple_source_tables_with_join_invoker,
                parallel=True,
                executor=executor,
            )(
                user_source_1_privileges=user_source_1_privileges,
                user_source_2_privileges=user_source_2_privileges,
                user_source_3_privileges=user_source_3_privileges,
                join_option=join_option,
                grant_privilege=grant_privilege,
            )
        join()


@TestFeature
@Name("joins")
def feature(self, node="clickhouse1"):
    """Check privileges for operations on views with multiple source tables
    combined with different joins and when different sql security options are set.
    """
    self.context.node = self.context.cluster.node(node)

    Feature(run=run_mv_with_joins)
    Feature(run=run_normal_view_with_joins)
