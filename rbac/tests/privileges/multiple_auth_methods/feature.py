from testflows.core import *

from rbac.helper.common import *


@TestFeature
@Name("multiple authentication methods")
def feature(self):
    """Check that multiple authentication methods support."""
    with Pool(4) as pool:
        try:
            # Feature(
            #     run=load(
            #         "rbac.tests.privileges.multiple_auth_methods.reset", "feature"
            #     ),
            #     parallel=True,
            #     executor=pool,
            # )
            # Feature(
            #     run=load(
            #         "rbac.tests.privileges.multiple_auth_methods.add_identified",
            #         "feature",
            #     ),
            #     parallel=True,
            #     executor=pool,
            # )
            Feature(
                run=load(
                    "rbac.tests.privileges.multiple_auth_methods.alter_identified",
                    "feature",
                ),
                parallel=True,
                executor=pool,
            )
            # Feature(
            #     run=load(
            #         "rbac.tests.privileges.multiple_auth_methods.create", "feature"
            #     ),
            #     parallel=True,
            #     executor=pool,
            # )
        finally:
            join()
