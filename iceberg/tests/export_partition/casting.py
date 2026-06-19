"""Export casting parity for Altinity/ClickHouse PR 1779.

PR 1779 makes ``EXPORT PARTITION`` / ``EXPORT PART`` apply the same automatic
column casts as ``INSERT INTO <iceberg> SELECT * FROM <source>`` when the
source and destination column types differ positionally
(``canBeSafelyCast`` in ``src/DataTypes/Utils.cpp``). Lossy casts require
``export_merge_tree_part_allow_lossy_cast = 1``.

## Test pattern (every scenario)

1. Create a ReplicatedMergeTree **source** with wider / native types.
2. Create twin **Iceberg** destinations with the same casted schema.
3. Seed the source partition.
4. **Benchmark:** ``INSERT INTO dest_insert SELECT * FROM source``.
5. **Under test:** ``EXPORT PARTITION`` into ``dest_export``.
6. **Data correctness:** byte-compare ``dest_insert`` vs ``dest_export``.
7. **Metadata correctness:** current snapshot ``total-records`` and partition
   spec source columns match the destination layout.

## Scenario groups

* ``safe`` — one scenario per ``canBeSafelyCast`` family that maps to Iceberg
  DDL (integer widening, float widening, ``* -> String``, nullable/array/map/tuple
  recursion).
* ``lossy`` — narrowing casts rejected by default, accepted with
  ``export_merge_tree_part_allow_lossy_cast``.
* ``cisco`` — full DNS schema from ``schema_sample.sql``: production MergeTree
  types on the source, Iceberg-native cast targets on the destination.

Module registration in ``feature.py`` stays commented out until PR 1779 merges.
"""

from testflows.core import *

from iceberg.requirements.export_partition import (
    RQ_Iceberg_ExportPartition_Casting_SafeCasts,
    RQ_Iceberg_ExportPartition_Casting_LossyCasts,
)

from helpers.common import getuid

from iceberg.tests.export_partition.steps.casting import (
    LOSSY_CAST_CASES,
    SAFE_CAST_CASES,
    assert_destinations_match,
    insert_select_into_iceberg_destination,
    run_cast_parity_case,
)
from iceberg.tests.export_partition.steps.cisco_schema import (
    CISCO_DEST_COLUMNS,
    CISCO_EXPORT_SETTINGS,
    CISCO_INSERT_SELECT,
    CISCO_PARTITION_BY,
    CISCO_SOURCE_COLUMNS,
    CISCO_WHERE,
)
from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    resolve_first_partition_id,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_partition as export_partition_step,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    assert_manifest_spec_matches_partition,
    assert_snapshot_row_count,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
)


def _safe_cast_scenario(case):
    @TestScenario
    @Requirements(RQ_Iceberg_ExportPartition_Casting_SafeCasts("1.0"))
    @Name(case.name)
    def scenario(self, minio_root_user, minio_root_password):
        run_cast_parity_case(
            case=case,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    scenario.__name__ = "safe_cast_" + "".join(
        c.lower() if c.isalnum() else "_" for c in case.name
    )
    return scenario


def _lossy_cast_scenario(case):
    @TestScenario
    @Requirements(RQ_Iceberg_ExportPartition_Casting_LossyCasts("1.0"))
    @Name(case.name)
    def scenario(self, minio_root_user, minio_root_password):
        run_cast_parity_case(
            case=case,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    scenario.__name__ = "lossy_cast_" + "".join(
        c.lower() if c.isalnum() else "_" for c in case.name
    )
    return scenario


SAFE_SCENARIOS = tuple(_safe_cast_scenario(case) for case in SAFE_CAST_CASES)
LOSSY_SCENARIOS = tuple(_lossy_cast_scenario(case) for case in LOSSY_CAST_CASES)


@TestScenario
@Requirements(RQ_Iceberg_ExportPartition_Casting_SafeCasts("1.0"))
@Name("cisco schema casts to Iceberg destination")
def cisco_schema(self, minio_root_user, minio_root_password):
    """DNS-shaped production schema with casted Iceberg destination.

    Source columns match ``schema_sample.sql`` MergeTree types; destination
    columns use Iceberg-legal equivalents (``LowCardinality``/``Enum8``/``UInt8``
    -> ``String``/``Int32``, etc.). Several mappings are lossy, so export runs
    with ``export_merge_tree_part_allow_lossy_cast = 1``. Parity is checked
    against ``INSERT INTO dest SELECT * FROM source``, not Hybrid/S3 cold storage.
    """
    node = self.context.node
    source_table = f"cisco_src_{getuid()}"
    expected_rows = 3

    with Given("ReplicatedMergeTree source with Cisco production types"):
        create_replicated_mergetree(
            table_name=source_table,
            columns=CISCO_SOURCE_COLUMNS,
            partition_by=CISCO_PARTITION_BY,
            order_by="(mspOrganizationId, qname, timestamp)",
            node=node,
        )

    with And("seed the cold-tier partition"):
        node.query(f"INSERT INTO {source_table} {CISCO_INSERT_SELECT}")

    with And("Iceberg destination for INSERT SELECT benchmark"):
        dest_insert = create_iceberg_destination(
            columns=CISCO_DEST_COLUMNS,
            partition_by=CISCO_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node,
        )

    with And("twin Iceberg destination for EXPORT PARTITION"):
        dest_export = create_iceberg_destination(
            columns=CISCO_DEST_COLUMNS,
            partition_by=CISCO_PARTITION_BY,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            node=node,
        )

    with When("INSERT INTO benchmark destination SELECT * FROM source"):
        insert_select_into_iceberg_destination(
            destination=dest_insert,
            select_query=f"SELECT * FROM {source_table} WHERE {CISCO_WHERE}",
            node=node,
        )

    partition_id = resolve_first_partition_id(table_name=source_table, node=node)

    with And("EXPORT PARTITION into the twin destination"):
        export_partition_step(
            source_table=source_table,
            destination=dest_export,
            partition_id=partition_id,
            settings=CISCO_EXPORT_SETTINGS,
            node=node,
        )

    with Then("row counts match for the exported partition"):
        assert_destination_row_count(
            destination=dest_insert,
            expected=expected_rows,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            where_clause=CISCO_WHERE,
            node=node,
        )
        assert_destination_row_count(
            destination=dest_export,
            expected=expected_rows,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            where_clause=CISCO_WHERE,
            node=node,
        )

    with And("EXPORT matches the INSERT SELECT benchmark"):
        assert_destinations_match(
            left_destination=dest_insert,
            right_destination=dest_export,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            where_clause=CISCO_WHERE,
            order_by="timestamp",
            node=node,
        )

    with And("snapshot metadata reflects the casted export"):
        assert_snapshot_row_count(
            destination=dest_export,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected=expected_rows,
        )
        assert_manifest_spec_matches_partition(
            destination=dest_export,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_source_columns=["eventDate", "retention"],
        )


SCENARIOS = SAFE_SCENARIOS + LOSSY_SCENARIOS + (cisco_schema,)


@TestFeature
@Name("casting")
def feature(self, minio_root_user, minio_root_password):
    """EXPORT PARTITION casting parity vs INSERT SELECT (PR 1779)."""
    with Feature("safe"):
        for scenario in SAFE_SCENARIOS:
            Scenario(test=scenario, flags=TE)(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
    with Feature("lossy"):
        for scenario in LOSSY_SCENARIOS:
            Scenario(test=scenario, flags=TE)(
                minio_root_user=minio_root_user,
                minio_root_password=minio_root_password,
            )
    with Feature("cisco"):
        Scenario(test=cisco_schema, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
