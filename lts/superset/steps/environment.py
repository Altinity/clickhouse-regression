"""Reusable steps for setting up and tearing down the Superset + ClickHouse environment."""

import os
import subprocess

from testflows.core import *


@TestStep(Given)
def superset_environment(
    self,
    configs_dir,
    clickhouse_image,
    superset_version="4.1.1",
    clickhouse_driver="clickhouse-connect",
):
    """Bootstrap and start the Superset + ClickHouse Docker Compose environment.

    Yields after services are up; tears down on exit.
    """
    bootstrap_script = os.path.join(configs_dir, "bootstrap.sh")

    env = os.environ.copy()
    env["SUPERSET_VERSION"] = superset_version
    env["CLICKHOUSE_IMAGE"] = clickhouse_image
    env["CLICKHOUSE_PYTHON_DRIVER"] = clickhouse_driver

    note(f"Bootstrapping Superset {superset_version} with driver={clickhouse_driver}")
    result = subprocess.run(
        ["bash", bootstrap_script],
        cwd=configs_dir,
        env=env,
    )
    if result.returncode != 0:
        fail(f"bootstrap.sh failed with exit code {result.returncode}")

    try:
        yield
    finally:
        note("Tearing down Superset environment")
        subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                "./superset/docker-compose-non-dev.yml",
                "down",
                "--remove-orphans",
            ],
            cwd=configs_dir,
        )


@TestStep(Given)
def wait_for_superset(self, url="http://localhost:8088/health", timeout=120):
    """Wait until Superset health endpoint responds."""
    import time
    import urllib.request

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = urllib.request.urlopen(url, timeout=5)
            if resp.status == 200:
                note("Superset is healthy")
                return
        except Exception:
            pass
        time.sleep(5)
    fail(f"Superset did not become healthy within {timeout}s")
