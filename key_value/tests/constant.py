from key_value.tests.steps import *
from key_value.tests.checks import *


@TestOutline
def constant_input(self, input, output, params, node=None, function=None):
    """Check that ClickHouse's extractKeyValuePairs function support constant input string."""

    if node is None:
        node = self.context.node

    with Then(
        "I check extractKeyValuePairs function returns correct value for constant input"
    ):
        check_constant_input(
            input=input, output=output, params=params, function=function
        )


@TestOutline
def constant_input_alias(self, input, output, params, node=None, function=None):
    """Check that ClickHouse's extractKeyValuePairs function support constant input string with alias."""

    if node is None:
        node = self.context.node

    with Then(
        "I check extractKeyValuePairs function returns correct value for constant input"
    ):
        check_constant_input(
            input=input, output=output, params=params, function=function, alias=True
        )


@TestFeature
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Constant("1.0"),
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_InputDataSource_Alias("1.0"),
)
@Name("constant")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse's extractKeyValuePairs function support constant input string."""

    self.context.node = self.context.cluster.node(node)

    for check in checks:
        Feature(test=check, format_name=True)(scenario=constant_input)
