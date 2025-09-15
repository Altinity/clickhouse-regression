from oauth.tests.steps.clikhouse import *
from testflows.asserts import *
from oauth.requirements.requirements import *


@TestCheck
def access_clickhouse_with_modified_token(self, token_modification_step):
    """Attempt to access ClickHouse with a modified JWT token."""

    with Given("I get a valid OAuth token from the provider"):
        client = self.context.provider_client
        original_token = client.OAuthProvider.get_oauth_token()

    with When("I modify the token using the specified step"):
        modified_token = token_modification_step(original_token)

    with Then("I try to access ClickHouse with the modified token"):
        pass

    with And("I check that the ClickHouse server is still alive"):
        check_clickhouse_is_alive()


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def test_jwt_header_modifications(self):
    """Test ClickHouse behavior with modified JWT header fields."""
    client = self.context.provider_client

    header_modifications = [
        (
            "modify_jwt_header_alg_to_none",
            client.OAuthProvider.modify_jwt_header_alg_to_none,
        ),
        (
            "modify_jwt_header_alg_to_hs256",
            client.OAuthProvider.modify_jwt_header_alg_to_hs256,
        ),
        (
            "modify_jwt_header_alg_to_invalid",
            client.OAuthProvider.modify_jwt_header_alg_to_invalid,
        ),
        (
            "modify_jwt_header_typ_to_invalid",
            client.OAuthProvider.modify_jwt_header_typ_to_invalid,
        ),
        (
            "modify_jwt_header_kid_to_invalid",
            client.OAuthProvider.modify_jwt_header_kid_to_invalid,
        ),
    ]

    for modification_step in header_modifications:
        access_clickhouse_with_modified_token(token_modification_step=modification_step)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def test_jwt_payload_exp_modifications(self):
    """Test ClickHouse behavior with modified JWT expiration fields."""
    client = self.context.provider_client

    exp_modifications = [
        (
            "modify_jwt_payload_exp_to_expired",
            client.OAuthProvider.modify_jwt_payload_exp_to_expired,
        ),
        (
            "modify_jwt_payload_exp_to_far_future",
            client.OAuthProvider.modify_jwt_payload_exp_to_far_future,
        ),
        (
            "modify_jwt_payload_iat_to_future",
            client.OAuthProvider.modify_jwt_payload_iat_to_future,
        ),
    ]

    for modification_step in exp_modifications:
        access_clickhouse_with_modified_token(token_modification_step=modification_step)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def test_jwt_payload_identity_modifications(self):
    """Test ClickHouse behavior with modified JWT identity fields."""
    client = self.context.provider_client

    identity_modifications = [
        (
            "modify_jwt_payload_jti_to_invalid",
            client.OAuthProvider.modify_jwt_payload_jti_to_invalid,
        ),
        (
            "modify_jwt_payload_iss_to_invalid",
            client.OAuthProvider.modify_jwt_payload_iss_to_invalid,
        ),
        (
            "modify_jwt_payload_sub_to_invalid",
            client.OAuthProvider.modify_jwt_payload_sub_to_invalid,
        ),
        (
            "modify_jwt_payload_typ_to_invalid",
            client.OAuthProvider.modify_jwt_payload_typ_to_invalid,
        ),
        (
            "modify_jwt_payload_azp_to_invalid",
            client.OAuthProvider.modify_jwt_payload_azp_to_invalid,
        ),
        (
            "modify_jwt_payload_sid_to_invalid",
            client.OAuthProvider.modify_jwt_payload_sid_to_invalid,
        ),
    ]

    for modification_step in identity_modifications:
        access_clickhouse_with_modified_token(token_modification_step=modification_step)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def test_jwt_payload_authorization_modifications(self):
    """Test ClickHouse behavior with modified JWT authorization fields."""
    client = self.context.provider_client

    auth_modifications = [
        (
            "modify_jwt_payload_acr_to_invalid",
            client.OAuthProvider.modify_jwt_payload_acr_to_invalid,
        ),
        (
            "modify_jwt_payload_allowed_origins_to_invalid",
            client.OAuthProvider.modify_jwt_payload_allowed_origins_to_invalid,
        ),
        (
            "modify_jwt_payload_scope_to_invalid",
            client.OAuthProvider.modify_jwt_payload_scope_to_invalid,
        ),
        (
            "modify_jwt_payload_groups_to_admin",
            client.OAuthProvider.modify_jwt_payload_groups_to_admin,
        ),
        (
            "modify_jwt_payload_groups_to_empty",
            client.OAuthProvider.modify_jwt_payload_groups_to_empty,
        ),
    ]

    for modification_step in auth_modifications:
        access_clickhouse_with_modified_token(token_modification_step=modification_step)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def test_jwt_payload_user_info_modifications(self):
    """Test ClickHouse behavior with modified JWT user information fields."""
    client = self.context.provider_client

    user_info_modifications = [
        (
            "modify_jwt_payload_email_verified_to_false",
            client.OAuthProvider.modify_jwt_payload_email_verified_to_false,
        ),
        (
            "modify_jwt_payload_name_to_invalid",
            client.OAuthProvider.modify_jwt_payload_name_to_invalid,
        ),
        (
            "modify_jwt_payload_preferred_username_to_admin",
            client.OAuthProvider.modify_jwt_payload_preferred_username_to_admin,
        ),
        (
            "modify_jwt_payload_given_name_to_invalid",
            client.OAuthProvider.modify_jwt_payload_given_name_to_invalid,
        ),
        (
            "modify_jwt_payload_family_name_to_invalid",
            client.OAuthProvider.modify_jwt_payload_family_name_to_invalid,
        ),
        (
            "modify_jwt_payload_email_to_invalid",
            client.OAuthProvider.modify_jwt_payload_email_to_invalid,
        ),
    ]

    for modification_step in user_info_modifications:
        access_clickhouse_with_modified_token(token_modification_step=modification_step)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def test_jwt_signature_modifications(self):
    """Test ClickHouse behavior with modified JWT signatures."""
    client = self.context.provider_client

    signature_modifications = [
        (
            "modify_jwt_signature_to_invalid",
            client.OAuthProvider.modify_jwt_signature_to_invalid,
        ),
        ("invalidate_jwt_signature", client.OAuthProvider.invalidate_jwt_signature),
        ("remove_jwt_signature", client.OAuthProvider.remove_jwt_signature),
        (
            "modify_jwt_signature_e_to_invalid",
            client.OAuthProvider.modify_jwt_signature_e_to_invalid,
        ),
        (
            "modify_jwt_signature_kty_to_invalid",
            client.OAuthProvider.modify_jwt_signature_kty_to_invalid,
        ),
        (
            "modify_jwt_signature_n_to_invalid",
            client.OAuthProvider.modify_jwt_signature_n_to_invalid,
        ),
    ]

    for modification_step in signature_modifications:
        access_clickhouse_with_modified_token(token_modification_step=modification_step)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def test_comprehensive_jwt_modifications(self):
    """Test all JWT token modifications comprehensively."""
    client = self.context.provider_client

    all_modifications = [
        (
            "modify_jwt_header_alg_to_none",
            client.OAuthProvider.modify_jwt_header_alg_to_none,
        ),
        (
            "modify_jwt_header_alg_to_hs256",
            client.OAuthProvider.modify_jwt_header_alg_to_hs256,
        ),
        (
            "modify_jwt_header_alg_to_invalid",
            client.OAuthProvider.modify_jwt_header_alg_to_invalid,
        ),
        (
            "modify_jwt_header_typ_to_invalid",
            client.OAuthProvider.modify_jwt_header_typ_to_invalid,
        ),
        (
            "modify_jwt_header_kid_to_invalid",
            client.OAuthProvider.modify_jwt_header_kid_to_invalid,
        ),
        (
            "modify_jwt_payload_exp_to_expired",
            client.OAuthProvider.modify_jwt_payload_exp_to_expired,
        ),
        (
            "modify_jwt_payload_exp_to_far_future",
            client.OAuthProvider.modify_jwt_payload_exp_to_far_future,
        ),
        (
            "modify_jwt_payload_iat_to_future",
            client.OAuthProvider.modify_jwt_payload_iat_to_future,
        ),
        (
            "modify_jwt_payload_jti_to_invalid",
            client.OAuthProvider.modify_jwt_payload_jti_to_invalid,
        ),
        (
            "modify_jwt_payload_iss_to_invalid",
            client.OAuthProvider.modify_jwt_payload_iss_to_invalid,
        ),
        (
            "modify_jwt_payload_sub_to_invalid",
            client.OAuthProvider.modify_jwt_payload_sub_to_invalid,
        ),
        (
            "modify_jwt_payload_typ_to_invalid",
            client.OAuthProvider.modify_jwt_payload_typ_to_invalid,
        ),
        (
            "modify_jwt_payload_azp_to_invalid",
            client.OAuthProvider.modify_jwt_payload_azp_to_invalid,
        ),
        (
            "modify_jwt_payload_sid_to_invalid",
            client.OAuthProvider.modify_jwt_payload_sid_to_invalid,
        ),
        (
            "modify_jwt_payload_acr_to_invalid",
            client.OAuthProvider.modify_jwt_payload_acr_to_invalid,
        ),
        (
            "modify_jwt_payload_allowed_origins_to_invalid",
            client.OAuthProvider.modify_jwt_payload_allowed_origins_to_invalid,
        ),
        (
            "modify_jwt_payload_scope_to_invalid",
            client.OAuthProvider.modify_jwt_payload_scope_to_invalid,
        ),
        (
            "modify_jwt_payload_groups_to_admin",
            client.OAuthProvider.modify_jwt_payload_groups_to_admin,
        ),
        (
            "modify_jwt_payload_groups_to_empty",
            client.OAuthProvider.modify_jwt_payload_groups_to_empty,
        ),
        (
            "modify_jwt_payload_email_verified_to_false",
            client.OAuthProvider.modify_jwt_payload_email_verified_to_false,
        ),
        (
            "modify_jwt_payload_name_to_invalid",
            client.OAuthProvider.modify_jwt_payload_name_to_invalid,
        ),
        (
            "modify_jwt_payload_preferred_username_to_admin",
            client.OAuthProvider.modify_jwt_payload_preferred_username_to_admin,
        ),
        (
            "modify_jwt_payload_given_name_to_invalid",
            client.OAuthProvider.modify_jwt_payload_given_name_to_invalid,
        ),
        (
            "modify_jwt_payload_family_name_to_invalid",
            client.OAuthProvider.modify_jwt_payload_family_name_to_invalid,
        ),
        (
            "modify_jwt_payload_email_to_invalid",
            client.OAuthProvider.modify_jwt_payload_email_to_invalid,
        ),
        (
            "modify_jwt_signature_to_invalid",
            client.OAuthProvider.modify_jwt_signature_to_invalid,
        ),
        ("invalidate_jwt_signature", client.OAuthProvider.invalidate_jwt_signature),
        ("remove_jwt_signature", client.OAuthProvider.remove_jwt_signature),
        (
            "modify_jwt_signature_e_to_invalid",
            client.OAuthProvider.modify_jwt_signature_e_to_invalid,
        ),
        (
            "modify_jwt_signature_kty_to_invalid",
            client.OAuthProvider.modify_jwt_signature_kty_to_invalid,
        ),
        (
            "modify_jwt_signature_n_to_invalid",
            client.OAuthProvider.modify_jwt_signature_n_to_invalid,
        ),
    ]

    for modification_step in all_modifications:
        access_clickhouse_with_modified_token(token_modification_step=modification_step)


@TestScenario
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
)
def test_multiple_jwt_modifications(self):
    """Test combining multiple JWT token modifications."""
    client = self.context.provider_client

    with Given("I get a valid OAuth token from the provider"):
        original_token = client.OAuthProvider.get_oauth_token()

    modifications_combinations = [
        (
            "header + payload",
            client.OAuthProvider.modify_jwt_header_alg_to_invalid,
            client.OAuthProvider.modify_jwt_payload_exp_to_expired,
        ),
        (
            "payload + signature",
            client.OAuthProvider.modify_jwt_payload_groups_to_admin,
            client.OAuthProvider.invalidate_jwt_signature,
        ),
        (
            "header + signature",
            client.OAuthProvider.modify_jwt_header_alg_to_none,
            client.OAuthProvider.remove_jwt_signature,
        ),
    ]

    for combination_name, first_step, second_step in modifications_combinations:
        token_step1 = first_step(original_token)
        modified_token = second_step(token_step1)
        check_clickhouse_is_alive()


@TestFeature
@Name("jwt_manipulation")
@Requirements(
    RQ_SRS_042_OAuth_Authentication_UserDirectories_IncorrectConfiguration_provider(
        "1.0"
    ),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Alg("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Typ("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Exp("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Header_Signature("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Sub("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Aud("1.0"),
    RQ_SRS_042_OAuth_Authentication_IncorrectRequests_Body_Exp("1.0"),
    RQ_SRS_042_OAuth_Authentication_TokenHandling_Incorrect("1.0"),
    RQ_SRS_042_OAuth_Authentication_TokenHandling_EmptyString("1.0"),
)
def feature(self):
    """Feature to test OAuth authentication flow with JWT token manipulation."""

    Scenario(run=test_jwt_header_modifications)
    Scenario(run=test_jwt_payload_exp_modifications)
    Scenario(run=test_jwt_payload_identity_modifications)
    Scenario(run=test_jwt_payload_authorization_modifications)
    Scenario(run=test_jwt_payload_user_info_modifications)
    Scenario(run=test_jwt_signature_modifications)
    Scenario(run=test_comprehensive_jwt_modifications)
    Scenario(run=test_multiple_jwt_modifications)
