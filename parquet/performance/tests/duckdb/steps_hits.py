from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid
import time


@TestOutline
def run_query(self, name: str, clickhouse_query: str, duckdb_query: str, database: str):
    """Run the query on clickhouse and duckdb and collect the metrics of execution time for each.
    :param name: name of the query that is being run
    :param clickhouse_query: full query being run in ClickHouse
    :param duckdb_query: full query being run in DuckDB
    """

    clickhouse_node = self.context.clickhouse_node
    duckdb_node = self.context.duckdb_node
    duckdb_database = "db_" + getuid()
    repeats = self.context.run_count
    if database == "clickhouse":
        with By("running the query on clickhouse", description=f"{clickhouse_query}"):
            clickhouse_times = []
            for _ in range(repeats):
                start_time = time.time()
                clickhouse_node.query(clickhouse_query)
                clickhouse_run_time = time.time() - start_time
                clickhouse_times.append(clickhouse_run_time)
            metric(name="clickhouse-" + name, value=min(clickhouse_times), units="s")

        csv_result = (
            name,
            self.context.clickhouse_version,
            clickhouse_run_time,
            clickhouse_query,
        )

        for i in range(repeats):
            csv_result += (clickhouse_times[i],)

        self.context.query_results_hits.append(csv_result)

    elif database == "duckdb":
        with By("running the query on duckdb", description=f"{duckdb_query}"):
            duckdb_times = []
            for _ in range(repeats):
                start_time = time.time()
                duckdb_node.command(
                    f'duckdb {duckdb_database} "{duckdb_query}"', exitcode=0
                )
                duckdb_run_time = time.time() - start_time
                duckdb_times.append(duckdb_run_time)
            metric(name="duckdb-" + name, value=min(duckdb_times), units="s")
        csv_result = (
            name,
            self.context.duckdb_version,
            duckdb_run_time,
            duckdb_query,
        )

        for i in range(repeats):
            csv_result += (duckdb_times[i],)

        self.context.query_results_hits.append(csv_result)


@TestScenario
def get_row_count(self, filename: str):
    """Calculating and uploading the row count of the parquet file into the CSV."""
    clickhouse_node = self.context.clickhouse_node

    with Given("I select the number of rows from the parquet file"):
        rows = clickhouse_node.query(f"SELECT count() FROM file({filename})")
    self.context.row_count.append(rows.output.strip())


@TestStep
def query_0(self, filename: str, database: str):
    r = "SELECT COUNT(*) FROM {filename};"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_0",
        database=database,
    )


@TestStep
def query_1(self, filename: str, database: str):
    r = "SELECT COUNT(*) FROM {filename} WHERE AdvEngineID <> 0;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_1",
        database=database,
    )


@TestStep
def query_2(self, filename: str, database: str):
    r = "SELECT SUM(AdvEngineID), COUNT(*), AVG(ResolutionWidth) FROM {filename};"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_2",
        database=database,
    )


@TestStep
def query_3(self, filename: str, database: str):
    r = "SELECT AVG(UserID) FROM {filename};"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_3",
        database=database,
    )


@TestStep
def query_4(self, filename: str, database: str):
    r = "SELECT COUNT(DISTINCT UserID) FROM {filename};"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_4",
        database=database,
    )


@TestStep
def query_5(self, filename: str, database: str):
    r = "SELECT COUNT(DISTINCT SearchPhrase) FROM {filename};"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_5",
        database=database,
    )


@TestStep
def query_6(self, filename: str, database: str):
    r = "SELECT MIN(EventDate), MAX(EventDate) FROM {filename};"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_6",
        database=database,
    )


@TestStep
def query_7(self, filename: str, database: str):
    r = "SELECT AdvEngineID, COUNT(*) FROM {filename} WHERE AdvEngineID <> 0 GROUP BY AdvEngineID ORDER BY COUNT(*) DESC;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_7",
        database=database,
    )


@TestStep
def query_8(self, filename: str, database: str):
    r = "SELECT RegionID, COUNT(DISTINCT UserID) AS u FROM {filename} GROUP BY RegionID ORDER BY u DESC LIMIT 10;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_8",
        database=database,
    )


@TestStep
def query_9(self, filename: str, database: str):
    r = "SELECT RegionID, SUM(AdvEngineID), COUNT(*) AS c, AVG(ResolutionWidth), COUNT(DISTINCT UserID) FROM {filename} GROUP BY RegionID ORDER BY c DESC LIMIT 10;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_9",
        database=database,
    )


@TestStep
def query_10(self, filename: str, database: str):
    r = "SELECT MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM {filename} WHERE MobilePhoneModel <> '' GROUP BY MobilePhoneModel ORDER BY u DESC LIMIT 10;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_10",
        database=database,
    )


@TestStep
def query_11(self, filename: str, database: str):
    r = "SELECT MobilePhone, MobilePhoneModel, COUNT(DISTINCT UserID) AS u FROM {filename} WHERE MobilePhoneModel <> '' GROUP BY MobilePhone, MobilePhoneModel ORDER BY u DESC LIMIT 10;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_11",
        database=database,
    )


@TestStep
def query_12(self, filename: str, database: str):
    r = "SELECT SearchPhrase, COUNT(*) AS c FROM {filename} WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY c DESC LIMIT 10;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_12",
        database=database,
    )


@TestStep
def query_13(self, filename: str, database: str):
    r = "SELECT SearchPhrase, COUNT(DISTINCT UserID) AS u FROM {filename} WHERE SearchPhrase <> '' GROUP BY SearchPhrase ORDER BY u DESC LIMIT 10;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_13",
        database=database,
    )


@TestStep
def query_14(self, filename: str, database: str):
    r = "SELECT SearchEngineID, SearchPhrase, COUNT(*) AS c FROM {filename} WHERE SearchPhrase <> '' GROUP BY SearchEngineID, SearchPhrase ORDER BY c DESC LIMIT 10;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_14",
        database=database,
    )


@TestStep
def query_15(self, filename: str, database: str):
    r = "SELECT UserID, COUNT(*) FROM {filename} GROUP BY UserID ORDER BY COUNT(*) DESC LIMIT 10;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_15",
        database=database,
    )


@TestStep
def query_16(self, filename: str, database: str):
    r = "SELECT UserID, SearchPhrase, COUNT(*) FROM {filename} GROUP BY UserID, SearchPhrase ORDER BY COUNT(*) DESC LIMIT 10;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_16",
        database=database,
    )


@TestStep
def query_17(self, filename: str, database: str):
    r = "SELECT UserID, SearchPhrase, COUNT(*) FROM {filename} GROUP BY UserID, SearchPhrase LIMIT 10;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_17",
        database=database,
    )


@TestStep
def query_19(self, filename: str, database: str):
    r = "SELECT UserID FROM {filename} WHERE UserID = 435090932899640449;"

    clickhouse_query = r.format(filename=f"file({filename})")
    duckdb_query = r.format(filename=f"'/data1/{filename}'")

    run_query(
        clickhouse_query=clickhouse_query,
        duckdb_query=duckdb_query,
        name="query_19",
        database=database,
    )


@TestSuite
def clickhouse(self, filename):
    duckdb_node = self.context.duckdb_node
    duckdb_node.stop()

    for step in loads(current_module(), Step):
        step(filename=filename, database="clickhouse")

    duckdb_node.start()


@TestScenario
def duckdb(self, filename):
    clickhouse_node = self.context.clickhouse_node
    clickhouse_node.stop()

    for step in loads(current_module(), Step):
        step(filename=filename, database="duckdb")

    clickhouse_node.start()


@TestScenario
def queries_hits(self, filename):
    """Save number of rows of th parquet file into a CSV file and run the set of queries on ClickHouse and DuckDB."""
    Feature(run=get_row_count(filename=filename))
    Feature(test=clickhouse)(filename=filename)
    Feature(test=duckdb)(filename=filename)
