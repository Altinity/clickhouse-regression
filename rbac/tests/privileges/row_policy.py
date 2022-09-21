from testflows.core import *
from testflows.asserts import error

from rbac.requirements import *
from rbac.helper.common import *

@TestStep(Given)
def create_table(
    self,
    table_name,
    node=None
):
    """Create a simple table used by all the tests in this suite.
    """
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    try:
        node.query(f"""
            CREATE TABLE {table_name}(
            x Int16,
            y String
            ) ENGINE = MergeTree
            ORDER BY x
            SETTINGS index_granularity = 8192
        """)

        yield

    finally:
        with Finally("I clean up"):
            node.query(f"DROP TABLE IF EXISTS {table_name}")

@TestStep(Given)
def insert_data(
    self,
    table_name,
    node=None
):
    """Insert simple data.
    """
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    node.query(f"INSERT INTO {table_name}(y, x) VALUES ('A',1), ('B',2), ('C',3)")

@TestStep(Given)
def create_row_policy(
    self,
    table_name,
    node=None
):
    """Create a simple row policy.
    """
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    try:
        node.query(f"CREATE ROW POLICY pol0 ON default.{table_name} FOR SELECT USING x >= 0 TO default")
        yield

    finally:
        with Finally("I clean up"):
            node.query(f"DROP ROW POLICY IF EXISTS pol0 ON {table_name}")


@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_RowPolicy_MultiIf("1.0")
)
def multiIf_alias(self, node=None):
    """Check that row policy works correctly regardless of what the multiIf alias.
    """
    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given(f"I have a table {table_name}"):
        create_table(table_name=table_name)

    with And("I insert data into the table in one part."):
        insert_data(table_name=table_name)

    with And("I have a row policy that does not filter any rows."):
        create_row_policy(table_name=table_name)

    with When("I select with a query where the multiIf alias matches the name of a column."):
        output_dup = node.query(f"""
            WITH Test AS (
            SELECT
                multiIf(y = 'Aaaaaaaaaaaa', 'Bbbbbbbbbbbb', y) AS y,
                x
            FROM {table_name}
            WHERE y IN ('A', 'C')
            ) SELECT DISTINCT (y, x)
            FROM Test""").output
    
    with And("I select with a query where the multiIf alias is unique."):
        output_unq = node.query(f"""
            WITH Test AS (
            SELECT
                multiIf(y = 'Aaaaaaaaaaaa', 'Bbbbbbbbbbbb', y) AS y1,
                x
            FROM {table_name}
            WHERE y IN ('A', 'C')
            ) SELECT DISTINCT (y1, x)
            FROM Test""").output

    with Then("The outputs should match"):
        assert output_dup == output_unq, error()

@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_RowPolicy_Columns("1.0")
)
def columns_selected(self, node=None):
    """Check that row policy works correctly regardless of how many columns are being selected.
    """
    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given(f"I have a table {table_name}"):
        create_table(table_name=table_name)

    with And("I insert data into the table"):
        insert_data(table_name=table_name)

    with And("I have a row policy that does not filter any rows."):
        create_row_policy(table_name=table_name)

    with When("I select with a query where the SELECT targets one column."):
        output_single = node.query(f"""
            WITH Test AS (
            SELECT
                multiIf(y = 'Aaaaaaaaaaaa', 'Bbbbbbbbbbbb', y) AS y,
                x
            FROM {table_name}
            WHERE y IN ('A', 'C')
            ) SELECT DISTINCT count((y,))
            FROM Test""").output
    
    with And("I select with a query where the SELECT targets multiple columns."):
        output_tuple = node.query(f"""
            WITH Test AS (
            SELECT
                multiIf(y = 'Aaaaaaaaaaaa', 'Bbbbbbbbbbbb', y) AS y,
                x
            FROM {table_name}
            WHERE y IN ('A', 'C')
            ) SELECT DISTINCT count((y, x))
            FROM Test""").output

    with Then("The outputs should match"):
        assert output_single == output_tuple, error()

@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_RowPolicy_Rows("1.0")
)
def row_policy_filtering(self, node=None):
    """Check that row policy works correctly regardless of how many rows are being filtered.
    """
    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"
    pol_name = f"pol_{getuid()}"

    try:
        with Given(f"I have a table {table_name}"):
            create_table(table_name=table_name)

        with And("I insert data into the table"):
            insert_data(table_name=table_name)

        with And("I have a row policy that does not filter any rows."):
            create_row_policy(table_name=table_name)

        with When("I select with a query where the multiIf alias matches the name of a column."):
            output_one_row_pol = node.query(f"""
                WITH Test AS (
                SELECT
                    multiIf(y = 'Aaaaaaaaaaaa', 'Bbbbbbbbbbbb', y) AS y,
                    x
                FROM {table_name}
                WHERE y IN ('A', 'C')
                ) SELECT DISTINCT count((y, x))
                FROM Test""").output

        with And("I have a row policy that filters a row that should already be filtered by WITH."):
            node.query(f"CREATE ROW POLICY {pol_name} ON default.{table_name} FOR SELECT USING x = 2 TO default")

        with And("I select with a query where the multiIf alias is unique."):
            output_two_row_pol = node.query(f"""
                WITH Test AS (
                SELECT
                    multiIf(y = 'Aaaaaaaaaaaa', 'Bbbbbbbbbbbb', y) AS y,
                    x
                FROM {table_name}
                WHERE y IN ('A', 'C')
                ) SELECT DISTINCT count((y, x))
                FROM Test""").output

        with Then("The outputs should match"):
            assert output_one_row_pol == output_two_row_pol, error()

    finally:

        with Finally(f"I drop the row policy {pol_name}", flags=TE):
            node.query(f"DROP ROW POLICY IF EXISTS {pol_name} ON {table_name}")

@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_RowPolicy_MultiIfLength("1.0")
)
def multiIf_length(self, node=None):
    """Check that row policy works correctly regardless of how length of the multiIf arguments.
    """
    if node is None:
        node = self.context.node

    table_name = f"table_{getuid()}"

    with Given(f"I have a table {table_name}"):
        create_table(table_name=table_name)

    with And("I insert data into the table"):
        insert_data(table_name=table_name)

    with And("I have a row policy that does not filter any rows."):
        create_row_policy(table_name=table_name)

    with When("I select with a query where multiIf uses short arguements."):
        output_short = node.query(f"""
            WITH Test AS (
            SELECT
                multiIf(y = 'X', 'B', y) AS y,
                x
            FROM {table_name}
            WHERE y IN ('A', 'C')
            ) SELECT DISTINCT (y,x)
            FROM Test""").output
    
    with And("I select with a query where multiIf uses long arguements."):
        output_long = node.query(f"""
            WITH Test AS (
            SELECT
                multiIf(y = 'Xxxxxxxxxxxx', 'Bbbbbbbbbbbb', y) AS y,
                x
            FROM {table_name}
            WHERE y IN ('A', 'C')
            ) SELECT DISTINCT (y, x)
            FROM Test""").output

    with Then("The outputs should match"):
        assert output_short == output_long, error()

@TestScenario
@Requirements(
    RQ_SRS_006_RBAC_RowPolicy_Parts("1.0")
)
def parts(self, node=None):
    """Check that row policy works correctly regardless of how many parts the data was inserted in.
    """
    if node is None:
        node = self.context.node

    table0_name = f"table_{getuid()}"
    table1_name = f"table_{getuid()}"

    with Given(f"I have a table {table0_name}"):
        create_table(table_name=table0_name)

    with And(f"I have a table {table1_name}"):
        create_table(table_name=table1_name)

    with And(f"I insert data into {table0_name} in one part"):
        insert_data(table_name=table0_name)

    with And(f"I insert data into {table1_name} in multiple parts"):
        node.query(f"INSERT INTO {table1_name} VALUES (1,'A')")
        node.query(f"INSERT INTO {table1_name} VALUES (2,'B')")
        node.query(f"INSERT INTO {table1_name} VALUES (3,'C')")

    with And("I have a row policy that does not filter any rows."):
        create_row_policy(table_name=table0_name)
        create_row_policy(table_name=table1_name)

    with When("I select with a query where the data was inserted in 1 part."):
        output_one_part = node.query(f"""
            WITH Test AS(
            SELECT
                multiIf(y = 'X', 'B', y) AS y,
                x
            FROM {table0_name}
            WHERE y IN ('A', 'C')
            ) SELECT DISTINCT (y,x)
            ORDER BY x
            FROM Test""").output
    
    with And("I select with a query where the data was inserted in many parts."):
        output_multi_part = node.query(f"""
            WITH Test AS (
            SELECT
                multiIf(y = 'Aaaaaaaaaaaa', 'Bbbbbbbbbbbb', y) AS y,
                x
            FROM {table1_name}
            WHERE y IN ('A', 'C')
            ) SELECT DISTINCT (y, x)
            ORDER BY x
            FROM Test""").output

    with Then("The outputs should match"):
        assert output_one_part == output_multi_part, error()

@TestFeature
@Name("row policy")
@Requirements(
    RQ_SRS_006_RBAC_RowPolicy("1.0")
)
def feature(self, node="clickhouse1"):
    """Check the functionality of row policies."""

    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()