from testflows.core import *


@TestFeature
def feature(self, minio_root_user, minio_root_password):
    """Check swarm cluster functionality."""
    self.context.catalog = "rest"
    Feature(
        test=load("swarms.tests.joins", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("swarms.tests.swarm_sanity", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("swarms.tests.invalid_configuration", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("swarms.tests.cluster_discovery", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    Feature(
        test=load("swarms.tests.node_failure", "feature"),
    )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    # Feature(
    #     test=load("swarms.tests.joins_sanity", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    # Feature(
    #     test=load("swarms.tests.swarm_iceberg_partition_pruning", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    # Feature(
    #     test=load("swarms.tests.performance", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
    # Feature(
    #     test=load("swarms.tests.schema_evolution", "feature"),
    # )(minio_root_user=minio_root_user, minio_root_password=minio_root_password)
