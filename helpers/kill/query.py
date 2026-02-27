from testflows.core import *


@TestStep(When)
def kill_query(
    self,
    where_clause,
    node=None,
    cluster=None,
    sync=False,
    async_mode=False,
    test=False,
    output_format=None,
    **query_kwargs
):
    """
    Kill queries using KILL QUERY command.
    
    Args:
        where_clause: WHERE expression to filter queries from system.processes
        node: ClickHouse node to execute the query on (defaults to context.node)
        cluster: Cluster name for ON CLUSTER clause (optional)
        sync: Use SYNC mode (waits for queries to stop)
        async_mode: Use ASYNC mode (default, doesn't wait)
        test: Use TEST mode (only checks rights and displays queries)
        output_format: Output format (optional)
        **query_kwargs: Additional arguments to pass to node.query()
    
    Examples:
        kill_query(where_clause="query_id='2-857d-4a57-9ee0-327da5d60a90'")
        kill_query(where_clause="user='username'", sync=True)
        kill_query(where_clause="query LIKE 'SELECT%'", cluster="my_cluster")
    """
    if node is None:
        node = self.context.node

    with By("killing queries"):
        query = "KILL QUERY"
        
        if cluster:
            query += f" ON CLUSTER {cluster}"
        
        query += f" WHERE {where_clause}"
        
        if test:
            query += " TEST"
        elif sync:
            query += " SYNC"
        elif async_mode:
            query += " ASYNC"
        
        if output_format:
            query += f" FORMAT {output_format}"
        
        return node.query(query, **query_kwargs)


@TestStep(When)
def kill_query_by_id(
    self,
    query_id,
    node=None,
    cluster=None,
    sync=False,
    **query_kwargs
):
    """
    Kill a query by its query_id.
    
    Args:
        query_id: The query_id to kill
        node: ClickHouse node to execute the query on (defaults to context.node)
        cluster: Cluster name for ON CLUSTER clause (optional)
        sync: Use SYNC mode (waits for query to stop)
        **query_kwargs: Additional arguments to pass to node.query()
    """
    return kill_query(
        where_clause=f"query_id='{query_id}'",
        node=node,
        cluster=cluster,
        sync=sync,
        **query_kwargs
    )


@TestStep(When)
def kill_query_by_user(
    self,
    user,
    node=None,
    cluster=None,
    sync=False,
    **query_kwargs
):
    """
    Kill all queries run by a specific user.
    
    Args:
        user: Username whose queries should be killed
        node: ClickHouse node to execute the query on (defaults to context.node)
        cluster: Cluster name for ON CLUSTER clause (optional)
        sync: Use SYNC mode (waits for queries to stop)
        **query_kwargs: Additional arguments to pass to node.query()
    """
    return kill_query(
        where_clause=f"user='{user}'",
        node=node,
        cluster=cluster,
        sync=sync,
        **query_kwargs
    )


@TestStep(When)
def kill_query_by_initial_query_id(
    self,
    initial_query_id,
    node=None,
    cluster=None,
    sync=False,
    **query_kwargs
):
    """
    Kill queries by their initial_query_id.
    
    Args:
        initial_query_id: The initial_query_id to kill
        node: ClickHouse node to execute the query on (defaults to context.node)
        cluster: Cluster name for ON CLUSTER clause (optional)
        sync: Use SYNC mode (waits for queries to stop)
        **query_kwargs: Additional arguments to pass to node.query()
    """
    return kill_query(
        where_clause=f"initial_query_id='{initial_query_id}'",
        node=node,
        cluster=cluster,
        sync=sync,
        **query_kwargs
    )


@TestStep(When)
def test_kill_query(
    self,
    where_clause,
    node=None,
    cluster=None,
    output_format=None,
    **query_kwargs
):
    """
    Test KILL QUERY command (only checks user rights and displays queries to stop).
    
    Args:
        where_clause: WHERE expression to filter queries from system.processes
        node: ClickHouse node to execute the query on (defaults to context.node)
        cluster: Cluster name for ON CLUSTER clause (optional)
        output_format: Output format (optional)
        **query_kwargs: Additional arguments to pass to node.query()
    """
    return kill_query(
        where_clause=where_clause,
        node=node,
        cluster=cluster,
        test=True,
        output_format=output_format,
        **query_kwargs
    )

