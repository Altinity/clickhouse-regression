"""Reusable steps for setting up and tearing down the Grafana + ClickHouse environment."""

import os
import subprocess
import time
import urllib.request

from testflows.core import *

PROJECT_NAME = "grafana-lts"


def _compose_cmd(compose_file):
    """Return the base docker compose command list."""
    return ["docker", "compose", "-f", compose_file, "-p", PROJECT_NAME]


@TestStep(Given)
def grafana_environment(
    self,
    configs_dir,
    clickhouse_image,
    grafana_version="latest",
    grafana_plugin_version="3.4.9",
    selenium_version="4.40.0",
):
    """Start the Grafana + ClickHouse + Selenium Docker Compose environment.

    Yields after services are up; tears down on exit.
    """
    compose_file = os.path.join(configs_dir, "docker-compose.yml")

    image_parts = clickhouse_image.rsplit(":", 1)
    ch_image = image_parts[0]
    ch_version = image_parts[1] if len(image_parts) > 1 else "latest"

    env = os.environ.copy()
    env["CLICKHOUSE_IMAGE"] = ch_image
    env["CLICKHOUSE_VERSION"] = ch_version
    env["GRAFANA_VERSION"] = grafana_version
    env["GRAFANA_PLUGIN_VERSION"] = grafana_plugin_version
    env["SELENIUM_VERSION"] = selenium_version

    self.context.grafana_compose_file = compose_file
    self.context.grafana_compose_env = env

    note(
        f"Starting environment: ClickHouse={clickhouse_image}, "
        f"Grafana={grafana_version}, Plugin={grafana_plugin_version}"
    )

    result = subprocess.run(
        _compose_cmd(compose_file) + ["up", "-d", "--wait"],
        cwd=configs_dir,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        note(f"stdout: {result.stdout}")
        note(f"stderr: {result.stderr}")
        fail(f"docker compose up failed with exit code {result.returncode}")

    try:
        yield
    finally:
        note("Tearing down Grafana environment")
        subprocess.run(
            _compose_cmd(compose_file) + ["down", "--remove-orphans", "-v"],
            cwd=configs_dir,
            env=env,
        )


def _get_selenium_host_port(compose_file, env):
    """Discover the ephemeral host port mapped to selenium:4444."""
    result = subprocess.run(
        _compose_cmd(compose_file) + ["port", "selenium", "4444"],
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"Failed to discover selenium port: {result.stderr}")
    addr = result.stdout.strip()
    return addr


@TestStep(Given)
def wait_for_grafana(self, timeout=180):
    """Wait until Grafana health endpoint responds (checked via docker exec)."""
    compose_file = self.context.grafana_compose_file
    env = self.context.grafana_compose_env

    deadline = time.time() + timeout
    while time.time() < deadline:
        result = subprocess.run(
            _compose_cmd(compose_file)
            + [
                "exec",
                "-T",
                "grafana",
                "curl",
                "-sf",
                "http://localhost:3000/api/health",
            ],
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            note("Grafana is healthy")
            return
        time.sleep(5)
    fail(f"Grafana did not become healthy within {timeout}s")


@TestStep(Given)
def wait_for_selenium(self, timeout=120):
    """Wait until Selenium Grid is ready and store its URL in context."""
    compose_file = self.context.grafana_compose_file
    env = self.context.grafana_compose_env

    addr = _get_selenium_host_port(compose_file, env)
    selenium_url = f"http://{addr}"
    status_url = f"{selenium_url}/wd/hub/status"

    note(f"Selenium Grid mapped to {selenium_url}")

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = urllib.request.urlopen(status_url, timeout=5)
            if resp.status == 200:
                note("Selenium Grid is ready")
                self.context.selenium_url = selenium_url
                return
        except Exception:
            pass
        time.sleep(5)
    fail(f"Selenium Grid did not become ready within {timeout}s")
