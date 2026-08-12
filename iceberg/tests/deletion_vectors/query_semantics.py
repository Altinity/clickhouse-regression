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


@TestStep(Given)
def join_dimension_table(self, rows):
    """A small MergeTree dimension table for the join scenario (dropped on
    cleanup)."""
    node = self.context.node
    join_table = f"dv_join_{getuid()}"
    try:
        node.query(
            f"CREATE TABLE {join_table} (id Int64, tag String) "
            f"ENGINE = MergeTree ORDER BY id"
        )
        node.query(
            f"INSERT INTO {join_table} SELECT number, concat('t', toString(number)) "
            f"FROM numbers({rows})"
        )
        yield join_table
    finally:
        with Finally("drop the join table"):
            node.query(f"DROP TABLE IF EXISTS {join_table}")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_OperatorIndependence("1.0"))
def operator(self, name, iceberg_query, oracle_query):
    """One relational operator observes exactly the post-vector row set."""
    node = self.context.node
    with Then("the Iceberg row set equals the oracle row set"):
        iceberg_result = node.query(f"{iceberg_query} FORMAT TabSeparated")
        oracle_result = node.query(f"{oracle_query} FORMAT TabSeparated")
        assert iceberg_result.output == oracle_result.output, error(
            f"operator '{name}' observed a different row set"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_OperatorIndependence("1.0"))
def prewhere(self):
    """PREWHERE maps surviving rows back to correct absolute positions."""
    ctx = self.context
    with Then("the PREWHERE row set equals the oracle row set"):
        prewhere_result = ctx.node.query(
            f"SELECT id FROM {ctx.engine_table} PREWHERE data = '10' "
            f"ORDER BY id FORMAT TabSeparated"
        )
        where_result = ctx.node.query(
            f"SELECT id FROM {ctx.oracle} WHERE data = '10' "
            f"ORDER BY id FORMAT TabSeparated"
        )
        assert prewhere_result.output == where_result.output, error(
            "PREWHERE returned a different row set than the oracle"
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_OperatorIndependence("1.0"))
def operator_independence(self):
    """Every relational operator observes exactly the post-vector row set;
    a MergeTree table holding the surviving rows is the oracle."""
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

    with And("a small dimension table for the join scenario"):
        join_table = join_dimension_table(rows=rows)

    with And("an Iceberg engine table for the PREWHERE scenario"):
        self.context.engine_table = common.engine_table(table=table)
        self.context.oracle = oracle

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

    for name, (iceberg_query, oracle_query) in query_pairs.items():
        Scenario(test=operator, name=name)(
            name=name, iceberg_query=iceberg_query, oracle_query=oracle_query
        )

    Scenario(run=prewhere)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_ProjectionIndependence("1.0"))
def project_amount_only(self):
    """A query projecting only the amount column excludes deleted rows."""
    ctx = self.context
    with Then("aggregates reflect only surviving rows"):
        result = common.read_result(table=ctx.table, columns="sum(amount), count()")
        assert result.output.split() == [
            str(sum(i * 2 for i in ctx.surviving)),
            str(len(ctx.surviving)),
        ], error(result.output)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_ProjectionIndependence("1.0"))
def project_id_only(self):
    """A query projecting only the id column excludes deleted rows."""
    ctx = self.context
    with Then("the visible row set matches"):
        common.assert_visible_ids(table=ctx.table, ids=ctx.surviving)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_ProjectionIndependence("1.0"))
def project_all_columns(self):
    """A query over all columns excludes deleted rows."""
    ctx = self.context
    with Then("the count reflects only surviving rows"):
        result = common.read_result(table=ctx.table, columns="count()")
        assert int(result.output.strip()) == len(ctx.surviving), error(result.output)


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_ProjectionIndependence("1.0"))
def projection_independence(self):
    """Row visibility does not depend on the projected columns: a query not
    selecting the writer's predicate column still excludes deleted rows."""
    rows = 100

    with Given(
        "a table where Spark deleted rows by customer_id, a column the "
        "scenarios below never project"
    ):
        self.context.table = common.table_with_deletion_vectors(
            rows=0,
            columns="id BIGINT, customer_id BIGINT, amount BIGINT",
            setup_statements=[
                "INSERT INTO {table} SELECT /*+ COALESCE(1) */ id, "
                "100 + id % 10, id * 2 FROM range(100)",
                "DELETE FROM {table} WHERE customer_id = 100",
            ],
        )
        self.context.surviving = [i for i in range(rows) if 100 + i % 10 != 100]

    Scenario(run=project_amount_only)
    Scenario(run=project_id_only)
    Scenario(run=project_all_columns)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_CombinedFilters("1.0"))
def predicate_as_where(self):
    """Vector, equality delete, and a WHERE predicate compose."""
    ctx = self.context
    with Then("all three filters compose"):
        result = common.read_result(
            table=ctx.table,
            columns="id",
            where_clause=ctx.predicate,
            order_by="id",
            settings=[("use_iceberg_metadata_files_cache", "0")],
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == ctx.expected, error(
            f"WHERE: rows matched by any filter must be absent exactly "
            f"once, got {len(ids)} rows"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_CombinedFilters("1.0"))
def predicate_as_prewhere(self):
    """Vector, equality delete, and a PREWHERE predicate compose."""
    ctx = self.context
    with Then("all three filters compose"):
        result = ctx.node.query(
            f"SELECT id FROM {ctx.engine_table} PREWHERE {ctx.predicate} "
            f"ORDER BY id FORMAT TabSeparated",
            settings=[("use_iceberg_metadata_files_cache", "0")],
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == ctx.expected, error(f"PREWHERE returned {len(ids)} rows")


@TestSuite
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

    with And("an Iceberg engine table for the PREWHERE scenario"):
        self.context.engine_table = common.engine_table(table=table)

    survivors = [i for i in range(rows) if i not in dv_deleted | eq_deleted]
    self.context.table = table
    self.context.predicate = "id % 3 = 0"
    self.context.expected = [i for i in survivors if i % 3 == 0]

    Scenario(run=predicate_as_where)
    Scenario(run=predicate_as_prewhere)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_IOReductionOptimizations("1.0"))
def filter_push_down_parity(self, setting_value):
    """The post-vector row set is identical with Parquet predicate
    push-down enabled or disabled."""
    ctx = self.context
    with Then("the filtered row set matches the expected survivors"):
        ids = common.select_ids(
            table=ctx.table,
            where_clause="label = 'batch-1'",
            settings=[("input_format_parquet_filter_push_down", setting_value)],
        )
        assert ids == ctx.expected, error(
            f"push_down={setting_value} returned {len(ids)} rows, "
            f"expected {len(ctx.expected)}"
        )

    with And("the count agrees"):
        count = common.count_rows(
            table=ctx.table,
            settings=[("input_format_parquet_filter_push_down", setting_value)],
        )
        assert count == len(ctx.expected), error(f"count = {count}")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_IOReductionOptimizations("1.0"))
def constant_column_reads(self):
    """Queries projecting or filtering a constant-value column (min = max
    in the file statistics, eligible for read elision) still reflect only
    surviving rows."""
    ctx = self.context

    with Then("an aggregation grouped by the constant column is exact"):
        result = common.read_result(
            table=ctx.table, columns="label, count()", group_by="label"
        )
        assert result.output.split() == ["batch-1", str(len(ctx.expected))], error(
            result.output
        )

    with And("a projection of only the constant column has one row per survivor"):
        result = common.read_result(table=ctx.table, columns="label")
        lines = [line for line in result.output.splitlines() if line.strip()]
        assert len(lines) == len(ctx.expected) and set(lines) == {"batch-1"}, error(
            f"constant-column projection returned {len(lines)} rows"
        )

    with And("a filter on the constant column composed with an id filter is exact"):
        ids = common.select_ids(
            table=ctx.table, where_clause="label = 'batch-1' AND id < 50"
        )
        assert ids == [i for i in ctx.expected if i < 50], error(
            f"combined filter returned {len(ids)} rows"
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_QuerySemantics_IOReductionOptimizations("1.0"))
def io_reduction_optimizations(self):
    """Parquet I/O-reducing optimizations (predicate push-down, constant-
    value column detection) do not shift, drop, or resurrect rows filtered
    by a deletion vector."""
    rows = 100

    with Given(
        "a table with a constant-value column (min = max in file "
        "statistics) and a deletion vector"
    ):
        self.context.table = common.table_with_deletion_vectors(
            rows=0,
            columns="id BIGINT, label STRING, data STRING",
            setup_statements=[
                "INSERT INTO {table} SELECT /*+ COALESCE(1) */ id, 'batch-1', "
                f"concat('row-', CAST(id AS STRING)) FROM range({rows})",
                "DELETE FROM {table} WHERE id % 10 = 0",
            ],
        )
        self.context.expected = [i for i in range(rows) if i % 10 != 0]

    for setting_value in ("0", "1"):
        Scenario(
            test=filter_push_down_parity,
            name=f"filter push-down {setting_value}",
        )(setting_value=setting_value)

    Scenario(run=constant_column_reads)


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
        result = common.read_result(table=table, columns="id, payload", order_by="id")
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
    Suite(run=operator_independence)
    Suite(run=projection_independence)
    Suite(run=combined_filters)
    Suite(run=io_reduction_optimizations)
    Scenario(run=schema_evolution)
