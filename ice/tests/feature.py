from testflows.core import *


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Run Ice tests."""
    Feature(
        test=load("ice.tests.ice_export_sanity", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
