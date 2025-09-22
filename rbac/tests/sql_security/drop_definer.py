from testflows.core import *

from helpers.common import *

from rbac.requirements import *
from rbac.helper.common import *
from rbac.tests.sql_security.common import *


@TestScenario
def check_drop_definer(self):
    """Check that definer user can not be dropped when dependent mv exists."""
    node = self.context.node

    with Given(
        "create view's source and target tables and insert data into target table"
    ):
        source_table_name = create_simple_MergeTree_table(
            table_name="source_table_" + getuid(),
            column_name="x",
        )
        target_table_name = create_simple_MergeTree_table(
            table_name="target_table_" + getuid(),
            column_name="x",
            rows=10,
        )

    with And("create definer user"):
        definer_user = "definer" + getuid()
        create_user(user_name=definer_user)

    with And("create materialized view specifying SQL security and definer"):
        mv_name = create_materialized_view(
            source_table_name=source_table_name,
            target_table_name=target_table_name,
            sql_security="DEFINER",
            definer=definer_user,
        )

    with Then("check that definer user can not be dropped when dependent mv exists"):
        node.query(
            f"DROP USER {definer_user}",
            exitcode=118,
            message=f"DB::Exception: User `{definer_user}` is used as a definer in views",
        )

    with And("create new definer user"):
        new_definer_user = "new_definer_" + getuid()
        create_user(user_name=new_definer_user)

    with And("alter sql security to use new definer"):
        node.query(f"ALTER TABLE {mv_name} MODIFY DEFINER={new_definer_user}")

    with And("drop old definer user"):
        node.query(f"DROP USER {definer_user}")

    with And("try to drop new definer user"):
        node.query(
            f"DROP USER {new_definer_user}",
            exitcode=118,
            message=f"DB::Exception: User `{new_definer_user}` is used as a definer in views",
        )

    with And("drop materialized view"):
        node.query(f"DROP TABLE {mv_name}")

    with And("drop new definer user"):
        node.query(f"DROP USER {new_definer_user}")


@TestScenario
def check_drop_definer_default_values(self):
    """Check that definer user can not be dropped when mv exists with default values."""
    node = self.context.node

    with Given(
        "create view's source and target tables and insert data into target table"
    ):
        source_table_name = create_simple_MergeTree_table(
            table_name="source_table_" + getuid(),
            column_name="x",
        )
        target_table_name = create_simple_MergeTree_table(
            table_name="target_table_" + getuid(),
            column_name="x",
            rows=10,
        )

    with And("create definer user"):
        definer_user = "definer" + getuid()
        create_user(user_name=definer_user)

    with And(f"change default_view_definer setting to {definer_user} for default user"):
        entries = {
            "profiles": {
                "default": {
                    "default_view_definer": f"{definer_user}",
                }
            }
        }
        change_core_settings(restart=True, entries=entries)

    with And(
        "change ignore_empty_sql_security_in_create_view_query to 0 so defaults will be used"
    ):
        default_ignore_empty_sql_security_in_create_view_query = get_settings_value(
            setting_name="ignore_empty_sql_security_in_create_view_query",
            table="system.server_settings",
        )
        if default_ignore_empty_sql_security_in_create_view_query == "1":
            entries = {"ignore_empty_sql_security_in_create_view_query": "0"}
            change_core_settings(
                restart=True,
                entries=entries,
                config_d_dir="/etc/clickhouse-server/config.d",
                preprocessed_name="config.xml",
            )

    with And("create materialized view using default definer settings"):
        mv_name = create_materialized_view(
            source_table_name=source_table_name,
            target_table_name=target_table_name,
        )

    with Then("verify the materialized view was created with correct definer"):
        show_create_output = node.query(
            f"SHOW CREATE TABLE {mv_name} FORMAT TabSeparated"
        ).output
        assert (
            definer_user in show_create_output
        ), f"Expected definer {definer_user} not found in SHOW CREATE output"

    with And("try to drop definer user"):
        node.query(
            f"DROP USER {definer_user}",
            exitcode=118,
            message=f"DB::Exception: User `{definer_user}` is used as a definer in views",
        )

    with And("drop materialized view"):
        node.query(f"DROP TABLE {mv_name}")

    with And("drop definer user"):
        node.query(f"DROP USER {definer_user}")

    with And("create mv without specifying definer, expect error"):
        create_materialized_view(
            source_table_name=source_table_name,
            target_table_name=target_table_name,
            exitcode=192,
            message=f"DB::Exception: There is no user `{definer_user}` in `user directories`",
        )


@TestScenario
def check_drop_definer_modified(self):
    """Check that definer user can be dropped when mv's sql security is modified to `NONE`."""
    node = self.context.node

    with Given(
        "create view's source and target tables and insert data into target table"
    ):
        source_table_name = create_simple_MergeTree_table(
            table_name="source_table_" + getuid(),
            column_name="x",
        )
        target_table_name = create_simple_MergeTree_table(
            table_name="target_table_" + getuid(),
            column_name="x",
            rows=10,
        )

    with And("create definer user"):
        definer_user = "definer" + getuid()
        create_user(user_name=definer_user)

    with And("create materialized view specifying SQL security and definer"):
        mv_name = create_materialized_view(
            source_table_name=source_table_name,
            target_table_name=target_table_name,
            sql_security="DEFINER",
            definer=definer_user,
        )

    with And("try to drop definer user, expect error"):
        node.query(
            f"DROP USER {definer_user}",
            exitcode=118,
            message=f"DB::Exception: User `{definer_user}` is used as a definer in views",
        )

    with And("alter sql security to NONE"):
        node.query(f"ALTER TABLE {mv_name} MODIFY SQL SECURITY NONE")

    with And("drop definer user"):
        node.query(f"DROP USER {definer_user}")


@TestFeature
@Name("drop definer")
def feature(self):
    """Check that definer user can not be dropped when mv depends on it."""
    self.context.node = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node_2, self.context.node_3]

    Scenario(run=check_drop_definer)
    Scenario(run=check_drop_definer_default_values)
    Scenario(run=check_drop_definer_modified)
