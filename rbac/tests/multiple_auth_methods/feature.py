from testflows.core import *

from rbac.helper.common import *


@TestFeature
@Name("multiple authentication methods")
def feature(self, node="clickhouse1"):
    """Check that multiple authentication methods support."""
    self.context.node = self.context.cluster.node(node)
    self.context.node_2 = self.context.cluster.node("clickhouse2")
    self.context.node_3 = self.context.cluster.node("clickhouse3")
    self.context.nodes = [self.context.node, self.context.node_2, self.context.node_3]

    with Pool(5) as pool:
        try:
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.create", "feature"
                ),
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.reset", "feature"
                ),
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.alter_add_identified",
                    "feature",
                ),
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.alter_identified",
                    "feature",
                ),
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.syntax",
                    "feature",
                ),
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.sanity",
                    "feature",
                ),
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.multiple_users",
                    "feature",
                ),
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.on_cluster",
                    "feature",
                ),
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.combinations",
                    "feature",
                ),
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.combinations_on_cluster",
                    "feature",
                ),
                parallel=True,
                executor=pool,
            )

        finally:
            join()

    Feature(
        run=load(
            "rbac.tests.privileges.multiple_auth_methods.server_setting.feature",
            "feature",
        ),
    )
    Feature(
        run=load(
            "rbac.tests.privileges.multiple_auth_methods.many_auth_methods",
            "feature",
        ),
    )
    Feature(
        run=load(
            "rbac.tests.privileges.multiple_auth_methods.parallel_modification",
            "feature",
        ),
    )
