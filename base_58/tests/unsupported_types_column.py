from base_58.tests.steps import *


@TestScenario
def unsupported_types(self, column_type="Int64", nullable=False, node=None):
    """Check that clickhouse base58 functions returns an error if column data type is not supported."""
    if node is None:
        node = self.context.node

    table_name_random = f"table_{getuid()}_random"
    table_name = f"table_{getuid()}"

    with When("I create a table with random engine"):
        create_partitioned_table(
            table_name=table_name_random,
            engine="GenerateRandom(1, 10, 10)",
            order="",
            partition="",
            column_type="Int64",
        )

    with When("I add toNullable if it is needed"):
        if nullable:
            nullable_start = "Nullable("
            nullable_end = ")"
        else:
            nullable_start = ""
            nullable_end = ""

    with When("I create a table with MergeTree engine"):
        create_partitioned_table(
            table_name=table_name,
            column_type=nullable_start + column_type + nullable_end,
            partition="",
        )

    if column_type == "UUID":
        with When("I insert data into the MergeTree table"):
            node.query(
                f"INSERT INTO {table_name} SELECT id, generateUUIDv4() from {table_name_random} LIMIT 10"
            )
            if nullable:
                node.query(f"INSERT INTO {table_name} VALUES (100, null)")
    elif column_type == "Array(String)":
        node.query(
            f"INSERT INTO {table_name} SELECT id, [toString(x%100)] from {table_name_random} LIMIT 10"
        )
    elif "Date" in column_type:
        node.query(
            f"INSERT INTO {table_name} SELECT id, '2019-01-01' from {table_name_random} LIMIT 10"
        )
        if nullable:
            node.query(f"INSERT INTO {table_name} VALUES (100, null)")
    elif column_type == "FixedString(3)":
        node.query(
            f"INSERT INTO {table_name} SELECT id, toString(x%100) from {table_name_random} LIMIT 10"
        )
        if nullable:
            node.query(f"INSERT INTO {table_name} VALUES (100, null)")
    elif column_type == "Map(String, String)":
        node.query(
            f"INSERT INTO {table_name} SELECT id, map(toString(x%100),toString(x%100)) from {table_name_random} LIMIT 10"
        )
        if nullable:
            node.query(f"INSERT INTO {table_name} VALUES (100, null)")
    elif column_type == "Tuple(String)":
        node.query(
            f"INSERT INTO {table_name} SELECT id, tuple(toString(x%100)) from {table_name_random} LIMIT 10"
        )
        if nullable:
            node.query(f"INSERT INTO {table_name} VALUES (100, null)")
    else:
        with When("I insert data into the MergeTree table"):
            node.query(
                f"INSERT INTO {table_name} SELECT id, x%100 from {table_name_random} LIMIT 10"
            )
            if nullable:
                node.query(f"INSERT INTO {table_name} VALUES (100, null)")

    with When(
        "I check base58Encode function returns an error if data type is not supported"
    ):
        r = node.query(f"SELECT id, base58Encode(x) FROM {table_name}", no_checks=True)
        assert r.exitcode in (43, 27)

    with When(
        "I check base58Decode function returns an error if data type is not supported"
    ):
        r = node.query(f"SELECT id, base58Decode(x) FROM {table_name}", no_checks=True)
        assert r.exitcode in (43, 27)


@TestModule
@Requirements()
@Name("unsupported types column")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 functions returns an error if constant data type is not supported."""

    self.context.node = self.context.cluster.node(node)

    column_types = [
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
        "Array(String)",
        "FixedString(3)",
        "Map(String, String)",
        "Tuple(String)",
    ]

    for nullable in [True, False]:
        for column_type in column_types:
            if nullable and not (
                column_type
                in (
                    "Array(String)",
                    "FixedString(3)",
                    "Tuple(String)",
                    "Map(String, String)",
                )
            ):
                with Feature(f"Nullable({column_type})"):
                    for scenario in loads(current_module(), Scenario):
                        scenario(column_type=column_type, nullable=nullable)
            elif not nullable:
                with Feature(f"{column_type}"):
                    for scenario in loads(current_module(), Scenario):
                        scenario(column_type=column_type, nullable=nullable)
