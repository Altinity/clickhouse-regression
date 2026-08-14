"""Covering-set construction for the parquet-variety feature.

The full cross product of file-shape dimensions is impractical to produce
with the Spark writer (~30 s of JVM per table), so the feature Spark-writes
one table per *file shape* from a pairwise covering set — every pair of
dimension values appears in at least one shape — and then applies every
deleted-position pattern to every shape by crafting replacement vectors,
which costs seconds instead of a writer commit.

The covering set is built deterministically on the rows × codec grid, with
row-group layout and schema assigned by rotating indices; pairwise coverage
is machine-checked by :func:`assert_pairwise_coverage`, so editing the
dimension lists cannot silently lose a pair.
"""

import random
from collections import namedtuple

from testflows.core import *
from testflows.asserts import error

from iceberg.tests.deletion_vectors.steps import common
from iceberg.tests.deletion_vectors.steps import schemas

FileShape = namedtuple("FileShape", ["rows", "row_groups", "codec", "schema"])

# the smallest DV-bearing file has 2 rows: a writer DELETE covering a whole
# file becomes a metadata-only file drop and produces no vector
ROWS_OPTIONS = (2, 100, 10_000, 100_000)

ROW_GROUP_OPTIONS = {
    "default": {},
    "tiny": {
        "write.parquet.row-group-size-bytes": "4096",
        "write.parquet.page-size-bytes": "1024",
    },
}

CODEC_OPTIONS = ("zstd", "snappy", "gzip", "uncompressed")

SCHEMA_OPTIONS = tuple(schemas.SCHEMAS)

RANDOM_PATTERN_SEED = 48  # stable expected sets across runs (SRS-048)


def covering_set():
    """Pairwise covering set of file shapes: all rows × codec combinations,
    with row-group layout and schema rotating so that every pair of values
    across any two dimensions co-occurs in at least one shape."""
    group_names = tuple(ROW_GROUP_OPTIONS)
    shapes = []
    for rows_index, rows in enumerate(ROWS_OPTIONS):
        for codec_index, codec in enumerate(CODEC_OPTIONS):
            rotation = rows_index + codec_index
            shapes.append(
                FileShape(
                    rows=rows,
                    row_groups=group_names[rotation % len(group_names)],
                    codec=codec,
                    schema=SCHEMA_OPTIONS[rotation % len(SCHEMA_OPTIONS)],
                )
            )
    return shapes


def shape_name(shape):
    return (
        f"{shape.rows} rows, {shape.row_groups} row groups, "
        f"{shape.codec}, {shape.schema}"
    )


def assert_pairwise_coverage(shapes):
    """Every pair of values across any two dimensions appears in at least
    one shape — the guard that keeps the covering set honest when the
    dimension lists change."""
    dimensions = {
        "rows": ROWS_OPTIONS,
        "row_groups": tuple(ROW_GROUP_OPTIONS),
        "codec": CODEC_OPTIONS,
        "schema": SCHEMA_OPTIONS,
    }
    names = list(dimensions)
    covered = {
        (a, b): {(getattr(s, a), getattr(s, b)) for s in shapes}
        for i, a in enumerate(names)
        for b in names[i + 1 :]
    }
    missing = [
        (a, value_a, b, value_b)
        for (a, b), pairs in covered.items()
        for value_a in dimensions[a]
        for value_b in dimensions[b]
        if (value_a, value_b) not in pairs
    ]
    assert not missing, f"covering set misses dimension pairs: {missing}"


def delete_patterns(rows):
    """name → sorted deleted positions for a file of *rows* rows. Patterns
    are defined relative to the row count so every shape gets meaningful
    (if degenerate for tiny files) instances of each."""
    quarter = max(1, rows // 4)
    seeded = random.Random(RANDOM_PATTERN_SEED)
    return {
        "empty vector": [],
        "single row": [rows // 2],
        "sparse": list(range(0, rows, max(2, rows // 100))),
        "alternating": list(range(0, rows, 2)),
        "dense": [position for position in range(rows) if position % 10 != 0],
        "prefix run": list(range(quarter)),
        "suffix run": list(range(rows - quarter, rows)),
        "pseudo random": sorted(seeded.sample(range(rows), max(1, rows // 10))),
    }


@TestStep(Given)
def file_shape_table(self, shape):
    """Spark-written table matching one covering-set file shape, with one
    replaceable vector entry (a DELETE of a single row) and the physical
    row order of its single data file captured.

    Returns (table, ids_in_order).
    """
    columns, insert = schemas.columns_and_insert(shape.schema, shape.rows)

    with By(f"creating a table shaped as {shape_name(shape)}"):
        table = common.table_with_deletion_vectors(
            rows=0,
            columns=columns,
            extra_properties={
                "write.parquet.compression-codec": shape.codec,
                **ROW_GROUP_OPTIONS[shape.row_groups],
            },
            setup_statements=[insert, "DELETE FROM {table} WHERE id = 0"],
        )

    with And("capturing the physical row order of its single data file"):
        common.assert_data_file_count(table=table, count=1)
        ids_in_order = common.parquet_column_values(table=table)
        assert len(ids_in_order) == shape.rows, error(
            f"data file holds {len(ids_in_order)} rows, expected {shape.rows}"
        )

    return table, ids_in_order
