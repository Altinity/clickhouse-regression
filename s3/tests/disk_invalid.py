from testflows.core import *

from s3.tests.common import *
from s3.requirements import *

import time
import datetime
import os


@TestOutline(Scenario)
@Examples(
    "invalid_type", [("", Name("empty string")), ("not_a_type", Name("unknown type"))]
)
@Requirements(RQ_SRS_015_S3_Disk_Configuration_Invalid("1.0"))
def invalid_type(self, invalid_type):
    """Check that invalid S3 disk types are not allowed."""
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    disks = None
    policies = None
    node = current().context.node
    disk_name = "external"

    with Given(
        """I have a disk configuration with a S3 storage disk with invalid
               disk type"""
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            f"{disk_name}": {
                "type": f"{invalid_type}",
                "endpoint": f"{uri}",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "external": {"volumes": {"external": {"disk": f"{disk_name}"}}},
        }

    invalid_s3_storage_config(
        disks,
        policies,
        message=f"DB::Exception: DiskFactory: the disk '{disk_name}' has unknown disk type",
        tail=300,
    )


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_Invalid("1.0"))
def empty_endpoint(self):
    """Check that empty string as a S3 disk endpoint is not allowed."""
    name = "table_" + getuid()
    disks = None
    policies = None
    node = current().context.node

    with Given(
        """I have a disk configuration with a S3 storage disk with empty
               string as endpoint"""
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "external": {"type": "s3", "endpoint": ""},
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "external": {"volumes": {"external": {"disk": "external"}}},
        }

    invalid_s3_storage_config(
        disks, policies, message="DB::Exception: Host is empty in S3 URI", tail=300
    )


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_Invalid("1.0"))
def invalid_endpoint(self):
    """Check that an invalid URI for the S3 disk endpoint is not allowed."""
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    disks = None
    policies = None
    node = current().context.node

    with Given(
        "I have a disk configuration with a S3 storage disk with invalid endpoint URI"
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "external": {
                "type": "s3",
                "endpoint": "https://unknown-website/data/",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "external": {"volumes": {"external": {"disk": "external"}}},
        }

    invalid_s3_storage_config(disks, policies, message="DB::Exception:", tail=300)


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_Access("1.0"))
def access_failed(self):
    """Check that ClickHouse S3 disk can be configured with the
    skip_access_check parameter set to 0 when ClickHouse does not have access
    to the corresponding endpoint.
    """
    name = "table_" + getuid()
    disks = None
    policies = None
    node = current().context.node
    expected = "427"

    with Given(
        """I have a disk configuration with a S3 storage disk with
               a bucket with no access, and the skip_access_check parameter
               set to 0"""
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "external": {
                "type": "s3",
                "endpoint": "https://s3.us-west-2.amazonaws.com/shyiko-playground-1/data/",
                "skip_access_check": "0",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "external": {"volumes": {"external": {"disk": "external"}}},
        }

    invalid_s3_storage_config(disks, policies, message="Access Denied", tail=300)


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_Access("1.0"))
def access_failed_skip_check(self):
    """Check that ClickHouse S3 disk can be configured with the
    skip_access_check parameter set to 1 when ClickHouse does not have access
    to the corresponding endpoint.
    """
    name = "table_" + getuid()
    disks = None
    policies = None
    node = current().context.node

    with Given(
        """I have a disk configuration with a S3 storage disk with a
               bucket with no access and the skip_access_check parameter set
               to 1"""
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "external": {
                "type": "s3",
                "endpoint": "https://s3.us-west-2.amazonaws.com/shyiko-playground-1/data/",
                "skip_access_check": "1",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "external": {"volumes": {"external": {"disk": "external"}}},
        }

    with s3_storage(disks, policies, restart=True):
        try:
            with Given(
                f"""I create table using S3 storage policy external,
                       expecting success because there is no access check to this
                       disk"""
            ):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    SETTINGS storage_policy='external'
                """
                )

            with Then(
                """I store simple data in the table, expecting failure
                      because there is no access to the S3 bucket"""
            ):
                message = (
                    """DB::Exception: Access Denied."""
                    if check_clickhouse_version("<22.9")(self)
                    else """DB::Exception: Message: Access Denied"""
                )
                node.query(
                    f"INSERT INTO {name} VALUES (427)",
                    message=message,
                    exitcode=243,
                )

        finally:
            with Finally("I drop the table"):
                node.query(f"DROP TABLE IF EXISTS {name}")


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_Access_Default("1.0"))
def access_default(self):
    """Check that ClickHouse errors upon loading configuration when S3 disk
    is added with no access to the corresponding endpoint. This indicates that
    the access check is performed by default without explicitly setting
    skip_access_check to 0.
    """
    name = "table_" + getuid()
    disks = None
    policies = None
    node = current().context.node
    expected = "427"

    with Given(
        """I have a disk configuration with a S3 storage disk with
               a bucket with no access."""
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "external": {
                "type": "s3",
                "endpoint": "https://s3.us-west-2.amazonaws.com/shyiko-playground-1/data/",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "external": {"volumes": {"external": {"disk": "external"}}},
        }

    invalid_s3_storage_config(disks, policies, message="Access Denied", tail=300)


@TestScenario
@Requirements(RQ_SRS_015_S3_Disk_Configuration_CachePath_Conflict("1.0"))
def cache_path_conflict(self):
    """Check that ClickHouse returns an error when the disk cache path is changed
    to the same path as the metadata path.
    """
    name = "table_" + getuid()
    access_key_id = self.context.access_key_id
    secret_access_key = self.context.secret_access_key
    uri = self.context.uri
    disk_name = "external_" + getuid()
    disks = None
    policies = None
    node = current().context.node

    with Given(
        """I have a disk configuration with a S3 storage disk, access id
               and key provided through environment variables, cache_path set to
               same as metadata path"""
    ):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            f"{disk_name}": {
                "type": "s3",
                "endpoint": f"{uri}/",
                "access_key_id": f"{access_key_id}",
                "secret_access_key": f"{secret_access_key}",
                "cache_path": f"/var/lib/clickhouse/disks/{disk_name}/",
            },
        }

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            "default": {"volumes": {"default": {"disk": "default"}}},
            "external": {"volumes": {"external": {"disk": f"{disk_name}"}}},
        }

    message = (
        "DB::Exception: Metadata and cache path should be different:"
        if check_clickhouse_version("<22.3")(self)
        else "DB::Exception: Metadata and cache paths should be different:"
    )
    invalid_s3_storage_config(disks, policies, message=message, tail=300)


@TestOutline(Feature)
@Requirements(
    RQ_SRS_015_S3_Disk("1.0"),
    RQ_SRS_015_S3_Disk_Configuration("1.0"),
    RQ_SRS_015_S3_Policy("1.0"),
)
def outline(self):
    """Test S3 and S3 compatible storage through storage disks."""
    for scenario in loads(current_module(), Scenario):
        scenario()


@TestFeature
@Name("aws s3 invalid disk")
def aws_s3(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "aws_s3"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    outline()


@TestFeature
@Name("gcs invalid disk")
def gcs(self, uri, access_key, key_id, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "gcs"
    self.context.uri = uri
    self.context.access_key_id = key_id
    self.context.secret_access_key = access_key

    outline()


@TestFeature
@Name("minio invalid disk")
def minio(self, uri, key, secret, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    self.context.storage = "minio"
    self.context.uri = uri
    self.context.access_key_id = key
    self.context.secret_access_key = secret

    outline()
