"""Docker and Compose steps shared by the LTS sub-suites."""

import os
import shutil
import subprocess

from testflows.core import *

LTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def suite_results_dir(suite):
    """Return (and create) ``lts/_instances/<suite>``, the host directory mounted
    into a runner container as ``/results``.

    Logs go to its ``logs/`` subfolder so the CI artifact glob
    ``./*/_instances/*/logs/*.log`` collects them.
    """
    path = os.path.join(LTS_DIR, "_instances", suite)
    os.makedirs(os.path.join(path, "logs"), exist_ok=True)
    return path


def reset_suite_results_dir(suite):
    """Empty ``lts/_instances/<suite>`` so a run's evidence (logs, JUnit XML,
    screenshots) never mixes with an earlier run's. Returns the path."""
    path = os.path.join(LTS_DIR, "_instances", suite)
    shutil.rmtree(path, ignore_errors=True)
    return suite_results_dir(suite)


def screenshots_dir(suite):
    """Return (and create) ``lts/_instances/<suite>/screenshots``, where the
    browser suites save screenshots, next to their other evidence."""
    path = os.path.join(suite_results_dir(suite), "screenshots")
    os.makedirs(path, exist_ok=True)
    return path


def compose_command():
    """Return the Docker Compose command: the standalone ``docker-compose``
    that CI installs if present, as ``helpers/cluster.py`` does, otherwise
    the ``docker compose`` plugin."""
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    return ["docker", "compose"]


def tail(path, size=3000):
    """Return the last ``size`` characters of a text file."""
    if not os.path.exists(path):
        return ""
    with open(path, errors="replace") as f:
        return f.read()[-size:]


@TestStep(Given)
def pull_image(self, image, timeout=1800):
    """Pull a Docker image so that pull time and pull errors are not attributed
    to the tests that use it."""
    note(f"Pulling {image}")
    result = subprocess.run(
        ["docker", "pull", image], capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0:
        local = subprocess.run(
            ["docker", "image", "inspect", image], capture_output=True
        )
        if local.returncode != 0:
            fail(f"docker pull {image} failed:\n{result.stderr[-2000:]}")
        note(f"docker pull {image} failed, using the local image")


@TestStep(Given)
def build_runner_image(self, context_dir, tag, build_args=None, log_path=None):
    """Build a runner image from ``context_dir``.

    The build output is written to ``log_path`` when given, and its tail is
    shown if the build fails.
    """
    cmd = ["docker", "build", "-t", tag]
    for key, value in (build_args or {}).items():
        cmd += ["--build-arg", f"{key}={value}"]
    cmd.append(".")

    note(f"Running: {' '.join(cmd)}")
    with open(log_path or os.devnull, "w") as log:
        result = subprocess.run(
            cmd, cwd=context_dir, stdout=log, stderr=subprocess.STDOUT
        )
    if result.returncode != 0:
        fail(
            f"docker build of {tag} failed with exit code {result.returncode}\n"
            f"{tail(log_path) if log_path else ''}"
        )


@TestStep(When)
def run_container(
    self,
    image,
    name,
    log_path,
    env=None,
    mounts=None,
    docker_args=None,
    timeout=None,
):
    """Run a runner container to completion and return its exit code.

    The container's combined output is written to ``log_path``. A non-zero exit
    code is returned, not treated as a failure, because a test
    runner exits non-zero whenever any test fails; the caller decides from the
    test results. The container is always force-removed afterwards, including
    on timeout, since killing ``docker run`` does not stop the container.
    """
    cmd = ["docker", "run", "--name", name]
    env = dict(env or {})
    env.setdefault("HOST_UID", str(os.getuid()))
    env.setdefault("HOST_GID", str(os.getgid()))
    for key, value in env.items():
        cmd += ["-e", f"{key}={value}"]
    for host_path, container_path in (mounts or {}).items():
        cmd += ["-v", f"{host_path}:{container_path}"]
    cmd += list(docker_args or [])
    cmd.append(image)

    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    note(f"Running: {' '.join(cmd)}")
    note(f"Output: {log_path}")
    try:
        with open(log_path, "w") as log:
            result = subprocess.run(
                cmd, stdout=log, stderr=subprocess.STDOUT, timeout=timeout
            )
    except subprocess.TimeoutExpired:
        fail(f"{name} did not finish within {timeout}s\n{tail(log_path)}")
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)

    note(f"{name} exited with code {result.returncode}")
    return result.returncode


def _run_quietly(cmd, env, stdout, timeout):
    """Run ``cmd`` for teardown or diagnostics: output to a file, no stdin,
    bounded by ``timeout``. Never raises, so teardown always continues."""
    try:
        subprocess.run(
            cmd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        note(f"timed out after {timeout}s: {' '.join(cmd)}")


def save_compose_logs(compose_cmd, env, logs_dir, timeout=120):
    """Write each Compose service's logs, and the service status, to
    ``logs_dir``. Call before ``down -v``, which removes the containers and
    their logs. Never fails, so that teardown still runs.
    """
    os.makedirs(logs_dir, exist_ok=True)
    services_log = os.path.join(logs_dir, "compose-services.txt")
    with open(services_log, "w") as f:
        _run_quietly(compose_cmd + ["ps", "--all", "--services"], env, f, timeout)
    with open(services_log) as f:
        services = f.read().split()
    os.remove(services_log)
    with open(os.path.join(logs_dir, "compose-ps.log"), "w") as f:
        _run_quietly(compose_cmd + ["ps", "--all"], env, f, timeout)
    for service in services:
        with open(os.path.join(logs_dir, f"{service}.log"), "w") as f:
            _run_quietly(
                compose_cmd + ["logs", "--no-color", "--timestamps", service],
                env,
                f,
                timeout,
            )
    note(f"saved logs of {services} to {logs_dir}")


def compose_down(compose_cmd, env, logs_dir, timeout=300):
    """Remove a Compose project with its volumes. The output goes to
    ``logs_dir/compose-down.log`` rather than a pipe, and the call is bounded
    by ``timeout``, so a stuck or detached process cannot hang teardown."""
    os.makedirs(logs_dir, exist_ok=True)
    with open(os.path.join(logs_dir, "compose-down.log"), "w") as f:
        _run_quietly(compose_cmd + ["down", "--remove-orphans", "-v"], env, f, timeout)
