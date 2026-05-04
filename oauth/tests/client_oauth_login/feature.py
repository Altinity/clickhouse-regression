"""Tests for clickhouse-client's ``--login`` OAuth flow."""

from testflows.core import *


@TestFeature
@Name("client oauth login")
def feature(self):
    """Tests for clickhouse-client's ``--login`` OAuth flow."""

    Feature(run=load("oauth.tests.client_oauth_login.argument_validation", "feature"))
    Feature(run=load("oauth.tests.client_oauth_login.credentials_file", "feature"))
    Feature(run=load("oauth.tests.client_oauth_login.connection_block_segfault", "feature"))
    Feature(run=load("oauth.tests.client_oauth_login.device_flow", "feature"))
    Feature(run=load("oauth.tests.client_oauth_login.refresh_token_cache", "feature"))
    Feature(run=load("oauth.tests.client_oauth_login.cloud_auto_login", "feature"))
    Feature(run=load("oauth.tests.client_oauth_login.connection_block_oauth", "feature"))
