import os
import boto3
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

from testflows.core import *


@TestStep(Given)
def create_and_upload_delta_table(
    self,
    s3_bucket,
    s3_key_prefix,
    delta_table_path="/tmp/delta_table",
    local_save_path="/tmp/delta_table_to_parquet",
):
    """
    Creates a Delta Lake table with example data, saves it as Parquet, and uploads it to an S3 bucket.

    Args:
        s3_bucket (str): The name of the S3 bucket.
        s3_key_prefix (str): The S3 folder path where files will be uploaded.
        delta_table_path (str): The local path where the Delta Lake table will be stored. Default is '/tmp/delta_table'.
        local_save_path (str): The local directory where the Delta table will be saved in Parquet format. Default is '/tmp/delta_table_to_parquet'.
    """
    try:
        with By("Initialize Spark session with Delta Lake support"):
            builder = (
                SparkSession.builder.appName("DeltaLakeToS3")
                .config(
                    "spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension"
                )
                .config(
                    "spark.sql.catalog.spark_catalog",
                    "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                )
            )

            spark = configure_spark_with_delta_pip(builder).getOrCreate()

        with By("Create a Delta Lake table with some example data"):
            data = [(1, "Alice", 25), (2, "Bob", 30), (3, "Charlie", 35)]
            columns = ["id", "name", "age"]

            df = spark.createDataFrame(data, columns)

        with By("Save the DataFrame as a Delta table"):
            df.write.format("delta").mode("overwrite").save(delta_table_path)

        with By("Read the Delta table and convert it to Parquet format"):
            delta_df = spark.read.format("delta").load(delta_table_path)
            delta_df.write.mode("overwrite").parquet(local_save_path)

        with By("Upload the Parquet files to S3"):
            s3_client = boto3.client("s3")
            for root, dirs, files in os.walk(local_save_path):
                for file in files:
                    if file.endswith(".parquet"):
                        local_file_path = os.path.join(root, file)
                        s3_key = os.path.join(s3_key_prefix, file)

                        # Upload the file to S3
                        s3_client.upload_file(local_file_path, s3_bucket, s3_key)
                        print(f"Uploaded {file} to s3://{s3_bucket}/{s3_key}")

    finally:
        with Finally("Stop the Spark session"):
            spark.stop()


@TestStep(Given)
def download_and_print_delta_table_from_s3(
    self, s3_bucket, s3_key_prefix, local_download_path="/tmp/delta_table_from_s3"
):
    """
    Downloads the Delta Lake table (stored as Parquet files) from an S3 bucket and prints the contents.

    Args:
        s3_bucket (str): The name of the S3 bucket.
        s3_key_prefix (str): The S3 folder path where the Parquet files are stored.
        local_download_path (str): The local directory where the Parquet files will be downloaded. Default is '/tmp/delta_table_from_s3'.
    """

    s3_client = boto3.client("s3")

    if not os.path.exists(local_download_path):
        os.makedirs(local_download_path)

    try:

        with By("Download the Parquet files from S3"):
            paginator = s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=s3_bucket, Prefix=s3_key_prefix)

            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        file_key = obj["Key"]
                        if file_key.endswith(".parquet"):
                            local_file_path = os.path.join(
                                local_download_path, os.path.basename(file_key)
                            )
                            s3_client.download_file(
                                s3_bucket, file_key, local_file_path
                            )
                            note(f"Downloaded {file_key} to {local_file_path}")

        with By("Initialize Spark session with Delta Lake support"):
            builder = (
                SparkSession.builder.appName("DeltaLakeReadFromS3")
                .config(
                    "spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension"
                )
                .config(
                    "spark.sql.catalog.spark_catalog",
                    "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                )
            )

            spark = configure_spark_with_delta_pip(builder).getOrCreate()

        with By("Read the Parquet files as a DataFrame"):
            df = spark.read.parquet(local_download_path)

        with By("Print the contents of the Delta Lake table from S3"):
            note("Contents of the Delta Lake table from S3:")
            df.show()

    finally:
        with Finally("Stop the Spark session"):
            spark.stop()
