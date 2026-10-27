import os

from testflows.core import *

from helpers.common import check_clickhouse_version, check_if_antalya_build

from iceberg.requirements.aggregate_states import (
    SRS_051_ClickHouse_Aggregate_Function_States_in_Parquet_and_Iceberg,
)
from iceberg.tests.iceberg_engine.aggregate_states.steps import feature_available

# Modules over tables ClickHouse writes at a path, without a catalog.
MODULES = [
    "parquet_footer",
    "setting_gate",
    "round_trip",
    "annotations",
]

# Modules that go through a catalog; they run once per catalog.
CATALOG_MODULES = [
    "annotation_survival",
    "external_engines",
]


@TestFeature
@Name("aggregate states")
@Specifications(SRS_051_ClickHouse_Aggregate_Function_States_in_Parquet_and_Iceberg)
def feature(self, minio_root_user, minio_root_password):
    """`AggregateFunction` and `SimpleAggregateFunction` columns in Parquet
    files and Iceberg tables (Altinity/ClickHouse#2680, issue #2206)."""
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password
    self.context.catalog = "rest"

    if not (check_if_antalya_build(self) and check_clickhouse_version(">=26.8")(self)):
        skip("aggregate function states in open formats need an Antalya build >= 26.8")

    if not feature_available(self.context.node):
        skip(
            "build has no aggregate function states in open formats "
            "(system.settings lacks allow_experimental_aggregate_function_states_in_open_formats)"
        )

    for module in MODULES:
        Feature(
            test=load(f"iceberg.tests.iceberg_engine.aggregate_states.{module}", "feature"),
            flags=TE,
        )()

    catalogs = ["rest"]
    if os.getenv("LOCALSTACK_AUTH_TOKEN"):
        catalogs.append("glue")

    for catalog in catalogs:
        with Feature(f"{catalog} catalog"):
            self.context.catalog = catalog
            for module in CATALOG_MODULES:
                Feature(
                    test=load(
                        f"iceberg.tests.iceberg_engine.aggregate_states.{module}",
                        "feature",
                    ),
                    flags=TE,
                )()
