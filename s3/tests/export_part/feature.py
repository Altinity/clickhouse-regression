from testflows.core import *


@TestFeature
@Name("export parts")
def minio(self, uri, bucket_prefix):
    """Run features from the export parts suite."""

    self.context.uri_base = uri
    self.context.bucket_prefix = bucket_prefix
    self.context.default_columns = [
        {"name": "p", "type": "Int8"},
        {"name": "i", "type": "UInt64"},
    ]

    Feature(run=load("s3.tests.export_part.sanity", "feature"))
    # Feature(run=load("s3.tests.export_part.error_handling", "feature"))
    # Feature(run=load("s3.tests.export_part.system_monitoring", "feature"))
    Feature(run=load("s3.tests.export_part.clusters_and_nodes", "feature"))