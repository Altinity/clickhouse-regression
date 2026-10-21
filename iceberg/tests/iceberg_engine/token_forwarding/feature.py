from testflows.core import *

from helpers.common import check_clickhouse_version, check_if_antalya_build

from iceberg.tests.iceberg_engine.token_forwarding.steps import (
    ALLOWED_HOSTS,
    feature_available,
    mocks_are_running,
    token_forwarding_server_config,
)

MODULES = [
    "capture",
    "rest_passthrough",
    "rest_exchange",
    "vended_credentials",
    "writes",
    "propagation",
    "configuration",
    "glue",
]


@TestFeature
@Name("token forwarding")
def feature(self, minio_root_user, minio_root_password):
    """Forwarding the querying user's bearer token to Iceberg REST and Glue
    catalogs (`oauth_forward_user_token`, Altinity/ClickHouse#2329)."""
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password
    self.context.catalog = "rest"

    if not (check_if_antalya_build(self) and check_clickhouse_version(">=26.6")(self)):
        skip("token forwarding to data lake catalogs needs an Antalya build >= 26.6")

    if not feature_available(self.context.node):
        skip("build has no `enable_token_forwarding` server setting")

    with Given("the token-mocks service is running"):
        mocks_are_running()

    with And("token authentication and token forwarding are enabled on all nodes"):
        token_forwarding_server_config(allowed_hosts=ALLOWED_HOSTS)

    for module in MODULES:
        Feature(
            test=load(
                f"iceberg.tests.iceberg_engine.token_forwarding.{module}", "feature"
            ),
            flags=TE,
        )()
