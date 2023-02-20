from selects.tests.steps import *


@TestStep(When)
def simple_select(self, statement, name, final_manual, final=0, node=None):
    """Select query step."""
    if node is None:
        node = self.context.cluster.node("clickhouse1")

    with When(f"I make select from table"):
        node.query(
            f"{statement}".format(name=name, final=final_manual),
            settings=[("final", final)],
        )


@TestStep(When)
def simple_insert(self, name, first_insert_id=1, last_insert_id=4):
    """
    Insert query step
    :param self:
    :param first_delete_id:
    :param last_delete_id:
    :param name:
    :return:
    """
    node = self.context.cluster.node("clickhouse1")

    with When(f"I insert {first_insert_id - last_insert_id} rows of data"):
        for i in range(first_insert_id, last_insert_id):
            node.query(
                f"INSERT INTO {name} VALUES ({i},777, 77{i}, 'ivan', '2019-01-01 00:00:00')"
            )


@TestStep(When)
def delete(self, name, first_delete_id=1, last_delete_id=4):
    """
    Delete query step
    :param self:
    :param first_delete_id:
    :param last_delete_id:
    :param name:
    :return:
    """
    node = self.context.cluster.node("clickhouse1")

    with When(f"I delete {last_delete_id - first_delete_id} rows of data"):
        for i in range(first_delete_id, last_delete_id):
            node.query(f"ALTER TABLE {name} DELETE WHERE id={i}")


@TestStep(When)
def update(self, name, first_update_id=1, last_update_id=4):
    """
    Update query step
    :param self:
    :param first_update_id:
    :param last_update_id:
    :param name:
    :return:
    """
    node = self.context.cluster.node("clickhouse1")

    with When(f"I update {last_update_id - first_update_id} rows of data"):
        for i in range(first_update_id, last_update_id):
            node.query(f"ALTER TABLE {name} UPDATE x=x+5 WHERE id={i};")


@TestOutline
def parallel_outline(
    self,
    tables,
    selects,
    inserts=None,
    updates=None,
    deletes=None,
    iterations=10,
    parallel_select=True,
):
    """Execute specified selects, inserts, updates, and deletes in parallel."""
    for table in tables:
        with Example(f"{table.name}", flags=TE):
            for i in range(iterations):
                for select in selects:
                    if select.name.endswith("negative_select_check"):
                        with Example(f"negative", flags=TE):
                            By(f"{select.name}", test=select, parallel=parallel_select)(
                                name=table.name,
                                final_modifier_available=table.final_modifier_available,
                            )
                    else:
                        By(f"{select.name}", test=select, parallel=parallel_select)(
                            name=table.name,
                            final_modifier_available=table.final_modifier_available,
                        )

                if not inserts is None:
                    for insert in inserts:
                        By(f"{insert.name}", test=simple_insert, parallel=True)(
                            name=table.name
                        )

                if not updates is None:
                    for update in updates:
                        By(f"{update.name}", test=update, parallel=True)(
                            name=table.name
                        )

                if not deletes is None:
                    for delete in deletes:
                        By(f"{delete.name}", test=delete, parallel=True)(
                            name=table.name
                        )
