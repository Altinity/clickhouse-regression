from testflows.core import *


# TODO large data export? which file should it go in?


@TestFeature
@Name("export parts")
def minio(self, uri, bucket_prefix):
    """Run features from the export parts suite."""

    self.context.uri_base = uri
    self.context.bucket_prefix = bucket_prefix

    Feature(run=load("s3.tests.export_part.sanity", "feature"))
    Feature(run=load("s3.tests.export_part.error_handling", "feature"))
    # Feature(run=load("s3.tests.export_part.system_monitoring", "feature"))
    # Feature(run=load("s3.tests.export_part.clusters_and_nodes", "feature"))
    # Feature(run=load("s3.tests.export_part.engines", "feature"))
    # Feature(run=load("s3.tests.export_part.datatypes", "feature"))
    # Feature(run=load("s3.tests.export_part.concurrency", "feature"))
