from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


@TestScenario
@Name("jwt authentication on cluster")
def jwt_auth_on_cluster(self):
    """Check that user created with jwt authentication on cluster
    can login with jwt on all nodes."""
    nodes = [self.context.node, self.context.node2, self.context.node3]
    with Given("defining parameters for new validator"):
        validator_id = define("validator_id", "validator_1")
        algorithm = define("algorithm", "HS256")
        secret = define("secret", "some_secret")

    with And("add new validator to the config.xml on all nodes"):
        for node in nodes:
            steps.add_static_key_validator_to_config_xml(
                validator_id=validator_id, algorithm=algorithm, secret=secret, node=node
            )

    with When("create user with jwt authentication"):
        user_name = f"jwt_user_{getuid()}"
        steps.create_user_with_jwt_auth(
            user_name=user_name, cluster="replicated_cluster"
        )

    with And("create jwt"):
        token = steps.create_static_jwt(
            user_name=user_name, secret=secret, algorithm=algorithm
        )

    with Then("check that user can login with jwt on all nodes"):
        for node in nodes:
            steps.check_jwt_login(user_name=user_name, token=token, node=node)


@TestFeature
def feature(self):
    """Check jwt authentication with static key validator on cluster."""
    Scenario(test=jwt_auth_on_cluster, flags=TE)()
