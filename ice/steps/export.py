from testflows.core import *

from iceberg.tests.steps.catalog import clean_minio_bucket


@TestStep(Given)
def export_partitions_to_s3(
    self,
    merge_tree_table_name,
    s3_table_name,
    partition_ids,
    minio_root_user,
    minio_root_password,
    node=None,
    s3_endpoint="http://localhost:9002",
    allow_experimental_export_merge_tree_partition=1,
    export_merge_tree_partition_background_execution=0,
):
    """Export partitions to s3."""
    if node is None:
        node = self.context.node

    settings = {}

    if allow_experimental_export_merge_tree_partition:
        settings["allow_experimental_export_merge_tree_part"] = (
            allow_experimental_export_merge_tree_partition
        )
    if export_merge_tree_partition_background_execution:
        settings["export_merge_tree_partition_background_execution"] = (
            export_merge_tree_partition_background_execution
        )

    if settings:
        settings_str = ",".join(
            [f"{key} = '{value}'" for key, value in settings.items()]
        )

    try:
        for partition_id in partition_ids:
            node.query(
                f"""
                    ALTER TABLE {merge_tree_table_name} 
                    EXPORT PARTITION ID '{partition_id}' 
                    TO TABLE {s3_table_name} 
                    SETTINGS 
                        {settings_str}
                """
            )

        yield

    finally:
        with Finally("clean the s3 bucket"):
            clean_minio_bucket(
                bucket_name="warehouse",
                s3_endpoint=s3_endpoint,
                s3_access_key_id=minio_root_user,
                s3_secret_access_key=minio_root_password,
            )
