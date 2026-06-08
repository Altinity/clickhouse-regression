"""[H-06] Invalid roles_filter regex — fail-closed validation.

Fixed in antalya-26.3 (PR #1777, commit H-06): ``TokenAccessStorage``
validates the RE2 pattern at construction time and throws
``BAD_ARGUMENTS`` when ``!roles_filter->ok()``, refusing to instantiate
the storage in a permissive state.

These scenarios verify that ClickHouse rejects the invalid config at
startup/reload and emits the expected error message.
"""

from testflows.core import *

from oauth.tests.steps.clikhouse import apply_fatal_user_directories_config


@TestScenario
@Name("H-06 / 1")
def scenario_1(self):
    """ClickHouse SHALL reject a user-directory config with an invalid
    roles_filter regex at parse time (fail-closed).
    """
    with Given("I apply a user_directories config with a malformed roles_filter"):
        apply_fatal_user_directories_config(
            entries={
                "user_directories": {
                    "token": {
                        "processor": "keycloak",
                        "common_roles": {"general-role": {}},
                        "roles_filter": "[invalid-regex",
                    }
                }
            },
            expected_message="Invalid 'roles_filter' regex",
        )


@TestScenario
@Name("H-06 / 2")
def scenario_2(self):
    """ClickHouse SHALL reject a user-directory config with a different
    malformed roles_filter regex (unmatched bracket).
    """
    with Given("I apply a user_directories config with another malformed regex"):
        apply_fatal_user_directories_config(
            entries={
                "user_directories": {
                    "token": {
                        "processor": "keycloak",
                        "common_roles": {"general-role": {}},
                        "roles_filter": "[broken",
                    }
                }
            },
            expected_message="Invalid 'roles_filter' regex",
        )


@TestFeature
@Name("H-06")
def feature(self):
    """[H-06] Invalid roles_filter regex — fail-closed validation."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
