from testflows.core import *


@TestFeature
@Name("alter")
def feature(self):
    """ALTER TABLE operations on content-addressed storage."""
    Feature(run=load("cas.tests.alter.column", "feature"))
    Feature(run=load("cas.tests.alter.constraint", "feature"))
    Feature(run=load("cas.tests.alter.index", "feature"))
    Feature(run=load("cas.tests.alter.mutations", "feature"))
    Feature(run=load("cas.tests.alter.keys", "feature"))
    Feature(run=load("cas.tests.alter.projection", "feature"))
    Feature(run=load("cas.tests.alter.ttl", "feature"))
    Feature(run=load("cas.tests.alter.statistics", "feature"))
