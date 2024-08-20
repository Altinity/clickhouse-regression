from testflows.core import *

from rbac.helper.common import *


@TestFeature
@Name("multiple authentication methods")
def feature(self, node="clickhouse1"):
    """Check that multiple authentication methods support."""
    self.context.node = self.context.cluster.node(node)
    with Pool(4) as pool:
        try:
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
                    "rbac.tests.privileges.multiple_auth_methods.create", "feature"
                ),
                parallel=True,
                executor=pool,
            )
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.system_table",
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
                    "rbac.tests.privileges.multiple_auth_methods.many_auth_methods",
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
        finally:
            join()
