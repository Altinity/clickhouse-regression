from testflows.core import *
from testflows.asserts import error


@TestFeature
def auto_final(self):
    """Check applying FINAL modifier automatically by using `auto_final` query setting.
    """
    pass


@TestFeature
def apply_final_by_default(self):
    """Check applying FINAL modifier automatically using
    `apply_final_by_default` MergeTree table setting.
    """
    pass


@TestFeature
@Name("final modifier")
def feature(self):
    """Check FINAL modifier."""
    Feature(run=auto_final)
    Feature(run=apply_final_by_default)
