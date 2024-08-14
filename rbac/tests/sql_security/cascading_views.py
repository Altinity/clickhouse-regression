from testflows.core import *
from testflows.combinatorics import CoveringArray, combinations

from rbac.requirements import *
from rbac.tests.sql_security.common import *

from helpers.common import getuid


@TestScenario
def cascade_mv_definer_mv_definer_mv_definer(
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
    """
    Test privileges for different operations on cascading view:
    source table -> MV with definer -> MV with definer -> MV with definer
    """
    node = self.context.node

    with Given("source table for the first MV in cascade"):
        source_table_name = "source_table_" + getuid()
        create_simple_MergeTree_table(table_name=source_table_name)

    with And("target table and definer user for the first MV"):
        target_table_name_one = "target_table_one_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_one)
        definer_user_one = "definer_one_" + getuid()
        create_user(user_name=definer_user_one)

    with And("first MV"):
        view_name_1 = "view_one_" + getuid()
        create_materialized_view(
            view_name=view_name_1,
            source_table_name=source_table_name,
            target_table_name=target_table_name_one,
            definer=definer_user_one,
            sql_security="DEFINER",
        )

    with And("target table and definer user for the second MV"):
        target_table_name_two = "target_table_two_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_two)
        definer_user_two = "definer_two_" + getuid()
        create_user(user_name=definer_user_two)

    with And("second MV"):
        view_name_2 = "view_two_" + getuid()
        create_materialized_view(
            view_name=view_name_2,
            source_table_name=target_table_name_one,
            target_table_name=target_table_name_two,
            definer=definer_user_two,
            sql_security="DEFINER",
        )

    with And("target table and definer user for the third MV"):
        target_table_name_three = "target_table_three_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_three)
        definer_user_three = "definer_three_" + getuid()
        create_user(user_name=definer_user_three)

    with And("third MV"):
        view_name_3 = "view_three_" + getuid()
        create_materialized_view(
            view_name=view_name_3,
            source_table_name=target_table_name_two,
            target_table_name=target_table_name_three,
            definer=definer_user_three,
            sql_security="DEFINER",
        )

    with And(
        "new user to test required privileges for different operations with cascading view"
    ):
        new_user = "new_user_" + getuid()
        create_user(user_name=new_user)

    with And(
        f"grant following privileges to new user for source table: {user_source_privileges}"
    ):
        grant_privilege(
            privileges=user_source_privileges, object=source_table_name, user=new_user
        )

    with And(
        "grant privileges to all three definer users on their source and target tables"
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

    with And(
        """check that following set of grants allows to insert into source table:
        - INSERT on source table for user, 
        - SELECT on source table for definer one,
        - INSERT on target table one for definer one, 
        - SELECT on target table one for definer two,
        - INSERT on target table two for definer two, 
        - SELECT on target table two for definer three,
        - INSERT on target table three for definer three
        otherwise expect exception"""
    ):
        if (
            "INSERT" in user_source_privileges
            and "SELECT" in definer_one_source_privileges
            and "INSERT" in definer_one_target_one_privileges
            and "SELECT" in definer_two_target_one_privileges
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

    with And("grant SELECT privilege on the third MV to new user"):
        grant_privilege(privileges=["SELECT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to select from third MV:
        - SELECT on third MV for new user
        - SELECT on second target table (third MV's source table) for definer three 
        - SELECT on third target table for definer three
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if (
            "SELECT" in definer_three_target_two_privileges
            and "SELECT" in definer_three_target_three_privileges
        ):
            node.query(f"SELECT * FROM {view_name_3}", settings=[("user", new_user)])
        else:
            node.query(
                f"SELECT * FROM {view_name_3}",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )

    with And("grant INSERT privilege on the third MV to new user"):
        grant_privilege(privileges=["INSERT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to insert into third MV:
        - INSERT on third MV for new user
        - INSERT on third MV's target table for definer three
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if "INSERT" in definer_three_target_three_privileges:
            node.query(
                f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
                settings=[("user", new_user)],
            )
        else:
            node.query(
                f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def cascade_mv_mv_definer_mv_definer(
    self,
    user_source_privileges,
    definer_two_target_one_privileges,
    definer_two_target_two_privileges,
    definer_three_target_two_privileges,
    definer_three_target_three_privileges,
    grant_privilege,
):
    """
    Test privileges for different operations on cascading view:
    source table -> MV without sql security specified-> MV with definer -> MV with definer
    """
    node = self.context.node

    with Given("source table for the first MV in cascade"):
        source_table_name = "source_table_" + getuid()
        create_simple_MergeTree_table(table_name=source_table_name)

    with And("target table for the first MV"):
        target_table_name_one = "target_table_one_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_one)

    with And("first MV"):
        view_name_1 = "view_one_" + getuid()
        create_materialized_view(
            view_name=view_name_1,
            source_table_name=source_table_name,
            target_table_name=target_table_name_one,
        )

    with And("target table and definer user for the second MV"):
        target_table_name_two = "target_table_two_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_two)
        definer_user_two = "definer_two_" + getuid()
        create_user(user_name=definer_user_two)

    with And("second MV"):
        view_name_2 = "view_two_" + getuid()
        create_materialized_view(
            view_name=view_name_2,
            source_table_name=target_table_name_one,
            target_table_name=target_table_name_two,
            definer=definer_user_two,
            sql_security="DEFINER",
        )

    with And("target table and definer user for the third MV"):
        target_table_name_three = "target_table_three_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_three)
        definer_user_three = "definer_three_" + getuid()
        create_user(user_name=definer_user_three)

    with And("third MV"):
        view_name_3 = "view_three_" + getuid()
        create_materialized_view(
            view_name=view_name_3,
            source_table_name=target_table_name_two,
            target_table_name=target_table_name_three,
            definer=definer_user_three,
            sql_security="DEFINER",
        )

    with And(
        "new user to test required privileges for different operations with cascading view"
    ):
        new_user = "new_user_" + getuid()
        create_user(user_name=new_user)

    with And(
        f"grant following privileges to new user on source table: {user_source_privileges}"
    ):
        grant_privilege(
            privileges=user_source_privileges, object=source_table_name, user=new_user
        )

    with And("grant privileges to all definer users on their source and target tables"):
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

    with And(
        """check that following set of grants allows to insert into source table:
        - INSERT on source table for user, 
        - SELECT on source table for user,
        - SELECT on target table one for definer two,
        - INSERT on target table two for definer two, 
        - SELECT on target table two for definer three,
        - INSERT on target table three for definer three
        otherwise expect exception"""
    ):
        if (
            "INSERT" in user_source_privileges
            and "SELECT" in user_source_privileges
            and "SELECT" in definer_two_target_one_privileges
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

    with And("grant SELECT privilege on the third MV to new user"):
        grant_privilege(privileges=["SELECT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to select from third MV:
        - SELECT on third MV for new user
        - SELECT on second target table (third MV's source table) for definer three 
        - SELECT on third target table for definer three
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if (
            "SELECT" in definer_three_target_two_privileges
            and "SELECT" in definer_three_target_three_privileges
        ):
            node.query(f"SELECT * FROM {view_name_3}", settings=[("user", new_user)])
        else:
            node.query(
                f"SELECT * FROM {view_name_3}",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )

    with And("grant INSERT privilege on the third MV to new user"):
        grant_privilege(privileges=["INSERT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to insert into third MV:
        - INSERT on third MV for new user
        - INSERT on third MV's target table for definer three
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if "INSERT" in definer_three_target_three_privileges:
            node.query(
                f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
                settings=[("user", new_user)],
            )
        else:
            node.query(
                f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def cascade_mv_definer_mv_mv_definer(
    self,
    user_source_privileges,
    definer_one_source_privileges,
    definer_one_target_one_privileges,
    definer_three_target_two_privileges,
    definer_three_target_three_privileges,
    grant_privilege,
):
    """
    Test privileges for different operations on cascading view:
    source table -> MV with definer -> MV without sql security specified -> MV with definer
    """
    node = self.context.node

    with Given("source table for the first MV in cascade"):
        source_table_name = "source_table_" + getuid()
        create_simple_MergeTree_table(table_name=source_table_name)

    with And("target table and definer user for the first MV"):
        target_table_name_one = "target_table_one_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_one)
        definer_user_one = "definer_one_" + getuid()
        create_user(user_name=definer_user_one)

    with And("first MV"):
        view_name_1 = "view_one_" + getuid()
        create_materialized_view(
            view_name=view_name_1,
            source_table_name=source_table_name,
            target_table_name=target_table_name_one,
            definer=definer_user_one,
            sql_security="DEFINER",
        )

    with And("target table for the second MV"):
        target_table_name_two = "target_table_two_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_two)

    with And("second MV"):
        view_name_2 = "view_two_" + getuid()
        create_materialized_view(
            view_name=view_name_2,
            source_table_name=target_table_name_one,
            target_table_name=target_table_name_two,
        )

    with And("target table and definer user for the third MV"):
        target_table_name_three = "target_table_three_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_three)
        definer_user_three = "definer_three_" + getuid()
        create_user(user_name=definer_user_three)

    with And("third MV"):
        view_name_3 = "view_three_" + getuid()
        create_materialized_view(
            view_name=view_name_3,
            source_table_name=target_table_name_two,
            target_table_name=target_table_name_three,
            definer=definer_user_three,
            sql_security="DEFINER",
        )

    with And(
        "new user to test required privileges for different operations with cascading view"
    ):
        new_user = "new_user_" + getuid()
        create_user(user_name=new_user)

    with And(
        f"grant following privileges to new user on source table: {user_source_privileges}"
    ):
        grant_privilege(
            privileges=user_source_privileges, object=source_table_name, user=new_user
        )

    with And("grant privileges to all definer users on their source and target tables"):
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
            privileges=definer_three_target_two_privileges,
            object=target_table_name_two,
            user=definer_user_three,
        )
        grant_privilege(
            privileges=definer_three_target_three_privileges,
            object=target_table_name_three,
            user=definer_user_three,
        )

    with And(
        """check that following set of grants allows to insert into source table:
        - INSERT on source table for user, 
        - SELECT on source table for definer one,
        - SELECT on target table one for definer one,
        - INSERT on target table one for definer one, 
        - SELECT on target table two for definer three,
        - INSERT on target table three for definer three
        otherwise expect exception"""
    ):
        if (
            "INSERT" in user_source_privileges
            and "SELECT" in definer_one_source_privileges
            and "SELECT" in definer_one_target_one_privileges
            and "INSERT" in definer_one_target_one_privileges
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

    with And("grant SELECT privilege on the third MV to new user"):
        grant_privilege(privileges=["SELECT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to select from third MV:
        - SELECT on third MV for new user
        - SELECT on second target table (third MV's source table) for definer three 
        - SELECT on third target table for definer three
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if (
            "SELECT" in definer_three_target_two_privileges
            and "SELECT" in definer_three_target_three_privileges
        ):
            node.query(f"SELECT * FROM {view_name_3}", settings=[("user", new_user)])
        else:
            node.query(
                f"SELECT * FROM {view_name_3}",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )

    with And("grant INSERT privilege on the third MV to new user"):
        grant_privilege(privileges=["INSERT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to insert into third MV:
        - INSERT on third MV for new user
        - INSERT on third MV's target table for definer three
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if "INSERT" in definer_three_target_three_privileges:
            node.query(
                f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
                settings=[("user", new_user)],
            )
        else:
            node.query(
                f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def cascade_mv_mv_mv_definer(
    self,
    user_source_privileges,
    user_target_one_privileges,
    definer_three_target_two_privileges,
    definer_three_target_three_privileges,
    grant_privilege,
):
    """
    Test privileges for different operations on cascading view:
    source table -> MV without sql security specified -> MV without sql security specified -> MV with definer
    """
    node = self.context.node

    with Given("source table for the first MV in cascade"):
        source_table_name = "source_table_" + getuid()
        create_simple_MergeTree_table(table_name=source_table_name)

    with And("target table for the first MV"):
        target_table_name_one = "target_table_one_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_one)

    with And("first MV"):
        view_name_1 = "view_one_" + getuid()
        create_materialized_view(
            view_name=view_name_1,
            source_table_name=source_table_name,
            target_table_name=target_table_name_one,
        )

    with And("target table for the second MV"):
        target_table_name_two = "target_table_two_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_two)

    with And("second MV"):
        view_name_2 = "view_two_" + getuid()
        create_materialized_view(
            view_name=view_name_2,
            source_table_name=target_table_name_one,
            target_table_name=target_table_name_two,
        )

    with And("target table and definer user for the third MV"):
        target_table_name_three = "target_table_three_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_three)
        definer_user_three = "definer_three_" + getuid()
        create_user(user_name=definer_user_three)

    with And("third MV"):
        view_name_3 = "view_three_" + getuid()
        create_materialized_view(
            view_name=view_name_3,
            source_table_name=target_table_name_two,
            target_table_name=target_table_name_three,
            definer=definer_user_three,
            sql_security="DEFINER",
        )

    with And(
        "new user to test required privileges for different operations with cascading view"
    ):
        new_user = "new_user_" + getuid()
        create_user(user_name=new_user)

    with And("grant privileges to new user"):
        grant_privilege(
            privileges=user_source_privileges, object=source_table_name, user=new_user
        )
        grant_privilege(
            privileges=user_target_one_privileges,
            object=target_table_name_one,
            user=new_user,
        )

    with And(
        "grant privileges to third definer user on third MV's source and target tables"
    ):
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

    with And(
        """check that following set of grants allows to insert into source table:
        - INSERT on source table for user, 
        - SELECT on source table for user,
        - SELECT on target table one for user,
        - SELECT on target table two for definer three,
        - INSERT on target table three for definer three
        otherwise expect exception"""
    ):
        if (
            "INSERT" in user_source_privileges
            and "SELECT" in user_source_privileges
            and "SELECT" in user_target_one_privileges
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

    with And("grant SELECT privilege on the third MV to new user"):
        grant_privilege(privileges=["SELECT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to select from third MV:
        - SELECT on third MV for new user
        - SELECT on second target table (third MV's source table) for definer three 
        - SELECT on third target table for definer three
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if (
            "SELECT" in definer_three_target_two_privileges
            and "SELECT" in definer_three_target_three_privileges
        ):
            node.query(f"SELECT * FROM {view_name_3}", settings=[("user", new_user)])
        else:
            node.query(
                f"SELECT * FROM {view_name_3}",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )

    with And("grant INSERT privilege on the third MV to new user"):
        grant_privilege(privileges=["INSERT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to insert into third MV:
        - INSERT on third MV for new user
        - INSERT on third MV's target table for definer three
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if "INSERT" in definer_three_target_three_privileges:
            node.query(
                f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
                settings=[("user", new_user)],
            )
        else:
            node.query(
                f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )


@TestScenario
def cascade_mv_mv_definer_mv(
    self,
    user_source_privileges,
    user_target_two_privileges,
    definer_two_target_one_privileges,
    definer_two_target_two_privileges,
    grant_privilege,
):
    """
    Test privileges for different operations on cascading view:
    source table -> MV without sql security specified-> MV with definer -> MV without sql security specified
    """
    node = self.context.node

    with Given("source table for the first MV in cascade"):
        source_table_name = "source_table_" + getuid()
        create_simple_MergeTree_table(table_name=source_table_name)

    with And("target table for the first MV"):
        target_table_name_one = "target_table_one_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_one)

    with And("first MV"):
        view_name_1 = "view_one_" + getuid()
        create_materialized_view(
            view_name=view_name_1,
            source_table_name=source_table_name,
            target_table_name=target_table_name_one,
        )

    with And("target table and definer user for the second MV"):
        target_table_name_two = "target_table_two_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_two)
        definer_user_two = "definer_two_" + getuid()
        create_user(user_name=definer_user_two)

    with And("second MV"):
        view_name_2 = "view_two_" + getuid()
        create_materialized_view(
            view_name=view_name_2,
            source_table_name=target_table_name_one,
            target_table_name=target_table_name_two,
            definer=definer_user_two,
            sql_security="DEFINER",
        )

    with And("target table for the third MV"):
        target_table_name_three = "target_table_three_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_three)

    with And("third MV"):
        view_name_3 = "view_three_" + getuid()
        create_materialized_view(
            view_name=view_name_3,
            source_table_name=target_table_name_two,
            target_table_name=target_table_name_three,
        )

    with And(
        "new user to test required privileges for different operations with cascading view"
    ):
        new_user = "new_user_" + getuid()
        create_user(user_name=new_user)

    with And("grant privileges to new user"):
        grant_privilege(
            privileges=user_source_privileges, object=source_table_name, user=new_user
        )
        grant_privilege(
            privileges=user_target_two_privileges,
            object=target_table_name_two,
            user=new_user,
        )

    with And(
        "grant privileges to second definer user on second MV's source and target tables"
    ):
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

    with And(
        """check that following set of grants allows to insert into source table:
        - INSERT on source table for user, 
        - SELECT on source table for user,
        - SELECT on target table one for definer two,
        - SELECT on target table two for definer two,
        - INSERT on target table two for definer two, 
        otherwise expect exception"""
    ):
        if (
            "INSERT" in user_source_privileges
            and "SELECT" in user_source_privileges
            and "SELECT" in definer_two_target_one_privileges
            and "SELECT" in definer_two_target_two_privileges
            and "INSERT" in definer_two_target_two_privileges
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

    with And("grant SELECT privilege on the third MV to new user"):
        grant_privilege(privileges=["SELECT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to select from third MV:
        - SELECT on third MV for new user
        - SELECT on target table two (third MV's source table) for new user
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if "SELECT" in user_target_two_privileges:
            node.query(f"SELECT * FROM {view_name_3}", settings=[("user", new_user)])
        else:
            node.query(
                f"SELECT * FROM {view_name_3}",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )

    with And("grant INSERT privilege on the third MV to new user"):
        grant_privilege(privileges=["INSERT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to insert into third MV:
        - INSERT on third MV for new user"""
    ):
        node.query(
            f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
            settings=[("user", new_user)],
        )


@TestScenario
def cascade_mv_definer_mv_definer_mv(
    self,
    user_source_privileges,
    user_target_two_privileges,
    definer_one_source_privileges,
    definer_one_target_one_privileges,
    definer_two_target_one_privileges,
    definer_two_target_two_privileges,
    grant_privilege,
):
    """
    Test privileges for different operations on cascading view:
    source table -> MV with definer -> MV with definer -> MV without sql security specified
    """
    node = self.context.node

    with Given("source table for the first MV in cascade"):
        source_table_name = "source_table_" + getuid()
        create_simple_MergeTree_table(table_name=source_table_name)

    with And("target table and definer user for the first MV"):
        target_table_name_one = "target_table_one_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_one)
        definer_user_one = "definer_one_" + getuid()
        create_user(user_name=definer_user_one)

    with And("first MV"):
        view_name_1 = "view_one_" + getuid()
        create_materialized_view(
            view_name=view_name_1,
            source_table_name=source_table_name,
            target_table_name=target_table_name_one,
            definer=definer_user_one,
            sql_security="DEFINER",
        )

    with And("target table and definer user for the second MV"):
        target_table_name_two = "target_table_two_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_two)
        definer_user_two = "definer_two_" + getuid()
        create_user(user_name=definer_user_two)

    with And("second MV"):
        view_name_2 = "view_two_" + getuid()
        create_materialized_view(
            view_name=view_name_2,
            source_table_name=target_table_name_one,
            target_table_name=target_table_name_two,
            definer=definer_user_two,
            sql_security="DEFINER",
        )

    with And("target table for the third MV"):
        target_table_name_three = "target_table_three_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_three)

    with And("third MV"):
        view_name_3 = "view_three_" + getuid()
        create_materialized_view(
            view_name=view_name_3,
            source_table_name=target_table_name_two,
            target_table_name=target_table_name_three,
        )

    with And(
        "new user to test required privileges for different operations with cascading view"
    ):
        new_user = "new_user_" + getuid()
        create_user(user_name=new_user)

    with And(f"grant privileges to new user on source table and target table two"):
        grant_privilege(
            privileges=user_source_privileges, object=source_table_name, user=new_user
        )
        grant_privilege(
            privileges=user_target_two_privileges,
            object=target_table_name_two,
            user=new_user,
        )

    with And("grant privileges to all definer users on their source and target tables"):
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

    with And(
        """check that following set of grants allows to insert into source table:
        - INSERT on source table for user, 
        - SELECT on source table for definer one,
        - INSERT on target table one for definer one, 
        - SELECT on target table one for definer two,
        - SELECT on target table two for definer two,
        - INSERT on target table two for definer two, 
        otherwise expect exception"""
    ):
        if (
            "INSERT" in user_source_privileges
            and "SELECT" in definer_one_source_privileges
            and "INSERT" in definer_one_target_one_privileges
            and "SELECT" in definer_two_target_one_privileges
            and "SELECT" in definer_two_target_two_privileges
            and "INSERT" in definer_two_target_two_privileges
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

    with And("grant SELECT privilege on the third MV to new user"):
        grant_privilege(privileges=["SELECT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to select from third MV:
        - SELECT on third MV for new user
        - SELECT on second target table (third MV's source table) for new user
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if "SELECT" in user_target_two_privileges:
            node.query(f"SELECT * FROM {view_name_3}", settings=[("user", new_user)])
        else:
            node.query(
                f"SELECT * FROM {view_name_3}",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )

    with And("grant INSERT privilege on the third MV to new user"):
        grant_privilege(privileges=["INSERT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to insert into third MV:
        - INSERT on third MV for new user
        otherwise expect exception"""
    ):
        node.query(
            f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
            settings=[("user", new_user)],
        )


@TestScenario
def cascade_mv_definer_mv_mv(
    self,
    user_source_privileges,
    user_target_two_privileges,
    definer_one_source_privileges,
    definer_one_target_one_privileges,
    definer_one_target_two_privileges,
    grant_privilege,
):
    """
    Test privileges for different operations on cascading view:
    source table -> MV with definer -> MV without sql security specified -> MV without sql security specified
    """
    node = self.context.node

    with Given("source table for the first MV in cascade"):
        source_table_name = "source_table_" + getuid()
        create_simple_MergeTree_table(table_name=source_table_name)

    with And("target table and definer user for the first MV"):
        target_table_name_one = "target_table_one_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_one)
        definer_user_one = "definer_one_" + getuid()
        create_user(user_name=definer_user_one)

    with And("first MV"):
        view_name_1 = "view_one_" + getuid()
        create_materialized_view(
            view_name=view_name_1,
            source_table_name=source_table_name,
            target_table_name=target_table_name_one,
            definer=definer_user_one,
            sql_security="DEFINER",
        )

    with And("target table for the second MV"):
        target_table_name_two = "target_table_two_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_two)

    with And("second MV"):
        view_name_2 = "view_two_" + getuid()
        create_materialized_view(
            view_name=view_name_2,
            source_table_name=target_table_name_one,
            target_table_name=target_table_name_two,
        )

    with And("target table for the third MV"):
        target_table_name_three = "target_table_three_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_three)

    with And("third MV"):
        view_name_3 = "view_three_" + getuid()
        create_materialized_view(
            view_name=view_name_3,
            source_table_name=target_table_name_two,
            target_table_name=target_table_name_three,
        )

    with And(
        "new user to test required privileges for different operations with cascading view"
    ):
        new_user = "new_user_" + getuid()
        create_user(user_name=new_user)

    with And(f"grant privileges to new user on source table and target table two"):
        grant_privilege(
            privileges=user_source_privileges, object=source_table_name, user=new_user
        )
        grant_privilege(
            privileges=user_target_two_privileges,
            object=target_table_name_two,
            user=new_user,
        )

    with And(
        "grant privileges to first define user on first MV's source and target tables"
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
            privileges=definer_one_target_two_privileges,
            object=target_table_name_two,
            user=definer_user_one,
        )

    with And(
        """check that following set of grants allows to insert into source table:
        - INSERT on source table for user, 
        - SELECT on source table for definer one,
        - INSERT on target table one for definer one, 
        - SELECT on target table one for definer one,
        - SELECT on target table two for definer one,
        otherwise expect exception"""
    ):
        if (
            "INSERT" in user_source_privileges
            and "SELECT" in definer_one_source_privileges
            and "INSERT" in definer_one_target_one_privileges
            and "SELECT" in definer_one_target_one_privileges
            and "SELECT" in definer_one_target_two_privileges
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

    with And("grant SELECT privilege on the third MV to new user"):
        grant_privilege(privileges=["SELECT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to select from third MV:
        - SELECT on third MV for new user
        - SELECT on second target table (third MV's source table) for new user
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if "SELECT" in user_target_two_privileges:
            node.query(f"SELECT * FROM {view_name_3}", settings=[("user", new_user)])
        else:
            node.query(
                f"SELECT * FROM {view_name_3}",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )

    with And("grant INSERT privilege on the third MV to new user"):
        grant_privilege(privileges=["INSERT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to insert into third MV:
        - INSERT on third MV for new user
        otherwise expect exception"""
    ):
        node.query(
            f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
            settings=[("user", new_user)],
        )


@TestScenario
def cascade_mv_mv_mv(
    self,
    user_source_privileges,
    user_target_one_privileges,
    user_target_two_privileges,
    grant_privilege,
):
    """
    Test privileges for different operations on cascading view:
    source table -> MV without sql security specified -> MV without sql security specified -> MV without sql security specified
    """
    node = self.context.node

    with Given("source table for the first MV in cascade"):
        source_table_name = "source_table_" + getuid()
        create_simple_MergeTree_table(table_name=source_table_name)

    with And("target table for the first MV"):
        target_table_name_one = "target_table_one_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_one)

    with And("first MV"):
        view_name_1 = "view_one_" + getuid()
        create_materialized_view(
            view_name=view_name_1,
            source_table_name=source_table_name,
            target_table_name=target_table_name_one,
        )

    with And("target table for the second MV"):
        target_table_name_two = "target_table_two_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_two)

    with And("second MV"):
        view_name_2 = "view_two_" + getuid()
        create_materialized_view(
            view_name=view_name_2,
            source_table_name=target_table_name_one,
            target_table_name=target_table_name_two,
        )

    with And("target table for the third MV"):
        target_table_name_three = "target_table_three_" + getuid()
        create_simple_MergeTree_table(table_name=target_table_name_three)

    with And("third MV"):
        view_name_3 = "view_three_" + getuid()
        create_materialized_view(
            view_name=view_name_3,
            source_table_name=target_table_name_two,
            target_table_name=target_table_name_three,
        )

    with And(
        "new user to test required privileges for different operations with cascading view"
    ):
        new_user = "new_user_" + getuid()
        create_user(user_name=new_user)

    with And(f"grant privileges to new user on source table and target table two"):
        grant_privilege(
            privileges=user_source_privileges, object=source_table_name, user=new_user
        )
        grant_privilege(
            privileges=user_target_one_privileges,
            object=target_table_name_one,
            user=new_user,
        )
        grant_privilege(
            privileges=user_target_two_privileges,
            object=target_table_name_two,
            user=new_user,
        )

    with And(
        """check that following set of grants allows to insert into source table:
        - INSERT on source table for user, 
        - SELECT on source table for user,
        - SELECT on target table one for user,
        - SELECT on target table two for user,
        otherwise expect exception"""
    ):
        if (
            "INSERT" in user_source_privileges
            and "SELECT" in user_source_privileges
            and "SELECT" in user_target_one_privileges
            and "SELECT" in user_target_two_privileges
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

    with And("grant SELECT privilege on the third MV to new user"):
        grant_privilege(privileges=["SELECT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to select from third MV:
        - SELECT on third MV for new user
        - SELECT on second target table (third MV's source table) for new user
        otherwise expect exception"""
    ):
        exitcode, message = 241, f"Exception:"
        if "SELECT" in user_target_two_privileges:
            node.query(f"SELECT * FROM {view_name_3}", settings=[("user", new_user)])
        else:
            node.query(
                f"SELECT * FROM {view_name_3}",
                settings=[("user", new_user)],
                exitcode=exitcode,
                message=message,
            )

    with And("grant INSERT privilege on the third MV to new user"):
        grant_privilege(privileges=["INSERT"], object=view_name_3, user=new_user)

    with And(
        """check that following set of grants allows user to insert into third MV:
        - INSERT on third MV for new user
        otherwise expect exception"""
    ):
        node.query(
            f"INSERT INTO {view_name_3} VALUES (4), (5), (6)",
            settings=[("user", new_user)],
        )


@TestFeature
def check_cascade_mv_definer_mv_definer_mv_definer(self):
    """
    Run test for all possible combinations of privileges for cascading view:
    source table -> MV with definer -> MV with definer -> MV with definer
    """
    if self.context.stress:
        with Given("choices how privileges can be granted"):
            grant_privileges = define(
                "grant privileges",
                [grant_privileges_directly, grant_privileges_via_role],
                encoder=get_name,
            )

        with And("possible table privileges"):
            privileges = define(
                "privileges", ("SELECT", "INSERT", "ALTER", "CREATE", "NONE")
            )
    else:
        with Given("privileges are only granted directly"):
            grant_privileges = define(
                "grant privileges", [grant_privileges_directly], encoder=get_name
            )

        with And("only required privileges"):
            privileges = define("privileges", ("SELECT", "INSERT", "NONE"))

    with Given(
        "generate all possible pairs of privileges and add an option with no privileges"
    ):
        privilege_pairs = define(
            "privilege pairs", list(combinations(privileges, 2)) + [("NONE",)]
        )

    with And(
        "create dictionary for storing possible privileges for definer users and for user executing queries"
    ):
        combinations_dict = {}

        with By(
            "define privileges for the user executing queries for the source table of the first MV"
        ):
            combinations_dict["user_source_privileges"] = privilege_pairs
        with By(
            "define privileges for the first definer user for the source table of the first MV"
        ):
            combinations_dict["definer_one_source_privileges"] = privilege_pairs
        with By(
            "define privileges for the first definer user for the target table of the first MV"
        ):
            combinations_dict["definer_one_target_one_privileges"] = privilege_pairs
        with By(
            "define privileges for the second definer user for the target table of the first MV (which is the source table of the second MV)"
        ):
            combinations_dict["definer_two_target_one_privileges"] = privilege_pairs
        with By(
            "define privileges for the second definer user for the target table of the second MV"
        ):
            combinations_dict["definer_two_target_two_privileges"] = privilege_pairs
        with By(
            "define privileges for the third definer user for the target table of the second MV (which is the source table of the third MV)"
        ):
            combinations_dict["definer_three_target_two_privileges"] = privilege_pairs
        with By(
            "define privileges for the third definer user for the target table of the third MV"
        ):
            combinations_dict["definer_three_target_three_privileges"] = privilege_pairs
        with By("define the method of granting privileges"):
            combinations_dict["grant_privilege"] = grant_privileges

    with And(
        """using covering array with strength 6 to decrease the number of combinations.
        The strength of a covering array specifies the number of variables for which 
        all possible value combinations must appear at least once in the array."""
    ):
        covering_array = CoveringArray(combinations_dict, strength=6)

    with And(
        "creating a list of lists of privileges from the covering array with some combinations of privileges"
    ):
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
            test_name = f"user_source-{user_source_privileges},definer_one_source-{definer_one_source_privileges},definer_one_target_one-{definer_one_target_one_privileges},definer_two_target_one-{definer_two_target_one_privileges},definer_two_target_two-{definer_two_target_two_privileges},definer_three_target_two-{definer_three_target_two_privileges},definer_three_target_three-{definer_three_target_three_privileges},grant_privileges_option-{grant_privilege.__name__}"
            test_name = (
                test_name.replace("(", "_")
                .replace(")", "_")
                .replace(" ", "")
                .replace("'", "")
            )
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
                test=cascade_mv_definer_mv_definer_mv_definer,
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


@TestScenario
def check_cascade_mv_mv_definer_mv_definer(self):
    """
    Run test for all possible combinations of privileges for cascading view:
    source table -> MV without sql security specified-> MV with definer -> MV with definer
    """
    if self.context.stress:
        with Given("choices how privileges can be granted"):
            grant_privileges = define(
                "grant privileges",
                [grant_privileges_directly, grant_privileges_via_role],
                encoder=get_name,
            )

        with And("possible table privileges"):
            privileges = define(
                "privileges", ("SELECT", "INSERT", "ALTER", "CREATE", "NONE")
            )
    else:
        with Given("privileges are only granted directly"):
            grant_privileges = define(
                "grant privileges", [grant_privileges_directly], encoder=get_name
            )
            grant_privileges = [grant_privileges_directly]

        with And("only required privileges"):
            privileges = define("privileges", ("SELECT", "INSERT", "NONE"))

    with Given(
        "generate all possible pairs of privileges and add an option with no privileges"
    ):
        privilege_pairs = define(
            "privilege pairs", list(combinations(privileges, 2)) + [("NONE",)]
        )

    with And(
        "create dictionary for storing possible privileges for definer users and for user executing queries"
    ):
        combinations_dict = {}

        with By(
            "define privileges for the user executing queries for the source table of the first MV"
        ):
            combinations_dict["user_source_privileges"] = privilege_pairs
        with By(
            "define privileges for the second definer user for the target table of the first MV (which is the source table of the second MV)"
        ):
            combinations_dict["definer_two_target_one_privileges"] = privilege_pairs
        with By(
            "define privileges for the second definer user for the target table of the second MV"
        ):
            combinations_dict["definer_two_target_two_privileges"] = privilege_pairs
        with By(
            "define privileges for the third definer user for the target table of the second MV (which is the source table of the third MV)"
        ):
            combinations_dict["definer_three_target_two_privileges"] = privilege_pairs
        with By(
            "define privileges for the third definer user for the target table of the third MV"
        ):
            combinations_dict["definer_three_target_three_privileges"] = privilege_pairs
        with By("define the method of granting privileges"):
            combinations_dict["grant_privilege"] = grant_privileges

    with And(
        """using covering array with strength 5 to decrease the number of combinations.
        The strength of a covering array specifies the number of variables for which 
        all possible value combinations must appear at least once in the array."""
    ):
        covering_array = CoveringArray(combinations_dict, strength=5)

    with And(
        "creating a list of lists from covering array with some combinations of privileges"
    ):
        privileges_combinations = [
            [
                item["user_source_privileges"],
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
            definer_two_target_one_privileges,
            definer_two_target_two_privileges,
            definer_three_target_two_privileges,
            definer_three_target_three_privileges,
            grant_privilege,
        ) in privileges_combinations:
            test_name = f"user_source-{user_source_privileges},definer_two_target_one-{definer_two_target_one_privileges},definer_two_target_two-{definer_two_target_two_privileges},definer_three_target_two-{definer_three_target_two_privileges},definer_three_target_three-{definer_three_target_three_privileges},grant_privileges_option-{grant_privilege.__name__}"
            test_name = (
                test_name.replace("(", "_")
                .replace(")", "_")
                .replace(" ", "")
                .replace("'", "")
            )
            Scenario(
                test_name,
                description=f"""
                User source privileges: {user_source_privileges}
                Definer two target one privileges: {definer_two_target_one_privileges}
                Definer two target two privileges: {definer_two_target_two_privileges}
                Definer three target two privileges: {definer_three_target_two_privileges}
                Definer three target three privileges: {definer_three_target_three_privileges}     
                """,
                test=cascade_mv_mv_definer_mv_definer,
                parallel=True,
                executor=executor,
            )(
                user_source_privileges=user_source_privileges,
                definer_two_target_one_privileges=definer_two_target_one_privileges,
                definer_two_target_two_privileges=definer_two_target_two_privileges,
                definer_three_target_two_privileges=definer_three_target_two_privileges,
                definer_three_target_three_privileges=definer_three_target_three_privileges,
                grant_privilege=grant_privilege,
            )
        join()


@TestScenario
def check_cascade_mv_definer_mv_mv_definer(self):
    """
    Run test for all possible combinations of privileges for cascading view:
    source table -> MV with definer -> MV without sql security specified -> MV with definer
    """
    if self.context.stress:
        with Given("choices how privileges can be granted"):
            grant_privileges = define(
                "grant privileges",
                [grant_privileges_directly, grant_privileges_via_role],
                encoder=get_name,
            )

        with And("possible table privileges"):
            privileges = define(
                "privileges", ("SELECT", "INSERT", "ALTER", "CREATE", "NONE")
            )
    else:
        with Given("privileges are only granted directly"):
            grant_privileges = define(
                "grant privileges", [grant_privileges_directly], encoder=get_name
            )
            grant_privileges = [grant_privileges_directly]

        with And("only required privileges"):
            privileges = define("privileges", ("SELECT", "INSERT", "NONE"))

    with Given(
        "generate all possible pairs of privileges and add an option with no privileges"
    ):
        privilege_pairs = define(
            "privilege pairs", list(combinations(privileges, 2)) + [("NONE",)]
        )

    with And(
        "create dictionary for storing possible privileges for definer users and for user executing queries"
    ):
        combinations_dict = {}

        with By(
            "define privileges for the user executing queries for the source table of the first MV"
        ):
            combinations_dict["user_source_privileges"] = privilege_pairs
        with By(
            "define privileges for the first definer user for the source table of the first MV"
        ):
            combinations_dict["definer_one_source_privileges"] = privilege_pairs
        with By(
            "define privileges for the first definer user for the target table of the first MV"
        ):
            combinations_dict["definer_one_target_one_privileges"] = privilege_pairs
        with By(
            "define privileges for the third definer user for the target table of the second MV (which is the source table of the third MV)"
        ):
            combinations_dict["definer_three_target_two_privileges"] = privilege_pairs
        with By(
            "define privileges for the third definer user for the target table of the third MV"
        ):
            combinations_dict["definer_three_target_three_privileges"] = privilege_pairs
        with By("define the method of granting privileges"):
            combinations_dict["grant_privilege"] = grant_privileges

    with And(
        """using covering array with strength 5 to decrease the number of combinations.
        The strength of a covering array specifies the number of variables for which 
        all possible value combinations must appear at least once in the array."""
    ):
        covering_array = CoveringArray(combinations_dict, strength=5)

    with And(
        "creating a list of lists of privileges from the covering array with some combinations of privileges"
    ):
        privileges_combinations = [
            [
                item["user_source_privileges"],
                item["definer_one_source_privileges"],
                item["definer_one_target_one_privileges"],
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
            definer_three_target_two_privileges,
            definer_three_target_three_privileges,
            grant_privilege,
        ) in privileges_combinations:
            test_name = f"user_source-{user_source_privileges},definer_one_source-{definer_one_source_privileges},definer_one_target_one-{definer_one_target_one_privileges},definer_three_target_two-{definer_three_target_two_privileges},definer_three_target_three-{definer_three_target_three_privileges},grant_privileges_option-{grant_privilege.__name__}"
            test_name = (
                test_name.replace("(", "_")
                .replace(")", "_")
                .replace(" ", "")
                .replace("'", "")
            )
            Scenario(
                test_name,
                description=f"""
                User source privileges: {user_source_privileges}
                Definer one source privileges: {definer_one_source_privileges}
                Definer one target one privileges: {definer_one_target_one_privileges}
                Definer three target two privileges: {definer_three_target_two_privileges}
                Definer three target three privileges: {definer_three_target_three_privileges}
                """,
                test=cascade_mv_definer_mv_mv_definer,
                parallel=True,
                executor=executor,
            )(
                user_source_privileges=user_source_privileges,
                definer_one_source_privileges=definer_one_source_privileges,
                definer_one_target_one_privileges=definer_one_target_one_privileges,
                definer_three_target_two_privileges=definer_three_target_two_privileges,
                definer_three_target_three_privileges=definer_three_target_three_privileges,
                grant_privilege=grant_privilege,
            )
        join()


@TestFeature
def check_cascade_mv_mv_mv_definer(self):
    """
    Run test for all possible combinations of privileges for cascading view:
    source table -> MV without sql security specified-> MV without sql security specified -> MV with definer
    """
    if self.context.stress:
        with Given("choices how privileges can be granted"):
            grant_privileges = define(
                "grant privileges",
                [grant_privileges_directly, grant_privileges_via_role],
                encoder=get_name,
            )

        with And("possible table privileges"):
            privileges = define(
                "privileges", ("SELECT", "INSERT", "ALTER", "CREATE", "NONE")
            )
    else:
        with Given("privileges are only granted directly"):
            grant_privileges = define(
                "grant privileges", [grant_privileges_directly], encoder=get_name
            )

        with And("only required privileges"):
            privileges = define("privileges", ("SELECT", "INSERT", "NONE"))

    with Given(
        "generate all possible pairs of privileges and add an option with no privileges"
    ):
        privilege_pairs = define(
            "privilege pairs", list(combinations(privileges, 2)) + [("NONE",)]
        )

    with And(
        "create dictionary for storing possible privileges for definer users and for user executing queries"
    ):
        combinations_dict = {}

        with By(
            "define privileges for the user executing queries for the source table of the first MV"
        ):
            combinations_dict["user_source_privileges"] = privilege_pairs
        with By(
            "define privileges for user executing queries for the target table of the first MV"
        ):
            combinations_dict["user_target_one_privileges"] = privilege_pairs
        with By(
            "define privileges for the third definer user for the target table of the second MV (which is the source table of the third MV)"
        ):
            combinations_dict["definer_three_target_two_privileges"] = privilege_pairs
        with By(
            "define privileges for the third definer user for the target table of the third MV"
        ):
            combinations_dict["definer_three_target_three_privileges"] = privilege_pairs
        with By("define the method of granting privileges"):
            combinations_dict["grant_privilege"] = grant_privileges

    with And(
        """using covering array with strength 5 to decrease the number of combinations.
        The strength of a covering array specifies the number of variables for which 
        all possible value combinations must appear at least once in the array."""
    ):
        covering_array = CoveringArray(combinations_dict, strength=5)

    with And(
        "creating a list of lists of privileges from the covering array with some combinations of privileges"
    ):
        privileges_combinations = [
            [
                item["user_source_privileges"],
                item["user_target_one_privileges"],
                item["definer_three_target_two_privileges"],
                item["definer_three_target_three_privileges"],
                item["grant_privilege"],
            ]
            for item in covering_array
        ]

    with Pool(7) as executor:
        for (
            user_source_privileges,
            user_target_one_privileges,
            definer_three_target_two_privileges,
            definer_three_target_three_privileges,
            grant_privilege,
        ) in privileges_combinations:
            test_name = f"user_source-{user_source_privileges},user_target_one-{user_target_one_privileges},definer_three_target_two-{definer_three_target_two_privileges},definer_three_target_three-{definer_three_target_three_privileges},grant_privileges_option-{grant_privilege.__name__}"
            test_name = (
                test_name.replace("(", "_")
                .replace(")", "_")
                .replace(" ", "")
                .replace("'", "")
            )
            Scenario(
                test_name,
                description=f"""
                User source privileges: {user_source_privileges}
                User target one privileges: {user_target_one_privileges}
                Definer three target two privileges: {definer_three_target_two_privileges}
                Definer three target three privileges: {definer_three_target_three_privileges}
                """,
                test=cascade_mv_mv_mv_definer,
                parallel=True,
                executor=executor,
            )(
                user_source_privileges=user_source_privileges,
                user_target_one_privileges=user_target_one_privileges,
                definer_three_target_two_privileges=definer_three_target_two_privileges,
                definer_three_target_three_privileges=definer_three_target_three_privileges,
                grant_privilege=grant_privilege,
            )
        join()


@TestScenario
def check_cascade_mv_mv_definer_mv(self):
    """
    Run test for all possible combinations of privileges for cascading view:
    source table -> MV without sql security specified-> MV with definer -> MV without sql security specified
    """
    if self.context.stress:
        with Given("choices how privileges can be granted"):
            grant_privileges = define(
                "grant privileges",
                [grant_privileges_directly, grant_privileges_via_role],
                encoder=get_name,
            )

        with And("possible table privileges"):
            privileges = define(
                "privileges", ("SELECT", "INSERT", "ALTER", "CREATE", "NONE")
            )
    else:
        with Given("privileges are only granted directly"):
            grant_privileges = define(
                "grant privileges", [grant_privileges_directly], encoder=get_name
            )
            grant_privileges = [grant_privileges_directly]

        with And("only required privileges"):
            privileges = define("privileges", ("SELECT", "INSERT", "NONE"))

    with Given(
        "generate all possible pairs of privileges and add an option with no privileges"
    ):
        privilege_pairs = define(
            "privilege pairs", list(combinations(privileges, 2)) + [("NONE",)]
        )

    with And(
        "create dictionary for storing possible privileges for definer users and for user executing queries"
    ):
        combinations_dict = {}

        with By(
            "define privileges for the user executing queries for the source table of the first MV"
        ):
            combinations_dict["user_source_privileges"] = privilege_pairs
        with By(
            "define privileges for the user executing queries for the target table two"
        ):
            combinations_dict["user_target_two_privileges"] = privilege_pairs
        with By(
            "define privileges for the second definer user for the target table of the first MV (which is the source table of the second MV)"
        ):
            combinations_dict["definer_two_target_one_privileges"] = privilege_pairs
        with By(
            "define privileges for the second definer user for the target table of the second MV"
        ):
            combinations_dict["definer_two_target_two_privileges"] = privilege_pairs
        with By("define the method of granting privileges"):
            combinations_dict["grant_privilege"] = grant_privileges

    with And(
        """using covering array with strength 5 to decrease the number of combinations.
        The strength of a covering array specifies the number of variables for which 
        all possible value combinations must appear at least once in the array."""
    ):
        covering_array = CoveringArray(combinations_dict, strength=5)

    with And(
        "creating a list of lists from covering array with some combinations of privileges"
    ):
        privileges_combinations = [
            [
                item["user_source_privileges"],
                item["user_target_two_privileges"],
                item["definer_two_target_one_privileges"],
                item["definer_two_target_two_privileges"],
                item["grant_privilege"],
            ]
            for item in covering_array
        ]

    with Pool(7) as executor:
        for (
            user_source_privileges,
            user_target_two_privileges,
            definer_two_target_one_privileges,
            definer_two_target_two_privileges,
            grant_privilege,
        ) in privileges_combinations:
            test_name = f"user_source-{user_source_privileges},user_target_two-{user_target_two_privileges},definer_two_target_one-{definer_two_target_one_privileges},definer_two_target_two-{definer_two_target_two_privileges},grant_privileges_option-{grant_privilege.__name__}"
            test_name = (
                test_name.replace("(", "_")
                .replace(")", "_")
                .replace(" ", "")
                .replace("'", "")
            )
            Scenario(
                test_name,
                description=f"""
                User source privileges: {user_source_privileges}
                User target two privileges: {user_target_two_privileges}
                Definer two target one privileges: {definer_two_target_one_privileges}
                Definer two target two privileges: {definer_two_target_two_privileges}  
                """,
                test=cascade_mv_mv_definer_mv,
                parallel=True,
                executor=executor,
            )(
                user_source_privileges=user_source_privileges,
                user_target_two_privileges=user_target_two_privileges,
                definer_two_target_one_privileges=definer_two_target_one_privileges,
                definer_two_target_two_privileges=definer_two_target_two_privileges,
                grant_privilege=grant_privilege,
            )
        join()


@TestFeature
def check_cascade_mv_definer_mv_definer_mv(self):
    """
    Run test for all possible combinations of privileges for cascading view:
    source table -> MV with definer -> MV with definer -> MV without sql security specified
    """
    if self.context.stress:
        with Given("choices how privileges can be granted"):
            grant_privileges = define(
                "grant privileges",
                [grant_privileges_directly, grant_privileges_via_role],
                encoder=get_name,
            )

        with And("possible table privileges"):
            privileges = define(
                "privileges", ("SELECT", "INSERT", "ALTER", "CREATE", "NONE")
            )
    else:
        with Given("privileges are only granted directly"):
            grant_privileges = define(
                "grant privileges", [grant_privileges_directly], encoder=get_name
            )

        with And("only required privileges"):
            privileges = define("privileges", ("SELECT", "INSERT", "NONE"))

    with Given(
        "generate all possible pairs of privileges and add an option with no privileges"
    ):
        privilege_pairs = define(
            "privilege pairs", list(combinations(privileges, 2)) + [("NONE",)]
        )

    with And(
        "create dictionary for storing possible privileges for definer users and for user executing queries"
    ):
        combinations_dict = {}

        with By(
            "define privileges for the user executing queries for the source table of the first MV"
        ):
            combinations_dict["user_source_privileges"] = privilege_pairs
        with By(
            "define privileges for the user executing queries for the target table of the second MV"
        ):
            combinations_dict["user_target_two_privileges"] = privilege_pairs
        with By(
            "define privileges for the first definer user for the source table of the first MV"
        ):
            combinations_dict["definer_one_source_privileges"] = privilege_pairs
        with By(
            "define privileges for the first definer user for the target table of the first MV"
        ):
            combinations_dict["definer_one_target_one_privileges"] = privilege_pairs
        with By(
            "define privileges for the second definer user for the target table of the first MV (which is the source table of the second MV)"
        ):
            combinations_dict["definer_two_target_one_privileges"] = privilege_pairs
        with By(
            "define privileges for the second definer user for the target table of the second MV"
        ):
            combinations_dict["definer_two_target_two_privileges"] = privilege_pairs
        with By("define the method of granting privileges"):
            combinations_dict["grant_privilege"] = grant_privileges

    with And(
        """using covering array with strength 5 to decrease the number of combinations.
        The strength of a covering array specifies the number of variables for which 
        all possible value combinations must appear at least once in the array."""
    ):
        covering_array = CoveringArray(combinations_dict, strength=5)

    with And(
        "creating a list of lists of privileges from the covering array with some combinations of privileges"
    ):
        privileges_combinations = [
            [
                item["user_source_privileges"],
                item["user_target_two_privileges"],
                item["definer_one_source_privileges"],
                item["definer_one_target_one_privileges"],
                item["definer_two_target_one_privileges"],
                item["definer_two_target_two_privileges"],
                item["grant_privilege"],
            ]
            for item in covering_array
        ]

    with Pool(7) as executor:
        for (
            user_source_privileges,
            user_target_two_privileges,
            definer_one_source_privileges,
            definer_one_target_one_privileges,
            definer_two_target_one_privileges,
            definer_two_target_two_privileges,
            grant_privilege,
        ) in privileges_combinations:
            test_name = f"user_source-{user_source_privileges},user_target_two-{user_target_two_privileges},definer_one_source-{definer_one_source_privileges},definer_one_target_one-{definer_one_target_one_privileges},definer_two_target_one-{definer_two_target_one_privileges},definer_two_target_two-{definer_two_target_two_privileges},grant_privileges_option-{grant_privilege.__name__}"
            test_name = (
                test_name.replace("(", "_")
                .replace(")", "_")
                .replace(" ", "")
                .replace("'", "")
            )
            Scenario(
                test_name,
                description=f"""
                User source privileges: {user_source_privileges}
                User target two privileges: {user_target_two_privileges}
                Definer one source privileges: {definer_one_source_privileges}
                Definer one target one privileges: {definer_one_target_one_privileges}
                Definer two target one privileges: {definer_two_target_one_privileges}
                Definer two target two privileges: {definer_two_target_two_privileges}
                """,
                test=cascade_mv_definer_mv_definer_mv,
                parallel=True,
                executor=executor,
            )(
                user_source_privileges=user_source_privileges,
                user_target_two_privileges=user_target_two_privileges,
                definer_one_source_privileges=definer_one_source_privileges,
                definer_one_target_one_privileges=definer_one_target_one_privileges,
                definer_two_target_one_privileges=definer_two_target_one_privileges,
                definer_two_target_two_privileges=definer_two_target_two_privileges,
                grant_privilege=grant_privilege,
            )
        join()


@TestFeature
def check_cascade_mv_definer_mv_mv(self):
    """
    Run test for all possible combinations of privileges for cascading view:
    source table -> MV with definer -> MV without sql security specified -> MV without sql security specified
    """
    if self.context.stress:
        with Given("choices how privileges can be granted"):
            grant_privileges = define(
                "grant privileges",
                [grant_privileges_directly, grant_privileges_via_role],
                encoder=get_name,
            )

        with And("possible table privileges"):
            privileges = define(
                "privileges", ("SELECT", "INSERT", "ALTER", "CREATE", "NONE")
            )
    else:
        with Given("privileges are only granted directly"):
            grant_privileges = define(
                "grant privileges", [grant_privileges_directly], encoder=get_name
            )

        with And("only required privileges"):
            privileges = define("privileges", ("SELECT", "INSERT", "NONE"))

    with Given(
        "generate all possible pairs of privileges and add an option with no privileges"
    ):
        privilege_pairs = define(
            "privilege pairs", list(combinations(privileges, 2)) + [("NONE",)]
        )

    with And(
        "create dictionary for storing possible privileges for definer users and for user executing queries"
    ):
        combinations_dict = {}

        with By(
            "define privileges for the user executing queries for the source table of the first MV"
        ):
            combinations_dict["user_source_privileges"] = privilege_pairs
        with By(
            "define privileges for the user executing queries for the target table of the second MV"
        ):
            combinations_dict["user_target_two_privileges"] = privilege_pairs
        with By(
            "define privileges for the first definer user for the source table of the first MV"
        ):
            combinations_dict["definer_one_source_privileges"] = privilege_pairs
        with By(
            "define privileges for the first definer user for the target table of the first MV"
        ):
            combinations_dict["definer_one_target_one_privileges"] = privilege_pairs
        with By(
            "define privileges for the first definer user for the target table of the second MV"
        ):
            combinations_dict["definer_one_target_two_privileges"] = privilege_pairs
        with By("define the method of granting privileges"):
            combinations_dict["grant_privilege"] = grant_privileges

    with And(
        """using covering array with strength 5 to decrease the number of combinations.
        The strength of a covering array specifies the number of variables for which 
        all possible value combinations must appear at least once in the array."""
    ):
        covering_array = CoveringArray(combinations_dict, strength=5)

    with And(
        "creating a list of lists of privileges from the covering array with some combinations of privileges"
    ):
        privileges_combinations = [
            [
                item["user_source_privileges"],
                item["user_target_two_privileges"],
                item["definer_one_source_privileges"],
                item["definer_one_target_one_privileges"],
                item["definer_one_target_two_privileges"],
                item["grant_privilege"],
            ]
            for item in covering_array
        ]

    with Pool(7) as executor:
        for (
            user_source_privileges,
            user_target_two_privileges,
            definer_one_source_privileges,
            definer_one_target_one_privileges,
            definer_one_target_two_privileges,
            grant_privilege,
        ) in privileges_combinations:
            test_name = f"user_source-{user_source_privileges},user_target_two-{user_target_two_privileges},definer_one_source-{definer_one_source_privileges},definer_one_target_one-{definer_one_target_one_privileges},definer_one_target_two-{definer_one_target_two_privileges},grant_privileges_option-{grant_privilege.__name__}"
            test_name = (
                test_name.replace("(", "_")
                .replace(")", "_")
                .replace(" ", "")
                .replace("'", "")
            )
            Scenario(
                test_name,
                description=f"""
                User source privileges: {user_source_privileges}
                User target two privileges: {user_target_two_privileges}
                Definer one source privileges: {definer_one_source_privileges}
                Definer one target one privileges: {definer_one_target_one_privileges}
                Definer one target two privileges: {definer_one_target_two_privileges}
                """,
                test=cascade_mv_definer_mv_mv,
                parallel=True,
                executor=executor,
            )(
                user_source_privileges=user_source_privileges,
                user_target_two_privileges=user_target_two_privileges,
                definer_one_source_privileges=definer_one_source_privileges,
                definer_one_target_one_privileges=definer_one_target_one_privileges,
                definer_one_target_two_privileges=definer_one_target_two_privileges,
                grant_privilege=grant_privilege,
            )
        join()


@TestFeature
def check_cascade_mv_mv_mv(self):
    """
    Run test for all possible combinations of privileges for cascading view:
    source table -> MV without sql security specified -> MV without sql security specified -> MV without sql security specified
    """
    if self.context.stress:
        with Given("choices how privileges can be granted"):
            grant_privileges = define(
                "grant privileges",
                [grant_privileges_directly, grant_privileges_via_role],
                encoder=get_name,
            )

        with And("possible table privileges"):
            privileges = define(
                "privileges", ("SELECT", "INSERT", "ALTER", "CREATE", "NONE")
            )
    else:
        with Given("privileges are only granted directly"):
            grant_privileges = define(
                "grant privileges", [grant_privileges_directly], encoder=get_name
            )

        with And("only required privileges"):
            privileges = define("privileges", ("SELECT", "INSERT", "NONE"))

    with Given(
        "generate all possible pairs of privileges and add an option with no privileges"
    ):
        privilege_pairs = define(
            "privilege pairs", list(combinations(privileges, 2)) + [("NONE",)]
        )

    with And(
        "create dictionary for storing possible privileges for definer users and for user executing queries"
    ):
        combinations_dict = {}

        with By(
            "define privileges for the user executing queries for the source table of the first MV"
        ):
            combinations_dict["user_source_privileges"] = privilege_pairs
        with By(
            "define privileges for the user executing queries for the target table of the first MV"
        ):
            combinations_dict["user_target_one_privileges"] = privilege_pairs
        with By(
            "define privileges for the user executing queries for the target table of the second MV"
        ):
            combinations_dict["user_target_two_privileges"] = privilege_pairs
        with By("define the method of granting privileges"):
            combinations_dict["grant_privilege"] = grant_privileges

    with And(
        """using covering array with strength 4 to decrease the number of combinations.
        The strength of a covering array specifies the number of variables for which 
        all possible value combinations must appear at least once in the array."""
    ):
        covering_array = CoveringArray(combinations_dict, strength=4)

    with And(
        "creating a list of lists of privileges from the covering array with some combinations of privileges"
    ):
        privileges_combinations = [
            [
                item["user_source_privileges"],
                item["user_target_one_privileges"],
                item["user_target_two_privileges"],
                item["grant_privilege"],
            ]
            for item in covering_array
        ]

    with Pool(7) as executor:
        for (
            user_source_privileges,
            user_target_one_privileges,
            user_target_two_privileges,
            grant_privilege,
        ) in privileges_combinations:
            test_name = f"user_source-{user_source_privileges},user_target_one-{user_target_one_privileges},user_target_two-{user_target_two_privileges},grant_privileges_option-{grant_privilege.__name__}"
            test_name = (
                test_name.replace("(", "_")
                .replace(")", "_")
                .replace(" ", "")
                .replace("'", "")
            )
            Scenario(
                test_name,
                description=f"""
                User source privileges: {user_source_privileges}
                User target one privileges: {user_target_one_privileges}
                User target two privileges: {user_target_two_privileges}
                """,
                test=cascade_mv_mv_mv,
                parallel=True,
                executor=executor,
            )(
                user_source_privileges=user_source_privileges,
                user_target_one_privileges=user_target_one_privileges,
                user_target_two_privileges=user_target_two_privileges,
                grant_privilege=grant_privilege,
            )
        join()


@TestFeature
@Requirements(RQ_SRS_006_RBAC_SQLSecurity_MaterializedView_CascadingViews("1.0"))
@Name("cascading views")
def feature(self, node="clickhouse1"):
    """Test cascading materialized views with different sql security options."""
    self.context.node = self.context.cluster.node(node)

    Scenario(run=check_cascade_mv_definer_mv_definer_mv_definer)
    Scenario(run=check_cascade_mv_mv_definer_mv_definer)
    Scenario(run=check_cascade_mv_definer_mv_mv_definer)
    Scenario(run=check_cascade_mv_mv_mv_definer)
    Scenario(run=check_cascade_mv_mv_definer_mv)
    Scenario(run=check_cascade_mv_definer_mv_definer_mv)
    Scenario(run=check_cascade_mv_definer_mv_mv)
    Scenario(run=check_cascade_mv_mv_mv)
