from testflows.asserts import values as That
from testflows.core.name import basename
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *
from testflows.asserts import snapshot, error


@TestOutline
def check_comparable_part_sizes(
    self, part_type, policy=None, disk_path=None, node=None
):
    """Check that size of encrypted and unencrypted parts differ by no more than 1 percent."""

    node = self.context.node if node is None else node

    with Given("I have policy that uses local encrypted disk"):
        create_policy_with_local_encrypted_disk_and_local_disk()

    disk_path_encrypted = "/disk_local0"
    disk_path_local = "/disk_local1"

    policy = self.context.policy if policy is None else policy

    min_bytes_for_wide_part = 0 if part_type == "Wide" else 1000000

    with And("I create two tables one on encrypted disk, one not"):
        table_name_unencrypted = create_table(
            policy="local",
            min_bytes_for_wide_part=min_bytes_for_wide_part,
            partition_by_id=True,
        )
        table_name_encrypted = create_table(
            policy=policy,
            min_bytes_for_wide_part=min_bytes_for_wide_part,
            partition_by_id=True,
        )

    with When("I insert data into the table"):
        values = (
            "("
            + "), (".join([str(i % 50) + f",'insert_number {i}'" for i in range(1000)])
            + ")"
        )
        insert_into_table(name=table_name_unencrypted, values=values)
        insert_into_table(name=table_name_encrypted, values=values)

    with Then("I expect all the data in wide format"):
        r_unencrypted = node.query(
            f"SELECT DISTINCT part_type FROM system.parts WHERE table = '{table_name_unencrypted}' and active ORDER BY part_type"
        )
        r_encrypted = node.query(
            f"SELECT DISTINCT part_type FROM system.parts WHERE table = '{table_name_encrypted}' and active ORDER BY part_type"
        )
        assert r_unencrypted.output == r_encrypted.output == part_type, error()

    with Then("I check file sizes"):
        sql = f"""SELECT sum(bytes)
                      FROM system.parts
                      WHERE active AND (table = '{table_name_unencrypted}')
                      GROUP BY table
                   """
        r_unencrypted = int(node.query(sql).output)
        sql = f"""SELECT sum(bytes)
                      FROM system.parts
                      WHERE active AND (table = '{table_name_encrypted}')
                      GROUP BY table
                   """
        r_encrypted = int(node.query(sql).output)
        assert 0.01 > (r_unencrypted - r_encrypted) / r_encrypted > -0.01, error()

    with Then("I restart server"):
        node.restart()

    with Then("I check file sizes after restart"):
        sql = f"""SELECT sum(bytes)
                      FROM system.parts
                      WHERE active AND (table = '{table_name_unencrypted}')
                      GROUP BY table
                   """
        r_unencrypted = int(node.query(sql).output)
        sql = f"""SELECT sum(bytes)
                      FROM system.parts
                      WHERE active AND (table = '{table_name_encrypted}')
                      GROUP BY table
                   """
        r_encrypted = int(node.query(sql).output)
        assert 0.01 > (r_unencrypted - r_encrypted) / r_encrypted > -0.01, error()


@TestScenario
def check_comparable_part_sizes_for_wide_format(
    self, policy=None, disk_path=None, node=None
):
    """Check that size of encrypted and unencrypted wide parts differ by no more than 1 percent."""
    check_comparable_part_sizes(part_type="Wide")


@TestScenario
def check_comparable_part_sizes_for_compact_format(
    self, policy=None, disk_path=None, node=None
):
    """Check that size of encrypted and unencrypted compact parts differ by no more than 1 percent."""
    check_comparable_part_sizes(part_type="Compact")


@TestFeature
@Name("comparable part sizes")
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_ComparablePartSizes("1.0"))
def feature(self, node="clickhouse1"):
    """Check that size of encrypted and unencrypted compact and wide parts differ by no more than 1 percent."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
