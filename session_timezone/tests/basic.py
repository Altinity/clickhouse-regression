from testflows.core import *
from session_timezone.requirements import *
from testflows.asserts import error


@TestScenario
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_WrongSettingValue("1.0"))
def bad_arguments(self):
    """Check behavior with bad arguments."""
    node = self.context.cluster.node("clickhouse1")

    with When("I try that timezone provides exception with bad arguments"):
        node.query(
            "select timezoneOf(now()) SETTINGS session_timezone = 'fasdf' format TSV;",
            exitcode=36,
            message="Exception: Invalid time zone",
        )


@TestScenario
@Requirements()
def set_timezone(self):
    """Check behavior of `toDateTime64` with `SET session_timezone`."""

    node = self.context.cluster.node("clickhouse1")

    with When("I try that timezone is changing when `SET session_timezone` is applied"):
        node.query(
            ("SET session_timezone = 'Asia/Novosibirsk';")
            + (
                "SELECT toDateTime64(toDateTime64('2022-12-12 23:23:23.123', 3), 3, 'Europe/Zurich');"
            ),
            exitcode=0,
            message="2022-12-12 17:23:23.123",
        )


@TestScenario
def set_timezone_with_the_same_continent(self):
    """Check behavior of `toDateTime64` with `SET session_timezone` when it has the same continent."""

    node = self.context.cluster.node("clickhouse1")

    with When(
        "I try that timezone is changing when `SET session_timezone` with the same continent is applied"
    ):
        node.query(
            ("SET session_timezone = 'Asia/Manila';")
            + (
                "SELECT toDateTime64(toDateTime64('2022-12-12 23:23:23.123', 3), 3, 'Asia/Novosibirsk');"
            ),
            exitcode=0,
            message="2022-12-12 22:23:23.123",
        )


@TestScenario
def set_and_setting_timezone(self):
    """Check behavior of `toDateTime64` with `SET session_timezone`and `SETTING timezone."""

    node = self.context.cluster.node("clickhouse1")

    with When(
        "I try that timezone is changing when `SET session_timezone` is not influence on query with "
        "`SETTINGS session_timezone`"
    ):
        node.query(
            ("SET session_timezone = 'Asia/Novosibirsk';")
            + (
                "SELECT toDateTime64(toDateTime64('2022-12-12 23:23:23.123', 3), 3, 'Europe/Zurich') "
                "SETTINGS session_timezone = 'Europe/Zurich';"
            ),
            exitcode=0,
            message="2022-12-12 23:23:23.123",
        )


@TestScenario
def timezone_and_timezone_of_now(self):
    """Check that session_timezone is changing timezone() and timezoneOf(now())."""
    node = self.context.cluster.node("clickhouse1")

    with When("I try to change timezone(), timezoneOf(now())"):
        node.query(
            "SELECT timezone(), timezoneOf(now()) SETTINGS session_timezone = 'Europe/Zurich' FORMAT TSV;",
            message="Europe/Zurich	Europe/Zurich",
        )
        node.query(
            "SELECT timezone(), timezoneOf(now()) SETTINGS session_timezone = 'Pacific/Pitcairn' FORMAT TSV;",
            message="Pacific/Pitcairn	Pacific/Pitcairn",
        )


@TestScenario
def date_datetime_column_types(self):
    """Check the way session_timezone setting affects parsing of Date or DateTime types."""
    xfail("need to finish")
    node = self.context.cluster.node("clickhouse1")

    with Given("I create table with DateTime('UTC') datatype"):
        node.query(
            "CREATE TABLE test_tz (d DateTime('UTC')) ENGINE = Memory AS SELECT "
            "toDateTime('2000-01-01 00:00:00', 'UTC');"
        )

    with Then(
        "I check the way session_timezone setting affects parsing of Date or DateTime types"
    ):
        node.query(
            "SELECT *, timezone() FROM test_tz WHERE d = toDateTime('2000-01-01 00:00:00') "
            "SETTINGS session_timezone = 'Asia/Novosibirsk'"
        )
        node.query(
            "SELECT *, timezone() FROM test_tz WHERE d = '2000-01-01 00:00:00' "
            "SETTINGS session_timezone = 'Asia/Novosibirsk' FORMAT TSV;",
            message="2000-01-01 00:00:00   Asia/Novosibirsk"
        )


@TestFeature
@Name("basic")
def feature(self):
    """Basic check suites."""
    for scenario in loads(current_module(), Scenario):
        scenario()
