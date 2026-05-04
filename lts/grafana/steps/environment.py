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


def _get_compose_service_host_port(compose_file, env, service, container_port):
    """Discover the ephemeral host port mapped to ``service:container_port``."""
    result = subprocess.run(
        _compose_cmd(compose_file) + ["port", service, str(container_port)],
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(
            f"Failed to discover host port for {service}:{container_port}: "
            f"{result.stderr}"
        )
    return result.stdout.strip()


def _get_selenium_host_port(compose_file, env):
    """Backwards-compatible alias used elsewhere in this module."""
    return _get_compose_service_host_port(compose_file, env, "selenium", 4444)


@TestStep(Given)
def wait_for_grafana(self, timeout=180):
    """Wait until Grafana health endpoint responds.

    The upstream ``grafana/grafana`` image does not ship ``curl``, so probing
    via ``docker compose exec`` is unreliable. Instead, we discover the host
    port mapped to Grafana's container port 3000 and probe it from the host.
    Falls back to a docker-exec wget probe if no host port is published.
    """
    compose_file = self.context.grafana_compose_file
    env = self.context.grafana_compose_env

    addr = ""
    try:
        addr = _get_compose_service_host_port(compose_file, env, "grafana", 3000)
    except Exception:
        addr = ""

    deadline = time.time() + timeout
    if addr:
        health_url = f"http://{addr}/api/health"
        note(f"Probing Grafana health at {health_url}")
        while time.time() < deadline:
            try:
                resp = urllib.request.urlopen(health_url, timeout=5)
                if resp.status == 200:
                    note("Grafana is healthy")
                    return
            except Exception:
                pass
            time.sleep(5)
        fail(f"Grafana did not become healthy within {timeout}s")

    note(
        "Grafana port 3000 is not published to the host; falling back to "
        "in-container wget probe"
    )
    while time.time() < deadline:
        result = subprocess.run(
            _compose_cmd(compose_file)
            + [
                "exec",
                "-T",
                "grafana",
                "wget",
                "-q",
                "-O",
                "-",
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
