from testflows.asserts import error
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *

entries = {
    "storage_configuration": {
        "disks": [],
        "policies": {"local_encrypted": {"volumes": {"volume1": []}}},
    }
}


@TestOutline
def multi_disk_volume(
    self,
    number_of_disks,
    disks_types,
    keys,
    number_of_inserts,
    check_merge=True,
    node=None,
):
    """Check ClickHouse supports policies with different number of
    disks in one volume, and with different disks configurations.
    """

    if node is None:
        node = self.context.node

    with Given("I create directories"):
        create_directories_multi_disk_volume(number_of_disks=number_of_disks)

    with Given("I add configuration file"):
        add_config_multi_disk_volume(
            number_of_disks=number_of_disks, disks_types=disks_types, keys=keys
        )

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy="local_encrypted")

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

    with Then("I compute expected output for used disks"):
        disks = []
        for i in range(number_of_disks):
            if disks_types[i] == "local":
                disks.append(f"local{i}")
            elif disks_types[i] == "encrypted":
                disks.append(f"encrypted_local{i}")
        disks.sort()
        used_disks = "\n".join(disks)

    with Then("I expect data is inserted into all disks"):
        r = node.query(
            f"SELECT DISTINCT disk_name FROM system.parts WHERE table = '{table_name}' ORDER BY disk_name"
        )
        note(r.output)
        note(used_disks)
        assert r.output == used_disks, error()

    if check_merge:
        with And("I check we can merge these parts"):
            r = node.query(f"OPTIMIZE TABLE {table_name} FINAL")
            r = node.query(
                f"SELECT count() FROM system.parts WHERE table =  '{table_name}' AND active FORMAT JSONEachRow"
            )
            assert r.output == '{"count()":"1"}', error()

        with And("I check data is not lost after merge"):
            r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
            assert r.output == expected_output, error()

    with Then("I restart server"):
        node.restart()

    with Then("I expect data is not changed after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestScenario
def multi_disk_volume_two_disks_one_encrypted(self):
    """Check ClickHouse supports policy with one volume which contains two disks,
    one encrypted, one not encrypted.
    """
    multi_disk_volume(
        number_of_disks=2,
        disks_types=["local", "encrypted"],
        keys=[None, "firstfirstfirstf"],
        number_of_inserts=5,
    )


@TestScenario
def multi_disk_volume_two_encrypted_disks_one_key(self):
    """Check ClickHouse supports policy with one volume which contains two encrypted disks,
    with one encryption key.
    """
    multi_disk_volume(
        number_of_disks=2,
        disks_types=["encrypted", "encrypted"],
        keys=["firstfirstfirstf", "firstfirstfirstf"],
        number_of_inserts=5,
    )


@TestScenario
def multi_disk_volume_two_encrypted_disks_two_keys(self):
    """Check ClickHouse supports policy with one volume which contains two encrypted disks,
    with two different encryption keys.
    """
    multi_disk_volume(
        number_of_disks=2,
        disks_types=["encrypted", "encrypted"],
        keys=["firstfirstfirstf", "secondsecondseco"],
        number_of_inserts=5,
    )


@TestScenario
def multi_disk_volume_three_encrypted_disks_two_keys(self):
    """Check ClickHouse supports policy with one volume which contains three encrypted disks,
    with two different encryption keys.
    """
    multi_disk_volume(
        number_of_disks=3,
        disks_types=["encrypted", "encrypted", "encrypted"],
        keys=["secondsecondseco", "firstfirstfirstf", "secondsecondseco"],
        number_of_inserts=5,
    )


@TestScenario
def multi_disk_volume_three_encrypted_disks_three_keys(self):
    """Check ClickHouse supports policy with one volume which contains three encrypted disks,
    with three different encryption keys.
    """
    multi_disk_volume(
        number_of_disks=3,
        disks_types=["encrypted", "encrypted", "encrypted"],
        keys=["firstfirstfirstf", "secondsecondseco", "thirdthirdthirdt"],
        number_of_inserts=5,
    )


@TestScenario
def multi_disk_volume_three_encrypted_disks_same_key(self):
    """Check ClickHouse supports policy with one volume which contains three encrypted disks,
    with one encryption key.
    """
    multi_disk_volume(
        number_of_disks=3,
        disks_types=["encrypted", "encrypted", "encrypted"],
        keys=["firstfirstfirstf", "firstfirstfirstf", "firstfirstfirstf"],
        number_of_inserts=5,
    )


@TestScenario
def multi_disk_volume_three_disks_two_encrypted_same_key(self):
    """Check ClickHouse supports policy with one volume which contains two encrypted disks
    and one unencrypted, with one encryption key.
    """
    multi_disk_volume(
        number_of_disks=3,
        disks_types=["encrypted", "local", "encrypted"],
        keys=["firstfirstfirstf", None, "firstfirstfirstf"],
        number_of_inserts=5,
    )


@TestScenario
def multi_disk_volume_three_disks_two_encrypted_two_keys(self):
    """Check ClickHouse supports policy with one volume which contains two encrypted disks
    and one unencrypted, with two encryption key.
    """
    multi_disk_volume(
        number_of_disks=3,
        disks_types=["encrypted", "local", "encrypted"],
        keys=["firstfirstfirstf", None, "secondsecondseco"],
        number_of_inserts=5,
    )


@TestScenario
def multi_disk_volume_three_disks_one_encrypted_same_key(self):
    """Check ClickHouse supports policy with one volume which contains one encrypted disks
    and two unencrypted.
    """
    multi_disk_volume(
        number_of_disks=3,
        disks_types=["local", "encrypted", "local"],
        keys=[None, "firstfirstfirstf", None],
        number_of_inserts=5,
    )


@TestFeature
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_MultiDiskVolumes("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_TieredStorage("1.0"),
)
@Name("multi disk volume")
def feature(self, node="clickhouse1"):
    """Check that clickhouse supports having encrypted disk when policy contains
    one volume which have one or more encrypted disks.
    """
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
