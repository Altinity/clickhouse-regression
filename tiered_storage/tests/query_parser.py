#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from testflows.core import *
from tiered_storage.requirements import *


@TestScenario
@Name("query parser")
@Requirements(
    RQ_SRS_004_StoragePolicy_Assignment("1.0"),
    RQ_SRS_004_StoragePolicy_AddingToTable_CreateTable("1.0"),
    RQ_SRS_004_Volume_StoragePolicy_AddingToTable_AlterTable("1.0"),
)
def scenario(self, cluster, node="clickhouse1"):
    """Check query parsing."""
    with Given("cluster"):
        node = cluster.node(node)
        with When("I create table with an invalid storage policy"):
            with When("I create table with storage policy that is not defined"):
                exitcode = 222
                message = "Exception: Unknown storage policy `very_exciting_policy`"
                node.query(
                    """
                    CREATE TABLE table_with_absent_policy (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    SETTINGS storage_policy='very_exciting_policy'
                """,
                    message,
                    exitcode,
                )

            with When("I create table with storage policy that uses disk name"):
                exitcode = 222
                message = "Exception: Unknown storage policy `jbod1`"
                node.query(
                    """
                    CREATE TABLE table_with_absent_policy (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    SETTINGS storage_policy='jbod1'
                """,
                    message,
                    exitcode,
                )

        with When("I create table with normal policy"):
            with When("I create table"):
                node.query(
                    """
                    CREATE TABLE table_with_normal_policy (
                        d UInt64
                    ) ENGINE = MergeTree()
                    ORDER BY d
                    SETTINGS storage_policy='default'
                 """,
                    exitcode=0,
                )

            try:
                with And("I insert data into it"):
                    node.query(
                        "INSERT INTO table_with_normal_policy VALUES (5)", exitcode=0
                    )

                with When("I try to move partition 'all' to invalid volume"):
                    exitcode = 248
                    message = "Exception: Wrong number of fields in the partition expression: 1, must be: 0"
                    sql = "ALTER TABLE table_with_normal_policy MOVE PARTITION 'all' TO VOLUME 'some_volume'"
                    node.query(sql, message, exitcode)

                with When("I try to move partition 'all' to invalid disk"):
                    exitcode = 248
                    message = "Exception: Wrong number of fields in the partition expression: 1, must be: 0"
                    sql = "ALTER TABLE table_with_normal_policy MOVE PARTITION 'all' TO DISK 'some_volume'"
                    node.query(sql, message, exitcode)

                with When("I try to move invalid part 'xxxx' to valid disk"):
                    exitcode = 233
                    message = "Exception: Unexpected part name: xxxx."
                    sql = "ALTER TABLE table_with_normal_policy MOVE PART 'xxxx' TO DISK 'jbod1'"
                    node.query(sql, message, exitcode)

                with When("I try to move invalid partition 'yyyy' to valid disk"):
                    exitcode = 248
                    message = "Exception: Wrong number of fields in the partition expression: 1, must be: 0"
                    sql = "ALTER TABLE table_with_normal_policy MOVE PARTITION 'yyyy' TO DISK 'jbod1'"
                    node.query(sql, message, exitcode)

                with When("I try to modify storage policy setting"):
                    exitcode = 36
                    message = "Exception: New storage policy `default` shall contain volumes of old one"
                    sql = "ALTER TABLE table_with_normal_policy MODIFY SETTING storage_policy='moving_jbod_with_external'"
                    node.query(sql, message, exitcode)
            finally:
                with Finally("I clean up"):
                    node.query("DROP TABLE IF EXISTS table_with_normal_policy SYNC")
