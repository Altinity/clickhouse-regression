from helpers.common import *
from helpers.cluster import *
from testflows.combinatorics import product


@TestSketch(Scenario)
def floats(self, client=None):
    """Check addition of floats using the plus() function inside the SELECT statement"""
    if client is None:
        client = self.context.client

    sign = ["-", "+", ""]
    value = [
        "inf",
        "nan",
        "0.0",
        "0.1",
        "123456.7",
        "101.7654",
        "3.1415926535897932384626433832795028841971693993751058209749445923078164062",
        "1.1",
        str(1 / 3),
        "1.7976931348623157e+308",
        "2.2250738585072014e-308",
    ]

    a = either(*sign, i="sign") + either(*value, i="value")
    b = either(*sign, i="sign") + either(*value, i="value")
    expected = float(a) + float(b)
    r = client.query(f"SELECT {a} + {b}").output
    assert str(float(r[0][0])) == str(expected), error()


@TestFeature
@Name("plus")
def feature(self, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)
    bash_tools = self.context.cluster.node("bash-tools")

    with bash_tools.client(client_args={"host": node}) as client:
        self.context.client = client
        for scenario in loads(current_module(), Scenario):
            scenario()
