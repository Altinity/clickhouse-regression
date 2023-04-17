from key_value.tests.steps import *


@TestScenario
def supported_types(self, constant_type="String", nullable=False, node=None):
    """Check that ClickHouse's extractKeyValuePairs function supports String types."""
    if node is None:
        node = self.context.node

    with When("I change constant type if the type has arguments"):
        if "(" in constant_type:
            extra_args = (
                ","
                + constant_type[constant_type.find("(") + 1 : constant_type.find(")")]
            )
            constant_type = constant_type[0 : constant_type.find("(")]
        else:
            extra_args = ""

    with And("I add toNullable if it is needed"):
        if nullable:
            to_nullable_start = "toNullable("
            to_nullable_end = ")"
        else:
            to_nullable_start = ""
            to_nullable_end = ""

    with Then(f"I check extractKeyValuePairs support {constant_type}"):
        r = node.query(
            f"SELECT extractKeyValuePairs({to_nullable_start}to{constant_type}('100'{extra_args}){to_nullable_end})"
        )

    with And(f"I check extractKeyValuePairs support {constant_type}"):
        r = node.query(
            f"SELECT extractKeyValuePairs({to_nullable_start}to{constant_type}('123'{extra_args}){to_nullable_end})"
        )


@TestModule
@Requirements(
    RQ_SRS_033_ClickHouse_ExtractKeyValuePairs_Function_SupportedDataTypes("1.0")
)
@Name("supported types")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse's extractKeyValuePairs function supports String types."""

    self.context.node = self.context.cluster.node(node)

    constant_types = ["String", "LowCardinality", "FixedString(3)"]

    for constant_type in constant_types:
        with Feature(f"{constant_type}"):
            for scenario in loads(current_module(), Scenario):
                scenario(constant_type=constant_type, nullable=False)
