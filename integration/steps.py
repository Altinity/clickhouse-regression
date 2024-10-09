"""TestFlows framework steps and utility functions for the regression.py"""

import os
import time
import uuid
import json
import zlib
import shlex
import tempfile
import hashlib
import subprocess
import testflows.settings

from contextlib import contextmanager
from testflows.core import *
from testflows.connect import Shell
from testflows._core.cli.arg.type import count


def next_group_timeout(group_timeout, timeout):
    """Return next group timeout."""
    if timeout is not None:
        if group_timeout is not None:
            return int(max(min(group_timeout, timeout - current_time()), 0))
        else:
            return int(timeout - current_time())
    return group_timeout


def readline(file):
    """Read full line from a file taking into account
    that if the file is updated concurrently the line
    may not be complete yet."""
    while True:
        pos = file.tell()
        line = file.readline()

        if line:
            if not line.endswith("\n"):
                log.seek(pos)
                time.sleep(1)
                continue
        break
    return line


@contextmanager
def catch(exceptions, raising):
    """Catch exception and raise it as another one."""
    try:
        yield
    except exceptions as e:
        raise raising from e


def getuid(self):
    """Return unique id."""
    return str(uuid.uuid1()).replace("-", "_")


def short_hash(s):
    """Return good enough short hash of a string."""
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


@TestStep(Given)
def temporary_file(self, mode, dir=None, prefix=None, suffix=None):
    """Create temporary named file."""
    with tempfile.NamedTemporaryFile(
        mode,
        dir=dir,
        prefix=prefix,
        suffix=suffix,
        delete=(not testflows.settings.debug),
    ) as log:
        yield log


@TestStep(Given)
def sysprocess(self, command, name=None):
    """Run system command."""

    log = temporary_file(
        mode="w", dir=current_dir(), prefix="sysprocess-", suffix=".log"
    )

    proc = subprocess.Popen(
        command,
        stdout=log,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        shell=True,
    )
    proc.stdout = open(log.name, "r")
    try:
        yield proc

    finally:
        if proc.poll() is None:
            proc.kill()

        while proc.poll() is None:
            debug(f"waiting for {proc.pid} to exit running {command}")
            time.sleep(1)

        with Finally(f"stdout for {command}"):
            proc.stdout.flush()
            for line in proc.stdout.readlines():
                if not line:
                    break
                message(line, stream=name)


@TestStep(Given)
def syscommand(self, command, timeout=None, name=None, exitcode=0):
    """Execute command."""
    proc = sysprocess(command=command)

    while proc.poll() is None:
        with timer(timeout, f"command '{command}' took too long"):
            if self.terminating:
                break
            line = proc.stdout.readline()
            if line:
                message(f"{line}", stream=name)
        time.sleep(1)

    assert (
        proc.returncode == exitcode
    ), f"command {command} failed with unexpected exitcode {proc.returncode}"


@TestStep
def get_clickhouse_binary_from_docker_container(
    self,
    docker_image,
    container_binary="/usr/bin/clickhouse",
    container_odbc_bridge_binary="/usr/bin/clickhouse-odbc-bridge",
    container_library_bridge_binary="/usr/bin/clickhouse-library-bridge",
    host_binary=None,
    host_odbc_bridge_binary=None,
    host_library_bridge_binary=None,
):
    """Get clickhouse binaries from some ClickHouse docker container."""
    docker_image = docker_image.split("docker://", 1)[-1]
    docker_container_name = str(uuid.uuid1())

    if host_binary is None:
        host_binary = os.path.join(
            tempfile.gettempdir(),
            f"{docker_image.rsplit('/', 1)[-1].replace(':', '_')}",
        )

    if host_odbc_bridge_binary is None:
        host_odbc_bridge_binary = host_binary + "_odbc_bridge"

    if host_library_bridge_binary is None:
        host_library_bridge_binary = host_binary + "_library_bridge"

    with Given(
        "I get ClickHouse server binary from docker container",
        description=f"{docker_image}",
    ):
        with Shell() as bash:
            bash.timeout = 300
            bash(
                f'set -o pipefail && docker run -d --name "{docker_container_name}" {docker_image} | tee'
            )
            bash(
                f'docker cp "{docker_container_name}:{container_binary}" "{host_binary}"'
            )
            bash(
                f'docker cp "{docker_container_name}:{container_odbc_bridge_binary}" "{host_odbc_bridge_binary}"'
            )
            bash(
                f'docker cp "{docker_container_name}:{container_library_bridge_binary}" "{host_library_bridge_binary}"'
            )
            bash(f'docker stop "{docker_container_name}"')

    with And("debug"):
        with Shell() as bash:
            bash(f"ls -la {host_binary}", timeout=300)
            bash(f"ls -la {host_odbc_bridge_binary}", timeout=300)
            bash(f"ls -la {host_library_bridge_binary}", timeout=300)

    return host_binary, host_odbc_bridge_binary, host_library_bridge_binary


@TestStep(Given)
def download_clickhouse_binary(self, path):
    """I download ClickHouse server binary using wget"""
    filename = f"{short_hash(path)}-{path.rsplit('/', 1)[-1]}"

    if not os.path.exists(f"./{filename}"):
        with Shell() as bash:
            bash.timeout = 300
            try:
                cmd = bash(f'wget --progress dot "{path}" -O {filename}')
                assert cmd.exitcode == 0
            except BaseException:
                if os.path.exists(filename):
                    os.remove(filename)
                raise

    return f"./{filename}"


@TestStep(Given)
def get_clickhouse_binary_from_deb(self, path):
    """Get clickhouse binary from deb package."""

    deb_binary_dir = path.rsplit(".deb", 1)[0]
    os.makedirs(deb_binary_dir, exist_ok=True)

    with Shell() as bash:
        bash.timeout = 300
        if not os.path.exists(f"{deb_binary_dir}/clickhouse") or not os.path.exists(
            f"{deb_binary_dir}/clickhouse-odbc-bridge"
        ):
            bash(f'ar x "{clickhouse_path}" --output "{deb_binary_dir}"')
            bash(
                f'tar -vxzf "{deb_binary_dir}/data.tar.gz" ./usr/bin/clickhouse -O > "{deb_binary_dir}/clickhouse"'
            )
            bash(f'chmod +x "{deb_binary_dir}/clickhouse"')
            bash(
                f'tar -vxzf "{deb_binary_dir}/data.tar.gz" ./usr/bin/clickhouse-odbc-bridge -O > "{deb_binary_dir}/clickhouse-odbc-bridge"'
            )
            bash(f'chmod +x "{deb_binary_dir}/clickhouse-odbc-bridge"')
            bash(
                f'tar -vxzf "{deb_binary_dir}/data.tar.gz" ./usr/bin/clickhouse-library-bridge -O > "{deb_binary_dir}/clickhouse-library-bridge"'
            )
            bash(f'chmod +x "{deb_binary_dir}/clickhouse-library-bridge"')

    return (
        f"./{deb_binary_dir}/clickhouse",
        f"{deb_binary_dir}/clickhouse-odbc-bridge",
        f"{deb_binary_dir}/clickhouse-library-bridge",
    )


@TestStep(Given)
def clickhouse_binaries(self, path, odbc_bridge_path=None, library_bridge_path=None):
    """Extract clickhouse, clickhouse-odbc-bridge, clickhouse-library-bridge
    binaries from --clickhouse_path."""

    if path.startswith(("http://", "https://")):
        path = download_clickhouse_binary(clickhouse_path=path)

    elif path.startswith("docker://"):
        (
            path,
            odbc_bridge_path,
            library_bridge_path,
        ) = get_clickhouse_binary_from_docker_container(docker_image=path)

    if path.endswith(".deb"):
        path, odbc_bridge_path, library_bridge_path = get_clickhouse_binary_from_deb(
            path=path
        )

    if odbc_bridge_path is None:
        odbc_bridge_path = path + "-odbc-bridge"

    if library_bridge_path is None:
        library_bridge_path = path + "-library-bridge"

    path = os.path.abspath(path)
    odbc_bridge_path = os.path.abspath(odbc_bridge_path)
    library_bridge_path = os.path.abspath(library_bridge_path)

    with Shell() as bash:
        bash(f"chmod +x {path}", timeout=300)
        bash(f"chmod +x {odbc_bridge_path}", timeout=300)
        bash(f"chmod +x {library_bridge_path}", timeout=300)

    return path, odbc_bridge_path, library_bridge_path


@TestScenario
def build_image(self, path, name, dependent, tag="latest", timeout=None):
    """Build single image in specified path and with the specified name
    and tag taking account any dependent images that must be build first.
    """
    with By(f"waiting for dependent images to be ready"):
        for d in dependent:
            with By(f"waiting for {d} to be ready"):
                while d not in self.context.ready:
                    if self.terminating:
                        return
                    with timer(timeout, f"waiting for depended {d} image to be ready"):
                        time.sleep(1)

    command = f"cd {path}; docker build -t {name}:{tag} ."

    with And("launching build command"):
        proc = sysprocess(command=command)

    while proc.poll() is None:
        with timer(timeout, f"building image took too long"):
            if self.terminating:
                return
            line = proc.stdout.readline()
            if line:
                message(f"{line}", stream=name)
            time.sleep(1)

    assert (
        proc.returncode == 0
    ), f"failed to build {name} at {path}; exitcode {proc.returncode}"

    self.context.ready.append(path)


@TestFeature
def build_images(self, root_dir, image_tag="latest", timeout=None):
    """Build all images."""
    self.context.ready = []

    with Given("I load images.json definitions"):
        with open(os.path.join(root_dir, "docker", "images.json")) as images_json:
            images_json = json.load(images_json)

    with And("I create images dictionary"):
        images = {}
        for path in images_json:
            image = images_json[path]
            image["tag"] = image_tag

            filter_path = "docker/test/integration"

            if not path.startswith(filter_path) and not [
                d for d in image["dependent"] if d.startswith(filter_path)
            ]:
                # filter out all non test related images
                continue

            dependents = []
            for dependent in image["dependent"]:
                dependents.append(os.path.join(root_dir, dependent))

            # use the original runner image as the base
            if image["name"] == "clickhouse/integration-tests-runner":
                image["tag"] = f"{image['tag']}.base"
                dependents.append(os.path.join(current_dir(), "docker", "runner"))

            images[os.path.join(root_dir, path)] = {
                "name": image["name"],
                "dependent": dependents,
                "tag": image["tag"],
            }

        # add customized testflows wrapper compatible runner image
        images[os.path.join(current_dir(), "docker", "runner")] = {
            "name": "clickhouse/integration-tests-runner",
            "tag": image_tag,
            "dependent": [],
        }

        debug(json.dumps(images, indent=2))

    with And("I build a dictionary of image dependencies"):
        dependents = {}

        for path in images:
            if path not in dependents:
                dependents[path] = []
            for _path, _image in images.items():
                dependent = _image["dependent"]
                if path in dependent:
                    dependents[path].append(_path)

        debug(json.dumps(dependents, indent=2))

    with Pool() as executor:
        for path, image in images.items():
            name = image["name"]
            tag = image["tag"]
            dependent = dependents[path]
            Scenario(
                name=f"build {name}:{tag}",
                description=f"depends on {dependent}",
                test=build_image,
                executor=executor,
                parallel=True,
            )(path=path, name=name, dependent=dependent, tag=tag, timeout=timeout)

        join()

    return images


@TestScenario
def save_images(self, images, path, dir=None):
    """Save images to tar file."""

    with By(f"saving all images to file"):
        if not os.path.isabs(path):
            path = os.path.join(dir or current_dir(), path)
        command = define(
            "command",
            f"docker save -o {shlex.quote(path)} "
            + " ".join(
                [
                    shlex.quote(f"{image['name']}:{image['tag']}")
                    for image in images.values()
                ]
            ),
        )
        syscommand(command=command)
