"""Partition spec behaviour across sequential EXPORT PARTITION calls.

ClickHouse's Iceberg ``ALTER`` path (``IcebergMetadata::checkAlterIsPossible``)
only accepts ``ADD_COLUMN`` / ``DROP_COLUMN`` / ``MODIFY_COLUMN`` today, so
partition-spec *evolution* cannot be triggered through ClickHouse DDL. That
leaves two testable properties for this module:

* Multiple sequential exports of **different** partitions under the same
  ``PARTITION BY`` must all land in a single Iceberg partition spec
  (``table.specs()`` stays size-1, ``default-spec-id`` never advances).
* Per-partition manifest entries must tag each data file with the correct
  partition-tuple values, so Iceberg readers can prune by partition.

When ClickHouse learns to emit ``ALTER TABLE ... UPDATE SPEC ...`` this
module should grow a third class of scenarios: exporting under spec v1,
evolving the spec, exporting again under spec v2, and verifying both
snapshots remain individually readable.
"""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.export_partition import RQ_Iceberg_ExportPartition_PartitionSpecEvolution

from helpers.common import getuid

from iceberg.tests.export_partition.steps.common import (
    create_replicated_mergetree,
    get_partition_ids,
    insert_data,
)
from iceberg.tests.export_partition.steps.export_operations import (
    export_all_partitions,
    export_partition,
)
from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_iceberg_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    get_data_files,
    load_pyiceberg_table,
)
from iceberg.tests.export_partition.steps.verification import (
    assert_destination_row_count,
)


# ClickHouse defaults to writing bucket-relative paths into the Iceberg
# manifest-list ``manifest_path`` and snapshot ``manifest-list`` entries.
# PyIceberg's StaticTable (no-catalog mode) then interprets those as local
# paths and fails when the scenario tries to open them. Scenarios that
# inspect manifest contents must flip ``write_full_path_in_iceberg_metadata``
# on for both the ``CREATE TABLE`` (so the initial ``metadata.json``'s
# ``location`` holds an ``s3://`` URI) and the ``EXPORT PARTITION``
# (so every new snapshot's ``manifest-list`` location is absolute).
FULL_PATHS_SETTING = [("write_full_path_in_iceberg_metadata", 1)]


@TestScenario
@Name("single spec for multiple partition exports")
def single_spec_for_multiple_partitions(
    self, minio_root_user, minio_root_password
):
    """Export three distinct partitions one by one and verify the Iceberg
    destination still advertises exactly one partition spec.

    ``table.specs()`` is a ``Dict[int, PartitionSpec]``; ClickHouse should
    keep writing under ``default-spec-id = 0`` for every export.
    """
    source_table = f"mt_{getuid()}"
    columns = "id Int64, year Int32"
    partition_by = "year"

    with Given("create source with three partitions"):
        create_replicated_mergetree(
            table_name=source_table, columns=columns, partition_by=partition_by
        )
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2021), (3, 2022)",
        )

    with And("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=columns,
            partition_by=partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            query_settings=FULL_PATHS_SETTING,
        )

    with When("export every partition"):
        export_all_partitions(
            source_table=source_table,
            destination=destination,
            extra_settings=FULL_PATHS_SETTING,
        )

    with Then("all source rows landed in the destination"):
        assert_destination_row_count(
            destination=destination,
            expected=3,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )

    with And("iceberg metadata still advertises a single partition spec"):
        table = load_pyiceberg_table(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        specs = table.specs()
        assert len(specs) == 1, error(
            f"Expected exactly one partition spec after three exports, "
            f"got {len(specs)}: {specs!r}"
        )
        assert table.metadata.default_spec_id == 0, error(
            f"Expected default-spec-id = 0 after three exports, "
            f"got {table.metadata.default_spec_id}"
        )


@TestScenario
@Name("partition tuple matches partition_id across exports")
def partition_tuple_matches_partition_id(
    self, minio_root_user, minio_root_password
):
    """For every partition we export, the manifest entry's partition tuple
    must carry the same scalar value we used as ``partition_id``.

    This is the basic Iceberg-readable promise: metadata pruning by
    partition value can only work if the writer populated the partition
    struct correctly.
    """
    source_table = f"mt_{getuid()}"
    columns = "id Int64, year Int32"
    partition_by = "year"

    with Given("create source with three partitions"):
        create_replicated_mergetree(
            table_name=source_table, columns=columns, partition_by=partition_by
        )
        insert_data(
            table_name=source_table,
            values="(1, 2020), (2, 2021), (3, 2022)",
        )

    with And("create the Iceberg destination"):
        destination = create_iceberg_destination(
            columns=columns,
            partition_by=partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            query_settings=FULL_PATHS_SETTING,
        )

    with When("list the source's partition IDs"):
        partition_ids = get_partition_ids(table_name=source_table)

    with And("export every partition and remember the partition IDs"):
        exported = []
        for pid in partition_ids:
            export_partition(
                source_table=source_table,
                destination=destination,
                partition_id=pid,
                extra_settings=FULL_PATHS_SETTING,
            )
            exported.append(pid)

    with Then("every manifest entry's partition value matches an exported partition_id"):
        data_files = get_data_files(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert data_files, error("no data files found in destination manifests")
        observed = set()
        for df in data_files:
            partition = df.partition
            if partition is None:
                observed.add(None)
                continue
            # PyIceberg's data_file.partition is a Record; iterate its
            # positional values. With a single identity(year) partition
            # field we expect a one-element tuple.
            values = [v for v in partition]
            assert len(values) == 1, error(
                f"expected single-field partition tuple, got {values!r}"
            )
            observed.add(str(values[0]))
        assert observed == set(exported), error(
            f"manifest partition values {observed!r} != exported IDs {set(exported)!r}"
        )


@TestScenario
@Name("multi-column partition spec is preserved")
def multi_column_partition_spec_preserved(
    self, minio_root_user, minio_root_password
):
    """Source partitioned by ``(year, region)`` — the resulting Iceberg
    partition spec must carry both identity fields (in order) and exports
    must populate both positions of the partition tuple.
    """
    source_table = f"mt_{getuid()}"
    columns = "id Int64, year Int32, region String"
    partition_by = "(year, region)"

    with Given("create source partitioned by (year, region)"):
        create_replicated_mergetree(
            table_name=source_table, columns=columns, partition_by=partition_by
        )
        insert_data(
            table_name=source_table,
            values="(1, 2020, 'EU'), (2, 2020, 'US'), (3, 2021, 'EU')",
        )

    with And("create the Iceberg destination with the same spec"):
        destination = create_iceberg_destination(
            columns=columns,
            partition_by=partition_by,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            query_settings=FULL_PATHS_SETTING,
        )

    with When("export every partition"):
        export_all_partitions(
            source_table=source_table,
            destination=destination,
            extra_settings=FULL_PATHS_SETTING,
        )

    with Then("iceberg spec has two identity fields in the declared order"):
        table = load_pyiceberg_table(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        spec = table.spec()
        assert len(spec.fields) == 2, error(
            f"Expected 2 partition fields, got {len(spec.fields)}: {spec!r}"
        )
        field_names = [field.name for field in spec.fields]
        transforms = [str(field.transform) for field in spec.fields]
        assert field_names == ["year", "region"], error(
            f"Partition field order wrong: {field_names}"
        )
        assert all("identity" in t for t in transforms), error(
            f"Expected identity transforms, got {transforms}"
        )

    with And("every data file carries a two-value partition tuple"):
        data_files = get_data_files(
            destination=destination,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        assert data_files, error("no data files found")
        for df in data_files:
            values = list(df.partition)
            assert len(values) == 2, error(
                f"expected 2 partition values per file, got {values!r}"
            )


SCENARIOS = (
    single_spec_for_multiple_partitions,
    partition_tuple_matches_partition_id,
    multi_column_partition_spec_preserved,
)


@TestFeature
@Requirements(RQ_Iceberg_ExportPartition_PartitionSpecEvolution("1.0"))
@Name("partition spec evolution")
def feature(self, minio_root_user, minio_root_password):
    """Partition spec behaviour across sequential exports.

    ClickHouse cannot evolve the Iceberg partition spec through DDL today
    (see ``IcebergMetadata::checkAlterIsPossible``), so this module
    verifies that the spec stays consistent across every export and that
    per-partition tuples are preserved; true spec-evolution coverage is
    TODO until the ClickHouse side gains ``UPDATE SPEC`` support.
    """
    for scenario in SCENARIOS:
        Scenario(test=scenario, flags=TE)(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
