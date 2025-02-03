from testflows.core import *

from iceberg.requirements import *


@TestFeature
@Name("iceberg integration")
def feature(self):
    """Check different ways of reading (and writing later) data from/to Iceberg
    tables in Clickhouse."""

    Feature(run=load("iceberg.tests.s3_table_function", "feature"))
    Feature(run=load("iceberg.tests.icebergS3_table_function", "icebergS3_table_function"))
    Feature(run=load("iceberg.tests.iceberg_engine", "feature"))
