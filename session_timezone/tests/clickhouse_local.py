from testflows.core import *
from session_timezone.requirements import *
from testflows.asserts import error
from session_timezone.tests.steps import *


@TestScenario
def bad_arguments(self):
    """Check behavior with bad arguments."""
    with Check(
        "I check that attempting to use the timezone with incorrect or invalid arguments lead to an exception"
    ):
        clickhouse_local(
            query="select timezoneOf(now()) SETTINGS session_timezone = 'fasdf' format TSV;",
            message="Exception: Invalid time zone",
        )


@TestScenario
def timezone_default(self):
    """Verify that the session_timezone is set to the default value when it is not explicitly defined."""
    node = self.context.cluster.node("clickhouse1")

    with Check(
        "I check timezone(), timezoneOf(now()) without session_timezone setting"
    ):
        clickhouse_local(
            query="SELECT timezone(), timezoneOf(now()) FORMAT CSV;",
            message='"UTC","UTC"',
        )


@TestScenario
def timezone_default_value(self):
    """Verify that the session_timezone is set to the default value if it is set to an empty string."""
    with Check(
        "I check timezone(), timezoneOf(now()) with session_timezone is set to an empty string"
    ):
        clickhouse_local(
            query="SELECT timezone(), timezoneOf(now()) SETTINGS session_timezone = '' FORMAT CSV;",
            message='"UTC","UTC"',
        )


@TestScenario
def set_timezone(self):
    """Check behavior of `toDateTime64` with `SET session_timezone`."""
    with Check(
        "I check that timezone is changing when `SET session_timezone` is applied"
    ):
        clickhouse_local(
            query=("SET session_timezone = 'Asia/Novosibirsk';")
            + (
                "SELECT toDateTime64(toDateTime64('2022-12-12 23:23:23.123', 3), 3, 'Europe/Zurich');"
            ),
            message="2022-12-12 17:23:23.123",
        )


@TestScenario
def set_timezone_with_the_same_continent(self):
    """Check behavior of `toDateTime64` with `SET session_timezone` when it has the same continent."""
    with Check(
        "I confirm that the timezone is updated when the SET session_timezone command is executed with a continent "
        "value that matches the current timezone."
    ):
        clickhouse_local(
            query=("SET session_timezone = 'Asia/Manila';")
            + (
                "SELECT toDateTime64(toDateTime64('2022-12-12 23:23:23.123', 3), 3, 'Asia/Novosibirsk');"
            ),
            message="2022-12-12 22:23:23.123",
        )


@TestScenario
def set_and_setting_timezone(self):
    """Check behavior of `toDateTime64` with `SET session_timezone` and `SETTING timezone."""
    with Check(
        "I verify that the `SET session_timezone` command does not affect queries using "
        "the `SETTINGS session_timezone` option."
    ):
        clickhouse_local(
            query=("SET session_timezone = 'Asia/Novosibirsk';")
            + (
                "SELECT toDateTime64(toDateTime64('2022-12-12 23:23:23.123', 3), 3, 'Europe/Zurich') "
                "SETTINGS session_timezone = 'Europe/Zurich';"
            ),
            message="2022-12-12 23:23:23.123",
        )


@TestScenario
def timezone_and_timezone_of_now(self):
    """Check that session_timezone is changing timezone() and timezoneOf(now())."""
    with Check(
        "I check that `SETTINGS session_timezone` is changing timezone(), timezoneOf(now())"
    ):
        clickhouse_local(
            query="SELECT timezone(), timezoneOf(now()) SETTINGS session_timezone = 'Europe/Zurich' "
            "FORMAT CSV;",
            message='"Europe/Zurich","Europe/Zurich"',
        )
        clickhouse_local(
            query="SELECT timezone(), timezoneOf(now()) SETTINGS session_timezone = 'Pacific/Pitcairn' FORMAT CSV;",
            message='"Pacific/Pitcairn","Pacific/Pitcairn"',
        )


@TestScenario
def date_datetime_column_types(self):
    """Check the way session_timezone setting affects parsing of Date or DateTime types."""
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_tz{getuid()}"
    with Check(
        "I create table with DateTime('UTC') datatype and heck the way session_timezone setting affects "
        "parsing of Date or DateTime types"
    ):
        clickhouse_local(
            query=f"create table {table_name} (d DateTime) Engine=Memory as select "
            "toDateTime('2000-01-01 00:00:00', 'UTC');"
            f" select *, timezone() from {table_name} where d = toDateTime('2000-01-01 00:00:00')"
            " settings session_timezone ='Asia/Novosibirsk' FORMAT TSV;"
        )

        clickhouse_local(
            query=f"create table {table_name} (d DateTime) Engine=Memory as select "
            "toDateTime('2000-01-01 00:00:00', 'UTC');"
            f" select *, timezone() from {table_name} where d = '2000-01-01 00:00:00' "
            "settings session_timezone ='Asia/Novosibirsk' FORMAT TSV;",
            message="2000-01-01 00:00:00\tAsia/Novosibirsk",
        )


@TestScenario
def all_possible_values_of_timezones(self):
    """Check all possible timezones"""
    node = self.context.cluster.node("clickhouse1")

    number_of_timezones = node.query(
        "SELECT count() FROM system.time_zones"
    ).output.strip()

    with Check("I check all possible timezones from system.time_zones table"):
        for i in range(0, int(number_of_timezones)):
            time_zone = node.query(
                f"select time_zone from "
                f"(select *,ROW_NUMBER() OVER (ORDER BY time_zone) as order_number from system.time_zones)"
                f" WHERE order_number = {i+1}"
            ).output.strip()
            with Step(
                f"I check that `session_timezone` is changing timezone to {time_zone}"
            ):
                clickhouse_local(
                    query=f"SELECT timezone() SETTINGS session_timezone = '{time_zone}' "
                    "FORMAT TSV;",
                    message=f"{time_zone}",
                )


@TestFeature
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_ClickhouseLocal("1.0"))
@Name("clickhouse local")
def feature(self):
    """Check all basic suites in clickhouse local with `UTC` timezone."""
    for scenario in loads(current_module(), Scenario):
        scenario()
