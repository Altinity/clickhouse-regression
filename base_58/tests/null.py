from base_58.tests.steps import *


@TestScenario
@Requirements(RQ_ClickHouse_Base58_Null("1.0"))
def null(self, node=None):
    """Check that clickhouse base58 functions return Null with Null input."""

    if node is None:
        node = self.context.node

    with When("I check base58Encode(NULL) is NULL"):
        r = node.query(
            f"SELECT base58Encode(NULL)"
        )
        encoded_string = r.output
        assert encoded_string == "\\N", error()

    with Then(
        "I check base58Decode(NULL) is NULL"
    ):
        r = node.query(f"SELECT base58Decode(NULL)")
        assert "\\N" == r.output, error()


@TestFeature
@Requirements()
@Name("null")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 function support null input."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
