from testflows.core import *


@TestFeature
@Name("core")
def feature(self, minio_root_user, minio_root_password):
    """Hybrid engine core: queries, distributed paths, INSERT, watermarks, pruning, types."""
    Feature(test=load("iceberg.tests.hybrid.core.query_pack", "feature"))()
    Feature(test=load("iceberg.tests.hybrid.core.execution_paths", "feature"))()
    Feature(test=load("iceberg.tests.hybrid.core.insert_routing", "feature"))()
    Feature(test=load("iceberg.tests.hybrid.core.watermarks", "feature"))()
    Feature(test=load("iceberg.tests.hybrid.core.predicate_pruning", "feature"))()
    Feature(test=load("iceberg.tests.hybrid.core.type_autocast", "feature"))()
    Feature(test=load("iceberg.tests.hybrid.core.mergetree_iceberg", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Feature(test=load("iceberg.tests.hybrid.core.topology", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
