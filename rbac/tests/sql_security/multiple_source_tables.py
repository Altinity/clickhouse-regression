from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product

from itertools import combinations


import rbac.helper.errors as errors
from rbac.requirements import *
from rbac.tests.sql_security.common import *
from helpers.common import getuid, get_settings_value


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_MultipleSourceTables_Select_SqlSecurityDefiner_Definer(
        "1.0"
    ),
)
def multiple_source_table_with_join(
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
    DEFINER      | alice     | SELECT/INSERT
    =======      | =======   | =======

    Check that user can select from materialized view with given SQL SECURITY
    options when user has SELECT privilege for mv and definer user has SELECT
    privilege for all mv's source tables and target table.
    Check that user can insert into materialized view with given SQL SECURITY
    options when user has INSERT privilege for mv and definer user has INSERT
    privilege for all mv's source tables and target table.
    """
    node = self.context.node

    with Given("I create three source tables with data"):
        source_table_1 = f"table_source1_{getuid()}"
        source_table_2 = f"table_source2_{getuid()}"
        source_table_3 = f"table_source3_{getuid()}"
        create_table_with_two_columns_with_data(table_name=source_table_1)
        create_table_with_two_columns_with_data(table_name=source_table_2)
        create_table_with_two_columns_with_data(table_name=source_table_3)

    with And("I create materialized view target table"):
        target_table = f"table_target_{getuid()}"
        create_table_with_two_columns_with_data(table_name=target_table, rows=10)

    with And("I create definer user"):
        definer = f"definer_{getuid()}"
        node.query(f"CREATE USER {definer}")

    with And("I create materialized view"):
        view = create_materialized_view_with_join(
            source_table_name_1=source_table_1,
            source_table_name_2=source_table_2,
            source_table_name_3=source_table_3,
            target_table_name=target_table,
            join_option=join_option,
            sql_security="DEFINER",
            definer=definer,
        )

    with And("I create user"):
        user = f"user_{getuid()}"
        node.query(f"CREATE USER {user}")

    with When("I grant SELECT privilege on materialized view to user"):
        node.query(f"GRANT SELECT ON {view} TO {user}")

    with And(
        "I check that user can not select form view unless definer has SELECT privilege for all source tables and target table"
    ):
        exitcode, message = errors.not_enough_privileges(name=definer)
        node.query(
            f"SELECT count() FROM {view} FORMAT TabSeparated",
            settings=[("user", user)],
            exitcode=exitcode,
            message=message,
        )

    with And(
        "I grant privileges to definer user on source tables and target table",
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
        "I check that user can select from view if definer has SELECT privilege for first source table in create query and target table"
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
        "I try to insert some data to first source table that triggers materialized view update"
    ):
        if (
            "INSERT" in definer_target_privileges
            and "SELECT" in definer_source_2_privileges
            and "SELECT" in definer_source_1_privileges
        ):
            node.query(
                f"INSERT INTO {source_table_1} SELECT number, number%3 FROM numbers(20)"
            )
        else:
            node.query(
                f"INSERT INTO {source_table_1} SELECT number, number%3 FROM numbers(20)",
                settings=[("user", definer)],
                exitcode=exitcode,
                message=message,
            )


@TestFeature
@Name("joins")
def feature(self, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
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

    privileges = [
        "SELECT",
        "INSERT",
        "NONE",
    ]

    with Pool(5) as executor:
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
            test_name = f"{definer_source_1_privileges}_{definer_source_2_privileges}_{definer_source_3_privileges}_{definer_target_privileges}_({join_option})_({grant_privilege.__name__})"
            test_name = (
                test_name.replace("[", "_")
                .replace("]", "_")
                .replace(")", "_")
                .replace("(", "_")
            )
            Scenario(
                test_name,
                test=multiple_source_table_with_join,
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
