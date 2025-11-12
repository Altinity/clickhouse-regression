from testflows.core import *
from s3.requirements.export_partition import *


@TestFeature
@Specifications(SRS_016_ClickHouse_Export_Partition_to_S3)
@Requirements()
@Name("export partition")
def minio(self, uri, bucket_prefix):
    """Export partition suite."""

    self.context.uri_base = uri
    self.context.bucket_prefix = bucket_prefix
    self.context.default_settings = [("allow_experimental_export_merge_tree_part", 1)]

    Feature(run=load("s3.tests.export_partition.sanity", "feature"))
    Feature(run=load("s3.tests.export_partition.error_handling", "feature"))
    Feature(run=load("s3.tests.export_partition.clusters_nodes", "feature"))
    Feature(run=load("s3.tests.export_partition.engines_volumes", "feature"))
    Feature(run=load("s3.tests.export_partition.datatypes", "feature"))
    Feature(run=load("s3.tests.export_partition.concurrency_networks", "feature"))
    Feature(run=load("s3.tests.export_partition.concurrent_actions", "feature"))
    Feature(run=load("s3.tests.export_partition.system_monitoring", "feature"))
