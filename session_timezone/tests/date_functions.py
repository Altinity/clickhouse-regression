from testflows.core import *
from session_timezone.requirements import *
from testflows.asserts import error
from session_timezone.tests.steps import *


@TestFeature
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDate("1.0"))
def to_date(self):
    """Check conversation to Date types with the `toDate`, `toDate32`, `toDateTime`, `toDateTime32` and `toDateTime64` functions
    when the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = [
        "toDate32",
        "toDate",
        "toDateTime",
        "toDateTime32",
        "toDateTime64",
    ]

    for function in list_of_functions:
        with Check(function):
            with Then("I check value for simple `toDate` function"):
                if function == "toDateTime64":
                    node.query(
                        f"SELECT {function}('2000-01-01 00:00:00',3) SETTINGS session_timezone = 'UTC';",
                        message=f"2000-01-01",
                    )
                else:
                    node.query(
                        f"SELECT {function}('2000-01-01 00:00:00') SETTINGS session_timezone = 'UTC';",
                        message=f"2000-01-01",
                    )


@TestFeature
@Requirements(
    RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDateOrDefault("1.0")
)
def date_default(self):
    """Verify the default values of the `toDateOrDefault`, `toDate32OrDefault`, `toDateTimeOrDefault` and
    `toDateTime64OrDefault` functions when the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = [
        "toDate32OrDefault",
        "toDateOrDefault",
        "toDateTimeOrDefault",
        "toDateTime64OrDefault",
    ]

    for function in list_of_functions:
        with Check(function):
            with Then("I check default value for simple `toDateOrDefault` function"):
                if function == "toDateTimeOrDefault":
                    node.query(
                        f"SELECT {function}('2020-01-01') SETTINGS session_timezone = 'UTC';",
                        message=f"2020-01-01",
                    )

                elif function == "toDateTime64OrDefault":
                    node.query(
                        f"SELECT {function}('2020-01-01', 3)"
                        f" SETTINGS session_timezone = 'UTC';",
                        message=f"2020-01-01",
                    )
                else:
                    node.query(
                        f"SELECT {function}('wrong value', {function}('2020-01-01')) SETTINGS session_timezone = 'UTC';",
                        message=f"2020-01-01",
                    )


@TestFeature
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDateOrNull("1.0"))
def date_null(self):
    """Verify that `toDateOrNull`, `toDate32OrNull`, `toDateTimeOrNull` and `toDateTime64OrNull` functions are
    returning the null values when the `session_timezone` setting is applied."""

    node = self.context.cluster.node("clickhouse1")

    list_of_functions = [
        "toDate32OrNull",
        "toDateOrNull",
        "toDateTimeOrNull",
        "toDateTime64OrNull",
    ]

    for function in list_of_functions:
        with Check(function):
            with Then("I check null value for simple `toDateOrNull` function"):
                if function == "toDateTime64":
                    node.query(
                        f"SELECT {function}('wrong value',3) SETTINGS session_timezone = 'UTC';",
                        message=f"\\N",
                    )
                else:
                    node.query(
                        f"SELECT {function}('wrong value') SETTINGS session_timezone = 'UTC';",
                        message=f"\\N",
                    )


@TestFeature
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDateOrZero("1.0"))
def date_zero(self):
    """Verify that `toDateOrZero`, `toDate32OrZero`, `toDateTimeOrZero` and `toDateTime64OrZero` functions are returning
     the minimum values when the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = [
        "toDate32OrZero",
        "toDateOrZero",
        "toDateTimeOrZero",
        "toDateTime64OrZero",
    ]

    for function in list_of_functions:
        with Check(function):
            with Then("I check minimum value for `OrZero` function"):
                node.query(
                    f"SELECT {function}('wrong value'{',3' if function == 'toDateTime64OrZero' else ''}) SETTINGS session_timezone = 'Africa/Bissau';",
                    message=f"{'1900-01-01' if function is 'toDate32OrZero' else '1970-01-01' if function is 'toDateOrZero' else '1969-12-31 23:00:00' if function is 'toDateTimeOrZero' else '1969-12-31 23:00:00.000'}",
                )


@TestScenario
@Requirements(
    RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_SnowflakeToDateTime("1.0")
)
def snowflake_to_datetime(self):
    """Verify correctness of the extract time from Snowflake ID as DateTime and Datetime64 by the `snowflakeToDateTime`
    and `snowflakeToDateTime64` functions when the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    with Check("snowflakeToDateTime function"):
        node.query(
            f"SELECT snowflakeToDateTime(CAST('1426860802823350272', 'Int64')) SETTINGS session_timezone = 'UTC';",
            message=f"2021-08-15 10:58:19",
        )

    with Check("snowflakeToDateTime64 function"):
        node.query(
            f"SELECT snowflakeToDateTime64(CAST('1426860802823350272', 'Int64')) SETTINGS session_timezone = 'UTC';",
            message=f"2021-08-15 10:58:19.841",
        )


@TestScenario
@Requirements(
    RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_DateTimeToSnowflake("1.0")
)
def datetime_to_snowflake(self):
    """Verify correctness of the convert DateTime, DateTime64 value to the Snowflake ID at the giving time by
    using `dateTimeToSnowflake` and `dateTime64ToSnowflake` when the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    with Check("dateTime64ToSnowflake function"):
        node.query(
            f"WITH toDateTime64('2021-08-15 18:57:56.492', 3) AS dt64 SELECT dateTime64ToSnowflake(dt64) "
            f"SETTINGS session_timezone = 'Asia/Shanghai';",
            message=f"1426860704886947840",
        )

    with Check("dateTimeToSnowflake function"):
        node.query(
            f"WITH toDateTime('2021-08-15 18:57:56') AS dt SELECT dateTimeToSnowflake(dt) SETTINGS"
            f" session_timezone = 'Asia/Shanghai';",
            message=f"1426860702823350272",
        )


@TestFeature
@Requirements(
    RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ParseDateTime64BestEffort("1.0")
)
def parce_best_effort64(self):
    """Verify that `parseDateTime64BestEffort` functions are returning correct values when
    the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = [
        "parseDateTime64BestEffort",
        "parseDateTime64BestEffortOrZero",
        "parseDateTime64BestEffortUSOrZero",
        "parseDateTime64BestEffortUS",
        "parseDateTime64BestEffortUSOrNull",
        "parseDateTime64BestEffortOrNull",
    ]

    for function in list_of_functions:
        with Check(function):
            with Then(f"I check result for `{function}` function"):
                node.query(
                    f"SELECT {function}('2021-01-01') SETTINGS session_timezone = 'Africa/Bissau';",
                    message=f"2021-01-01 00:00:00.000",
                )


@TestFeature
@Requirements(
    RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ParseDateTimeBestEffort("1.0")
)
def parce_best_effort(self):
    """Verify that parce `parseDateTimeBestEffort` functions are returning correct values when
    the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = [
        "parseDateTimeBestEffort",
        "parseDateTimeBestEffortOrZero",
        "parseDateTimeBestEffortUSOrZero",
        "parseDateTimeBestEffortUS",
        "parseDateTimeBestEffortUSOrNull",
        "parseDateTimeBestEffortOrNull",
    ]

    for function in list_of_functions:
        with Check(function):
            with Then(f"I check result for {function} function"):
                node.query(
                    f"SELECT {function}('2021-01-01') SETTINGS session_timezone = 'Africa/Bissau';",
                    message=f"2021-01-01 00:00:00",
                )


@TestFeature
@Requirements(
    RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ParseDateTime32BestEffort("1.0")
)
def parce_best_effort32(self):
    """Verify that parce `parseDateTime32BestEffort` functions are returning correct values when
    the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = [
        "parseDateTime32BestEffort",
        "parseDateTime32BestEffortOrNull",
        "parseDateTime32BestEffortOrZero",
    ]

    for function in list_of_functions:
        with Check(function):
            with Then(f"I check value for {function} function"):
                node.query(
                    f"SELECT {function}('2021-01-01') SETTINGS session_timezone = 'Africa/Bissau';",
                    message=f"2021-01-01 00:00:00",
                )


@TestFeature
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ParseDateTime("1.0"))
def parce_date_time(self):
    """Verify that `parseDateTime` functions are returning correct values when
    the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = [
        "parseDateTime",
        "parseDateTimeInJodaSyntaxOrZero",
        "parseDateTimeOrNull",
        "parseDateTimeOrZero",
        "parseDateTimeInJodaSyntaxOrNull",
        "parseDateTimeInJodaSyntax",
    ]

    for function in list_of_functions:
        with Check(function):
            with Then(f"I check values for {function} function"):
                if function.startswith("parseDateTimeInJodaSyntax"):
                    node.query(
                        f"SELECT {function}('2023-02-24 14:53:31', 'yyyy-MM-dd HH:mm:ss') SETTINGS session_timezone = 'Europe/Minsk';",
                        message=f"2023-02-24 14:53:31",
                    )
                else:
                    node.query(
                        f"SELECT {function}('2021-01-04+23:00:00', '%Y-%m-%d+%H:%i:%s') SETTINGS session_timezone = 'Africa/Bissau';",
                        message=f"2021-01-04 23:00:00",
                    )


@TestFeature
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_MakeDate("1.0"))
def make_date(self):
    """Verify the results of the `makeDate`, `makeDate32`, `makeDateTime`, `makeDateTime64` functions
    when the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = [
        "makeDate",
        "makeDate32",
        "makeDateTime",
        "makeDateTime64",
    ]

    for function in list_of_functions:
        with Check(function):
            with Then(f"I check result for {function} function"):
                if function == "makeDateTime64" or function == "makeDateTime":
                    node.query(
                        f"SELECT {function}(2023, 2, 28, 17, 12, 33) SETTINGS session_timezone = 'UTC';",
                        message=f"2023-02-28 17:12:33",
                    )
                else:
                    node.query(
                        f"SELECT {function}(2023, 2, 28) SETTINGS session_timezone = 'UTC';",
                        message=f"2023-02-28",
                    )


@TestScenario
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_FormatDateTime("1.0"))
def format_date_time(self):
    """Check formatting a Time according to the given Format string by using `formatDateTime`."""
    node = self.context.cluster.node("clickhouse1")

    with Check("formatDateTime function"):
        node.query(
            f"SELECT formatDateTime(toDate('2010-01-04'), '%g') "
            f"SETTINGS session_timezone = 'Asia/Shanghai';",
            message="10",
        )


@TestScenario
@Requirements(
    RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_FormatDateTimeInJodaSyntax(
        "1.0"
    )
)
def format_date_time_joda(self):
    """Check formatting a Time according to the given Format string by using `formatDateTimeInJodaSyntax`."""
    node = self.context.cluster.node("clickhouse1")

    with Check("formatDateTimeInJodaSyntax function"):
        node.query(
            f"SELECT formatDateTimeInJodaSyntax(toDateTime('2010-01-04 12:34:56'), 'yyyy-MM-dd HH:mm:ss') "
            f"SETTINGS session_timezone = 'Asia/Shanghai';",
            message="2010-01-04 12:34:56",
        )


@TestScenario
@Requirements(
    RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ULIDStringToDateTime("1.0")
)
def ulid_date(self):
    """Check extracting the timestamp from a ULID by using `ULIDStringToDateTime`."""
    node = self.context.cluster.node("clickhouse1")

    with Check("ULIDStringToDateTime function"):
        node.query(
            f"SELECT ULIDStringToDateTime('01GNB2S2FGN2P93QPXDNB4EN2R') "
            f"SETTINGS session_timezone = 'UTC';",
            message="2022-12-28 00:40:37.616",
        )


@TestFeature
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions("1.0"))
@Name("date functions")
def feature(self):
    """Basic check suites."""
    with Pool(1) as executor:

        try:
            for feature in loads(current_module(), Feature):
                if not feature.name.endswith("date functions"):
                    Feature(test=feature, parallel=True, executor=executor)()
        finally:
            join()

    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()
