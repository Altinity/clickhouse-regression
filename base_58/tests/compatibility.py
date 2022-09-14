from base58 import *
from base_58.tests.steps import *


def shift(s, i):
    """Return string shifted left on i symbols."""
    return s[i % len(s) :] + s[: i % len(s)]


@TestScenario
def compatibility(self, shift_on=0, node=None):
    """Check that clickhouse base58 functions are compatible with functions from python base58 functions."""

    if node is None:
        node = self.context.node

    with When(
        "I check base58Encode function and function from base58 library return the same string"
    ):
        r = node.query(
            f"SELECT base58Encode('{shift(string_of_all_askii_symbols(), shift_on)*30}')"
        )
        encoded_string = r.output
        assert encoded_string == b58encode(
            shift(string_of_all_askii_symbols(), shift_on) * 30
        ).decode("ascii"), error()

    with Then(
        "I check base58Encode function and function from base58 library return the same string"
    ):
        r = node.query(f"SELECT base58Decode('{encoded_string}')")
        decoded_string = r.output
        assert decoded_string == b58decode(encoded_string).decode("ascii"), error()


@TestModule
@Requirements()
@Name("compatibility")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 functions are compatible with functions from python base58 functions.
    Every symbol can be the first in our string."""

    self.context.node = self.context.cluster.node(node)
    for i in range(100):
        with Feature(f"all symbols with shift on {i}"):
            for scenario in loads(current_module(), Scenario):
                scenario(shift_on=i)
