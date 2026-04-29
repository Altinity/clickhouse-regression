"""Min/max pruning for Iceberg destinations populated by EXPORT PARTITION.

Verifies that the per-column lower/upper bound stats ClickHouse writes
during ``EXPORT PARTITION`` round-trip through the reader: a predicate
that fits inside one partition's ``id`` range prunes the other data
files (``IcebergMinMaxIndexPrunedFiles`` and ``read_rows`` confirm).
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import RQ_Iceberg_ExportPartition_MinMaxPruning

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_destination_name,
    create_iceberg_destination,
)
from iceberg.tests.steps.metrics import (
    get_IcebergMinMaxIndexPrunedFiles,
    get_read_rows,
)


# A column type ClickHouse/Iceberg will write min/max bounds for, with
# three disjoint partitions so the matching predicate narrows to
# exactly one data file.
COLUMNS = "id Int64, year Int32"
PARTITION_BY = "year"

PARTITION_DATA = {
    "2020": [(1, 2020), (10, 2020), (20, 2020)],
    "2021": [(100, 2021), (110, 2021), (120, 2021)],
    "2022": [(1000, 2022), (1010, 2022), (1020, 2022)],
}

TOTAL_ROWS = sum(len(rows) for rows in PARTITION_DATA.values())
EXPECTED_TOTAL_FILES = len(PARTITION_DATA)


def _values_clause(rows):
    return ", ".join(f"({r[0]}, {r[1]})" for r in rows)


def _int(result):
    raw = result.output.strip()
    try:
        return int(raw)
    except ValueError:
        # Empty ProfileEvent (the key absent from the map) renders as
        # empty string — treat that as zero pruned files.
        return 0


@TestScenario
@Name("minmax pruning on exported data")
def pruning_predicate_narrows_read_rows(self, minio_root_user, minio_root_password):
    """``WHERE id = <value>`` on a destination with three non-overlapping
    per-partition files prunes to exactly one file's worth of rows.
    """
    node = self.context.node
    source_table = f"mt_{getuid()}"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=COLUMNS,
            partition_by=PARTITION_BY,
        )

    with And("insert disjoint ``id`` ranges across three partitions"):
        # Single INSERT per partition keeps one data part per
        # partition on the source, so each EXPORT commits exactly one
        # data file with its own min/max bounds.
        for partition_id, rows in PARTITION_DATA.items():
            insert_data(
                table_name=source_table,
                values=_values_clause(rows),
            )

    with And("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=COLUMNS,
            partition_by=PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export every partition"):
        for partition_id in PARTITION_DATA:
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id=partition_id,
            )

    dest_name = as_destination_name(destination)
    # Pick a target value that lives inside exactly one partition so
    # the other two files can be fully pruned.
    target_id = 1010
    assert any(
        row[0] == target_id for row in PARTITION_DATA["2022"]
    ), "test data drift: target_id must live in the 2022 partition only"

    log_comment = f"minmax_pruning_{getuid()}"

    with When(f"SELECT ... WHERE id = {target_id} with log_comment for metrics"):
        result = node.query(
            f"SELECT id, year FROM {dest_name} WHERE id = {target_id} "
            f"ORDER BY id",
            settings=[("log_comment", log_comment)],
        )
        assert result.output.strip() == f"{target_id}\t2022", error(
            f"unexpected rows for id={target_id} on {dest_name}:\n{result.output}"
        )

    with And("flush logs so query_log has the completed row"):
        node.query("SYSTEM FLUSH LOGS")

    with Then(
        "IcebergMinMaxIndexPrunedFiles reports at least "
        f"{EXPECTED_TOTAL_FILES - 1} pruned files"
    ):
        pruned = _int(get_IcebergMinMaxIndexPrunedFiles(log_comment=log_comment))
        assert pruned >= EXPECTED_TOTAL_FILES - 1, error(
            f"expected >= {EXPECTED_TOTAL_FILES - 1} min/max pruned files, "
            f"got {pruned}. This usually means EXPORT PARTITION did not "
            f"write per-file lower/upper bounds into the manifest, or the "
            f"reader is not applying them for the predicate shape."
        )

    with And("read_rows matches the unpruned partition size, not the full table"):
        # Only the year=2022 data file should be opened; the other two
        # files get skipped before any rows are read.
        read_rows = _int(get_read_rows(log_comment=log_comment))
        matching_file_rows = len(PARTITION_DATA["2022"])
        assert read_rows <= matching_file_rows, error(
            f"read_rows={read_rows} exceeds size of the single matching "
            f"file ({matching_file_rows}); pruning did not limit I/O to "
            f"one data file. Full table has {TOTAL_ROWS} rows."
        )
        assert read_rows > 0, error(
            f"read_rows={read_rows}; expected the matching data file to "
            f"actually be read"
        )


@TestScenario
@Name("minmax pruning on range predicate")
def pruning_range_predicate(self, minio_root_user, minio_root_password):
    """A range predicate fitting inside one partition's ``id`` range
    prunes the other two files.
    """
    node = self.context.node
    source_table = f"mt_{getuid()}"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=COLUMNS,
            partition_by=PARTITION_BY,
        )

    with And("insert the disjoint partitions"):
        for rows in PARTITION_DATA.values():
            insert_data(
                table_name=source_table,
                values=_values_clause(rows),
            )

    with And("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=COLUMNS,
            partition_by=PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export every partition"):
        for partition_id in PARTITION_DATA:
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id=partition_id,
            )

    dest_name = as_destination_name(destination)
    log_comment = f"minmax_range_{getuid()}"

    with When("query with a range that fits inside the 2021 partition"):
        # 2021 ids: 100, 110, 120. Predicate selects all three and
        # nothing from 2020 or 2022.
        result = node.query(
            f"SELECT id FROM {dest_name} WHERE id BETWEEN 100 AND 120 "
            f"ORDER BY id",
            settings=[("log_comment", log_comment)],
        )
        assert result.output.strip().splitlines() == ["100", "110", "120"], error(
            f"unexpected rows for range predicate on {dest_name}:\n"
            f"{result.output}"
        )

    with And("flush logs"):
        node.query("SYSTEM FLUSH LOGS")

    with Then("at least two files were pruned by min/max bounds"):
        pruned = _int(get_IcebergMinMaxIndexPrunedFiles(log_comment=log_comment))
        assert pruned >= EXPECTED_TOTAL_FILES - 1, error(
            f"expected >= {EXPECTED_TOTAL_FILES - 1} min/max pruned files "
            f"for range predicate, got {pruned}"
        )


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_MinMaxPruning("1.0"))
@Name("minmax pruning")
def feature(self, minio_root_user, minio_root_password):
    """Min/max pruning on Iceberg destinations populated by EXPORT PARTITION."""
    Scenario(test=pruning_predicate_narrows_read_rows, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=pruning_range_predicate, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
