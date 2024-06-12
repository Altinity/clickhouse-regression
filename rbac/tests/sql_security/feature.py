from testflows.core import *
from rbac.helper.common import *


@TestFeature
@Name("SQL security")
def feature(self):
    """Check SQL security feature."""
    # Feature(run=load("rbac.tests.sql_security.materialized_view", "feature"))
    # Feature(run=load("rbac.tests.sql_security.view", "feature"))
    # Feature(run=load("rbac.tests.sql_security.cluster", "feature"))

    Feature(run=load("rbac.tests.sql_security.mv_small_tests", "feature"))
    Feature(run=load("rbac.tests.sql_security.modify", "feature"))
    Feature(run=load("rbac.tests.sql_security.view_tests", "feature"))
    Feature(run=load("rbac.tests.sql_security.multiple_source_tables", "feature"))