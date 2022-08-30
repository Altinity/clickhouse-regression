#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
from tiered_storage.tests.common import get_random_string
from testflows.core import *
from testflows.asserts import error


@TestScenario
@Name("double move while select")
@Examples(
    "name positive",
    [
        ("test_double_move_while_select_negative", 0),
        ("test_double_move_while_select_positive", 1),
    ],
)
def scenario(self, cluster, node="clickhouse1"):
    """Check that we can perform second move of the part
    during a long select query.
    """
    with Given("cluster node"):
        node = cluster.node(node)

    for example in self.examples:
        name, positive = example
        with When(f"for example name='{name}', positive='{positive}'"):
            with When("I create table"):
                node.query(
                    f"""
                    CREATE TABLE {name} (
                        n Int64,
                        s String
                    ) ENGINE = MergeTree
                    ORDER BY tuple()
                    PARTITION BY n
                    SETTINGS storage_policy='small_jbod_with_external'
                """
                )
            try:
                with When(
                    "I insert some data", description="one row with 10MB of data"
                ):
                    string = get_random_string(cluster, 10 * 1024 * 1024, steps=False)
                    node.query(f"INSERT INTO {name} VALUES (1, '{string}')")

                with When("I get number of active parts for the table"):
                    parts = (
                        node.query(
                            f"SELECT name FROM system.parts WHERE table = '{name}' AND active = 1"
                        )
                        .output.strip()
                        .splitlines()
                    )

                    with Then("I check that number of parts is 1"):
                        assert len(parts) == 1, error()

                with When("I manually move the part to another disk"):
                    part = parts[0]
                    node.query(
                        f"ALTER TABLE {name} MOVE PART '{part}' TO DISK 'external'"
                    )

                def long_select():
                    if positive:
                        with When("I do long select"):
                            node.query(
                                f"SELECT sleep(3), sleep(2), sleep(1), n FROM {name}",
                                steps=False,
                                timeout=60,
                            )
                    else:
                        with When("I skip doing long select"):
                            pass

                with When(
                    f"I start a thread to {('do' if positive else 'skip')} long select"
                ):
                    with Pool(1) as p:
                        task = p.submit(long_select)
                        try:
                            with When(
                                "in parallel I move the part again back to the original disk"
                            ):
                                part = parts[0]
                                node.query(
                                    f"ALTER TABLE {name} MOVE PART '{part}' TO DISK 'jbod1'"
                                )

                            with When(
                                "I then fill the disk to force the server to make move of partition"
                            ):
                                node.query(
                                    f"INSERT INTO {name} VALUES (2, '{get_random_string(cluster, 9 * 1024 * 1024, steps=False)}')"
                                )
                                node.query(
                                    f"INSERT INTO {name} VALUES (3, '{get_random_string(cluster, 9 * 1024 * 1024, steps=False)}')"
                                )
                                node.query(
                                    f"INSERT INTO {name} VALUES (4, '{get_random_string(cluster, 9 * 1024 * 1024, steps=False)}')"
                                )

                            with When("I check disk that used for the active part"):
                                part = parts[0]
                                r = (
                                    node.query(
                                        f"SELECT disk_name FROM system.parts WHERE table = '{name}' AND active = 1 AND name = '{part}'"
                                    )
                                    .output.strip()
                                    .splitlines()
                                )
                                with Then(
                                    "if select locked old part on the destination disk the move shall fail"
                                ):
                                    assert r == [
                                        ("jbod1" if positive else "external")
                                    ], error()
                        finally:
                            with Finally("I join the thread"):
                                task.result(timeout=60)

                with When("I do select on the table"):
                    r = (
                        node.query(f"SELECT n FROM {name} ORDER BY n")
                        .output.strip()
                        .splitlines()
                    )

                    expected = ["1", "2", "3", "4"]
                    with Then("it should match the expected", description=expected):
                        assert r == expected, error()

            finally:
                with Finally("I drop the table"):
                    node.query(f"DROP TABLE IF EXISTS {name} SYNC")
