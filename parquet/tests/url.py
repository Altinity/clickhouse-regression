from testflows.core import *
from parquet.requirements import *
from parquet.tests.common import *
from helpers.common import *


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_URL("1.0"))
def insert_into_engine(self):
    """Check that when data is inserted into a table with `URL` engine, it is written into the source file correctly."""
    self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    node = self.context.node
    table_name = "table_" + getuid()

    with Given("I have a table with a `URL` engine"):
        table = create_table(
            name=table_name,
            engine=f"URL('http://bash-tools:5000/{table_name}.Parquet', 'Parquet')",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with And(
        "I populate table with test data",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        table.insert_test_data()

    with Check(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        node.command(
            f"cp /share/app_files/{table_name}.Parquet /var/lib/clickhouse/user_files/{table_name}.Parquet"
        )
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{table_name}.Parquet",
            reference_table_name=table_name,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_URL("1.0"))
def select_from_engine(self):
    """Check that when a table with `URL` engine is attached on top of a Parquet file, it reads the data correctly."""
    self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    node = self.context.node
    table_name = "table_" + getuid()
    table_columns = self.context.parquet_table_columns

    node.command(f"mkdir /var/lib/clickhouse/user_files/{table_name}")
    node.command(
        f"cp /var/lib/test_files/data_NONE.Parquet /var/lib/clickhouse/user_files/{table_name}/data.Parquet"
    )

    with Given("I attach a table with a `URL` engine on top of a Parquet file"):
        create_table(
            name=table_name,
            engine="URL('http://bash-tools:5000/data_NONE.Parquet', 'Parquet')",
            columns=table_columns,
        )

    with Check("I check that the table reads the data correctly"):
        with Pool(3) as executor:
            for column in table_columns:
                Check(
                    test=execute_query_step,
                    name=f"{column.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM {table_name}"
                )
            join()


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_URL("1.0"))
def engine_to_file_to_engine(self):
    """Check that when data is inserted into a table with `URL` engine,
    the data can be read back correctly from the source file using a different table with `URL` engine.
    """
    self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    node = self.context.node
    table0_name = "table0_" + getuid()
    table1_name = "table1_" + getuid()

    with Given("I have a table with a `URL` engine"):
        table0 = create_table(
            name=table0_name,
            engine=f"URL('http://bash-tools:5000/{table0_name}.Parquet', 'Parquet')",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with When(
        "I insert data into the table",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        table0.insert_test_data()

    with Check(
        "I check that the data inserted into the table was correctly written into the file"
    ):
        node.command(
            f"cp /share/app_files/{table0_name}.Parquet /var/lib/clickhouse/user_files/{table0_name}.Parquet"
        )
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{table0_name}.Parquet",
            reference_table_name=table0_name,
        )

    with When("I copy of the Parquet source file to a new directory"):
        node.command(
            f"cp /share/app_files/{table0_name}.Parquet /share/app_files/{table1_name}.Parquet"
        )

    with Given("I have a table with a `URL` engine"):
        table1 = create_table(
            name=table1_name,
            engine=f"URL('http://bash-tools:5000/{table1_name}.Parquet', 'Parquet')",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with Check(
        "I check that the new table is able to read the data from the file correctly"
    ):
        with Pool(3) as executor:
            for column in table1.columns:
                r = node.query(
                    f"SELECT {column.name}, toTypeName({column.name}) FROM {table0_name}"
                    + " FORMAT JSONEachRow",
                    exitcode=0,
                )
                Check(
                    test=execute_query_step,
                    name=f"{column.name}",
                    parallel=True,
                    executor=executor,
                )(
                    sql=f"SELECT {column.name}, toTypeName({column.name}) FROM {table1.name}",
                    expected=r.output.strip(),
                )
            join()


@TestOutline(Scenario)
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Compression_None("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"),
)
@Examples(
    "compression_type",
    [
        (
            "NONE",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_None("1.0")),
        ),
        (
            "GZIP",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0")),
        ),
        (
            "LZ4",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0")),
        ),
    ],
)
def insert_into_engine_from_file(self, compression_type):
    """Check that that data read from a Parquet file using the `INFILE` clause in `INSERT` query is
    correctly written into a table with a `URL` engine."""
    self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    node = self.context.node
    table_name = "table_" + getuid()
    table_columns = self.context.parquet_table_columns

    with Given("I have a table with a `URL` engine"):
        create_table(
            name=table_name,
            engine=f"URL('http://bash-tools:5000/{table_name}.Parquet', 'Parquet')",
            columns=table_columns,
        )

    with When("I insert data into the table from a Parquet file"):
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/data_{compression_type}.Parquet' FORMAT Parquet"
        )

    with Check("I check that the table contains correct data"):
        for column in table_columns:
            with Check(f"{column.name}"):
                execute_query(
                    f"SELECT {column.name}, toTypeName({column.name}) FROM {table_name}"
                )


@TestOutline(Scenario)
@Requirements(
    RQ_SRS_032_ClickHouse_Parquet_Compression_None("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0"),
    RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0"),
)
@Examples(
    "compression_type",
    [
        (
            "NONE",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_None("1.0")),
        ),
        (
            "GZIP",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Gzip("1.0")),
        ),
        (
            "LZ4",
            Requirements(RQ_SRS_032_ClickHouse_Parquet_Compression_Lz4("1.0")),
        ),
    ],
)
def engine_select_output_to_file(self, compression_type):
    """Check that data is correctly written into a Parquet file when using `SELECT` query with `OUTFILE` clause on a table with `URL` engine."""
    self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    node = self.context.node
    table_name = "table_" + getuid()
    path = f"'/var/lib/clickhouse/user_files/{table_name}_{compression_type}.Parquet'"

    with Given("I have a table with a `URL` engine"):
        table = create_table(
            name=table_name,
            engine=f"URL('http://bash-tools:5000/{table_name}.Parquet', 'Parquet')",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    with And(
        "I populate table with test data",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        table.insert_test_data()

    with When("I select data from the table and write it into a Parquet file"):
        node.query(
            f"SELECT * FROM {table_name} INTO OUTFILE {path} COMPRESSION '{compression_type.lower()}' FORMAT Parquet"
        )

    with Check("I check that data was written into the Parquet file correctly"):
        node.command(f"cp {path} /var/lib/clickhouse/user_files/{table_name}.Parquet")
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{table_name}.Parquet",
            compression=f"'{compression_type.lower()}'",
            reference_table_name=table_name,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_URL("1.0"))
def insert_into_function(self):
    """Check that when data is inserted into `url` table function with manually defined structure,
    it is written into the source file correctly."""
    self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    node = self.context.node
    file_name = "file_" + getuid() + ".Parquet"
    table_name = "table_" + getuid()
    columns = generate_all_column_types(include=parquet_test_columns())
    func_def = ",".join([column.full_definition() for column in columns])

    columns_values = [column.values(row_count=2, cardinality=1) for column in columns]
    total_values = []

    with Given("I have a table with a `MergeTree` engine"):
        table = create_table(
            name=table_name,
            engine="MergeTree",
            order_by="tuple()",
            columns=generate_all_column_types(include=parquet_test_columns()),
        )

    for row in range(2):
        total_values.append(
            "("
            + ",".join([next(column_values) for column_values in columns_values])
            + ")"
        )

    with When(
        "I insert data into the function",
        description="insert data includes all of the ClickHouse data types supported by Parquet, including nested types and nulls",
    ):
        node.query(
            f"INSERT INTO FUNCTION url('http://bash-tools:5000/{file_name}', 'Parquet', '{func_def}') VALUES {','.join(total_values)}",
            settings=[("allow_suspicious_low_cardinality_types", 1)],
        )

    with Then(
        "I insert the data from the 'file' table function into a MergeTree engine table"
    ):
        node.command(
            f"cp /share/app_files/{file_name} /var/lib/clickhouse/user_files/{file_name}"
        )
        node.query(
            f"INSERT INTO {table_name} FROM INFILE '/var/lib/clickhouse/user_files/{file_name}' FORMAT Parquet",
            settings=[("allow_suspicious_low_cardinality_types", 1)],
        )

    with Check(
        "I check that the data inserted into the table was correctly written to the file"
    ):
        check_source_file(
            path=f"/var/lib/clickhouse/user_files/{file_name}",
            reference_table_name=table_name,
        )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_URL("1.0"))
def select_from_function_manual_cast_types(self):
    """Check that when data is selected from a `url` table function with manually cast column types,
    it is read correctly."""
    self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    table_columns = self.context.parquet_table_columns
    table_def = ",".join([column.full_definition() for column in table_columns])

    with Check("I check that the `file` table function reads data correctly"):
        for column in table_columns:
            with Check(f"{column.name}"):
                execute_query(
                    f"SELECT {column.name}, toTypeName({column.name}) FROM url('http://bash-tools:5000/data_NONE.Parquet', 'Parquet', '{table_def}')"
                )


@TestScenario
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_URL("1.0"))
def select_from_function_auto_cast_types(self):
    """Check that when data is selected from a `url` table function with automatic cast column types,
    it is read correctly."""
    if check_clickhouse_version("<22.6")(self):
        self.context.snapshot_id = get_snapshot_id(clickhouse_version="<22.6")
    else:
        self.context.snapshot_id = get_snapshot_id(clickhouse_version=">=24.1")
    table_columns = self.context.parquet_table_columns

    with Check("I check that the `file` table function reads data correctly"):
        for column in table_columns:
            with Check(f"{column.name}"):
                execute_query(
                    f"SELECT {column.name}, toTypeName({column.name}) FROM url('http://bash-tools:5000/data_NONE.Parquet', 'Parquet')"
                )


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableEngines_Special_URL("1.0"))
def engine(self):
    """Check that table with `URL` engine correctly reads and writes Parquet format."""
    with Pool(5) as executor:
        Scenario(
            run=insert_into_engine,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=select_from_engine,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=engine_to_file_to_engine,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=insert_into_engine_from_file,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=engine_select_output_to_file,
            parallel=True,
            executor=executor,
        )
        join()


@TestSuite
@Requirements(RQ_SRS_032_ClickHouse_Parquet_TableFunctions_URL("1.0"))
def function(self):
    """Check that `url` table function correctly reads and writes Parquet format."""
    with Pool(3) as executor:
        Scenario(
            run=insert_into_function,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=select_from_function_manual_cast_types,
            parallel=True,
            executor=executor,
        )
        Scenario(
            run=select_from_function_auto_cast_types,
            parallel=True,
            executor=executor,
        )
        join()


@TestFeature
@Name("url")
def feature(self, node="clickhouse1"):
    """Run checks for `URL()` table engine and `url` table function when used with Parquet format."""
    self.context.node = self.context.cluster.node(node)
    bash_tools = self.context.cluster.node("bash-tools")

    with Given("I have a directory for the flask server"):
        bash_tools.command("mkdir /share/app_files")
        bash_tools.command("cp /var/lib/test_files/* /share/app_files")

    with self.context.cluster.shell("bash-tools") as bash:
        cmd = "python3 /var/lib/test_files/local_app.py"

        try:
            with Given("I launch the flask server"):
                bash.send(cmd)
                bash.expect(cmd, escape=True)
                bash.expect("\n")
                bash.expect("Serving Flask app 'local_app'", escape=True)
            with Pool(2) as executor:
                Suite(run=engine, parallel=True, executor=executor)
                Suite(run=function, parallel=True, executor=executor)
                join()
        finally:
            while True:
                try:
                    bash.expect("\n")
                except Exception:
                    break
