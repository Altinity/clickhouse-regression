from testflows.core import *


@TestFeature
@Name("schema")
def feature(self, minio_root_user, minio_root_password):
    """Schema variety (PR scale), operational drills, PyIceberg interop.

    Large soak (100M+) remains a nightly/optional job — not enabled here.
    """
    Feature(test=load("iceberg.tests.hybrid.schema.variety", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Feature(test=load("iceberg.tests.hybrid.schema.operational", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Feature(test=load("iceberg.tests.hybrid.schema.external_reader", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
