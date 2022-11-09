from base_58.tests.steps import *


@TestScenario
def supported_types(self, column_type="String", nullable=False, node=None):
    """Check that clickhouse base58 functions support column String types."""
    if node is None:
        node = self.context.node

    table_name_random = f"table_{getuid()}_random"
    table_name = f"table_{getuid()}"
    table_name_e58 = f"table_{getuid()}_e58"

    with When("I create a table with random engine"):
        create_partitioned_table(
            table_name=table_name_random,
            engine="GenerateRandom(1, 10, 10)",
            order="",
            partition="",
        )

    with When("I add toNullable if it is needed"):
        if nullable:
            nullable_start = "Nullable("
            nullable_end = ")"
        else:
            nullable_start = ""
            nullable_end = ""

    with When("I create a tale with MergeTree engine"):
        create_partitioned_table(
            table_name=table_name,
            column_type=nullable_start + column_type + nullable_end,
            partition="",
        )

    with When("I insert data into the MergeTree table"):
        node.query(
            f"INSERT INTO {table_name} SELECT id, x from {table_name_random} LIMIT 10"
        )
        if nullable:
            node.query(f"INSERT INTO {table_name} VALUES (100, null)")
    with When("I create a table with MergeTree engine"):
        create_partitioned_table(
            table_name=table_name_e58,
            column_type=nullable_start + column_type + nullable_end,
            partition="",
        )

    with When("I insert data into the table with base58 encoding"):
        node.query(
            f"INSERT INTO {table_name_e58} SELECT id, base58Encode(x) FROM {table_name};"
        )

    with Then("I check data in the table can be correctly decoded"):
        r1 = node.query(
            f"SELECT id, base58Decode(x) FROM {table_name_e58} ORDER BY id, base58Decode(x)"
        )
        r2 = node.query(f"SELECT id, x FROM {table_name} ORDER BY id, x")
        assert r1.output == r2.output, error()


@TestModule
@Requirements(
    RQ_ClickHouse_Base58_Encode_SupportedDataTypes("1.0"),
    RQ_ClickHouse_Base58_Decode_SupportedDataTypes("1.0"),
)
@Name("supported types column")
def feature(self, node="clickhouse1"):
    """Check that clickhouse base58 functions support column String types."""

    self.context.node = self.context.cluster.node(node)

    column_types = ["String", "LowCardinality(String)"]

    for nullable in [True, False]:
        for column_type in column_types:
            if nullable and (column_type == "String"):
                with Feature(f"Nullable({column_type})"):
                    for scenario in loads(current_module(), Scenario):
                        scenario(column_type=column_type, nullable=nullable)
            elif not nullable:
                with Feature(f"{column_type}"):
                    for scenario in loads(current_module(), Scenario):
                        scenario(column_type=column_type, nullable=nullable)
