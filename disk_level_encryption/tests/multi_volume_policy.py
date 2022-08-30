import time
from testflows.core import *
from testflows.asserts import error
from disk_level_encryption.tests.steps import *
from disk_level_encryption.requirements.requirements import *
from helpers.cluster import QueryRuntimeException


@TestOutline
def multi_volume_policy_using_move_factor(
    self,
    number_of_volumes,
    numbers_of_disks,
    disks_types,
    keys,
    number_of_inserts,
    check_merge=True,
    node=None,
):
    """Check ClickHouse supports policies with different number of
    disks in several volumes, and with different disks configurations.
    """

    if node is None:
        node = self.context.node

    with Given("I create directories I add configuration file"):
        create_directories_multi_volume_policy(
            number_of_volumes=number_of_volumes, numbers_of_disks=numbers_of_disks
        )

    with And("I add configuration file"):
        add_config_multi_volume_policy(
            number_of_volumes=number_of_volumes,
            numbers_of_disks=numbers_of_disks,
            disks_types=disks_types,
            keys=keys,
            move_factor=True,
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
        for j in range(number_of_volumes):
            for i in range(numbers_of_disks[j]):
                if disks_types[j][i] == "local":
                    disks.append(f"local{j}{i}")
                elif disks_types[j][i] == "encrypted":
                    disks.append(f"encrypted_local{j}{i}")
        disks.sort()
        used_disks = "\n".join(disks)

    with Then("I expect data is inserted into all disks"):
        r = node.query(
            f"SELECT DISTINCT disk_name FROM system.parts WHERE table = '{table_name}' ORDER BY disk_name"
        )
        assert r.output == used_disks, error()

    if check_merge:
        with Then("I check we can merge these parts"):
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


@TestOutline
def multi_volume_policy_using_ttl(
    self,
    number_of_volumes,
    numbers_of_disks,
    disks_types,
    keys,
    check_merge=True,
    node=None,
):
    """Check ClickHouse supports policies with different number of
    disks in several volumes, and with different disks configurations.
    """

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
        table_name = create_table(policy="local_encrypted", ttl=True, ttl_timeout=10)

    with When("I insert data into the table"):
        now = time.time()
        wait_expire = 31 * 60
        date = now
        for i in range(6):
            values = f"({i}, toDateTime({date-i*wait_expire}), '{i}{i}')"
            insert_into_table(name=table_name, values=values)

    r = node.query(
        f"SELECT Id, Date as Seconds, Value FROM {table_name} ORDER BY Id FORMAT JSONEachRow"
    )
    with Then("I compute expected output"):
        expected_output = (
            '{"Id":0,"Seconds":' + f"{int(date)}" + ',"Value":"00"}\n'
            '{"Id":1,"Seconds":' + f"{int(date-wait_expire)}" + ',"Value":"11"}\n'
            '{"Id":2,"Seconds":' + f"{int(date-2*wait_expire)}" + ',"Value":"22"}\n'
            '{"Id":3,"Seconds":' + f"{int(date-3*wait_expire)}" + ',"Value":"33"}'
        )

    with Then("I expect data is successfully inserted"):
        for attempt in retries(timeout=30, delay=5):
            with attempt:
                r = node.query(
                    f"SELECT Id, toInt32(Date) as Seconds, Value FROM {table_name} ORDER BY Id FORMAT JSONEachRow",
                    steps=False,
                )
                assert r.output == expected_output, error()

    if check_merge:
        with Then("I check we can merge these parts"):
            r = node.query(
                f"SELECT name, disk_name, active FROM system.parts WHERE table = '{table_name}'"
            )
            with Then("I expect data is successfully inserted"):
                for attempt in retries(timeout=30, delay=5):
                    with attempt:
                        r = node.query(
                            f"OPTIMIZE TABLE {table_name} FINAL", steps=False
                        )

            r = node.query(
                f"SELECT count() FROM system.parts WHERE table = '{table_name}' AND active FORMAT JSONEachRow"
            )
            assert r.output == '{"count()":"1"}', error()

        with And("I check data is not lost after merge"):
            r = node.query(
                f"SELECT Id, toInt32(Date) as Seconds, Value FROM {table_name} ORDER BY Id FORMAT JSONEachRow"
            )
            assert r.output == expected_output, error()

    with Then("I restart server"):
        node.restart()

    with Then("I expect data is not changed after restart"):
        r = node.query(
            f"SELECT Id, toInt32(Date) as Seconds, Value FROM {table_name} ORDER BY Id FORMAT JSONEachRow"
        )
        assert r.output == expected_output, error()


@TestScenario
def multi_volume_policy_two_volumes_one_encrypted_disk_one_not_in_each_one_key(self):
    """Check ClickHouse supports policy with two volumes which contains two disks,
    one encrypted, one not encrypted with the same key.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["local", "encrypted"], ["local", "encrypted"]],
        keys=[[None, "firstfirstfirstf"], [None, "firstfirstfirstf"]],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_one_encrypted_disk_one_not_in_each_two_keys(self):
    """Check ClickHouse supports policy with two volumes which contains two disks,
    one encrypted, one not encrypted with two different keys.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["local", "encrypted"], ["local", "encrypted"]],
        keys=[[None, "firstfirstfirstf"], [None, "secondsecondseco"]],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_each_one_key(self):
    """Check ClickHouse supports policy with two volumes which contains two encrypted disks,
    with one key.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "encrypted"]],
        keys=[
            ["firstfirstfirstf", "firstfirstfirstf"],
            ["firstfirstfirstf", "firstfirstfirstf"],
        ],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_each_two_keys_in_one_volume(
    self,
):
    """Check ClickHouse supports policy with two volumes which contains two encrypted disks,
    with two keys when one volume has different keys.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "encrypted"]],
        keys=[
            ["firstfirstfirstf", "secondsecondseco"],
            ["firstfirstfirstf", "firstfirstfirstf"],
        ],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_each_two_keys_in_two_volumes(
    self,
):
    """Check ClickHouse supports policy with two volumes which contains two encrypted disks,
    with two keys when two volumes have different keys.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "encrypted"]],
        keys=[
            ["firstfirstfirstf", "secondsecondseco"],
            ["secondsecondseco", "firstfirstfirstf"],
        ],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_each_two_keys_one_key_for_one_volume(
    self,
):
    """Check ClickHouse supports policy with two volumes which contains two encrypted disks,
    with two keys when one key refers to one volume.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "encrypted"]],
        keys=[
            ["secondsecondseco", "secondsecondseco"],
            ["firstfirstfirstf", "firstfirstfirstf"],
        ],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_each_three_keys_same_keys_in_one_volume(
    self,
):
    """Check ClickHouse supports policy with two volumes which contains two encrypted disks,
    with three keys when one volume has one encryption key.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "encrypted"]],
        keys=[
            ["firstfirstfirstf", "secondsecondseco"],
            ["thirdthirdthirdt", "thirdthirdthirdt"],
        ],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_each_three_keys_same_keys_in_different_disks(
    self,
):
    """Check ClickHouse supports policy with two volumes which contains two encrypted disks,
    with three keys when each volume has two encryption keys.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "encrypted"]],
        keys=[
            ["firstfirstfirstf", "secondsecondseco"],
            ["secondsecondseco", "thirdthirdthirdt"],
        ],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_each_four_keys(self):
    """Check ClickHouse supports policy with two volumes which contains two encrypted disks,
    with four keys.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "encrypted"]],
        keys=[
            ["firstfirstfirstf", "secondsecondseco"],
            ["thirdthirdthirdt", "fourthfourthfour"],
        ],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_one_one_encrypted_in_the_other_one_key(
    self,
):
    """Check ClickHouse supports policy with two volumes, one contains two encrypted disks,
    the other contains one encrypted disk with one key.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "local"]],
        keys=[["firstfirstfirstf", "firstfirstfirstf"], ["firstfirstfirstf", None]],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_one_one_encrypted_in_the_other_two_keys_in_one_volume(
    self,
):
    """Check ClickHouse supports policy with two volumes, one contains two encrypted disks,
    the other contains one encrypted disk with two keys in one volume.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "local"]],
        keys=[["firstfirstfirstf", "secondsecondseco"], ["firstfirstfirstf", None]],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_one_one_encrypted_in_the_other_two_keys_for_each_volume(
    self,
):
    """Check ClickHouse supports policy with two volumes, one contains two encrypted disks,
    the other contains one encrypted disk with two keys, one for each volume.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "local"]],
        keys=[["firstfirstfirstf", "firstfirstfirstf"], ["secondsecondseco", None]],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_one_one_encrypted_in_the_other_three_keys(
    self,
):
    """Check ClickHouse supports policy with two volumes, one contains two encrypted disks,
    the other contains one encrypted disk with two keys, one for each volume.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "local"]],
        keys=[["firstfirstfirstf", "secondsecondseco"], ["thirdthirdthirdt", None]],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_one_two_unencrypted_in_the_other_one_key(
    self,
):
    """Check ClickHouse supports policy with two volumes, one contains two encrypted disks,
    the other contains two unencrypted disks with one key.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["local", "local"]],
        keys=[["firstfirstfirstf", "firstfirstfirstf"], [None, None]],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_two_encrypted_disk_in_one_two_unencrypted_in_the_other_two_keys(
    self,
):
    """Check ClickHouse supports policy with two volumes, one contains two encrypted disks,
    the other contains two unencrypted disks with two keys.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["local", "local"]],
        keys=[["firstfirstfirstf", "secondsecondseco"], [None, None]],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_two_volumes_one_encrypted_disk_in_one_two_unencrypted_in_the_other(
    self,
):
    """Check ClickHouse supports policy with two volumes, one contains one encrypted disk,
    the other contains two unencrypted disks.
    """
    multi_volume_policy_using_move_factor(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "local"], ["local", "local"]],
        keys=[["firstfirstfirstf", None], [None, None]],
        number_of_inserts=100,
    )


@TestScenario
def multi_volume_policy_one_encrypted_disk_ttl(self):
    """Check ClickHouse supports TTL move and delete for policy with two volumes,
    one contains one encrypted disk, the other contains two unencrypted disks.
    """
    multi_volume_policy_using_ttl(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "local"], ["local", "local"]],
        keys=[["firstfirstfirstf", None], [None, None]],
    )


@TestScenario
def multi_volume_policy_two_encrypted_disks_in_different_policies_ttl(self):
    """Check ClickHouse supports TTL move and delete for policy with two volumes,
    that contain one encrypted disk.
    """
    multi_volume_policy_using_ttl(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "local"], ["local", "encrypted"]],
        keys=[["firstfirstfirstf", None], [None, "secondsecondseco"]],
    )


@TestScenario
def multi_volume_policy_two_encrypted_disks_in_one_policy_ttl(self):
    """Check ClickHouse supports TTL move and delete for policy with two volumes,
    one contains two encrypted disk, the other contains two unencrypted disks.
    """
    multi_volume_policy_using_ttl(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["local", "local"]],
        keys=[["firstfirstfirstf", "secondsecondseco"], [None, None]],
    )


@TestScenario
def multi_volume_policy_three_encrypted_disks_ttl(self):
    """Check ClickHouse supports TTL move and delete for policy with two volumes,
    that contain three encrypted disks.
    """
    multi_volume_policy_using_ttl(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "local"]],
        keys=[["firstfirstfirstf", "secondsecondseco"], ["thirdthirdthirdt", None]],
    )


@TestScenario
def multi_volume_policy_four_encrypted_disks_ttl(self):
    """Check ClickHouse supports TTL move and delete for policy with two volumes,
    that contain three encrypted disks.
    """
    multi_volume_policy_using_ttl(
        number_of_volumes=2,
        numbers_of_disks=[2, 2],
        disks_types=[["encrypted", "encrypted"], ["encrypted", "encrypted"]],
        keys=[
            ["firstfirstfirstf", "secondsecondseco"],
            ["thirdthirdthirdt", "fourthfourthfour"],
        ],
    )


@TestFeature
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_TieredStorage("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_MultiVolumePolicies("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Operations_TableTTL("1.0"),
)
@Name("multi volume policy")
def feature(self, node="clickhouse1"):
    """Check that clickhouse supports having encrypted disk when policy contains
    one volume which have one or more encrypted disks.
    """
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
