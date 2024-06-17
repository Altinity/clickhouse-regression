from testflows.core import *
from testflows.asserts import error
from testflows.combinatorics import product, CoveringArray

from itertools import combinations

import rbac.helper.errors as errors
from rbac.requirements import *
from rbac.tests.sql_security.common import *

from helpers.common import getuid


@TestScenario
def cascade_mv_mv_mv(
    self,
    user_source_privileges,
    definer_one_source_privileges,
    definer_one_target_one_privileges,
    definer_two_target_one_privileges,
    definer_two_target_two_privileges,
    definer_three_target_two_privileges,
    definer_three_target_three_privileges,
    grant_privilege,
):
    """Check cascading materialized views with sql security:
    source table -> materialized view -> materialized view -> materialized view
    """

    node = self.context.node

    with Given("I source table for first materialized view in cascade"):
        source_table_name = "source_table_" + getuid()
        create_simple_MergeTree_table(table_name=source_table_name)

    with And("I create target table for first materialized view"):
        target_table_name_one = "target_table_one_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_one)

    with And("I create first definer user"):
        definer_user_one = "definer_one_" + getuid()
        create_user(user_name=definer_user_one)

    with And("I create first materialized view"):
        view_name_1 = "view_1_" + getuid()
        create_materialized_view(
            view_name=view_name_1,
            source_table_name=source_table_name,
            target_table_name=target_table_name_one,
            definer=definer_user_one,
            sql_security="DEFINER",
        )

    with And("I create target table for second materialized view"):
        target_table_name_two = "target_table_two_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_two)

    with And("I create second definer user"):
        definer_user_two = "definer_two_" + getuid()
        create_user(user_name=definer_user_two)

    with And("I create second materialized view"):
        view_name_2 = "view_2_" + getuid()
        create_materialized_view(
            view_name=view_name_2,
            source_table_name=target_table_name_one,
            target_table_name=target_table_name_two,
            definer=definer_user_two,
            sql_security="DEFINER",
        )

    with And("I create target table for third materialized view"):
        target_table_name_three = "target_table_three_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_three)

    with And("I create third definer user"):
        definer_user_three = "definer_three_" + getuid()
        create_user(user_name=definer_user_three)

    with And("I create third materialized view"):
        view_name_3 = "view_3_" + getuid()
        create_materialized_view(
            view_name=view_name_3,
            source_table_name=target_table_name_two,
            target_table_name=target_table_name_three,
            definer=definer_user_three,
            sql_security="DEFINER",
        )

    with And("I create new user"):
        new_user = "new_user_" + getuid()
        create_user(user_name=new_user)

    with And("I grant privileges to new user"):
        grant_privilege(
            privileges=user_source_privileges, object=source_table_name, user=new_user
        )

    with And(
        "I grant privileges to all three definer users to their source and target tables"
    ):
        grant_privilege(
            privileges=definer_one_source_privileges,
            object=source_table_name,
            user=definer_user_one,
        )
        grant_privilege(
            privileges=definer_one_target_one_privileges,
            object=target_table_name_one,
            user=definer_user_one,
        )
        grant_privilege(
            privileges=definer_two_target_one_privileges,
            object=target_table_name_one,
            user=definer_user_two,
        )
        grant_privilege(
            privileges=definer_two_target_two_privileges,
            object=target_table_name_two,
            user=definer_user_two,
        )
        grant_privilege(
            privileges=definer_three_target_two_privileges,
            object=target_table_name_two,
            user=definer_user_three,
        )
        grant_privilege(
            privileges=definer_three_target_three_privileges,
            object=target_table_name_three,
            user=definer_user_three,
        )

    with And("I try to insert into source table with new user"):
        if (
            # "SELECT" in user_source_privileges
            "INSERT" in user_source_privileges
            and "SELECT" in definer_one_source_privileges
            and "INSERT" in definer_one_target_one_privileges
            # and "SELECT" in definer_one_target_one_privileges
            and "SELECT" in definer_two_target_one_privileges
            # and "SELECT" in definer_two_target_two_privileges
            and "INSERT" in definer_two_target_two_privileges
            and "SELECT" in definer_three_target_two_privileges
            and "INSERT" in definer_three_target_three_privileges
        ):
            node.query(
                f"INSERT INTO {source_table_name} VALUES (1), (2), (3)",
                settings=[("user", new_user)],
            )
        else:
            exitcode, message = 241, f"Exception:"
            node.query(
                f"INSERT INTO {source_table_name} VALUES (1), (2), (3)",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )


@TestFeature
@Name("cascading views")
def feature(self, node="clickhouse1"):
    """Test cascading views with different sql security options."""
    self.context.node = self.context.cluster.node(node)
    grant_privileges = [grant_privileges_directly, grant_privileges_via_role]
    privileges = ("SELECT", "INSERT", "ALTER", "CREATE", "NONE")

    if not self.context.stress:
        privileges = ("SELECT", "INSERT", "NONE")
        grant_privileges = [grant_privileges_directly]

    privileges = list(combinations(privileges, 2)) + [("NONE",)]

    combinations_dict = {
        "user_source_privileges": privileges,
        "definer_one_source_privileges": privileges,
        "definer_one_target_one_privileges": privileges,
        "definer_two_target_one_privileges": privileges,
        "definer_two_target_two_privileges": privileges,
        "definer_three_target_two_privileges": privileges,
        "definer_three_target_three_privileges": privileges,
        "grant_privilege": grant_privileges,
    }

    covering_array = CoveringArray(combinations_dict, strength=5)

    privileges_combinations = [
        [
            item["user_source_privileges"],
            item["definer_one_source_privileges"],
            item["definer_one_target_one_privileges"],
            item["definer_two_target_one_privileges"],
            item["definer_two_target_two_privileges"],
            item["definer_three_target_two_privileges"],
            item["definer_three_target_three_privileges"],
            item["grant_privilege"],
        ]
        for item in covering_array
    ]

    with Pool(7) as executor:
        for (
            user_source_privileges,
            definer_one_source_privileges,
            definer_one_target_one_privileges,
            definer_two_target_one_privileges,
            definer_two_target_two_privileges,
            definer_three_target_two_privileges,
            definer_three_target_three_privileges,
            grant_privilege,
        ) in privileges_combinations:
            test_name = f"cascade_mv_mv_mv_{user_source_privileges}_{definer_one_source_privileges}_{definer_one_target_one_privileges}_{definer_two_target_one_privileges}_{definer_two_target_two_privileges}_{definer_three_target_two_privileges}_{definer_three_target_three_privileges}_{grant_privilege.__name__}"
            test_name = test_name.replace("[", "_").replace("]", "_")
            Scenario(
                test_name,
                description=f"""
                User source privileges: {user_source_privileges}
                Definer one source privileges: {definer_one_source_privileges}
                Definer one target one privileges: {definer_one_target_one_privileges}
                Definer two target one privileges: {definer_two_target_one_privileges}
                Definer two target two privileges: {definer_two_target_two_privileges}
                Definer three target two privileges: {definer_three_target_two_privileges}
                Definer three target three privileges: {definer_three_target_three_privileges}     
                """,
                test=cascade_mv_mv_mv,
                parallel=True,
                executor=executor,
            )(
                user_source_privileges=user_source_privileges,
                definer_one_source_privileges=definer_one_source_privileges,
                definer_one_target_one_privileges=definer_one_target_one_privileges,
                definer_two_target_one_privileges=definer_two_target_one_privileges,
                definer_two_target_two_privileges=definer_two_target_two_privileges,
                definer_three_target_two_privileges=definer_three_target_two_privileges,
                definer_three_target_three_privileges=definer_three_target_three_privileges,
                grant_privilege=grant_privilege,
            )
        join()
