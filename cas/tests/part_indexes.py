"""Indexes that ClickHouse stores in a part, published through a CAS manifest.

A column ``.bin`` and ``primary.idx`` are blobs. A skip-index or text-index
file of 1 MiB or less is stored inline in the part manifest. The manifest
refuses a part whose inline files together pass 16 MiB. The customer's
otel_logs merges fail that way on text indexes: each source part commits,
and the merge is what crosses the cap.

These scenarios expect the publication to commit. A server that still
rejects the oversized manifest fails the scenario.
"""

from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from cas.requirements.requirements import (
    RQ_SRS_048_CAS_MergeTree,
    RQ_SRS_048_CAS_ObjectModel_Manifests,
)
from cas.tests.steps import (
    active_part_disk,
    create_cas_merge_tree_table,
)

INLINE_ENTRY_CAP = 1024 * 1024

WIDE = [
    "min_bytes_for_wide_part = 0",
    "min_rows_for_wide_part = 0",
]


def _word_expr(index_expr):
    """Eight letters from a mixed integer.

    ``splitByNonAlpha`` drops digits, and a run of ``w1 w2 w3`` compresses
    away. The inline cap measures the stored index.
    """
    mixed = f"bitXor(multiply({index_expr}, 2654435761), 2246822519)"
    piece = mixed
    parts = []
    for _ in range(8):
        parts.append(
            f"substring('abcdefghijklmnopqrstuvwxyz', ({piece}) % 26 + 1, 1)"
        )
        piece = f"intDiv({piece}, 26)"
    return "concat(" + ", ".join(parts) + ")"


def _token_rows(op_id, n_text, tokens):
    """One row whose text columns hold ``tokens`` words.

    Parts use disjoint words, so a merge unions the dictionaries.
    """
    start = op_id * tokens
    words = (
        f"arrayStringConcat(arrayMap(i -> {_word_expr(f'(i + {start})')}, "
        f"range({tokens})), ' ')"
    )
    cols = [f"{op_id} AS id", f"{words} AS body"]
    cols += [f"{words} AS t{i}" for i in range(n_text)]
    return "SELECT " + ", ".join(cols)


def _create(self, suffix, columns, order_by="id", extra_settings=None):
    table = f"cas_part_idx_{suffix}_{getuid()}"
    create_cas_merge_tree_table(
        table_name=table,
        columns=columns,
        partition_by="tuple()",
        order_by=order_by,
        extra_settings=WIDE + (extra_settings or []),
    )
    return table


def _part_row(node, table):
    """Active part count, rows, secondary-index bytes, primary-key bytes."""
    text = node.query(
        "SELECT count(), sum(rows), "
        "sum(secondary_indices_compressed_bytes), "
        "sum(primary_key_bytes_in_memory) "
        f"FROM system.parts WHERE database = currentDatabase() "
        f"AND table = '{table}' AND active "
        "FORMAT TabSeparated"
    ).output.strip()
    parts, rows, secondary, primary = text.split("\t")
    return int(parts), int(rows), int(secondary), int(primary)


def _publish(self, table, inserts, query_settings=None):
    """Insert each statement as its own part, then merge them."""
    node = self.context.node
    for sql in inserts:
        node.query(
            f"INSERT INTO {table} {sql}",
            settings=query_settings,
        )
    node.query(f"OPTIMIZE TABLE {table} FINAL", settings=query_settings)
    parts, rows, secondary, primary = _part_row(node, table)
    disk = active_part_disk(node, table)
    note(
        f"{table}: parts={parts} rows={rows} "
        f"secondary_bytes={secondary} primary_key_bytes={primary} disk={disk}"
    )
    assert disk == self.context.cas_disk_name, error(disk)
    assert parts == 1, error(f"expected one merged part, found {parts}")
    return rows, secondary, primary


def _text_columns(n_text):
    """One text index per string column. A column can carry only one."""
    cols = ["id UInt64", "body String"]
    cols += [f"t{i} String" for i in range(n_text)]
    cols += [
        f"INDEX tx{i} t{i} TYPE text(tokenizer = splitByNonAlpha) GRANULARITY 1"
        for i in range(n_text)
    ]
    return ", ".join(cols)


@TestScenario
@Name("adaptive sparse primary index")
@Requirements(
    RQ_SRS_048_CAS_MergeTree("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Manifests("1.0"),
)
def adaptive_primary_index(self):
    """Default granule size. The sparse primary index is ``primary.idx``."""
    node = self.context.node
    with Given("a wide table ordered by id"):
        table = _create(self, "primary_adaptive", "id UInt64, v String")

    with When("two parts merge on CAS"):
        rows, _, primary = _publish(
            self,
            table,
            [
                "SELECT number, 'alpha' FROM numbers(10000)",
                "SELECT number + 10000, 'beta' FROM numbers(10000)",
            ],
        )

    with Then("the merged part keeps every row and a primary index"):
        assert rows == 20000, error(rows)
        assert primary > 0, error(primary)
        got = node.query(f"SELECT count() FROM {table}").output.strip()
        assert got == "20000", error(got)


@TestScenario
@Name("constant granularity sparse primary index")
@Requirements(
    RQ_SRS_048_CAS_MergeTree("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Manifests("1.0"),
)
def constant_primary_index(self):
    """``index_granularity_bytes = 0`` stores one primary-key entry per granule."""
    node = self.context.node
    with Given("granules of 128 rows"):
        table = _create(
            self,
            "primary_constant",
            "id UInt64, v String",
            extra_settings=[
                "index_granularity = 128",
                "index_granularity_bytes = 0",
            ],
        )

    with When("two parts merge on CAS"):
        rows, _, primary = _publish(
            self,
            table,
            [
                "SELECT number, 'alpha' FROM numbers(4096)",
                "SELECT number + 4096, 'beta' FROM numbers(4096)",
            ],
        )

    with Then("the merged part keeps every row and a primary index"):
        assert rows == 8192, error(rows)
        assert primary > 0, error(primary)
        got = node.query(f"SELECT count() FROM {table}").output.strip()
        assert got == "8192", error(got)


@TestScenario
@Name("large sparse primary index stays a blob")
@Requirements(
    RQ_SRS_048_CAS_MergeTree("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Manifests("1.0"),
)
def large_primary_index(self):
    """One primary-key entry per row, each key 64 bytes.

    ``primary.idx`` is a blob, so a file past 1 MiB still publishes.
    """
    node = self.context.node
    with Given("a granule per row"):
        table = _create(
            self,
            "primary_large",
            "id UInt64, k String",
            order_by="k",
            extra_settings=[
                "index_granularity = 1",
                "index_granularity_bytes = 0",
            ],
        )

    with When("two parts of 64-byte keys merge on CAS"):
        key = (
            "concat(hex(sipHash64({n})), hex(sipHash64({n} + 1)), "
            "hex(sipHash64({n} + 2)), hex(sipHash64({n} + 3)))"
        )
        rows, _, primary = _publish(
            self,
            table,
            [
                f"SELECT number, {key.format(n='number')} FROM numbers(20000)",
                "SELECT number + 20000, "
                f"{key.format(n='(number + 20000)')} FROM numbers(20000)",
            ],
        )

    with Then("the merge commits and the primary index is present"):
        assert rows == 40000, error(rows)
        assert primary > INLINE_ENTRY_CAP, error(
            f"primary index is {primary} bytes, under 1 MiB"
        )
        got = node.query(f"SELECT count() FROM {table}").output.strip()
        assert got == "40000", error(got)


@TestScenario
@Name("sampling key on the sparse primary index")
@Requirements(
    RQ_SRS_048_CAS_MergeTree("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Manifests("1.0"),
)
def sampling_primary_index(self):
    """SAMPLE BY uses a prefix of the sparse primary key."""
    node = self.context.node
    table = f"cas_part_idx_sample_{getuid()}"
    with Given("a table with SAMPLE BY intHash32(id)"):
        create_cas_merge_tree_table(
            table_name=table,
            columns="id UInt64",
            partition_by="tuple()",
            order_by="intHash32(id)",
            extra_settings=WIDE
            + [
                "index_granularity = 128",
                "index_granularity_bytes = 0",
            ],
        )
        node.query(
            f"ALTER TABLE {table} MODIFY SAMPLE BY intHash32(id)"
        )

    with When("the part is published and merged"):
        rows, _, primary = _publish(
            self,
            table,
            [
                "SELECT number FROM numbers(4000)",
                "SELECT number + 4000 FROM numbers(4000)",
            ],
        )

    with Then("SAMPLE reads the merged part"):
        assert rows == 8000, error(rows)
        assert primary > 0, error(primary)
        sampled = node.query(
            f"SELECT count() FROM {table} SAMPLE 0.25"
        ).output.strip()
        assert sampled.isdigit(), error(sampled)
        assert int(sampled) < 8000, error(sampled)


# Data-skipping indexes. Each file stays far under 1 MiB, so the manifest
# accepts the part. vector_similarity is the approximate-nearest-neighbour index.
_SKIP = (
    (
        "minmax",
        "id UInt64, v UInt64, INDEX idx v TYPE minmax GRANULARITY 1",
        ["SELECT 1, 10", "SELECT 2, 20"],
        "SELECT count() FROM {table} WHERE v = 10",
        "1",
    ),
    (
        "set",
        "id UInt64, v UInt64, INDEX idx v TYPE set(100) GRANULARITY 1",
        ["SELECT 1, 10", "SELECT 2, 20"],
        "SELECT count() FROM {table} WHERE v = 20",
        "1",
    ),
    (
        "bloom_filter",
        "id UInt64, v UInt64, INDEX idx v TYPE bloom_filter(0.01) GRANULARITY 1",
        ["SELECT 1, 10", "SELECT 2, 20"],
        "SELECT count() FROM {table} WHERE v = 10",
        "1",
    ),
    (
        "ngrambf_v1",
        "id UInt64, s String, INDEX idx s TYPE ngrambf_v1(3, 256, 2, 0) GRANULARITY 1",
        ["SELECT 1, 'alpha beta'", "SELECT 2, 'gamma delta'"],
        "SELECT count() FROM {table} WHERE s LIKE '%alpha%'",
        "1",
    ),
    (
        "tokenbf_v1",
        "id UInt64, s String, INDEX idx s TYPE tokenbf_v1(256, 2, 0) GRANULARITY 1",
        ["SELECT 1, 'alpha beta'", "SELECT 2, 'gamma delta'"],
        "SELECT count() FROM {table} WHERE hasToken(s, 'gamma')",
        "1",
    ),
    (
        "sparse_grams",
        "id UInt64, s String, "
        "INDEX idx s TYPE sparse_grams(3, 5, 256, 2, 0) GRANULARITY 1",
        ["SELECT 1, 'alpha beta'", "SELECT 2, 'gamma delta'"],
        "SELECT count() FROM {table} WHERE s LIKE '%alpha%'",
        "1",
    ),
    (
        "vector_similarity",
        "id UInt64, v Array(Float32), "
        "INDEX idx v TYPE vector_similarity('hnsw', 'L2Distance', 2) GRANULARITY 1",
        ["SELECT 1, [0.1, 0.2]", "SELECT 2, [0.3, 0.4]"],
        "SELECT count() FROM {table}",
        "2",
    ),
)


@TestScenario
@Name("data skipping indexes publish with the part")
@Requirements(
    RQ_SRS_048_CAS_MergeTree("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Manifests("1.0"),
)
def skipping_indexes(self):
    """Each skip-index type is written into the part and survives the merge."""
    node = self.context.node
    for name, columns, inserts, query, expected in _SKIP:
        with Scenario(name):
            with Given(f"a wide table with a {name} index"):
                table = _create(self, name, columns)
            with When("two parts merge on CAS"):
                rows, secondary, _ = _publish(self, table, inserts)
            with Then("the index bytes were stored and the rows read back"):
                assert rows == 2, error(rows)
                assert secondary > 0, error(
                    f"{name} wrote no secondary index bytes"
                )
                got = node.query(query.format(table=table)).output.strip()
                assert got == expected, error(got)


@TestScenario
@Name("small text index merges")
@Requirements(
    RQ_SRS_048_CAS_MergeTree("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Manifests("1.0"),
)
def small_text_index(self):
    """A few tokens stay under the inline cap, so the merge commits."""
    node = self.context.node
    with Given("one text index"):
        table = _create(
            self,
            "text_small",
            "id UInt64, s String, "
            "INDEX tx s TYPE text(tokenizer = splitByNonAlpha) GRANULARITY 1",
        )

    with When("two parts merge on CAS"):
        rows, secondary, _ = _publish(
            self,
            table,
            ["SELECT 1, 'alpha beta'", "SELECT 2, 'gamma delta'"],
        )

    with Then("hasToken reads the merged part"):
        assert rows == 2, error(rows)
        assert secondary > 0, error(secondary)
        got = node.query(
            f"SELECT count() FROM {table} WHERE hasToken(s, 'alpha')"
        ).output.strip()
        assert got == "1", error(got)


@TestScenario
@Name("text index merge past the 16 MiB inline cap")
@Requirements(
    RQ_SRS_048_CAS_MergeTree("1.0"),
    RQ_SRS_048_CAS_ObjectModel_Manifests("1.0"),
)
def text_index_inline_cap(self):
    """Merge of text-index parts whose inline files pass 16 MiB.

    36 indexes and 50,000 disjoint words per part. Each source part stays
    under the cap. The merge inlines 28,649,320 bytes, and each index stays
    under 1 MiB, so the files remain inline. This is the customer's
    otel_logs failure.
    """
    node = self.context.node
    n_text = 36
    tokens = 50000
    with Given("36 text indexes, one per column"):
        table = _create(self, "text_cap", _text_columns(n_text))

    with When("two source parts merge"):
        for op_id in (0, 1):
            node.query(
                f"INSERT INTO {table} {_token_rows(op_id, n_text, tokens)}"
            )
        before = _part_row(node, table)
        note(f"before merge parts,rows,secondary,primary={before}")
        node.query(f"OPTIMIZE TABLE {table} FINAL")

    with Then("the merge commits and keeps both rows"):
        parts, rows, secondary, _ = _part_row(node, table)
        assert parts == 1, error(parts)
        assert rows == 2, error(rows)
        got = node.query(f"SELECT count() FROM {table}").output.strip()
        assert got == "2", error(got)
        note(f"merged secondary_bytes={secondary}")


@TestFeature
@Name("part indexes")
def feature(self):
    """Sparse primary indexes, data-skipping indexes, and text indexes on CAS."""
    for scenario in loads(current_module(), Scenario):
        scenario()
