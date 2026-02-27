from testflows.core import *
import json
from helpers.common import getuid
from helpers.create import *
from s3.tests.common import temporary_bucket_path, s3_storage


@TestStep(Given)
def minio_storage_configuration(self, restart=True):
    """Create storage configuration with jbod disks, MinIO S3 disk, and tiered storage policy."""
    with Given(
        "I configure storage with jbod disks, MinIO S3 disk, and tiered storage"
    ):
        disks = {
            "jbod1": {"path": "/jbod1/"},
            "jbod2": {"path": "/jbod2/"},
            "jbod3": {"path": "/jbod3/"},
            "jbod4": {"path": "/jbod4/"},
            "external": {"path": "/external/"},
            "external2": {"path": "/external2/"},
            "minio": {
                "type": "s3",
                "endpoint": "http://minio1:9001/root/data/",
                "access_key_id": "minio_user",
                "secret_access_key": "minio123",
            },
            "s3_cache": {
                "type": "cache",
                "disk": "minio",
                "path": "minio_cache/",
                "max_size": "22548578304",
                "cache_on_write_operations": "1",
            },
        }

        policies = {
            "jbod1": {"volumes": {"main": {"disk": "jbod1"}}},
            "jbod2": {"volumes": {"main": {"disk": "jbod2"}}},
            "jbod3": {"volumes": {"main": {"disk": "jbod3"}}},
            "jbod4": {"volumes": {"main": {"disk": "jbod4"}}},
            "external": {"volumes": {"main": {"disk": "external"}}},
            "external2": {"volumes": {"main": {"disk": "external2"}}},
            "tiered_storage": {
                "volumes": {
                    "hot": [
                        {"disk": "jbod1"},
                        {"disk": "jbod2"},
                        {"max_data_part_size_bytes": "2048"},
                    ],
                    "cold": [
                        {"disk": "external"},
                        {"disk": "external2"},
                    ],
                },
                "move_factor": "0.7",
            },
            "s3_cache": {"volumes": {"external": {"disk": "s3_cache"}}},
            "minio_external_nocache": {"volumes": {"external": {"disk": "minio"}}},
        }

        s3_storage(disks=disks, policies=policies, restart=restart)


def default_columns(simple=True, partition_key_type="UInt8"):
    columns = [
        {"name": "p", "type": partition_key_type},
        {"name": "i", "type": "UInt64"},
        {"name": "Path", "type": "String"},
        {"name": "Time", "type": "DateTime"},
        {"name": "Value", "type": "Float64"},
        {"name": "Timestamp", "type": "Int64"},
        {"name": "extra", "type": "Int64"},
    ]

    if simple:
        return columns[:2]
    else:
        return columns


def valid_partition_key_types_columns():
    return [
        {"name": "int8", "type": "Int8"},
        {"name": "int16", "type": "Int16"},
        {"name": "int32", "type": "Int32"},
        {"name": "int64", "type": "Int64"},
        {"name": "uint8", "type": "UInt8"},
        {"name": "uint16", "type": "UInt16"},
        {"name": "uint32", "type": "UInt32"},
        {"name": "uint64", "type": "UInt64"},
        {"name": "date", "type": "Date"},
        {"name": "date32", "type": "Date32"},
        {"name": "datetime", "type": "DateTime"},
        {"name": "datetime64", "type": "DateTime64"},
        {"name": "string", "type": "String"},
        {"name": "fixedstring", "type": "FixedString(10)"},
    ]


def escape_json_for_sql(json_obj):
    """Escape JSON object for use in SQL string literals."""
    json_str = json.dumps(json_obj)
    return json_str.replace("'", "''")


@TestStep(Given)
def create_temp_bucket(self):
    """Create temporary S3 bucket."""

    temp_s3_path = temporary_bucket_path(
        bucket_prefix=f"{self.context.bucket_prefix}/export_part"
    )

    self.context.uri = f"{self.context.uri_base}export_part/{temp_s3_path}/"


@TestStep(Given)
def create_s3_table(
    self,
    table_name,
    cluster=None,
    create_new_bucket=False,
    columns=None,
    partition_by="p",
):
    """Create a destination S3 table."""

    if create_new_bucket:
        create_temp_bucket()

    if columns is None:
        columns = default_columns(simple=True)

    table_name = f"{table_name}_{getuid()}"
    engine = f"""
        S3(
            '{self.context.uri}',
            '{self.context.access_key_id}',
            '{self.context.secret_access_key}',
            filename='{table_name}',
            format='Parquet',
            compression='auto',
            partition_strategy='hive'
        )
    """

    create_table(
        table_name=table_name,
        columns=columns,
        partition_by=partition_by,
        engine=engine,
        cluster=cluster,
    )

    return table_name
