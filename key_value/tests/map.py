from key_value.tests.steps import *
from key_value.tests.checks import *


@TestOutline
def map_input(self, input, output, params, node=None, function=None):
    """Check that ClickHouse's extractKeyValuePairs function support input as the value from the map."""

    if function is None:
        function = "extractKeyValuePairs"
    if node is None:
        node = self.context.node

    if params != "":
        params = ", " + params

    with Then("I check parseKeyValue function returns correct value"):
        r = node.query(
            f"SELECT {function}(map({input}, {input})[{input}]{params})",
            use_file=True,
        )
        assert r.output == output, error()


@TestOutline
def map_column_input(self, input, output, params, node=None, function=None):
    """Check that ClickHouse's extractKeyValuePairs function support input as the value from the map from the table."""

    if function is None:
        function = "extractKeyValuePairs"
    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    if params != "":
        params = ", " + params

    with Given("I have a table"):
        create_partitioned_table(
            table_name=table_name, extra_table_col="", column_type="Map(String, String)"
        )

    with When("I insert values into the table and compute expected output"):
        insert(table_name=table_name, x=f"map({input}, {input})")
        expected_output = output.replace("\\", "\\\\").replace("'", "\\'")

    with Then("I check extractKeyValuePairs function returns correct value"):
        r = node.query(f"""select x[{input}] from {table_name}""", use_file=True)
        r = node.query(
            f"""select toString({function}(x[{input}]{params})) from {table_name}""",
            use_file=True,
        )
        assert r.output == expected_output, error()


@TestFeature
@Name("map")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Map("1.0"))
def feature(self, node="clickhouse1"):
    """Check that ClickHouse's extractKeyValuePairs function support input as value from a map."""

    self.context.node = self.context.cluster.node(node)
    for check in checks:
        with Feature(f"{check.name}"):
            Feature(test=check, name=map_input.name)(scenario=map_input)
            Feature(test=check, name=map_column_input.name)(scenario=map_column_input)