"""Deletion vectors apply identically across every Iceberg access form and
storage backend.

One fixture table is created at the feature level and shared read-only by
all suites; each access form (icebergS3 table function, Iceberg table
engine, DataLakeCatalog database, icebergLocal, icebergAzure) gets its own
suite of scenarios over it."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.local_clone as local_clone

ROWS = 100
DELETED = list(range(0, ROWS, 10))
EXPECTED = [i for i in range(ROWS) if i % 10 != 0]


@TestScenario
@Requirements(
    RQ_Iceberg_DeletionVectors_AccessForms("1.0"),
    RQ_Iceberg_DeletionVectors_StorageBackends("1.0"),
)
def function_select(self):
    """The full visible row set through the icebergS3 table function."""
    with Then("deleted rows are excluded exactly"):
        common.assert_visible_ids(table=self.context.table, ids=EXPECTED)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_AccessForms("1.0"))
def function_count(self):
    """count() through the icebergS3 table function."""
    with Then("the count reflects the deletion vector"):
        assert common.count_rows(table=self.context.table) == len(EXPECTED), error()


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_AccessForms("1.0"))
def function_filtered_select(self):
    """A filtered read through the icebergS3 table function."""
    with Then("the filter applies on top of the deletion vector"):
        ids = common.select_ids(table=self.context.table, where_clause="id < 50")
        assert ids == [i for i in EXPECTED if i < 50], error(
            f"filtered read returned {len(ids)} rows"
        )


@TestSuite
@Requirements(
    RQ_Iceberg_DeletionVectors_AccessForms("1.0"),
    RQ_Iceberg_DeletionVectors_StorageBackends("1.0"),
)
def icebergS3_function(self):
    """Reads through the icebergS3 table function (S3 storage backend)."""
    Scenario(run=function_select)
    Scenario(run=function_count)
    Scenario(run=function_filtered_select)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_AccessForms("1.0"))
def engine_select(self):
    """The full visible row set through the Iceberg table engine."""
    with Then("deleted rows are excluded exactly"):
        result = self.context.node.query(
            f"SELECT id FROM {self.context.engine_table} "
            f"ORDER BY id FORMAT TabSeparated"
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == EXPECTED, error(f"engine returned {len(ids)} rows")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_AccessForms("1.0"))
def engine_count(self):
    """count() through the Iceberg table engine."""
    with Then("the count reflects the deletion vector"):
        result = self.context.node.query(
            f"SELECT count() FROM {self.context.engine_table} FORMAT TabSeparated"
        )
        assert int(result.output.strip()) == len(EXPECTED), error(result.output)


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_AccessForms("1.0"))
def iceberg_engine(self):
    """Reads through a table with the Iceberg table engine."""
    with Given("an Iceberg engine table over the shared fixture table"):
        self.context.engine_table = common.engine_table(table=self.context.table)

    Scenario(run=engine_select)
    Scenario(run=engine_count)


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_AccessForms("1.0"))
def catalog_select(self):
    """The full visible row set through a DataLakeCatalog database."""
    with Then("deleted rows are excluded exactly"):
        result = self.context.node.query(
            f"SELECT id FROM {self.context.catalog_table} "
            f"ORDER BY id FORMAT TabSeparated"
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == EXPECTED, error(f"catalog returned {len(ids)} rows")


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_AccessForms("1.0"))
def catalog_count(self):
    """count() through a DataLakeCatalog database."""
    with Then("the count reflects the deletion vector"):
        result = self.context.node.query(
            f"SELECT count() FROM {self.context.catalog_table} FORMAT TabSeparated"
        )
        assert int(result.output.strip()) == len(EXPECTED), error(result.output)


@TestSuite
@Requirements(RQ_Iceberg_DeletionVectors_AccessForms("1.0"))
def datalake_catalog(self):
    """Reads through a DataLakeCatalog database over the REST catalog."""
    with Given("a DataLakeCatalog database over the REST catalog"):
        database_name = common.catalog_database()
        self.context.catalog_table = common.catalog_table_expr(
            database_name, self.context.table
        )

    Scenario(run=catalog_select)
    Scenario(run=catalog_count)


@TestScenario
@Requirements(
    RQ_Iceberg_DeletionVectors_AccessForms("1.0"),
    RQ_Iceberg_DeletionVectors_StorageBackends("1.0"),
)
def local_select(self):
    """The full visible row set through icebergLocal on a local-filesystem
    clone of the S3 table."""
    with Then("deleted rows are excluded exactly"):
        ids = local_clone.read_local_ids(local_dir=self.context.local_dir)
        assert ids == EXPECTED, error(f"icebergLocal returned {len(ids)} rows")


@TestSuite
@Requirements(
    RQ_Iceberg_DeletionVectors_AccessForms("1.0"),
    RQ_Iceberg_DeletionVectors_StorageBackends("1.0"),
)
def icebergLocal_function(self):
    """Reads through the icebergLocal table function (local filesystem
    storage backend)."""
    with Given("a local-filesystem clone of the shared fixture table"):
        self.context.local_dir = local_clone.clone_table_to_local(
            table=self.context.table
        )

    Scenario(run=local_select)


@TestScenario
@Requirements(
    RQ_Iceberg_DeletionVectors_AccessForms("1.0"),
    RQ_Iceberg_DeletionVectors_StorageBackends("1.0"),
)
def azure_select(self):
    """Reads through the icebergAzure table function (Azure storage
    backend)."""
    skip(
        "the iceberg_env docker environment has no Azure (azurite) "
        "service, so icebergAzure cannot be exercised here"
    )


@TestSuite
@Requirements(
    RQ_Iceberg_DeletionVectors_AccessForms("1.0"),
    RQ_Iceberg_DeletionVectors_StorageBackends("1.0"),
)
def icebergAzure_function(self):
    """Reads through the icebergAzure table function (Azure storage
    backend) — not testable in this environment."""
    Scenario(run=azure_select)


@TestFeature
@Name("access forms")
def feature(self, minio_root_user, minio_root_password):
    """Access-form and storage-backend independence of deletion vectors."""
    with Given("a table with a deletion vector shared by every access form"):
        self.context.table = common.table_with_deletion_vectors(
            rows=ROWS, delete_condition="id % 10 = 0"
        )

    Suite(run=icebergS3_function)
    Suite(run=iceberg_engine)
    Suite(run=datalake_catalog)
    Suite(run=icebergLocal_function)
    Suite(run=icebergAzure_function)
