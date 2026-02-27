from testflows.core import *


@TestStep(When)
def kill_mutation(
    self,
    where_clause,
    node=None,
    test=False,
    output_format=None,
    **query_kwargs
):
    """
    Kill mutations using KILL MUTATION command.
    
    Args:
        where_clause: WHERE expression to filter mutations from system.mutations
        node: ClickHouse node to execute the query on (defaults to context.node)
        test: Use TEST mode (only checks rights and displays mutations)
        output_format: Output format (optional)
        **query_kwargs: Additional arguments to pass to node.query()
    
    Examples:
        kill_mutation(where_clause="database='default' AND table='table'")
        kill_mutation(where_clause="database='default' AND table='table' AND mutation_id='mutation_3.txt'")
    """
    if node is None:
        node = self.context.node

    with By("killing mutations"):
        query = "KILL MUTATION"
        
        query += f" WHERE {where_clause}"
        
        if test:
            query += " TEST"
        
        if output_format:
            query += f" FORMAT {output_format}"
        
        return node.query(query, **query_kwargs)


@TestStep(When)
def kill_mutation_by_table(
    self,
    database,
    table,
    node=None,
    **query_kwargs
):
    """
    Kill all mutations for a specific table.
    
    Args:
        database: Database name
        table: Table name
        node: ClickHouse node to execute the query on (defaults to context.node)
        **query_kwargs: Additional arguments to pass to node.query()
    """
    return kill_mutation(
        where_clause=f"database='{database}' AND table='{table}'",
        node=node,
        **query_kwargs
    )


@TestStep(When)
def kill_mutation_by_id(
    self,
    database,
    table,
    mutation_id,
    node=None,
    **query_kwargs
):
    """
    Kill a specific mutation by its mutation_id.
    
    Args:
        database: Database name
        table: Table name
        mutation_id: The mutation_id to kill
        node: ClickHouse node to execute the query on (defaults to context.node)
        **query_kwargs: Additional arguments to pass to node.query()
    """
    return kill_mutation(
        where_clause=f"database='{database}' AND table='{table}' AND mutation_id='{mutation_id}'",
        node=node,
        **query_kwargs
    )


@TestStep(When)
def test_kill_mutation(
    self,
    where_clause,
    node=None,
    output_format=None,
    **query_kwargs
):
    """
    Test KILL MUTATION command (only checks user rights and displays mutations to stop).
    
    Args:
        where_clause: WHERE expression to filter mutations from system.mutations
        node: ClickHouse node to execute the query on (defaults to context.node)
        output_format: Output format (optional)
        **query_kwargs: Additional arguments to pass to node.query()
    """
    return kill_mutation(
        where_clause=where_clause,
        node=node,
        test=True,
        output_format=output_format,
        **query_kwargs
    )

