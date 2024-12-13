from testflows.core import *


@TestFeature
@Name("dynamic jwks")
def feature(self):
    """Check jwt authentication with dynamic jwks validator."""

    Feature(
        run=load("jwt_authentication.tests.dynamic_jwks.sanity", "check_dynamic_jwks")
    )
