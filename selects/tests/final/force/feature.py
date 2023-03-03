from testflows.core import *


@TestFeature
@Name("force")
def feature(self):
    """Run tests for --final query setting that force FINAL clause modifier on all tables used in the query."""

    Feature(run=load("final.force.general", "feature"))
    Feature(run=load("final.force.concurrent", "feature"))
    Feature(run=load("final.force.user_rights", "feature"))
    Feature(run=load("final.force.alias", "feature"))
