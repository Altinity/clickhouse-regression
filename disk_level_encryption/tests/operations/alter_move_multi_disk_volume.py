from testflows.asserts import error
from disk_level_encryption.tests.steps import *
from disk_level_encryption.requirements.requirements import *


@TestOutline
def alter_move_multi_disk_volume(
    self,
    number_of_disks,
    disks_types,
    keys,
    number_of_inserts,
    partition=False,
    node=None,
):
    """Check that ClickHouse supports alter move part and partition."""

    if node is None:
        node = self.context.node

    with Given("I create directories"):
        create_directories_multi_disk_volume(number_of_disks=number_of_disks)

    with And("I add configuration file"):
        add_config_multi_disk_volume(
            number_of_disks=number_of_disks, disks_types=disks_types, keys=keys
        )

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy="local_encrypted", partition_by_id=True)

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

        if disks_types[0] == "encrypted":
            r = node.query(
                f"SELECT disk_name FROM system.parts WHERE table = '{table_name}' AND {partition_part_table_row} = '{partition_part_name}'"
            )
            assert r.output == "encrypted_local0", error()
        else:
            r = node.query(
                f"SELECT disk_name FROM system.parts WHERE table = '{table_name}' AND {partition_part_table_row} = '{partition_part_name}'"
            )
            assert r.output == "local0", error()

        if disks_types[1] == "encrypted":
            r = node.query(
                f"ALTER TABLE {table_name} MOVE {part_or_partition} '{partition_part_name}' TO DISK 'encrypted_local1'"
            )
            r = node.query(
                f"SELECT disk_name FROM system.parts WHERE table = '{table_name}' AND {partition_part_table_row} = '{partition_part_name}'"
            )
            assert r.output == "encrypted_local1", error()
        else:
            r = node.query(
                f"ALTER TABLE {table_name} MOVE {part_or_partition} '{partition_part_name}' TO DISK 'local1'"
            )
            r = node.query(
                f"SELECT disk_name FROM system.parts WHERE table = '{table_name}' AND {partition_part_table_row} = '{partition_part_name}'"
            )
            assert r.output == "local1", error()

    with Then("I expect data is not changed after move to encrypted disk"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with Then("I check alter move from encrypted disk"):
        if disks_types[0] == "encrypted":
            r = node.query(
                f"ALTER TABLE {table_name} MOVE {part_or_partition} '{partition_part_name}' TO DISK 'encrypted_local0'"
            )
            r = node.query(
                f"SELECT disk_name FROM system.parts WHERE table = '{table_name}' AND {partition_part_table_row} = '{partition_part_name}'"
            )
            assert r.output == "encrypted_local0", error()
        else:
            r = node.query(
                f"ALTER TABLE {table_name} MOVE {part_or_partition} '{partition_part_name}' TO DISK 'local0'"
            )
            r = node.query(
                f"SELECT disk_name FROM system.parts WHERE table = '{table_name}' AND {partition_part_table_row} = '{partition_part_name}'"
            )
            assert r.output == "local0", error()

    with Then("I expect data is not changed after move from encrypted disk"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with And("I restart server"):
        node.restart()
        r = node.query(
            f"SELECT name, disk_name, path FROM system.parts WHERE table = '{table_name}'"
        )

    with Then("I expect data is not changed after ALTER MOVE"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestScenario
def alter_move_part_multi_disk_volume_local_and_encrypted(self):
    """Check that ClickHouse supports alter move part from local to encrypted disk and vice versa."""
    alter_move_multi_disk_volume(
        number_of_disks=2,
        disks_types=["local", "encrypted"],
        keys=[None, "firstfirstfirstf"],
        number_of_inserts=10,
    )


@TestScenario
def alter_move_part_multi_disk_volume_encrypted_and_encrypted(self):
    """Check that ClickHouse supports alter move part from encrypted to encrypted disk and vice versa."""
    alter_move_multi_disk_volume(
        number_of_disks=2,
        disks_types=["encrypted", "encrypted"],
        keys=["secondsecondseco", "firstfirstfirstf"],
        number_of_inserts=10,
    )


@TestScenario
def alter_move_partition_multi_disk_volume_local_and_encrypted(self):
    """Check that ClickHouse supports alter move partition from local to encrypted disk and vice versa."""
    alter_move_multi_disk_volume(
        number_of_disks=2,
        disks_types=["local", "encrypted"],
        keys=[None, "firstfirstfirstf"],
        number_of_inserts=10,
        partition=True,
    )


@TestScenario
def alter_move_partition_multi_disk_volume_encrypted_and_encrypted(self):
    """Check that ClickHouse supports alter move partition from encrypted to encrypted disk and vice versa."""
    alter_move_multi_disk_volume(
        number_of_disks=2,
        disks_types=["encrypted", "encrypted"],
        keys=["secondsecondseco", "firstfirstfirstf"],
        number_of_inserts=10,
        partition=True,
    )


@TestFeature
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_Alter_MoveBetweenEncryptedAndNonEncryptedDisks(
        "1.0"
    )
)
@Name("alter move multi disk volume")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse supports alter move for multi disk volume."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
