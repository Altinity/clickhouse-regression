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


@TestOutline
def check_invalid_key_size(
    self, algorithm=None, number_of_symbols=16, policy=None, disk_path=None, node=None
):
    """Check that ClickHouse returns an error if specified key has invalid size for specified algorithm
    when the key is specified in common format.
    """

    disk_local = "/disk_local"
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    key = "firstfirstfirstffirstfirstfirstffirstfirstfirstffirstfirstfirstffirstfirstfirstffirstfirstfirstf"
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
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, message="Exception", restart=True
        )


@TestOutline
def check_hex_invalid_key_size(
    self, algorithm=None, number_of_symbols=32, policy=None, disk_path=None, node=None
):
    """Check that ClickHouse returns an error if specified key has invalid size for specified algorithm
    when the key is specified in hexadecimal format.
    """

    disk_local = "/disk_local"
    disk_path = disk_local
    if node is None:
        node = self.context.node

    with Given("I create local disk folder on the server"):
        create_directory(path=disk_local)

    key = "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
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
        add_invalid_encrypted_disk_configuration(
            entries=entries_in_this_test, message="Exception", restart=True
        )


@TestScenario
def check_invalid_key_size_AES_128_CTR(self):
    """Check that ClickHouse returns an error if key length is 17 symbols and algorithm is AES_128_CTR
    when the key is specified in common format.
    """
    check_invalid_key_size(algorithm="AES_128_CTR", number_of_symbols=17)


@TestScenario
def check_invalid_key_size_AES_192_CTR(self):
    """Check that ClickHouse returns an error if key length is 25 symbols and algorithm is AES_192_CTR
    when the key is specified in common format.
    """
    check_invalid_key_size(algorithm="AES_192_CTR", number_of_symbols=25)


@TestScenario
def check_invalid_key_size_AES_256_CTR(self):
    """Check that ClickHouse returns an error if key length is 33 symbols and algorithm is AES_256_CTR
    when the key is specified in common format.
    """
    check_invalid_key_size(algorithm="AES_256_CTR", number_of_symbols=33)


@TestScenario
def check_invalid_key_size_default(self):
    """Check that ClickHouse returns an error if key length is 17 symbols and algorithm is default
    when the key is specified in common format.
    """
    check_invalid_key_size(number_of_symbols=17)


@TestScenario
def check_invalid_key_size_AES_128_CTR(self):
    """Check that ClickHouse returns an error if key length is 15 symbols and algorithm is AES_128_CTR
    when the key is specified in common format.
    """
    check_invalid_key_size(algorithm="AES_128_CTR", number_of_symbols=15)


@TestScenario
def check_invalid_key_size_AES_192_CTR(self):
    """Check that ClickHouse returns an error if key length is 23 symbols and algorithm is AES_192_CTR
    when the key is specified in common format.
    """
    check_invalid_key_size(algorithm="AES_192_CTR", number_of_symbols=23)


@TestScenario
def check_invalid_key_size_AES_256_CTR(self):
    """Check that ClickHouse returns an error if key length is 31 symbols and algorithm is AES_256_CTR
    when the key is specified in common format.
    """
    check_invalid_key_size(algorithm="AES_256_CTR", number_of_symbols=31)


@TestScenario
def check_invalid_key_size_default(self):
    """Check that ClickHouse returns an error if key length is 15 symbols and algorithm is default
    when the key is specified in common format.
    """
    check_invalid_key_size(number_of_symbols=15)


@TestScenario
def check_hex_invalid_key_size_AES_128_CTR(self):
    """Check that ClickHouse returns an error if key length is 33 symbols and algorithm is AES_128_CTR
    when the key is specified in hexadecimal format.
    """
    check_hex_invalid_key_size(algorithm="AES_128_CTR", number_of_symbols=33)


@TestScenario
def check_hex_invalid_key_size_AES_192_CTR(self):
    """Check that ClickHouse returns an error if key length is 49 symbols and algorithm is AES_192_CTR
    when the key is specified in hexadecimal format.
    """
    check_hex_invalid_key_size(algorithm="AES_192_CTR", number_of_symbols=49)


@TestScenario
def check_hex_invalid_key_size_AES_256_CTR(self):
    """Check that ClickHouse returns an error if key length is 65 symbols and algorithm is AES_256_CTR
    when the key is specified in hexadecimal format.
    """
    check_hex_invalid_key_size(algorithm="AES_256_CTR", number_of_symbols=65)


@TestScenario
def check_hex_invalid_key_size_default(self):
    """Check that ClickHouse returns an error if key length is 33 symbols and algorithm is default
    when the key is specified in hexadecimal format.
    """
    check_hex_invalid_key_size(number_of_symbols=33)


@TestScenario
def check_hex_invalid_key_size_AES_128_CTR(self):
    """Check that ClickHouse returns an error if key length is 31 symbols and algorithm is AES_128_CTR
    when the key is specified in hexadecimal format.
    """
    check_hex_invalid_key_size(algorithm="AES_128_CTR", number_of_symbols=31)


@TestScenario
def check_hex_invalid_key_size_AES_192_CTR(self):
    """Check that ClickHouse returns an error if key length is 47 symbols and algorithm is AES_192_CTR
    when the key is specified in hexadecimal format.
    """
    check_hex_invalid_key_size(algorithm="AES_192_CTR", number_of_symbols=47)


@TestScenario
def check_hex_invalid_key_size_AES_256_CTR(self):
    """Check that ClickHouse returns an error if key length is 63 symbols and algorithm is AES_256_CTR
    when the key is specified in hexadecimal format.
    """
    check_hex_invalid_key_size(algorithm="AES_256_CTR", number_of_symbols=63)


@TestScenario
def check_hex_invalid_key_size_default(self):
    """Check that ClickHouse returns an error if key length is 31 symbols and algorithm is default
    when the key is specified in hexadecimal format.
    """
    check_hex_invalid_key_size(number_of_symbols=31)


@TestFeature
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Invalid_Size("1.0"))
@Name("invalid key size")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse returns an error if specified key has invalid size for specified algorithm."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
