import time
from testflows.asserts import values as That
from testflows.core.name import basename
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *
from testflows.asserts import snapshot, error
from helpers.common import getuid


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_ComparablePerformance("1.0"))
def check_comparable_performance(self, policy=None, disk_path=None, node=None):
    """Check that insertion and selection time of encrypted and unencrypted parts differ by no more than 10 percent."""

    node = self.context.node if node is None else node

    with Given("I have policy that uses local encrypted disk"):
        create_policy_with_local_encrypted_disk_and_local_disk()

    disk_path_encrypted = "/disk_local0"
    disk_path_local = "/disk_local1"

    policy = self.context.policy if policy is None else policy

    with And("I create two tables one on encrypted disk, one not"):
        table_name_unencrypted = create_table(policy="local", partition_by_id=True)
        table_name_encrypted = create_table(policy=policy, partition_by_id=True)

    with When("I insert data into the table"):
        values = (
            "("
            + "), (".join(
                [str(i % 50) + f",'insert_number {i}'" for i in range(10000000)]
            )
            + ")"
        )
        uid1 = getuid() + "1"
        uid2 = getuid() + "2"
        uid3 = getuid() + "3"
        uid4 = getuid() + "4"
        insert_into_table(
            name=table_name_unencrypted, values=values, settings=[("query_id", uid1)]
        )
        insert_into_table(
            name=table_name_encrypted, values=values, settings=[("query_id", uid2)]
        )

    with Then("I check performance for insert statement"):
        node.query("SYSTEM FLUSH LOGS")
        sql = f"select query_duration_ms from system.query_log where query_id='{uid1}' order by event_time desc limit 1"
        r_unencrypted = int((node.query(sql)).output)
        sql = f"select query_duration_ms from system.query_log where query_id='{uid2}' order by event_time desc limit 1"
        r_encrypted = int((node.query(sql)).output)
        assert 0.5 > (r_unencrypted - r_encrypted) / r_encrypted > -0.5, error()

    with Then("I check select statement"):
        node.query(
            f"SELECT * from {table_name_unencrypted} where Value LIKE '%100000%'",
            settings=[("query_id", uid3)],
        )
        node.query(
            f"SELECT * from {table_name_encrypted} where Value LIKE '%100000%'",
            settings=[("query_id", uid4)],
        )

    with Then("I check performance for select statement"):
        node.query("SYSTEM FLUSH LOGS")
        sql = f"select query_duration_ms from system.query_log where query_id='{uid3}' order by event_time desc limit 1"
        r_unencrypted = int((node.query(sql)).output)
        sql = f"select query_duration_ms from system.query_log where query_id='{uid4}' order by event_time desc limit 1"
        r_encrypted = int((node.query(sql)).output)
        assert 0.5 > (r_unencrypted - r_encrypted) / r_encrypted > -0.5, error()


@TestFeature
@Name("comparable performance")
def feature(self, node="clickhouse1"):
    """Check that insertion and selection time of encrypted and unencrypted parts differ by no more than 20 percent."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
