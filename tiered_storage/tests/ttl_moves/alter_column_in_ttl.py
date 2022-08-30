#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import datetime

from testflows.core import *
from testflows.asserts import error
from tiered_storage.requirements import *


@TestScenario
@Name("alter column in ttl")
@Requirements(
    RQ_SRS_004_TTLExpressions_Alter_DropColumn("1.0"),
    RQ_SRS_004_TTLExpressions_Alter_AddColumn("1.0"),
    RQ_SRS_004_TTLExpressions_Alter_CommentColumn("1.0"),
    RQ_SRS_004_TTLExpressions_Alter_ClearColumn("1.0"),
    RQ_SRS_004_TTLExpressions_Alter_ModifyColumn("1.0"),
)
@Examples(
    "name engine",
    [
        ("mt_alter_column_in_ttl", "MergeTree()"),
        # ("replicated_mt_alter_column_in_ttl", "ReplicatedMergeTree('/clickhouse/replicated_alter_column_in_ttl', '1')"),
    ],
    "%-31s | %-20s",
)
def scenario(self, cluster, node="clickhouse1"):
    """Check altering columns that are used in the TTL expression."""
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, engine = example
        with Example(f"table name='{name}', engine='{engine}'"):
            try:
                with Given("I create table"):
                    node.query(
                        f"""
                        CREATE TABLE {name}
                        (
                            date Date,
                            ttl_days UInt16,
                            value String
                        )
                        ENGINE = {engine}
                        PARTITION BY (date)
                        ORDER BY (date, value)
                        TTL date + INTERVAL ttl_days DAY TO VOLUME 'medium',
                            date + INTERVAL (ttl_days * 4) DAY TO VOLUME 'slow',
                            date + INTERVAL (ttl_days * 24) DAY DELETE
                        SETTINGS storage_policy='fast_med_and_slow'
                    """
                    )

                    def date(offset, convert=True):
                        date = (
                            datetime.datetime.now() + datetime.timedelta(days=offset)
                        ).strftime("%Y-%m-%d")
                        if convert:
                            return f"toDate('{date}')"
                        else:
                            return date

                    with And("some data in the table"):
                        for i in range(4):
                            node.query(
                                f"INSERT INTO {name} VALUES ({date(0)},1,'fast{i}')"
                            )

                with When("I try to drop column"):
                    exitcode = 47
                    message = "Exception: Missing columns: 'ttl_days'"
                    node.query(
                        f"ALTER TABLE {name} DROP COLUMN ttl_days", message, exitcode
                    )

                    message = "Exception: Missing columns: 'date'"
                    node.query(
                        f"ALTER TABLE {name} DROP COLUMN date", message, exitcode
                    )

                with When("I try to add column"):
                    node.query(
                        f"ALTER TABLE {name} ADD COLUMN ttl_days_offset Int16 AFTER ttl_days"
                    )

                    with When("I modify TTL expressions to use the new column"):
                        node.query(
                            f"""ALTER TABLE {name} MODIFY
                            TTL date + INTERVAL ttl_days + ttl_days_offset DAY TO VOLUME 'medium',
                            date + INTERVAL (ttl_days + ttl_days_offset * 4) DAY TO VOLUME 'slow',
                            date + INTERVAL (ttl_days + ttl_days_offset * 24) DAY DELETE
                        """
                        )

                    with And(
                        "I insert a row that would be remove with new TTL expressions"
                    ):
                        node.query(
                            f"INSERT INTO {name} VALUES ({date(-2)},1,0,'delete')"
                        )

                    with Then("I check the row was removed"):
                        if hasattr(cluster, "with_minio") and hasattr(
                            cluster, "with_s3amazon"
                        ):
                            node.query(f"OPTIMIZE TABLE {name}")
                        r = node.query(
                            f"SELECT * FROM {name} WHERE value = 'delete'"
                        ).output.strip()
                        assert r == "", error()

                with When("I try to add column comment"):
                    node.query(
                        f"ALTER TABLE {name} COMMENT COLUMN ttl_days 'TTL days parameter'"
                    )

                    with Then("the comment shall be in the table description"):
                        r = node.query(f"DESCRIBE TABLE {name}").output.strip()
                        assert "ttl_days\tUInt16\t\t\tTTL days parameter" in r, error()

                with When("I try to clear column"):
                    with When("I list used disks before alter"):
                        before_disks = set(
                            node.query(
                                f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                                " AND active = 1"
                            ).output.splitlines()
                        )

                    with And("I execute alter command"):
                        node.query(
                            f"ALTER TABLE {name} CLEAR COLUMN ttl_days IN PARTITION ('{date(0, convert=False)}')"
                        )

                    with And("I optimize table to make sure all rows get deleted"):
                        node.query(f"OPTIMIZE TABLE {name} FINAL")

                    with Then("all rows should now be deleted"):
                        for retry in retries(timeout=30, delay=1):
                            with retry:
                                r = (
                                    node.query(f"SELECT ttl_days FROM {name}")
                                    .output.strip()
                                    .splitlines()
                                )
                                assert r == [], error()

                    with Then("I wait for used disks to become empty"):
                        for retry in retries(timeout=30):
                            with retry:
                                after_disks = set(
                                    node.query(
                                        f"SELECT disk_name FROM system.parts WHERE table = '{name}'"
                                        " AND active = 1"
                                    ).output.splitlines()
                                )
                                assert after_disks == set(), error()

                with When("I try to modify column type then it should work"):
                    node.query(f"ALTER TABLE {name} MODIFY COLUMN ttl_days UInt64")

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
