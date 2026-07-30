from testflows.core import *


@TestFeature
@Name("content addressed storage")
def feature(self):
    """Content-addressed storage test suite."""
    Feature(run=load("cas.tests.sanity", "feature"))
