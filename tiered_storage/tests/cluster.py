#!/usr/bin/env python3
#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import os
import time
import threading
import tempfile

from testflows.core import Given, By, Then, And, Finally, NullStep
from testflows.asserts import error
from testflows.connect import Shell
from testflows.connect.shell import ExpectTimeoutError

docker_compose = os.getenv("DOCKER_CO3MPOSE", "docker-compose")
current_dir = os.path.dirname(os.path.abspath(__file__))


class QueryRuntimeException(Exception):
    """Exception during query execution on the server."""

    pass


class Node(object):
    """Generic cluster node."""

    config_d_dir = "/etc/clickhouse-server/config.d/"

    def __init__(self, cluster, name):
        self.cluster = cluster
        self.name = name

    def repr(self):
        return f"Node(name='{self.name}')"

    def command(self, *args, **kwargs):
        try:
            return self.cluster.command(self.name, *args, **kwargs)
        except ExpectTimeoutError as e:
            self.cluster.delete_bash(self.name)
            raise


class ClickHouseNode(Node):
    """Node with ClickHouse server."""

    def wait_healthy(self, timeout=120):
        with By("waiting until container is healthy"):
            start_time = time.time()
            while True:
                if self.query("select 1", no_checks=1, timeout=120).exitcode == 0:
                    break
                if time.time() - start_time < timeout:
                    time.sleep(2)
                    continue
                assert False, "container is not healthy"

    def restart(self, timeout=120, safe=True):
        """Restart node."""
        if safe:
            self.query("SYSTEM STOP MOVES")
            self.query("SYSTEM STOP MERGES")
            self.query("SYSTEM FLUSH LOGS")
            with By("waiting for 5 sec for moves and merges to stop"):
                time.sleep(5)
            with And("force to sync everything to disk"):
                self.command("sync", timeout=30)

        with self.cluster.lock:
            for key in list(self.cluster._bash.keys()):
                if key.endswith(f"-{self.name}"):
                    shell = self.cluster._bash.pop(key)
                    shell.__exit__(None, None, None)

        self.cluster.command(
            None, f"{docker_compose} restart {self.name}", timeout=timeout
        )

        if safe:
            self.wait_healthy(timeout)

    def query(
        self,
        sql,
        message=None,
        exitcode=None,
        steps=True,
        max_insert_block_size=None,
        no_checks=False,
        *args,
        **kwargs,
    ):
        """Execute and check query.

        :param sql: sql query
        :param message: expected message that should be in the output, default: None
        :param exitcode: expected exitcode, default: None
        """
        if len(sql) > 1024:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8") as query:
                query.write(sql)
                query.flush()
                command = f'cat "{query.name}" | {docker_compose} exec -T {self.name} clickhouse client -n'
                if max_insert_block_size is not None:
                    command += f" --max_insert_block_size={max_insert_block_size}"
                description = f"""
                    echo -e \"{sql[:100]}...\" > {query.name}
                    {command}
                """
                with By(
                    "executing command", description=description
                ) if steps else NullStep():
                    try:
                        r = self.cluster.bash(None)(command, *args, **kwargs)
                    except ExpectTimeoutError as e:
                        self.cluster.delete_bash(None)
                        raise
        else:
            command = f'echo -e "{sql}" | clickhouse client -n'
            if max_insert_block_size is not None:
                command += f" --max_insert_block_size={max_insert_block_size}"
            with By("executing command", description=command) if steps else NullStep():
                try:
                    r = self.cluster.bash(self.name)(command, *args, **kwargs)
                except ExpectTimeoutError as e:
                    self.cluster.delete_bash(self.name)
                    raise

        if no_checks:
            return r

        if exitcode is not None:
            with Then(f"exitcode should be {exitcode}") if steps else NullStep():
                assert r.exitcode == exitcode, error(r.output)

        if message is not None:
            with Then(
                f"output should contain message", description=message
            ) if steps else NullStep():
                assert message in r.output, error(r.output)

        if message is None or "Exception:" not in message:
            if "Exception:" in r.output:
                raise QueryRuntimeException(r.output)

        return r


class Cluster(object):
    """Simple object around docker-compose cluster."""

    def __init__(
        self,
        local=False,
        clickhouse_binary_path=None,
        base_config_path=None,
        nodes=None,
        with_minio=False,
        with_s3amazon=False,
        with_s3gcs=False,
    ):
        self._bash = {}
        self.clickhouse_binary_path = clickhouse_binary_path
        self.base_config_path = base_config_path
        self.local = local
        self.nodes = nodes or {}
        self.with_minio = with_minio
        self.with_s3amazon = with_s3amazon
        self.with_s3gcs = with_s3gcs
        self.lock = threading.Lock()

    def delete_bash(self, node):
        """Close and delete tjread-locl bash terminal
        to a specific node.
        """
        current_thread = threading.current_thread()
        id = f"{current_thread.ident}-{node}"
        if self._bash.get(id) is not None:
            self._bash[id].close()
            del self._bash[id]

    def bash(self, node, timeout=60):
        """Returns thread-local bash terminal
        to a specific node.

        :param node: name of the service
        """
        current_thread = threading.current_thread()
        id = f"{current_thread.ident}-{node}"
        with self.lock:
            if self._bash.get(id) is None:
                if node is None:
                    self._bash[id] = Shell().__enter__()
                else:
                    self._bash[id] = Shell(
                        command=[
                            "/bin/bash",
                            "--noediting",
                            "-c",
                            f"docker-compose exec {node} bash --noediting",
                        ],
                        name=node,
                    ).__enter__()
                self._bash[id].timeout = timeout
            return self._bash[id]

    def __enter__(self):
        with Given("docker-compose cluster"):
            self.up()
        return self

    def __exit__(self, type, value, traceback):
        try:
            with Finally("I clean up"):
                self.down()
        finally:
            with self.lock:
                for shell in self._bash.values():
                    shell.__exit__(type, value, traceback)

    def node(self, name):
        """Get object with node bound methods.

        :param name: name of service name
        """
        if name.startswith("clickhouse"):
            return ClickHouseNode(self, name)
        return Node(self, name)

    def down(self, timeout=120):
        """Bring cluster down by executing docker-compose down."""
        try:
            bash = self.bash(None)
            with self.lock:
                # remove and close all not None node terminals
                for id in list(self._bash.keys()):
                    shell = self._bash.pop(id)
                    if shell is not bash:
                        shell.__exit__(None, None, None)
                    else:
                        self._bash[id] = shell
        finally:
            return self.command(None, f"{docker_compose} down", timeout=timeout)

    def up(self):
        with Given("I setup storage configuration"), Shell() as bash:
            configs_dir = os.path.join(current_dir, "..", "configs")
            storage_config_dst = os.path.join(configs_dir, "storage_configuration.xml")
            storage_config_src = os.path.join(
                configs_dir, "storage_configuration_original.xml"
            )

            if self.with_minio:
                storage_config_src = os.path.join(
                    configs_dir, "storage_configuration_minio.xml"
                )
            elif self.with_s3amazon:
                assert os.getenv(
                    "S3_AMAZON_KEY_ID", None
                ), "S3_AMAZON_KEY_ID env variable must be defined"
                assert os.getenv(
                    "S3_AMAZON_ACCESS_KEY", None
                ), "S3_AMAZON_ACCESS_KEY env variable must be defined"
                storage_config_src = os.path.join(
                    configs_dir, "storage_configuration_s3amazon.xml"
                )
            elif self.with_s3gcs:
                assert os.getenv(
                    "GCS_KEY_ID", None
                ), "GCS_KEY_ID env variable must be defined"
                assert os.getenv(
                    "GCS_KEY_SECRET", None
                ), "GCS_KEY_SECRET env variable must be defined"
                storage_config_src = os.path.join(
                    configs_dir, "storage_configuration_s3gcs.xml"
                )

            bash(f'ln -sf "{storage_config_src}" "{storage_config_dst}"')
            bash(f'ls -la "{configs_dir}"')

        if self.local:
            with Given("I am running in local mode"):
                with Then("check --clickhouse-binary-path is specified"):
                    assert (
                        self.clickhouse_binary_path
                    ), "when running in local mode then --clickhouse-binary-path must be specified"
                with And("path should exist"):
                    assert os.path.exists(self.clickhouse_binary_path)

            os.environ["CLICKHOUSE_TESTS_SERVER_BIN_PATH"] = self.clickhouse_binary_path
            os.environ["CLICKHOUSE_TESTS_ODBC_BRIDGE_BIN_PATH"] = os.path.join(
                os.path.dirname(self.clickhouse_binary_path), "clickhouse-odbc-bridge"
            )
            os.environ["CLICKHOUSE_TESTS_BASE_CONFIG_DIR"] = self.base_config_path

            with Given("docker-compose"):
                self.command(None, "env | grep CLICKHOUSE")
                cmd = self.command(
                    None, f"{docker_compose} up -d 2>&1 | tee", timeout=30 * 60
                )
        else:
            with Given("docker-compose"):
                cmd = self.command(
                    None, f"{docker_compose} up -d --no-recreate 2>&1 | tee"
                )

        with Then("check there are no unhealthy containers"):
            assert "is unhealthy" not in cmd.output, error()

        with Then("wait all nodes report healhy"):
            for name in self.nodes["clickhouse"]:
                self.node(name).wait_healthy()

    def command(
        self, node, command, message=None, exitcode=None, steps=True, *args, **kwargs
    ):
        """Execute and check command.

        :param node: name of the service
        :param command: command
        :param message: expected message that should be in the output, default: None
        :param exitcode: expected exitcode, default: None
        :param steps: don't break command into steps, default: True
        """
        with By("executing command", description=command) if steps else NullStep():
            r = self.bash(node)(command, *args, **kwargs)
        if exitcode is not None:
            with Then(f"exitcode should be {exitcode}") if steps else NullStep():
                assert r.exitcode == exitcode, error(r.output)
        if message is not None:
            with Then(
                f"output should contain message", description=message
            ) if steps else NullStep():
                assert message in r.output, error(r.output)
        return r
