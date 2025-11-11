from testflows.core import *


@TestStep(Given)
def ice_create_table_from_parquet(
    self,
    iceberg_table_name,
    parquet_path,
    partition_column,
    sort_column,
    ice_node=None,
):
    """Create an iceberg table from parquet schema."""
    if ice_node is None:
        ice_node = self.context.ice_node

    if partition_column:
        partition_columns_str = f'--partition=\'[{{"column":"{partition_column}","transform":"identity"}}]\''
    else:
        partition_columns_str = ""

    if (
        sort_column
        and ("map" not in iceberg_table_name)
        and ("tuple" not in iceberg_table_name)
        and ("array" not in iceberg_table_name)
        and ("list" not in iceberg_table_name)
        and ("nullable" not in iceberg_table_name)
        and ("fixedstring" not in iceberg_table_name)
    ):
        sort_columns_str = f'--sort=\'[{{"column":"{sort_column}"}}]\''
    else:
        sort_columns_str = ""

    try:
        ice_node.command(
            f"ice create-table default.{iceberg_table_name} -p --schema-from-parquet {parquet_path} {partition_columns_str} {sort_columns_str}"
        )
        yield iceberg_table_name
    finally:
        with Finally("drop the table"):
            # ice_node.command(f"ice delete-table default.{iceberg_table_name}")
            pass


@TestStep(Given)
def ice_insert_data_from_parquet(
    self,
    iceberg_table_name,
    parquet_path,
    no_copy=False,
    skip_duplicates=False,
    ice_node=None,
):
    """Insert parquet data into an iceberg table."""
    if ice_node is None:
        ice_node = self.context.ice_node

    command = f"ice insert default.{iceberg_table_name}"

    if no_copy:
        command += " --no-copy"
    if skip_duplicates:
        command += " --skip-duplicates"

    command += f" -p {parquet_path}"

    ice_node.command(command)
