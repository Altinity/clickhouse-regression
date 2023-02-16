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
def simple_insert(self, first_insert_id, last_insert_id, table_name):
    """
    Insert query step
    :param self:
    :param first_delete_id:
    :param last_delete_id:
    :param table_name:
    :return:
    """
    node = self.context.cluster.node("clickhouse1")

    with When(f"I insert {first_insert_id - last_insert_id} rows of data"):
        for i in range(first_insert_id, last_insert_id):
            node.query(
                f"INSERT INTO {table_name} VALUES ({i},777, 77{i}, 'ivan', '2019-01-01 00:00:00')"
            )


@TestStep(When)
def delete(self, first_delete_id, last_delete_id, table_name):
    """
    Delete query step
    :param self:
    :param first_delete_id:
    :param last_delete_id:
    :param table_name:
    :return:
    """
    node = self.context.cluster.node("clickhouse1")

    with When(f"I delete {last_delete_id - first_delete_id} rows of data"):
        for i in range(first_delete_id, last_delete_id):
            node.query(f"ALTER TABLE {table_name} DELETE WHERE id={i}")


@TestStep(When)
def update(self, first_update_id, last_update_id, table_name):
    """
    Update query step
    :param self:
    :param first_update_id:
    :param last_update_id:
    :param table_name:
    :return:
    """
    node = self.context.cluster.node("clickhouse1")

    with When(f"I update {last_update_id - first_update_id} rows of data"):
        for i in range(first_update_id, last_update_id):
            node.query(f"ALTER TABLE {table_name} UPDATE x=x+5 WHERE id={i};")

@TestStep(When)
def concurrent_queries(
    self,
    statement="SELECT count() FROM {name} {final} FORMAT JSONEachRow;",
    parallel_runs=1,
    parallel_selects=0,
    parallel_inserts=0,
    parallel_deletes=0,
    parallel_updates=0,
    final=0,
    final_manual="",
    table_name=None,
    node=None,
    first_insert_id=None,
    last_insert_id=None,
    first_delete_id=None,
    last_delete_id=None,
    first_update_id=None,
    last_update_id=None,
):
    """
    Run concurrent select queries with optional parallel insert, update, and delete.

    :param self:
    :param table_name: table name
    :param first_insert_number: first id of precondition insert
    :param last_insert_number:  last id of precondition insert
    :param first_insert_id: first id of concurrent insert
    :param last_insert_id: last id of concurrent insert
    :param first_delete_id: first id of concurrent delete
    :param last_delete_id: last id of concurrent delete
    :param first_update_id: first id of concurrent update
    :param last_update_id: last id of concurrent update
    :return:
    """
    for i in range(parallel_runs):
        if parallel_selects > 0:
            for i in range(parallel_selects):
                By("selecting data", test=simple_select, parallel=True)(
                    statement=statement,
                    name=table_name,
                    final_manual=final_manual,
                    final=final,
                    node=node,
                )

        if parallel_inserts > 0:
            for i in range(parallel_inserts):
                By("inserting data", test=simple_insert, parallel=True)(
                    first_insert_id=first_insert_id,
                    last_insert_id=last_insert_id,
                    table_name=table_name,
                )

        if parallel_deletes > 0:
            for i in range(parallel_deletes):
                By("deleting data", test=delete, parallel=True,)(
                    first_delete_id=first_delete_id,
                    last_delete_id=last_delete_id,
                    table_name=table_name,
                )

        if parallel_updates > 0:
            for i in range(parallel_updates):
                By("updating data", test=update, parallel=True,)(
                    first_update_id=first_update_id,
                    last_update_id=last_update_id,
                    table_name=table_name,
                )
