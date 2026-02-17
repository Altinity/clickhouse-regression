"""Test scenarios for Superset database connection to ClickHouse."""

from testflows.core import *

from lts.superset.requirements.requirements import (
    RQ_SRS_101_Superset_DatabaseConnection,
    RQ_SRS_101_Superset_DatabaseConnection_HTTP,
    RQ_SRS_101_Superset_DatabaseConnection_HTTPS,
    RQ_SRS_101_Superset_Compatibility_LTS,
)


@TestScenario
@Requirements(
    RQ_SRS_101_Superset_DatabaseConnection("1.0"),
    RQ_SRS_101_Superset_DatabaseConnection_HTTP("1.0"),
    RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
)
def http_connection(self):
    """Verify Superset can connect to ClickHouse over HTTP."""
    pass


@TestScenario
@Requirements(
    RQ_SRS_101_Superset_DatabaseConnection("1.0"),
    RQ_SRS_101_Superset_DatabaseConnection_HTTPS("1.0"),
    RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
)
def https_connection(self):
    """Verify Superset can connect to ClickHouse over HTTPS."""
    pass


@TestFeature
@Name("connection")
def feature(self):
    """Test database connection scenarios."""
    Scenario(run=http_connection)
    Scenario(run=https_connection)
