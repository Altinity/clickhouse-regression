from testflows.asserts import error
from disk_level_encryption.requirements.requirements import *
from disk_level_encryption.tests.steps import *


@TestOutline
def check_key_format(
    self, key_parameter_name, key_value, policy=None, disk_path=None, node=None
):
    """Check that specifying encryption key using
    some format is supported.
    """

    node = self.context.node if node is None else node

    with Given("I have policy that uses local encrypted disk"):
        create_policy_with_local_encrypted_disk(
            key_parameter_name=key_parameter_name, key_value=key_value
        )

    policy = self.context.policy if policy is None else policy

    with And("I create a table that uses encrypted disk"):
        table_name = create_table(policy=policy)

    with When("I insert data into the table"):
        values = "(1, 'hello'),(2, 'there')"
        insert_into_table(name=table_name, values=values)

    with Then("I expect data is successfully inserted"):
        r = node.query(f"SELECT * FROM {table_name} ORDER BY Id FORMAT JSONEachRow")
        assert r.output == '{"Id":1,"Value":"hello"}\n{"Id":2,"Value":"there"}', error()


@TestScenario
@Name("hexadecimal")
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key_Hex("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_Hex("1.0"),
)
def hexadecimal(self, node=None):
    """Check specifying key using hexadecimal via key_hex parameter."""
    check_key_format(
        key_parameter_name="key_hex",
        key_value="efadfdfdfdfdfd1234adfdfdfdfdfdfa",
        node=node,
    )


@TestScenario
@Name("utf-8")
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_UTF8("1.0"))
def utf8(self, node=None):
    """Check specifying key that contains UTF-8 characters."""
    check_key_format(key_parameter_name="key", key_value="нпуёЁВПВ", node=node)


@TestScenario
@Name("ascii")
@Requirements(RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_ASCII("1.0"))
def ascii(self, node=None):
    """Check specifying key that only contains ASCII characters."""
    check_key_format(key_parameter_name="key", key_value="{~j=:;!/()*|^%@$", node=node)


@TestScenario
@Name("special xml symbols")
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Format_SpecialXMLSymbols("1.0")
)
def special_xml_symbols(self, node=None):
    """Check specifying key that contains special XML characters."""
    check_key_format(key_parameter_name="key", key_value="aaaaaaaaaaaa'&<>", node=node)


@TestFeature
@Requirements(
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Encryption("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Key_Decryption("1.0"),
    RQ_SRS_025_ClickHouse_DiskLevelEncryption_Config_Key("1.0"),
)
@Name("key formats")
def feature(self, node="clickhouse1"):
    """Check different key formats."""
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
