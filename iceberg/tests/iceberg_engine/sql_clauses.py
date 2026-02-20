from testflows.core import *
from testflows.asserts import error

import iceberg.tests.steps.catalog as catalog_steps
import iceberg.tests.steps.iceberg_engine as iceberg_engine

from helpers.common import getuid, check_clickhouse_version


@TestScenario
def where_clause(self, table_name, node=None):
    """Check reading data from ClickHouse table from Iceberg database with where clause."""
    if node is None:
        node = self.context.node

    with Then(
        "read data from table from Iceberg database with where applied on string column"
    ):
        result = node.query(
            f"""
                SELECT * FROM {table_name} 
                WHERE string_col = 'Alice' 
                FORMAT TabSeparated
            """
        )
        assert result.output.strip() == "true	1000	456.78	Alice	2024-01-01", error()

    with And(
        "read data from table from Iceberg database with where applied on integer and boolean columns"
    ):
        result = node.query(
            f"""
                SELECT * FROM {table_name} 
                WHERE long_col > 1000 AND boolean_col = false 
                ORDER BY tuple(*)
                FORMAT TabSeparated
            """
        )
        assert (
            result.output.strip()
            == """false	2000	456.78	Bob	2023-05-15\nfalse	4000	8.9	1	2021-01-01"""
        ), error()

    with And(
        "read data from table from Iceberg database with where applied on double column"
    ):
        result = node.query(
            f"""
                SELECT * FROM {table_name} 
                WHERE double_col < 456.78 
                ORDER BY tuple(*)
                FORMAT TabSeparated
            """
        )
        assert (
            result.output.strip()
            == "false	4000	8.9	1	2021-01-01\ntrue	3000	6.7	Charlie	2022-01-01"
        ), error()

    with And(
        "read data from table from Iceberg database with where applied on date column"
    ):
        result = node.query(
            f"""
                SELECT * FROM {table_name} 
                WHERE date_col > '2023-01-01' 
                ORDER BY tuple(*)
                FORMAT TabSeparated
            """
        )
        assert (
            result.output.strip()
            == "false	2000	456.78	Bob	2023-05-15\ntrue	1000	456.78	Alice	2024-01-01"
        ), error()


@TestScenario
def prewhere_clause(self, table_name, node=None):
    """Check reading data from ClickHouse table from Iceberg database with prewhere clause."""
    if node is None:
        node = self.context.node

    table_name_without_backslashes = table_name.replace("\\", "")
    exitcode, message = 0, None

    if check_clickhouse_version("<26.2")(self):
        exitcode = 182
        storage_name = "IcebergS3" if check_clickhouse_version(">=25")(self) else "Iceberg"
        message = f"DB::Exception: Storage {storage_name} (table {table_name_without_backslashes}) does not support PREWHERE. (ILLEGAL_PREWHERE)"

    result = node.query(
        f"""
            SELECT * FROM {table_name} 
            PREWHERE boolean_col = false 
            WHERE string_col = 'Bob'
        """,
        exitcode=exitcode,
        message=message,
    )

    if exitcode == 0:
        assert result.output.strip() == "false	2000	456.78	Bob	2023-05-15", error()


@TestScenario
def group_by_clause(self, table_name, node=None):
    """Check reading data from ClickHouse table from Iceberg database with group by clause."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
        SELECT count(), boolean_col, sum(long_col)
        FROM {table_name}
        GROUP BY boolean_col
        """
    )
    assert result.output.strip() == "2	false	6000\n2	true	4000", error()


@TestScenario
def having_clause(self, table_name, node=None):
    """Check reading data from ClickHouse table from Iceberg database with having clause."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
        SELECT count(), boolean_col, sum(long_col), sum(double_col)
        FROM {table_name}
        GROUP BY boolean_col
        HAVING sum(double_col) > 456.78 + 6.7
            """
    )
    assert result.output.strip() == "2	false	6000	465.67999999999995", error()


@TestScenario
def limit_clause(self, table_name, node=None):
    """Check reading data from ClickHouse table from Iceberg database with limit clause."""
    if node is None:
        node = self.context.node

    result_limit_1 = node.query(
        f"""
            SELECT *
            FROM {table_name}
            ORDER BY tuple(*)
            LIMIT 1
        """
    )
    assert result_limit_1.output.strip() == "false	2000	456.78	Bob	2023-05-15", error()

    result_limit_2 = node.query(
        f"""
            SELECT *
            FROM {table_name}
            ORDER BY tuple(*)
            LIMIT 2
        """
    )
    assert (
        result_limit_2.output.strip()
        == "false	2000	456.78	Bob	2023-05-15\nfalse	4000	8.9	1	2021-01-01"
    ), error()


@TestScenario
def distinct_clause(self, table_name, node=None):
    """Check reading data from ClickHouse table from Iceberg database with distinct clause."""
    if node is None:
        node = self.context.node

    result = node.query(
        f"""
            SELECT DISTINCT boolean_col
            FROM {table_name}
            ORDER BY boolean_col
            FORMAT TabSeparated
            
        """
    )
    assert result.output.strip() == "false\ntrue", error()


@TestScenario
def join_clause(self, table_name, node=None):
    """Check reading data from ClickHouse table from Iceberg database with basic join clause."""
    if node is None:
        node = self.context.node

    try:
        with Given("create simple MergeTree table and insert data"):
            merge_tree_table_name = f"merge_tree_table_{getuid()}"
            node.query(
                f"""
                CREATE TABLE {merge_tree_table_name} (
                    boolean_col Boolean,
                    long_col UInt64,
                    double_col Float64,
                    string_col String,
                    date_col Date
                ) 
                ENGINE = MergeTree()
                ORDER BY boolean_col
                """
            )
            node.query(
                f"""
                INSERT INTO {merge_tree_table_name} 
                VALUES 
                    (true, 1, 1, 'a', '2021-01-01'), 
                    (false, 2, 2, 'b', '2021-01-01'), 
                    (true, 3, 3, 'c', '2021-01-01'), 
                    (false, 4, 4, 'd', '2021-01-01')
                """
            )

        with Then("join iceberg table with itself"):
            result = node.query(
                f"""
                SELECT *
                FROM {table_name} AS t1
                JOIN {table_name} AS t2
                ON t1.boolean_col = t2.boolean_col
                ORDER BY tuple(*)
                FORMAT Values
                """
            )
            assert (
                result.output.strip()
                == "(false,2000,456.78,'Bob','2023-05-15',false,2000,456.78,'Bob','2023-05-15'),(false,2000,456.78,'Bob','2023-05-15',false,4000,8.9,'1','2021-01-01'),(false,4000,8.9,'1','2021-01-01',false,2000,456.78,'Bob','2023-05-15'),(false,4000,8.9,'1','2021-01-01',false,4000,8.9,'1','2021-01-01'),(true,1000,456.78,'Alice','2024-01-01',true,1000,456.78,'Alice','2024-01-01'),(true,1000,456.78,'Alice','2024-01-01',true,3000,6.7,'Charlie','2022-01-01'),(true,3000,6.7,'Charlie','2022-01-01',true,1000,456.78,'Alice','2024-01-01'),(true,3000,6.7,'Charlie','2022-01-01',true,3000,6.7,'Charlie','2022-01-01')"
            ), error()

        with And("join merge tree table to iceberg table"):
            result = node.query(
                f"""
                SELECT *
                FROM {table_name} AS t1
                JOIN {merge_tree_table_name} AS t2
                ON t1.boolean_col = t2.boolean_col
                ORDER BY tuple(*)
                FORMAT Values
                """
            )
            assert (
                result.output.strip()
                == "(false,2000,456.78,'Bob','2023-05-15',false,2,2,'b','2021-01-01'),(false,2000,456.78,'Bob','2023-05-15',false,4,4,'d','2021-01-01'),(false,4000,8.9,'1','2021-01-01',false,2,2,'b','2021-01-01'),(false,4000,8.9,'1','2021-01-01',false,4,4,'d','2021-01-01'),(true,1000,456.78,'Alice','2024-01-01',true,1,1,'a','2021-01-01'),(true,1000,456.78,'Alice','2024-01-01',true,3,3,'c','2021-01-01'),(true,3000,6.7,'Charlie','2022-01-01',true,1,1,'a','2021-01-01'),(true,3000,6.7,'Charlie','2022-01-01',true,3,3,'c','2021-01-01')"
            ), error()

        with And("join iceberg table to merge tree table"):
            result = node.query(
                f"""
                SELECT *
                FROM {merge_tree_table_name} AS t1
                JOIN {table_name} AS t2
                ON t1.boolean_col = t2.boolean_col
                ORDER BY tuple(*)
                FORMAT Values
                """
            )
            assert (
                result.output.strip()
                == "(false,2,2,'b','2021-01-01',false,2000,456.78,'Bob','2023-05-15'),(false,2,2,'b','2021-01-01',false,4000,8.9,'1','2021-01-01'),(false,4,4,'d','2021-01-01',false,2000,456.78,'Bob','2023-05-15'),(false,4,4,'d','2021-01-01',false,4000,8.9,'1','2021-01-01'),(true,1,1,'a','2021-01-01',true,1000,456.78,'Alice','2024-01-01'),(true,1,1,'a','2021-01-01',true,3000,6.7,'Charlie','2022-01-01'),(true,3,3,'c','2021-01-01',true,1000,456.78,'Alice','2024-01-01'),(true,3,3,'c','2021-01-01',true,3000,6.7,'Charlie','2022-01-01')"
            ), error()
    finally:
        with Finally("drop merge tree table"):
            node.query(f"DROP TABLE {merge_tree_table_name}")


@TestScenario
def order_by_clause(self, table_name, node=None):
    """Check reading data from ClickHouse table from Iceberg database with different order by clauses."""
    if node is None:
        node = self.context.node

    result_order_by_boolean_col = node.query(
        f"""
            SELECT * FROM {table_name} 
            ORDER BY boolean_col, long_col
            FORMAT Values
        """
    )
    assert (
        result_order_by_boolean_col.output.strip()
        == "(false,2000,456.78,'Bob','2023-05-15'),(false,4000,8.9,'1','2021-01-01'),(true,1000,456.78,'Alice','2024-01-01'),(true,3000,6.7,'Charlie','2022-01-01')"
    ), error()

    result_order_by_long_col = node.query(
        f"""
            SELECT * FROM {table_name} 
            ORDER BY long_col
            FORMAT Values
        """
    )
    assert (
        result_order_by_long_col.output.strip()
        == "(true,1000,456.78,'Alice','2024-01-01'),(false,2000,456.78,'Bob','2023-05-15'),(true,3000,6.7,'Charlie','2022-01-01'),(false,4000,8.9,'1','2021-01-01')"
    ), error()

    result_order_by_double_col = node.query(
        f"""
            SELECT * FROM {table_name} 
            ORDER BY double_col, string_col
            FORMAT Values
        """
    )
    assert (
        result_order_by_double_col.output.strip()
        == "(true,3000,6.7,'Charlie','2022-01-01'),(false,4000,8.9,'1','2021-01-01'),(true,1000,456.78,'Alice','2024-01-01'),(false,2000,456.78,'Bob','2023-05-15')"
    ), error()

    result_order_by_string_col = node.query(
        f"""
            SELECT * FROM {table_name}  
            ORDER BY string_col
            FORMAT Values
        """
    )
    assert (
        result_order_by_string_col.output.strip()
        == "(false,4000,8.9,'1','2021-01-01'),(true,1000,456.78,'Alice','2024-01-01'),(false,2000,456.78,'Bob','2023-05-15'),(true,3000,6.7,'Charlie','2022-01-01')"
    ), error()

    result_order_by_date_col = node.query(
        f"""
            SELECT * FROM {table_name}  
            ORDER BY date_col
            FORMAT Values
        """
    )
    assert (
        result_order_by_date_col.output.strip()
        == "(false,4000,8.9,'1','2021-01-01'),(true,3000,6.7,'Charlie','2022-01-01'),(false,2000,456.78,'Bob','2023-05-15'),(true,1000,456.78,'Alice','2024-01-01')"
    ), error()


@TestFeature
@Name("sql clauses")
def feature(self, minio_root_user, minio_root_password):
    """Test various SQL operations on Iceberg database tables including WHERE, GROUP BY, HAVING,
    LIMIT, DISTINCT, and JOIN clauses."""

    with By("create catalog and Iceberg table with 5 columns and 4 rows"):
        table_name, namespace = (
            catalog_steps.create_catalog_and_iceberg_table_with_data(
                minio_root_user=minio_root_user, minio_root_password=minio_root_password
            )
        )

    with And("create database with Iceberg engine"):
        database_name = f"database_{getuid()}"
        iceberg_engine.drop_database(database_name=database_name)
        iceberg_engine.create_experimental_iceberg_database(
            database_name=database_name,
            s3_access_key_id=minio_root_user,
            s3_secret_access_key=minio_root_password,
        )

    clickhouse_iceberg_table_name = f"{database_name}.\\`{namespace}.{table_name}\\`"

    Scenario(test=where_clause)(
        table_name=clickhouse_iceberg_table_name,
    )
    Scenario(test=prewhere_clause)(
        table_name=clickhouse_iceberg_table_name,
    )
    Scenario(test=group_by_clause)(
        table_name=clickhouse_iceberg_table_name,
    )
    Scenario(test=having_clause)(
        table_name=clickhouse_iceberg_table_name,
    )
    Scenario(test=limit_clause)(
        table_name=clickhouse_iceberg_table_name,
    )
    Scenario(test=distinct_clause)(
        table_name=clickhouse_iceberg_table_name,
    )
    Scenario(test=join_clause)(
        table_name=clickhouse_iceberg_table_name,
    )
    Scenario(test=order_by_clause)(
        table_name=clickhouse_iceberg_table_name,
    )
