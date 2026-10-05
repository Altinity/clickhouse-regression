"""Start and stop the DBeaver desktop container."""

import os
import subprocess
import time

from testflows.core import *

from lts.steps.docker import build_runner_image, suite_results_dir

SUITE = "dbeaver_ui"
CONFIGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs")
# Unique per run, so that two runs on one Docker host do not share a container.
CONTAINER = f"lts-dbeaver-ui-{os.getpid()}"
IMAGE = "lts-dbeaver-ui"


def docker_exec(*args, timeout=120, check=True):
    """Run a command in the desktop container with the display and accessibility
    bus environment from ``/tmp/desktop.env``, and return its stdout."""
    script = 'source /tmp/desktop.env && exec "$@"'
    result = subprocess.run(
        ["docker", "exec", CONTAINER, "bash", "-c", script, "_", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if check and result.returncode != 0:
        fail(f"{' '.join(args)} failed with exit code {result.returncode}:\n{result.stderr[-2000:]}")
    return result.stdout


@TestStep(Given)
def desktop_container(self, clickhouse_image, dbeaver_version):
    """Build the image, start ClickHouse and a virtual display in a container,
    and remove the container on exit, after saving DBeaver's logs."""
    results_dir = suite_results_dir(SUITE)
    logs_dir = os.path.join(results_dir, "logs")

    build_runner_image(
        context_dir=CONFIGS_DIR,
        tag=IMAGE,
        build_args={"CLICKHOUSE_IMAGE": clickhouse_image, "DBEAVER_VERSION": dbeaver_version},
        log_path=os.path.join(logs_dir, "build.log"),
    )

    subprocess.run(["docker", "rm", "-f", CONTAINER], capture_output=True)
    result = subprocess.run(
        ["docker", "run", "-d", "--name", CONTAINER, "--shm-size", "1g",
         "-v", f"{results_dir}:/results", IMAGE],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        fail(f"docker run {IMAGE} failed:\n{result.stderr}")
    note(f"container {CONTAINER}")

    try:
        for _ in range(180):
            if subprocess.run(["docker", "exec", CONTAINER, "test", "-f", "/tmp/ready"]).returncode == 0:
                break
            time.sleep(1)
        else:
            fail(f"the desktop did not start within 180s:\n{_container_log()}")
        yield
    finally:
        with By("saving DBeaver's logs and removing the container"):
            docker_exec(
                "bash", "-c",
                "cp /tmp/dbeaver.log /results/logs/dbeaver.log; "
                "cp /root/workspace/.metadata/dbeaver-debug.log /results/logs/dbeaver-debug.log; "
                f"chown -R {os.getuid()}:{os.getgid()} /results",
                check=False,
            )
            with open(os.path.join(logs_dir, "container.log"), "w") as log:
                log.write(_container_log(size=None))
            subprocess.run(["docker", "rm", "-f", CONTAINER], capture_output=True)


def _container_log(size=3000):
    result = subprocess.run(["docker", "logs", CONTAINER], capture_output=True, text=True)
    output = result.stdout + result.stderr
    return output if size is None else output[-size:]


@TestStep(Given)
def dbeaver_running(self):
    """Start DBeaver with a new workspace, so every run starts from DBeaver's
    first-run state."""
    docker_exec(
        "bash", "-c",
        "nohup /opt/dbeaver/dbeaver -data /root/workspace > /tmp/dbeaver.log 2>&1 &",
    )


def clickhouse_query(sql):
    """Run ``sql`` with clickhouse-client in the container and return its output
    without the trailing newline."""
    return docker_exec("clickhouse-client", "-q", sql).rstrip("\n")


def logs_tail():
    """Return the end of DBeaver's log, for failure messages."""
    return docker_exec("bash", "-c", "tail -c 3000 /tmp/dbeaver.log", check=False)
