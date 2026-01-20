from testflows.core import *
from s3.requirements.export_partition import *
from s3.tests.common import enable_export_partition


@TestFeature
@Specifications(SRS_016_ClickHouse_Export_Partition_to_S3)
@Requirements()
@Name("export partition")
def minio(self, uri, bucket_prefix):
    """Export partition suite."""

    self.context.uri_base = uri
    self.context.bucket_prefix = bucket_prefix
    self.context.default_settings = [("allow_experimental_export_merge_tree_part", "1")]

    with Given("I enable export partition"):
        enable_export_partition()

    Feature(run=load("s3.tests.export_partition.sanity", "feature"))
    # Feature(run=load("s3.tests.export_partition.error_handling", "feature"))
    # Feature(run=load("s3.tests.export_partition.kill", "feature"))
    # Feature(run=load("s3.tests.export_partition.clusters_nodes", "feature"))
    # Feature(run=load("s3.tests.export_partition.engines_volumes", "feature"))
    # Feature(run=load("s3.tests.export_partition.datatypes", "feature"))
    # Feature(run=load("s3.tests.export_partition.network", "feature"))
    # Feature(run=load("s3.tests.export_partition.concurrent_actions", "feature"))
    # Feature(run=load("s3.tests.export_partition.system_monitoring", "feature"))
    # Feature(run=load("s3.tests.export_partition.schema_evolution", "feature"))
    Feature(run=load("s3.tests.export_partition.parallel_export_partition", "feature"))
    # Feature(
    # run=load("s3.tests.export_partition.alter_destination_during_export", "feature")
    # )
    # Feature(run=load("s3.tests.export_partition.alter_source_timing", "feature"))
    # Feature(run=load("s3.tests.export_partition.replica_failover", "feature"))
    # Feature(run=load("s3.tests.export_partition.versions", "feature"))
    # Feature(
    # run=load("s3.tests.export_partition.parallel_inserts_and_selects", "feature")
    # )
