from testflows.core import *


@TestFeature
@Name("content addressed storage")
def feature(self):
    """Content-addressed storage test suite."""
    # Feature(run=load("cas.tests.sanity", "feature"))
    # Feature(run=load("cas.tests.partition", "feature"))
    # Feature(run=load("cas.tests.concurrent_attach", "feature"))
    # Feature(run=load("cas.tests.pool_corruption", "feature"))
    Feature(run=load("cas.tests.ref_collision", "feature"))
    # Feature(run=load("cas.tests.server_root_id_unique", "feature"))
    # Feature(run=load("cas.tests.stress_create_drop", "feature"))
