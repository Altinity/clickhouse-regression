"""Combinatorial coverage: deletion vectors over a pairwise covering set of
Parquet file shapes (row count × row-group layout × compression codec ×
schema), with every deleted-position pattern applied to every shape.

File shapes are Spark-written once each; position patterns are applied by
crafting replacement vectors, so the expensive writer runs scale with the
number of shapes, not shapes × patterns. Expected row sets derive from the
data file's physical row order, never from assumed insertion order."""

from testflows.core import *

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.variety as variety


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_ParquetVariety("1.0"))
def delete_pattern(self, pattern, positions):
    """One deleted-position pattern against the suite's file shape."""
    ctx = self.context

    with When(f"the vector is replaced to delete {len(positions)} position(s)"):
        common.replace_vector_with_positions(table=ctx.table, positions=positions)

    with Then("exactly the rows at the deleted positions are hidden"):
        common.assert_visible_positions(
            table=ctx.table,
            ids_in_order=ctx.ids_in_order,
            deleted_positions=positions,
        )


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_ParquetVariety("1.0"))
def file_shape(self, shape):
    """Every deleted-position pattern against one covering-set file shape."""
    with Given(f"a Spark-written table shaped as {variety.shape_name(shape)}"):
        self.context.table, self.context.ids_in_order = variety.file_shape_table(
            shape=shape
        )

    for pattern, positions in variety.delete_patterns(shape.rows).items():
        Scenario(test=delete_pattern, name=pattern)(
            pattern=pattern, positions=positions
        )


@TestFeature
@Name("parquet variety")
def feature(self, minio_root_user, minio_root_password):
    """Deletion vectors over a pairwise covering set of Parquet file
    shapes."""
    shapes = variety.covering_set()

    with Given("a covering set where every pair of dimension values appears"):
        variety.assert_pairwise_coverage(shapes)
        note(f"{len(shapes)} file shapes: {[variety.shape_name(s) for s in shapes]}")

    for shape in shapes:
        Suite(test=file_shape, name=variety.shape_name(shape))(shape=shape)
