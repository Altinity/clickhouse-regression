import os
import textwrap

from extended_precision_data_types.requirements import *
from extended_precision_data_types.common import *

funcs = [
    ("plus", "2"),
    ("minus", "0"),
    ("multiply", "1"),
    ("divide", "1"),
    ("intDiv", "1"),
    ("intDivOrZero", "1"),
    ("modulo", "0"),
    ("moduloOrZero", "0"),
    ("negate", "-1"),
    ("abs", "1"),
    ("gcd", "1"),
    ("lcm", "1"),
]

Examples_list = [
    tuple(list(func) + list(data_type) + [Name(f"{func[0]} - {data_type[0]}")])
    for func in funcs
    for data_type in data_types
]
Examples_dec_list = [
    tuple(list(func) + [Name(f"{func[0]} - Decimal256")]) for func in funcs
]


@TestOutline
@Examples("arithmetic_func expected_result int_type min max", Examples_list)
def inline_check(self, arithmetic_func, expected_result, int_type, min, max, node=None):
    """Check that arithmetic functions work using inline tests with Int128, UInt128, Int256, and UInt256."""

    if node is None:
        node = self.context.node

    if arithmetic_func == "divide":
        skip("divide is not supported for int types")

    if arithmetic_func in ["negate", "abs"]:
        with When(f"I check {arithmetic_func} with {int_type}"):
            output = node.query(
                f"SELECT {arithmetic_func}(to{int_type}(1)) FORMAT TabSeparated"
            ).output
            assert output == expected_result, error()

        with When(f"I check {arithmetic_func} with {int_type} max and min value"):
            execute_query(
                f"""
                SELECT {arithmetic_func}(to{int_type}(\'{max}\')), {arithmetic_func}(to{int_type}(\'{min}\'))
                """
            )

    else:
        with When(f"I check {arithmetic_func} with {int_type}"):
            output = node.query(
                f"SELECT {arithmetic_func}(to{int_type}(1), to{int_type}(1)) FORMAT TabSeparated"
            ).output
            assert output == expected_result, error()

        if arithmetic_func in ["gcd", "lcm"]:
            if int_type in ["UInt128", "UInt256"]:
                exitcode = 153
            else:
                exitcode = 151

            with When(f"I check {arithmetic_func} with {int_type} max and min value"):
                node.query(
                    f"SELECT {arithmetic_func}(to{int_type}('{max}'), to{int_type}(1)), {arithmetic_func}(to{int_type}('{min}'), to{int_type}(1)) FORMAT TabSeparated",
                    exitcode=exitcode,
                    message="Exception:",
                )

        else:
            with When(f"I check {arithmetic_func} with {int_type} max and min value"):
                execute_query(
                    f"""
                    SELECT round({arithmetic_func}(to{int_type}(\'{max}\'), to{int_type}(1)), {rounding_precision}), round({arithmetic_func}(to{int_type}(\'{min}\'), to{int_type}(1)), {rounding_precision})
                    """
                )


@TestOutline
@Examples("arithmetic_func expected_result int_type min max", Examples_list)
def table_check(self, arithmetic_func, expected_result, int_type, min, max, node=None):
    """Check that arithmetic functions work using tables with Int128, UInt128, Int256, and UInt256."""

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    if arithmetic_func == "divide":
        skip("divide is not supported for int types")

    with Given(f"I have a table"):
        table(name=table_name, data_type=int_type)

    if arithmetic_func in ["negate", "abs"]:
        for value in [1, min, max]:
            with When(
                f"I insert {arithmetic_func} with {int_type} {value} into the table"
            ):
                node.query(
                    f"INSERT INTO {table_name} SELECT {arithmetic_func}(to{int_type}('{value}')) FORMAT TabSeparated"
                )

        with Then(f"I check the table output of {arithmetic_func} with {int_type}"):
            execute_query(
                f"""
                SELECT * FROM {table_name} ORDER BY a ASC
                """
            )

    else:
        with When(f"I insert {arithmetic_func} with {int_type} into the table"):
            node.query(
                f"INSERT INTO {table_name} SELECT round({arithmetic_func}(to{int_type}(1), to{int_type}(1)), {rounding_precision}) FORMAT TabSeparated"
            )

        with Then("I check that the output matches the expected value"):
            output = node.query(
                f"SELECT * FROM {table_name} FORMAT TabSeparated"
            ).output
            assert output == expected_result, error()

        if arithmetic_func in ["gcd", "lcm"]:
            if int_type in ["UInt128", "UInt256"]:
                with When(
                    f"I insert {arithmetic_func} with {int_type} {min} into the table"
                ):
                    node.query(
                        f"INSERT INTO {table_name} SELECT {arithmetic_func}(to{int_type}('{min}'), to{int_type}(1)) FORMAT TabSeparated",
                        exitcode=153,
                        message="Exception:",
                    )

                with And(
                    f"I insert {arithmetic_func} with {int_type} {max} into the table"
                ):
                    node.query(
                        f"INSERT INTO {table_name} SELECT {arithmetic_func}(to{int_type}('{max}'), to{int_type}(1)) FORMAT TabSeparated"
                    )

            else:
                for value in [min, max]:
                    with When(
                        f"I insert {arithmetic_func} with {int_type} {value} into the table"
                    ):
                        node.query(
                            f"INSERT INTO {table_name} SELECT {arithmetic_func}(to{int_type}('{value}'), to{int_type}(1)) FORMAT TabSeparated",
                            exitcode=151,
                            message="Exception:",
                        )

        else:
            for value in [min, max]:
                with When(
                    f"I insert {arithmetic_func} with {int_type} {value} into the table"
                ):
                    node.query(
                        f"INSERT INTO {table_name} SELECT round({arithmetic_func}(to{int_type}('{value}'), to{int_type}(1)), {rounding_precision}) FORMAT TabSeparated"
                    )

        with Then(f"I check the table output of {arithmetic_func} with {int_type}"):
            execute_query(
                f"""
                SELECT * FROM {table_name} ORDER BY a ASC
                """
            )


@TestOutline
@Examples("arithmetic_func expected_result", Examples_dec_list)
def inline_check_dec(self, arithmetic_func, expected_result, node=None):
    """Check that arithmetic functions work using inline with Decimal256."""

    if node is None:
        node = self.context.node

    if arithmetic_func in ["negate", "abs"]:
        with When(f"I check {arithmetic_func} with toDecimal256"):
            output = node.query(
                f"SELECT {arithmetic_func}(toDecimal256(1,0)) FORMAT TabSeparated"
            ).output
            assert output == expected_result, error()

    elif arithmetic_func in ["modulo", "moduloOrZero", "gcd", "lcm"]:
        with When(f"I check {arithmetic_func} with toDecimal256"):
            if arithmetic_func == "modulo" and check_clickhouse_version(">=23.8")(self):
                node.query(
                    f"SELECT {arithmetic_func}(toDecimal256(1,0), toDecimal256(1,0)) FORMAT TabSeparated",
                )
            else:
                node.query(
                    f"SELECT {arithmetic_func}(toDecimal256(1,0), toDecimal256(1,0)) FORMAT TabSeparated",
                    exitcode=43,
                    message="Exception:",
                )

    else:
        with When(f"I check {arithmetic_func} with toDecimal256"):
            output = node.query(
                f"SELECT {arithmetic_func}(toDecimal256(1,0), toDecimal256(1,0)) FORMAT TabSeparated"
            ).output
            assert output == expected_result, error()


@TestOutline
@Examples("arithmetic_func expected_result", Examples_dec_list)
def table_check_dec(self, arithmetic_func, expected_result, node=None):
    """Check that arithmetic functions work using tables with Decimal256."""

    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    if arithmetic_func in ["intDiv", "intDivOrZero"] and check_clickhouse_version(
        ">=24.2"
    ):
        data_type = "Int256"
    else:
        data_type = "Decimal256(0)"

    with Given(f"I have a table"):
        table(name=table_name, data_type=data_type)

    if arithmetic_func in ["negate", "abs"]:
        with When(f"I insert {arithmetic_func} with toDecimal256 into the table"):
            node.query(
                f"INSERT INTO {table_name} SELECT {arithmetic_func}(toDecimal256(1,0)) FORMAT TabSeparated"
            )

        with Then(f"I check the table for output of {arithmetic_func} with Decimal256"):
            execute_query(
                f"""
                SELECT * FROM {table_name} ORDER BY a ASC
                """
            )

    elif arithmetic_func in ["modulo", "moduloOrZero", "gcd", "lcm"]:
        with When(f"I check {arithmetic_func} with toDecimal256"):
            if arithmetic_func == "modulo" and check_clickhouse_version(">=23.8")(self):
                node.query(
                    f"INSERT INTO {table_name} SELECT {arithmetic_func}(toDecimal256(1,0), toDecimal256(1,0)) FORMAT TabSeparated",
                )
            else:
                node.query(
                    f"INSERT INTO {table_name} SELECT {arithmetic_func}(toDecimal256(1,0), toDecimal256(1,0)) FORMAT TabSeparated",
                    exitcode=43,
                    message="Exception:",
                )

    else:
        with When(f"I insert {arithmetic_func} with toDecimal256 into the table"):
            node.query(
                f"INSERT INTO {table_name} SELECT round({arithmetic_func}(toDecimal256(1,0), toDecimal256(1,0)), {rounding_precision}) FORMAT TabSeparated"
            )

        with Then("I check that the output matches the expected value"):
            output = node.query(
                f"SELECT * FROM {table_name} FORMAT TabSeparated"
            ).output
            assert output == expected_result, error()


@TestFeature
@Name("arithmetic")
@Requirements(
    RQ_SRS_020_ClickHouse_Extended_Precision_Arithmetic_Int_Supported("1.0"),
    RQ_SRS_020_ClickHouse_Extended_Precision_Arithmetic_Dec_Supported("1.0"),
    RQ_SRS_020_ClickHouse_Extended_Precision_Arithmetic_Dec_NotSupported("1.0"),
)
def feature(self, node="clickhouse1", mysql_node="mysql1", stress=None, parallel=None):
    """Check that arithmetic functions work with extended precision data types."""
    self.context.node = self.context.cluster.node(node)
    self.context.mysql_node = self.context.cluster.node(mysql_node)

    with allow_experimental_bigint(self.context.node):
        Scenario(run=inline_check)
        Scenario(run=table_check)
        Scenario(run=inline_check_dec)
        Scenario(run=table_check_dec)
