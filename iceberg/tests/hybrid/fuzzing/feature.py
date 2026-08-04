from testflows.core import *


@TestFeature
@Name("fuzzing")
def feature(self, minio_root_user, minio_root_password):
    """Hybrid query fuzzing: curated SQL + upstream-derived shapes."""
    self.context.catalog = "rest"

    Feature(test=load("iceberg.tests.hybrid.fuzzing.hybrid_queries", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
    Feature(test=load("iceberg.tests.hybrid.fuzzing.upstream_queries", "feature"))(
        minio_root_user=minio_root_user,
        minio_root_password=minio_root_password,
    )
