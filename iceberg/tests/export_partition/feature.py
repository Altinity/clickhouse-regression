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
    "system_monitoring",
    "settings",
    # Post-EXPORT interactions with the Iceberg destination (direct
    # INSERT / TRUNCATE / min-max reader round-trip) — these exercise
    # the same IcebergWrites.cpp / IcebergMetadata.cpp write paths as
    # EXPORT PARTITION so parity across the three catalog modes
    # matters here as much as in the original suite.
    "direct_writes",
    "truncate",
    "minmax_pruning",
    # Backward-compat: ReplicatedMergeTree tables that predate the
    # EXPORT feature and therefore do not have the /exports znode.
    # no_catalog-only (the invariant is on the source RMT, not on
    # any particular destination catalog).
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
@Name("export partition")
def feature(self, minio_root_user, minio_root_password):
    """Run export-partition tests across every supported catalog mode."""
    for mode in CATALOG_MODES:
        with Feature(f"{mode} catalog"):
            self.context.catalog = mode
            _load_modules(self, minio_root_user, minio_root_password)
