from testflows.core import *
from testflows.asserts import error

from iceberg.requirements.token_forwarding import *
from iceberg.tests.iceberg_engine.token_forwarding.steps import *


def vended(access_key, secret_key):
    return {
        "s3.access-key-id": access_key,
        "s3.secret-access-key": secret_key,
        "s3.endpoint": "http://minio:9000",
        "s3.path-style-access": "true",
    }


@TestScenario
@Requirements(RQ_Iceberg_TokenForwarding_VendedCredentials_PerUser("1.0"))
def vended_credentials_are_isolated_per_user(self):
    """Check that storage credentials vended for one user SHALL NOT be reused
    for another user's query on the same table, in either order."""
    alice, mallory = make_token("alice"), make_token("mallory")

    with Given("a table and a forwarding database without storage keys"):
        clean_mocks()
        namespace, table, rows = catalog_table()
        database = forwarding_database(with_storage_keys=False)

    with And(
        "the catalog vends working credentials to alice and broken ones to mallory"
    ):
        configure_mocks(
            catalog={
                "vended": {
                    "alice": vended(
                        self.context.minio_root_user, self.context.minio_root_password
                    ),
                    "mallory": vended("mallory_key", "mallory_secret"),
                }
            }
        )

    sql = select_rows_sql(database, namespace, table)

    with When("alice reads the table"):
        result = jwt_query(sql=sql, token=alice)

    with Then("she gets the rows"):
        assert result.output.strip() == expected_rows(rows), error()

    with And("ClickHouse asked the catalog for vended credentials"):
        delegations = {
            r["access_delegation"]
            for r in catalog_requests()
            if r["path"].endswith(f"/tables/{table}")
        }
        assert "vended-credentials" in delegations, error()

    with When("mallory reads the same table right after"):
        result = jwt_query(sql=sql, token=mallory, no_checks=True)

    with Then(
        "mallory's read fails with her own credentials instead of reusing alice's"
    ):
        assert result.exitcode != 0, error(result.output)

    with When("alice reads the table again"):
        result = jwt_query(sql=sql, token=alice)

    with Then("her read is not affected by mallory's credentials"):
        assert result.output.strip() == expected_rows(rows), error()


@TestFeature
@Name("vended credentials")
def feature(self):
    """Storage credentials vended by the REST catalog are cached per user."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario, flags=TE)
