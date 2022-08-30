#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import json
from testflows.core import *
from testflows.asserts import error, snapshot, values
from helpers.common import check_clickhouse_version
from tiered_storage.requirements import *


@TestScenario
@Name("system tables")
@Requirements(
    RQ_SRS_004_StoragePolicy_Introspection("1.0"),
    RQ_SRS_004_Configuration_DefiningMultipleDisks("1.0"),
    RQ_SRS_004_Configuration_DefiningMultipleDisks_DefaultDisk("1.0"),
    RQ_SRS_004_Configuration_MultipleDisksDefinition_Syntax("1.0"),
    RQ_SRS_004_Configuration_MultipleDisksDefinition_Syntax_Disk_Options("1.0"),
    RQ_SRS_004_Configuration_Disks_Reading("1.0"),
    RQ_SRS_004_StoragePolicy("1.0"),
    RQ_SRS_004_StoragePolicy_Multiple("1.0"),
    RQ_SRS_004_StoragePolicy_Syntax("1.0"),
    RQ_SRS_004_StoragePolicy_Syntax_Volume_Options("1.0"),
    RQ_SRS_004_StoragePolicy_Reading("1.0"),
)
def scenario(self, cluster, node="clickhouse1"):
    """Check output from system.disks and system.storage_policies tables."""
    with Given("cluster"):
        node = cluster.node(node)
        with When("I read system.disks table"):
            result = node.query(
                "SELECT name, path, keep_free_space FROM system.disks FORMAT JSON"
            ).output

            with And("convert result data to JSON"):
                disk_data = json.loads(result)["data"]

            with And("sort disks data by name"):
                disk_data = sorted(disk_data, key=lambda x: x["name"])

            with Then("result should match the expected"):
                with values() as that:
                    name = "disk_data"
                    if (
                        cluster.with_minio
                        or (cluster.with_s3gcs)
                        or (
                            check_clickhouse_version(">=22.3")(self)
                            and cluster.with_s3amazon
                        )
                    ):
                        name += "_with_external"
                    assert that(snapshot(disk_data, id=name)), error()

        with When("I read system.storage_policies"):
            result = node.query(
                "SELECT * FROM system.storage_policies WHERE policy_name != 'default' FORMAT JSON"
            ).output

            with And("convert result data to JSON"):
                policies_data = json.loads(result)["data"]

            with And("sort policies data by policy_name and volume_name"):

                def key(x):
                    return (x["policy_name"], x["volume_name"], x["volume_priority"])

                policies_data = sorted(policies_data, key=key)

            with Then("result should match the expected"):
                with values() as that:
                    name = "policies_data"
                    if (
                        cluster.with_minio
                        or (cluster.with_s3gcs)
                        or (
                            check_clickhouse_version(">=22.3")(self)
                            and cluster.with_s3amazon
                        )
                    ):
                        name += "_with_external"
                    assert that(snapshot(policies_data, id=name)), error()
