#!/usr/bin/env python3
import os
import sys
import platform

from testflows.core import *

append_path(sys.path, "..")

from helpers.cluster import create_cluster
from helpers.argparser import argparser, CaptureClusterArgs
from helpers.common import check_clickhouse_version, experimental_analyzer, check_with_any_sanitizer
from rbac.requirements import SRS_006_ClickHouse_Role_Based_Access_Control
from rbac.helper.common import add_rbac_config_file

issue_14091 = "https://github.com/ClickHouse/ClickHouse/issues/14091"
issue_14149 = "https://github.com/ClickHouse/ClickHouse/issues/14149"
issue_14224 = "https://github.com/ClickHouse/ClickHouse/issues/14224"
issue_14418 = "https://github.com/ClickHouse/ClickHouse/issues/14418"
issue_14451 = "https://github.com/ClickHouse/ClickHouse/issues/14451"
issue_14566 = "https://github.com/ClickHouse/ClickHouse/issues/14566"
issue_14674 = "https://github.com/ClickHouse/ClickHouse/issues/14674"
issue_14810 = "https://github.com/ClickHouse/ClickHouse/issues/14810"
issue_15165 = "https://github.com/ClickHouse/ClickHouse/issues/15165"
issue_15980 = "https://github.com/ClickHouse/ClickHouse/issues/15980"
issue_16403 = "https://github.com/ClickHouse/ClickHouse/issues/16403"
issue_17146 = "https://github.com/ClickHouse/ClickHouse/issues/17146"
issue_17147 = "https://github.com/ClickHouse/ClickHouse/issues/17147"
issue_17653 = "https://github.com/ClickHouse/ClickHouse/issues/17653"
issue_17655 = "https://github.com/ClickHouse/ClickHouse/issues/17655"
issue_17766 = "https://github.com/ClickHouse/ClickHouse/issues/17766"
issue_18110 = "https://github.com/ClickHouse/ClickHouse/issues/18110"
issue_21083 = "https://github.com/ClickHouse/ClickHouse/issues/21083"
issue_21084 = "https://github.com/ClickHouse/ClickHouse/issues/21084"
issue_25413 = "https://github.com/ClickHouse/ClickHouse/issues/25413"
issue_26746 = "https://github.com/ClickHouse/ClickHouse/issues/26746"
issue_37389 = "https://github.com/ClickHouse/ClickHouse/issues/37389"
issue_37580 = "https://github.com/ClickHouse/ClickHouse/issues/37580"
issue_38716 = "https://github.com/ClickHouse/ClickHouse/issues/38716"
pull_47002 = "https://github.com/ClickHouse/ClickHouse/pull/47002"
issue_65134 = "https://github.com/ClickHouse/ClickHouse/issues/65134"
issue_70898 = "https://github.com/ClickHouse/ClickHouse/issues/70898"

xfails = {
    "part 1/syntax/show create quota/I show create quota current": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/12495")
    ],
    "part 1/views/:/create with subquery privilege granted directly or via role/:": [
        (Fail, issue_14091)
    ],
    "part 1/views/:/create with join query privilege granted directly or via role/:": [
        (Fail, issue_14091)
    ],
    "part 1/views/:/create with union query privilege granted directly or via role/:": [
        (Fail, issue_14091)
    ],
    "part 1/views/:/create with join union subquery privilege granted directly or via role/:": [
        (Fail, issue_14091)
    ],
    "part 1/views/:/create with nested views privilege granted directly or via role/:": [
        (Fail, issue_14091)
    ],
    "part 1/views/view/select with join query privilege granted directly or via role/:": [
        (Fail, issue_14149)
    ],
    "part 1/views/view/select with join union subquery privilege granted directly or via role/:": [
        (Fail, issue_14149)
    ],
    "part 1/views/view/select with nested views privilege granted directly or via role/:": [
        (Fail, issue_14149)
    ],
    "part 1/views/live view/refresh with privilege granted directly or via role/:": [
        (Fail, issue_14224)
    ],
    "part 1/views/live view/refresh with privilege revoked directly or from role/:": [
        (Fail, issue_14224)
    ],
    "part 1/views/live view/select:": [(Fail, issue_14418)],
    "part 1/views/live view/select:/:": [(Fail, issue_14418)],
    "part 1/views/materialized view/select with:": [(Fail, issue_14451)],
    "part 1/views/materialized view/select with:/:": [(Fail, issue_14451)],
    "part 1/views/materialized view/modify query:": [(Fail, issue_14674)],
    "part 1/views/materialized view/modify query:/:": [(Fail, issue_14674)],
    "part 1/views/materialized view/insert on source table privilege granted directly or via role/:": [
        (Fail, issue_14810)
    ],
    "part 1/privileges/alter ttl/table_type=:/user with some privileges": [
        (Fail, issue_14566)
    ],
    "part 1/privileges/alter ttl/table_type=:/role with some privileges": [
        (Fail, issue_14566)
    ],
    "part 1/privileges/alter ttl/table_type=:/user with privileges on cluster": [
        (Fail, issue_14566)
    ],
    "part 1/privileges/alter ttl/table_type=:/user with privileges from user with grant option": [
        (Fail, issue_14566)
    ],
    "part 1/privileges/alter ttl/table_type=:/user with privileges from role with grant option": [
        (Fail, issue_14566)
    ],
    "part 1/privileges/alter ttl/table_type=:/role with privileges from user with grant option": [
        (Fail, issue_14566)
    ],
    "part 1/privileges/alter ttl/table_type=:/role with privileges from role with grant option": [
        (Fail, issue_14566)
    ],
    "part 1/privileges/distributed table/:/special cases/insert with table on source table of materialized view:": [
        (Fail, issue_14810)
    ],
    "part 1/privileges/distributed table/cluster tests/cluster='sharded*": [
        (Fail, issue_15165)
    ],
    "part 1/privileges/distributed table/cluster tests/cluster=:/special cases/insert with table on source table of materialized view privilege granted directly or via role/:": [
        (Fail, issue_14810)
    ],
    "part 1/views/materialized view/select from implicit target table privilege granted directly or via role/select from implicit target table, privilege granted directly": [
        (Fail, ".inner table is not created as expected")
    ],
    "part 1/views/materialized view/insert on target table privilege granted directly or via role/insert on target table, privilege granted through a role": [
        (Fail, ".inner table is not created as expected")
    ],
    "part 1/views/materialized view/select from implicit target table privilege granted directly or via role/select from implicit target table, privilege granted through a role": [
        (Fail, ".inner table is not created as expected")
    ],
    "part 1/views/materialized view/insert on target table privilege granted directly or via role/insert on target table, privilege granted directly": [
        (Fail, ".inner table is not created as expected")
    ],
    "part 1/views/materialized view/select from source table privilege granted directly or via role/select from implicit target table, privilege granted directly": [
        (Fail, ".inner table is not created as expected")
    ],
    "part 1/views/materialized view/select from source table privilege granted directly or via role/select from implicit target table, privilege granted through a role": [
        (Fail, ".inner table is not created as expected")
    ],
    "part 1/privileges/alter move/:/:/:/:/move partition to implicit target table of a materialized view": [
        (Fail, ".inner table is not created as expected")
    ],
    "part 1/privileges/alter move/:/:/:/:/user without ALTER MOVE PARTITION privilege/": [
        (Fail, issue_16403)
    ],
    "part 1/privileges/alter move/:/:/:/:/user with revoked ALTER MOVE PARTITION privilege/": [
        (Fail, issue_16403)
    ],
    "part 1/privileges/create table/create with join query privilege granted directly or via role/:": [
        (Fail, issue_17653)
    ],
    "part 1/privileges/create table/create with join union subquery privilege granted directly or via role/:": [
        (Fail, issue_17653)
    ],
    "part 1/privileges/create table/create with nested tables privilege granted directly or via role/:": [
        (Fail, issue_17653)
    ],
    "part 1/privileges/kill mutation/no privilege/kill mutation on cluster": [
        (Fail, issue_17146)
    ],
    "part 1/privileges/kill query/privilege granted directly or via role/:/": [
        (Fail, issue_17147)
    ],
    "part 1/privileges/show dictionaries/:/check privilege/:/exists/EXISTS with privilege": [
        (Fail, issue_17655)
    ],
    "part 1/privileges/public tables/sensitive tables": [
        (Fail, issue_18110, check_clickhouse_version("<24.4"))
    ],
    "part 1/privileges/: row policy/nested live:": [(Fail, issue_21083)],
    "part 1/privileges/: row policy/nested mat:": [(Fail, issue_21084)],
    "part 1/privileges/show dictionaries/:/check privilege/check privilege=SHOW DICTIONARIES/show dict/SHOW DICTIONARIES with privilege": [
        (Fail, "new bug")
    ],
    "part 1/privileges/show dictionaries/:/check privilege/check privilege=CREATE DICTIONARY/show dict/SHOW DICTIONARIES with privilege": [
        (Fail, "new bug")
    ],
    "part 1/privileges/show dictionaries/:/check privilege/check privilege=DROP DICTIONARY/show dict/SHOW DICTIONARIES with privilege": [
        (Fail, "new bug")
    ],
    "part 1/privileges/kill mutation/:/:/KILL ALTER : without privilege": [
        (Fail, issue_25413)
    ],
    "part 1/privileges/kill mutation/:/:/KILL ALTER : with revoked privilege": [
        (Fail, issue_25413)
    ],
    "part 1/privileges/kill mutation/:/:/KILL ALTER : with revoked ALL privilege": [
        (Fail, issue_25413)
    ],
    "part 1/privileges/create table/create with subquery privilege granted directly or via role/create with subquery, privilege granted directly": [
        (Fail, issue_26746)
    ],
    "part 1/privileges/create table/create with subquery privilege granted directly or via role/create with subquery, privilege granted through a role": [
        (Fail, issue_26746)
    ],
    "part 1/views/live view/create with join subquery privilege granted directly or via role/create with join subquery, privilege granted directly": [
        (Fail, issue_26746)
    ],
    "part 1/views/live view/create with join subquery privilege granted directly or via role/create with join subquery, privilege granted through a role": [
        (Fail, issue_26746)
    ],
    "part 1/privileges/table functions/cluster": [(Fail, issue_37389)],
    "part 1/privileges/table functions/remote": [(Fail, issue_37389)],
    "part 1/privileges/create row policy/remote": [(Fail, issue_37580)],
    "part 1/privileges/system drop replica/:/drop replica/check privilege:/:": [
        (Fail, issue_38716)
    ],
    "part 1/privileges/orphaned role": [(Fail, pull_47002)],
    "part 1/privileges/projections/ : privilege, ADD PROJECTION, privilege granted to :": [
        (Fail, "unstable test")
    ],
    "/rbac/part 2/SQL security/materialized view with definer/check default values/*": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/63564")
    ],
    "/rbac/part 2/SQL security/materialized view with definer/check change default values/I try to select from materialized view with second user/*": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/63564")
    ],
    "/rbac/part 2/SQL security/view with definer/check default sql security with definer/I try to select from view with user/*": [
        (Fail, "https://github.com/ClickHouse/ClickHouse/issues/63564")
    ],
    "part 1/privileges/create row policy/or replace/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/64486",
            check_clickhouse_version("<24.4"),
        ),
    ],
    "/rbac/part 3/multiple authentication methods/valid until/sha 256 hash auth method/*": [
        (Fail, "Should be fixed soon")
    ],
    "/rbac/part 1/privileges/valid until/check old behavior/no_password/*": [
        (
            Fail,
            "Does not include no_password in SHOW CREATE USER before 24.9",
            check_clickhouse_version("<24.9"),
        )
    ],
    "/rbac/part 3/multiple authentication methods/ssh key/multiple ssh keys exceeding limit/*": [
        (Fail, issue_70898),
    ],
    "/rbac/part 1/privileges/alter user/alter user granted directly/*": [
        (
            Fail,
            "https://github.com/ClickHouse/ClickHouse/issues/74372",
            check_clickhouse_version(">=25.1"),
        ),
    ],
}

xflags = {
    "part 1/privileges/alter index/table_type='ReplicatedVersionedCollapsingMergeTree-sharded_cluster'/role with privileges from role with grant option/granted=:/I try to ALTER INDEX with given part 1/privileges/I check order by when privilege is granted": (
        SKIP,
        0,
    )
}

ffails = {
    "/rbac/part 1/privileges/sources/HDFS*": (
        Skip,
        "Not supportted in ARM builds",
        (lambda test: platform.machine() == "aarch64"),
    ),
    "/rbac/part 1/privileges/system drop cache/compiled expression cache*": [
        (
            Skip,
            "Not supported in ARM builds",
            (lambda test: platform.machine() == "aarch64"),
        ),
        (
            Skip,
            "JIT compilation disabled in sanitizer builds",
            check_with_any_sanitizer,
        ),
    ],
    "rbac/part 1/privileges/:/table_type='ReplicatedReplacingMergeTree-sharded_cluster": (
        Skip,
        "Causes clickhouse timeout on 21.10",
        (
            lambda test: check_clickhouse_version(">=21.10")(test)
            and check_clickhouse_version("<21.11")(test)
        ),
    ),
    "rbac/part 1/views": (
        Skip,
        "Does not work on clickhouse 21.09",
        (
            lambda test: check_clickhouse_version(">=21.9")(test)
            and check_clickhouse_version("<21.10")(test)
        ),
    ),
    "rbac/part 1/privileges/system merges": (
        XFail,
        "Does not work on clickhouse 21.8",
        (lambda test: check_clickhouse_version("<21.9")(test)),
    ),
    "rbac/part 1/privileges/system ttl merges": (
        XFail,
        "Does not work on clickhouse 21.8",
        (lambda test: check_clickhouse_version("<21.9")(test)),
    ),
    "rbac/part 1/privileges/system moves": (
        XFail,
        "Does not work on clickhouse 21.8",
        (lambda test: check_clickhouse_version("<21.9")(test)),
    ),
    "rbac/part 1/privileges/system sends": (
        XFail,
        "Does not work on clickhouse 21.8",
        (lambda test: check_clickhouse_version("<21.9")(test)),
    ),
    "rbac/part 1/privileges/system fetches": (
        XFail,
        "Does not work on clickhouse 21.8",
        (lambda test: check_clickhouse_version("<21.9")(test)),
    ),
    "rbac/part 1/privileges/system replication queues": (
        XFail,
        "Does not work on clickhouse 21.8",
        (lambda test: check_clickhouse_version("<21.9")(test)),
    ),
    "/rbac/part 1/privileges/row policy/:": (
        XFail,
        "Does not work on clickhouse 22.8 https://github.com/ClickHouse/ClickHouse/issues/40956",
        (lambda test: check_clickhouse_version(">=22.8")(test)),
    ),
    "/rbac/part 1/privileges/system restart disk": (
        Skip,
        "No longer supported",
        (lambda test: check_clickhouse_version(">=23.2")(test)),
    ),
    "part 1/privileges/system reload/:/symbols/*": (
        Skip,
        "SYMBOLS was removed https://github.com/ClickHouse/ClickHouse/pull/51873",
        (lambda test: check_clickhouse_version(">=23.8")(test)),
    ),
    "/rbac/part 2/SQL security": (
        Skip,
        "SQL security was introduced in 24.2 and https://github.com/ClickHouse/ClickHouse/issues/79951",
        check_clickhouse_version("<24.2"),
    ),
    "/rbac/part 2/SQL security/modify materialized view SQL security/modify sql security on cluster": (
        Skip,
        "Crashes the server.",
        check_clickhouse_version("<24.6"),
    ),
    "/rbac/part 2/SQL security/joins/Select:PASTE:": (
        Skip,
        issue_65134,
        (
            lambda test: check_clickhouse_version(">=24.3")(test)
            or check_clickhouse_version("<24.5")(test)
        ),
    ),
    "/rbac/part 1/privileges/valid until": (
        Skip,
        "valid until was introduced in 23.9",
        check_clickhouse_version("<23.9"),
    ),
    "/rbac/part 1/privileges/valid until timezones": (
        Skip,
        "valid until was introduced in 23.9",
        check_clickhouse_version("<23.9"),
    ),
    "/rbac/part 3/multiple authentication methods": (
        Skip,
        "multiple authentication methods were introduced in 24.9",
        check_clickhouse_version("<24.9"),
    ),
    "/rbac/part 3/multiple authentication methods/valid until clause combinatorics": (
        Skip,
        "multiple authentication methods were introduced in 24.12",
        check_clickhouse_version("<24.12"),
    ),
    "/rbac/part 3/multiple authentication methods/valid until": (
        Skip,
        "multiple authentication methods were introduced in 24.12",
        check_clickhouse_version("<24.12"),
    ),
    "/rbac/part 1/privileges/check table": (
        Skip,
        "check privilege was introduced in 25.1",
        check_clickhouse_version("<25.1"),
    ),
    "/rbac/part 2/SQL security/drop definer": (
        Skip,
        "before 25.8, definer user can be dropped when mv depends on it",
        check_clickhouse_version("<25.8"),
    ),
    "/rbac/part 1/privileges/attach temporary table": (
        Skip,
        "https://github.com/ClickHouse/ClickHouse/pull/89450",
        check_clickhouse_version(">=25.11"),
    ),
}


@TestModule
@ArgumentParser(argparser)
@XFails(xfails)
@XFlags(xflags)
@FFails(ffails)
@Name("rbac")
@Specifications(SRS_006_ClickHouse_Role_Based_Access_Control)
@CaptureClusterArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
):
    """RBAC regression."""
    nodes = {"clickhouse": ("clickhouse1", "clickhouse2", "clickhouse3")}

    self.context.clickhouse_version = clickhouse_version

    if stress is not None:
        self.context.stress = stress

    note(self.context.stress)
    note(stress)

    with Given("docker-compose cluster"):
        cluster = create_cluster(
            **cluster_args,
            nodes=nodes,
            configs_dir=current_dir(),
        )
        self.context.cluster = cluster

    with And("I enable or disable experimental analyzer if needed"):
        for node in nodes["clickhouse"]:
            experimental_analyzer(node=cluster.node(node), with_analyzer=with_analyzer)

    if check_clickhouse_version(">=23.2")(self):
        for node in nodes["clickhouse"]:
            add_rbac_config_file(node=cluster.node(node))

    with Feature("part 1"):
        Feature(run=load("rbac.tests.syntax.feature", "feature"))
        Feature(run=load("rbac.tests.privileges.feature", "feature"))
        Feature(run=load("rbac.tests.views.feature", "feature"))

    with Feature("part 2"):
        Feature(run=load("rbac.tests.sql_security.feature", "feature"))

    with Feature("part 3"):
        Feature(
            run=load("rbac.tests.multiple_auth_methods.feature", "feature"),
        )


if main():
    regression()
