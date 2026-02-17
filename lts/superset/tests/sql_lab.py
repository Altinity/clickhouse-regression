"""Test scenarios for Superset SQL Lab with ClickHouse."""

from testflows.core import *

from lts.superset.requirements.requirements import (
    RQ_SRS_101_Superset_SQLLab_QueryExecution,
    RQ_SRS_101_Superset_SQLLab_SchemaExplorer,
    RQ_SRS_101_Superset_Compatibility_LTS,
)


@TestScenario
@Requirements(
    RQ_SRS_101_Superset_SQLLab_QueryExecution("1.0"),
    RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
)
def query_execution(self):
    """Verify queries can be executed in SQL Lab against ClickHouse."""
    pass


@TestScenario
@Requirements(
    RQ_SRS_101_Superset_SQLLab_SchemaExplorer("1.0"),
    RQ_SRS_101_Superset_Compatibility_LTS("1.0"),
)
def schema_explorer(self):
    """Verify schema explorer lists ClickHouse databases, tables, and columns."""
    pass


@TestFeature
@Name("sql lab")
def feature(self):
    """Test SQL Lab scenarios."""
    Scenario(run=query_execution)
    Scenario(run=schema_explorer)
