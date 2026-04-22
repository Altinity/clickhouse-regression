"""Entry point for the ``export_partition`` suite.

Each scenario module inside ``export_partition/`` is parameterised three ways
by running the same feature under three different catalog contexts:

* ``"no_catalog"`` - pure Iceberg writes via ``ENGINE = IcebergS3(...)``.
* ``"rest"``       - REST DataLakeCatalog (the ``ice-rest-catalog`` service).
* ``"glue"``       - Glue DataLakeCatalog (LocalStack).

Scenarios read ``self.context.catalog`` to choose the right helpers (see
``steps/iceberg_destination.py``) so individual tests stay mode-agnostic.

Some modules are only meaningful in a single mode (e.g. ``catalogs.py``
exercises catalog-specific commit paths). Those modules internally skip
scenarios that do not apply to the current ``self.context.catalog`` and are
therefore still loaded here for completeness.
"""

from testflows.core import *


CATALOG_MODES = ("no", "rest", "glue")


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
    "system_monitoring",
    "settings",
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
