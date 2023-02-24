from selects.tests.steps.main_steps import *


@TestStep(Given)
def join(self, table1, table2, join_type, node=None):
    """Execute select some join type query without `FINAL` clause and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make {join_type} {table2} on {table1}"):
        node.query(
            f"SELECT count() FROM {table1} {join_type}"
            f" {table2} on {table1}.id = {table2}.id",
            settings=[("final", 0)],
        ).output.strip()


@TestStep(Given)
def join_with_force_final(self, table1, table2, join_type, node=None):
    """Execute select some join type query without `FINAL` clause and with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make {join_type} {table2} on {table1} with --final enabled"):
        node.query(
            f"SELECT count() FROM {table1} {join_type}"
            f" {table2} on {table1}.id = {table2}.id",
            settings=[("final", 1)],
        ).output.strip()


@TestStep(Given)
def join_with_final_on_left_table(self, table1, table2, join_type, node=None):
    """Execute select some join type query with `FINAL` clause on left table and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make {join_type} {table2} on {table1} with left 'FINAL'"):
        node.query(
            f"SELECT count() FROM {table1} "
            f"{' FINAL' if table1.final_modifier_available else ''} {join_type}"
            f" {table2} on {table1}.id = {table2}.id",
            settings=[("final", 0)],
        ).output.strip()


@TestStep(Given)
def join_with_final_on_left_table_with_force_final(
    self, table1, table2, join_type, node=None
):
    """Execute select some join type query with `FINAL` clause on left table and with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make {join_type} {table2} on {table1} with left 'FINAL' with --final enabled"
    ):
        node.query(
            f"SELECT count() FROM {table1} "
            f"{' FINAL' if table1.final_modifier_available else ''} {join_type}"
            f" {table2} on {table1}.id = {table2}.id",
            settings=[("final", 1)],
        ).output.strip()


@TestStep(Given)
def join_with_final_on_right_table(self, table1, table2, join_type, node=None):
    """Execute select some join type query with `FINAL` clause on right table and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make {join_type} {table2} on {table1} with right 'FINAL'"):
        node.query(
            f"SELECT count() FROM {table1} {join_type}"
            f" {table2} {' FINAL' if table2.final_modifier_available else ''} on {table1}.id = {table2.name}.id",
            settings=[("final", 0)],
        ).output.strip()


@TestStep(Given)
def join_with_final_on_right_table_with_force_final(
    self, table1, table2, join_type, node=None
):
    """Execute select some join type query with `FINAL` clause on right table and with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make {join_type} {table2} on {table1} with right 'FINAL' with --final enabled"
    ):
        node.query(
            f"SELECT count() FROM {table1} {join_type}"
            f" {table2} {' FINAL' if table2.final_modifier_available else ''} on {table1}.id = {table2.name}.id",
            settings=[("final", 1)],
        ).output.strip()


@TestStep(Given)
def join_with_final_on_both_tables(self, table1, table2, join_type, node=None):
    """Execute select some join type query with `FINAL` clause on both tables and with --final setting disabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make {join_type} {table2} on {table1} with both tables 'FINAL'"):
        node.query(
            f"SELECT count() FROM {table1} {' FINAL' if table1.final_modifier_available else ''} {join_type}"
            f" {table2.name} {' FINAL' if table2.final_modifier_available else ''} on {table1}.id = {table2}.id",
            settings=[("final", 0)],
        ).output.strip()


@TestStep(Given)
def join_with_final_on_both_tables_with_force_final(
    self, table1, table2, join_type, node=None
):
    """Execute select some join type query with `FINAL` clause on both tables and with --final setting enabled."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(
        f"I make {join_type} {table2} on {table1} with both tables 'FINAL' with --final enabled"
    ):
        node.query(
            f"SELECT count() FROM {table1} {' FINAL' if table1.final_modifier_available else ''} {join_type}"
            f" {table2.name} {' FINAL' if table2.final_modifier_available else ''} on {table1}.id = {table2}.id",
            settings=[("final", 1)],
        ).output.strip()
