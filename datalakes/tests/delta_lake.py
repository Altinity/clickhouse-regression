from testflows.core import *

from data_lakes.tests.common import (
    create_and_upload_delta_table,
    download_and_print_delta_table_from_s3,
)


@TestScenario
def upload_and_download_delta_table(self):
    """Uploads a Delta Lake table to S3 and downloads it back."""
    s3_bucket = self.context.bucket_name
    s3_key_prefix = "data"

    with Given("I create and upload a Delta Lake table to S3"):
        create_and_upload_delta_table(s3_bucket=s3_bucket, s3_key_prefix=s3_key_prefix)

    with Then("I download and print the Delta Lake table from S3"):
        download_and_print_delta_table_from_s3(s3_bucket=s3_bucket, s3_key_prefix=s3_key_prefix)


@TestFeature
def feature(self):
    s3_bucket = self.context.bucket_name
    s3_key_prefix = "data"

    with Given("I create and upload a Delta Lake table to S3"):
        create_and_upload_delta_table(s3_bucket=s3_bucket, s3_key_prefix=s3_key_prefix)

    with Then("I download and print the Delta Lake table from S3"):
        download_and_print_delta_table_from_s3(s3_bucket=s3_bucket, s3_key_prefix=s3_key_prefix)
