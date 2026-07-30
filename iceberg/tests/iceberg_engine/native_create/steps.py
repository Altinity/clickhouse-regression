from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import Column, create_table

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine


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
):
    """Create an Iceberg table natively via ClickHouse ``CREATE TABLE`` inside
    a DataLakeCatalog database.

    Delegates to ``helpers.tables.create_table`` so the table is automatically
    dropped (``DROP TABLE IF EXISTS``) when the test finishes.

    Returns the ``Table`` object yielded by ``create_table``.
    """
    return create_table(
        name=clickhouse_table_name(database_name, namespace, table_name),
        engine=iceberg_s3_engine(
            namespace, table_name, minio_root_user, minio_root_password
        ),
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
