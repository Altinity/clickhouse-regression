from testflows.core import *


@TestFeature
@Name("multiple authentication methods")
def feature(self, node="clickhouse1"):
    """Check support of multiple authentication methods."""

    self.context.node = self.context.cluster.node(node)

    with Pool(4) as executor:
        Scenario(
            test=load(
                "rbac.tests.privileges.multiple_auth_methods_v2.create_user", "feature"
            ),
            parallel=True,
            executor=executor,
        )()
        Scenario(
            test=load(
                "rbac.tests.privileges.multiple_auth_methods_v2.alter_user", "feature"
            ),
            parallel=True,
            executor=executor,
        )()
        join()
