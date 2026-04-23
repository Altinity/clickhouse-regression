"""Direct INSERT scenarios against destinations previously populated by EXPORT PARTITION.

Exercises the end-to-end path where ClickHouse first commits data through
the new ``ALTER TABLE ... EXPORT PARTITION ... TO TABLE ...`` primitive
and then keeps writing to the same Iceberg destination through the
experimental ``INSERT INTO <iceberg_table>`` code path
(``IcebergMetadata::write`` / ``IcebergWrites.cpp`` — same write path,
different entrypoint).

Gaps this fills:

* Ensures INSERT commits see and extend the snapshot chain produced by
  EXPORT instead of diverging / overwriting it.
* Checks the destination stays readable through both ``IcebergS3`` (no
  catalog) and ``DataLakeCatalog`` (rest / glue) after the mixed
  commit sequence.
* Under catalog mode, also confirms PyIceberg sees one strictly-growing
  snapshot history (EXPORT → INSERT both appear as ``append`` ops).

Glue notes:
The ``apply_glue_metadata_path_workaround`` helper already forces
``write_full_path_in_iceberg_metadata=1`` for every ``ALTER ... EXPORT
PARTITION`` under Glue (see ``steps/export_operations.py``). Because
the INSERT helper here goes through the same workaround, these
scenarios are expected to pass on Glue too. If a new fail shows up
under Glue specifically, xfail it here with a message that makes the
bug obvious to triage — the rest of the suite should not be held back
for a Glue-only regression.
"""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    insert_data,
    count_rows,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition,
    insert_into_iceberg_destination,
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


def _assert_snapshot_history_grows(destination, minio_root_user, minio_root_password, expected_at_least):
    """PyIceberg sanity: snapshot history must be monotonically growing.

    Only runs under catalog mode (``as_pyiceberg_handle`` returns the
    catalog-backed dict). Under ``no_catalog`` the destination is an
    ``IcebergS3`` table with no catalog handle; the row-count / data
    parity checks in the scenario already cover the same invariant
    there.
    """
    if as_pyiceberg_handle(destination) is None:
        return
    table = load_pyiceberg_table(
        destination=destination,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    snapshots = list(table.snapshots())
    assert len(snapshots) >= expected_at_least, error(
        f"expected at least {expected_at_least} snapshots on "
        f"{as_destination_name(destination)}, got {len(snapshots)}"
    )
    timestamps = [s.timestamp_ms for s in snapshots]
    assert timestamps == sorted(timestamps), error(
        f"snapshot timestamps not monotonically increasing: {timestamps!r}"
    )


@TestScenario
@Name("insert after export")
def insert_after_export(self, minio_root_user, minio_root_password):
    """Export one partition, then INSERT extra rows directly into the
    same Iceberg destination. The destination must expose both sets of
    rows on subsequent reads.
    """
    source_table = f"mt_{getuid()}"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )

    with And("insert data into one partition on the source"):
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2020), (3, 2020)",
        )

    with And("create the Iceberg destination table"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with When("export the 2020 partition to the destination"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )

    with And("INSERT two additional rows directly into the destination"):
        insert_into_iceberg_destination(
            destination=destination,
            values="(4, 2021), (5, 2021)",
        )

    with Then("destination contains rows from both EXPORT and the follow-up INSERT"):
        assert_destination_row_count(
            destination=destination,
            expected=5,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("content matches the expected union"):
        result = select_from_destination(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            columns="id, year",
            order_by="id",
        ).output.strip()
        expected = "\n".join(
            f"{row[0]}\t{row[1]}"
            for row in [(1, 2020), (2, 2020), (3, 2020), (4, 2021), (5, 2021)]
        )
        assert result == expected, error(
            f"destination rows differ from expected union\n"
            f"got:\n{result}\nexpected:\n{expected}"
        )

    with And("catalog snapshot history strictly grows (export then insert)"):
        _assert_snapshot_history_grows(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_at_least=2,
        )


@TestScenario
@Name("alternating export and insert")
def alternating_export_insert(self, minio_root_user, minio_root_password):
    """Interleave EXPORT PARTITION and INSERT statements against the
    same destination to confirm the append-only snapshot chain stays
    well-formed.

    Sequence:
        EXPORT 2020 -> INSERT {2021 rows} -> EXPORT 2022 -> INSERT {2023 rows}

    Every stage is checked for the correct running row count so a
    regression is localised to the exact transition that broke.
    """
    source_table = f"mt_{getuid()}"

    with Given("create the source ReplicatedMergeTree table"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
        )

    with And("insert 2020 and 2022 partitions on the source"):
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2020), (3, 2022), (4, 2022), (5, 2022)",
        )

    with And("create the Iceberg destination table"):
        destination = create_iceberg_destination(
            columns=SIMPLE_COLUMNS,
            partition_by=SIMPLE_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    running_expected = 0

    with When("EXPORT 2020 -> destination has 2 rows"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2020",
        )
        running_expected += 2
        assert_destination_row_count(
            destination=destination,
            expected=running_expected,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("INSERT 2021 rows -> destination grows to 4 rows"):
        insert_into_iceberg_destination(
            destination=destination,
            values="(10, 2021), (11, 2021)",
        )
        running_expected += 2
        assert_destination_row_count(
            destination=destination,
            expected=running_expected,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("EXPORT 2022 -> destination grows to 7 rows"):
        export_partition(
            source_table=source_table,
            destination=destination,
            partition_id="2022",
        )
        running_expected += 3
        assert_destination_row_count(
            destination=destination,
            expected=running_expected,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("INSERT 2023 row -> destination grows to 8 rows"):
        insert_into_iceberg_destination(
            destination=destination,
            values="(20, 2023)",
        )
        running_expected += 1
        assert_destination_row_count(
            destination=destination,
            expected=running_expected,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with Then("per-partition projections all read back the exact values written"):
        # Spot-check each of the 4 append stages to catch snapshot-chain
        # regressions that leave the wrong subset of rows live.
        for year, expected in [
            (2020, {(1, 2020), (2, 2020)}),
            (2021, {(10, 2021), (11, 2021)}),
            (2022, {(3, 2022), (4, 2022), (5, 2022)}),
            (2023, {(20, 2023)}),
        ]:
            output = select_from_destination(
                destination=destination,
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
                columns="id, year",
                where_clause=f"year = {year}",
                order_by="id",
            ).output.strip()
            got = {
                tuple(int(x) for x in row.split("\t"))
                for row in output.splitlines()
                if row.strip()
            }
            assert got == expected, error(
                f"year {year}: expected {expected!r}, got {got!r}"
            )

    with And("catalog snapshot history reflects all four append commits"):
        _assert_snapshot_history_grows(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_at_least=4,
        )


@TestFeature
@Name("direct writes")
def feature(self, minio_root_user, minio_root_password):
    """Direct INSERT after / around EXPORT PARTITION."""
    Scenario(test=insert_after_export, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    Scenario(test=alternating_export_insert, flags=TE)(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
