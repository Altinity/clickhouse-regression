from testflows.core import *

from jwt_authentication.requirements import *


@TestFeature
@Name("static key")
@Requirements(
    RQ_SRS_042_JWT_StaticKey("1.0"),
)
def feature(self, node="clickhouse1"):
    """Check jwt authentication with static key validator."""

    Feature(run=load("jwt_authentication.tests.static_key.sanity", "feature"))
    Feature(run=load("jwt_authentication.tests.static_key.recreate_user", "feature"))
    Feature(
        run=load("jwt_authentication.tests.static_key.different_algorithms", "feature")
    )
    Feature(run=load("jwt_authentication.tests.static_key.invalid_token", "feature"))
    Feature(
        run=load(
            "jwt_authentication.tests.static_key.combinatorial_test",
            "jwt_authentication_combinatorics",
        )
    )
    Feature(run=load("jwt_authentication.tests.static_key.on_cluster", "feature"))
