from testflows.core import *
from testflows.asserts import error
from clickhouse_driver import Client
import boto3
from pyiceberg.catalog import load_catalog
from pyiceberg.table import Table
from pyiceberg.schema import Schema
from pyiceberg.types import IntegerType, StringType


@TestFeature
def feature(self, servers=None, node="clickhouse1"):
    self.context.node = self.context.cluster.node(node)

    for scenario in loads(current_module(), Scenario):
        scenario()
