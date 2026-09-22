from contextlib import contextmanager

from testflows.asserts import error
from testflows.combinatorics import product
from testflows.core import *

from rbac.helper.common import *
from rbac.requirements import *
import rbac.helper.errors as errors

# A mutation is accepted only when the submitting user can read everything it
# will read. validate_mutation_query does not change that. The product below is
# entry point x what is read x whether the read privilege is granted x the
# validation setting. Name resolution and other shapes that are not that
# rectangle are their own scenarios.
#
# https://github.com/ClickHouse/ClickHouse/issues/105614
# https://github.com/ClickHouse/ClickHouse/issues/107588
# https://github.com/ClickHouse/ClickHouse/pull/107486

CLUSTER = "sharded_cluster"

CARRIERS = {
    "where_column": {
        "kinds": None,
        "read_in": "where",
        "where": "hidden = 7",
        "assignment": "name = name",
        "grant": "SELECT(hidden) ON {tab}",
        "needs": (),
    },
    "assignment": {
        "kinds": ("update", "lightweight_update"),
        "read_in": "assignment",
        "where": "1",
        "assignment": "name = toString(hidden)",
        "grant": "SELECT(hidden) ON {tab}",
        "needs": (),
    },
    "subquery": {
        "kinds": None,
        "read_in": "where",
        "where": "id IN (SELECT secret FROM {secret_tab})",
        "assignment": "name = name",
        "grant": "SELECT ON {secret_tab}",
        "needs": ("secret",),
    },
    "subquery_constant": {
        "kinds": None,
        "read_in": "where",
        "where": "id IN (SELECT 1 FROM {secret_tab} WHERE payload = 'TOP-SECRET')",
        "assignment": "name = name",
        "grant": "SELECT ON {secret_tab}",
        "needs": ("secret",),
    },
    "subquery_assignment": {
        "kinds": ("update", "lightweight_update"),
        "read_in": "assignment",
        "where": "1",
        "assignment": "name = (SELECT max(payload) FROM {secret_tab})",
        "grant": "SELECT ON {secret_tab}",
        "needs": ("secret",),
        "copies_secret": True,
    },
    "in_set": {
        "kinds": None,
        "read_in": "where",
        "where": "id IN {secret_set}",
        "assignment": "name = name",
        "grant": "SELECT ON {secret_set}",
        "needs": ("set",),
    },
    "udf": {
        "kinds": None,
        "read_in": "where",
        "where": "{udf}()",
        "assignment": "name = name",
        "grant": "SELECT(hidden) ON {tab}",
        "needs": ("udf",),
    },
    "dict_get": {
        "kinds": None,
        "read_in": "where",
        "where": "dictGet('{db}.{dict}', 'payload', toUInt64(id)) = 'from-dict'",
        "assignment": "name = name",
        "grant": "dictGet ON {dict}",
        "needs": ("dict",),
    },
    "join_get": {
        "kinds": None,
        "read_in": "where",
        "where": "joinGet('{db}.{join_tab}', 'payload', id) = 'joined'",
        "assignment": "name = name",
        "grant": "SELECT ON {join_tab}",
        "needs": ("join",),
    },
}

# Column-level SELECT is enough for one plain table. A star or a join requires
# SELECT on the whole table, so a column grant stays a denial.
PARTIAL_CASES = {
    "subquery_wrong_column": {
        "where": "id IN (SELECT secret FROM {secret_tab})",
        "grants": ("SELECT(payload) ON {secret_tab}",),
        "needs": ("secret",),
        "denied": True,
    },
    "subquery_right_column": {
        "where": "id IN (SELECT secret FROM {secret_tab})",
        "grants": ("SELECT(secret) ON {secret_tab}",),
        "needs": ("secret",),
        "denied": False,
    },
    "star_column_grant": {
        "where": "1 IN (SELECT 1 FROM (SELECT * FROM {secret_tab}))",
        "grants": ("SELECT(secret) ON {secret_tab}",),
        "needs": ("secret",),
        "denied": True,
    },
    "star_table_grant": {
        "where": "1 IN (SELECT 1 FROM (SELECT * FROM {secret_tab}))",
        "grants": ("SELECT ON {secret_tab}",),
        "needs": ("secret",),
        "denied": False,
    },
    "join_column_grant": {
        "where": "id IN (SELECT r.id FROM {readable} r JOIN {dim} d ON r.id = d.id)",
        "grants": ("SELECT(id) ON {readable}", "SELECT(id) ON {dim}"),
        "needs": ("readable", "dim"),
        "denied": True,
    },
    "join_table_grant": {
        "where": "id IN (SELECT r.id FROM {readable} r JOIN {dim} d ON r.id = d.id)",
        "grants": ("SELECT ON {readable}", "SELECT ON {dim}"),
        "needs": ("readable", "dim"),
        "denied": False,
    },
}

ON_CLUSTER_CARRIERS = (
    "where_column",
    "assignment",
    "subquery",
    "subquery_assignment",
    "in_set",
    "udf",
)

NESTED_READS = (
    "id IN (SELECT id FROM {readable} WHERE id IN {secret_set})",
    "id IN (SELECT r.id FROM {readable} r JOIN {dim} d ON r.id = d.id AND r.id IN {secret_set})",
    "id IN (SELECT r.id FROM {readable} r JOIN {dim} d ON r.id = d.id AND dictGet('{db}.{dict}', 'payload', toUInt64(r.id)) = '')",
)


def sql_ident():
    """Identifier safe for an unquoted SQL name.

    The current step title is part of getuid(). A When() title can be a WHERE
    clause, so keep only characters that are legal in an unquoted name.
    """
    raw = getuid()
    cleaned = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in raw)
    return "m_" + cleaned


def entry_points():
    """Mutation entry points this server can parse."""
    entries = [
        ("alter_update", "update"),
        ("alter_delete", "delete"),
        ("lightweight_delete", "lightweight_delete"),
    ]
    if check_clickhouse_version(">=25.7")(current()):
        entries.append(("lightweight_update", "lightweight_update"))
    return entries


def mutation_settings(validate, kind, on_cluster):
    parts = [f"validate_mutation_query = {int(validate)}"]
    if on_cluster:
        parts.append("distributed_ddl_task_timeout = 120")
    else:
        parts.append("mutations_sync = 2")
    if kind == "lightweight_update":
        if check_clickhouse_version(">=25.8")(current()):
            parts.append("enable_lightweight_update = 1")
        else:
            parts.append("allow_experimental_lightweight_update = 1")
    return ", ".join(parts)


def mutation_statement(kind, table, where, assignment, settings, on_cluster):
    cluster_clause = f" ON CLUSTER {CLUSTER}" if on_cluster else ""
    if kind == "update":
        return (
            f"ALTER TABLE {table}{cluster_clause} UPDATE {assignment} "
            f"WHERE {where} SETTINGS {settings}"
        )
    if kind == "delete":
        return (
            f"ALTER TABLE {table}{cluster_clause} DELETE "
            f"WHERE {where} SETTINGS {settings}"
        )
    if kind == "lightweight_delete":
        return f"DELETE FROM {table}{cluster_clause} WHERE {where} SETTINGS {settings}"
    if kind == "lightweight_update":
        return (
            f"UPDATE {table}{cluster_clause} SET {assignment} "
            f"WHERE {where} SETTINGS {settings}"
        )
    raise AssertionError(kind)


def render_where(carrier, names, granted):
    where = carrier["where"].format(**names)
    if not granted:
        return where
    if carrier["read_in"] == "assignment":
        return "0"
    return f"({where}) AND 0"


def grant(node, privilege_on, user, on_cluster=False):
    cluster = f" ON CLUSTER {CLUSTER}" if on_cluster else ""
    node.query(f"GRANT{cluster} {privilege_on} TO {user}")


def run_as_user(node, user, sql, denied, extra_settings=None, use_file=False):
    settings = [("user", user)]
    if extra_settings:
        settings.extend(extra_settings)
    if denied:
        exitcode, message = errors.not_enough_privileges(name=user)
        node.query(
            sql,
            settings=settings,
            exitcode=exitcode,
            message=message,
            use_file=use_file,
        )
    else:
        node.query(sql, settings=settings, use_file=use_file)


def assert_not_access_denied(node, user, sql, extra_settings=None):
    """The query may fail for a reason of its own. Access control must not be that reason."""
    settings = [("user", user)]
    if extra_settings:
        settings.extend(extra_settings)
    result = node.query(sql, settings=settings, no_checks=True)
    assert "Not enough privileges" not in result.output, error(result.output)


def assert_refused(node, sql, user=None):
    settings = [("user", user)] if user is not None else None
    result = node.query(sql, settings=settings, no_checks=True)
    assert result.exitcode != 0, error(result.output)


def launch(executor, name, test, **kwargs):
    Scenario(
        name,
        test=test,
        parallel=True,
        executor=executor,
        setup=instrument_clickhouse_server_log,
    )(**kwargs)


@contextmanager
def mutation_fixture(self, needs=(), on_cluster=False):
    """Create the mutated table, the user who may mutate it but not read `hidden`, and the objects a carrier reads."""
    node = self.context.node
    uid = sql_ident()
    on = f" ON CLUSTER {CLUSTER}" if on_cluster else ""
    names = {
        "db": "default",
        "tab": f"tab_{uid}",
        "user": f"user_{uid}",
        "secret_tab": f"secret_tab_{uid}",
        "secret_set": f"secret_set_{uid}",
        "dict": f"dict_{uid}",
        "dict_src": f"dict_src_{uid}",
        "join_tab": f"join_tab_{uid}",
        "udf": f"udf_{uid}",
        "readable": f"readable_{uid}",
        "dim": f"dim_{uid}",
        "arr_tab": f"arr_tab_{uid}",
        "other_db": f"other_{uid}",
    }
    created_tables = []
    created_dict = False
    created_udf = False
    created_user = False

    def create_table(name, statement):
        node.query(statement)
        created_tables.append(name)

    try:
        create_table(
            names["tab"],
            f"CREATE TABLE {names['tab']}{on} (id UInt32, name String, hidden UInt32) "
            f"ENGINE = MergeTree ORDER BY id "
            f"SETTINGS enable_block_number_column = 1, enable_block_offset_column = 1",
        )
        node.query(f"INSERT INTO {names['tab']} VALUES (1, 'a', 7), (42, 'b', 8)")

        if "secret" in needs:
            create_table(
                names["secret_tab"],
                f"CREATE TABLE {names['secret_tab']}{on} (secret UInt32, payload String) "
                f"ENGINE = MergeTree ORDER BY secret",
            )
            node.query(f"INSERT INTO {names['secret_tab']} VALUES (42, 'TOP-SECRET')")

        if "set" in needs:
            create_table(
                names["secret_set"],
                f"CREATE TABLE {names['secret_set']}{on} (secret UInt32) ENGINE = Set",
            )
            node.query(f"INSERT INTO {names['secret_set']} VALUES (42)")

        if "readable" in needs:
            create_table(
                names["readable"],
                f"CREATE TABLE {names['readable']}{on} "
                f"(id UInt32, arr Array(UInt32), hidden_arr Array(UInt32)) "
                f"ENGINE = MergeTree ORDER BY id",
            )
            node.query(f"INSERT INTO {names['readable']} VALUES (1, [1], [7])")

        if "dim" in needs:
            create_table(
                names["dim"],
                f"CREATE TABLE {names['dim']}{on} (id UInt32) ENGINE = MergeTree ORDER BY id",
            )
            node.query(f"INSERT INTO {names['dim']} VALUES (1)")

        if "arr" in needs:
            create_table(
                names["arr_tab"],
                f"CREATE TABLE {names['arr_tab']}{on} (id UInt32, arr Array(UInt32)) "
                f"ENGINE = MergeTree ORDER BY id",
            )
            node.query(f"INSERT INTO {names['arr_tab']} VALUES (1, [1]), (42, [42])")

        if "dict" in needs:
            create_table(
                names["dict_src"],
                f"CREATE TABLE {names['dict_src']}{on} (key UInt64, payload String) "
                f"ENGINE = MergeTree ORDER BY key",
            )
            node.query(f"INSERT INTO {names['dict_src']} VALUES (1, 'from-dict')")
            node.query(
                f"CREATE DICTIONARY {names['dict']}{on} (key UInt64, payload String) "
                f"PRIMARY KEY key "
                f"SOURCE(CLICKHOUSE(HOST 'localhost' PORT tcpPort() USER 'default' "
                f"TABLE '{names['dict_src']}' PASSWORD '' DB 'default')) "
                f"LAYOUT(FLAT()) LIFETIME(0)"
            )
            created_dict = True

        if "join" in needs:
            create_table(
                names["join_tab"],
                f"CREATE TABLE {names['join_tab']}{on} (id UInt32, payload String) "
                f"ENGINE = Join(ANY, LEFT, id)",
            )
            node.query(f"INSERT INTO {names['join_tab']} VALUES (1, 'joined')")

        if "udf" in needs:
            node.query(f"CREATE FUNCTION {names['udf']}{on} AS () -> hidden = 7")
            created_udf = True

        node.query(f"CREATE USER OR REPLACE {names['user']}{on}")
        created_user = True
        grant(
            node,
            f"ALTER UPDATE, ALTER DELETE, UPDATE, DELETE ON {names['tab']}",
            names["user"],
            on_cluster,
        )
        grant(
            node,
            f"SELECT(id, name) ON {names['tab']}",
            names["user"],
            on_cluster,
        )
        if on_cluster:
            grant(node, "CLUSTER ON *.*", names["user"], on_cluster=True)

        yield names
    finally:
        if created_user:
            if on_cluster:
                node.query(f"DROP USER IF EXISTS {names['user']} ON CLUSTER {CLUSTER}")
            else:
                node.query(f"DROP USER IF EXISTS {names['user']}")
        if created_udf:
            node.query(f"DROP FUNCTION IF EXISTS {names['udf']}{on}")
        if created_dict:
            node.query(f"DROP DICTIONARY IF EXISTS {names['dict']}{on}")
        for table in reversed(created_tables):
            node.query(f"DROP TABLE IF EXISTS {table}{on} SYNC")


def execute_carrier(self, kind, carrier_name, granted, validate, on_cluster=False):
    node = self.context.node
    carrier = CARRIERS[carrier_name]
    with mutation_fixture(self, needs=carrier["needs"], on_cluster=on_cluster) as names:
        if granted:
            grant(node, carrier["grant"].format(**names), names["user"], on_cluster)
        where = render_where(carrier, names, granted)
        assignment = carrier["assignment"].format(**names)
        sql = mutation_statement(
            kind,
            names["tab"],
            where,
            assignment,
            mutation_settings(validate, kind, on_cluster),
            on_cluster,
        )
        run_as_user(node, names["user"], sql, denied=not granted)
        if granted and carrier.get("copies_secret"):
            leaked = node.query(
                f"SELECT count() FROM {names['tab']} WHERE name = 'TOP-SECRET'"
            ).output.strip()
            assert leaked == "0", error()


@TestScenario
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess("1.0"))
def check_carrier(self, kind, carrier_name, granted, validate):
    """One cell of the local entry-point, carrier, grant, and validation product."""
    execute_carrier(self, kind, carrier_name, granted, validate, on_cluster=False)


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess("1.0"),
    RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_OnCluster("1.0"),
)
def check_carrier_on_cluster(self, kind, carrier_name, granted, validate):
    """The same cell, checked on the initiator before ON CLUSTER enqueue."""
    execute_carrier(self, kind, carrier_name, granted, validate, on_cluster=True)


@TestScenario
@Name("combinations")
def combinations(self):
    """Every entry point, every indirect or direct read, with and without the grant, validation on and off."""
    with Pool(8) as executor:
        for (entry_name, kind), carrier_name, granted, validate in product(
            entry_points(),
            tuple(CARRIERS),
            (False, True),
            (0, 1),
        ):
            carrier = CARRIERS[carrier_name]
            if carrier["kinds"] is not None and kind not in carrier["kinds"]:
                continue
            launch(
                executor,
                f"{entry_name} {carrier_name} grant={int(granted)} validate={validate}",
                check_carrier,
                kind=kind,
                carrier_name=carrier_name,
                granted=granted,
                validate=validate,
            )
        join()


@TestScenario
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess("1.0"))
def check_partial_grant(self, kind, case_name, validate):
    """A column grant covers one plain table. A star or a join still needs the whole table."""
    node = self.context.node
    case = PARTIAL_CASES[case_name]
    with mutation_fixture(self, needs=case["needs"]) as names:
        for privilege in case["grants"]:
            grant(node, privilege.format(**names), names["user"])
        where = case["where"].format(**names)
        if not case["denied"]:
            where = f"({where}) AND 0"
        sql = mutation_statement(
            kind,
            names["tab"],
            where,
            "name = name",
            mutation_settings(validate, kind, on_cluster=False),
            on_cluster=False,
        )
        run_as_user(node, names["user"], sql, denied=case["denied"])


@TestScenario
@Name("partial grant")
def partial_grants(self):
    """Column-level SELECT against the whole-table fallback."""
    with Pool(8) as executor:
        for (entry_name, kind), case_name, validate in product(
            entry_points(),
            tuple(PARTIAL_CASES),
            (0, 1),
        ):
            launch(
                executor,
                f"{entry_name} {case_name} denied={int(PARTIAL_CASES[case_name]['denied'])} validate={validate}",
                check_partial_grant,
                kind=kind,
                case_name=case_name,
                validate=validate,
            )
        join()


@TestScenario
@Name("on cluster")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_OnCluster("1.0"))
def on_cluster(self):
    """ON CLUSTER mutations are checked for the initiating user before they are enqueued."""
    with Pool(4) as executor:
        for (entry_name, kind), carrier_name, granted, validate in product(
            entry_points(),
            ON_CLUSTER_CARRIERS,
            (False, True),
            (0, 1),
        ):
            carrier = CARRIERS[carrier_name]
            if carrier["kinds"] is not None and kind not in carrier["kinds"]:
                continue
            launch(
                executor,
                f"{entry_name} {carrier_name} grant={int(granted)} validate={validate}",
                check_carrier_on_cluster,
                kind=kind,
                carrier_name=carrier_name,
                granted=granted,
                validate=validate,
            )
        join()


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess("1.0"),
    RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_ReplicatedDatabase("1.0"),
)
def check_replicated_database(self, kind, granted, validate):
    """A Replicated database enqueues the mutation without the initiator's user, so the check is local."""
    node = self.context.node
    uid = sql_ident()
    database = f"rdb_{uid}"
    user = f"user_{uid}"
    table = f"{database}.tab"
    try:
        node.query(
            f"CREATE DATABASE {database} ENGINE = Replicated("
            f"'/clickhouse/rbac_mutation/{uid}', '01', 'clickhouse1')"
        )
        node.query(
            f"CREATE TABLE {table} (id UInt32, name String) ENGINE = MergeTree ORDER BY id"
        )
        node.query(f"INSERT INTO {table} VALUES (1, 'a'), (42, 'b')")
        node.query(f"CREATE USER {user}")
        if kind == "update":
            node.query(f"GRANT ALTER UPDATE ON {table} TO {user}")
            statement = (
                f"ALTER TABLE {table} UPDATE name = '' WHERE id = 42 "
                f"SETTINGS {mutation_settings(validate, kind, on_cluster=False)}"
            )
            if granted:
                statement = (
                    f"ALTER TABLE {table} UPDATE name = '' WHERE 0 "
                    f"SETTINGS {mutation_settings(validate, kind, on_cluster=False)}"
                )
        else:
            node.query(f"GRANT ALTER DELETE ON {table} TO {user}")
            statement = (
                f"ALTER TABLE {table} DELETE WHERE id = 42 "
                f"SETTINGS {mutation_settings(validate, kind, on_cluster=False)}"
            )
            if granted:
                statement = (
                    f"ALTER TABLE {table} DELETE WHERE 0 "
                    f"SETTINGS {mutation_settings(validate, kind, on_cluster=False)}"
                )
        node.query(f"GRANT SELECT(name) ON {table} TO {user}")
        if granted:
            node.query(f"GRANT SELECT(id) ON {table} TO {user}")
        run_as_user(node, user, statement, denied=not granted)
    finally:
        node.query(f"DROP USER IF EXISTS {user}")
        node.query(f"DROP DATABASE IF EXISTS {database} SYNC")


@TestScenario
@Name("replicated database")
def replicated_database(self):
    """Direct column reads of ALTER UPDATE and ALTER DELETE in a Replicated database."""
    with Pool(4) as executor:
        for (entry_name, kind), granted, validate in product(
            (("alter_update", "update"), ("alter_delete", "delete")),
            (False, True),
            (0, 1),
        ):
            launch(
                executor,
                f"{entry_name} where_column grant={int(granted)} validate={validate}",
                check_replicated_database,
                kind=kind,
                granted=granted,
                validate=validate,
            )
        join()


@TestScenario
@Name("readable and virtual columns")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_VirtualColumn("1.0"))
def readable_and_virtual_columns(self):
    """A column the user can read, and a virtual column, need no extra SELECT."""
    node = self.context.node
    reads = (
        ("readable column", "name = 'x'", ()),
        ("virtual column", "_part = 'nonexistent'", ()),
        (
            "subquery virtual column",
            "id IN (SELECT id FROM {readable} WHERE _part != '')",
            ("readable",),
        ),
    )
    for (entry_name, kind), (read_name, where, needs) in product(entry_points(), reads):
        with When(f"{entry_name} {read_name}"):
            with mutation_fixture(self, needs=needs) as names:
                if "readable" in needs:
                    grant(node, f"SELECT ON {names['readable']}", names["user"])
                sql = mutation_statement(
                    kind,
                    names["tab"],
                    f"({where.format(**names)}) AND 0",
                    "name = name",
                    mutation_settings(0, kind, on_cluster=False),
                    on_cluster=False,
                )
                run_as_user(node, names["user"], sql, denied=False)


@TestScenario
@Name("real column shadowing virtual")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_VirtualColumn("1.0"))
def real_column_shadowing_virtual(self):
    """A real column named `_part` is data, and still needs SELECT."""
    node = self.context.node
    for validate in (0, 1):
        with When(f"validate={validate}"):
            uid = sql_ident()
            table = f"shadow_{uid}"
            user = f"user_{uid}"
            try:
                node.query(
                    f"CREATE TABLE {table} (`_part` String, id UInt32) "
                    f"ENGINE = MergeTree ORDER BY id",
                    use_file=True,
                )
                node.query(f"CREATE USER {user}")
                node.query(f"GRANT ALTER DELETE, SELECT(id) ON {table} TO {user}")
                run_as_user(
                    node,
                    user,
                    f"ALTER TABLE {table} DELETE WHERE `_part` = 'x' "
                    f"SETTINGS {mutation_settings(validate, 'delete', on_cluster=False)}",
                    denied=True,
                    use_file=True,
                )
            finally:
                node.query(f"DROP USER IF EXISTS {user}")
                node.query(f"DROP TABLE IF EXISTS {table} SYNC")


@TestScenario
@Name("one part in name is a table")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_ObjectResolution("1.0"))
def one_part_in_name_is_a_table(self):
    """`1 IN arr` is stored as a table. `1 IN tab.arr` is the array column."""
    node = self.context.node
    with mutation_fixture(self, needs=("arr",)) as names:
        grant(
            node,
            f"ALTER DELETE, SELECT(id, arr) ON {names['arr_tab']}",
            names["user"],
        )
        settings = mutation_settings(0, "delete", on_cluster=False)
        with When("a qualified array column is the column"):
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['arr_tab']} DELETE WHERE 1 IN {names['arr_tab']}.arr AND 0 "
                f"SETTINGS {settings}",
                denied=False,
            )
        with When("a one-part name is a table"):
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['arr_tab']} DELETE WHERE 1 IN arr AND 0 SETTINGS {settings}",
                denied=True,
            )


@TestScenario
@Name("with and alias scope")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_ObjectResolution("1.0"))
def with_and_alias_scope(self):
    """A WITH name or a SELECT alias on the right of IN is not a table, and only at its own level."""
    node = self.context.node
    with mutation_fixture(self, needs=("arr", "dim", "set", "readable")) as names:
        grant(
            node,
            f"ALTER DELETE, SELECT(id, arr) ON {names['arr_tab']}",
            names["user"],
        )
        grant(node, f"SELECT ON {names['dim']}", names["user"])
        grant(node, f"SELECT ON {names['readable']}", names["user"])
        settings = mutation_settings(0, "delete", on_cluster=False)
        with When("a WITH name is not a table"):
            assert_not_access_denied(
                node,
                names["user"],
                f"ALTER TABLE {names['arr_tab']} DELETE WHERE id IN "
                f"(WITH s AS (SELECT 1 AS v) SELECT v FROM s) AND 0 SETTINGS {settings}",
            )
        with When("a SELECT alias and an ARRAY JOIN alias are not tables"):
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
                f"(SELECT 3 AS col3 FROM {names['dim']} WHERE 3 IN col3) AND 0 SETTINGS {settings}",
                denied=False,
            )
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
                f"(SELECT id FROM {names['readable']} ARRAY JOIN arr AS elem WHERE 1 IN elem) AND 0 "
                f"SETTINGS {settings}",
                denied=False,
            )
        with When("the same name below that level is a table again"):
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
                f"(SELECT 3 AS {names['secret_set']} FROM {names['dim']} WHERE id IN "
                f"(SELECT id FROM {names['dim']} WHERE 1 IN {names['secret_set']})) "
                f"SETTINGS {settings}",
                denied=True,
            )


@TestScenario
@Name("temporary table is not grant free")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_ObjectResolution("1.0"))
def temporary_table_is_not_grant_free(self):
    """The mutation runs with no session temporary tables, so a same-named one does not grant the read."""
    node = self.context.node
    with mutation_fixture(self, needs=("set",)) as names:
        grant(node, "CREATE TEMPORARY TABLE ON *.*", names["user"])
        grant(node, "TABLE ENGINE ON Memory", names["user"])
        with When("the session can create and read its temporary table"):
            run_as_user(
                node,
                names["user"],
                f"CREATE TEMPORARY TABLE {names['secret_set']} (secret UInt32); "
                f"SELECT count() FROM {names['secret_set']}",
                denied=False,
            )
        with When("the mutation of the same name still needs the permanent table"):
            run_as_user(
                node,
                names["user"],
                f"CREATE TEMPORARY TABLE {names['secret_set']} (secret UInt32); "
                f"ALTER TABLE {names['tab']} DELETE WHERE id IN {names['secret_set']} "
                f"SETTINGS {mutation_settings(0, 'delete', on_cluster=False)}",
                denied=True,
            )


@TestScenario
@Name("unqualified name without grant")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_ObjectResolution("1.0"))
def unqualified_name_without_grant(self):
    """A grant on the session database's same-named table does not cover the mutated database."""
    node = self.context.node
    with mutation_fixture(self, needs=("set", "secret")) as names:
        node.query(f"CREATE DATABASE {names['other_db']}")
        try:
            grant(
                node,
                f"SELECT ON {names['other_db']}.{names['secret_set']}",
                names["user"],
            )
            grant(
                node,
                f"SELECT ON {names['other_db']}.{names['secret_tab']}",
                names["user"],
            )
            settings = [("database", names["other_db"])]
            settings_sql = mutation_settings(0, "delete", on_cluster=False)
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['db']}.{names['tab']} DELETE WHERE id IN {names['secret_set']} "
                f"SETTINGS {settings_sql}",
                denied=True,
                extra_settings=settings,
            )
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['db']}.{names['tab']} DELETE WHERE id IN "
                f"(SELECT secret FROM {names['secret_tab']}) SETTINGS {settings_sql}",
                denied=True,
                extra_settings=settings,
            )
        finally:
            node.query(f"DROP DATABASE IF EXISTS {names['other_db']}")


@TestScenario
@Name("unqualified name with grant")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_ObjectResolution("1.0"))
def unqualified_name_with_grant(self):
    """With the grant on the mutated database, the same unqualified names are accepted."""
    node = self.context.node
    with mutation_fixture(self, needs=("set", "secret")) as names:
        node.query(f"CREATE DATABASE {names['other_db']}")
        try:
            grant(node, f"SELECT ON {names['secret_set']}", names["user"])
            grant(node, f"SELECT ON {names['secret_tab']}", names["user"])
            session = [("database", names["other_db"])]
            settings_sql = mutation_settings(0, "delete", on_cluster=False)
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['db']}.{names['tab']} DELETE WHERE id IN {names['secret_set']} AND 0 "
                f"SETTINGS {settings_sql}",
                denied=False,
                extra_settings=session,
            )
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['db']}.{names['tab']} UPDATE name = "
                f"(SELECT max(payload) FROM {names['secret_tab']}) WHERE 0 "
                f"SETTINGS {mutation_settings(0, 'update', on_cluster=False)}",
                denied=False,
                extra_settings=session,
            )
        finally:
            node.query(f"DROP DATABASE IF EXISTS {names['other_db']}")


@TestScenario
@Name("stored mutation reads mutated database")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_ObjectResolution("1.0"))
def stored_mutation_reads_mutated_database(self):
    """An unqualified dictGet is the dictionary in the mutated table's database, not the session's."""
    node = self.context.node
    with mutation_fixture(self, needs=("dict",)) as names:
        node.query(f"CREATE DATABASE {names['other_db']}")
        other_src = f"{names['other_db']}.dict_src"
        other_dict = f"{names['other_db']}.{names['dict']}"
        try:
            node.query(
                f"CREATE TABLE {other_src} (key UInt64, payload String) "
                f"ENGINE = MergeTree ORDER BY key"
            )
            node.query(f"INSERT INTO {other_src} VALUES (1, 'from-other-dict')")
            node.query(
                f"CREATE DICTIONARY {other_dict} (key UInt64, payload String) PRIMARY KEY key "
                f"SOURCE(CLICKHOUSE(HOST 'localhost' PORT tcpPort() USER 'default' "
                f"TABLE 'dict_src' PASSWORD '' DB '{names['other_db']}')) "
                f"LAYOUT(FLAT()) LIFETIME(0)"
            )
            grant(node, f"dictGet ON {names['dict']}", names["user"])
            grant(node, f"dictGet ON {other_dict}", names["user"])
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['db']}.{names['tab']} UPDATE name = "
                f"dictGet('{names['dict']}', 'payload', toUInt64(id)) WHERE id = 1 "
                f"SETTINGS {mutation_settings(0, 'update', on_cluster=False)}",
                denied=False,
                extra_settings=[("database", names["other_db"])],
            )
            stored = node.query(
                f"SELECT name FROM {names['tab']} WHERE id = 1"
            ).output.strip()
            assert stored == "from-dict", error()
        finally:
            node.query(f"DROP DICTIONARY IF EXISTS {other_dict}")
            node.query(f"DROP DATABASE IF EXISTS {names['other_db']}")


@TestScenario
@Name("dictGet name that is not one object")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_ObjectResolution("1.0"))
def dictget_name_that_is_not_one_object(self):
    """A dictGet argument that is not one constant string requires the privilege on every dictionary."""
    node = self.context.node
    with mutation_fixture(self, needs=("dict", "dim")) as names:
        grant(node, f"dictGet ON {names['dict']}", names["user"])
        grant(node, f"SELECT ON {names['dim']}", names["user"])
        node.query(
            f"ALTER TABLE {names['tab']} ADD COLUMN {names['dict']} String DEFAULT ''"
        )
        settings = mutation_settings(0, "update", on_cluster=False)
        dictionary = f"{names['db']}.{names['dict']}"
        dict_name = names["dict"]
        statements = (
            f"dictGet(concat('{names['db']}', '.{dict_name}'), 'payload', toUInt64(id))",
            f"(SELECT dictGet({dict_name}, 'payload', toUInt64(1)) "
            f"FROM (SELECT '{dictionary}' AS {dict_name}) s)",
            f"dictGet({dict_name}, 'payload', toUInt64(id))",
            f"(WITH materialize('{dictionary}') AS d SELECT dictGet(d, 'payload', toUInt64(1)))",
        )
        for statement in statements:
            with When(statement):
                run_as_user(
                    node,
                    names["user"],
                    f"ALTER TABLE {names['tab']} UPDATE name = {statement} WHERE 0 "
                    f"SETTINGS {settings}",
                    denied=True,
                )


@TestScenario
@Name("dictGet string alias is that object")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_ObjectResolution("1.0"))
def dictget_string_alias_is_that_object(self):
    """A WITH alias or a query alias that is one constant string names that dictionary."""
    node = self.context.node
    with mutation_fixture(self, needs=("dict", "dim")) as names:
        grant(node, f"dictGet ON {names['dict']}", names["user"])
        grant(node, f"SELECT ON {names['dim']}", names["user"])
        settings = mutation_settings(0, "update", on_cluster=False)
        dictionary = f"{names['db']}.{names['dict']}"
        statements = (
            f"(WITH '{dictionary}' AS d SELECT dictGet(d, 'payload', toUInt64(1)))",
            f"(SELECT dictGet(d, 'payload', toUInt64(1)) FROM {names['dim']} "
            f"WHERE ('{dictionary}' AS d) != '')",
        )
        for statement in statements:
            with When(statement):
                run_as_user(
                    node,
                    names["user"],
                    f"ALTER TABLE {names['tab']} UPDATE name = {statement} WHERE 0 "
                    f"SETTINGS {settings}",
                    denied=False,
                )


@TestScenario
@Name("joinGet attribute without key")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess("1.0"))
def joinget_attribute_without_key(self):
    """joinGet reads the key columns of the Join table as well as the attribute it returns."""
    node = self.context.node
    with mutation_fixture(self, needs=("join",)) as names:
        grant(node, f"SELECT(payload) ON {names['join_tab']}", names["user"])
        run_as_user(
            node,
            names["user"],
            f"ALTER TABLE {names['tab']} UPDATE name = "
            f"joinGet('{names['db']}.{names['join_tab']}', 'payload', id) WHERE 0 "
            f"SETTINGS {mutation_settings(0, 'update', on_cluster=False)}",
            denied=True,
        )


@TestScenario
@Name("joinGet with key columns")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess("1.0"))
def joinget_with_key_columns(self):
    """SELECT on the attribute and the key columns allows joinGet."""
    node = self.context.node
    with mutation_fixture(self, needs=("join",)) as names:
        grant(node, f"SELECT(payload, id) ON {names['join_tab']}", names["user"])
        run_as_user(
            node,
            names["user"],
            f"ALTER TABLE {names['tab']} UPDATE name = "
            f"joinGet('{names['db']}.{names['join_tab']}', 'payload', id) WHERE 0 "
            f"SETTINGS {mutation_settings(0, 'update', on_cluster=False)}",
            denied=False,
        )


@TestScenario
@Name("nested indirect read")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess("1.0"))
def nested_indirect_read(self):
    """A read under a subquery, including a JOIN condition, is still a read."""
    node = self.context.node
    for (entry_name, kind), where in product(entry_points(), NESTED_READS):
        with When(f"{entry_name} {where}"):
            with mutation_fixture(
                self, needs=("readable", "dim", "set", "dict")
            ) as names:
                grant(node, f"SELECT ON {names['readable']}", names["user"])
                grant(node, f"SELECT ON {names['dim']}", names["user"])
                sql = mutation_statement(
                    kind,
                    names["tab"],
                    where.format(**names),
                    "name = name",
                    mutation_settings(0, kind, on_cluster=False),
                    on_cluster=False,
                )
                run_as_user(node, names["user"], sql, denied=True)


@TestScenario
@Name("array join column")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess("1.0"))
def array_join_column(self):
    """A column used only by ARRAY JOIN is read."""
    node = self.context.node
    with mutation_fixture(self, needs=("readable",)) as names:
        grant(node, f"SELECT(id, arr) ON {names['readable']}", names["user"])
        for validate in (0, 1):
            with When(f"validate={validate}"):
                run_as_user(
                    node,
                    names["user"],
                    f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
                    f"(SELECT id FROM {names['readable']} ARRAY JOIN hidden_arr AS elem) "
                    f"SETTINGS {mutation_settings(validate, 'delete', on_cluster=False)}",
                    denied=True,
                )


@TestScenario
@Name("table function without source grant")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess("1.0"))
def table_function_without_source_grant(self):
    """file() and view(SELECT ...) require the source access of the call."""
    node = self.context.node
    with mutation_fixture(self, needs=("secret",)) as names:
        settings = mutation_settings(0, "delete", on_cluster=False)
        statements = (
            f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
            f"file('mutation_read_access_no_such.tsv', 'TSV', 'id UInt32') SETTINGS {settings}",
            f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
            f"(SELECT id FROM file('mutation_read_access_no_such.tsv', 'TSV', 'id UInt32')) "
            f"SETTINGS {settings}",
            f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
            f"(SELECT secret FROM view(SELECT secret FROM {names['secret_tab']})) SETTINGS {settings}",
            f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
            f"(SELECT secret FROM view(SELECT secret FROM view(SELECT secret FROM {names['secret_tab']}))) "
            f"SETTINGS {settings}",
            f"DELETE FROM {names['tab']} WHERE id IN "
            f"(SELECT secret FROM view(SELECT secret FROM {names['secret_tab']})) SETTINGS {settings}",
        )
        for statement in statements:
            with When(statement):
                run_as_user(node, names["user"], statement, denied=True)


@TestScenario
@Name("table function with source grant")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess("1.0"))
def table_function_with_source_grant(self):
    """With the source grant the same calls are not denied. numbers() needs no grant."""
    node = self.context.node
    with mutation_fixture(self, needs=("secret",)) as names:
        settings = mutation_settings(0, "delete", on_cluster=False)
        with When("numbers() needs no grant"):
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
                f"(SELECT number FROM numbers(2)) AND 0 SETTINGS {settings}",
                denied=False,
            )
        with When("view() with SELECT on the table it reads is accepted"):
            grant(node, f"SELECT ON {names['secret_tab']}", names["user"])
            run_as_user(
                node,
                names["user"],
                f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
                f"(SELECT secret FROM view(SELECT secret FROM {names['secret_tab']})) AND 0 "
                f"SETTINGS {settings}",
                denied=False,
            )

    # id IN file(path, format, structure) is accepted with the source grants and
    # then cannot finish: the stored predicate calls the scalar file() function.
    # Keep it on its own table and do not wait for it.
    with mutation_fixture(self) as names:
        with When("file() with its source grants is not an access denial"):
            grant(node, "READ ON FILE", names["user"])
            grant(node, "CREATE TEMPORARY TABLE ON *.*", names["user"])
            assert_not_access_denied(
                node,
                names["user"],
                f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
                f"file('mutation_read_access_no_such.tsv', 'TSV', 'id UInt32') AND 0 "
                f"SETTINGS validate_mutation_query = 0, mutations_sync = 0",
            )
            node.query(
                f"KILL MUTATION WHERE database = 'default' AND table = '{names['tab']}' SYNC"
            )


@TestScenario
@Name("grant dependent table function")
@Requirements(
    RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess_GrantDependentTableFunction("1.0")
)
def grant_dependent_table_function(self):
    """viewIfPermitted and mergeTreeTextIndex cannot be stored in a mutation, for any user."""
    node = self.context.node
    with mutation_fixture(self) as names:
        settings = mutation_settings(0, "delete", on_cluster=False)
        view_if = (
            f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
            f"(SELECT id FROM viewIfPermitted(SELECT id FROM {names['tab']} "
            f"ELSE null('id UInt32'))) SETTINGS {settings}"
        )
        with When(
            "viewIfPermitted is refused for the restricted user and for the default user"
        ):
            assert_refused(node, view_if, user=names["user"])
            assert_refused(node, view_if)
        present = node.query(
            "SELECT count() FROM system.table_functions WHERE name = 'mergeTreeTextIndex'"
        ).output.strip()
        if present != "0":
            with When("mergeTreeTextIndex is refused"):
                text_index = (
                    f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
                    f"(SELECT 1 FROM mergeTreeTextIndex('{names['db']}', '{names['tab']}', 'idx')) "
                    f"SETTINGS {settings}"
                )
                assert_refused(node, text_index, user=names["user"])
                assert_refused(node, text_index)
        with When("a plain view() of a table the default user can read is not refused"):
            node.query(
                f"ALTER TABLE {names['tab']} DELETE WHERE id IN "
                f"(SELECT id FROM view(SELECT id FROM {names['tab']} WHERE 0)) AND 0 "
                f"SETTINGS {settings}"
            )


@TestScenario
@Name("kill mutation does not require select")
@Requirements(RQ_SRS_006_RBAC_Privileges_KillMutation_ReadAccess("1.0"))
def kill_mutation_does_not_require_select(self):
    """KILL MUTATION needs the mutation privilege, not SELECT on the predicate it kills."""
    node = self.context.node
    with mutation_fixture(self) as names:
        node.query(
            f"ALTER TABLE {names['tab']} UPDATE name = name WHERE hidden = 7 "
            f"SETTINGS mutations_sync = 0"
        )
        if check_clickhouse_version(">=24.4")(self):
            grant(node, "SELECT ON system.mutations", names["user"])
        run_as_user(
            node,
            names["user"],
            f"KILL MUTATION WHERE database = 'default' AND table = '{names['tab']}' AND is_done = 0",
            denied=False,
        )


@TestFeature
@Name("mutation read access")
@Requirements(RQ_SRS_006_RBAC_Privileges_Mutation_ReadAccess("1.0"))
def feature(self, node="clickhouse1"):
    """SELECT and the other read privileges a mutation needs, independent of validate_mutation_query."""
    self.context.node = self.context.cluster.node(node)

    for scenario in (
        combinations,
        partial_grants,
        on_cluster,
        replicated_database,
        readable_and_virtual_columns,
        real_column_shadowing_virtual,
        one_part_in_name_is_a_table,
        with_and_alias_scope,
        temporary_table_is_not_grant_free,
        unqualified_name_without_grant,
        unqualified_name_with_grant,
        stored_mutation_reads_mutated_database,
        dictget_name_that_is_not_one_object,
        dictget_string_alias_is_that_object,
        joinget_attribute_without_key,
        joinget_with_key_columns,
        nested_indirect_read,
        array_join_column,
        table_function_without_source_grant,
        table_function_with_source_grant,
        grant_dependent_table_function,
        kill_mutation_does_not_require_select,
    ):
        Scenario(run=scenario)
