from testflows.core import *
from session_timezone.requirements import *
from testflows.asserts import error


@TestScenario
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_WrongSettingValue("1.0"))
def bad_arguments(self):
    """Check behavior with bad arguments."""
    node = self.context.cluster.node("clickhouse1")

    with When(
        "I check that attempting to use the timezone with incorrect or invalid arguments lead to an exception"
    ):
        node.query(
            "select timezoneOf(now()) SETTINGS session_timezone = 'fasdf' format TSV;",
            exitcode=36,
            message="Exception: Invalid time zone",
        )


@TestScenario
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_ServerDefault("1.0"))
def timezone_default(self):
    """Verify that the session_timezone is set to the default value if it is not explicitly defined."""
    node = self.context.cluster.node("clickhouse1")

    with When("I check timezone(), timezoneOf(now()) without session_timezone setting"):
        node.query(
            "SELECT timezone(), timezoneOf(now()) FORMAT TSV;",
            message="Europe/Berlin	Europe/Berlin",
        )


@TestScenario
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DefaultValue("1.0"))
def timezone_default_value(self):
    """Verify that the session_timezone is set to the default value if it is set to an empty string."""
    node = self.context.cluster.node("clickhouse1")

    with When(
        "I check timezone(), timezoneOf(now()) with session_timezone is set to an empty string"
    ):
        node.query(
            "SELECT timezone(), timezoneOf(now()) SETTINGS session_timezone = '' FORMAT TSV;",
            message="Europe/Berlin	Europe/Berlin",
        )


@TestScenario
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateTime("1.0"))
def set_timezone(self):
    """Check behavior of `toDateTime64` with `SET session_timezone`."""

    node = self.context.cluster.node("clickhouse1")

    with When(
        "I check that timezone is changing when `SET session_timezone` is applied"
    ):
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
        "I verify that the timezone changes when the SET session_timezone command is applied with a continent value that"
        " is the same as the current timezone."
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
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_SettingsPriority("1.0"))
def set_and_setting_timezone(self):
    """Check behavior of `toDateTime64` with `SET session_timezone`and `SETTING timezone."""

    node = self.context.cluster.node("clickhouse1")

    with When(
        "I check that `SET session_timezone` is not influence on query with `SETTINGS session_timezone`"
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
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_ServerSession("1.0"))
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
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_ParsingOfDateOrDateTimeTypes("1.0"))
def date_datetime_column_types(self):
    """Check the way session_timezone setting affects parsing of Date or DateTime types."""
    node = self.context.cluster.node("clickhouse1")

    try:
        with Given("I create table with DateTime('UTC') datatype"):
            node.query(
                "CREATE TABLE IF NOT EXISTS test_tz (d DateTime('UTC')) ENGINE = Memory AS SELECT "
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
                "SETTINGS session_timezone = 'Asia/Novosibirsk';",
                message="2000-01-01 00:00:00\tAsia/Novosibirsk",
            )

    finally:
        with Finally("I drop test_tz table"):
            node.query("DROP TABLE IF EXISTS test_tz ")


@TestScenario
def clickhouse_local(self):
    """"""
    node = self.context.cluster.node("clickhouse1")

    with When("I try clickhouse local"):
        node.cmd(
            "TZ=UTC clickhouse local -q 'select timezone()'",
            message="UTC",
        )
        node.cmd(
            "TZ=Zulu clickhouse local -q 'select timezone()'",
            message="Zulu",
        )
        node.cmd(
            "TZ=UTC clickhouse local -q \"create table test_tz (d DateTime) Engine=Memory as select toDateTime('2000-01-01 00:00:00', 'UTC'); select *, timezone() from test_tz where d = toDateTime('2000-01-01 00:00:00') settings session_timezone ='Asia/Novosibirsk' FORMAT TSV;\"",
            message="",
        )

        node.cmd(
            "TZ=UTC clickhouse local -q \"create table test_tz (d DateTime) Engine=Memory as select toDateTime('2000-01-01 00:00:00', 'UTC'); select *, timezone() from test_tz where d = '2000-01-01 00:00:00' settings session_timezone ='Asia/Novosibirsk' FORMAT TSV;\"",
            message="2000-01-01 00:00:00\tAsia/Novosibirsk",
        )


@TestFeature
@Name("basic")
def feature(self):
    """Basic check suites."""
    for scenario in loads(current_module(), Scenario):
        scenario()
