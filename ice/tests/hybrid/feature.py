from testflows.core import *


@TestFeature
@Name("hybrid")
def feature(self, minio_root_user, minio_root_password):
    """Test hybrid table engine."""
    Feature(test=load("ice.tests.hybrid.hybrid_dropped_segment_repro", "feature"))()
    Feature(test=load("ice.tests.hybrid.hybrid_alias.feature", "feature"))(
        minio_root_user=minio_root_user, minio_root_password=minio_root_password
    )
    # Feature(test=load("ice.tests.hybrid.hybrid_query_fuzzing", "feature"))(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Feature(test=load("ice.tests.hybrid.alias_combinatorics", "feature"))(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Feature(test=load("ice.tests.hybrid.alias_test_runner", "feature"))(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
    # Feature(test=load("ice.tests.hybrid.hybrid_alias.feature", "feature"))(
    #     minio_root_user=minio_root_user, minio_root_password=minio_root_password
    # )
