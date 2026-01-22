from testflows.core import *
from s3.requirements.export_part import *


@TestFeature
@Specifications(
    SRS_015_ClickHouse_Export_Part_to_S3,
)
@Requirements(
    RQ_ClickHouse_ExportPart_S3("1.0"),
)
@Name("export part")
def minio(self, uri, bucket_prefix):
    """Run features from the export parts suite."""

    self.context.uri_base = uri
    self.context.bucket_prefix = bucket_prefix
    self.context.default_settings = [("allow_experimental_export_merge_tree_part", 1)]

    Feature(run=load("s3.tests.export_part.sanity", "feature"))
    Feature(run=load("s3.tests.export_part.error_handling", "feature"))
    Feature(run=load("s3.tests.export_part.clusters_nodes", "feature"))
    Feature(run=load("s3.tests.export_part.shards", "feature"))
    Feature(run=load("s3.tests.export_part.engines_volumes", "feature"))
    Feature(run=load("s3.tests.export_part.datatypes", "feature"))
    # Feature(run=load("s3.tests.export_part.columns", "feature"))
    Feature(run=load("s3.tests.export_part.network", "feature"))
    Feature(run=load("s3.tests.export_part.system_monitoring", "feature"))
    Feature(run=load("s3.tests.export_part.concurrent_alter", "feature"))
    Feature(run=load("s3.tests.export_part.concurrent_other", "feature"))
    Feature(
        run=load("s3.tests.export_part.pending_mutations_and_patch_parts", "feature")
    )
    Feature(run=load("s3.tests.export_part.rbac", "feature"))
