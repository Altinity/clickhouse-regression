"""External PyIceberg read of Hybrid cold tier after EXPORT PARTITION.

ClickHouse EXPORT PARTITION writes Parquet without Iceberg field-ids
(https://github.com/Altinity/ClickHouse/issues/2161). Strict readers
(PyIceberg) require either field-ids in the files or table property
``schema.name-mapping.default``. This scenario creates the cold destination
through PyIceberg with that name mapping so the Hybrid EXPORT path is
externally readable — matching the datalake pattern of a catalog-owned table
that ClickHouse exports into.
"""

from datetime import date

from testflows.core import *
from testflows.asserts import error

from pyiceberg.table.name_mapping import create_mapping_from_schema

from iceberg.requirements.hybrid import (
    RQ_ClickHouse_Hybrid_ExternalReader_Iceberg,
)

from iceberg.tests.export_partition.steps.iceberg_destination import (
    create_pyiceberg_catalog_destination,
)
from iceberg.tests.export_partition.steps.manifest_validation import (
    load_pyiceberg_table,
)
from iceberg.tests.export_partition.steps.pyiceberg_schema import (
    ch_columns_to_pyiceberg_schema,
    ch_partition_by_to_pyiceberg_spec,
)
from iceberg.tests.hybrid.core.common import (
    ALL_ROWS,
    COLUMNS_SQL,
    PREFER_LOCALHOST,
    RIGHT_PREDICATE,
    WATERMARK,
    settings_clause,
)
from iceberg.tests.hybrid.lifecycle.common import (
    EXPORT_PARTITION_BY,
    create_exportable_hot_segment,
    create_hybrid_remote_iceberg,
    export_partitions_matching,
)


@TestStep(Given)
def create_pyiceberg_cold_destination_with_name_mapping(
    self, minio_root_user, minio_root_password
):
    """Catalog-backed Iceberg table with name mapping for EXPORT Parquet."""
    schema, column_id_map = ch_columns_to_pyiceberg_schema(COLUMNS_SQL)
    partition_spec = ch_partition_by_to_pyiceberg_spec(
        EXPORT_PARTITION_BY, column_id_map
    )
    name_mapping = create_mapping_from_schema(schema)
    return create_pyiceberg_catalog_destination(
        schema=schema,
        partition_spec=partition_spec,
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
        table_properties={
            "schema.name-mapping.default": name_mapping.model_dump_json(),
        },
    )


@TestScenario
@Name("pyiceberg reads exported cold tier")
def pyiceberg_reads_exported_cold(self, minio_root_user, minio_root_password):
    """EXPORT cold partitions, then PyIceberg row count matches ClickHouse Iceberg."""
    # REST catalog so we can attach schema.name-mapping.default at CREATE.
    self.context.catalog = "ice"
    node = self.context.node
    clause = settings_clause(PREFER_LOCALHOST)

    with Given("exportable hot MT, catalog Iceberg with name mapping, Hybrid head"):
        hot = create_exportable_hot_segment()
        ice = create_pyiceberg_cold_destination_with_name_mapping(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        ctx = create_hybrid_remote_iceberg(hot_table=hot, iceberg_destination=ice)

    cold_n = sum(1 for _, _, d in ALL_ROWS if d < WATERMARK)

    with When("EXPORT cold partitions"):
        export_partitions_matching(
            source_table=hot,
            destination=ice,
            where=RIGHT_PREDICATE,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            expected_rows=cold_n,
        )

    with Then("ClickHouse Iceberg segment has the cold rows"):
        ch_count = int(
            node.query(
                f"SELECT count() FROM {ctx['right_from']} "
                f"WHERE {RIGHT_PREDICATE} {clause}"
            ).output.strip()
        )
        assert ch_count == cold_n, error()

    with And("PyIceberg scan sees the same cold-band row count"):
        table = load_pyiceberg_table(
            destination=ice,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
        arrow = table.scan().to_arrow()
        dates = arrow.column("date_col")
        wm = date.fromisoformat(WATERMARK)
        py_cold = sum(1 for d in dates.to_pylist() if d is not None and d < wm)
        assert py_cold == cold_n, error(
            f"PyIceberg cold count {py_cold} != expected {cold_n}"
        )

    with And("Hybrid full scan matches the full dataset"):
        hybrid_count = int(
            node.query(f"SELECT count() FROM {ctx['hybrid']} {clause}").output.strip()
        )
        assert hybrid_count == len(ALL_ROWS), error()


@TestFeature
@Requirements(
    RQ_ClickHouse_Hybrid_ExternalReader_Iceberg("1.0"),
)
@Name("external reader")
def feature(self, minio_root_user, minio_root_password):
    """PyIceberg interop on exported Hybrid cold tier."""
    Scenario(test=pyiceberg_reads_exported_cold)(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
