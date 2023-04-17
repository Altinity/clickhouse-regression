from key_value.tests.steps import *
from key_value.tests.checks import *


@TestOutline
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Array("1.0"))
def array_input(self, input, output, params, node=None, function=None):
    """Check that ClickHouse extractKeyValuePairs function support input as the value from the array."""

    if function is None:
        function = "extractKeyValuePairs"
    if node is None:
        node = self.context.node

    if params != "":
        params = ", " + params

    with Then("I check parseKeyValue function returns correct value"):
        r = node.query(f"SELECT {function}([{input}][1]{params})", use_file=True)
        assert r.output == output, error()


@TestOutline
def array_column_input(self, input, output, params, node=None, function=None):
    """Check that ClickHouse extractKeyValuePairs function support input as the value from the array from the table."""

    if function is None:
        function = "extractKeyValuePairs"
    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    if params != "":
        params = ", " + params

    with Given("I have a table"):
        create_partitioned_table(
            table_name=table_name, extra_table_col="", column_type="Array(String)"
        )

    with When("I insert values into the table and compute expected output"):
        insert(table_name=table_name, x=f"[{input}]")
        expected_output = output.replace("\\", "\\\\").replace("'", "\\'")

    with Then("I check extractKeyValuePairs function returns correct value"):
        r = node.query(
            f"""select toString({function}(x[1]{params})) from {table_name}""",
            use_file=True,
        )
        assert r.output == expected_output, error()


@TestFeature
@Name("array")
@Requirements(RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Array("1.0"))
def feature(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function support input as value from the array."""

    self.context.node = self.context.cluster.node(node)
    for check in checks:
        Feature(test=check)(scenario=array_input)
        Feature(test=check)(scenario=array_column_input)
