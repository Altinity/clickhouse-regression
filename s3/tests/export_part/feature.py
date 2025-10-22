from testflows.core import *


@TestFeature
@Name("export parts")
def minio(self, uri, bucket_prefix):
    """Run features from the export parts suite."""

    self.context.uri_base = uri
    self.context.bucket_prefix = bucket_prefix

    self.context.node_1 = self.context.cluster.node("clickhouse1")
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node_1, self.context.node_2, self.context.node_3]

    Feature(run=load("s3.tests.export_part.sanity", "feature"))
    Feature(run=load("s3.tests.export_part.error_handling", "feature"))
    Feature(run=load("s3.tests.export_part.system_monitoring", "feature"))
    Feature(run=load("s3.tests.export_part.clusters", "feature"))
