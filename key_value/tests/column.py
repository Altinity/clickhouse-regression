from key_value.tests.steps import *


@TestScenario
def conlumn_input(self, node=None):
    """Check that clickhouse extractKeyValuePairs function support column input."""

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_partitioned_table(table_name=table_name, extra_table_col=",y String")

    with When("I insert values into the table"):
        with open("input_strings_for_column") as input_strings:
            with open("output_strings") as output_strings:
                for input_string in input_strings:
                    output_string = output_strings.readline()
                    insert(table_name=table_name, x=input_string[0:-1], y=output_string[0:-1])

    with Then("I check parseKeyValue function returns correct value"):
        hash_expected_result = node.query(f"SELECT sum(cityhash(y)) from {table_name}")
        hash_result = node.query(
            f"SELECT sum(cityhash(extractKeyValuePairs(x))) from {table_name}"
        )
        assert hash_expected_result == hash_result, error()


@TestModule
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_Noise("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Parsing_RecognizedKeyValuePairs("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Key_Format("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Value_Format("1.0"),
)
@Name("column")
def feature(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function support column input."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
