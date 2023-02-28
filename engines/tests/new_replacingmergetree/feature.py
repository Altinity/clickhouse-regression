import sys

from testflows.core import *
from engines.requirements import *
from engines.tests.steps import *


append_path(sys.path, "..")


@TestModule
@Name("new_ReplacingMergeTree")
def module(self):
    """Check new ReplacingMergeTree modifier."""


    # Feature(run=load("final.", "feature"))

