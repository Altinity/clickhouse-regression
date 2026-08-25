"""Entry point for the ``export_partition`` suite.

Each scenario module is parameterised by **catalog** and **source engine**:

Catalog (``self.context.catalog``):

* ``"no"``   - pure Iceberg writes via ``ENGINE = IcebergS3(...)``.
* ``"ice"``  - DataLakeCatalog backed by the Altinity ``ice-rest-catalog``
  service (an Iceberg REST Catalog Spec implementation).
* ``"glue"`` - Glue DataLakeCatalog (LocalStack).

Source engine (``self.context.source_engine``):

* ``"replicated"`` - ``ReplicatedMergeTree`` (default; ZooKeeper-backed export
  coordination, ``system.replicated_partition_exports``).
* ``"plain"``      - ``MergeTree`` (Altinity/ClickHouse#2032;
  ``system.partition_exports``).

Scenarios read ``self.context.catalog`` for destination helpers (see
``steps/iceberg_destination.py``) and ``self.context.source_engine`` for
source DDL (see ``steps/common.create_export_source_table``).

Some modules are only meaningful in a single mode (e.g. ``catalogs.py``
exercises catalog-specific commit paths; ``zk_compat.py`` is replicated-only).
Those modules internally skip scenarios that do not apply.
"""

from testflows.core import *

from helpers.config import config_d, users_d
from helpers.common import check_if_antalya_build
from helpers.feature_support import validate_feature_support, setting_supported

from iceberg.requirements.export_partition import (
    SRS_047_ClickHouse_EXPORT_PARTITION_to_Apache_Iceberg,
)


CATALOG_MODES = ("no", "ice", "glue")
SOURCE_ENGINE_MODES = ("replicated", "plain")


MODULES = (
    "sanity",
    "partition_compatibility",
    "datatypes",
    "manifest_integrity",
    "catalogs",
    "transactions",
    "concurrent_writes",
    "schema_evolution",
    "schema_compatibility",  # Altinity/ClickHouse#2134 / #2111 matrix
    "partition_spec_evolution",
    "storage_paths",
    "disaster_recovery",
    "multi_replica_recovery",
    "replicas",
    "system_monitoring",
    "settings",
    "direct_writes",
    "truncate",
    "minmax_pruning",
    "zk_compat",
    "casting",  # Altinity/ClickHouse#1779 — catalog/version gating in regression.py
)


def _load_modules(self, minio_root_user, minio_root_password):
    for module in MODULES:
        Feature(
            test=load(f"iceberg.tests.export_partition.{module}", "feature"),
            flags=TE,
        )(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )


@TestFeature
@Specifications(SRS_047_ClickHouse_EXPORT_PARTITION_to_Apache_Iceberg)
@Name("export partition")
def feature(self, minio_root_user, minio_root_password):
    """Run export-partition tests across every catalog and source-engine mode."""
    if check_if_antalya_build(self) and not validate_feature_support(
        self,
        feature="Export merge tree partition",
        check=setting_supported("export_merge_tree_partition_force_export"),
    ):
        return

    config_d.enable_export_partition()

    with Given(
        "enable export-partition Iceberg and EXPORT PART gates in the default profile"
    ):
        for node in self.context.nodes:
            users_d.create_and_add(
                entries={
                    "profiles": {
                        "default": {
                            "allow_experimental_insert_into_iceberg": "1",
                            "allow_experimental_export_merge_tree_part": "1",
                            "allow_experimental_hybrid_table": "1",
                        }
                    }
                },
                config_file="allow_experimental_insert_into_iceberg.xml",
                node=node,
                modify=True,
            )

    for mode in CATALOG_MODES:
        with Feature(f"{mode} catalog"):
            self.context.catalog = mode
            for engine in SOURCE_ENGINE_MODES:
                with Feature(f"{engine} merge tree"):
                    self.context.source_engine = engine
                    _load_modules(self, minio_root_user, minio_root_password)
