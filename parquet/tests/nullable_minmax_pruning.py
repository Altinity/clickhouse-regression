"""Row-group and page min/max pruning on a nullable Parquet column.

Row groups, 100 rows each:

* group 0 is ``'aaa'`` plus one null
* group 1 is ``'sg2o27m'`` plus one null
* group 2 is ``'zzz'`` plus one null
* group 3 is all nulls

Pages are one row group of 3000 rows. Every tenth row is null, and the
non-null values are ``'aaa'``, ``'sg2o27m'``, then ``'zzz'`` in bands of
1000. Page size is in bytes, so a page does not line up with a band.
Equality on the probe reads 2 pages and prunes 1. A predicate that is true
for NULL reads all 3, because every page contains a null.

Min/max is the non-null range. A chunk is pruned when that range misses the
predicate and a SQL NULL in the chunk cannot make the predicate true.
``assumeNotNull`` and every ``IN`` / ``NOT IN`` can match NULL, so a chunk
that contains NULL is read. ``transform_null_in`` changes the row count.
"""

from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid


PROBE = "sg2o27m"

# (predicate, extra settings, rows, read, pruned)
ROW_GROUP_CASES = [
    (f"partner_id = '{PROBE}'", [], 99, 1, 3),
    ("partner_id = 'aaa'", [], 99, 1, 3),
    ("partner_id = 'zzz'", [], 99, 1, 3),
    (f"NOT partner_id = '{PROBE}'", [], 198, 2, 2),
    (f"partner_id <=> '{PROBE}'", [], 99, 1, 3),
    ("partner_id IS NULL", [], 103, 4, 0),
    (f"partner_id = '{PROBE}' OR partner_id IS NULL", [], 202, 4, 0),
    ("assumeNotNull(partner_id) = ''", [], 103, 4, 0),
    # assumeNotNull is a monotonic wrapper, so a NULL in the group can match.
    ("assumeNotNull(partner_id) = 'aaa'", [], 99, 4, 0),
    # IN / NOT IN do not record transform_null_in on the RPN, so a group
    # that contains NULL is read either way. The row count still differs.
    (f"partner_id IN ('{PROBE}')", [], 99, 4, 0),
    (f"partner_id IN ('{PROBE}', NULL)", [], 99, 4, 0),
    (f"partner_id IN ('{PROBE}', NULL)", [("transform_null_in", 1)], 202, 4, 0),
    ("partner_id NOT IN ('zzz')", [], 198, 4, 0),
    ("partner_id NOT IN ('zzz')", [("transform_null_in", 1)], 301, 4, 0),
    ("NOT (partner_id <=> 'zzz')", [], 301, 4, 0),
    (f"NOT (partner_id <=> '{PROBE}')", [], 301, 4, 0),
]

# Page splits follow data_page_size, not the 1000-row bands. Prune counts
# are pinned when they match the probe equality (2 read, 1 pruned) or when
# NULL keeps every page (3 read, 0 pruned).
PAGE_CASES = [
    (f"partner_id = '{PROBE}'", [], 900, 2, 1),
    (f"partner_id <=> '{PROBE}'", [], 900, 2, 1),
    # Every page has a null, and IN keeps such a page. See the row-group note.
    (f"partner_id IN ('{PROBE}')", [], 900, 3, 0),
    (f"partner_id IN ('{PROBE}', NULL)", [], 900, 3, 0),
    ("partner_id IS NULL", [], 300, 3, 0),
    (f"partner_id = '{PROBE}' OR partner_id IS NULL", [], 1200, 3, 0),
    ("assumeNotNull(partner_id) = ''", [], 300, 3, 0),
    (f"partner_id IN ('{PROBE}', NULL)", [("transform_null_in", 1)], 1200, 3, 0),
    ("partner_id NOT IN ('zzz')", [("transform_null_in", 1)], 2100, 3, 0),
    ("NOT (partner_id <=> 'zzz')", [], 2100, 3, 0),
    (f"NOT (partner_id <=> '{PROBE}')", [], 2100, 3, 0),
]

# These predicates are true on one band only, or reject NULL, so which page
# they prune depends on the byte split. The row count is still fixed.
PAGE_ROW_CASES = [
    ("partner_id = 'aaa'", [], 900),
    ("partner_id = 'zzz'", [], 900),
    (f"NOT partner_id = '{PROBE}'", [], 1800),
    ("assumeNotNull(partner_id) = 'aaa'", [], 900),
    ("partner_id NOT IN ('zzz')", [], 1800),
]

_READ_SETTINGS = [
    ("input_format_parquet_bloom_filter_push_down", 0),
    ("input_format_parquet_dictionary_filter_push_down", 0),
    ("use_cache_for_count_from_files", 0),
]


def _label(predicate, extra):
    if not extra:
        return predicate
    settings = ", ".join(f"{name} = {value}" for name, value in extra)
    return f"{predicate} SETTINGS {settings}"


def _profile_events(node, log_comment, names):
    columns = ", ".join(f"ProfileEvents['{name}']" for name in names)
    output = ""
    for retry in retries(count=10, delay=1):
        with retry:
            node.query("SYSTEM FLUSH LOGS")
            result = node.query(
                f"""
                SELECT {columns}
                FROM system.query_log
                WHERE log_comment = '{log_comment}'
                  AND type = 'QueryFinish'
                """
            )
            output = result.output.strip()
            assert output, error()
    lines = output.splitlines()
    assert len(lines) == 1, error()
    return [int(value) for value in lines[0].split("\t")]


def _check(
    node,
    file_name,
    predicate,
    rows,
    read_event,
    pruned_event,
    extra,
    read=None,
    pruned=None,
    chunks=None,
):
    """Check the row count and the read and pruned profile events.

    When ``read`` is omitted, ``chunks`` is the page total. The two counters
    must add up to it. Which pages are pruned follows the byte page size.
    """
    log_comment = f"nullable_minmax_{getuid()}"
    result = node.query(
        f"SELECT count() FROM file('{file_name}', Parquet) WHERE {predicate}",
        settings=[
            ("log_comment", log_comment),
            *_READ_SETTINGS,
            *(extra or []),
        ],
    )
    got_rows = int(result.output.strip())
    got_read, got_pruned = _profile_events(
        node, log_comment, (read_event, pruned_event)
    )
    assert got_rows == rows, error()
    if read is None:
        assert got_read + got_pruned == chunks, error()
        return
    assert got_read == read, error()
    assert got_pruned == pruned, error()


def _write(node, file_name, select, settings):
    node.query(
        "INSERT INTO FUNCTION file("
        f"'{file_name}', Parquet, 'partner_id Nullable(String)') {select}",
        settings=[
            ("max_threads", 1),
            ("max_insert_threads", 1),
            *settings,
        ],
    )


def _remove(node, file_name):
    node.command(f"rm -f /var/lib/clickhouse/user_files/{file_name}")


@TestScenario
def row_groups(self):
    """Prune nullable row groups from column-chunk min/max."""
    node = self.context.node
    file_name = f"nullable_minmax_row_groups_{getuid()}.parquet"
    try:
        with Given("four row groups, the last one all nulls"):
            _write(
                node,
                file_name,
                """
                SELECT CAST(
                    multiIf(
                        number >= 300, NULL,
                        number % 100 = 0, NULL,
                        ['aaa', 'sg2o27m', 'zzz'][intDiv(number, 100) + 1]),
                    'Nullable(String)') AS partner_id
                FROM numbers(400)
                """,
                [
                    ("output_format_parquet_row_group_size", 100),
                    ("output_format_parquet_write_page_index", 1),
                    ("max_block_size", 1000),
                ],
            )

        with Then("each predicate returns the matching rows and prunes the rest"):
            for predicate, extra, rows, read, pruned in ROW_GROUP_CASES:
                with By(_label(predicate, extra)):
                    _check(
                        node,
                        file_name,
                        predicate,
                        rows,
                        "ParquetReadRowGroups",
                        "ParquetPrunedRowGroups",
                        extra,
                        read=read,
                        pruned=pruned,
                    )
    finally:
        with Finally("remove the parquet file"):
            _remove(node, file_name)


@TestScenario
def pages(self):
    """Prune nullable data pages from the page index."""
    node = self.context.node
    file_name = f"nullable_minmax_pages_{getuid()}.parquet"
    try:
        with Given("one row group and a page index over three value bands"):
            _write(
                node,
                file_name,
                """
                SELECT CAST(
                    if(number % 10 = 0, NULL,
                       ['aaa', 'sg2o27m', 'zzz'][intDiv(number, 1000) + 1]),
                    'Nullable(String)') AS partner_id
                FROM numbers(3000)
                """,
                [
                    ("output_format_parquet_row_group_size", 3000),
                    ("output_format_parquet_data_page_size", 128),
                    ("output_format_parquet_max_dictionary_size", 0),
                    ("output_format_parquet_write_page_index", 1),
                    ("max_block_size", 10000),
                ],
            )

        with Then("null-rejecting and null-keeping predicates prune as specified"):
            for predicate, extra, rows, read, pruned in PAGE_CASES:
                with By(_label(predicate, extra)):
                    _check(
                        node,
                        file_name,
                        predicate,
                        rows,
                        "ParquetReadPages",
                        "ParquetPrunedPages",
                        extra,
                        read=read,
                        pruned=pruned,
                    )

        with And("band predicates still return the right rows"):
            for predicate, extra, rows in PAGE_ROW_CASES:
                with By(_label(predicate, extra)):
                    _check(
                        node,
                        file_name,
                        predicate,
                        rows,
                        "ParquetReadPages",
                        "ParquetPrunedPages",
                        extra,
                        chunks=3,
                    )
    finally:
        with Finally("remove the parquet file"):
            _remove(node, file_name)


@TestFeature
@Name("nullable minmax pruning")
def feature(self, node="clickhouse1"):
    """Nullable Parquet row-group and page min/max pruning."""
    self.context.node = self.context.cluster.node(node)
    Scenario(test=row_groups)()
    Scenario(test=pages)()
