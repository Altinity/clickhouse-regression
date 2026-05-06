"""TRUNCATE scenarios against destinations previously populated by EXPORT PARTITION.

Verifies that ``TRUNCATE TABLE <iceberg_dest>`` against a destination
already populated by EXPORT (or a mix of EXPORT and INSERT) drops to
zero rows, that a follow-up EXPORT repopulates cleanly, and that the
snapshot chain advances past the pre-truncate snapshot.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_Truncate,
    RQ_Iceberg_ExportPartition_Truncate_RepopulateAfterTruncate,
    RQ_Iceberg_ExportPartition_Truncate_AfterDirectInsert,
)

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
    insert_into_iceberg_destination,
    truncate_iceberg_destination,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    as_destination_name,
    as_pyiceberg_handle,
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    load_pyiceberg_table,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
    select_from_destination,
)


SIMPLE_COLUMNS = "id Int64, year Int32"
SIMPLE_PARTITION_BY = "year"


def _current_snapshot_id(destination, minio_root_user, minio_root_password):
    """Return the current snapshot id for catalog-backed destinations,
    or ``None`` for ``no_catalog`` mode (no live catalog handle to
    refresh against).
    """
    if as_pyiceberg_handle(destination) is None:
        return None
    table = load_pyiceberg_table(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    snapshot = table.current_snapshot()
    return snapshot.snapshot_id if snapshot else None


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Truncate("1.0"))
@Name("truncate after export")
def truncate_after_export(self, minio_root_user, minio_root_password):
    """``TRUNCATE`` after ``EXPORT PARTITION`` drops the destination
    back to zero rows.
    """
    source_table = f"mt_{getuid()}"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )

    with And("insert data into two partitions on the source"):
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2020), (3, 2021)",
        )

    with And("create the Iceberg destination table"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export both partitions"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2021",
        )

    with And("destination has the expected rows before TRUNCATE"):
        assert_destination_row_count(
            destination=destination,
            expected=3,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("TRUNCATE the iceberg destination"):
        # Glue note: if this call fails on the double-slash symptom,
        # that's IcebergMetadata::truncate constructing its own
        # catalog_filename independently of IcebergWrites.cpp. Surface
        # the exact statement we ran so triage can reproduce.
        truncate_iceberg_destination(destination=destination)

    with Then("destination is empty after TRUNCATE"):
        assert_destination_row_count(
            destination=destination,
            expected=0,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("SELECT returns no rows (belt and braces over count())"):
        output = select_from_destination(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns="*",
            order_by="id",
        ).output
        assert output.strip() == "", error(
            f"expected empty destination after TRUNCATE, got:\n{output}"
        )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Truncate_RepopulateAfterTruncate("1.0"))
@Name("export after truncate repopulates destination")
def export_after_truncate(self, minio_root_user, minio_root_password):
    """After ``TRUNCATE`` a fresh ``EXPORT`` repopulates the destination
    and the snapshot id advances past the pre-truncate one.
    """
    source_table = f"mt_{getuid()}"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )

    with And("insert data into three partitions on the source"):
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2020), (3, 2021), (4, 2022)",
        )

    with And("create the Iceberg destination table"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export the 2020 partition"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    pre_truncate_snapshot = _current_snapshot_id(
        destination, minio_root_user, minio_root_password
    )

    with When("TRUNCATE the destination"):
        truncate_iceberg_destination(destination=destination)

    with Then("destination is empty"):
        assert_destination_row_count(
            destination=destination,
            expected=0,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export a different partition"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2022",
        )

    with Then("destination has only the re-exported partition"):
        assert_destination_row_count(
            destination=destination,
            expected=1,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        output = select_from_destination(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns="id, year",
            order_by="id",
        ).output.strip()
        assert output == "4\t2022", error(
            f"expected only (4, 2022) after re-export, got:\n{output}"
        )

    with And("catalog snapshot id advanced past the pre-truncate one"):
        post_snapshot = _current_snapshot_id(
            destination, minio_root_user, minio_root_password
        )
        if pre_truncate_snapshot is not None and post_snapshot is not None:
            assert post_snapshot != pre_truncate_snapshot, error(
                f"snapshot id did not advance across TRUNCATE+EXPORT: "
                f"before={pre_truncate_snapshot} after={post_snapshot}"
            )


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Truncate_AfterDirectInsert("1.0"))
@Name("truncate after insert")
def truncate_after_insert(self, minio_root_user, minio_root_password):
    """``TRUNCATE`` drops a destination populated by both ``EXPORT
    PARTITION`` and ``INSERT INTO``.
    """
    source_table = f"mt_{getuid()}"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )

    with And("insert one partition on the source"):
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2020)",
        )

    with And("create the Iceberg destination table"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("EXPORT the partition and then INSERT more rows"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )
        insert_into_iceberg_destination(
            destination=destination,
            values="(10, 2099), (11, 2099)",
        )

    with And("destination has 4 rows before TRUNCATE"):
        assert_destination_row_count(
            destination=destination,
            expected=4,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("TRUNCATE the destination"):
        truncate_iceberg_destination(destination=destination)

    with Then("destination is empty"):
        assert_destination_row_count(
            destination=destination,
            expected=0,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_Truncate("1.0"))
@Name("truncate")
def feature(self, minio_root_user, minio_root_password):
    """TRUNCATE after / around EXPORT PARTITION."""
    Scenario(test=truncate_after_export, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=export_after_truncate, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=truncate_after_insert, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
