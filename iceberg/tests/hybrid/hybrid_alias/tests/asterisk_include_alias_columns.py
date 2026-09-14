from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid
from helpers.tables import create_table, Column
from helpers.datatypes import Int32, Int64, Date

from iceberg.tests.hybrid.hybrid_alias.requirements.requirements import (
    RQ_Ice_HybridAlias_Settings_AsteriskIncludeAliasColumns,
)
import iceberg.tests.steps.hybrid as hybrid_steps


@TestScenario
@Name("asterisk include alias columns")
def asterisk_include_alias_columns(self):
    """SELECT * includes Hybrid ALIAS columns only when asterisk_include_alias_columns=1."""
    node = self.context.node

    with Given("enable hybrid table"):
        hybrid_steps.enable_hybrid_table()

    with And("create left and right MergeTree segments with matching ALIAS columns"):
        segment_columns = [
            Column(name="id", datatype=Int32()),
            Column(name="value", datatype=Int32()),
            Column(name="date_col", datatype=Date()),
            Column(name="computed", alias="value * 2"),
        ]
        left_table_name = f"left_{getuid()}"
        right_table_name = f"right_{getuid()}"

        left_table = create_table(
            name=left_table_name,
            engine="MergeTree",
            columns=segment_columns,
            order_by="(date_col, id)",
            partition_by="toYYYYMM(date_col)",
        )
        left_table.insert_test_data(cardinality=1, shuffle_values=False)

        right_table = create_table(
            name=right_table_name,
            engine="MergeTree",
            columns=segment_columns,
            order_by="(date_col, id)",
            partition_by="toYYYYMM(date_col)",
        )
        right_table.insert_test_data(cardinality=1, shuffle_values=False)

    with And("create Hybrid table declaring the same ALIAS column"):
        hybrid_table_name = f"hybrid_{getuid()}"
        # Hybrid keeps computed as ALIAS so asterisk_include_alias_columns applies;
        # segments must expose the same name for pushdown when the setting is 1.
        hybrid_columns = [
            Column(name="id", datatype=Int32()),
            Column(name="value", datatype=Int32()),
            Column(name="date_col", datatype=Date()),
            Column(name="computed", datatype=Int64(), alias="value * 2"),
        ]
        left_tf = f"remote('localhost', currentDatabase(), '{left_table_name}')"
        right_tf = f"remote('localhost', currentDatabase(), '{right_table_name}')"
        create_table(
            name=hybrid_table_name,
            engine=(
                f"Hybrid({left_tf}, date_col >= '2025-01-15', "
                f"{right_tf}, date_col < '2025-01-15')"
            ),
            columns=hybrid_columns,
            settings=[("allow_experimental_hybrid_table", 1)],
        )

    def column_names(asterisk_include):
        header = node.query(
            f"SELECT * FROM {hybrid_table_name} ORDER BY id "
            f"SETTINGS enable_analyzer = 1, "
            f"asterisk_include_alias_columns = {asterisk_include} "
            f"FORMAT TSVWithNames"
        ).output.splitlines()[0]
        return header.split("\t")

    with When("SELECT * with asterisk_include_alias_columns = 0"):
        names_off = column_names(0)

    with Then("ALIAS column is omitted"):
        assert "computed" not in names_off, error()
        assert set(names_off) == {"id", "value", "date_col"}, error()

    with When("SELECT * with asterisk_include_alias_columns = 1"):
        names_on = column_names(1)

    with Then("ALIAS column is included alongside base columns"):
        assert "computed" in names_on, error()
        assert set(names_on) == {"id", "value", "date_col", "computed"}, error()

    with And("drop Hybrid table"):
        node.query(f"DROP TABLE IF EXISTS {hybrid_table_name}")


@TestScenario
@Requirements(
    RQ_Ice_HybridAlias_Settings_AsteriskIncludeAliasColumns("1.0"),
)
@Name("asterisk include alias columns")
def feature(self, minio_root_user, minio_root_password):
    """asterisk_include_alias_columns controls SELECT * ALIAS inclusion on Hybrid."""
    Scenario(run=asterisk_include_alias_columns)
