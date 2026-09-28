"""Reusable steps for setting up and tearing down the Superset + ClickHouse environment."""

import os
import subprocess
import time
import urllib.request

from testflows.core import *

from lts.steps.docker import compose_down, save_compose_logs, suite_results_dir

# Unique per run, so that two runs on one Docker host neither share nor tear
# down each other's containers, networks and volumes.
PROJECT_NAME = f"superset-lts-{os.getpid()}"


def _compose_cmd(compose_file):
    """Return the base docker compose command list with the LTS project name."""
    return ["docker", "compose", "-f", compose_file, "-p", PROJECT_NAME]


def _get_compose_service_host_port(compose_file, env, service, container_port):
    """Discover the ephemeral host port that compose published for a service."""
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
    addr = result.stdout.strip()
    if not addr:
        fail(
            f"docker compose port returned empty output for "
            f"{service}:{container_port}"
        )
    return addr


@TestStep(Given)
def superset_environment(
    self,
    configs_dir,
    clickhouse_image,
    superset_version="4.1.1",
    clickhouse_driver="clickhouse-connect",
    selenium_version="4.40.0",
):
    """Build and start the self-contained Superset + ClickHouse + Selenium stack.

    Yields after compose is up; tears down on exit (regardless of test outcome).
    Stores the compose file path and env on ``self.context`` for downstream
    steps to reuse.
    """
    compose_file = os.path.join(configs_dir, "docker-compose.yml")

    env = os.environ.copy()
    # The full reference, so registry ports and digests survive.
    env["CLICKHOUSE_IMAGE"] = clickhouse_image
    env["SUPERSET_VERSION"] = superset_version
    env["CLICKHOUSE_PYTHON_DRIVER"] = clickhouse_driver
    env["SELENIUM_VERSION"] = selenium_version

    self.context.superset_compose_file = compose_file
    self.context.superset_compose_env = env

    note(
        f"Starting environment: ClickHouse={clickhouse_image}, "
        f"Superset={superset_version}, driver={clickhouse_driver}"
    )

    try:
        build = subprocess.run(
            _compose_cmd(compose_file) + ["build", "superset"],
            cwd=configs_dir,
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=1800,
        )
    except subprocess.TimeoutExpired:
        fail("docker compose build superset did not finish within 30 minutes")
    if build.returncode != 0:
        note(f"stdout: {build.stdout}")
        note(f"stderr: {build.stderr}")
        fail(f"docker compose build failed with exit code {build.returncode}")

    try:
        up = subprocess.run(
            _compose_cmd(compose_file) + ["up", "-d"],
            cwd=configs_dir,
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=1800,
        )
    except subprocess.TimeoutExpired:
        fail("docker compose up -d did not finish within 30 minutes")
    if up.returncode != 0:
        note(f"stdout: {up.stdout}")
        note(f"stderr: {up.stderr}")
        fail(f"docker compose up failed with exit code {up.returncode}")

    try:
        yield
    finally:
        note("Tearing down Superset environment")
        logs_dir = os.path.join(suite_results_dir("superset"), "logs")
        save_compose_logs(_compose_cmd(compose_file), env, logs_dir)
        compose_down(_compose_cmd(compose_file), env, logs_dir)


@TestStep(Given)
def wait_for_superset(self, timeout=300):
    """Wait until Superset's /health endpoint returns 200 on its host port.

    Stores ``self.context.superset_url`` (e.g. ``http://127.0.0.1:54321``)
    so downstream UI/API steps can reach Superset from the host.
    """
    compose_file = self.context.superset_compose_file
    env = self.context.superset_compose_env

    addr = _get_compose_service_host_port(compose_file, env, "superset", 8088)
    superset_url = f"http://{addr}"
    health_url = f"{superset_url}/health"

    note(f"Probing Superset health at {health_url}")

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = urllib.request.urlopen(health_url, timeout=5)
            if resp.status == 200:
                note(f"Superset is healthy at {superset_url}")
                self.context.superset_url = superset_url
                self.context.superset_internal_url = "http://superset:8088"
                return
        except Exception:
            pass
        time.sleep(5)
    fail(f"Superset did not become healthy within {timeout}s")


@TestStep(Given)
def wait_for_selenium(self, timeout=120):
    """Wait until Selenium Grid is ready and store its URL on the context."""
    compose_file = self.context.superset_compose_file
    env = self.context.superset_compose_env

    addr = _get_compose_service_host_port(compose_file, env, "selenium", 4444)
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
