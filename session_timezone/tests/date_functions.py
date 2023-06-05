from testflows.core import *
from session_timezone.requirements import *
from testflows.asserts import error
from session_timezone.tests.steps import *


@TestFeature
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDate("1.0"))
def to_date(self):
    """Verify the data values of the `toDate`, `toDate32`, `toDateTime`, `toDateTime32` and `toDateTime64` functions
    when the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = ["toDate32",  "toDate", "toDateTime", "toDateTime32", "toDateTime64"]

    for function in list_of_functions:
        with Check(function):
            with Then("I check values for all simple `toDate` functions"):
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
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions_ToDateOrDefault("1.0"))
def date_default(self):
    """Verify the default values of the `toDateOrDefault`, `toDate32OrDefault`, `toDateTimeOrDefault` and
     `toDateTime64OrDefault` functions when the `session_timezone` setting is applied."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = ["toDate32OrDefault",  "toDateOrDefault", "toDateTimeOrDefault", "toDateTime64OrDefault"]

    for function in list_of_functions:
        with Check(function):
            with Then("I check default values for all simple `toDateOrDefault` functions"):
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
    """Check NULL value for toDate32OrNull, toDateOrNull, toDateTimeOrNull
    functions with session_timezone setting."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = ["toDate32OrNull",  "toDateOrNull", "toDateTimeOrNull", "toDateTime64OrNull"]

    for function in list_of_functions:
        with Check(function):
            with Then("I check default values for all simple `toDateOrDefault` functions"):
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
    """Check minimum value for DateOrZero, Date32OrZero, DateTimeOrZero functions with session_timezone setting."""
    node = self.context.cluster.node("clickhouse1")

    list_of_functions = ["toDate32OrZero", "toDateOrZero", "toDateTimeOrZero", "toDateTime64OrZero"]

    for function in list_of_functions:
        with Check(function):
            with Then("I check minimum values for all `OrZero` functions"):
                node.query(
                    f"SELECT {function}('wrong value'{',3' if function == 'toDateTime64OrZero' else ''}) SETTINGS session_timezone = 'Africa/Bissau';",
                    message=f"{'1900-01-01' if function is 'toDate32OrZero' else '1970-01-01' if function is 'toDateOrZero' else '1969-12-31 23:00:00' if function is 'toDateTimeOrZero' else '1969-12-31 23:00:00.000'}",
                )


@TestFeature
@Requirements(RQ_SRS_037_ClickHouse_SessionTimezone_DateFunctions("1.0"))
@Name("date functions")
def feature(self):
    """Basic check suites."""
    with Pool(1) as executor:

        try:
            for feature in loads(current_module(), Feature):
                if not feature.name.endswith(
                    "date functions"
                ):
                    Feature(test=feature, parallel=True, executor=executor)()
        finally:
            join()

    with Pool(1) as executor:
        try:
            for scenario in loads(current_module(), Scenario):
                Feature(test=scenario, parallel=True, executor=executor)()
        finally:
            join()