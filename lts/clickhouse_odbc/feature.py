"""ClickHouse ODBC driver sub-suite feature loaded by the LTS orchestrator."""

import os

from testflows.core import *

from lts.clickhouse_odbc.requirements.requirements import *
from lts.steps.tool_tests import run_tool_tests


@TestFeature
@Name("clickhouse-odbc")
@Specifications(SRS_100_ClickHouse_ODBC_Driver_LTS_Testing)
@Requirements(
    RQ_SRS_100_ODBC_DriverBuild("1.0"),
    RQ_SRS_100_ODBC_Connection("1.0"),
    RQ_SRS_100_ODBC_Connection_DSN("1.0"),
    # The parametrized-regression.py ctest targets round-trip these types and
    # parameters through pyodbc for both the ANSI and Unicode DSN.
    RQ_SRS_100_ODBC_DataTypes_Int8("1.0"),
    RQ_SRS_100_ODBC_DataTypes_Int16("1.0"),
    RQ_SRS_100_ODBC_DataTypes_Int32("1.0"),
    RQ_SRS_100_ODBC_DataTypes_Int64("1.0"),
    RQ_SRS_100_ODBC_DataTypes_UInt8("1.0"),
    RQ_SRS_100_ODBC_DataTypes_UInt16("1.0"),
    RQ_SRS_100_ODBC_DataTypes_UInt32("1.0"),
    RQ_SRS_100_ODBC_DataTypes_UInt64("1.0"),
    RQ_SRS_100_ODBC_DataTypes_Float32("1.0"),
    RQ_SRS_100_ODBC_DataTypes_Float64("1.0"),
    RQ_SRS_100_ODBC_DataTypes_Decimal("1.0"),
    RQ_SRS_100_ODBC_DataTypes_String("1.0"),
    RQ_SRS_100_ODBC_DataTypes_FixedString("1.0"),
    RQ_SRS_100_ODBC_DataTypes_Date("1.0"),
    RQ_SRS_100_ODBC_DataTypes_DateTime("1.0"),
    RQ_SRS_100_ODBC_DataTypes_Enum("1.0"),
    RQ_SRS_100_ODBC_DataTypes_UUID("1.0"),
    RQ_SRS_100_ODBC_DataTypes_IPv4("1.0"),
    RQ_SRS_100_ODBC_DataTypes_IPv6("1.0"),
    RQ_SRS_100_ODBC_DataTypes_Nullable("1.0"),
    RQ_SRS_100_ODBC_ParameterizedQueries("1.0"),
    RQ_SRS_100_ODBC_ParameterizedQueries_Null("1.0"),
    RQ_SRS_100_ODBC_Compatibility_LTS("1.0"),
)
def feature(self, release="v1.2.1.20220905", timeout=3600):
    """Run the clickhouse-odbc ctest targets against the ClickHouse image and
    report each target.

    The driver is compiled in a build stage that does not depend on the
    ClickHouse image, so it is cached across ClickHouse releases.
    """
    run_tool_tests(
        suite="clickhouse_odbc",
        configs_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs"),
        build_args={
            "CLICKHOUSE_IMAGE": self.context.clickhouse_image,
            "ODBC_RELEASE": release,
        },
        env={},
        timeout=timeout,
        # v1.2.1.20220905: 28 ctest targets, all run; fewer means a test tool
        # was missing when the build stage configured the tests.
        min_tests=28,
        max_skipped=0,
        # ctest exits with 8 when some tests failed
        ok_exit_codes=(0, 8),
    )
