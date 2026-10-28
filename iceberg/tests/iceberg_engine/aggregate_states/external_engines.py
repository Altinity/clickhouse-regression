"""Other engines read the states ClickHouse wrote, and Spark commits to the
table: PyIceberg through the suite's catalog, Spark through its own `demo`
catalog (the Apache REST fixture), into which the table is registered."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

import iceberg.tests.steps.spark as spark

from iceberg.requirements.aggregate_states import *
from iceberg.tests.iceberg_engine.aggregate_states.steps import *
from iceberg.tests.iceberg_engine.aggregate_states.annotation_survival import (
    EXPECTED_ANNOTATIONS,
    registered_clickhouse_table,
)
from iceberg.tests.iceberg_engine.native_create.steps import catalog_and_database


def clickhouse_rows(table_name, node=None):
    """``{k: (hex(u), s)}`` as ClickHouse reads its own table."""
    node = node or current().context.node
    output = node.query(
        f"SELECT k, hex(u), s FROM {table_name} ORDER BY k FORMAT TabSeparated",
        settings=STATE_SETTINGS,
    ).output
    rows = {}
    for line in output.splitlines():
        k, u, s = line.split("\t")
        rows[int(k)] = (u, int(s))
    return rows


@TestStep(Given)
def spark_registered_table(self, table_name):
    """Register a ClickHouse-written table in Spark's catalog at its latest
    metadata file. Returns ``(namespace, table_name)``."""
    namespace = f"agg_{getuid()}"
    key = latest_metadata_key(table_prefix(table_name))
    spark.run_spark_sql(
        [
            f"CREATE NAMESPACE IF NOT EXISTS {spark.spark_catalog()}.{namespace}",
            f"CALL {spark.spark_catalog()}.system.register_table("
            f"table => '{namespace}.{table_name}', "
            f"metadata_file => 's3://{s3.WAREHOUSE_BUCKET}/{key}')",
        ]
    )
    return namespace, table_name


@TestStep(When)
def spark_append_states(self, namespace, table_name, rows):
    """INSERT ``rows`` from Spark; the states are binary literals."""
    values = ", ".join(
        f"({row['k']}, X'{row['u'].hex().upper()}', {row['s']})" for row in rows
    )
    spark.insert_rows(namespace=namespace, table_name=table_name, values=values)


def spark_current_metadata_key(namespace, table_name):
    """Key of the metadata file Spark's catalog currently points at."""
    rows = spark.spark_query_rows(
        f"SELECT file FROM {spark.qualified_table_name(namespace, table_name)}"
        ".metadata_log_entries ORDER BY timestamp DESC LIMIT 1"
    )
    assert rows, error("Spark reports no metadata log entries")
    return s3.key_from_uri(rows[0][0])


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Interop_ExternalReaders("1.0"))
def pyiceberg_reads_states(self):
    """PyIceberg sees u as binary with the bytes ClickHouse reports, and s as
    a long with the same values."""
    with Given("catalog"):
        catalog, _ = catalog_and_database(
            minio_root_user=self.context.minio_root_user,
            minio_root_password=self.context.minio_root_password,
        )

    with And("a ClickHouse-written table with states, registered in the catalog"):
        _, table_name, table = registered_clickhouse_table(catalog=catalog)

    with Then("PyIceberg reports binary and long"):
        types = {f.name: str(f.field_type) for f in table.schema().fields}
        assert types == {"k": "int", "u": "binary", "s": "long"}, error(types)

    with And("PyIceberg reads the same bytes and values"):
        scanned = {
            row["k"]: (row["u"].hex().upper(), row["s"])
            for row in table.scan().to_arrow().to_pylist()
        }
        assert scanned == clickhouse_rows(table_name), error(scanned)


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Interop_ExternalReaders("1.0"))
def spark_reads_states(self):
    """Spark sees u as binary with the bytes ClickHouse reports, and s as a
    bigint with the same values."""
    with Given("a ClickHouse-written table with states"):
        table_name = iceberg_s3_table()
        insert_states(table_name=table_name)

    with And("registered in Spark's catalog"):
        namespace, _ = spark_registered_table(table_name=table_name)

    with Then("Spark reads the same bytes and values"):
        rows = spark.spark_query_rows(
            f"SELECT k, hex(u), s FROM {spark.qualified_table_name(namespace, table_name)} "
            "ORDER BY k"
        )
        scanned = {int(k): (u, int(s)) for k, u, s in rows}
        assert scanned == clickhouse_rows(table_name), error(scanned)


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Interop_ExternalCommit("1.0"))
def annotations_survive_spark_commit(self):
    """Spark appends to the table: the metadata file Spark's catalog now
    points at still carries the annotations."""
    with Given("a ClickHouse-written table with states, registered in Spark"):
        table_name = iceberg_s3_table()
        insert_states(table_name=table_name)
        namespace, _ = spark_registered_table(table_name=table_name)

    with When("Spark appends states"):
        spark_append_states(
            namespace=namespace,
            table_name=table_name,
            rows=external_rows(start=200, count=100),
        )

    with Then("the current metadata keeps the annotations"):
        key = spark_current_metadata_key(namespace, table_name)
        assert_annotations(
            metadata=s3.read_json_object(key), expected=EXPECTED_ANNOTATIONS, where=key
        )


@TestScenario
@Requirements(RQ_Iceberg_AggregateStates_Interop_ExternalCommit("1.0"))
def clickhouse_merges_after_spark_commit(self):
    """ClickHouse reads the metadata Spark committed: it reports the aggregate
    types and merges the states both engines wrote."""
    node = self.context.node

    with Given("a ClickHouse-written table with states, registered in Spark"):
        table_name = iceberg_s3_table()
        insert_states(table_name=table_name)
        namespace, _ = spark_registered_table(table_name=table_name)

    with When("Spark appends states for the next rows"):
        spark_append_states(
            namespace=namespace,
            table_name=table_name,
            rows=external_rows(start=200, count=100),
        )
        key = spark_current_metadata_key(namespace, table_name)
        function = icebergs3_function(
            table_name,
            storage_settings={
                "iceberg_metadata_file_path": key[len(table_prefix(table_name)) :]
            },
        )

    with Then("DESCRIBE at Spark's metadata reports the aggregate types"):
        columns = describe(function, settings=STATE_SETTINGS)
        assert columns == [("k", "Int32"), ("u", U_TYPE), ("s", S_TYPE)], error(columns)

    with And("both batches merge to the result over all rows"):
        actual = node.query(merge_select(function), settings=STATE_SETTINGS).output
        expected = expected_result(start=0, count=300)
        assert actual == expected, error(f"merged:\n{actual}\nexpected:\n{expected}")


@TestFeature
@Name("external engines")
def feature(self):
    """PyIceberg and Spark read and commit to ClickHouse-written states."""
    Scenario(run=pyiceberg_reads_states, flags=TE)

    if self.context.catalog != "rest":
        note("Spark runs against its own REST catalog; covered under the rest catalog")
        return

    with Given("Spark is up"):
        spark.wait_for_spark()

    for scenario in (
        spark_reads_states,
        annotations_survive_spark_commit,
        clickhouse_merges_after_spark_commit,
    ):
        Scenario(run=scenario, flags=TE)
