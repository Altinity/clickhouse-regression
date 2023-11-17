#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import TestScenario, Name
from testflows.core import Given, When, And, Then
from testflows.asserts import error


@TestScenario
@Name("no warning about zero max data part size")
def scenario(self, cluster):
    """Check there is no warning about zero
    max data part size in clickhouse-server.log
    """
    names = cluster.nodes.get("clickhouse", [])
    with Given("cluster"), Given(f"nodes {names}"):
        for node in [cluster.node(name) for name in names]:
            with When(f"I am on node {node.name}"):
                with When(
                    "I create table with storage policy 'small_jbod_with_external'"
                ):
                    node.query(
                        """
                        CREATE TABLE default.test_warning_table (
                            s String
                        ) ENGINE = MergeTree
                        ORDER BY tuple()
                        SETTINGS storage_policy='small_jbod_with_external'
                    """
                    )

                with And("I then drop the table"):
                    node.query(
                        """
                        DROP TABLE default.test_warning_table SYNC
                    """
                    )

                def check_log(cmd, exitcode=0):
                    cmd = node.command(
                        f"cat /var/log/clickhouse-server/clickhouse-server.log | {cmd}",
                        no_checks=True,
                    )
                    with Then(f"check exitcode is {exitcode}"):
                        assert cmd.exitcode == exitcode, error()

                warning = "Warning.*Volume.*special_warning_zero_volume"
                with Then(f"log should not contain '{warning}'"):
                    check_log(f'grep -E "{warning}"', exitcode=1)

                warning = "Warning.*Volume.*special_warning_default_volume"
                with And(f"log should not contain '{warning}'"):
                    check_log(f'grep -E "{warning}"', exitcode=1)

                warning = "Warning.*Volume.*special_warning_small_volume"
                with And(f"log should contain '{warning}'"):
                    check_log(f'grep -E "{warning}"', exitcode=0)

                warning = "Warning.*Volume.*special_warning_big_volume"
                with And(f"log should not contain '{warning}'"):
                    check_log(f'grep -E "{warning}"', exitcode=1)
