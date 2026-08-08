"""Feature-scope sanity: ClickHouse reads Iceberg v3 deletion vectors and
never writes them, regardless of which writer operation produced them."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.steps.spark as spark
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.s3_objects as s3_objects


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_Read("1.0"))
def read_deletion_vectors(self):
    """Rows deleted through a deletion vector are excluded exactly."""
    rows = 100
    deleted = [i for i in range(rows) if i % 10 == 0]

    with Given("a v3 merge-on-read table where Spark deleted every 10th row"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )

    with Then("the visible row set matches the writer-committed state"):
        common.assert_visible_ids(table=table, ids=common.expected_ids(rows, deleted))

    with And("count() agrees"):
        assert common.count_rows(table=table) == rows - len(deleted), error()


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ReadOnly("1.0"))
def read_only(self):
    """No ClickHouse read operation modifies Puffin files or any other
    table object."""
    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors()

    with And("the full object inventory of the table is recorded"):
        inventory_before = s3_objects.object_inventory(table.prefix)

    with When("ClickHouse reads the table in several ways"):
        common.read_result(table=table, order_by="id")
        common.count_rows(table=table)
        common.read_result(table=table, where_clause="id > 50", columns="id")
        common.read_result(table=table, cluster=True, order_by="id")
        engine_table = common.engine_table(table=table)
        self.context.node.query(f"SELECT count() FROM {engine_table}")

    with And("caches are dropped and the table is read again"):
        common.drop_puffin_cache()
        common.read_result(table=table, order_by="id")

    with Then("no object under the table location changed"):
        inventory_after = s3_objects.object_inventory(table.prefix)
        assert inventory_after == inventory_before, error(
            "table objects changed during read-only operations: "
            f"added={set(inventory_after) - set(inventory_before)}, "
            f"removed={set(inventory_before) - set(inventory_after)}"
        )


WRITER_OPERATIONS = {
    "delete": ["DELETE FROM {table} WHERE id % 7 = 0"],
    "update": ["UPDATE {table} SET data = 'updated' WHERE id BETWEEN 20 AND 40"],
    "merge": [
        "MERGE INTO {table} t "
        "USING (SELECT id * 3 AS id, concat('m-', CAST(id AS STRING)) AS data "
        "FROM range(40)) s "
        "ON t.id = s.id "
        "WHEN MATCHED AND s.id % 2 = 0 THEN UPDATE SET t.data = s.data "
        "WHEN MATCHED AND s.id % 2 = 1 THEN DELETE "
        "WHEN NOT MATCHED THEN INSERT (id, data) VALUES (s.id, s.data)"
    ],
    "combined operations": [
        "DELETE FROM {table} WHERE id % 11 = 0",
        "UPDATE {table} SET data = 'u' WHERE id % 5 = 0 AND id % 11 != 0",
        "MERGE INTO {table} t "
        "USING (SELECT id + 90 AS id, 'merged' AS data FROM range(20)) s "
        "ON t.id = s.id "
        "WHEN MATCHED THEN DELETE "
        "WHEN NOT MATCHED THEN INSERT (id, data) VALUES (s.id, s.data)",
    ],
}


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_WriterOperations("1.0"))
def writer_operations(self):
    """ClickHouse returns exactly the writer engine's own result whether the
    deletion vector came from DELETE, UPDATE, MERGE, or a combination."""
    for operation, statements in WRITER_OPERATIONS.items():
        with Check(operation):
            with Given("a v3 merge-on-read table with 100 rows and no deletes yet"):
                table = common.table_with_deletion_vectors(
                    rows=100, delete_condition=None, verify_puffin=False
                )

            with When(f"Spark commits the {operation}"):
                spark.execute(
                    namespace=table.namespace,
                    table_name=table.table_name,
                    statements=statements,
                )

            with And("the operation produced at least one deletion vector"):
                s3_objects.assert_puffin_exists(
                    namespace=table.namespace, table_name=table.table_name
                )

            with Then("ClickHouse rows equal the writer engine's own rows"):
                spark_rows = spark.select_rows(
                    namespace=table.namespace,
                    table_name=table.table_name,
                    columns="id, data",
                    order_by="id",
                )
                result = common.read_result(
                    table=table, columns="id, data", order_by="id"
                )
                clickhouse_rows = [
                    line.split("\t")
                    for line in result.output.splitlines()
                    if line.strip()
                ]
                assert clickhouse_rows == spark_rows, error(
                    f"ClickHouse returned {len(clickhouse_rows)} rows, "
                    f"Spark returned {len(spark_rows)}"
                )


@TestFeature
@Name("sanity")
def feature(self, minio_root_user, minio_root_password):
    """Basic deletion-vector read support."""
    Scenario(test=read_deletion_vectors, flags=TE)()
    Scenario(test=read_only, flags=TE)()
    Scenario(test=writer_operations, flags=TE)()
