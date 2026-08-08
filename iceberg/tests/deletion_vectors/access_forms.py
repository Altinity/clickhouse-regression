"""Deletion vectors apply identically across every Iceberg access form and
storage backend."""

from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.deletion_vectors import *

import iceberg.tests.deletion_vectors.steps.common as common
import iceberg.tests.deletion_vectors.steps.local_clone as local_clone


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_AccessForms("1.0"))
def access_forms(self):
    """The same table returns the same logical row set through the
    icebergS3 table function, the Iceberg table engine, a DataLakeCatalog
    database, and icebergLocal (on a local clone)."""
    rows = 100
    deleted = [i for i in range(rows) if i % 10 == 0]
    expected = common.expected_ids(rows, deleted)

    with Given("a table with a deletion vector"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 10 = 0"
        )

    with Check("icebergS3 table function"):
        common.assert_visible_ids(table=table, ids=expected)

    with Check("Iceberg table engine"):
        engine_table = common.engine_table(table=table)
        result = self.context.node.query(
            f"SELECT id FROM {engine_table} ORDER BY id FORMAT TabSeparated"
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == expected, error(f"engine returned {len(ids)} rows")

    with Check("DataLakeCatalog database"):
        database_name = common.catalog_database()
        result = self.context.node.query(
            f"SELECT id FROM {common.catalog_table_expr(database_name, table)} "
            f"ORDER BY id FORMAT TabSeparated"
        )
        ids = [int(line) for line in result.output.split() if line.strip()]
        assert ids == expected, error(f"catalog returned {len(ids)} rows")

    with Check("icebergLocal table function"):
        local_dir = local_clone.clone_table_to_local(table=table)
        ids = local_clone.read_local_ids(local_dir=local_dir)
        assert ids == expected, error(f"icebergLocal returned {len(ids)} rows")

    with Check("icebergAzure table function"):
        skip(
            "the iceberg_env docker environment has no Azure (azurite) "
            "service, so icebergAzure cannot be exercised here"
        )


@TestScenario
@Requirements(RQ_Iceberg_DeletionVectors_StorageBackends("1.0"))
def storage_backends(self):
    """Correctness does not depend on the storage backend: S3 (MinIO) and
    local filesystem return identical logical rows. Azure has no service in
    this environment."""
    rows = 60
    deleted = list(range(0, 60, 4))

    with Given("a table with a deletion vector on S3"):
        table = common.table_with_deletion_vectors(
            rows=rows, delete_condition="id % 4 = 0"
        )
        expected = common.expected_ids(rows, deleted)

    with Check("S3 backend"):
        common.assert_visible_ids(table=table, ids=expected)

    with Check("local filesystem backend"):
        local_dir = local_clone.clone_table_to_local(table=table)
        ids = local_clone.read_local_ids(local_dir=local_dir)
        assert ids == expected, error(
            f"local read returned {len(ids)} rows, expected {len(expected)}"
        )

    with Check("azure backend"):
        skip(
            "the iceberg_env docker environment has no Azure (azurite) "
            "service; deletion vectors on Azure storage are not testable here"
        )


@TestFeature
@Name("access forms")
def feature(self, minio_root_user, minio_root_password):
    """Access-form and storage-backend independence of deletion vectors."""
    Scenario(test=access_forms, flags=TE)()
    Scenario(test=storage_backends, flags=TE)()
