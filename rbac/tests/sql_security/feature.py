from testflows.core import *
from rbac.helper.common import *


@TestFeature
@Name("SQL security")
def feature(self):
    """Check SQL security feature."""
    Feature(run=load("rbac.tests.sql_security.materialized_view_tests", "feature"))
    Feature(run=load("rbac.tests.sql_security.modify", "feature"))
    Feature(run=load("rbac.tests.sql_security.view_tests", "feature"))
    Feature(run=load("rbac.tests.sql_security.multiple_source_tables", "feature"))
    Feature(run=load("rbac.tests.sql_security.cascading_views", "feature"))
    Feature(run=load("rbac.tests.sql_security.drop_definer", "feature"))
