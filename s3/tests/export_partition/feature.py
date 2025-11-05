from testflows.core import *


@TestFeature
@Specifications()
@Requirements()
@Name("export partition")
def minio(self, uri, bucket_prefix):
    """Export partition suite."""

    self.context.uri_base = uri
    self.context.bucket_prefix = bucket_prefix

    Feature(run=load("s3.tests.export_partition.sanity", "feature"))
    # Feature(run=load("s3.tests.export_part.error_handling", "feature"))
    # Feature(run=load("s3.tests.export_part.clusters_nodes", "feature"))
    # Feature(run=load("s3.tests.export_part.engines_volumes", "feature"))
    # Feature(run=load("s3.tests.export_part.datatypes", "feature"))
    # Feature(run=load("s3.tests.export_part.concurrency_networks", "feature"))
    # Feature(run=load("s3.tests.export_part.system_monitoring", "feature"))
