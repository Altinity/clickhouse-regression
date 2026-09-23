"""The explicit-engine path: engine family, backend consistency and initial
file naming (plan §3.6)."""

from testflows.core import *
from testflows.asserts import error

from helpers.common import getuid

from iceberg.requirements.native_create_drop import *
from iceberg.tests.iceberg_engine.native_create.steps import *

COLUMNS = ["id Int64", "name String"]


def engine_for(kind, key, user, password):
    return {
        "MergeTree": "MergeTree",
        "Memory": "Memory",
        "S3": f"S3('http://minio:9000/warehouse/{key}/', '{user}', '{password}', 'Parquet')",
        "DeltaLake": f"DeltaLake('http://minio:9000/warehouse/{key}/', '{user}', '{password}')",
        "Iceberg": f"Iceberg('http://minio:9000/warehouse/{key}/', '{user}', '{password}')",
        "IcebergS3": f"IcebergS3('http://minio:9000/warehouse/{key}/', '{user}', '{password}')",
        "IcebergAzure": f"IcebergAzure('http://azurite:10000/devstoreaccount1', 'c', '{key}/', 'a', 'k')",
        "IcebergLocal": f"IcebergLocal('/var/lib/clickhouse/user_files/{key}/')",
        "IcebergHDFS": f"IcebergHDFS('hdfs://namenode:9000/{key}/')",
    }[kind]


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_ExplicitEngine_IcebergFamilyOnly("1.0"))
@Examples("engine", [("MergeTree",), ("Memory",), ("S3",), ("DeltaLake",)])
def non_iceberg_engine_rejected(self, engine):
    """Only Iceberg-family engines are accepted inside a catalog database."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )
    with When("snapshot state"):
        before = snapshot_state(**args)
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        path=EXPLICIT_ENGINE,
        columns=COLUMNS,
        engine=engine_for(engine, table_name, minio_root_user, minio_root_password),
        order_by="id" if engine == "MergeTree" else None,
        exitcode=BAD_ARGUMENTS,
        message="-family tables; got table engine",  # "This DataLakeCatalog stores Iceberg-family tables; got table engine ...",
    )
    with When("snapshot state"):
        after = snapshot_state(**args)
    assert_rejected_no_trace(before=before, after=after, namespace_expected=False)


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_ExplicitEngine_BackendMismatch("1.0"))
@Examples("engine", [("IcebergAzure",), ("IcebergLocal",), ("IcebergHDFS",)])
def backend_mismatch_on_fixed_backend_catalog(self, engine):
    """A6: an engine on another backend than the catalog's fixed one is
    refused before anything is written."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    fixed = self.context.catalog == "glue" or getattr(catalog, "properties", {}).get(
        "default-base-location"
    )
    if not fixed:
        skip(
            "catalog has no fixed backend; see any_iceberg_engine_accepted_without_fixed_backend"
        )

    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )
    with When("snapshot state"):
        before = snapshot_state(**args)
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        path=EXPLICIT_ENGINE,
        columns=COLUMNS,
        engine=engine_for(engine, table_name, minio_root_user, minio_root_password),
        exitcode=BAD_ARGUMENTS,
        message="stores tables on",
    )
    with When("snapshot state"):
        after = snapshot_state(**args)
    assert_rejected_no_trace(before=before, after=after, namespace_expected=False)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_ExplicitEngine_GenericIcebergEngine("1.0"))
def generic_iceberg_engine_on_fixed_backend_catalog(self):
    """The generic `Iceberg` engine is refused on a fixed-backend catalog and
    the message points at the backend-specific engine."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    fixed = self.context.catalog == "glue" or getattr(catalog, "properties", {}).get(
        "default-base-location"
    )
    if not fixed:
        skip("catalog has no fixed backend")

    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )
    with When("snapshot state"):
        before = snapshot_state(**args)
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        path=EXPLICIT_ENGINE,
        columns=COLUMNS,
        engine=engine_for("Iceberg", table_name, minio_root_user, minio_root_password),
        exitcode=BAD_ARGUMENTS,
        message="backend-specific Iceberg engine",
    )
    with When("snapshot state"):
        after = snapshot_state(**args)
    assert_rejected_no_trace(before=before, after=after, namespace_expected=False)


@TestScenario
@Requirements(RQ_Iceberg_NativeCreateDrop_ExplicitEngine_BackendMismatch("1.0"))
def any_iceberg_engine_accepted_without_fixed_backend(self):
    """On a catalog with no fixed backend the DDL-level check accepts every
    Iceberg engine; `IcebergS3` produces a fully working table."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    if self.context.catalog == "glue" or getattr(catalog, "properties", {}).get(
        "default-base-location"
    ):
        skip("catalog has a fixed backend")

    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with When("IcebergS3 explicit engine"):
        before = snapshot_state(**args)
        create_table(
            database_name=database_name,
            namespace=namespace,
            table_name=table_name,
            path=EXPLICIT_ENGINE,
            columns=COLUMNS,
        )

    with Then("B1 and A"):
        after = snapshot_state(**args)
        assert_table_created(before=before, after=after)
        check_state_invariants(**args, expected=PRESENT, state=after)


@TestOutline(Scenario)
@Requirements(RQ_Iceberg_NativeCreateDrop_Metadata_InitialFile("1.0"))
@Examples("version_hint", [(0,), (1,)])
def initial_file_naming(self, version_hint):
    """The initial file is `v1[-<uuid>].metadata.json` (uuid for a
    transactional catalog) and, with iceberg_use_version_hint, a
    version-hint.text holding 1."""
    minio_root_user = self.context.minio_root_user
    minio_root_password = self.context.minio_root_password
    with Given("catalog and database"):
        catalog, database_name = catalog_and_database(
            minio_root_user=minio_root_user, minio_root_password=minio_root_password
        )
    namespace, table_name = f"ns_{getuid()}", f"t_{getuid()}"
    args = dict(
        catalog=catalog,
        namespace=namespace,
        table_name=table_name,
        database_name=database_name,
    )

    with When("snapshot state"):
        before = snapshot_state(**args)
    create_table(
        database_name=database_name,
        namespace=namespace,
        table_name=table_name,
        path=EXPLICIT_ENGINE,
        columns=COLUMNS,
        engine_settings=(
            {"iceberg_use_version_hint": version_hint} if version_hint else None
        ),
    )
    with When("snapshot state"):
        after = snapshot_state(**args)
    assert_table_created(before=before, after=after, version_hint=bool(version_hint))

    name = after.metadata_files[0].rsplit("/", 1)[-1]
    if self.context.catalog == "glue":
        assert name == "v1.metadata.json", error(name)
    else:
        assert name.startswith("v1") and name.endswith(".metadata.json"), error(name)
        note(f"initial file name on {self.context.catalog}: {name}")
        metadata = s3.read_json_object(after.metadata_files[0])
        if name != "v1.metadata.json":
            assert metadata["table-uuid"] in name, error(
                f"{name} does not carry table-uuid {metadata['table-uuid']}"
            )


@TestFeature
@Name("explicit engine")
def feature(self, minio_root_user, minio_root_password):
    """Explicit engine path."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
