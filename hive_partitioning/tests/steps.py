from testflows.core import *
from testflows.asserts import error

@TestStep(Given)
def create_table(self, table_name=None, engine=None, partition_by=None, columns="d Int64", settings=None, modify=False, node=None):
    """Create table."""
    if node is None:
        node = self.context.node

    if engine is None:
        engine = "MergeTree"

    if partition_by is None:
        partition_by = ""

    else:
        partition_by = f"PARTITION BY {partition_by}"
 
    if settings is None:
        settings = {}

    if table_name is None:
        table_name = "table_" + getuid()

    try:
        with Given(f"I create table {table_name}"):
            node.query(f"CREATE TABLE {table_name} ({columns}) ENGINE = {engine} {partition_by}", settings=settings)
        
        yield table_name

    finally:
        if not modify:
            with Finally(f"I drop table {table_name}"):
                node.query(f"DROP TABLE IF EXISTS {table_name}")

@TestStep(When)
def insert_into_bucket_s3_funtion(self, bucket_path, values, type, compression_method, structure, settings, node=None):
    """Insert into bucket using s3 function."""
    
    if node is None:
        node = self.context.node

    with When(f"I insert into bucket {bucket_path} using s3 function"):
        node.query(f"INSERT INTO s3('{bucket_path}', '{type}', '{compression_method}', '{structure}') VALUES {values}", settings=settings)

@TestStep(When)
def insert_into_bucket_s3_function_from_table(self, bucket_path, type, compression_method, structure, settings, node=None):
    """Insert into bucket using s3 function from table."""
    
    if node is None:
        node = self.context.node

    with When(f"I insert into bucket {bucket_path} using s3 function from table"):
        node.query(f"INSERT INTO s3('{bucket_path}', '{type}', '{compression_method}', '{structure}') FROM {table_name}", settings=settings)


@TestStep(When)
def insert_into_table_values(self, table_name, values, settings, node=None):
    """Insert into table values."""
    
    if node is None:
        node = self.context.node

    with When(f"I insert into table {table_name} values"):
        node.query(f"INSERT INTO {table_name} VALUES {values}", settings=settings)

@TestStep(When)
def insert_into_table_select(self, table_name, select_statement, settings, node=None):
    """Insert into table values from select statement."""
    
    if node is None:
        node = self.context.node
    
    with When(f"I insert into table {table_name} values"):
        node.query(f"INSERT INTO {table_name} SELECT {select_statement}", settings=settings)


@TestStep(When)
def check_select(self, select, query_id=None, settings=None, expected_result=None, node=None):
    """Check select statement."""
        
    if node is None:
        node = self.context.node

    with When(f"I check select statement"):
        r = node.query(f"{select}", query_id=query_id, settings=settings)
        if expected_result is not None:
            assert r.output == expected_result, error()

@TestStep(When)
def get_value_from_query_log(self, query_id, column_name, node=None):
    """Get value from query log."""
        
    if node is None:
        node = self.context.node

    with Then(f"I get {column_name} from system.query_log table"):
        r = node.query(f"SELECT {column_name} FROM system.query_log WHERE query_id = '{query_id}'") 
        return r.output

@TestStep(When)
def get_bucket_files_list(self, bucket_path, node=None):
    """Get bucket files list."""
    
    if node is None:
        node = self.context.node
        
    pass

@TestStep(When)
def get_bucket_file(self, bucket_path, file_name, node=None):
    """Get bucket file."""
    
    if node is None:
        node = self.context.node
        
    pass