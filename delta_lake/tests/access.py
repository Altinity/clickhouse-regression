"""Read a Delta table on RustFS without opening a Unity database.

Each scenario creates a table, reads it one way, and checks the result.
"""

from testflows.core import *

from delta_lake.requirements.requirements import (
    RQ_SRS_050_ClickHouse_DeltaLake_Access_Cluster,
    RQ_SRS_050_ClickHouse_DeltaLake_Access_Credentials,
    RQ_SRS_050_ClickHouse_DeltaLake_Access_Engine,
    RQ_SRS_050_ClickHouse_DeltaLake_Access_NamedCollection,
    RQ_SRS_050_ClickHouse_DeltaLake_Access_TableFunction,
    RQ_SRS_050_ClickHouse_DeltaLake_Access_TableFunction_Backends,
    RQ_SRS_050_ClickHouse_DeltaLake_Create_AttachExisting,
)
from delta_lake.tests.steps import column, create_delta_table, list_keys
from delta_lake.tests.steps.access import (
    create_engine_table,
    create_named_collection,
    create_parquet_prefix,
    expect_failed,
    expect_lines,
    expect_log_columns,
    expect_no_delta_log,
    expect_same_keys,
    expect_show_create,
    prefix_http_url,
    read_collection,
    read_function,
    read_source,
    try_engine,
    try_function,
)

ROWS = (
    ("Alice", 20),
    ("Bob", 30),
    ("Charlie", 40),
)

COLUMNS = (
    column("name", "STRING", "string", "string"),
    column("value", "LONG", "bigint", "long"),
)

EXPECTED = [
    "Alice\t20",
    "Bob\t30",
    "Charlie\t40",
]

EXPECTED_COLUMNS = [
    ("name", "Nullable(String)"),
    ("value", "Nullable(Int64)"),
]

CLUSTER = "test_cluster_two_shards_localhost"
PARQUET_MARKER = "not-a-delta-row"
WRONG_SECRET = "wrong-secret"
WRONG_KEY = "wrong-key"


def new_table():
    return create_delta_table(
        columns=COLUMNS, rows=ROWS, register=False, create_schema=False
    )


@TestScenario
@Name("table function")
@Requirements(
    RQ_SRS_050_ClickHouse_DeltaLake_Access_TableFunction("1.0"),
    RQ_SRS_050_ClickHouse_DeltaLake_Access_TableFunction_Backends("1.0"),
)
def table_function(self):
    """deltaLake and deltaLakeS3 return the rows written to RustFS."""

    with Given("I create a Delta table"):
        table = new_table()

    with When("I read it with deltaLake"):
        result = read_function(function="deltaLake", url=table.http_url)

    with Then("I get the written rows"):
        expect_lines(result=result, expected=EXPECTED)

    with And("DESCRIBE names the columns from the log"):
        expect_log_columns(
            function="deltaLake", url=table.http_url, columns=EXPECTED_COLUMNS
        )

    with When("I read it with deltaLakeS3"):
        result = read_function(function="deltaLakeS3", url=table.http_url)

    with Then("I get the same rows"):
        expect_lines(result=result, expected=EXPECTED)

    with When("I pass format Parquet and no structure"):
        result = read_function(
            function="deltaLake", url=table.http_url, data_format="Parquet"
        )

    with Then("I still get the written rows"):
        expect_lines(result=result, expected=EXPECTED)


@TestScenario
@Name("table engine")
@Requirements(
    RQ_SRS_050_ClickHouse_DeltaLake_Access_Engine("1.0"),
    RQ_SRS_050_ClickHouse_DeltaLake_Create_AttachExisting("1.0"),
)
def table_engine(self):
    """ENGINE = DeltaLake attaches with no column list."""

    with Given("I create a Delta table"):
        table = new_table()

    with When("I attach it with ENGINE = DeltaLake"):
        name = create_engine_table(url=table.http_url)

    with Then("SHOW CREATE lists the log schema"):
        expect_show_create(
            table_name=name, marker=table.prefix, columns=EXPECTED_COLUMNS
        )

    with When("I select from the engine table"):
        result = read_source(source=name)

    with Then("I get the written rows"):
        expect_lines(result=result, expected=EXPECTED)


@TestScenario
@Name("credentials")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Access_Credentials("1.0"))
def wrong_credentials(self):
    """A wrong secret or access key fails the read. The files stay put."""

    with Given("I create a Delta table"):
        table = new_table()

    with When("I record the files in the bucket"):
        before = list_keys(prefix=table.prefix)

    with When("I read deltaLake with a wrong secret"):
        result = try_function(
            function="deltaLake", url=table.http_url, secret_key=WRONG_SECRET
        )

    with Then("the read fails"):
        expect_failed(result=result, forbidden="Alice")

    with When("I read deltaLake with a wrong access key"):
        result = try_function(
            function="deltaLake", url=table.http_url, access_key=WRONG_KEY
        )

    with Then("that read fails too"):
        expect_failed(result=result, forbidden="Alice")

    with When("I attach the engine with a wrong secret"):
        result = try_engine(url=table.http_url, secret_key=WRONG_SECRET)

    with Then("the attach fails"):
        expect_failed(result=result, forbidden="Alice")

    with And("the files in the bucket are unchanged"):
        expect_same_keys(prefix=table.prefix, expected=before)


@TestScenario
@Name("missing delta log")
@Requirements(
    RQ_SRS_050_ClickHouse_DeltaLake_Access_TableFunction("1.0"),
    RQ_SRS_050_ClickHouse_DeltaLake_Create_AttachExisting("1.0"),
)
def missing_delta_log(self):
    """A Parquet file with no _delta_log is not a Delta table."""

    with Given("I upload a Parquet file and no _delta_log"):
        prefix = create_parquet_prefix(marker=PARQUET_MARKER)

    with When("I record the files"):
        before = list_keys(prefix=prefix)

    with When("I read that path with deltaLake"):
        result = try_function(function="deltaLake", url=prefix_http_url(prefix))

    with Then("the read fails and the Parquet row does not come back"):
        expect_failed(result=result, forbidden=PARQUET_MARKER)

    with When("I attach an engine at that path"):
        result = try_engine(url=prefix_http_url(prefix))

    with Then("the attach fails"):
        expect_failed(result=result, forbidden=PARQUET_MARKER)

    with And("the path still has no _delta_log"):
        expect_no_delta_log(prefix=prefix, before=before)


@TestScenario
@Name("named collection")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Access_NamedCollection("1.0"))
def named_collection(self):
    """A named collection supplies the URL and the keys."""

    with Given("I create a Delta table"):
        table = new_table()

    with And("I store the URL and the keys in a named collection"):
        collection = create_named_collection(url=table.http_url)

    with When("I read it with deltaLake and the collection"):
        result = read_collection(function="deltaLake", collection=collection)

    with Then("I get the written rows"):
        expect_lines(result=result, expected=EXPECTED)

    with When("I attach the engine with the collection"):
        name = create_engine_table(collection=collection)

    with When("I select from the engine table"):
        result = read_source(source=name)

    with Then("I get the written rows"):
        expect_lines(result=result, expected=EXPECTED)


@TestScenario
@Name("cluster")
@Requirements(RQ_SRS_050_ClickHouse_DeltaLake_Access_Cluster("1.0"))
def cluster(self):
    """deltaLakeCluster on two local shards returns the same rows."""

    with Given("I create a Delta table"):
        table = new_table()

    with When("I read it with deltaLakeCluster"):
        result = read_function(
            function="deltaLakeCluster", url=table.http_url, cluster=CLUSTER
        )

    with Then("I get the written rows"):
        expect_lines(result=result, expected=EXPECTED)

    with When("I read it with deltaLakeS3Cluster"):
        result = read_function(
            function="deltaLakeS3Cluster", url=table.http_url, cluster=CLUSTER
        )

    with Then("I get the same rows"):
        expect_lines(result=result, expected=EXPECTED)


@TestFeature
@Name("delta access")
def feature(self):
    """Delta Lake reads directly from RustFS."""
    Scenario(test=table_function)()
    Scenario(test=table_engine)()
    Scenario(test=wrong_credentials)()
    Scenario(test=missing_delta_log)()
    Scenario(test=named_collection)()
    Scenario(test=cluster)()
