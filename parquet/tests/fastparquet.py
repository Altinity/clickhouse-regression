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
    files = [
        "test-converted-type-null.parquet",
        "snappy-nation.impala.parquet",
        "test.parquet",
        "test-null-dictionary.parquet",
        "repeated_no_annotation.parquet",
        "gzip-nation.impala.parquet",
        "test-null.parquet",
        "non-std-kvm.fp-0.8.2.parquet",
        "nation.impala.parquet",
        "01bc139247874a0aa9e0e541f2eec497.parquet",
        "test-map-last-row-split.parquet",
        "nation.plain.parquet",
        "a97cc141d16f4014a59e5b234dddf07c.parquet",
        "nested1.parquet",
        "nation.dict.parquet",
        "map-test.snappy.parquet",
        "customer.impala.parquet",
    ]
    with Given("I import and export parquet files from the fastparquet directory"):
        with By("Iterating trough the list of files inside the directory"):
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
    files = [
        "00000-0-b5ea8b58-1686-4d25-af1d-9349b2d29fd0-00001.parquet",
        "00002-2-e5685594-0967-42ad-b306-2128ad35e716-00001.parquet",
        "00001-1-b7c7ea31-7ce3-4bd6-9d86-7e96dbffb589-00001.parquet",
        "00000-206-1427d50c-e5c0-401a-9f54-b37b943b98c3-00001.parquet",
        "00003-3-2a454a5e-dc13-4075-a9ad-91181d5ac450-00001.parquet",
        "00081-6-db4a5dc9-8fdc-4b1f-b88e-05e954a966f7-00001.parquet",
    ]
    with Given("I import and export parquet files from the fastparquet/evo directory"):
        with By("Iterating trough the list of files inside the directory"):
            for file in files:
                with By(f"Importing and exporting: {file}"):
                    import_file = os.path.join("fastparquet", "evo", file)

                    import_export(
                        snapshot_name=f"{file}_structure", import_file=import_file
                    )


@TestScenario
def empty_date(self):
    """Checking if ClickHouse can import and export files from the fastparquet/empty_date directory."""
    files = [
        "part-00011-b2b1875e-3f87-46b5-a3bc-31bca366bbcc-c000.snappy.parquet",
        "part-00005-b2b1875e-3f87-46b5-a3bc-31bca366bbcc-c000.snappy.parquet",
        "part-00000-b2b1875e-3f87-46b5-a3bc-31bca366bbcc-c000.snappy.parquet",
    ]
    with Given("I import and export parquet files from the fastparquet/evo directory"):
        with By("Iterating trough the list of files inside the directory"):
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
