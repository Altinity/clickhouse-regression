import sys

from testflows.core import *
from engines.requirements import *
from engines.tests.steps import *
from helpers.common import check_clickhouse_version


append_path(sys.path, "..")


@TestModule
@Name("replacing_merge_tree")
def feature(self):
    """Check new ReplacingMergeTree engine."""
    Feature(run=load("replacing_merge_tree.general", "feature"))
