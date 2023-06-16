from testflows.core import *
from session_timezone.requirements import *
from testflows.asserts import error
from session_timezone.tests.steps import *


@TestFeature
@Requirements(
    RQ_SRS_037_ClickHouse_SessionTimezone_ParsingOfDateTimeTypes_Insert("1.0")
)
def different_types_insert(self):
    """Simple check of different Date and DateTime type  with session_timezone setting."""
    note("check results with andrey")
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_tz{getuid()}"

    types = ["Date", "DateTime", "DateTime64", "DateTime('UTC')"]

    for type in types:
        with Check(f"{type}"):
            try:
                with Given("I create table with DateTime datatype"):
                    node.query(
                        f"CREATE TABLE IF NOT EXISTS {table_name} (d {type}) Engine=Memory AS SELECT toDateTime('2000-01-01 00:00:00');"
                    )

                with When("I insert data with enabled 'session_timezone' setting "):
                    node.query(
                        (" SET session_timezone = 'Asia/Novosibirsk';")
                        + (f"INSERT INTO {table_name} VALUES ('2000-01-01 01:00:00')")
                    )
                    node.query(
                        (" SET session_timezone = 'Asia/Novosibirsk';")
                        + (
                            f"INSERT INTO {table_name} VALUES (toDateTime('2000-01-02 02:00:00'))"
                        )
                    )

                with Then(
                    "I check that session_timezone setting affects correct on parse DateTime type"
                ):
                    node.query(
                        f"SELECT count()+1 FROM {table_name} WHERE d == '{'2000-01-01' if type is 'Date' else '2000-01-01 01:00:00'}';",
                        message=f"{'2' if type.endswith(')') else '3' if type is 'Date' else '1'}",
                    )
                    node.query(
                        f"SELECT count()+1 FROM {table_name} WHERE d == toDateTime('{'2000-01-01' if type is 'Date' else '2000-01-01 02:00:00'}');",
                        message=f"{'2' if type.endswith(')') else '3' if type is 'Date' else '1'}",
                    )
            finally:
                node.query(f"DROP TABLE IF EXISTS {table_name};")


@TestFeature
@Name("tables with date columns")
def feature(self):
    """Check tables with date, datetime, datetime64 columns."""
    with Pool(1) as executor:
        try:
            for feature in loads(current_module(), Feature):
                if not feature.name.endswith("date columns"):
                    Feature(test=feature, parallel=True, executor=executor)()
        finally:
            join()

    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()