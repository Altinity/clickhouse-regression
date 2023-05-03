from key_value.tests.steps import *
from key_value.tests.checks import *


@TestOutline
def column_input(self, input, output, params, node=None, function=None):
    """Check that ClickHouse's extractKeyValuePairs function supports column input."""

    if function is None:
        function = "extractKeyValuePairs"

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    if params != "":
        params = ", " + params

    with Given("I have a table"):
        create_partitioned_table(table_name=table_name, extra_table_col="")

    with When("I insert values into the table and compute expected output"):
        insert(table_name=table_name, x=input)
        expected_output = output.replace("\\", "\\\\").replace("'", "\\'")

    with Then("I check extractKeyValuePairs function returns correct value"):
        r = node.query(f"""select toString({function}(x{params})) from {table_name}""")
        assert r.output == expected_output, error()


@TestOutline
def column_input_alias(self, input, output, params, node=None, function=None):
    """Check that ClickHouse's extractKeyValuePairs function supports column input with alias."""

    if function is None:
        function = "extractKeyValuePairs"

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    if params != "":
        params = ", " + params

    with Given("I have a table"):
        create_partitioned_table(table_name=table_name, extra_table_col="")

    with When("I insert values into the table and compute expected output"):
        insert(table_name=table_name, x=input)
        expected_output = output.replace("\\", "\\\\").replace("'", "\\'")

    with Then("I check extractKeyValuePairs function returns correct value"):
        r = node.query(
            f"""with x as q select toString({function}(q{params})) from {table_name}"""
        )
        assert r.output == expected_output, error()


@TestFeature
@Name("column")
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Column("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Alias("1.0"),
)
def feature(self, node="clickhouse1"):
    """Check that ClickHouse's extractKeyValuePairs function support column input."""

    self.context.node = self.context.cluster.node(node)

    for check in checks:
        with Feature(f"{check.name}"):
            Feature(test=check, name=column_input.name)(scenario=column_input)
            Feature(test=check, name=column_input_alias.name)(
                scenario=column_input_alias
            )
