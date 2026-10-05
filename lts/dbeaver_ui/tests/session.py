"""One DBeaver session, as in the manual check: start DBeaver, connect to the
ClickHouse server, create a dataset from the SQL editor, query it and find it
in the navigator. The scenarios run in order and share the session."""

from testflows.core import *
from testflows.asserts import error

from lts.dbeaver_ui.requirements.requirements import (
    RQ_SRS_107_DBeaver_UI_Startup,
    RQ_SRS_107_DBeaver_UI_Connection,
    RQ_SRS_107_DBeaver_UI_Dataset,
    RQ_SRS_107_DBeaver_UI_Queries,
    RQ_SRS_107_DBeaver_UI_Navigator,
    RQ_SRS_107_DBeaver_UI_Screenshots,
)
from lts.dbeaver_ui.steps.environment import clickhouse_query
from lts.dbeaver_ui.steps.desktop import screenshot, wait_for
from lts.dbeaver_ui.steps.dbeaver import (
    expand_node,
    finish_wizard,
    main_window,
    new_connection,
    open_sql_editor,
    refresh_node,
    run_query,
    run_script,
    test_connection,
)

DATABASE = "lts_dbeaver_ui"
TABLE = f"{DATABASE}.events"

# The same dataset as the driver-level DBeaver suite (lts/dbeaver), with a
# fixed `created` so that every value is known.
CREATE_DATASET = f"""DROP DATABASE IF EXISTS {DATABASE};
CREATE DATABASE {DATABASE};
CREATE TABLE {TABLE}
(
    id UInt64,
    name String,
    created DateTime,
    score Nullable(Float64),
    tags Array(String)
)
ENGINE = MergeTree ORDER BY id;
INSERT INTO {TABLE}
SELECT number, concat('name_', toString(number)),
       toDateTime('2024-01-01 00:00:00') + number,
       if(number % 5 = 0, NULL, number / 4), [toString(number), 'tag']
FROM numbers(100);
"""

# Exact results, as the grid shows them. They follow from the dataset: id 0 to
# 99, score NULL for every fifth row (20 rows), two tags per row.
QUERIES = [
    ("count", f"SELECT count(), count(score) FROM {TABLE}", [["100", "80"]]),
    ("aggregates", f"SELECT sum(id), min(id), max(id), uniqExact(name) FROM {TABLE}",
     [["4950", "0", "99", "100"]]),
    ("where", f"SELECT count() FROM {TABLE} WHERE score IS NULL", [["20"]]),
    ("group by", f"SELECT id % 5 AS k, count() FROM {TABLE} GROUP BY k ORDER BY k",
     [[str(k), "20"] for k in range(5)]),
    ("order by limit", f"SELECT id, name FROM {TABLE} ORDER BY id DESC LIMIT 3",
     [["99", "name_99"], ["98", "name_98"], ["97", "name_97"]]),
    ("array join", f"SELECT count(), countIf(tag = 'tag') FROM {TABLE} ARRAY JOIN tags AS tag",
     [["200", "100"]]),
]


@TestScenario
@Requirements(RQ_SRS_107_DBeaver_UI_Startup("1.0"), RQ_SRS_107_DBeaver_UI_Screenshots("1.0"))
def start(self):
    """DBeaver starts with a new workspace and shows its main window."""
    with When("DBeaver's main window shows"):
        main_window(dbeaver_version=self.context.dbeaver_version)

    with Then("I take a screenshot of the main window"):
        screenshot(name="main_window")


@TestScenario
@Requirements(RQ_SRS_107_DBeaver_UI_Connection("1.0"), RQ_SRS_107_DBeaver_UI_Screenshots("1.0"))
def create_connection(self):
    """Create a ClickHouse connection to the local server with the New Database
    Connection wizard and test it."""
    with Given("the server version, from clickhouse-client"):
        version = clickhouse_query("SELECT version()")

    with When("I fill in a new ClickHouse connection"):
        new_connection()

    with And("I test the connection"):
        status, server, driver = test_connection()
        note(f"{status}; server: {server}; driver: {driver}")

    with Then("DBeaver connected"):
        assert status.startswith("Connected"), error(status)

    with And("DBeaver shows the server version"):
        assert version in server, error(f"{version!r} not in {server!r}")

    with When("I finish the wizard"):
        finish_wizard()

    with Then("the connection shows in the navigator"):
        wait_for(role="table cell", name="localhost")
        screenshot(name="connection_created")


@TestScenario
@Requirements(RQ_SRS_107_DBeaver_UI_Dataset("1.0"), RQ_SRS_107_DBeaver_UI_Screenshots("1.0"))
def create_dataset(self):
    """Create a database, a table and 100 rows from DBeaver's SQL editor."""
    with When("I open a SQL editor for the connection"):
        open_sql_editor()

    with And("I run the dataset script"):
        run_script(sql=CREATE_DATASET)
        screenshot(name="dataset_created")

    with Then("the server has the table with 100 rows"):
        rows = clickhouse_query(f"SELECT count() FROM {TABLE}")
        assert rows == "100", error(rows)


@TestScenario
@Requirements(RQ_SRS_107_DBeaver_UI_Queries("1.0"), RQ_SRS_107_DBeaver_UI_Screenshots("1.0"))
def queries(self):
    """Query the dataset from the SQL editor and check the result grid."""
    for name, sql, expected in QUERIES:
        with Check(name, flags=TE):
            with When(f"I run {sql}"):
                rows = run_query(sql=sql)

            with Then("the grid shows the expected rows"):
                screenshot(name=f"query_{name.replace(' ', '_')}")
                assert rows == expected, error(f"{rows} != {expected}")


@TestScenario
@Requirements(RQ_SRS_107_DBeaver_UI_Navigator("1.0"), RQ_SRS_107_DBeaver_UI_Screenshots("1.0"))
def navigator(self):
    """Find the dataset's database, table and columns in the navigator."""
    with When("I refresh and expand the connection"):
        refresh_node(name="localhost")
        expand_node(name="localhost")

    with And("I expand the database and its tables"):
        expand_node(name=DATABASE)
        expand_node(name="Tables")
        expand_node(name="events")
        expand_node(name="Columns")

    with Then("the table's columns show"):
        for column in ("id", "name", "created", "score", "tags"):
            wait_for(role="table cell", name=column)
        screenshot(name="navigator")


@TestFeature
@Name("session")
def feature(self):
    """Run the DBeaver session in order. A failed scenario stops the session,
    because every later scenario depends on the ones before it."""
    for scenario in (start, create_connection, create_dataset, queries, navigator):
        Scenario(run=scenario)
