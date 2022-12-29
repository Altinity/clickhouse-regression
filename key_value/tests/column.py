from key_value.tests.steps import *


@TestOutline
def column_input(self, input, output, params, node=None):
    """Check that clickhouse extractKeyValuePairs function supports column input."""

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given("I have a table"):
        create_partitioned_table(table_name=table_name, extra_table_col=",y String")

    with When("I insert values into the table"):
        insert(table_name=table_name, x=input, y=output.replace("'", "\\'"))

    with Then("I check extractKeyValuePairs function returns correct value"):
        r = node.query(f"""select toString(extractKeyValuePairs(x, {params})), y from {table_name}""", use_file=True)
        r = node.query(f"""select toString(extractKeyValuePairs(x, {params})) == y from {table_name}""", use_file=True)
        assert r.output == '1', error()


@TestModule
@Name("column")
def module(self, node="clickhouse1"):
    """Check that clickhouse extractKeyValuePairs function support column input."""

    self.context.node = self.context.cluster.node(node)

    key_format_feature(scenario=column_input)
    value_format_feature(scenario=column_input)
    input_format(scenario=column_input)
    specifying_special_symbols(scenario=column_input)