from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

CLUSTER = "replicated_cluster"


@TestStep(Given)
def cas_table(self, name, node=None):
    """Create a tiny ReplicatedMergeTree on storage_policy='ca' and drop it after."""
    if node is None:
        node = self.context.node
    node.query(f"DROP TABLE IF EXISTS {name} ON CLUSTER {CLUSTER} SYNC")
    node.query(
        f"""
        CREATE TABLE {name} ON CLUSTER {CLUSTER}
        (
            id UInt64
        )
        ENGINE = ReplicatedMergeTree('/clickhouse/tables/{{shard}}/{name}', '{{replica}}')
        ORDER BY id
        SETTINGS storage_policy = 'ca',
                 search_orphaned_parts_disks = 'local'
        """
    )
    try:
        yield name
    finally:
        with Finally("drop the smoke table"):
            node.query(f"DROP TABLE IF EXISTS {name} ON CLUSTER {CLUSTER} SYNC")


@TestScenario
@Name("select 1 on both replicas")
def select_one(self):
    for label, node in (
        ("clickhouse1", self.context.node),
        ("clickhouse2", self.context.node2),
    ):
        with When(f"I SELECT 1 on {label}"):
            r = node.query("SELECT 1 FORMAT TabSeparated").output.strip()
        with Then("the result is 1"):
            assert r == "1", error()


@TestScenario
@Name("cas disk is present")
def cas_disk(self):
    node = self.context.node
    with When("I read system.disks for disk ca"):
        r = node.query(
            "SELECT name, metadata_type FROM system.disks WHERE name = 'ca' "
            "FORMAT TabSeparated"
        ).output.strip()
    with Then("disk ca exists and is CAS"):
        parts = r.split("\t")
        assert len(parts) == 2 and parts[0] == "ca", error()
        assert parts[1].lower() in ("cas", "content_addressed"), error()


@TestScenario
@Name("insert and select on cas policy")
def insert_select(self):
    node = self.context.node
    with Given("a replicated table on storage_policy ca"):
        table = cas_table(name=f"soak_tests_smoke_{getuid()}")

    with When("I insert one row on replica 1"):
        node.query(f"INSERT INTO {table} VALUES (1)")

    with And("I sync replica 2"):
        self.context.node2.query(f"SYSTEM SYNC REPLICA {table}")

    with Then("both replicas see the row"):
        for n in self.context.nodes:
            count = n.query(f"SELECT count() FROM {table} FORMAT TabSeparated").output.strip()
            assert count == "1", error()


@TestFeature
@Name("smoke")
def feature(self):
    """Cluster bring-up check for the rewrite. Does not run soak workloads."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
