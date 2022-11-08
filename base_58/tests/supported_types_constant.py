from base_58.tests.steps import *


@TestScenario
def supported_types(self, constant_type="String", nullable=False, node=None):
    """Check that clickhouse base58 functions support constant String types."""
    if node is None:
        node = self.context.node

    with When("I change constant type if it has arguments"):
        if "(" in constant_type:
            extra_args = (
                ","
                + constant_type[constant_type.find("(") + 1 : constant_type.find(")")]
            )
            constant_type = constant_type[0 : constant_type.find("(")]
        else:
            extra_args = ""

    with When("I add toNullable if it is needed"):
        if nullable:
            to_nullable_start = "toNullable("
            to_nullable_end = ")"
        else:
            to_nullable_start = ""
            to_nullable_end = ""

    with When(f"I check base58Encode support {constant_type}"):
        r = node.query(
            f"SELECT base58Encode({to_nullable_start}to{constant_type}('100'{extra_args}){to_nullable_end})"
        )
    with When(f"I check base58Decode support {constant_type}"):
        r = node.query(
            f"SELECT base58Decode({to_nullable_start}to{constant_type}('123'{extra_args}){to_nullable_end})"
        )


@TestModule
@Requirements(RQ_ClickHouse_Base58_Encode_SupportedDataTypes("1.0"),
              RQ_ClickHouse_Base58_Decode_SupportedDataTypes("1.0"))
@Name("supported types constant")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 functions support constant String types."""

    self.context.node = self.context.cluster.node(node)

    constant_types = ["String", "LowCardinality"]

    for nullable in [True, False]:
        for constant_type in constant_types:
            if nullable:
                with Feature(f"Nullable({constant_type})"):
                    for scenario in loads(current_module(), Scenario):
                        scenario(constant_type=constant_type, nullable=nullable)
            else:
                with Feature(f"{constant_type}"):
                    for scenario in loads(current_module(), Scenario):
                        scenario(constant_type=constant_type, nullable=nullable)
