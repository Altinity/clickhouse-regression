"""Entry point for the ``export_partition`` suite.

Each scenario module inside ``export_partition/`` is parameterised three ways
by running the same feature under three different catalog contexts:

* ``"no_catalog"`` - pure Iceberg writes via ``ENGINE = IcebergS3(...)``.
* ``"ice"``        - DataLakeCatalog backed by the Altinity ``ice-rest-catalog``
  service (an Iceberg REST Catalog Spec implementation).
* ``"glue"``       - Glue DataLakeCatalog (LocalStack).

Scenarios read ``self.context.catalog`` to choose the right helpers (see
``steps/iceberg_destination.py``) so individual tests stay mode-agnostic.

Some modules are only meaningful in a single mode (e.g. ``catalogs.py``
exercises catalog-specific commit paths). Those modules internally skip
scenarios that do not apply to the current ``self.context.catalog`` and are
therefore still loaded here for completeness.
"""

from testflows.core import *

from helpers.config import users_d

from iceberg.requirements.export_partition import (
    SRS_047_ClickHouse_EXPORT_PARTITION_to_Apache_Iceberg,
)


CATALOG_MODES = ("no", "ice", "glue")


MODULES = (
    "sanity",
    "partition_compatibility",
    "datatypes",
    "manifest_integrity",
    "catalogs",
    "transactions",
    "concurrent_writes",
    "schema_evolution",
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
    """Run export-partition tests across every supported catalog mode."""
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
            _load_modules(self, minio_root_user, minio_root_password)
