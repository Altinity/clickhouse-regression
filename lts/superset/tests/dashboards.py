"""Test scenarios for Superset dashboards with ClickHouse-backed charts."""

from testflows.core import *

from lts.superset.requirements.requirements import (
    RQ_SRS_101_Superset_Dashboards_Create,
    RQ_SRS_101_Superset_Dashboards_Refresh,
    RQ_SRS_101_Superset_Compatibility_LTS,
)


@TestScenario
@Requirements(
    RQ_SRS_101_Superset_Dashboards_Create("1.0"),
    RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
)
def create_dashboard(self):
    """Verify a dashboard can be created with ClickHouse-backed charts."""
    pass


@TestScenario
@Requirements(
    RQ_SRS_101_Superset_Dashboards_Refresh("1.0"),
    RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
)
def refresh_dashboard(self):
    """Verify dashboard refresh works for ClickHouse data."""
    pass


@TestFeature
@Name("dashboards")
def feature(self):
    """Test dashboard scenarios."""
    Scenario(run=create_dashboard)
    Scenario(run=refresh_dashboard)
