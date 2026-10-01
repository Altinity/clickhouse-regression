"""Column ALTER TABLE scenarios for CAS-backed MergeTree tables."""

from testflows.asserts import error
from testflows.core import *

from helpers.common import getuid
from cas.requirements.requirements import *
from cas.tests.steps import *


@TestStep(Given)
def column_table(self, suffix, columns=ALTER_COLUMNS):
    """Create and fill an isolated table for one column ALTER scenario."""
    return create_filled_alter_table(
        table_name=f"cas_alter_column_{suffix}_{getuid()}", columns=columns
    )


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Alter("1.0"),
    RQ_SRS_048_CAS_MergeTree_Alter_Column("1.0"),
)
def add_and_drop(self):
    """Check that ADD COLUMN exposes defaults and DROP COLUMN removes the column."""

    with Given("create cas merge tree table with 10 rows"):
        table = column_table(suffix="add_drop")

    with When("add a column with a default expression"):
        add_column(table_name=table, definition="derived UInt64 DEFAULT id + 10")

    with Then("existing rows expose the default value"):
        result = self.context.node.query(
            f"SELECT sum(derived) FROM {table}"
        ).output.strip()
        assert result == "120", error(f"unexpected derived sum: {result}")

    with And("I drop the column"):
        drop_column(table_name=table, column_name="derived")

    with And("the column is absent from table metadata"):
        columns = table_columns(table_name=table)
        assert "derived" not in columns, error(str(columns))


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Column("1.0"))
def rename_and_comment(self):
    """Check that RENAME COLUMN preserves values and COMMENT COLUMN updates metadata."""
    with Given("create cas merge tree table with 10 rows"):
        table = column_table(suffix="rename_comment")
        expected = self.context.node.query(
            f"SELECT groupArray(string_column) FROM {table}"
        ).output

    with When("rename and comment a non-key column"):
        rename_column(table_name=table, old_name="string_column", new_name="payload")
        comment_column(table_name=table, column_name="payload", comment="CAS payload")

    with Then("the values and comment are preserved"):
        actual = self.context.node.query(
            f"SELECT groupArray(payload) FROM {table}"
        ).output
        assert actual == expected, error("renaming changed column values")
        metadata = column_metadata(self.context.node, table, "payload")
        assert metadata["comment"] == "CAS payload", error(str(metadata))

    with And("check renamed column is present, old column is absent"):
        columns = table_columns(table_name=table)
        assert "string_column" not in columns, error(str(columns))
        assert "payload" in columns, error(str(columns))


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Column("1.0"))
def modify_type(self):
    """Check that MODIFY COLUMN converts stored values on CAS."""
    with Given("create cas merge tree table with 10 rows"):
        table = column_table(suffix="modify_type")

    with When("widen a stored non-key column"):
        modify_column(table_name=table, definition="value Int128", mutation=True)

    with Then("the type and values are correct"):
        metadata = column_metadata(self.context.node, table, "value")
        assert metadata["type"] == "Int128", error(str(metadata))
        result = self.context.node.query(
            f"SELECT sum(value) FROM {table}"
        ).output.strip()
        assert result == "20", error(result)


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Column("1.0"))
def remove_property(self):
    """Check that MODIFY COLUMN REMOVE removes column metadata properties."""
    columns = (
        "partition_column UInt8, id UInt64, value Int64, "
        "string_column String DEFAULT 'seed' COMMENT 'temporary comment'"
    )
    with Given("create cas merge tree table with 10 rows"):
        table = column_table(suffix="remove_property", columns=columns)

    with When("remove the comment and default properties"):
        remove_column_property(
            table_name=table, column_name="string_column", property_name="COMMENT"
        )
        remove_column_property(
            table_name=table, column_name="string_column", property_name="DEFAULT"
        )

    with Then("the properties are absent"):
        metadata = column_metadata(self.context.node, table, "string_column")
        assert metadata["type"] == "String", error(str(metadata))
        assert metadata["default_kind"] == "", error(str(metadata))
        assert metadata["default_expression"] == "", error(str(metadata))
        assert metadata["comment"] == "", error(str(metadata))


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Column("1.0"))
def modify_and_reset_setting(self):
    """Check that column settings can be modified and reset."""
    with Given("create cas merge tree table with 10 rows"):
        table = column_table(suffix="column_setting")

    with When("modify the column setting"):
        modify_column_setting(
            table_name=table,
            column_name="string_column",
            setting="max_compress_block_size",
            value=131072,
        )

    with Then("SHOW CREATE contains the new setting"):
        create_query = show_create_table(self.context.node, table)
        assert "max_compress_block_size = 131072" in create_query, error(create_query)

    with When("I reset the column setting"):
        reset_column_setting(
            table_name=table,
            column_name="string_column",
            setting="max_compress_block_size",
        )

    with Then("SHOW CREATE no longer declares the setting"):
        create_query = show_create_table(self.context.node, table)
        assert "max_compress_block_size" not in create_query, error(create_query)


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Column("1.0"))
def enum_values(self):
    """Check that MODIFY COLUMN ADD ENUM VALUES extends an Enum without losing data."""
    columns = (
        "partition_column UInt8, id UInt64, value Int64, "
        "string_column String DEFAULT '', "
        "state Enum8('one' = 1) DEFAULT 'one'"
    )
    with Given("create cas merge tree table with 10 rows"):
        table = column_table(suffix="enum", columns=columns)

    with When("I add another Enum value"):
        add_enum_values(table_name=table, column_name="state", values="'two' = 2")
        self.context.node.query(
            f"INSERT INTO {table} (partition_column, id, value, state) "
            f"VALUES (3, 1, 1, 'two')"
        )

    with Then("old and new Enum values are readable"):
        result = self.context.node.query(
            f"SELECT state, count() FROM {table} GROUP BY state ORDER BY state"
        ).output.strip()
        assert result == "one\t10\ntwo\t1", error(result)


@TestScenario
@Requirements(RQ_SRS_048_CAS_MergeTree_Alter_Column("1.0"))
def materialize(self):
    """Check that MATERIALIZE COLUMN rewrites existing parts for a MATERIALIZED column."""
    with Given("create cas merge tree table with 10 rows"):
        table = column_table(suffix="materialize")

    with When("add a materialized column and materialize it"):
        add_column(table_name=table, definition="derived UInt64 MATERIALIZED id + 10")
        materialize_column(table_name=table, column_name="derived")

    with Then("existing parts hold the first expression"):
        result = self.context.node.query(
            f"SELECT sum(derived) FROM {table}"
        ).output.strip()
        assert result == "120", error(result)

    with When("change the expression and materialize again"):
        modify_column(
            table_name=table, definition="derived UInt64 MATERIALIZED id + 20"
        )
        materialize_column(table_name=table, column_name="derived")

    with Then("existing parts are rewritten with the new expression"):
        result = self.context.node.query(
            f"SELECT sum(derived) FROM {table}"
        ).output.strip()
        assert result == "220", error(result)


@TestScenario
@Requirements(
    RQ_SRS_048_CAS_MergeTree_Alter_Column("1.0"),
    RQ_SRS_048_CAS_Partition_ClearColumn("1.0"),
)
def clear_in_partition(self):
    """Check that CLEAR COLUMN resets only the selected partition."""
    with Given("create cas merge tree table with 10 rows"):
        table = column_table(suffix="clear_partition")

    with When("clear the payload column in partition 1"):
        clear_column_in_partition(
            table_name=table, column_name="string_column", partition=1
        )

    with Then("only partition 1 contains the default value"):
        result = self.context.node.query(
            f"SELECT partition_column, groupArray(string_column) "
            f"FROM {table} GROUP BY partition_column ORDER BY partition_column"
        ).output.strip()
        assert result == (
            "1\t['','','','','']\n" "2\t['p2-0','p2-1','p2-2','p2-3','p2-4']"
        ), error(result)


@TestFeature
@Name("column")
def feature(self):
    """Column ALTER TABLE operations on CAS."""
    for scenario in loads(current_module(), Scenario):
        scenario()
