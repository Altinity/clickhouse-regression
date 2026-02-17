# These requirements were auto generated
# from software requirements specification (SRS)
# document by TestFlows v2.1.240306.1133530.
# Do not edit by hand but re-generate instead
# using 'tfs requirements generate' command.
from testflows.core import Specification
from testflows.core import Requirement

Heading = Specification.Heading

RQ_SRS_101_Superset_Environment = Requirement(
    name="RQ.SRS-101.Superset.Environment",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The test environment SHALL deploy Apache Superset and ClickHouse using\n"
        "Docker Compose with all required services (superset, superset-init,\n"
        "superset-worker, clickhouse).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.1.1",
)

RQ_SRS_101_Superset_Environment_ClickHouseConnect = Requirement(
    name="RQ.SRS-101.Superset.Environment.ClickHouseConnect",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The environment SHALL support configuring Superset with the `clickhouse-connect`\n"
        "Python driver as the database backend.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.1.2",
)

RQ_SRS_101_Superset_Environment_ClickHouseSQLAlchemy = Requirement(
    name="RQ.SRS-101.Superset.Environment.ClickHouseSQLAlchemy",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "The environment SHALL support configuring Superset with the `clickhouse-sqlalchemy`\n"
        "Python driver as the database backend.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.1.3",
)

RQ_SRS_101_Superset_DatabaseConnection = Requirement(
    name="RQ.SRS-101.Superset.DatabaseConnection",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SHALL successfully add a ClickHouse database connection and verify\n"
        'it via the "Test Connection" button.\n'
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.1",
)

RQ_SRS_101_Superset_DatabaseConnection_HTTP = Requirement(
    name="RQ.SRS-101.Superset.DatabaseConnection.HTTP",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SHALL connect to ClickHouse over the HTTP interface (port 8123).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.2",
)

RQ_SRS_101_Superset_DatabaseConnection_HTTPS = Requirement(
    name="RQ.SRS-101.Superset.DatabaseConnection.HTTPS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SHALL connect to ClickHouse over HTTPS (port 8443) using the\n"
        "provided TLS certificates.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.3",
)

RQ_SRS_101_Superset_DatabaseConnection_NativeProtocol = Requirement(
    name="RQ.SRS-101.Superset.DatabaseConnection.NativeProtocol",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SHALL connect to ClickHouse over the native protocol (port 9000/9440)\n"
        "when using a driver that supports it.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.2.4",
)

RQ_SRS_101_Superset_SQLLab_QueryExecution = Requirement(
    name="RQ.SRS-101.Superset.SQLLab.QueryExecution",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SQL Lab SHALL execute queries against ClickHouse and display results\n"
        "correctly.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.1",
)

RQ_SRS_101_Superset_SQLLab_SchemaExplorer = Requirement(
    name="RQ.SRS-101.Superset.SQLLab.SchemaExplorer",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SQL Lab schema explorer SHALL list ClickHouse databases, tables,\n"
        "and columns.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.3.2",
)

RQ_SRS_101_Superset_Charts_Create = Requirement(
    name="RQ.SRS-101.Superset.Charts.Create",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SHALL allow creating charts from ClickHouse datasets.\n" "\n"
    ),
    link=None,
    level=4,
    num="3.4.1",
)

RQ_SRS_101_Superset_Charts_DataTypes = Requirement(
    name="RQ.SRS-101.Superset.Charts.DataTypes",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset charts SHALL correctly render data from ClickHouse columns of\n"
        "various types (numeric, string, date/time, etc.).\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.4.2",
)

RQ_SRS_101_Superset_Dashboards_Create = Requirement(
    name="RQ.SRS-101.Superset.Dashboards.Create",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset SHALL allow creating dashboards that include charts backed by\n"
        "ClickHouse data.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.5.1",
)

RQ_SRS_101_Superset_Dashboards_Refresh = Requirement(
    name="RQ.SRS-101.Superset.Dashboards.Refresh",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "Superset dashboards SHALL support manual and auto-refresh of ClickHouse-backed\n"
        "charts.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.5.2",
)

RQ_SRS_101_Superset_Compatibility_LTS = Requirement(
    name="RQ.SRS-101.Superset.Compatibility.LTS",
    version="1.0",
    priority=None,
    group=None,
    type=None,
    uid=None,
    description=(
        "All Superset features SHALL be verified to work against the current Altinity\n"
        "ClickHouse LTS build.\n"
        "\n"
    ),
    link=None,
    level=4,
    num="3.6.1",
)
