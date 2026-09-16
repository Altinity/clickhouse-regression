import re
from dataclasses import dataclass, field

import pyiceberg.exceptions

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import Column, create_table as helpers_create_table

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine
import iceberg.tests.steps.s3_objects as s3


class RawType:
    """Minimal DataType shim for a raw ClickHouse type name string.

    Use this for types that have no dedicated class in helpers/datatypes (e.g.
    ``DateTime64(6, 'UTC')``).  Column.full_definition() only reads `.name`,
    so this is sufficient.
    """

    def __init__(self, name):
        self.name = name


def clickhouse_table_name(database_name, namespace, table_name):
    """Return the backtick-escaped ClickHouse identifier for a table that lives
    inside a DataLakeCatalog database.

    Example:
        ``mydb.`mynamespace.mytable```
    """
    return f"{database_name}.\\`{namespace}.{table_name}\\`"


def iceberg_s3_engine(namespace, table_name, minio_root_user, minio_root_password):
    """Return the IcebergS3 engine clause for a natively created Iceberg table."""
    return (
        f"IcebergS3('http://minio:9000/warehouse/data/{namespace}/{table_name}/', "
        f"'{minio_root_user}', '{minio_root_password}')"
    )


@TestStep(Given)
def database_only_setup(
    self,
    minio_root_user,
    minio_root_password,
    database_name=None,
):
    """Create a DataLakeCatalog database only.

    The namespace is **not** pre-created via PyIceberg; ClickHouse registers
    it in the catalog automatically when the first native ``CREATE TABLE``
    is issued under that namespace identifier.

    Returns ``(namespace, database_name)`` where *namespace* is a fresh UUID
    string that callers embed in their table names.
    """
    namespace = f"ns_{getuid()}"
    if database_name is None:
        database_name = f"datalake_db_{getuid()}"

    with By("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            default_base_location=database_base_location(AUTO),
        )

    return namespace, database_name


@TestStep(Given)
def catalog_namespace_and_database(
    self,
    minio_root_user,
    minio_root_password,
    namespace=None,
    database_name=None,
):
    """Create an Iceberg catalog, a namespace inside it, and a DataLakeCatalog
    database in ClickHouse that points at that catalog.

    Returns a (catalog, namespace, database_name) tuple so callers can
    reference the catalog objects for PyIceberg-side verification.
    """
    if namespace is None:
        namespace = f"namespace_{getuid()}"
    if database_name is None:
        database_name = f"datalake_db_{getuid()}"

    with By("create iceberg catalog"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    with By("create namespace"):
        catalog_steps.create_namespace(catalog=catalog, namespace=namespace)

    with By("create DataLakeCatalog database"):
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            default_base_location=database_base_location(AUTO),
        )

    return catalog, namespace, database_name


@TestStep(Given)
def native_iceberg_table(
    self,
    database_name,
    namespace,
    table_name,
    minio_root_user,
    minio_root_password,
    columns,
    order_by=None,
    partition_by=None,
    node=None,
    exitcode=None,
    message=None,
    path=None,
):
    """Create an Iceberg table natively via ClickHouse ``CREATE TABLE`` inside
    a DataLakeCatalog database.

    ``path`` selects the creation form (``ENGINE_LESS`` or ``EXPLICIT_ENGINE``);
    when omitted it comes from ``self.context.create_path`` so a feature can run
    the same scenarios under both forms, defaulting to the explicit engine.

    On the explicit path it delegates to ``helpers.tables.create_table`` so the
    table is automatically dropped when the test finishes and returns its
    ``Table`` object; on the engine-less path it delegates to :func:`create_table`
    of this module.
    """
    if path is None:
        path = getattr(self.context, "create_path", EXPLICIT_ENGINE)
    if path == ENGINE_LESS:
        return create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=ENGINE_LESS,
            columns=columns,
            order_by=order_by,
            partition_by=partition_by,
            node=node,
            exitcode=exitcode,
            message=message,
        )
    return helpers_create_table(
        name=clickhouse_table_name(database_name, namespace, table_name),
        engine=iceberg_s3_engine(namespace, table_name, minio_root_user, minio_root_password),
        columns=columns,
        query_settings="write_full_path_in_iceberg_metadata = 1",
        order_by=order_by,
        partition_by=partition_by,
        node=node,
        exitcode=exitcode,
        message=message,
    )


@TestStep(When)
def insert_into_native_iceberg_table(
    self,
    table_name,
    values_sql,
    node=None,
):
    """INSERT a VALUES row into a natively created Iceberg table.

    ``table_name`` must be the fully-qualified ClickHouse name as returned by
    :func:`clickhouse_table_name`.  ``values_sql`` is a parenthesised
    VALUES expression, e.g. ``"(42, 'hello')"``.

    Sets ``allow_insert_into_iceberg = 1`` inline so the query does not
    require a prior SET statement.
    """
    if node is None:
        node = self.context.node
    node.query(
        f"INSERT INTO {table_name} VALUES {values_sql}",
        inline_settings=[("allow_insert_into_iceberg", 1)],
    )


@TestStep(Then)
def check_column_value(
    self,
    table_name,
    expected,
    columns="*",
    order_by="tuple(*)",
    node=None,
):
    """SELECT from a natively created Iceberg table and assert that *expected*
    appears somewhere in the TabSeparated output.

    ``expected`` is converted to ``str`` before the comparison so callers can
    pass Python scalars directly.

    Returns the raw query result for further assertions.
    """
    if node is None:
        node = self.context.node
    result = node.query(
        f"SELECT {columns} FROM {table_name} ORDER BY {order_by} FORMAT TabSeparated"
    )
    assert str(expected) in result.output, error()
    return result


# ---------------------------------------------------------------------------
# State observers and invariant checks
#
# See ``invariants.md`` next to this file. Every scenario in the package
# brackets each CREATE / DROP with ``snapshot_state`` (section B of the
# invariants) and ends with ``check_state_invariants`` (section A), so the
# same three observers - catalog, object storage, ClickHouse on every node -
# judge every outcome the same way.
# ---------------------------------------------------------------------------

DEFAULT_BASE_LOCATION = "s3://warehouse/data"

INITIAL_METADATA_NAME = re.compile(
    r"^(v1(-[0-9a-f-]{36})?(\.[a-z0-9]+)?|00000-[0-9a-f-]{36})\.metadata\.json$"
)

PRESENT = "present"
ABSENT_DATA_KEPT = "absent-data-kept"
ABSENT_PURGED = "absent-purged"


def expected_table_location(namespace, table_name, base_location=None):
    """``<base>/<namespace>/<table>`` as invariant A5 requires it: no trailing
    slash, no double slash, dots in a nested namespace kept as they are."""
    base = (base_location or DEFAULT_BASE_LOCATION).rstrip("/")
    return f"{base}/{namespace}/{table_name}"


def table_identifier(namespace, table_name):
    """PyIceberg identifier for ``<namespace>.<table>``; nested namespaces are
    dot-separated already, so a plain string is the right form."""
    return f"{namespace}.{table_name}"


# --- catalog observer -------------------------------------------------------


def catalog_has_table(catalog, namespace, table_name):
    return catalog.table_exists(table_identifier(namespace, table_name))


def catalog_has_namespace(catalog, namespace):
    try:
        catalog.load_namespace_properties(namespace)
        return True
    except pyiceberg.exceptions.NoSuchNamespaceError:
        return False


def catalog_namespace_location(catalog, namespace):
    """The namespace's ``location`` property, or ``None`` if the namespace does
    not exist or reports none."""
    try:
        return catalog.load_namespace_properties(namespace).get("location")
    except pyiceberg.exceptions.NoSuchNamespaceError:
        return None


def catalog_table_info(catalog, namespace, table_name):
    """``(metadata_location, table_location)`` from the catalog, or
    ``(None, None)`` if the table is not registered."""
    try:
        table = catalog.load_table(table_identifier(namespace, table_name))
    except pyiceberg.exceptions.NoSuchTableError:
        return None, None
    return table.metadata_location, table.metadata.location


# --- ClickHouse observer ----------------------------------------------------


def all_nodes(test=None):
    test = test or current()
    nodes = getattr(test.context, "nodes", None)
    return list(nodes) if nodes else [test.context.node]


def nodes_with_database(database_name, test=None):
    """The nodes on which ``database_name`` exists. A fixture database is
    created on one node unless a scenario creates it elsewhere too, and only
    those nodes can be asked about the table (A1, A7)."""
    return [
        node
        for node in all_nodes(test)
        if node.query(f"EXISTS DATABASE {database_name}").output.strip() == "1"
    ]


def clickhouse_table_visible(database_name, namespace, table_name, node):
    """``EXISTS TABLE`` on one node."""
    result = node.query(
        f"EXISTS TABLE {clickhouse_table_name(database_name, namespace, table_name)}"
    )
    return result.output.strip() == "1"


def clickhouse_table_view(database_name, namespace, table_name, node):
    """What a node reports about the table: create statement, described
    columns and row count. Used to prove every node sees the same table (A7)."""
    name = clickhouse_table_name(database_name, namespace, table_name)
    return {
        "show_create": node.query(f"SHOW CREATE TABLE {name}").output.strip(),
        "describe": node.query(f"DESCRIBE TABLE {name} FORMAT TSV").output.strip(),
        "count": node.query(f"SELECT count() FROM {name}").output.strip(),
    }


# --- snapshot ---------------------------------------------------------------


@dataclass
class State:
    """Everything the three observers see for one ``<namespace>.<table>``."""

    namespace: str
    table_name: str
    database_name: str
    prefix: str  # bucket-relative prefix of the table location, with trailing slash
    catalog_table: bool = False
    metadata_location: str = None
    table_location: str = None
    catalog_namespace: bool = False
    namespace_location: str = None
    objects: dict = field(default_factory=dict)  # {key: (etag, size)}
    visible: dict = field(default_factory=dict)  # {node.name: bool}

    @property
    def metadata_files(self):
        return s3.metadata_keys(self.objects)

    def describe(self):
        return (
            f"catalog_table={self.catalog_table} metadata_location={self.metadata_location} "
            f"table_location={self.table_location} catalog_namespace={self.catalog_namespace} "
            f"namespace_location={self.namespace_location} objects={len(self.objects)} "
            f"metadata_files={self.metadata_files} visible={self.visible}"
        )


# ``{(namespace, table): location}`` seen by ``snapshot_state`` so far. Namespaces
# and table names carry a uid per scenario, so a module-level map is safe and
# does not depend on how TestFlows shares ``context`` between steps.
_REMEMBERED_LOCATIONS = {}


def _remembered_locations(test=None):
    return _REMEMBERED_LOCATIONS


@TestStep(When)
def snapshot_state(
    self,
    catalog,
    namespace,
    table_name,
    database_name,
    base_location=None,
    location=None,
):
    """Capture what the catalog, object storage and every ClickHouse node see
    for ``<namespace>.<table>``.

    ``location`` overrides the storage prefix that is inspected; by default it
    is the location the catalog reports for a registered table. For an
    unregistered table it is the location the same table had the last time it
    was snapshotted in this test (so a drop is judged on the prefix the table
    really used, wherever an external writer put it), or else the expected
    ``<base>/<namespace>/<table>``.

    Call inside a ``When``/``Then``/``And``/``By`` context to get the ``State``
    back.
    """
    metadata_location, table_location = catalog_table_info(catalog, namespace, table_name)
    remembered = _remembered_locations(self)
    key = (namespace, table_name)
    inspect = (
        location
        or table_location
        or remembered.get(key)
        or expected_table_location(namespace, table_name, base_location)
    )
    if table_location:
        remembered[key] = table_location
    state = State(
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
        prefix=s3.prefix_from_uri(inspect),
        catalog_table=metadata_location is not None,
        metadata_location=metadata_location,
        table_location=table_location,
        catalog_namespace=catalog_has_namespace(catalog, namespace),
        namespace_location=catalog_namespace_location(catalog, namespace),
    )
    state.objects = s3.object_inventory(state.prefix)
    for node in nodes_with_database(database_name, self):
        state.visible[node.name] = clickhouse_table_visible(
            database_name, namespace, table_name, node
        )
    note(state.describe())
    return state


# --- section A: state invariants -------------------------------------------


@TestStep(Then)
def check_state_invariants(
    self,
    catalog,
    namespace,
    table_name,
    database_name,
    expected,
    base_location=None,
    before=None,
    state=None,
):
    """Assert the state invariants of ``invariants.md`` section A for one table.

    ``expected`` is one of ``PRESENT``, ``ABSENT_DATA_KEPT``, ``ABSENT_PURGED``.
    ``before`` is the ``State`` captured before the scenario's last operation;
    it is needed for A3 in the ``ABSENT_DATA_KEPT`` case, where the leftover
    objects must be exactly the ones that were there before.
    ``state`` lets a caller pass an already captured snapshot.
    """
    if state is None:
        state = snapshot_state(
            catalog=catalog,
            namespace=namespace,
            table_name=table_name,
            database_name=database_name,
            base_location=base_location,
        )

    with By("A1: catalog and every ClickHouse node agree on existence"):
        should_exist = expected == PRESENT
        assert state.catalog_table == should_exist, error(
            f"catalog has table={state.catalog_table}, expected {should_exist}: {state.describe()}"
        )
        for node_name, visible in state.visible.items():
            assert visible == should_exist, error(
                f"node {node_name} sees table={visible}, catalog has it={state.catalog_table}"
            )

    if expected == PRESENT:
        with By("A2: catalog metadata-location names an existing, parseable file"):
            assert state.metadata_location, error("catalog returned no metadata-location")
            key = s3.key_from_uri(state.metadata_location)
            assert key in state.objects, error(
                f"metadata-location {key} is not among objects under {state.prefix}: "
                f"{sorted(state.objects)}"
            )
            metadata = s3.read_json_object(key)
            assert metadata.get("location") == state.table_location, error(
                f"metadata file location {metadata.get('location')!r} != "
                f"catalog location {state.table_location!r}"
            )

        with By("A5: table location is <base>/<namespace>/<table>"):
            expected_location = expected_table_location(namespace, table_name, base_location)
            assert state.table_location == expected_location, error(
                f"catalog location {state.table_location!r} != expected {expected_location!r}"
            )

        with By("A4: namespace location is the namespace base, never a table directory"):
            assert state.catalog_namespace, error("namespace missing while table is present")
            if state.namespace_location is None:
                note("catalog reports no namespace location; A4 not applicable here")
            else:
                ns_location = state.namespace_location.rstrip("/")
                assert not ns_location.endswith(f"/{table_name}"), error(
                    f"namespace location {ns_location!r} ends with the table name"
                )
                assert state.table_location.startswith(ns_location + "/"), error(
                    f"table location {state.table_location!r} is not under "
                    f"namespace location {ns_location!r}"
                )

        with By("A6: location scheme matches the catalog's backend"):
            assert state.table_location.startswith("s3://"), error(
                f"unexpected scheme in {state.table_location!r}"
            )

        with By("A7: every node with the database reports the same table"):
            nodes = nodes_with_database(database_name, self)
            views = {
                node.name: clickhouse_table_view(database_name, namespace, table_name, node)
                for node in nodes
            }
            first = views[nodes[0].name]
            for node_name, view in views.items():
                assert view == first, error(
                    f"node {node_name} disagrees with {nodes[0].name}:\n{view}\nvs\n{first}"
                )

    elif expected == ABSENT_PURGED:
        with By("A3 / B6: nothing is left under the table location"):
            assert state.objects == {}, error(
                f"objects remain under {state.prefix} after purge: {sorted(state.objects)}"
            )

    elif expected == ABSENT_DATA_KEPT:
        with By("A3 / B5: only pre-existing objects remain, none were added"):
            if before is not None:
                assert state.objects == before.objects, error(
                    f"objects under {state.prefix} changed although the table was only "
                    f"unregistered:\nbefore={sorted(before.objects)}\nafter={sorted(state.objects)}"
                )
            else:
                note("no `before` snapshot given; A3 checked only as 'not purged'")
                assert state.metadata_files, error(
                    f"no metadata files under {state.prefix}; data was not kept"
                )

    else:
        raise ValueError(f"unknown expected state {expected!r}")

    return state


# --- section B: transition invariants --------------------------------------


@TestStep(Then)
def assert_state_unchanged(self, before, after):
    """B2, B3, B4, B7: a rejected or no-op statement changed nothing on any
    observer."""
    assert after.prefix == before.prefix, error(
        f"snapshots inspected different prefixes ({before.prefix} vs {after.prefix}); "
        f"pass location= to snapshot_state"
    )
    assert after.catalog_table == before.catalog_table, error(
        f"catalog table presence changed: {before.catalog_table} -> {after.catalog_table}"
    )
    assert after.metadata_location == before.metadata_location, error(
        f"metadata-location changed: {before.metadata_location} -> {after.metadata_location}"
    )
    assert after.catalog_namespace == before.catalog_namespace, error(
        f"namespace presence changed: {before.catalog_namespace} -> {after.catalog_namespace}"
    )
    assert after.objects == before.objects, error(
        f"objects under {before.prefix} changed:\n"
        f"added={sorted(set(after.objects) - set(before.objects))}\n"
        f"removed={sorted(set(before.objects) - set(after.objects))}\n"
        f"modified={sorted(k for k in before.objects if k in after.objects and before.objects[k] != after.objects[k])}"
    )
    assert after.visible == before.visible, error(
        f"visibility changed: {before.visible} -> {after.visible}"
    )


@TestStep(Then)
def assert_table_created(self, before, after, version_hint=False):
    """B1: a successful CREATE added exactly one table, at most one namespace,
    exactly one initial metadata file, no data, and the table is visible and
    empty on every node."""
    with By("table was not there before and is there now"):
        assert not before.catalog_table, error("table already registered before CREATE")
        assert after.catalog_table, error("table not registered after CREATE")

    with By("namespace exists now; if it was created it is this one"):
        assert after.catalog_namespace, error("namespace missing after CREATE")

    with By("exactly one initial metadata file, no data files"):
        added = sorted(set(after.objects) - set(before.objects))
        metadata_added = [k for k in added if k.endswith(".metadata.json")]
        assert len(metadata_added) == 1, error(
            f"expected one new metadata file, got {metadata_added}; all added: {added}"
        )
        name = metadata_added[0].rsplit("/", 1)[-1]
        # ClickHouse names the file it writes itself (explicit engine, Glue)
        # ``v1[-<uuid>][.<ext>].metadata.json``; on the engine-less REST path the
        # catalog server writes it and ice-rest-catalog uses the Java Iceberg
        # convention ``00000-<uuid>.metadata.json``. Both are initial versions.
        assert INITIAL_METADATA_NAME.match(name), error(
            f"initial metadata file is {name}, expected v1*.metadata.json or 00000-<uuid>.metadata.json"
        )
        note(
            f"initial metadata file written by {'ClickHouse' if name.startswith('v1') else 'the catalog server'}: {name}"
        )
        assert s3.key_from_uri(after.metadata_location) == metadata_added[0], error(
            f"catalog metadata-location {after.metadata_location} is not the file written "
            f"{metadata_added[0]}"
        )
        others = [k for k in added if not k.endswith(".metadata.json")]
        allowed = [k for k in others if k.endswith("metadata/version-hint.text")]
        assert others == allowed, error(f"unexpected objects written by CREATE: {others}")
        if version_hint:
            assert allowed, error("version-hint.text expected but not written")
            assert s3.get_object_bytes(allowed[0]).strip() == b"1", error(
                "version-hint.text does not contain 1"
            )

    with By("visible and empty on every node with the database"):
        for node in nodes_with_database(after.database_name, self):
            assert after.visible[node.name], error(f"node {node.name} does not see the table")
            count = node.query(
                f"SELECT count() FROM "
                f"{clickhouse_table_name(after.database_name, after.namespace, after.table_name)}"
            ).output.strip()
            assert count == "0", error(f"node {node.name} counts {count} rows in a new table")


@TestStep(Then)
def assert_table_dropped(self, before, after, purged):
    """B5 / B6: DROP unregistered the table, kept the namespace, and either
    left every object untouched (``purged=False``) or removed all of them
    (``purged=True``)."""
    assert after.prefix == before.prefix, error(
        f"snapshots inspected different prefixes ({before.prefix} vs {after.prefix}); "
        f"pass location= to snapshot_state"
    )
    with By("table was registered before and is gone now"):
        assert before.catalog_table, error("table was not registered before DROP")
        assert not after.catalog_table, error("table still registered after DROP")
        for node_name, visible in after.visible.items():
            assert not visible, error(f"node {node_name} still sees the dropped table")

    with By("namespace survived the drop"):
        assert after.catalog_namespace == before.catalog_namespace, error(
            "namespace presence changed on DROP TABLE"
        )

    if purged:
        with By("every object under the location is gone"):
            assert after.objects == {}, error(
                f"objects remain after purge: {sorted(after.objects)}"
            )
    else:
        with By("every object under the location is untouched"):
            assert after.objects == before.objects, error(
                f"objects changed on a keep-data drop:\n"
                f"before={sorted(before.objects)}\nafter={sorted(after.objects)}"
            )


@TestStep(Then)
def read_registered_metadata(self, catalog, namespace, table_name):
    """Parse the metadata file the catalog currently points at (section D
    checks build on this). Returns ``(metadata_dict, metadata_location)``."""
    metadata_location, _ = catalog_table_info(catalog, namespace, table_name)
    assert metadata_location, error(f"{namespace}.{table_name} is not registered")
    return s3.read_json_object(s3.key_from_uri(metadata_location)), metadata_location


# ---------------------------------------------------------------------------
# The statements under test
# ---------------------------------------------------------------------------

ENGINE_LESS = "engine_less"
EXPLICIT_ENGINE = "explicit_engine"
AS_SOURCE = "as_source"
CREATE_PATHS = [ENGINE_LESS, EXPLICIT_ENGINE, AS_SOURCE]

PURGE_SETTING = "data_lake_delete_data_on_drop"
PURGE_SETTING_ALIAS = "iceberg_delete_data_on_drop"


def column_defs(columns):
    """Render a column list. Each entry is either a raw ``"name Type ..."``
    string (kept verbatim, so modifiers like ``DEFAULT 1`` can be passed) or a
    ``helpers.tables.Column``."""
    out = []
    for column in columns or []:
        if isinstance(column, str):
            out.append(column)
        else:
            out.append(column.full_definition())
    return out


def build_create_table_query(
    database_name,
    namespace,
    table_name,
    path=ENGINE_LESS,
    columns=None,
    source=None,
    if_not_exists=False,
    partition_by=None,
    order_by=None,
    storage_clauses=None,
    engine_settings=None,
    table_elements=None,
    comment=None,
    as_select=None,
    engine=None,
    minio_root_user=None,
    minio_root_password=None,
):
    """Build the ``CREATE TABLE`` text for one of the three creation paths.

    ``storage_clauses`` is raw text appended after ``ORDER BY`` (e.g.
    ``"PRIMARY KEY id"`` or ``"TTL d + INTERVAL 1 DAY"``) for the rejection
    scenarios. ``table_elements`` are raw entries added to the column list
    (``"INDEX i x TYPE minmax"``, ``"CONSTRAINT c CHECK x > 0"``,
    ``"PROJECTION p (SELECT x)"``, ``"PRIMARY KEY x"``).
    """
    name = clickhouse_table_name(database_name, namespace, table_name)
    query = "CREATE TABLE "
    if if_not_exists:
        query += "IF NOT EXISTS "
    query += name

    elements = column_defs(columns) + list(table_elements or [])
    if elements:
        query += " (" + ", ".join(elements) + ")"

    if path == AS_SOURCE:
        assert source, "as_source path needs a source table"
        query += f" AS {source}"

    if path == EXPLICIT_ENGINE:
        if engine is None:
            engine = iceberg_s3_engine(namespace, table_name, minio_root_user, minio_root_password)
        query += f" ENGINE = {engine}"

    if partition_by:
        query += f" PARTITION BY {partition_by}"
    if order_by:
        query += f" ORDER BY {order_by}"
    if storage_clauses:
        query += f" {storage_clauses}"
    if engine_settings:
        query += " SETTINGS " + ", ".join(
            f"{key} = {value}" for key, value in engine_settings.items()
        )
    if comment:
        query += f" COMMENT '{comment}'"
    if as_select:
        query += f" AS {as_select}"
    return query


@TestStep(Given)
def create_table(
    self,
    database_name,
    namespace,
    table_name,
    path=ENGINE_LESS,
    columns=None,
    source=None,
    if_not_exists=False,
    partition_by=None,
    order_by=None,
    storage_clauses=None,
    engine_settings=None,
    table_elements=None,
    comment=None,
    as_select=None,
    engine=None,
    settings=None,
    node=None,
    exitcode=None,
    message=None,
    purge_on_exit=True,
):
    """Run ``CREATE TABLE`` in a DataLakeCatalog database through one of the
    three creation paths (``ENGINE_LESS``, ``EXPLICIT_ENGINE``, ``AS_SOURCE``).

    Query-level settings go through ``settings`` (client flags), never into
    the statement text, because a trailing ``SETTINGS`` clause is parsed as
    engine settings and rejected on the engine-less path.

    On exit the table is dropped with purge so the location is clean for the
    next scenario; pass ``purge_on_exit=False`` for scenarios that inspect
    leftovers themselves.

    Returns the query result.
    """
    if node is None:
        node = self.context.node

    query = build_create_table_query(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        path=path,
        columns=columns,
        source=source,
        if_not_exists=if_not_exists,
        partition_by=partition_by,
        order_by=order_by,
        storage_clauses=storage_clauses,
        engine_settings=engine_settings,
        table_elements=table_elements,
        comment=comment,
        as_select=as_select,
        engine=engine,
        minio_root_user=self.context.minio_root_user,
        minio_root_password=self.context.minio_root_password,
    )

    query_settings = list(settings or [])
    if path == EXPLICIT_ENGINE:
        query_settings.append(("write_full_path_in_iceberg_metadata", 1))
    if as_select:
        query_settings.append(("allow_insert_into_iceberg", 1))

    try:
        # An expected error still contains "Exception:", which node.query treats as
        # a failure unless told the exception is expected.
        yield node.query(
            query,
            settings=query_settings or None,
            exitcode=exitcode,
            message=message,
            ignore_exception=exitcode is not None or message is not None,
        )
    finally:
        if purge_on_exit:
            with Finally(f"drop {namespace}.{table_name} with purge"):
                node.query(
                    f"DROP TABLE IF EXISTS "
                    f"{clickhouse_table_name(database_name, namespace, table_name)}",
                    settings=[(PURGE_SETTING, 1)],
                    no_checks=True,
                )


@TestStep(When)
def drop_table(
    self,
    database_name,
    namespace,
    table_name,
    purge=None,
    if_exists=False,
    sync=False,
    alias=False,
    inline=False,
    name=None,
    node=None,
    exitcode=None,
    message=None,
):
    """``DROP TABLE`` with the purge setting passed the way the scenario asks:

    * ``purge=None`` sends no setting (server default applies);
    * ``purge=0/1`` sets ``data_lake_delete_data_on_drop`` (or its alias
      ``iceberg_delete_data_on_drop`` with ``alias=True``);
    * ``inline=True`` passes it as a ``SET`` before the query instead of a
      client flag, to cover the session-level route.

    ``name`` overrides the table identifier for tables outside a catalog.
    """
    if node is None:
        node = self.context.node
    if name is None:
        name = clickhouse_table_name(database_name, namespace, table_name)

    query = "DROP TABLE "
    if if_exists:
        query += "IF EXISTS "
    query += name
    if sync:
        query += " SYNC"

    setting = (
        [] if purge is None else [(PURGE_SETTING_ALIAS if alias else PURGE_SETTING, int(purge))]
    )
    kwargs = {"inline_settings": setting} if inline else {"settings": setting}
    return node.query(
        query,
        exitcode=exitcode,
        message=message,
        ignore_exception=exitcode is not None or message is not None,
        **kwargs,
    )


@TestStep(Given)
def mergetree_source_table(
    self,
    columns,
    partition_by=None,
    order_by="tuple()",
    settings=None,
    comment=None,
    rows=None,
    name=None,
    query_settings=None,
    node=None,
):
    """A MergeTree table in ``default`` to serve as the ``AS`` source.
    ``rows`` is an optional ``VALUES`` body to insert."""
    if node is None:
        node = self.context.node
    if name is None:
        name = f"default.src_{getuid()}"
    query = f"CREATE TABLE {name} (" + ", ".join(column_defs(columns)) + ") ENGINE = MergeTree"
    if partition_by:
        query += f" PARTITION BY {partition_by}"
    query += f" ORDER BY {order_by}"
    if settings:
        query += " SETTINGS " + ", ".join(f"{k} = {v}" for k, v in settings.items())
    if comment:
        query += f" COMMENT '{comment}'"
    try:
        node.query(query, settings=query_settings)
        if rows:
            node.query(f"INSERT INTO {name} VALUES {rows}")
        yield name
    finally:
        with Finally(f"drop source {name}"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


def feature_available(node):
    """The PR's marker: the unified drop setting exists only on builds that
    carry native CREATE/DROP for DataLakeCatalog."""
    # ``steps=False``: this runs at feature level, where a ``--only`` filter would
    # skip the implicit step ``node.query`` opens and the probe would never run.
    result = node.query(
        f"SELECT count() FROM system.settings WHERE name = '{PURGE_SETTING}'",
        steps=False,
        no_checks=True,
    )
    return result.exitcode == 0 and result.output.strip() == "1"


# ---------------------------------------------------------------------------
# Shared fixtures and error codes
# ---------------------------------------------------------------------------

# clickhouse-client exits with the error code modulo 256.
BAD_ARGUMENTS = 36
INCORRECT_QUERY = 80
FILE_DOESNT_EXIST = 107
NOT_IMPLEMENTED = 48
TABLE_ALREADY_EXISTS = 57
UNKNOWN_TABLE = 60
SUPPORT_IS_DISABLED = 344 % 256
ACCESS_DENIED = 497 % 256
CATALOG_NAMESPACE_DISABLED = 766 % 256


AUTO = "auto"


def database_base_location(value, test=None):
    """Resolve the ``default_base_location`` a fixture database gets.

    First run against PR 2305 (2026-09-15): ice-rest-catalog advertises no
    ``default-base-location``, and for a REST catalog without one the server
    refuses to guess a storage scheme from ``storage_endpoint``
    (``getLocationSchemeForTableCreation`` throws for ``ICEBERG_REST``). So the
    engine-less path on REST needs the setting on the database, and ``AUTO``
    resolves to ``DEFAULT_BASE_LOCATION`` there. Glue derives the location from
    ``storage_endpoint``, so ``AUTO`` resolves to nothing. Pass ``None`` to omit
    the setting deliberately.
    """
    if value is not AUTO:
        return value
    test = test or current()
    return DEFAULT_BASE_LOCATION if test.context.catalog in ("rest", "ice") else None


@TestStep(Given)
def catalog_and_database(
    self,
    minio_root_user,
    minio_root_password,
    node=None,
    default_base_location=AUTO,
    **kwargs,
):
    """A PyIceberg catalog handle plus a DataLakeCatalog database over the
    same catalog, without pre-creating any namespace, so the feature's
    namespace auto-creation is exercised. ``kwargs`` go to the database
    (``storage_uri_style``, ``storage_endpoint``, ``namespaces``).

    ``default_base_location`` defaults to ``DEFAULT_BASE_LOCATION`` on a REST
    catalog (see :func:`database_base_location`); pass ``None`` to omit it.
    Returns ``(catalog, database_name)``."""
    with By("open PyIceberg catalog"):
        catalog = catalog_steps.create_catalog(
            s3_endpoint="http://localhost:9002",
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )
    with By("create DataLakeCatalog database"):
        database_name = f"datalake_db_{getuid()}"
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
            node=node,
            default_base_location=database_base_location(default_base_location),
            **kwargs,
        )
    return catalog, database_name


@TestStep(Given)
def datalake_database(
    self,
    minio_root_user,
    minio_root_password,
    node=None,
    default_base_location=AUTO,
    **kwargs,
):
    """A second DataLakeCatalog database over the same catalog, e.g. on
    another node. Returns the database name."""
    database_name = f"datalake_db_{getuid()}"
    iceberg_engine.create_experimental_iceberg_database(
        database_name=database_name,
        s3_access_key_id=minio_root_user,
        s3_secret_access_key=minio_root_password,
        node=node,
        default_base_location=database_base_location(default_base_location),
        **kwargs,
    )
    return database_name


@TestStep(Given)
def pyiceberg_table(self, catalog, namespace, table_name, location=None, rows=None):
    """A table registered by PyIceberg (an external writer) at the same
    location ClickHouse would choose, with ``id long, name string``.
    ``rows`` is an optional list of ``{"id": .., "name": ..}`` dicts to
    append. The finaliser drops it with purge and clears the prefix."""
    from pyiceberg.schema import Schema, NestedField
    from pyiceberg.types import LongType, StringType
    import pyarrow as pa

    if location is None:
        location = expected_table_location(namespace, table_name)
    catalog_steps.create_namespace(catalog=catalog, namespace=namespace)
    schema = Schema(
        NestedField(field_id=1, name="id", field_type=LongType(), required=False),
        NestedField(field_id=2, name="name", field_type=StringType(), required=False),
    )
    try:
        table = catalog.create_table(
            identifier=table_identifier(namespace, table_name),
            schema=schema,
            location=location,
        )
        if rows:
            table.append(pa.Table.from_pylist(rows, schema=table.schema().as_arrow()))
        yield table
    finally:
        with Finally(f"drop PyIceberg table {namespace}.{table_name}"):
            try:
                catalog.drop_table(table_identifier(namespace, table_name))
            except pyiceberg.exceptions.NoSuchTableError:
                pass
            s3.delete_prefix(s3.prefix_from_uri(location))


def pyiceberg_schema_shape(table):
    """``[(name, type_string, required)]`` of a PyIceberg table schema."""
    return [(f.name, str(f.field_type), f.required) for f in table.schema().fields]


def pyiceberg_spec_shape(table):
    """``[(source_id, transform)]`` of the current partition spec."""
    return [(f.source_id, str(f.transform)) for f in table.spec().fields]


def pyiceberg_sort_shape(table):
    """``[(source_id, transform)]`` of the current sort order."""
    return [(f.source_id, str(f.transform)) for f in table.sort_order().fields]


@TestStep(Then)
def assert_rejected_no_trace(self, before, after, namespace_expected=None):
    """B2 for a rejection: nothing changed, the table is absent, and (unless
    the namespace existed before) no namespace was created."""
    assert_state_unchanged(before=before, after=after)
    assert not after.catalog_table, error("table registered after a rejected CREATE")
    if namespace_expected is None:
        namespace_expected = before.catalog_namespace
    assert after.catalog_namespace == namespace_expected, error(
        f"namespace present={after.catalog_namespace}, expected {namespace_expected}"
    )
