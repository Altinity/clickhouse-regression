import time
from testflows.asserts import error
from disk_level_encryption.tests.steps import *
from disk_level_encryption.requirements.requirements import *


@TestOutline
def alter_move_multi_volume_policy(
    self,
    number_of_volumes,
    numbers_of_disks,
    disks_types,
    keys,
    number_of_inserts,
    partition=True,
    node=None,
):
    """Check that ClickHouse supports alter move part between tho volumes that contain encrypted disks."""

    if node is None:
        node = self.context.node

    with Given("I create directories"):
        create_directories_multi_volume_policy(
            number_of_volumes=number_of_volumes, numbers_of_disks=numbers_of_disks
        )

    with And("I add configuration file"):
        add_config_multi_volume_policy(
            number_of_volumes=number_of_volumes,
            numbers_of_disks=numbers_of_disks,
            disks_types=disks_types,
            keys=keys,
        )

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy="local_encrypted", partition_by_id=partition)

    with When("I insert data into the table"):
        for i in range(number_of_inserts):
            values = f"({i}, '{i}{i}')"
            insert_into_table(name=table_name, values=values)

    with Then("I compute expected output"):
        expected_output = "\n".join(
            [
                '{"Id":' + f"{i}" + ',"Value":"' + f"{i}{i}" + '"}'
                for i in range(number_of_inserts)
            ]
        )

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with Then("I check alter move to encrypted disk"):
        r = node.query(
            f"SELECT name, disk_name, path FROM system.parts WHERE table = '{table_name}'"
        )
        partition_part_name = "2" if partition else "2_3_3_0"
        part_or_partition = "PARTITION" if partition else "PART"
        partition_part_table_row = "partition" if partition else "name"

        r = node.query(
            f"SELECT disk_name FROM system.parts WHERE table = '{table_name}' AND {partition_part_table_row} = '{partition_part_name}'"
        )
        assert "local0" in r.output, error()

        r = node.query(
            f"ALTER TABLE {table_name} MOVE {part_or_partition} '{partition_part_name}' TO VOLUME 'volume1'"
        )
        r = node.query(
            f"SELECT disk_name FROM system.parts WHERE table = '{table_name}' AND {partition_part_table_row} = '{partition_part_name}'"
        )
        assert "local1" in r.output, error()

    with Then("I expect data is not changed after move to encrypted disk"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with Then("I check alter move from encrypted disk"):
        r = node.query(
            f"ALTER TABLE {table_name} MOVE {part_or_partition} '{partition_part_name}' TO VOLUME 'volume0'"
        )
        r = node.query(
            f"SELECT disk_name FROM system.parts WHERE table = '{table_name}' AND {partition_part_table_row} = '{partition_part_name}'"
        )
        assert "local0" in r.output, error()

    with Then("I expect data is not changed after move from encrypted disk"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with Then("I restart server"):
        node.restart()

    with Then("I expect data is not changed after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestScenario
def alter_move_part_multi_volume_policy_two_volumes_one_encrypted_disk_one_not_in_each_one_key(
    self,
):
    """Check that ClickHouse supports alter move part between two volumes one encrypted disk in each."""
    alter_move_multi_volume_policy(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "local"], ["local", "encrypted"]],
        keys=[["firstfirstfirstf", None], [None, "secondsecondseco"]],
        number_of_inserts=10,
    )


@TestScenario
def alter_move_part_multi_volume_policy_two_volumes_four_encrypted_disks(self):
    """Check that ClickHouse supports alter move part between two volumes that contain two encrypted disks."""
    alter_move_multi_volume_policy(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "encrypted"]],
        keys=[
            ["firstfirstfirstf", "secondsecondseco"],
            ["thirdthirdthirdt", "fourthfourthfour"],
        ],
        number_of_inserts=10,
    )


@TestScenario
def alter_move_part_multi_volume_policy_two_volumes_one_encrypted_disk(self):
    """Check that ClickHouse supports alter move part between two volumes that contain one encrypted disk in one volume."""
    alter_move_multi_volume_policy(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "local"], ["local", "local"]],
        keys=[["firstfirstfirstf", None], [None, None]],
        number_of_inserts=10,
    )


@TestScenario
def alter_move_partition_multi_volume_policy_two_volumes_three_encrypted_disks(self):
    """Check that ClickHouse supports alter move part between two volumes that contain three encrypted disks."""
    alter_move_multi_volume_policy(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "local"], ["local", "local"]],
        keys=[["firstfirstfirstf", "secondsecondseco"], ["thirdthirdthirdt", None]],
        number_of_inserts=10,
        partition=True,
    )


@TestScenario
def alter_move_partition_multi_volume_policy_two_volumes_one_encrypted_disk_one_not_in_each_one_key(
    self,
):
    """Check that ClickHouse supports alter move part between two volumes one encrypted disk in each."""
    alter_move_multi_volume_policy(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "local"], ["local", "encrypted"]],
        keys=[["firstfirstfirstf", None], [None, "secondsecondseco"]],
        number_of_inserts=10,
        partition=True,
    )


@TestScenario
def alter_move_partition_multi_volume_policy_two_volumes_four_encrypted_disks(self):
    """Check that ClickHouse supports alter move part between two volumes that contain two encrypted disks."""
    alter_move_multi_volume_policy(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "encrypted"]],
        keys=[
            ["firstfirstfirstf", "secondsecondseco"],
            ["thirdthirdthirdt", "fourthfourthfour"],
        ],
        number_of_inserts=10,
        partition=True,
    )


@TestScenario
def alter_move_partition_multi_volume_policy_two_volumes_one_encrypted_disk(self):
    """Check that ClickHouse supports alter move part between two volumes that contain one encrypted disk in one volume."""
    alter_move_multi_volume_policy(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "local"], ["local", "local"]],
        keys=[["firstfirstfirstf", None], [None, None]],
        number_of_inserts=10,
        partition=True,
    )


@TestScenario
def alter_move_partition_multi_volume_policy_two_volumes_three_encrypted_disks(self):
    """Check that ClickHouse supports alter move part between two volumes that contain three encrypted disks."""
    alter_move_multi_volume_policy(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "local"], ["local", "local"]],
        keys=[["firstfirstfirstf", "secondsecondseco"], ["thirdthirdthirdt", None]],
        number_of_inserts=10,
        partition=True,
    )


@TestFeature
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_Alter_MoveBetweenEncryptedAndNonEncryptedDisks(
        "1.0"
    )
)
@Name("alter move multi volume policy")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse supports alter move for multi volume policy."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
