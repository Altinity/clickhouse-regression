from testflows.core import *
from session_timezone.requirements import *
from testflows.asserts import error
from session_timezone.tests.steps import *


@TestScenario
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_WrongSettingValue("1.0"))
def bad_arguments(self):
    """Check behavior with bad arguments."""
    node = self.context.cluster.node("clickhouse1")

    with Check(
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
    """Verify that the session_timezone is set to the default value when it is not explicitly defined.."""
    node = self.context.cluster.node("clickhouse1")

    with Check(
        "I check timezone(), timezoneOf(now()) without session_timezone setting"
    ):
        node.query(
            "SELECT timezone(), timezoneOf(now()) FORMAT TSV;",
            message="Europe/Berlin	Europe/Berlin",
        )


@TestScenario
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DefaultValue("1.0"))
def timezone_default_value(self):
    """Verify that the session_timezone is set to the default value if it is set to an empty string."""
    node = self.context.cluster.node("clickhouse1")

    with Check(
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

    with Check(
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

    with Check(
        "I confirm that the timezone is updated when the SET session_timezone command is executed with a continent "
        "value that matches the current timezone."
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
    """Check behavior of `toDateTime64` with `SET session_timezone` and `SETTING timezone."""

    node = self.context.cluster.node("clickhouse1")

    with Check(
        "I verify that the `SET session_timezone` command does not affect queries using "
        "the `SETTINGS session_timezone` option."
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

    with Check(
        "I check that `SETTINGS session_timezone` is changing timezone(), timezoneOf(now())"
    ):
        node.query(
            "SELECT timezone(), timezoneOf(now()) SETTINGS session_timezone = 'Europe/Zurich' FORMAT CSV;",
            message="",
        )
        node.query(
            "SELECT timezone(), timezoneOf(now()) SETTINGS session_timezone = 'Pacific/Pitcairn' FORMAT CSV;",
            message="",
        )


@TestScenario
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_ParsingOfDateTimeTypes("1.0"))
def date_datetime_column_types(self):
    """Check the way session_timezone setting affects parsing of DateTime type."""
    node = self.context.cluster.node("clickhouse1")
    table_name = f"test_tz{getuid()}"

    try:
        with Given("I create table with DateTime('UTC') datatype"):
            node.query(
                f"CREATE TABLE IF NOT EXISTS {table_name} (d DateTime('UTC')) ENGINE = Memory AS SELECT "
                "toDateTime('2000-01-01 00:00:00', 'UTC');"
            )

        with Then(
            "I check the way session_timezone setting affects parsing of DateTime type"
        ):
            node.query(
                f"SELECT *, timezone() FROM {table_name} WHERE d = toDateTime('2000-01-01 00:00:00') "
                "SETTINGS session_timezone = 'Asia/Novosibirsk'"
            )
            node.query(
                f"SELECT *, timezone() FROM {table_name} WHERE d = '2000-01-01 00:00:00' "
                "SETTINGS session_timezone = 'Asia/Novosibirsk';",
                message="2000-01-01 00:00:00\tAsia/Novosibirsk",
            )

    finally:
        with Finally("I drop test_tz table"):
            node.query(f"DROP TABLE IF EXISTS {table_name} ")


@TestScenario
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_PossibleValues("1.0"))
def all_possible_values_of_timezones(self):
    """Check all possible timezones"""
    node = self.context.cluster.node("clickhouse1")

    number_of_timezones = node.query(
        "SELECT count() FROM system.time_zones"
    ).output.strip()

    with Check("I check all possible timezones from system.time_zones table"):
        for i in range(0, int(number_of_timezones)):
            time_zone = node.query(
                f"SELECT time_zone FROM system.time_zones LIMIT 1 OFFSET {i}"
            ).output.strip()
            with Step(
                f"I check that `session_timezone` is changing timezone to {time_zone}"
            ):
                node.query(
                    f"SELECT timezone() SETTINGS session_timezone = '{time_zone}' FORMAT TSV;",
                    message=f"{time_zone}",
                )


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


@TestScenario
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateTypes("1.0"))
def different_types(self):
    """Simple check of different Date types and functions with session_timezone setting."""
    node = self.context.cluster.node("clickhouse1")

    number_of_timezones = node.query(
        "SELECT count() FROM system.time_zones"
    ).output.strip()

    with Check("I check all possible timezones from system.time_zones table"):
        # for i in range(0, int(number_of_timezones)):
        for i in range(0, 3):
            time_zone = node.query(
                f"SELECT time_zone FROM system.time_zones LIMIT 1 OFFSET {i}"
            ).output.strip()
            with Step(
                f"I check that `session_timezone` is changing timezone to {time_zone}"
            ):

                node.query(
                    f"SELECT Date('2000-01-01 01:00:00') SETTINGS session_timezone = '{time_zone}';",
                    message=f"2000-01-01",
                )

                node.query(
                    f"SELECT toDateTime(Date('2000-01-01 01:00:00'),3) SETTINGS session_timezone = '{time_zone}';",
                    message=f"2000-01-01 00:00:00.000",
                )

                node.query(
                    f"SELECT toDateTime64(Date('2000-01-01 01:00:00'),3) SETTINGS session_timezone = '{time_zone}';",
                    message=f"2000-01-01 00:00:00.000",
                )

                list_of_indexies = ["32", "", "Time"]

                for index in list_of_indexies:

                    node.query(
                        f"SELECT toDateTime(toDate{index}('2000-01-01 00:00:00'),3) SETTINGS session_timezone = '{time_zone}';",
                        message=f"2000-01-01 00:00:00",
                    )

                    node.query(
                        f"SELECT toDateTime64(toDate{index}('2000-01-01 00:00:00'),3) SETTINGS session_timezone = '{time_zone}';",
                        message=f"2000-01-01 00:00:00",
                    )

                for index in list_of_indexies:

                    node.query(
                        f"SELECT toDate{index}OrZero('wrong value') SETTINGS session_timezone = '{time_zone}';",
                        message=f"{'1900-01-01' if index is '32' else '1970-01-01'}",
                    )

                    if index is not "Time":
                        node.query(
                            f"SELECT toDate{index}OrDefault('wrong value', toDate{index}('2020-01-01')) SETTINGS session_timezone = '{time_zone}';",
                            message=f"2020-01-01",
                        )
                    else:
                        node.query(
                            f"SELECT toDate{index}OrDefault('2020-01-01') SETTINGS session_timezone = '{time_zone}';",
                            message=f"2020-01-01",
                        )

                    node.query(
                        f"SELECT toDate{index}OrNull('wrong value') SETTINGS session_timezone = '{time_zone}';",
                        message=f"\\N",
                    )


@TestScenario
def date_or_zero(self):
    """Check minimum value for DateOrZero, Date32OrZero, DateTimeOrZero functions with session_timezone setting."""
    node = self.context.cluster.node("clickhouse1")

    list_of_indexies = ["32", "", "Time"]

    with Check("I check minimum values for all `OrZero` functions"):
        for index in list_of_indexies:
            node.query(
                f"SELECT toDate{index}OrZero('wrong value') SETTINGS session_timezone = 'Africa/Bissau';",
                message=f"{'1900-01-01' if index is '32' else '1970-01-01' if index is ''  else '1969-12-31 23:00:00'}",
            )


@TestFeature
@Name("basic")
def feature(self):
    """Basic check suites."""
    with Pool(1) as executor:
        try:
            for feature in loads(current_module(), Feature):
                Feature(test=feature, parallel=True, executor=executor)()
        finally:
            join()

    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()
