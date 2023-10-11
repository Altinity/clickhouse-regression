import os

from testflows import *
from testflows.core import *
from testflows.asserts import snapshot, values
from parquet.requirements import *
from parquet.tests.outline import import_export
from helpers.common import *


def list_files(path):
    try:
        with os.scandir(path) as entries:
            return [entry.name for entry in entries if entry.is_file()]
    except FileNotFoundError:
        return f"No directory found at {path}"
    except PermissionError:
        return f"Permission denied for directory {path}"


@TestScenario
def fastparquet(self):
    """Checking if ClickHouse can import and export files from the fastparquet test suite."""
    path = os.path.join("data", "fastparquet")
    files = list_files(path)
    with Given("I import and export parquet files from the fastparquet directory"):
        for file in files:
            with By(f"Importing and exporting: {file}"):
                import_file = os.path.join("fastparquet", file)

                import_export(
                    snapshot_name=f"{file}_structure", import_file=import_file
                )


@TestScenario
def airlines(self):
    """Checking if ClickHouse can import and export files from the fastparquet/airlines directory."""
    import_file = os.path.join(
        "fastparquet",
        "airlines_parquet",
        "4345e5eef217aa1b-c8f16177f35fd983_1150363067_data.1.parquet",
    )

    import_export(snapshot_name=f"{import_file}_structure", import_file=import_file)


@TestScenario
def baz(self):
    """Checking if ClickHouse can import and export files from the fastparquet/baz directory."""
    import_file = os.path.join(
        "fastparquet",
        "baz.parquet",
        "part-00000-f689190d-8470-4dba-80ca-b8674fa9f15d-c000.snappy.parquet",
    )

    import_export(snapshot_name=f"{import_file}_structure", import_file=import_file)


@TestScenario
def evo(self):
    """Checking if ClickHouse can import and export files from the fastparquet/evo directory."""
    path = os.path.join("data", "fastparquet", "evo")
    files = list_files(path)
    with Given("I import and export parquet files from the fastparquet/evo directory"):
        for file in files:
            with By(f"Importing and exporting: {file}"):
                import_file = os.path.join("fastparquet", "evo", file)

                import_export(
                    snapshot_name=f"{file}_structure", import_file=import_file
                )


@TestScenario
def empty_date(self):
    """Checking if ClickHouse can import and export files from the fastparquet/empty_date directory."""
    path = os.path.join("data", "fastparquet", "spark-date-empty-rg.parq")
    files = list_files(path)
    with Given("I import and export parquet files from the fastparquet/evo directory"):
        for file in files:
            with By(f"Importing and exporting: {file}"):
                import_file = os.path.join(
                    "fastparquet", "spark-date-empty-rg.parq", file
                )

                import_export(
                    snapshot_name=f"{file}_structure", import_file=import_file
                )


@TestScenario
def spark_empty_date(self):
    """Checking if ClickHouse can import and export files from the fastparquet/spark-date-empty directory."""
    path = os.path.join("data", "fastparquet", "spark-date-empty-rg.parq")
    files = list_files(path)
    with Given("I import and export parquet files from the fastparquet/evo directory"):
        for file in files:
            with By(f"Importing and exporting: {file}"):
                import_file = os.path.join(
                    "fastparquet", "spark-date-empty-rg.parq", file
                )

                import_export(
                    snapshot_name=f"{file}_structure", import_file=import_file
                )


@TestFeature
@Requirements(RQ_SRS_032_ClickHouse_Parquet_Import_DataTypes_Conversion("1.0"))
@Name("fastparquet")
def feature(self, node="clickhouse1"):
    """Check that ClickHouse can import and export parquet files that were generated/used by fastparquet."""
    self.context.node = self.context.cluster.node(node)
    self.context.snapshot_id = "fastparquet"

    for scenario in loads(current_module(), Scenario):
        scenario()
