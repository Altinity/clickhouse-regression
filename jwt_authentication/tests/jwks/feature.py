from testflows.core import *


@TestFeature
@Name("static jwks")
def feature(self, node="clickhouse1"):
    """Check jwt authentication with static jwks validator."""

    Feature(run=load("jwt_authentication.tests.jwks.different_algorithms", "feature"))
    Feature(run=load("jwt_authentication.tests.jwks.mismatch_algorithms", "feature"))