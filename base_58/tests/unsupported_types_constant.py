from base_58.tests.steps import *


@TestScenario
def unsupported_types(self, constant_type="Int64", nullable=False, node=None):
    """Check that clickhouse base58 functions returns an error if constant data type is not supported."""
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

    if constant_type == "array":
        with When(f"I check base58Encode support {constant_type}"):
            r = node.query(
                f"SELECT base58Encode({to_nullable_start}{constant_type}(100{extra_args}){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()
        with When(f"I check base58Decode support {constant_type}"):
            r = node.query(
                f"SELECT base58Decode({to_nullable_start}{constant_type}(123{extra_args}){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()
        with When(f"I check base58Encode support {constant_type}"):
            r = node.query(
                f"SELECT base58Encode({to_nullable_start}{constant_type}('100'{extra_args}){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()
        with When(f"I check base58Decode support {constant_type}"):
            r = node.query(
                f"SELECT base58Decode({to_nullable_start}{constant_type}('123'{extra_args}){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()

    elif constant_type == "FixedString":
        with When(f"I check base58Encode support {constant_type}"):
            r = node.query(
                f"SELECT base58Encode({to_nullable_start}to{constant_type}('100'{extra_args}){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()
        with When(f"I check base58Decode support {constant_type}"):
            r = node.query(
                f"SELECT base58Decode({to_nullable_start}to{constant_type}('123'{extra_args}){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()

    elif constant_type == "UUID":
        with When(f"I check base58Encode support {constant_type}"):
            r = node.query(
                f"SELECT base58Encode({to_nullable_start}generateUUIDv4(){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()
        with When(f"I check base58Decode support {constant_type}"):
            r = node.query(
                f"SELECT base58Decode({to_nullable_start}generateUUIDv4(){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()

    elif constant_type == "Map":
        with When(f"I check base58Encode support {constant_type}"):
            r = node.query(
                f"SELECT base58Encode({to_nullable_start}map('100', '100'){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()
        with When(f"I check base58Decode support {constant_type}"):
            r = node.query(
                f"SELECT base58Decode({to_nullable_start}map('100', '100'){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()

    elif constant_type == "Tuple":
        with When(f"I check base58Encode support {constant_type}"):
            r = node.query(
                f"SELECT base58Encode({to_nullable_start}tuple('100', '100'){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()
        with When(f"I check base58Decode support {constant_type}"):
            r = node.query(
                f"SELECT base58Decode({to_nullable_start}tuple('100', '100'){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()
    else:
        with When(f"I check base58Encode support {constant_type}"):
            r = node.query(
                f"SELECT base58Encode({to_nullable_start}to{constant_type}(100{extra_args}){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()
        with When(f"I check base58Decode support {constant_type}"):
            r = node.query(
                f"SELECT base58Decode({to_nullable_start}to{constant_type}(123{extra_args}){to_nullable_end})",
                no_checks=True,
            )
            assert r.exitcode == 43, error()


@TestModule
@Requirements(
    RQ_ClickHouse_Base58_Encode_UnsupportedDataTypes("1.0"),
    RQ_ClickHouse_Base58_Decode_UnsupportedDataTypes("1.0"),
)
@Name("unsupported types constant")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 functions returns an error if constant data type is not supported."""

    self.context.node = self.context.cluster.node(node)

    constant_types = [
        "Int8",
        "Int16",
        "Int32",
        "Int64",
        "Int128",
        "Int256",
        "Float32",
        "Float64",
        "Decimal32(4)",
        "Bool",
        "UUID",
        "Date",
        "Date32",
        "DateTime",
        "DateTime64(4)",
        "LowCardinality",
        "array",
        "FixedString(3)",
        "Map(String, String)",
        "Tuple(String)",
    ]

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
