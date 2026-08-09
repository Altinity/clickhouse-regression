from testflows.core import *


@TestFeature
@Name("lifecycle")
def feature(self, minio_root_user, minio_root_password):
    """Operational Hybrid lifecycle: EXPORT → watermark, Distributed replace."""
    Feature(
        test=load("iceberg.tests.hybrid.lifecycle.export_then_watermark", "feature")
    )(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Feature(
        test=load("iceberg.tests.hybrid.lifecycle.replace_distributed_head", "feature")
    )(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
