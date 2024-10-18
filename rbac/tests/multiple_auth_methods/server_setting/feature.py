from testflows.core import *
from rbac.helper.common import *


@TestFeature
@Name("server setting max_authentication_methods_per_user")
def feature(self):
    """Check different manipulations with user's authentication methods with
    different values of `max_authentication_methods_per_user` setting."""
    Feature(
        run=load(
            "rbac.tests.multiple_auth_methods.server_setting.server_setting_create_user",
            "feature",
        ),
    )
    Feature(
        run=load(
            "rbac.tests.multiple_auth_methods.server_setting.server_setting_alter_user",
            "feature",
        ),
    )
    Feature(
        run=load(
            "rbac.tests.multiple_auth_methods.server_setting.server_setting_reset_auth_methods",
            "feature",
        ),
    )
    Feature(
        run=load(
            "rbac.tests.multiple_auth_methods.server_setting.server_setting_add_identified",
            "feature",
        ),
    )
