"""TTL ... EXPORT TO TABLE (Altinity/ClickHouse#2442).

The scenarios are skipped from ``iceberg/regression.py`` until that change
is in a release. Delete the ``/iceberg/export ttl`` entry in ``ffails`` to
run them against the PR. Released builds keep the existing export-partition
suite, which still checks ``system.replicated_partition_exports`` and
``system.partition_exports``.
"""

from testflows.core import *

from helpers.config import config_d, users_d


MODULES = (
    "backfill",
    "partition_and_ttl",
    "merges",
    "crashes",
    "manual_export",
    "object_storage",
)


@TestFeature
@Name("export ttl")
def feature(self, minio_root_user, minio_root_password):
    """Background export of due MergeTree parts to Iceberg."""
    self.context.catalog = "no"
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password

    with Given("enable export and Iceberg writes for background TTL tasks"):
        users_d.create_and_add(
            entries={
                "profiles": {
                    "default": {
                        "allow_experimental_insert_into_iceberg": "1",
                        "allow_experimental_export_merge_tree_part": "1",
                    }
                }
            },
            config_file="allow_experimental_export_ttl.xml",
            node=self.context.nodes[0],
            modify=True,
            restart=False,
        )
        config_d.enable_export_partition()

    for module in MODULES:
        Feature(
            test=load(f"iceberg.tests.export_ttl.{module}", "feature"),
        )(
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
        )
