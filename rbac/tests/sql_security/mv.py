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
    definer_view_source_table_privilege,
    definer_view_target_table_privilege,
    user_source_table_privilege,
    user_target_table_privilege,
    view_user_privilege,
    definer_user,
    user_name,
    view_name,
    node,
    expected_data=None,
):
    """Check select from view with given privileges."""
    if (
        "SELECT" in view_user_privilege
        and "SELECT" in definer_view_source_table_privilege
        and "SELECT" in definer_view_target_table_privilege
    ):
        result = node.query(
            f"SELECT * FROM {view_name} ORDER BY tuple(*) FORMAT TabSeparated",
            settings=[("user", user_name)],
        )
        if expected_data is not None:
            assert result.output == expected_data
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
    definer_view_source_table_privilege,
    definer_view_target_table_privilege,
    user_source_table_privilege,
    user_target_table_privilege,
    view_user_privilege,
    definer_user,
    user_name,
    view_name,
    node,
    data_before_insert=None,
):
    """Check insert into view with given privileges."""
    if (
        "INSERT" in view_user_privilege
        and "INSERT" in definer_view_target_table_privilege
    ):

        result = node.query(
            f"INSERT INTO {view_name} VALUES (1)",
            settings=[("user", user_name)],
        )
        if data_before_insert is not None:
            assert result.output != data_before_insert
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


@TestStep(Then)
def check_insert_into_source_table(
    self,
    definer_view_source_table_privilege,
    definer_view_target_table_privilege,
    user_source_table_privilege,
    user_target_table_privilege,
    view_user_privilege,
    definer_user,
    user_name,
    source_table_name,
    node,
    data_before_insert=None,
):
    """Check insert into mv source table."""

    if (
        ("INSERT" in view_user_privilege)
        and ("INSERT" in definer_view_target_table_privilege)
        and ("INSERT" in user_source_table_privilege)
    ):
        result = node.query(
            f"INSERT INTO {source_table_name} VALUES (1)",
            settings=[("user", user_name)],
        )
        assert result.output != data_before_insert
    else:
        if "INSERT" not in view_user_privilege or "INSERT" not in user_source_table_privilege:
            exitcode, message = errors.not_enough_privileges(name=f"{user_name}")
        else:
            exitcode, message = errors.not_enough_privileges(name=f"{definer_user}")
        node.query(
            f"INSERT INTO {source_table_name} VALUES (1)",
            settings=[("user", user_name)],
            exitcode=exitcode,
            message=message,
        )


@TestScenario
def check_materialized_view_with_definer(
    self,
    definer_view_source_table_privilege,
    definer_view_target_table_privilege,
    user_source_table_privilege,
    user_target_table_privilege,
    user_view_privilege,
    grant_privilege,
):
    """Check that I can perform `create` and `insert` operations as a
    user with privileges limited to a materialized view. The materialized
    view must have been created with a definer who has sufficient
    privileges for these operations."""

    node = self.context.node

    with Given("I create definer user"):
        user_name_definer = "definer_user_" + getuid()
        create_user(node=node, user_name=user_name_definer)

    with And("I create mv source table and insert data"):
        source_table_name = "source_table_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=source_table_name)
        insert_data_from_numbers(node=node, table_name=source_table_name)
        data = node.query(
            f"SELECT * FROM {source_table_name} ORDER BY tuple(*) FORMAT TabSeparated"
        ).output

    with And("I create mv target table"):
        mv_target_table_name = "mv_target_table_" + getuid()
        create_simple_MergeTree_table(node=node, table_name=mv_target_table_name)

    with And("I create materialized view and populate it with data"):
        view_name = "materialized_view_" + getuid()
        create_materialized_view(
            node=node,
            view_name=view_name,
            mv_table_name=mv_target_table_name,
            select_table_name=source_table_name,
            definer=user_name_definer,
            sql_security="DEFINER",
        )
        populate_mv_table(
            node=node, mv_table_name=mv_target_table_name, table_name=source_table_name
        )

    with And(
        "I grant privileges to source and target tables to definer user either directly or via role"
    ):
        grant_privilege(
            node=node,
            privileges=definer_view_source_table_privilege,
            object=source_table_name,
            user=user_name_definer,
        )
        grant_privilege(
            node=node,
            privileges=definer_view_target_table_privilege,
            object=mv_target_table_name,
            user=user_name_definer,
        )

    with When(
        "I create second user and grant privileges on source and destination tables"
    ):
        select_user_name = "select_user_" + getuid()
        create_user(node=node, user_name=select_user_name)

        grant_privilege(
            node=node,
            privileges=user_source_table_privilege,
            object=source_table_name,
            user=select_user_name,
        )
        grant_privilege(
            node=node,
            privileges=user_target_table_privilege,
            object=mv_target_table_name,
            user=select_user_name,
        )

    with And(
        "I grant privilege on materialized view to second user either directly or via role"
    ):
        grant_privilege(
            node=node,
            privileges=user_view_privilege,
            object=view_name,
            user=select_user_name,
        )

    with Then("I try to select from materialized view with second user"):
        check_select_from_mv(
            node=node,
            definer_user=user_name_definer,
            user_name=select_user_name,
            view_name=view_name,
            definer_view_source_table_privilege=definer_view_source_table_privilege,
            definer_view_target_table_privilege=definer_view_target_table_privilege,
            user_source_table_privilege=user_source_table_privilege,
            user_target_table_privilege=user_target_table_privilege,
            view_user_privilege=user_view_privilege,
            expected_data=data,
        )

    with And("I try to insert into materialized view with second user"):
        check_insert_into_mv(
            node=node,
            definer_user=user_name_definer,
            user_name=select_user_name,
            view_name=view_name,
            definer_view_source_table_privilege=definer_view_source_table_privilege,
            definer_view_target_table_privilege=definer_view_target_table_privilege,
            user_source_table_privilege=user_source_table_privilege,
            user_target_table_privilege=user_target_table_privilege,
            view_user_privilege=user_view_privilege,
            data_before_insert=data,
        )

    with And(
        "I try to insert into source table, which triggers materialized view update"
    ):
        check_insert_into_source_table(
            node=node,
            definer_user=user_name_definer,
            user_name=select_user_name,
            source_table_name=source_table_name,
            definer_view_source_table_privilege=definer_view_source_table_privilege,
            definer_view_target_table_privilege=definer_view_target_table_privilege,
            user_source_table_privilege=user_source_table_privilege,
            user_target_table_privilege=user_target_table_privilege,
            view_user_privilege=user_view_privilege,
            data_before_insert=data,
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
    grant_privileges = [grant_privileges_directly, grant_privileges_via_role]

    if not self.context.stress:
        privileges = ["NONE", "SELECT", "INSERT"]
        grant_privileges = [grant_privileges_directly]

    privilege_combinations = list(combinations(privileges, 1)) + [["NONE"]]

    definer_view_source_table_privileges = privilege_combinations
    definer_view_target_table_privileges = privilege_combinations
    user_source_table_privileges = privilege_combinations
    user_target_table_privileges = privilege_combinations
    user_view_privileges = privilege_combinations

    with Pool(10) as executor:
        for (
            definer_view_source_table_privilege,
            definer_view_target_table_privilege,
            user_source_table_privilege,
            user_target_table_privilege,
            user_view_privilege,
            grant_privilege,
        ) in product(
            definer_view_source_table_privileges,
            definer_view_target_table_privileges,
            user_source_table_privileges,
            user_target_table_privileges,
            user_view_privileges,
            grant_privileges,
        ):
            Scenario(
                name=f"{definer_view_source_table_privilege}, {definer_view_target_table_privilege}, {user_source_table_privilege}, {user_target_table_privilege}, {user_view_privilege}",
                test=check_materialized_view_with_definer,
                parallel=True,
                executor=executor,
            )(
                definer_view_source_table_privilege=definer_view_source_table_privilege,
                definer_view_target_table_privilege=definer_view_target_table_privilege,
                user_source_table_privilege=user_source_table_privilege,
                user_target_table_privilege=user_target_table_privilege,
                user_view_privilege=user_view_privilege,
                grant_privilege=grant_privilege,
            )
        join()


@TestFeature
@Name("materialized view with definer")
@Requirements(
    RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_CreateMaterializedView("1.0"),
)
def feature(self, node="clickhouse1"):
    """Check usage of materialized views that were created with definers."""
    self.context.node = self.context.cluster.node("clickhouse1")

    Scenario(run=materialized_view_with_definer)
