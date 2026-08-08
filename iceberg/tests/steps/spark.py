"""Steps for driving the external Spark writer (``iceberg_spark`` container).

Spark is the reference Iceberg writer for scenarios that ClickHouse cannot
produce itself — most importantly Iceberg format version 3 tables with
merge-on-read write modes, whose ``DELETE`` / ``UPDATE`` / ``MERGE`` commits
store row-level deletes as deletion vectors (``deletion-vector-v1`` blobs in
``Puffin`` files).

The ``iceberg_spark`` container (``tabulario/spark-iceberg`` in
``iceberg_env/docker-compose.yml``) ships a Spark catalog named ``demo``
pre-wired to the ``rest`` Iceberg REST catalog (``http://rest:8181``) and the
MinIO warehouse (``s3://warehouse/``), so a table
``demo.<namespace>.<table>`` lands under
``s3://warehouse/<namespace>/<table>/`` where ClickHouse can read it via
``icebergS3('http://minio:9000/warehouse/<namespace>/<table>', ...)``.

Every ``spark-sql`` invocation pays a JVM startup cost (~20-40s), so steps
accept lists of statements and callers should batch a whole fixture
(CREATE + INSERT + DELETE) into one invocation whenever possible.
"""

import subprocess

from testflows.core import *
from helpers.common import getuid

SPARK_CONTAINER = "iceberg_spark"
SPARK_CATALOG = "demo"
SPARK_SQL_TIMEOUT = 600

MOR_V3_TBLPROPERTIES = {
    "format-version": "3",
    "write.delete.mode": "merge-on-read",
    "write.update.mode": "merge-on-read",
    "write.merge.mode": "merge-on-read",
}


def spark_catalog(test=None):
    """Spark catalog name, overridable via ``self.context.spark_catalog``."""
    test = test or current()
    return getattr(test.context, "spark_catalog", SPARK_CATALOG)


def qualified_table_name(namespace, table_name, catalog=None):
    """Fully qualified Spark table name ``<catalog>.<namespace>.<table>``."""
    if catalog is None:
        catalog = spark_catalog()
    return f"{catalog}.{namespace}.{table_name}"


def tblproperties_clause(properties):
    """Render a ``TBLPROPERTIES`` clause from a dict; empty dict → empty string."""
    if not properties:
        return ""
    pairs = ", ".join(f"'{key}'='{value}'" for key, value in properties.items())
    return f"TBLPROPERTIES ({pairs})"


def run_spark_sql(statements, timeout=SPARK_SQL_TIMEOUT, container=SPARK_CONTAINER):
    """Execute one or more SQL statements in the Spark container with
    ``spark-sql -S -e`` and return stdout.

    Args:
        statements: a single SQL string or a list of statements that are
            joined with ``;`` and executed in one JVM invocation.
    """
    if not isinstance(statements, str):
        statements = ";\n".join(statements)

    cmd = ["docker", "exec", container, "spark-sql", "-S", "-e", statements]

    with By("executing spark-sql", description=statements):
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            fail(
                f"spark-sql failed (exit code {result.returncode}):\n"
                f"statements:\n{statements}\n"
                f"stderr (tail):\n{result.stderr[-4000:]}"
            )
        return result.stdout


def spark_query_rows(statement, timeout=SPARK_SQL_TIMEOUT):
    """Run a SELECT in Spark and return rows as a list of lists of strings
    (spark-sql prints rows tab-separated, NULL for nulls)."""
    output = run_spark_sql(statement, timeout=timeout)
    return [line.split("\t") for line in output.splitlines() if line.strip()]


@TestStep(Given)
def wait_for_spark(self, timeout=300, delay=10):
    """Wait until the Spark container answers queries (the container boots
    with the cluster but is not part of ``all_services_ready``)."""
    for retry in retries(timeout=timeout, delay=delay):
        with retry:
            cmd = [
                "docker",
                "exec",
                SPARK_CONTAINER,
                "spark-sql",
                "-S",
                "-e",
                "SELECT 1",
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=SPARK_SQL_TIMEOUT
            )
            assert result.returncode == 0, (
                f"spark not ready: {result.stderr[-1000:]}"
            )


@TestStep(Given)
def create_namespace(self, namespace):
    """Create a namespace in the Spark catalog if it does not exist."""
    run_spark_sql(f"CREATE NAMESPACE IF NOT EXISTS {spark_catalog()}.{namespace}")
    return namespace


@TestStep(Given)
def create_table(
    self,
    namespace=None,
    table_name=None,
    columns="id BIGINT, data STRING",
    partitioned_by=None,
    properties=None,
    setup_statements=None,
    cleanup=False,
):
    """Create an Iceberg table via Spark, optionally running extra
    ``setup_statements`` (INSERT/DELETE/...) in the same JVM invocation.

    Args:
        columns: column definition list of the CREATE TABLE.
        partitioned_by: optional ``PARTITIONED BY`` expression, e.g.
            ``"bucket(4, id)"`` or ``"category"``.
        properties: TBLPROPERTIES dict; defaults to v3 merge-on-read
            (``MOR_V3_TBLPROPERTIES``) which makes external deletes produce
            deletion vectors.
        setup_statements: statements executed right after CREATE, batched in
            the same spark-sql invocation. ``{table}`` placeholders inside
            them are replaced with the fully qualified table name.
        cleanup: drop the table (PURGE) in the Finally block. Off by default:
            table names are unique and dropping costs a JVM invocation.
    """
    if namespace is None:
        namespace = f"dv_{getuid()}"
    if table_name is None:
        table_name = f"table_{getuid()}"
    if properties is None:
        properties = MOR_V3_TBLPROPERTIES

    full_name = qualified_table_name(namespace, table_name)

    statements = [
        f"CREATE NAMESPACE IF NOT EXISTS {spark_catalog()}.{namespace}",
        f"CREATE TABLE {full_name} ({columns}) USING iceberg "
        + (f"PARTITIONED BY ({partitioned_by}) " if partitioned_by else "")
        + tblproperties_clause(properties),
    ]
    for statement in setup_statements or []:
        statements.append(statement.format(table=full_name))

    # suite-level teardown: a feature that initializes
    # ``context.spark_created_tables`` gets every table registered so it
    # can batch-drop them once at the end instead of paying one spark-sql
    # JVM start per table. Registered before the batch runs: CREATE may
    # succeed and a later setup statement fail, and cleanup tolerates
    # tables that were never created.
    registry = getattr(self.context, "spark_created_tables", None)
    if registry is not None:
        registry.append((namespace, table_name))

    try:
        run_spark_sql(statements)
        yield namespace, table_name

    finally:
        if cleanup:
            with Finally("drop the Spark table"):
                run_spark_sql(f"DROP TABLE IF EXISTS {full_name} PURGE")


@TestStep(When)
def execute(self, namespace, table_name, statements):
    """Execute statements against a Spark table in one invocation;
    ``{table}`` placeholders are replaced with the qualified table name."""
    full_name = qualified_table_name(namespace, table_name)
    return run_spark_sql(
        [statement.format(table=full_name) for statement in statements]
    )


@TestStep(When)
def insert_rows(self, namespace, table_name, values):
    """INSERT literal rows, e.g. ``values="(1, 'a'), (2, 'b')"``."""
    return execute(
        namespace=namespace,
        table_name=table_name,
        statements=[f"INSERT INTO {{table}} VALUES {values}"],
    )


@TestStep(When)
def delete_rows(self, namespace, table_name, condition):
    """DELETE rows; on a v3 merge-on-read table this commits a deletion
    vector instead of rewriting data files."""
    return execute(
        namespace=namespace,
        table_name=table_name,
        statements=[f"DELETE FROM {{table}} WHERE {condition}"],
    )


@TestStep(When)
def update_rows(self, namespace, table_name, set_clause, condition):
    """UPDATE rows (merge-on-read: deletion vector + new data file)."""
    return execute(
        namespace=namespace,
        table_name=table_name,
        statements=[f"UPDATE {{table}} SET {set_clause} WHERE {condition}"],
    )


@TestStep(When)
def merge_into(self, namespace, table_name, source_query, on, matched_clauses):
    """MERGE INTO the table from an inline source.

    Args:
        source_query: e.g. ``"SELECT * FROM VALUES (1, 'x') AS s(id, data)"``.
        on: join condition using aliases ``t`` (target) and ``s`` (source).
        matched_clauses: full WHEN ... THEN ... clauses string.
    """
    return execute(
        namespace=namespace,
        table_name=table_name,
        statements=[
            f"MERGE INTO {{table}} t USING ({source_query}) s ON {on} "
            f"{matched_clauses}"
        ],
    )


@TestStep(When)
def alter_table(self, namespace, table_name, alter_clauses):
    """Run ALTER TABLE statements (schema evolution, SET TBLPROPERTIES).

    Args:
        alter_clauses: list like ``["ADD COLUMN extra INT"]``.
    """
    return execute(
        namespace=namespace,
        table_name=table_name,
        statements=[f"ALTER TABLE {{table}} {clause}" for clause in alter_clauses],
    )


@TestStep(When)
def set_table_properties(self, namespace, table_name, properties):
    """ALTER TABLE ... SET TBLPROPERTIES from a dict."""
    pairs = ", ".join(f"'{key}'='{value}'" for key, value in properties.items())
    return alter_table(
        namespace=namespace,
        table_name=table_name,
        alter_clauses=[f"SET TBLPROPERTIES ({pairs})"],
    )


@TestStep(When)
def rewrite_data_files(self, namespace, table_name, options=None):
    """Compact the table with the ``rewrite_data_files`` procedure
    (rewrites data files and drops superseded deletion vectors)."""
    catalog = spark_catalog()
    args = f"table => '{namespace}.{table_name}'"
    if options:
        args += f", options => map({options})"
    return run_spark_sql(f"CALL {catalog}.system.rewrite_data_files({args})")


@TestStep(When)
def expire_snapshots(self, namespace, table_name, older_than=None):
    """Expire old snapshots via the ``expire_snapshots`` procedure."""
    catalog = spark_catalog()
    args = f"table => '{namespace}.{table_name}'"
    if older_than:
        args += f", older_than => TIMESTAMP '{older_than}'"
    return run_spark_sql(f"CALL {catalog}.system.expire_snapshots({args})")


@TestStep(Then)
def select_rows(self, namespace, table_name, columns="*", where=None, order_by=None):
    """SELECT from the table in Spark; returns rows as lists of strings.
    Used to compare ClickHouse results with the writer engine's own view."""
    full_name = qualified_table_name(namespace, table_name)
    query = f"SELECT {columns} FROM {full_name}"
    if where:
        query += f" WHERE {where}"
    if order_by:
        query += f" ORDER BY {order_by}"
    return spark_query_rows(query)
