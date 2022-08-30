from testflows.asserts import values as That
from testflows.core.name import basename
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *
from testflows.asserts import snapshot, error

entries = {
    "storage_configuration": {
        "disks": [
            {"local": {"path": "/disk_local/"}},
            {
                "encrypted_local": {
                    "type": "encrypted",
                    "disk": "local",
                    "path": "encrypted/",
                }
            },
        ],
        "policies": {
            "local_encrypted": {
                "volumes": {"encrypted_disk": {"disk": "encrypted_local"}}
            }
        },
    }
}

expected_output = '{"Id":1,"Value":"hello"}\n{"Id":2,"Value":"there"}'


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Default("1.0"))
def check_default_algorithm(self, policy=None, disk_path=None, node=None):
    """Check that ClickHouse uses AES_128_CTR as the default algorithm for disk level encryption."""
    disk_local = "/disk_local"
    disk_path = disk_local

    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    key = "firstfirstfirstffirstfirstfirstf"
    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = key[0:16]

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    policy = "local_encrypted"

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy)

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with Then("I change algorithm"):
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "algorithm"
        ] = "AES_128_CTR"
        add_encrypted_disk_configuration(
            entries=entries_in_this_test, modify=True, restart=True
        )

    with And("I expect data is not changed after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with Then("I expect all files has ENC header before restart"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with And("I restart server"):
        node.restart()

    with Then("I expect all files has ENC header after restart"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with And("I expect data is not changed after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestOutline
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Conflict("1.0"))
def check_changing_encryption_algorithm(
    self,
    first_algorithm=None,
    number_of_symbols_1=16,
    second_algorithm=None,
    number_of_symbols_2=16,
    policy=None,
    disk_path=None,
    node=None,
):
    """Check that data encrypted with one algorithm can't be decrypted
    with another when the key is specified in common format.
    """
    disk_local = "/disk_local"
    disk_path = disk_local
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    key = "firstfirstfirstffirstfirstfirstf"
    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = key[0:number_of_symbols_1]
        if first_algorithm is not None:
            entries_in_this_test["storage_configuration"]["disks"][1][
                "encrypted_local"
            ]["algorithm"] = first_algorithm

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    policy = "local_encrypted"

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy)

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with Then("I try to change algorithm"):
        wrong_entries = copy.deepcopy(entries_in_this_test)
        wrong_entries["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = key[0:number_of_symbols_2]
        if second_algorithm is not None:
            wrong_entries["storage_configuration"]["disks"][1]["encrypted_local"][
                "algorithm"
            ] = second_algorithm
        else:
            del wrong_entries["storage_configuration"]["disks"][1]["encrypted_local"][
                "algorithm"
            ]

    with And("I add storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            entries=wrong_entries,
            recover_entries=entries_in_this_test,
            message="Exception",
            restart=True,
        )

    with Then("I expect all files has ENC header before restart"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with And("I restart server"):
        node.restart()

    with Then("I expect all files has ENC header after restart"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with And("I expect data is not changed after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestOutline
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Conflict("1.0"))
def check_hex_changing_encryption_algorithm(
    self,
    first_algorithm=None,
    number_of_symbols_1=16,
    second_algorithm=None,
    number_of_symbols_2=16,
    policy=None,
    disk_path=None,
    node=None,
):
    """Check that data encrypted with one algorithm can't be decrypted
    with another when the key is specified in hexadecimal format.
    """
    disk_local = "/disk_local"
    disk_path = disk_local
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    key = "0000000000000000000000000000000000000000000000000000000000000000"
    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key_hex"
        ] = key[0:number_of_symbols_1]
        if first_algorithm is not None:
            entries_in_this_test["storage_configuration"]["disks"][1][
                "encrypted_local"
            ]["algorithm"] = first_algorithm

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    policy = "local_encrypted"

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy)

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with Then("I try to change algorithm"):
        wrong_entries = copy.deepcopy(entries_in_this_test)
        wrong_entries["storage_configuration"]["disks"][1]["encrypted_local"][
            "key_hex"
        ] = key[0:number_of_symbols_2]
        if second_algorithm is not None:
            wrong_entries["storage_configuration"]["disks"][1]["encrypted_local"][
                "algorithm"
            ] = second_algorithm
        else:
            del wrong_entries["storage_configuration"]["disks"][1]["encrypted_local"][
                "algorithm"
            ]

    with And("I add storage configuration that uses encrypted disk"):
        add_invalid_encrypted_disk_configuration(
            entries=wrong_entries,
            recover_entries=entries_in_this_test,
            message="Exception",
            restart=True,
        )

    with Then("I expect all files has ENC header before restart"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with And("I restart server"):
        node.restart()

    with Then("I expect all files has ENC header after restart"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with And("I expect data is not changed after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestOutline
def check_encryption_algorithms(
    self, algorithm=None, number_of_symbols=16, policy=None, disk_path=None, node=None
):
    """Check that ClickHouse can encrypt data with different algorithms
    when the key is specified in common format.
    """
    disk_local = "/disk_local"
    disk_path = disk_local
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    key = "firstfirstfirstffirstfirstfirstf"
    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key"
        ] = key[0:number_of_symbols]
        if algorithm is not None:
            entries_in_this_test["storage_configuration"]["disks"][1][
                "encrypted_local"
            ]["algorithm"] = algorithm

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    policy = "local_encrypted"

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy)

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with Then("I expect all files has ENC header before restart"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with And("I restart server"):
        node.restart()

    with Then("I expect all files has ENC header after restart"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with And("I expect data is not changed after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestOutline
def check_hex_encryption_algorithms(
    self, algorithm=None, number_of_symbols=32, policy=None, disk_path=None, node=None
):
    """Check that ClickHouse can encrypt data with different algorithms
    when key specified in hexadecimal format.
    """
    disk_local = "/disk_local"
    disk_path = disk_local
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    key = "0000000000000000000000000000000000000000000000000000000000000000"
    with And("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        entries_in_this_test["storage_configuration"]["disks"][1]["encrypted_local"][
            "key_hex"
        ] = key[0:number_of_symbols]
        if algorithm is not None:
            entries_in_this_test["storage_configuration"]["disks"][1][
                "encrypted_local"
            ]["algorithm"] = algorithm

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)

    policy = "local_encrypted"

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy)

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()

    with Then("I expect all files has ENC header before restart"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with And("I restart server"):
        node.restart()

    with Then("I expect all files has ENC header after restart"):
        check_if_all_files_are_encrypted(disk_path=disk_path)

    with And("I expect data is not changed after restart"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == expected_output, error()


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_128_CTR("1.0"))
def check_hex_encryption_AES_128_CTR(self):
    """Check that ClickHouse supports AES_128_CTR encryption algorithm
    when the key is specified in hexadecimal format.
    """
    check_hex_encryption_algorithms(algorithm="AES_128_CTR", number_of_symbols=32)


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_192_CTR("1.0"))
def check_hex_encryption_AES_192_CTR(self):
    """Check that ClickHouse supports AES_192_CTR encryption algorithm
    when the key is specified in hexadecimal format.
    """
    check_hex_encryption_algorithms(algorithm="AES_192_CTR", number_of_symbols=48)


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_256_CTR("1.0"))
def check_hex_encryption_AES_256_CTR(self):
    """Check that ClickHouse supports AES_256_CTR encryption algorithm
    when the key is specified in hexadecimal format.
    """
    check_hex_encryption_algorithms(algorithm="AES_256_CTR", number_of_symbols=64)


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_128_CTR("1.0"))
def check_encryption_AES_128_CTR(self):
    """Check that ClickHouse supports AES_128_CTR encryption algorithm
    when the key is specified in common format.
    """
    check_encryption_algorithms(algorithm="AES_128_CTR", number_of_symbols=16)


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_192_CTR("1.0"))
def check_encryption_AES_192_CTR(self):
    """Check that ClickHouse supports AES_192_CTR encryption algorithm
    when the key is specified in common format.
    """
    check_encryption_algorithms(algorithm="AES_192_CTR", number_of_symbols=24)


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_AES_256_CTR("1.0"))
def check_encryption_AES_256_CTR(self):
    """Check that ClickHouse supports AES_256_CTR encryption algorithm
    when the key is specified in common format.
    """
    check_encryption_algorithms(algorithm="AES_256_CTR", number_of_symbols=32)


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Conflict("1.0"))
def check_change_AES_256_CTR_AES_192_CTR(self):
    """Check that ClickHouse returns an error if encryption algorithm is changed
    from AES_256_CTR to AES_192_CTR when the key is specified in common format.
    """
    check_changing_encryption_algorithm(
        first_algorithm="AES_256_CTR",
        number_of_symbols_1=32,
        second_algorithm="AES_192_CTR",
        number_of_symbols_2=24,
    )


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Conflict("1.0"))
def check_change_AES_256_CTR_to_default(self):
    """Check that ClickHouse returns an error if encryption algorithm is changed
    from AES_256_CTR to default when the key is specified in common format.
    """
    check_changing_encryption_algorithm(
        first_algorithm="AES_256_CTR",
        number_of_symbols_1=32,
        second_algorithm=None,
        number_of_symbols_2=16,
    )


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Conflict("1.0"))
def check_change_AES_128_CTR_to_AES_192_CTR(self):
    """Check that ClickHouse returns an error if encryption algorithm is changed
    from AES_128_CTR to AES_192_CTR when the key is specified in common format.
    """
    check_changing_encryption_algorithm(
        first_algorithm="AES_128_CTR",
        number_of_symbols_1=16,
        second_algorithm="AES_192_CTR",
        number_of_symbols_2=24,
    )


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Conflict("1.0"))
def check_hex_change_AES_256_CTR_to_AES_192_CTR(self):
    """Check that ClickHouse returns an error if encryption algorithm is changed
    from AES_256_CTR to AES_192_CTR when the key is specified in hexadecimal format.
    """
    check_hex_changing_encryption_algorithm(
        first_algorithm="AES_256_CTR",
        number_of_symbols_1=64,
        second_algorithm="AES_192_CTR",
        number_of_symbols_2=48,
    )


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Conflict("1.0"))
def check_hex_change_AES_256_CTR_to_default(self):
    """Check that ClickHouse returns an error if encryption algorithm is changed
    from AES_256_CTR to default when the key is specified in hexadecimal format.
    """
    check_hex_changing_encryption_algorithm(
        first_algorithm="AES_256_CTR",
        number_of_symbols_1=64,
        second_algorithm=None,
        number_of_symbols_2=32,
    )


@TestScenario
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Algorithm_Conflict("1.0"))
def check_hex_change_AES_128_CTR_to_AES_192_CTR(self):
    """Check that ClickHouse returns an error if encryption algorithm is changed
    from AES_128_CTR to AES_192_CTR when the key is specified in hexadecimal format.
    """
    check_hex_changing_encryption_algorithm(
        first_algorithm="AES_128_CTR",
        number_of_symbols_1=32,
        second_algorithm="AES_192_CTR",
        number_of_symbols_2=48,
    )


@TestFeature
@Name("encryption algorithms")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse can encrypt data with different algorithms,
    and that data encrypted with one algorithm can't be decrypted with another.
    """
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
