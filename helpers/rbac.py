from testflows.core import *


@TestStep(Given)
def no_privileges(self, user, table, node=None):
    """Grant no privileges to a user."""
    if node is None:
        node = self.context.node

    with By(f"granting the user no privileges on the {table} table"):
        node.query(f"GRANT NONE ON {table} TO {user}")


@TestStep(Given)
def select_privileges(self, node, user, table):
    """Grant only select privileges to a user."""
    if node is None:
        node = self.context.node

    with By(f"granting the user only select privileges on the {table} table"):
        node.query(f"GRANT SELECT ON {table} TO {user}")


@TestStep(Given)
def insert_privileges(self, node, user, table):
    """Grant only insert privileges to a user."""
    if node is None:
        node = self.context.node

    with By(f"granting the user only insert privileges on the {table} table"):
        node.query(f"GRANT INSERT ON {table} TO {user}")


@TestStep(Given)
def alter_privileges(self, node, user, table):
    """Grant only alter privileges to a user."""
    if node is None:
        node = self.context.node

    with By(f"granting the user only alter privileges on the {table} table"):
        node.query(f"GRANT ALTER ON {table} TO {user}")


@TestStep(Given)
def alter_table_privileges(self, node, user, table):
    """Grant only alter table privileges to a user."""
    if node is None:
        node = self.context.node

    with By(f"granting the user only alter table privileges on the {table} table"):
        node.query(f"GRANT ALTER TABLE ON {table} TO {user}")
