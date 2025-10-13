from testflows.core import *
from testflows.combinatorics import product
from hive_partitioning.tests.steps import *
from hive_partitioning.requirements.requirements import *
from helpers.common import run_duckdb_query


@TestScenario
def duckdb_supported_types(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that DuckDB supports all the data types for hive partitioning."""

    data_types_examples = duckdb_data_types

    if node is None:
        node = self.context.node

    with Given("I set s3 connection parameters for DuckDB"):
        run_duckdb_query(
            query=f"""
            SET s3_endpoint='localhost:9001';
            SET s3_access_key_id='{minio_root_user}';
            SET s3_secret_access_key='{minio_root_password}';
            SET s3_use_ssl=false;
            SET s3_url_style='path';
        """
        )

    for data_type, value in data_types_examples:
        with Check(f"I check {data_type}"):

            table_name = (
                f"test_{data_type}".replace("(", "_")
                .replace(")", "")
                .replace(",", "_")
                .replace(" ", "_")
                .replace("<", "_")
                .replace(">", "_")
                .replace("[]", "_")
                .replace("'", "")
                .replace('"', "")
            )
            with When("I create table for hive partition writes"):
                debug(f"CREATE TABLE {table_name} (p {data_type}, i Int32)")
                run_duckdb_query(
                    query=f"CREATE TABLE {table_name} (p {data_type}, i Int32)"
                )

            with And("I insert data into table"):
                run_duckdb_query(query=f"INSERT INTO {table_name} VALUES ({value}, 1)")

            with And("I copy data to s3"):
                run_duckdb_query(
                    query=f"COPY {table_name} TO 's3://root/data/{table_name}/' (FORMAT 'parquet', PARTITION_BY ('p'))"
                )

            with Then("I check data in table"):
                data = run_duckdb_query(
                    query=f"SELECT i FROM read_parquet('s3://root/data/{table_name}/**') WHERE p = {value}"
                )
                assert data == [(1,)], error()


@TestScenario
def duckdb_supported_characters(
    self, uri, uri_readonly, minio_root_user, minio_root_password, node=None
):
    """Check that DuckDB supports all the UTF-8 characters for hive partitioning."""

    if node is None:
        node = self.context.node

    with Given("I set s3 connection parameters for DuckDB"):
        run_duckdb_query(
            query=f"""
            SET s3_endpoint='localhost:9001';
            SET s3_access_key_id='{minio_root_user}';
            SET s3_secret_access_key='{minio_root_password}';
            SET s3_use_ssl=false;
            SET s3_url_style='path';
        """
        )

    if self.context.stress:
        characters_range = range(32, 1114111, 16)
    else:
        characters_range = range(32, 256, 16)

    for i in characters_range:
        string = "".join([chr(j) for j in range(i, i + 16)])
        with Check(f"I check string with characters from {i} to {i+16}"):
            table_name = f"test_characters_{i}_{i+16}"
            with When("I create table for hive partition writes"):
                run_duckdb_query(query=f"CREATE TABLE {table_name} (d String, i Int32)")
                print(string)
            with And("I insert data into table"):
                if "'" in string:
                    string = string.replace("'", "")
                run_duckdb_query(
                    query=f"INSERT INTO {table_name} VALUES ('{string}', 1)"
                )

            with And("I copy data to s3"):
                run_duckdb_query(
                    query=f"COPY {table_name} TO 's3://root/data/{table_name}/' (FORMAT 'parquet', PARTITION_BY ('d'))"
                )

            with Then("I check data in table"):
                data = run_duckdb_query(
                    query=f"SELECT i FROM read_parquet('s3://root/data/{table_name}/**') WHERE d = '{string}'"
                )
                assert data == [(1,)], error()


@TestFeature
@Name("duckdb")
def feature(
    self, uri=None, minio_root_user=None, minio_root_password=None, uri_readonly=None
):
    """Run duckdb writes test."""
    if uri is None:
        uri = self.context.uri
    if minio_root_user is None:
        minio_root_user = self.context.root_user
    if minio_root_password is None:
        minio_root_password = self.context.root_password

    for scenario in loads(current_module(), Scenario):
        Scenario(
            test=scenario,
        )(
            uri=uri,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            uri_readonly=uri_readonly,
        )
