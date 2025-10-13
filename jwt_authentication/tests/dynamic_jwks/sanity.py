from testflows.core import *

from helpers.common import getuid
from jwt_authentication.requirements import *
import jwt_authentication.tests.steps as steps


def curl_with_jwt(token, ip, https=False):
    http_prefix = "https" if https else "http"
    curl = f'curl -H "X-ClickHouse-JWT-Token: Bearer {token}" "{http_prefix}://{ip}:8123/?query=SELECT%20currentUser()"'
    return curl


@TestFeature
@Name("check dynamic jwks")
def check_dynamic_jwks(self):
    steps.create_user_with_jwt_auth(user_name="jwt_user")
    node = self.context.node
    curl_auth = curl_with_jwt(
        token="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiIsImtpZCI6Im15a2lkIn0."
        "eyJzdWIiOiJqd3RfdXNlciIsImlzcyI6InRlc3RfaXNzIn0.MjegqrrVyrMMpkxIM-J_q-"
        "Sw68Vk5xZuFpxecLLMFs5qzvnh0jslWtyRfi-ANJeJTONPZM5m0yP1ITt8BExoHWobkkR11bXz0ylYEIOgwxqw"
        "36XhL2GkE17p-wMvfhCPhGOVL3b7msDRUKXNN48aAJA-NxRbQFhMr-eEx3HsrZXy17Qc7z-"
        "0dINe355kzAInGp6gMk3uksAlJ3vMODK8jE-WYFqXusr5GFhXubZXdE2mK0mIbMUGisOZhZLc4QVwvUsYDLBCgJ2RHr5vm"
        "jp17j_ZArIedUJkjeC4o72ZMC97kLVnVw94QJwNvd4YisxL6A_mWLTRq9FqNLD4HmbcOQ",
        ip="localhost",
    )
    node.command(curl_auth)
