"""Query semantics: deletion vectors are applied at the source, before any
SQL operator, independently of projection, combined with other filters, and
across schema evolution."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

from helpers.common import getuid

import iceberg.tests.steps.spark as spark
import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.delete_files as delete_files


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_OperatorIndependence("1.0"))
def operator_independence(self):
    """Every relational operator observes exactly the post-vector row set;
    a MergeTree table holding the surviving rows is the oracle."""
    node = self.context.node
    rows = 100
    # value '0' loses all its occurrences, value '10' only one of them
    deleted = [i for i in range(rows) if i % 20 == 0] + [30]

    with Given(
        "a table with duplicate data values where the vector removes all "
        "occurrences of one value and only some of another"
    ):
        table = common.table_with_deletion_vectors(
            setup_statements=[
                common.insert_range_statement(
                    rows, data_expr="CAST(id % 20 AS STRING)"
                ),
                "DELETE FROM {table} WHERE id % 20 = 0 OR id = 30",
            ],
        )

    with And("a MergeTree oracle with exactly the surviving rows"):
        oracle = common.merge_tree_oracle(
            rows=rows, deleted_ids=deleted, data_expr="toString(number % 20)"
        )

    with And("a small dimension table for the join check"):
        join_table = f"dv_join_{getuid()}"
        node.query(
            f"CREATE TABLE {join_table} (id Int64, tag String) "
            f"ENGINE = MergeTree ORDER BY id"
        )
        node.query(
            f"INSERT INTO {join_table} SELECT number, concat('t', toString(number)) "
            f"FROM numbers({rows})"
        )

    iceberg_expr = table.sql_expr()

    query_pairs = {
        "order by with limit": (
            f"SELECT id FROM {iceberg_expr} ORDER BY id LIMIT 30",
            f"SELECT id FROM {oracle} ORDER BY id LIMIT 30",
        ),
        "distinct": (
            f"SELECT DISTINCT data FROM {iceberg_expr} ORDER BY data",
            f"SELECT DISTINCT data FROM {oracle} ORDER BY data",
        ),
        "join against a non-Iceberg table": (
            f"SELECT t.id, j.tag FROM {iceberg_expr} AS t "
            f"INNER JOIN {join_table} AS j ON t.id = j.id ORDER BY t.id",
            f"SELECT t.id, j.tag FROM {oracle} AS t "
            f"INNER JOIN {join_table} AS j ON t.id = j.id ORDER BY t.id",
        ),
        "subquery": (
            f"SELECT count(), sum(id) FROM (SELECT * FROM {iceberg_expr})",
            f"SELECT count(), sum(id) FROM (SELECT * FROM {oracle})",
        ),
        "cte": (
            f"WITH source AS (SELECT * FROM {iceberg_expr}) "
            f"SELECT id FROM source ORDER BY id",
            f"WITH source AS (SELECT * FROM {oracle}) "
            f"SELECT id FROM source ORDER BY id",
        ),
        "derived table with aggregation": (
            f"SELECT data, cnt FROM (SELECT data, count() AS cnt "
            f"FROM {iceberg_expr} GROUP BY data) ORDER BY data",
            f"SELECT data, cnt FROM (SELECT data, count() AS cnt "
            f"FROM {oracle} GROUP BY data) ORDER BY data",
        ),
    }

    try:
        for name, (iceberg_query, oracle_query) in query_pairs.items():
            with Check(name):
                iceberg_result = node.query(f"{iceberg_query} FORMAT TabSeparated")
                oracle_result = node.query(f"{oracle_query} FORMAT TabSeparated")
                assert iceberg_result.output == oracle_result.output, error(
                    f"operator '{name}' observed a different row set"
                )

        with Check("prewhere maps back to correct absolute positions"):
            engine_table = common.engine_table(table=table)
            prewhere_result = node.query(
                f"SELECT id FROM {engine_table} PREWHERE data = '10' "
                f"ORDER BY id FORMAT TabSeparated"
            )
            where_result = node.query(
                f"SELECT id FROM {oracle} WHERE data = '10' "
                f"ORDER BY id FORMAT TabSeparated"
            )
            assert prewhere_result.output == where_result.output, error(
                "PREWHERE returned a different row set than the oracle"
            )
    finally:
        with Finally("drop the join table"):
            node.query(f"DROP TABLE IF EXISTS {join_table}")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_ProjectionIndependence("1.0"))
def projection_independence(self):
    """Row visibility does not depend on the projected columns: a query not
    selecting the writer's predicate column still excludes deleted rows."""
    rows = 100

    with Given(
        "a table where Spark deleted rows by customer_id, a column the "
        "ClickHouse queries below never project"
    ):
        table = common.table_with_deletion_vectors(
            rows=0,
            columns="id BIGINT, customer_id BIGINT, amount BIGINT",
            setup_statements=[
                "INSERT INTO {table} SELECT /*+ COALESCE(1) */ id, 100 + id % 10, id * 2 "
                "FROM range(100)",
                "DELETE FROM {table} WHERE customer_id = 100",
            ],
        )

    surviving = [i for i in range(rows) if 100 + i % 10 != 100]

    with Check("projecting only amount"):
        result = common.read_result(table=table, columns="sum(amount), count()")
        assert result.output.split() == [
            str(sum(i * 2 for i in surviving)),
            str(len(surviving)),
        ], error(result.output)

    with Check("projecting only id"):
        common.assert_visible_ids(table=table, ids=surviving)

    with Check("projecting all columns"):
        result = common.read_result(table=table, columns="count()")
        assert int(result.output.strip()) == len(surviving), error(result.output)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_CombinedFilters("1.0"))
def combined_filters(self):
    """Deletion vector, equality delete, and user predicate compose as
    vector → other delete semantics → predicate, identically for WHERE and
    PREWHERE."""
    rows = 100
    dv_deleted = set(range(0, rows, 10))
    eq_deleted = {5, 20, 55}  # 20 overlaps the vector

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )

    with And("an equality delete overlapping the vector"):
        delete_files.add_equality_delete(
            namespace=table.namespace,
            table_name=table.table_name,
            ids=sorted(eq_deleted),
        )
        common.drop_iceberg_metadata_cache()

    survivors = [i for i in range(rows) if i not in dv_deleted | eq_deleted]
    predicate = "id % 3 = 0"
    expected = [i for i in survivors if i % 3 == 0]

    with Check("user predicate as WHERE"):
        result = common.read_result(
            table=table,
            columns="id",
            where_clause=predicate,
            order_by="id",
            settings=[("use_iceberg_metadata_files_cache", "0")],
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == expected, error(
            f"WHERE: rows matched by any filter must be absent exactly once, "
            f"got {len(ids)} rows"
        )

    with Check("user predicate as PREWHERE"):
        engine_table = common.engine_table(table=table)
        result = self.context.node.query(
            f"SELECT id FROM {engine_table} PREWHERE {predicate} "
            f"ORDER BY id FORMAT TabSeparated",
            settings=[("use_iceberg_metadata_files_cache", "0")],
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == expected, error(f"PREWHERE returned {len(ids)} rows")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_SchemaEvolution("1.0"))
def schema_evolution(self):
    """A deletion vector stays valid across ADD COLUMN, column rename, and
    column drop; added columns are NULL for surviving rows."""
    rows = 100
    deleted = list(range(0, rows, 10))
    expected = common.expected_ids(rows, deleted)

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )

    with When("a column is added, and the data column is renamed"):
        spark.alter_table(
            namespace=table.namespace,
            table_name=table.table_name,
            alter_clauses=[
                "ADD COLUMN extra INT",
                "RENAME COLUMN data TO payload",
            ],
        )

    with Then("row visibility is unchanged for projections over any column"):
        common.assert_visible_ids(table=table, ids=expected)
        result = common.read_result(
            table=table, columns="id, payload", order_by="id"
        )
        lines = [line for line in result.output.splitlines() if line.strip()]
        assert len(lines) == len(expected), error(
            f"projection over renamed column returned {len(lines)} rows"
        )

    with And("the added column is NULL for every surviving row"):
        result = common.read_result(
            table=table, columns="countIf(isNull(extra)), count()"
        )
        null_count, total = result.output.split()
        assert null_count == total == str(len(expected)), error(result.output)

    with When("the renamed data column is dropped"):
        spark.alter_table(
            namespace=table.namespace,
            table_name=table.table_name,
            alter_clauses=["DROP COLUMN payload"],
        )

    with Then("row visibility is still unchanged"):
        common.assert_visible_ids(table=table, ids=expected)


@TestFeature
@Name("query semantics")
def feature(self, minio_root_user, minio_root_password):
    """Query semantics over deletion vectors."""
    Scenario(run=operator_independence)
    Scenario(run=projection_independence)
    Scenario(run=combined_filters)
    Scenario(run=schema_evolution)
