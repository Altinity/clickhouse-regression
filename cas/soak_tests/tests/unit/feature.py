from testflows.core import *


@TestFeature
@Name("unit")
def feature(self):
    """Oracle unit tests. No cluster."""
    Feature(run=load("cas.soak_tests.tests.unit.rng", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.ledger", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.rowgen", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.model", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.cliff", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.workload", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.fsck", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.checker", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.http", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.transport", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.chaos", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.driver", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.schedule", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.phase3", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.pool", "feature"))
    Feature(run=load("cas.soak_tests.tests.unit.scenario", "feature"))
