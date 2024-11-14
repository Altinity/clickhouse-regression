from testflows.core import *


@TestFeature
@Name("static key")
def feature(self, node="clickhouse1"):
    """Check jwt authentication with static key validator."""

    Feature(run=load("jwt_authentication.tests.static_key.sanity", "feature"))
    Feature(run=load("jwt_authentication.tests.static_key.recreate_user", "feature"))
    Feature(
        run=load("jwt_authentication.tests.static_key.different_algorithms", "feature")
    )
    Feature(run=load("jwt_authentication.tests.static_key.invalid_token", "feature"))
