from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

from testflows.core import *
from helpers.common import getuid


@TestFeature
@Name("PySpark and Delta Lake are working")
def feature(self):
    """Check that PySpark and Delta Lake are working."""
    builder = (
        SparkSession.builder.appName("TestDeltaLake")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
    )

    spark = configure_spark_with_delta_pip(builder).getOrCreate()

    df = spark.createDataFrame([(1, "foo"), (2, "bar")], ["id", "value"])
    df.write.format("delta").save("/tmp/delta-table" + getuid())
    df.show()
