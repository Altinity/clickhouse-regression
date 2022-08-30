#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from helpers.common import *
from tiered_storage.requirements import *


@TestScenario
@Name(
    "volume configuration either max_data_part_size_bytes or max_data_part_size_ratio"
)
@Requirements(RQ_SRS_004_StoragePolicy_Syntax_Volume_Options_EitherBytesOrRatio("1.0"))
def scenario(self, cluster, node="clickhouse1"):
    """Check that an exception is raised if both max_data_part_size_bytes and
    max_data_part_size_ratio is specified for the same volume.
    """
    with Given("cluster"):
        node = cluster.node(node)
        self.context.cluster = cluster
        self.context.node = node

    with When("I read system.storage_policies table"):
        node.query(
            "SELECT * FROM system.storage_policies WHERE policy_name != 'default' FORMAT Vertical"
        )

    try:
        with And("I add invalid storage configuration"):
            entries = {
                "storage_configuration": {
                    "default_disk_with_external": {
                        "volumes": {
                            "small": {
                                "disk": "default",
                                "max_data_part_size_bytes": "2097152",
                                "max_data_part_size_ratio": "0.25",
                            }
                        }
                    }
                }
            }
            config = create_xml_config_content(
                entries,
                "invalid_volume_configuration_either_max_data_part_size_bytes_or_ratio.xml",
            )
            add_invalid_config(
                config,
                message="StorageConfiguration: Volume \\`special_warning_small_volume\\` max_data_part_size is too low",
            )

    finally:
        with Finally("check that query still works"):
            node.query(
                "SELECT * FROM system.storage_policies WHERE policy_name != 'default' FORMAT Vertical"
            )
