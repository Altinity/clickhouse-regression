#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import os

from testflows.core import TestScenario, Name, Requirements
from testflows.core import Given, When, Then, And, By, Finally
from testflows.connect import Shell
from testflows.asserts import error

from tiered_storage.requirements import *

test_dir = os.path.dirname(os.path.abspath(__file__))


@TestScenario
@Name("disk configuration either keep_free_space_bytes or keep_free_space_ratio")
@Requirements(
    RQ_SRS_004_Configuration_MultipleDisksDefinition_Syntax_Disk_Options_EitherBytesOrRatio(
        "1.0"
    )
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that an exception is raised if both keep_free_space_bytes and
    keep_free_space_ratio is specified for the same disk.
    """
    with Given("cluster"):
        node = cluster.node(node)

    with When("I read system.disks table"):
        node.query(
            "SELECT name, path, keep_free_space FROM system.disks FORMAT Vertical"
        )

    try:
        with And(
            "I change configuration",
            description="""
            storage configuration that has keep_free_space_bytes and keep_free_space_ratio defined for the same disk
            """,
        ):
            node.command(
                "cp /etc/clickhouse-server/config_variants/invalid_disk_configuration_either_keep_free_space_bytes_or_ratio.xml /etc/clickhouse-server/config.d"
            )
            node.command("ls /etc/clickhouse-server/config.d")

        with And("I restart the clickhouse node"):
            node.restart(safe=False)

        with Then("I should see an exception in the clickhouse-server.err log"):
            with Shell(
                command=[
                    "/bin/bash",
                    "--noediting",
                    "-c",
                    f"docker-compose run --entrypoint /bin/bash {node.name}",
                ],
                name=node.name,
            ) as bash:
                command = (
                    "tail -n 1 /var/log/clickhouse-server/clickhouse-server.err.log"
                )
                with By("executing command", description=command):
                    last_err = bash(command).output.strip()
                expected_err = "Exception: Only one of 'keep_free_space_bytes' and 'keep_free_space_ratio' can be specified"
                with Then(f"checking if '{expected_err}' is present"):
                    assert expected_err in last_err, error()
    finally:
        with Finally("I reset container"):
            cluster.command(None, f"docker-compose rm -f {node.name}")
            cluster.command(None, f"docker-compose up -d {node.name}")

            with And("check that query still works"):
                node.query(
                    "SELECT name, path, keep_free_space FROM system.disks FORMAT Vertical"
                )
