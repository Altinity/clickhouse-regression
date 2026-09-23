"""IF NOT EXISTS, concurrent creators, leftover metadata and the no-trace
rule (plan §3.8)."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import *

COLUMNS = ["id Int64", "name String"]


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_IfNotExists("1.0"))
@Examples("creator", [("clickhouse",), ("pyiceberg",)])
def if_not_exists_on_existing_table(self, creator):
    """B3: IF NOT EXISTS over a registered table (whoever created it) succeeds
    and changes nothing; without it the statement is TABLE_ALREADY_EXISTS."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    ch_name = clickhouse_table_name(database_name, namespace, table_name)
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with Given(f"a table created by {creator} with one row"):
        if creator == "clickhouse":
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                columns=COLUMNS,
            )
            insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1, 'a')")
        else:
            pyiceberg_table(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                rows=[{"id": 1, "name": "a"}],
            )
        before = snapshot_state(**args)

    for path in (ENGINE_LESS, EXPLICIT_ENGINE):
        with When(f"CREATE TABLE IF NOT EXISTS via {path} with a different schema"):
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                path=path,
                columns=["other UInt8"],
                if_not_exists=True,
                purge_on_exit=False,
            )

        with Then("nothing changed, the original schema and row remain"):
            after = snapshot_state(**args)
            assert_state_unchanged(before=before, after=after)
            check_column_value(table_name=ch_name, expected="1\ta")

        with When(f"CREATE TABLE via {path} without IF NOT EXISTS"):
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                path=path,
                columns=["other UInt8"],
                exitcode=TABLE_ALREADY_EXISTS,
                message="already exists",
                purge_on_exit=False,
            )

        with Then("still nothing changed"):
            after = snapshot_state(**args)
            assert_state_unchanged(before=before, after=after)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_IfNotExists("1.0"))
def if_not_exists_as_select_does_not_fill(self):
    """B3: CREATE TABLE IF NOT EXISTS ... AS SELECT over an existing table
    inserts nothing."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    ch_name = clickhouse_table_name(database_name, namespace, table_name)
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with Given("a table with one row"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            columns=COLUMNS,
        )
        insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1, 'a')")
        before = snapshot_state(**args)

    with When("CREATE TABLE IF NOT EXISTS ... AS SELECT"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            if_not_exists=True,
            as_select="SELECT number AS id, 'x' AS name FROM numbers(5)",
            purge_on_exit=False,
        )

    with Then("row count is still one and no object was added"):
        after = snapshot_state(**args)
        assert_state_unchanged(before=before, after=after)
        got = self.context.node.query(f"SELECT count() FROM {ch_name}").output.strip()
        assert got == "1", error(got)


@TestStep(When)
def start_create(self, node, tag, database_name, namespace, table_name, if_not_exists):
    """Launch one racing CREATE as a background `clickhouse client` inside the
    container and return at once. The query goes through a file, the client's
    output and exit code land in `/tmp/race_<tag>.{out,rc}`.

    Racing through background processes rather than parallel TestFlows steps
    keeps the test process single-threaded: two threads opening a shell to the
    same node at the same moment crashed the test runner (segfault, 2026-09-22).
    """
    import base64

    query = build_create_table_query(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        columns=COLUMNS,
        if_not_exists=if_not_exists,
    )
    # clickhouse_table_name escapes backticks for the shell; the file is read verbatim.
    encoded = base64.b64encode(query.replace("\\`", "`").encode()).decode()
    # The namespace is pre-created per round; a loser that reaches the catalog's
    # createTable still pays ~33 s of 409 retries (findings.md #3, #6). A query-level
    # http_max_tries does not reach the catalog's HTTP client, so no workaround here.
    node.command(
        f"echo {encoded} | base64 -d > /tmp/race_{tag}.sql && rm -f /tmp/race_{tag}.rc && "
        f"bash -c '( clickhouse client --queries-file /tmp/race_{tag}.sql "
        f"> /tmp/race_{tag}.out 2>&1 < /dev/null; echo $? > /tmp/race_{tag}.rc ) &'",
        exitcode=0,
    )


@TestStep(Then)
def wait_create(self, node, tag, timeout=180):
    """Wait for a racing CREATE started by `start_create`; returns
    ``(node name, exit code, output)``."""
    import re as _re

    for attempt in retries(timeout=timeout, delay=0.5):
        with attempt:
            rc = node.command(f"cat /tmp/race_{tag}.rc", no_checks=True)
            assert rc.exitcode == 0 and _re.search(r"\d+", rc.output), error(
                "still running"
            )
    exitcode = int(_re.search(r"\d+", rc.output).group())
    output = node.command(f"cat /tmp/race_{tag}.out", no_checks=True).output.strip()
    node.command(
        f"rm -f /tmp/race_{tag}.sql /tmp/race_{tag}.out /tmp/race_{tag}.rc",
        no_checks=True,
    )
    return (node.name, exitcode, output)


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_IfNotExists_ConcurrentCreate("1.0"))
@Examples("if_not_exists rounds", [(False, 5), (True, 5)])
def concurrent_creators_on_three_nodes(self, if_not_exists, rounds):
    """F3: three nodes with their own databases over one catalog race to
    create the same table; each round ends with exactly one table, one
    initial metadata file, and the expected split of OK / TABLE_ALREADY_EXISTS."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    nodes = all_nodes(self)
    if len(nodes) < 3:
        skip("needs three nodes")

    with Given("a catalog handle and a database on every node"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=nodes[0],
        )
        databases = {nodes[0].name: database_name}
        for node in nodes[1:]:
            databases[node.name] = datalake_database(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                node=node,
            )

    conflicts_seen = 0

    for round_no in range(rounds):
        # A fresh namespace per round, created up front by PyIceberg, so the race
        # is about the table: otherwise the first creator also wins the namespace
        # and the others spend ~33 s retrying a 409 first (findings.md #3).
        namespace = f"ns_{round_no}_{getuid()}"
        with Given(f"round {round_no}: namespace {namespace} exists"):
            catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
        table_name = f"t_{round_no}_{getuid()}"
        args = dict(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            database_name=database_name,
        )
        with When(
            f"round {round_no}: all nodes CREATE {'IF NOT EXISTS ' if if_not_exists else ''}{table_name}"
        ):
            before = snapshot_state(**args)
            tags = {node.name: f"{node.name}_{round_no}_{getuid()}" for node in nodes}
            for node in nodes:
                start_create(
                    node=node,
                    tag=tags[node.name],
                    database_name=databases[node.name],
                    namespace=namespace,
                    table_name=table_name,
                    if_not_exists=if_not_exists,
                )
            results = [wait_create(node=node, tag=tags[node.name]) for node in nodes]

        with Then("exactly one creator won"):
            note(results)
            ok = [r for r in results if r[1] == 0]
            failed = [r for r in results if r[1] != 0]
            if if_not_exists:
                assert len(ok) == len(nodes), error(
                    f"IF NOT EXISTS should never fail: {failed}"
                )
            else:
                assert len(ok) == 1, error(
                    f"expected one winner, got {len(ok)}: {results}"
                )
                for _, code, output in failed:
                    assert code == TABLE_ALREADY_EXISTS, error(
                        f"loser failed with {code}: {output}"
                    )
            for _, _, output in failed:
                if "already exists" in output or "already present" in output:
                    conflicts_seen += 1
                    note(
                        f"detection path: {'leftover files' if 'already present' in output else 'catalog conflict'}"
                    )

        with And("one table, one initial metadata file, visible everywhere"):
            after = snapshot_state(**args)
            assert_table_created(before=before, after=after)
            check_state_invariants(**args, expected=PRESENT, state=after)

        with Finally(f"drop {table_name} with purge"):
            drop_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                purge=1,
                node=nodes[0],
            )

    note(f"loser paths observed across {rounds} rounds: {conflicts_seen}")


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_IfNotExists_ConcurrentCreate("1.0"))
def concurrent_creators_on_one_node(self):
    """F3 on a single node: two parallel CREATEs in the same database."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    node = self.context.node
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )
    with When("two parallel CREATE TABLE without IF NOT EXISTS"):
        before = snapshot_state(**args)
        tags = [f"one_node_{i}_{getuid()}" for i in range(2)]
        for tag in tags:
            start_create(
                node=node,
                tag=tag,
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                if_not_exists=False,
            )
        results = [wait_create(node=node, tag=tag) for tag in tags]

    with Then("one OK, one TABLE_ALREADY_EXISTS, one table"):
        note(results)
        codes = sorted(r[1] for r in results)
        assert codes == [0, TABLE_ALREADY_EXISTS], error(results)
        after = snapshot_state(**args)
        assert_table_created(before=before, after=after)

    with Finally("drop with purge"):
        drop_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            purge=1,
        )


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_LeftoverMetadata("1.0"))
@Examples("creator", [("clickhouse",), ("pyiceberg",)])
def leftover_metadata_after_keep_drop(self, creator):
    """B4: with metadata files left at the location by a keep-drop, the
    explicit-engine CREATE is refused (naming the purge setting), and with
    IF NOT EXISTS succeeds while registering nothing; the files are untouched.

    The engine-less path hands the write to the REST server, which may or
    may not refuse to place a new table over old files; that outcome is
    recorded, and the invariants are checked either way.
    """
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    ch_name = clickhouse_table_name(database_name, namespace, table_name)
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with Given(f"a table created by {creator}, then dropped keeping its data"):
        if creator == "clickhouse":
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                columns=COLUMNS,
                purge_on_exit=False,
            )
            insert_into_native_iceberg_table(table_name=ch_name, values_sql="(1, 'a')")
            drop_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                purge=0,
            )
        else:
            pyiceberg_table(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                rows=[{"id": 1, "name": "a"}],
            )
            catalog.drop_table(table_identifier(namespace, table_name))
        before = snapshot_state(**args)
        assert not before.catalog_table and before.metadata_files, error(
            before.describe()
        )

    with When("explicit-engine CREATE TABLE over the leftovers"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=EXPLICIT_ENGINE,
            columns=COLUMNS,
            exitcode=TABLE_ALREADY_EXISTS,
            message=PURGE_SETTING,
            purge_on_exit=False,
        )

    with Then("nothing changed"):
        after = snapshot_state(**args)
        assert_state_unchanged(before=before, after=after)

    with When("explicit-engine CREATE TABLE IF NOT EXISTS over the leftovers"):
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=EXPLICIT_ENGINE,
            columns=COLUMNS,
            if_not_exists=True,
            purge_on_exit=False,
        )

    with Then("success, yet the table is absent and the files untouched"):
        after = snapshot_state(**args)
        assert_state_unchanged(before=before, after=after)
        check_state_invariants(
            **args, expected=ABSENT_DATA_KEPT, before=before, state=after
        )

    with When("engine-less CREATE TABLE over the leftovers (server-side write)"):
        result = self.context.node.query(
            build_create_table_query(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                columns=COLUMNS,
            ),
            no_checks=True,
        )

    with Then(
        "either refused with nothing changed, or created with the old files untouched"
    ):
        after = snapshot_state(**args)
        if result.exitcode == 0:
            note("REST server created the table over the leftover files")
            assert after.catalog_table, error("OK reported but table not registered")
            for key, value in before.objects.items():
                assert after.objects.get(key) == value, error(
                    f"leftover {key} was modified or removed"
                )
            check_state_invariants(**args, expected=PRESENT, state=after)
        else:
            note(f"engine-less create refused: {result.output.strip()[:200]}")
            assert result.exitcode == TABLE_ALREADY_EXISTS, error(result.output)
            assert_state_unchanged(before=before, after=after)

    with Finally("clean up"):
        self.context.node.query(
            f"DROP TABLE IF EXISTS {ch_name}",
            settings=[(PURGE_SETTING, 1)],
            no_checks=True,
        )
        s3.delete_prefix(after.prefix)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_LeftoverMetadata("1.0"))
def path_based_if_not_exists_attaches(self):
    """Contrast to B4: outside any catalog, IF NOT EXISTS over existing
    metadata attaches to it and reads the old rows."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    node = self.context.node
    key = f"pathbased_{getuid()}"
    engine = f"IcebergS3('http://minio:9000/warehouse/{key}/', '{minio_root_user}', '{minio_root_password}')"
    first, second = f"default.pb1_{getuid()}", f"default.pb2_{getuid()}"

    try:
        with Given("a path-based table with a row, dropped keeping data"):
            node.query(
                f"CREATE TABLE {first} (id Int64) ENGINE = {engine}",
                settings=[("write_full_path_in_iceberg_metadata", 1)],
            )
            node.query(
                f"INSERT INTO {first} VALUES (42)",
                inline_settings=[("allow_insert_into_iceberg", 1)],
            )
            node.query(f"DROP TABLE {first} SYNC", settings=[(PURGE_SETTING, 0)])
            before = s3.object_inventory(f"{key}/")
            assert before, error("no leftovers")

        with When("CREATE TABLE IF NOT EXISTS at the same path"):
            node.query(
                f"CREATE TABLE IF NOT EXISTS {second} (id Int64) ENGINE = {engine}"
            )

        with Then("it attaches to the old metadata and reads the old row"):
            assert s3.object_inventory(f"{key}/") == before, error(
                "attach modified objects"
            )
            got = node.query(f"SELECT id FROM {second}").output.strip()
            assert got == "42", error(got)
    finally:
        with Finally("cleanup"):
            node.query(f"DROP TABLE IF EXISTS {first} SYNC", no_checks=True)
            node.query(f"DROP TABLE IF EXISTS {second} SYNC", no_checks=True)
            s3.delete_prefix(f"{key}/")


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_FailedCreateLeavesNoTrace("1.0"))
def no_trace_after_each_rejection_class(self):
    """B2 across one representative of every validation class, in a fresh
    namespace: no table, no namespace, no object."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    cases = {
        "bad transform": dict(partition_by="toYYYYMM(d)", exitcode=BAD_ARGUMENTS),
        "bad modifier": dict(
            columns=["id Int64 DEFAULT 1", "d Date"], exitcode=BAD_ARGUMENTS
        ),
        "bad clause": dict(
            order_by="id", storage_clauses="PRIMARY KEY id", exitcode=BAD_ARGUMENTS
        ),
        "non-Iceberg engine": dict(
            path=EXPLICIT_ENGINE,
            engine="MergeTree",
            order_by="id",
            exitcode=BAD_ARGUMENTS,
        ),
        "empty column list": dict(columns=[], exitcode=INCORRECT_QUERY),
    }
    for label, extra in cases.items():
        with Check(label, flags=TE):
            namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
            args = dict(
                catalog=catalog,
                namespace=namespace,
                table_name=table_name,
                database_name=database_name,
            )
            kwargs = dict(columns=["id Int64", "d Date"])
            kwargs.update(extra)
            with By("snapshot state"):
                before = snapshot_state(**args)
            assert not before.catalog_namespace, error("fresh namespace already exists")
            create_table(
                database_name=database_name,
                namespace=namespace,
                table_name=table_name,
                **kwargs,
            )
            with By("snapshot state"):
                after = snapshot_state(**args)
            assert_rejected_no_trace(
                before=before, after=after, namespace_expected=False
            )
            assert after.objects == {}, error(f"objects left: {sorted(after.objects)}")


@TestFeature
@Name("idempotency")
def feature(self, minio_root_user, minio_root_password):
    """IF NOT EXISTS, races, leftovers and the no-trace rule."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
