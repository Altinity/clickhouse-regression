import requests
from testflows.core import *


@TestStep(Then)
def access_clickhouse(token, ip="clickhouse", https=False):
    """Execute a query to ClickHouse with JWT token authentication."""
    http_prefix = "https" if https else "http"
    url = f"{http_prefix}://{ip}:8123/"

    headers = {"X-ClickHouse-JWT-Token": f"Bearer {token}"}

    params = {"query": "SELECT currentUser()"}

    verify = False if https else True

    response = requests.get(url, headers=headers, params=params, verify=verify)
    response.raise_for_status()

    return response.text.strip()
