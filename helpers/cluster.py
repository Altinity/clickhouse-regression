import os
import uuid
import time
import inspect
import hashlib
import threading
import tempfile
import re
import json
import shutil
from contextlib import contextmanager
from urllib.parse import unquote

from testflows._core.cli.arg.common import description

import testflows.settings as settings

from testflows.core import *
from testflows.asserts import error
from testflows.connect import Shell as ShellBase
from testflows.uexpect import ExpectTimeoutError
from testflows._core.testtype import TestSubType
from helpers.common import check_clickhouse_version, current_cpu

MINIMUM_COMPOSE_VERSION = "2.23.1"

NONE = object()

MESSAGES_TO_RETRY = [
    "DB::Exception: ZooKeeper session has been expired",
    "DB::Exception: Connection loss",
    "DB::Exception: Table is in readonly mode",
    "Coordination::Exception: Session expired",
    "Coordination::Exception: Connection loss",
    "Coordination::Exception: Coordination error: Connection loss.",
    "Coordination::Exception: Operation timeout",
    "DB::Exception: Operation timeout",
    "Coordination::Exception: Coordination error: Operation timeout",
    "Operation timed out",
    "ConnectionPoolWithFailover: Connection failed at try",
    "DB::Exception: New table appeared in database being dropped or detached. Try again",
    "is already started to be removing by another replica right now",
    "Shutdown is called for table",
    # happens in SYSTEM SYNC REPLICA query if session with ZooKeeper is being reinitialized.
    "is executing longer than distributed_ddl_task_timeout",  # distributed TTL timeout message
    "You can retry this error.",  # happens with too many pending alters
]


def short_hash(s):
    """Return good enough short hash of a string."""
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:10]


def download_http_binary(binary_source):
    """Download binary from http source and return path to the downloaded file."""
    file_name = f"{binary_source.rsplit('/', 1)[-1]}"
    file_dir = f"{current_dir()}/../binaries/{short_hash(binary_source)}/"
    os.makedirs(file_dir, exist_ok=True)
    file_path = file_dir + file_name

    for retry in retries(count=10, delay=10):
        with retry:
            if not os.path.exists(file_path):
                with Shell() as bash:
                    bash.timeout = 300
                    try:
                        if current_cpu() == "arm":
                            note(f'curl -L --progress-bar "{binary_source}" -o {file_path}')
                            cmd = bash(f'curl -L --progress-bar "{binary_source}" -o {file_path}')
                        else:
                            note(f'wget --progress dot:giga "{binary_source}" -O {file_path}')
                            cmd = bash(f'wget --progress dot:giga "{binary_source}" -O {file_path}')
                        assert cmd.exitcode == 0
                    except BaseException:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        raise

    return file_path


def filter_version(version):
    """Filter version from string."""
    return "".join([c for c in version.strip(".") if c in ".0123456789"])


def parse_version_from_docker_path(docker_path):
    """Parse version from docker path."""
    return filter_version(docker_path.rsplit(":", 1)[-1])


def unpack_deb(deb_binary_path, program_name):
    """Unpack deb binary and return path to the binary."""
    assert deb_binary_path.endswith(".deb"), error("not a .deb file")
    deb_binary_dir = deb_binary_path.rsplit(".deb", 1)[0]
    os.makedirs(deb_binary_dir, exist_ok=True)
    with Shell() as bash:
        bash.timeout = 300
        if not os.path.exists(f"{deb_binary_dir}/{program_name}"):
            if current_cpu() == "arm":
                deb_abs_path = os.path.abspath(deb_binary_path)
                deb_binary_dir_abs = os.path.abspath(deb_binary_dir)
                # BSD ar extracts to current directory, so extract and move data.tar.gz
                cmd = bash(f'ar x "{deb_abs_path}" && mv data.tar.gz "{deb_binary_dir_abs}/"')
            else:
                cmd = bash(f'ar x "{deb_binary_path}" --output "{deb_binary_dir}"')
            assert cmd.exitcode == 0, error()
            if current_cpu() == "arm":
                # BSD tar: -O must come right after -x, before -f
                cmd = bash(
                    f'tar -vxOz -f "{deb_binary_dir}/data.tar.gz" "./usr/bin/{program_name}" > "{deb_binary_dir}/{program_name}"'
                )
            else:
                cmd = bash(
                    f'tar -vxzf "{deb_binary_dir}/data.tar.gz" "./usr/bin/{program_name}" -O > "{deb_binary_dir}/{program_name}"'
                )
            assert cmd.exitcode == 0, error()
            cmd = bash(f'chmod +x "{deb_binary_dir}/{program_name}"')
            assert cmd.exitcode == 0, error()

    return f"{deb_binary_dir}/{program_name}"


def unpack_tgz(tar_path):
    """Unpack tgz file and return path to the result."""
    assert tar_path.endswith(".tgz"), error("not a .tgz file")
    tar_dest_dir = tar_path.rsplit(".tgz", 1)[0]
    os.makedirs(tar_dest_dir, exist_ok=True)
    with Shell() as bash:
        bash.timeout = 300
        cmd = bash(f'tar -xzf "{tar_path}" -C "{tar_dest_dir}" --strip-components=1')
        assert cmd.exitcode == 0, error()
        cmd = bash(f"chmod +x {tar_dest_dir}/usr/bin/*")
        assert cmd.exitcode == 0, error()

    return tar_dest_dir


def get_binary_from_docker_container(
    docker_image,
    container_binary_path="/usr/bin/clickhouse",
    host_binary_path=None,
):
    """
    Get clickhouse-keeper binary from some Docker container.

    Args:
        docker_image: docker image name
        container_binary_path: path to the binary in the container
        host_binary_path: path to store the binary on the host
    """
    assert docker_image.startswith("docker://"), error("not a docker image path")
    docker_image = docker_image.split("docker://", 1)[-1]
    docker_container_name = str(uuid.uuid1())
    binary_name = container_binary_path.rsplit("/", 1)[-1]

    if host_binary_path is None:
        host_binary_path = os.path.join(
            f"{current_dir()}/../binaries",
            f"docker-{docker_image.rsplit('/', 1)[-1].replace(':', '_')}",
        )

    with By(
        "I return host_binary_path if it already exists and version patch is specified",
        description=host_binary_path,
    ):
        if os.path.exists(host_binary_path):
            version = docker_image.split(":")[-1]
            version_components = version.split(".")
            if len(version_components) >= 3:
                return host_binary_path

    with And("copying binary from docker container", description=docker_image):
        with Shell() as bash:
            bash.timeout = 300
            bash(f"mkdir -p {host_binary_path}")
            bash(f'set -o pipefail && docker run -d --name "{docker_container_name}" {docker_image} | tee')
            bash(f'docker cp "{docker_container_name}:{container_binary_path}" "{host_binary_path}/{binary_name}"')
            bash(f'docker stop "{docker_container_name}"')

    with And("debug"):
        with Shell() as bash:
            bash.timeout = 300
            bash(f"ls -la {host_binary_path}")

    return f"{host_binary_path}/{binary_name}"


def sanitize_docker_tag(tag):
    """Replace all characters that are invalid in a docker tag with underscores."""
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", unquote(tag))


class Shell(ShellBase):
    def __exit__(self, type, value, traceback):
        # send exit and Ctrl-D repeatedly
        # to terminate any open shell commands.
        # This is needed for example
        # to solve a problem with
        # 'docker-compose exec {name} bash --noediting'
        # that does not clean up open bash processes
        # if not exited normally
        for i in range(10):
            if self.child is not None:
                try:
                    self.send("exit\r", eol="")
                    self.send("\x04\r", eol="")
                except OSError:
                    pass
        return super(Shell, self).__exit__(type, value, traceback)


class QueryRuntimeException(Exception):
    """Exception during query execution on the server."""

    pass


class ClientQueryResult:
    def __init__(self, output, errorcode=0):
        self.raw_output = output
        self.errorcode = errorcode
        self._output = None

    @property
    def output(self):
        """Return parsed query output."""
        if self._output is None:
            try:
                if self.raw_output:
                    self._output = [json.loads(line) for line in self.raw_output.splitlines()]
            except json.JSONDecodeError:
                self._output = self.raw_output
        return self._output

    def __repr__(self):
        lines = self.raw_output.strip().splitlines()
        first_line = lines[0]
        if len(first_line) > 30 or len(lines) > 1:
            first_line = first_line[:30] + "..."
        return f"{self.__class__.__name__}(output={first_line})"


class Node(object):
    """Generic cluster node."""

    config_d_dir = "/etc/clickhouse-server/config.d/"

    def __init__(self, cluster, name):
        self.cluster = cluster
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __str__(self):
        return self.__repr__()

    def close_bashes(self):
        """Close all active bashes to the node."""
        with self.cluster.lock:
            for key in list(self.cluster._bash.keys()):
                if key[1].endswith(f"{self.name}"):
                    shell = self.cluster._bash.pop(key)
                    shell.__exit__(None, None, None)

    def wait_healthy(self, timeout=300):
        with By(f"waiting until container {self.name} is healthy"):
            for attempt in retries(timeout=timeout, delay=1):
                with attempt:
                    if self.command("echo 1", no_checks=1, steps=False).exitcode != 0:
                        fail("container is not healthy")

    def restart(self, timeout=300, retry_count=5, safe=True):
        """Restart node."""
        self.close_bashes()
        retry(self.cluster.command, retry_count)(
            None,
            f"{self.cluster.docker_compose} restart {self.name}",
            timeout=timeout,
            exitcode=0,
            steps=False,
        )

    def start(self, timeout=300, retry_count=5):
        """Start node."""
        retry(self.cluster.command, retry_count)(
            None,
            f"{self.cluster.docker_compose} start {self.name}",
            timeout=timeout,
            exitcode=0,
            steps=False,
        )

    def stop(self, timeout=300, retry_count=5, safe=True):
        """Stop node."""
        self.close_bashes()

        retry(self.cluster.command, retry_count)(
            None,
            f"{self.cluster.docker_compose} stop {self.name}",
            timeout=timeout,
            exitcode=0,
            steps=False,
        )

    def command(self, *args, **kwargs):
        return self.cluster.command(self.name, *args, **kwargs)

    class ClientQueryHandler:
        """Query handler for the clickhouse-client-tty."""

        def __init__(self, command_context, prompt=r"⇒ ", output_prompt="⇐ "):
            self.command_context = command_context
            self.prompt = prompt
            self.output_prompt = output_prompt

        def __enter__(self):
            self.command_context.__enter__()
            self.command_context.app.expect(self.prompt)
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.command_context:
                self.command_context.app.send("exit")
                self.command_context.__exit__(exc_type, exc_val, exc_tb)

        @staticmethod
        def _parse_error_code(message):
            if "🔥 Exception:" not in message:
                return 0
            match = re.search(r"Code:\s*(\d+)", message)

            return int(match.group(1))

        @staticmethod
        def _remove_stack_trace(log: str) -> str:
            """Find the index of "Stack trace" and slice the string up to that point."""
            stack_trace_index = log.find("Stack trace")
            return log[:stack_trace_index].strip() if stack_trace_index != -1 else log.strip()

        def query(
            self,
            query_string,
            match=None,
            errorcode=None,
            no_checks=False,
            message=None,
            ignore_exception=False,
            raise_on_exception=False,
            settings=None,
            messages_to_retry=None,
            retry_count=5,
            retry_delay=5,
            stack_trace=True,
        ):
            """Execute query and return the result.
            :param query_string: query to execute.
            :param match: expect a specific match in the output
            :param errorcode: assert that a specific error code is in the output.
            :param message: assert that a specific message is in the output.
            :param ignore_exception: ignore exception.
            :param raise_on_exception: raise a QueryRuntimeException with the query message.
            :param settings: query settings, a list of tuple where in the tuple the first value is a setting and the second is a value.
            :param messages_to_retry: list of messages that should trigger a retry.
            :param retry_count: number of retries.
            :param retry_delay: delay between retries.
            """

            retry_count = max(0, int(retry_count))
            retry_delay = max(0, float(retry_delay))

            if messages_to_retry is None:
                messages_to_retry = MESSAGES_TO_RETRY

            if settings is not None:
                query_string += " SETTINGS "
                for key, value in settings:
                    query_string += f"{key} = {value}, "

                query_string = query_string.rstrip(", ")

            self.command_context.app.send(query_string)
            self.command_context.app.expect(self.output_prompt, escape=True)

            if match is not None:
                self.command_context.app.expect(match, escape=True)

            self.command_context.app.expect(self.prompt, escape=True)

            query_result = self.command_context.app.child.before

            if retry_count and retry_count > 0:
                if any(msg in query_result for msg in messages_to_retry):
                    time.sleep(retry_delay)
                    return self.query(
                        query_string=query_string,
                        match=match,
                        errorcode=errorcode,
                        no_checks=no_checks,
                        message=message,
                        ignore_exception=ignore_exception,
                        raise_on_exception=raise_on_exception,
                        settings=settings,
                        messages_to_retry=messages_to_retry,
                        retry_count=retry_count - 1,
                        retry_delay=retry_delay,
                    )

            _output = query_result.split(self.prompt, 1)[-1]
            _errorcode = self._parse_error_code(query_result)

            if no_checks:
                if "🔥 Exception:" in _output and not stack_trace:
                    _output = self._remove_stack_trace(_output)
                return ClientQueryResult(_output, errorcode=_errorcode)

            if errorcode is not None:
                with Then(f"errorcode should be {errorcode}", format_name=False):
                    assert errorcode == _errorcode, error()

            if message is not None:
                with Then(f"message should be {message}", format_name=False):
                    assert message in _output, error()

            if not ignore_exception:
                if message is None or "Exception:" not in message:
                    if not stack_trace:
                        _output = self._remove_stack_trace(_output)
                    if "🔥 Exception:" in _output:
                        if raise_on_exception:
                            raise QueryRuntimeException(_output)
                        assert False, error(_output)

            return ClientQueryResult(_output, errorcode=_errorcode)

    @contextmanager
    def client(
        self,
        client="clickhouse-client-tty",
        client_args=None,
        name="clickhouse-client-tty",
    ):
        """Context manager for the clickhouse-client-tty."""
        if client_args is None:
            client_args = {}

        for arg, value in client_args.items():
            if value == "null":
                client += f" --{arg}"
            else:
                client += f" --{arg} {value}"

        with self.cluster.shell(self.name) as bash:
            command_context = self.command(client, asynchronous=True, no_checks=True, name=name, bash=bash)

            with self.ClientQueryHandler(command_context) as _client:
                yield _client


class ZooKeeperNode(Node):
    """Node with ZooKeeper server."""

    SERVER_ENV = ""
    version_regex = re.compile(r"version ([.0-9]+)")

    def zk_server_command(self, command, **kwargs):
        return self.command(
            f"{self.SERVER_ENV}zkServer.sh {command}",
            steps=False,
            **kwargs,
        )

    def wait_zookeeper_healthy(self, timeout=300):
        with By(f"waiting until ZooKeeper server on {self.name} is healthy"):
            for attempt in retries(timeout=timeout, delay=1):
                with attempt:
                    if self.zk_server_command("status", no_checks=1).exitcode != 0:
                        fail("ZooKeeper server is not healthy")

    def zookeeper_pid(self):
        """Return ZooKeeper server pid if present otherwise return None."""
        if self.command("ls /data/zookeeper_server.pid", no_checks=True).exitcode == 0:
            return self.command("cat /data/zookeeper_server.pid").output.strip()
        return None

    def kill_zookeeper(self, timeout=300, signal="TERM"):
        """Kill ZooKeeper server."""

        with By(f"sending kill -{signal} to ZooKeeper server process on {self.name}"):
            pid = self.zookeeper_pid()
            self.command(f"kill -{signal} {pid}", exitcode=0, steps=False, timeout=timeout)

        with And("checking pid does not exist"):
            retry(self.command, timeout=timeout, delay=3)(
                f"ps {pid} | grep -v grep | grep ' {pid} '", steps=False, exitcode=1
            )

    def stop_zookeeper(self, timeout=300):
        """Stop ZooKeeper server."""

        with By(f"stopping {self.name}"):
            self.zk_server_command("stop")

    def start_zookeeper(self, timeout=300, check_version=True, skip_if_running=False):
        """Start ZooKeeper server."""
        if check_version:
            r = self.zk_server_command("version")
            version = self.version_regex.search(r.output).group(1)
            current().context.zookeeper_version = version

        with By(f"starting {self.name}"):
            r = self.zk_server_command("start", no_checks=True)
            if skip_if_running and "already running" in r.output:
                return
            assert r.exitcode == 0, error(r.output)

    def restart_zookeeper(self, timeout=300):
        """Restart ZooKeeper server."""

        with By(f"restarting {self.name}"):
            self.zk_server_command("restart", exitcode=0)

    def stop(self, timeout=300, retry_count=5):
        """Stop node."""
        if self.zookeeper_pid():
            self.stop_zookeeper(timeout=timeout)

        return super(ZooKeeperNode, self).stop(timeout=timeout, retry_count=retry_count)

    def start(
        self,
        timeout=300,
        start_zookeeper=True,
        retry_count=5,
    ):
        """Start node."""
        super(ZooKeeperNode, self).start(timeout=timeout, retry_count=retry_count)

        if start_zookeeper:
            self.start_zookeeper(
                timeout=timeout,
            )

    def restart(
        self,
        timeout=300,
        start_zookeeper=True,
        retry_count=5,
    ):
        """Restart node."""
        if self.zookeeper_pid():
            self.stop_zookeeper(timeout=timeout)

        super(ZooKeeperNode, self).restart(timeout=timeout, retry_count=retry_count)

        if start_zookeeper:
            self.start_zookeeper(timeout=timeout)


class ClickHouseNode(Node):
    """Node with ClickHouse server."""

    def enable_thread_fuzzer(self):
        with Given("enabling THREAD_FUZZER"):
            self.command("export THREAD_FUZZER_CPU_TIME_PERIOD_US=1000")
            self.command("export THREAD_FUZZER_SLEEP_PROBABILITY=0.1")
            self.command("export THREAD_FUZZER_SLEEP_TIME_US=100000")

            self.command("export THREAD_FUZZER_pthread_mutex_lock_BEFORE_MIGRATE_PROBABILITY=1")
            self.command("export THREAD_FUZZER_pthread_mutex_lock_AFTER_MIGRATE_PROBABILITY=1")
            self.command("export THREAD_FUZZER_pthread_mutex_unlock_BEFORE_MIGRATE_PROBABILITY=1")
            self.command("export THREAD_FUZZER_pthread_mutex_unlock_AFTER_MIGRATE_PROBABILITY=1")

            self.command("export THREAD_FUZZER_pthread_mutex_lock_BEFORE_SLEEP_PROBABILITY=0.001")
            self.command("export THREAD_FUZZER_pthread_mutex_lock_AFTER_SLEEP_PROBABILITY=0.001")
            self.command("export THREAD_FUZZER_pthread_mutex_unlock_BEFORE_SLEEP_PROBABILITY=0.001")
            self.command("export THREAD_FUZZER_pthread_mutex_unlock_AFTER_SLEEP_PROBABILITY=0.001")
            self.command("export THREAD_FUZZER_pthread_mutex_lock_BEFORE_SLEEP_TIME_US=10000")
            self.command("export THREAD_FUZZER_pthread_mutex_lock_AFTER_SLEEP_TIME_US=10000")
            self.command("export THREAD_FUZZER_pthread_mutex_unlock_BEFORE_SLEEP_TIME_US=10000")
            self.command("export THREAD_FUZZER_pthread_mutex_unlock_AFTER_SLEEP_TIME_US=10000")

    def wait_clickhouse_healthy(self, timeout=90, check_version=True, initial_delay=0):
        with By(f"waiting until ClickHouse server on {self.name} is healthy"):
            for attempt in retries(timeout=timeout, delay=5, initial_delay=initial_delay):
                with attempt:
                    with By("checking ClickHouse server is accessible"):
                        r = self.query("SELECT version() FORMAT CSV", no_checks=1, steps=False)
                    if r.exitcode == 0:
                        break

                    with By("checking logs for errors"):
                        log_messages = self.command(
                            "cat /var/log/clickhouse-server/clickhouse-server.err.log "
                            "| grep '^20.*Exception:' | tail -n 5 | cut -b -512",
                            no_checks=True,
                            steps=False,
                        ).output

                        fail(f"ClickHouse server is not healthy\nServer Exceptions:\n{log_messages}")

            if check_version:
                node_version = self.query("SELECT version() FORMAT CSV", no_checks=1, steps=False).output.replace(
                    '"', ""
                )
                if current().context.clickhouse_version is None:
                    current().context.clickhouse_version = node_version
                else:
                    assert check_clickhouse_version(f"={node_version}")(current()), error()

            query = "SELECT * FROM system.build_options " "WHERE name = 'CXX_FLAGS' FORMAT TabSeparated"
            output = self.query(query, no_checks=1, steps=False).output
            sanitizers = {
                "fsanitize=thread": "tsan",
                "fsanitize=memory": "msan",
                "fsanitize=address": "asan",
                "fsanitize=undefined": "ubsan",
            }
            sanitizer_name = next((name for flag, name in sanitizers.items() if flag in output), None)
            build_option = {}
            if sanitizer_name:
                build_option["sanitizer"] = sanitizer_name
            current().context.build_options = getattr(current().context, "build_options", {})
            current().context.build_options[self.name] = build_option

            git_branch = self.query(
                "SELECT value FROM system.build_options WHERE name = 'GIT_BRANCH' FORMAT TabSeparated",
                no_checks=1,
                steps=False,
            ).output.strip()

            current().context.build_options[self.name]["git_branch"] = git_branch

            full_clickhouse_version = self.query(
                "SELECT version() FORMAT TabSeparated", no_checks=1, steps=False
            ).output.strip()
            current().context.full_clickhouse_version = full_clickhouse_version

    def clickhouse_pid(self):
        """
        Return ClickHouse server pid if present otherwise return None.
        """
        r = self.command("cat /tmp/clickhouse-server.pid", no_checks=True, steps=False)
        if r.exitcode == 0:
            return r.output.strip()
        return None

    def stop_clickhouse(self, timeout=300, safe=True, signal="TERM"):
        """Stop ClickHouse server."""
        with By("capturing pid"):
            pid = self.clickhouse_pid()
            if pid is None:  # we have crashed or already stopped
                return

        if safe:
            with By("stopping ClickHouse server gracefully"):
                self.query("SYSTEM STOP MOVES")
                self.query("SYSTEM STOP MERGES")
                self.query("SYSTEM FLUSH LOGS")
                with By("waiting for 5 sec for moves and merges to stop"):
                    time.sleep(5)
                with And("forcing to sync everything to disk"):
                    self.command("sync", timeout=300, exitcode=0)

        with By(f"sending kill -{signal} to ClickHouse server process on {self.name}"):
            self.command(f"kill -{signal} {pid}", no_checks=True, steps=False)

        with And("checking pid does not exist"):
            for i, attempt in enumerate(retries(timeout=100, delay=3)):
                with attempt:
                    if i > 0 and i % 20 == 0:
                        self.command(f"kill -KILL {pid}", no_checks=True, steps=False)
                    if (
                        self.command(
                            f"ps {pid} | grep -v grep | grep ' clickhouse.server '",
                            steps=False,
                            no_checks=True,
                        ).exitcode
                        != 1
                    ):
                        fail("pid still alive")

        with And("killing any remaining ClickHouse child processes"):
            for i, attempt in enumerate(retries(timeout=100, delay=3)):
                with attempt:
                    result = self.command(
                        "pgrep -f 'clickhouse.*server'",
                        steps=False,
                        no_checks=True,
                    )
                    if result.exitcode == 1:
                        break

                    if i > 0 and i % 10 == 0:
                        self.command(
                            f"pkill -KILL -f 'clickhouse.*server'",
                            steps=False,
                            no_checks=True,
                        )
                    else:
                        self.command(
                            f"pkill -{signal} -f 'clickhouse.*server'",
                            steps=False,
                            no_checks=True,
                        )

                    result = self.command(
                        "pgrep -f 'clickhouse.*server'",
                        steps=False,
                        no_checks=True,
                    )
                    if result.exitcode != 1:
                        fail("ClickHouse server process still alive")

        with And("deleting ClickHouse server pid file"):
            self.command("rm -rf /tmp/clickhouse-server.pid", exitcode=0, steps=False)

    def start_clickhouse(
        self,
        timeout=60,
        wait_healthy=True,
        user=None,
        thread_fuzzer=False,
        check_version=True,
        log_dir="/var/log/clickhouse-server",
        skip_if_running=False,
    ):
        """Start ClickHouse server."""
        pid = self.clickhouse_pid()
        if pid:
            if skip_if_running:
                return
            else:
                raise RuntimeError(f"ClickHouse server already running with pid {pid}")

        if thread_fuzzer:
            self.enable_thread_fuzzer()

        for attempt in retries(timeout=timeout, delay=30):
            with attempt:
                if user is None:
                    with By("starting ClickHouse server process"):
                        self.command(
                            "clickhouse server --config-file=/etc/clickhouse-server/config.xml"
                            f" --log-file={log_dir}/clickhouse-server.log"
                            f" --errorlog-file={log_dir}/clickhouse-server.err.log"
                            " --pidfile=/tmp/clickhouse-server.pid --daemon",
                            exitcode=0,
                            steps=False,
                        )
                else:
                    with By(f"starting ClickHouse server process from {user}"):
                        self.command(
                            f"su {user} -c"
                            '"clickhouse server --config-file=/etc/clickhouse-server/config.xml'
                            f" --log-file={log_dir}/clickhouse-server.log"
                            f" --errorlog-file={log_dir}/clickhouse-server.err.log"
                            ' --pidfile=/tmp/clickhouse-server.pid --daemon"',
                            exitcode=0,
                            steps=False,
                        )

                with And("checking that ClickHouse server pid file was created"):
                    for attempt in retries(timeout=timeout, delay=3):
                        with attempt:
                            if (
                                self.command(
                                    "ls /tmp/clickhouse-server.pid",
                                    steps=False,
                                    no_checks=True,
                                ).exitcode
                                != 0
                            ):
                                fail("no pid file yet")

                if wait_healthy:
                    self.wait_clickhouse_healthy(timeout=timeout, check_version=check_version, initial_delay=2)

    def restart_clickhouse(self, timeout=300, safe=True, wait_healthy=True, retry_count=5, user=None):
        """Restart ClickHouse server."""
        self.stop_clickhouse(timeout=timeout, safe=safe)

        self.start_clickhouse(timeout=timeout, wait_healthy=wait_healthy, user=user)

    def stop(self, timeout=300, safe=True, retry_count=5):
        """Stop node."""
        if self.clickhouse_pid():
            self.stop_clickhouse(timeout=timeout, safe=safe)

        return super(ClickHouseNode, self).stop(timeout=timeout, retry_count=retry_count)

    def start(
        self,
        timeout=300,
        start_clickhouse=True,
        wait_healthy=True,
        retry_count=5,
        user=None,
    ):
        """Start node."""
        super(ClickHouseNode, self).start(timeout=timeout, retry_count=retry_count)

        if start_clickhouse:
            self.start_clickhouse(
                timeout=timeout,
                wait_healthy=wait_healthy,
                user=user,
            )

    def restart(
        self,
        timeout=300,
        safe=True,
        start_clickhouse=True,
        wait_healthy=True,
        retry_count=5,
        user=None,
    ):
        """Restart node."""
        if self.clickhouse_pid():
            self.stop_clickhouse(timeout=timeout, safe=safe)

        super(ClickHouseNode, self).restart(timeout=timeout, retry_count=retry_count)

        if start_clickhouse:
            self.start_clickhouse(timeout=timeout, wait_healthy=wait_healthy, user=user)

    def hash_query(
        self,
        sql,
        hash_utility="sha1sum",
        steps=True,
        step=By,
        settings=None,
        secure=False,
        query_id=None,
        pipe_cmd="echo -e",
        *args,
        **kwargs,
    ):
        """Execute sql query inside the container and return the hash of the output.

        :param sql: sql query
        :param hash_utility: hash function which used to compute hash
        """
        settings = list(settings or [])
        query_settings = list(settings)

        if hasattr(current().context, "default_query_settings"):
            query_settings += current().context.default_query_settings

        if query_id is not None:
            query_settings += [("query_id", f"{query_id}")]

        client = "clickhouse client -n"
        if secure:
            client += " -s" if check_clickhouse_version("<24.1")(current()) else " --secure"

        if len(sql) > 1024:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8") as query:
                query.write(sql)
                query.flush()
                command = f'set -o pipefail && cat "{query.name}" | {self.cluster.docker_compose} exec -T {self.name} {client} | {hash_utility}'
                for setting in query_settings:
                    name, value = setting
                    client += f' --{name} "{value}"'
                description = f"""
                            {pipe_cmd} \"{sql[:100]}...\" > {query.name}
                            {command}
                        """
                with (
                    step(
                        "executing command",
                        description=description,
                        format_description=False,
                    )
                    if steps
                    else NullStep()
                ):
                    try:
                        r = self.cluster.bash(None)(command, *args, **kwargs)
                    except ExpectTimeoutError:
                        self.cluster.close_bash(None)
        else:
            command = f'set -o pipefail && {pipe_cmd} "{sql}" | {client} | {hash_utility}'
            for setting in query_settings:
                name, value = setting
                client += f' --{name} "{value}"'
            with step("executing command", description=command, format_description=False) if steps else NullStep():
                try:
                    r = self.cluster.bash(self.name)(command, *args, **kwargs)
                except ExpectTimeoutError:
                    self.cluster.close_bash(self.name)

        with Then(f"exitcode should be 0") if steps else NullStep():
            assert r.exitcode == 0, error(r.output)

        return r.output

    def diff_query(
        self,
        sql,
        expected_output,
        steps=True,
        step=By,
        settings=None,
        secure=False,
        query_id=None,
        pipe_cmd="echo -e",
        *args,
        **kwargs,
    ):
        """Execute inside the container but from the host and compare its output
        to file that is located on the host.

        For example:
            diff <(echo "SELECT * FROM myints FORMAT CSVWithNames" | clickhouse-client -mn) select.out

        :param sql: sql query
        :param expected_output: path to the expected output
        """
        settings = list(settings or [])
        query_settings = list(settings)

        if hasattr(current().context, "default_query_settings"):
            query_settings += current().context.default_query_settings

        if query_id is not None:
            query_settings += [("query_id", f"{query_id}")]

        client = "clickhouse client -n"
        if secure:
            client += " -s" if check_clickhouse_version("<24.1")(current()) else " --secure"

        if len(sql) > 1024:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8") as query:
                query.write(sql)
                query.flush()
                command = f'diff <(cat "{query.name}" | {self.cluster.docker_compose} exec -T {self.name} {client}) {expected_output}'
                for setting in query_settings:
                    name, value = setting
                    command += f' --{name} "{value}"'
                description = f"""
                    {pipe_cmd} \"{sql[:100]}...\" > {query.name}
                    {command}
                """
                with (
                    step(
                        "executing command",
                        description=description,
                        format_description=False,
                    )
                    if steps
                    else NullStep()
                ):
                    try:
                        r = self.cluster.bash(None)(command, *args, **kwargs)
                    except ExpectTimeoutError:
                        self.cluster.close_bash(None)
        else:
            command = f'diff <({pipe_cmd} "{sql}" | {self.cluster.docker_compose} exec -T {self.name} {client}) {expected_output}'
            for setting in query_settings:
                name, value = setting
                command += f' --{name} "{value}"'
            with step("executing command", description=command, format_description=False) if steps else NullStep():
                try:
                    r = self.cluster.bash(None)(command, *args, **kwargs)
                except ExpectTimeoutError:
                    self.cluster.close_bash(None)

        with Then(f"exitcode should be 0") if steps else NullStep():
            assert r.exitcode == 0, error(r.output)

    def query(
        self,
        sql,
        message=None,
        exitcode=None,
        steps=True,
        no_checks=False,
        raise_on_exception=False,
        ignore_exception=False,
        step=By,
        settings=None,
        inline_settings=None,
        retry_count=5,
        messages_to_retry=None,
        retry_delay=5,
        secure=False,
        max_query_output_in_bytes="-0",
        query_id=None,
        use_file=False,
        hash_output=None,
        file_output=None,
        pipe_cmd="echo -e",
        progress=False,
        rewrite_settings=False,
        *args,
        **kwargs,
    ):
        """Execute and check query.
        :param sql: sql query
        :param message: expected message that should be in the output, default: None
        :param exitcode: expected exitcode, default: None
        :param steps: wrap query execution in a step, default: True
        :param no_check: disable exitcode and message checks, default: False
        :param step: wrapping step class, default: By
        :param settings: list of settings to be used for the query in the form [(name, value),...], default: None
        :param inline_settings: list of inline settings to be used for the query in the form [(name, value),...], default: None
        :param retry_count: number of retries, default: 5
        :param messages_to_retry: list of messages in the query output for
               which retry should be triggered, default: MESSAGES_TO_RETRY
        :param retry_delay: number of seconds to sleep before retry, default: 5
        :param secure: use secure connection, default: False
        :param max_query_output_in_bytes: truncate query output the specified number of bytes using 'head' command utility,
                default: -0 (do not truncate any output)
        :param use_file: determines whether to use a temporary file for storing the SQL query. default: False
        :param hash_output: specifies whether the output of the executed command should be hashed.
                if set to True, the output will be processed through the `sha512sum` command, which calculates the SHA-512 hash value.
                default: None
        :param file_output: specifies the file path where the output of the executed command should be stored.
                if specified, the output will be redirected to the specified file instead of being displayed on the console.
                default: None
        :param rewrite_settings: specifies whether to rewrite the default query settings with the provided settings.
                if set to True, the default query settings will be rewritten by the same settings that are provided in the 'settings' parameter.
                default: False
        """
        r = None
        retry_count = max(0, int(retry_count))
        retry_delay = max(0, float(retry_delay))
        settings = list(settings or [])
        inline_settings = list(inline_settings or [])
        query_settings = list(settings)

        if raise_on_exception:
            steps = False

        if messages_to_retry is None:
            messages_to_retry = MESSAGES_TO_RETRY

        if hasattr(current().context, "default_query_settings"):
            if rewrite_settings:
                settings_names = [name for name, _ in settings]
                for name, value in current().context.default_query_settings:
                    if name not in settings_names:
                        query_settings.append((name, value))
            else:
                query_settings += current().context.default_query_settings

        if query_id is not None:
            query_settings += [("query_id", f"{query_id}")]

        if inline_settings:
            sql = "; ".join([f"SET {name} = {value}" for name, value in inline_settings]) + "; " + sql

        client = "clickhouse client -n"
        if secure:
            client += " -s" if check_clickhouse_version("<24.1")(current()) else " --secure"

        if progress:
            client += " --progress"

        if len(sql) > 1024 or use_file:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8") as query:
                query.write(sql)
                query.flush()

                client_options = ""
                for setting in query_settings:
                    name, value = setting
                    client_options += f' --{name} "{value}"'

                if max_query_output_in_bytes != "-0":
                    command = f'cat "{query.name}" | {self.cluster.docker_compose} exec -T {self.name} bash -c "(set -o pipefail && {client}{client_options} 2>&1 | head -c {max_query_output_in_bytes})"'
                else:
                    if hash_output:
                        command = f'cat "{query.name}" | {self.cluster.docker_compose} exec -T {self.name} bash -c "(set -o pipefail && {client}{client_options} 2>&1 | sha512sum)"'
                    elif file_output:
                        command = f'cat "{query.name}" | {self.cluster.docker_compose} exec -T {self.name} bash -c "(set -o pipefail && {client}{client_options} 2>&1 > \'{file_output}\')"'
                    else:
                        command = f'cat "{query.name}" | {self.cluster.docker_compose} exec -T {self.name} bash -c "{client}{client_options} 2>&1"'

                description = f"""
                    {pipe_cmd} \"{sql[:100]}...\" > {query.name}
                    {command}
                """
                with (
                    step(
                        "executing command",
                        description=description,
                        format_description=False,
                    )
                    if steps
                    else NullStep()
                ):
                    try:
                        r = self.cluster.bash(None)(command, *args, **kwargs)
                    except ExpectTimeoutError:
                        self.cluster.close_bash(None)
                        raise
        else:
            client_options = ""
            for setting in query_settings:
                name, value = setting
                client_options += f' --{name} "{value}"'

            if max_query_output_in_bytes != "-0":
                command = f'(set -o pipefail && {pipe_cmd} "{sql}" | {client}{client_options} 2>&1 | head -c {max_query_output_in_bytes})'
            else:
                if hash_output:
                    command = f'(set -o pipefail && {pipe_cmd} "{sql}" | {client}{client_options} 2>&1 | sha512sum)'
                else:
                    command = f'{pipe_cmd} "{sql}" | {client}{client_options} 2>&1'

            with step("executing command", description=command, format_description=False) if steps else NullStep():
                try:
                    r = self.cluster.bash(self.name)(command, *args, **kwargs)
                except ExpectTimeoutError:
                    self.cluster.close_bash(self.name)
                    raise

        if r is None:
            raise RuntimeError("query was not executed; did you skip the steps?")

        if retry_count and retry_count > 0:
            if any(msg in r.output for msg in messages_to_retry):
                time.sleep(retry_delay)
                return self.query(
                    sql=sql,
                    message=message,
                    exitcode=exitcode,
                    steps=steps,
                    no_checks=no_checks,
                    raise_on_exception=raise_on_exception,
                    step=step,
                    settings=settings,
                    retry_count=retry_count - 1,
                    messages_to_retry=messages_to_retry,
                    retry_delay=retry_delay,
                    *args,
                    **kwargs,
                )

        if no_checks:
            return r

        if exitcode is not None:
            with Then(f"exitcode should be {exitcode}") if steps else NullStep():
                assert r.exitcode == exitcode, error(r.output)

        if message is not None:
            with Then(f"output should contain message", description=message) if steps else NullStep():
                assert message in r.output, error(r.output)

        if not ignore_exception:
            if message is None or "Exception:" not in message:
                with Then("check if output has exception") if steps else NullStep():
                    if "Exception:" in r.output:
                        if raise_on_exception:
                            raise QueryRuntimeException(r.output)
                        assert False, error(r.output)

        return r


class ClickHouseKeeperNode(Node):
    """Node with ClickHouse Keeper."""

    def keeper_pid(self):
        """Return ClickHouse Keeper pid if present
        otherwise return None.
        """
        if self.command("ls /tmp/clickhouse-keeper.pid", no_checks=True).exitcode == 0:
            return self.command("cat /tmp/clickhouse-keeper.pid").output.strip()
        return None

    def stop_keeper(self, timeout=100, signal="TERM"):
        """Stop ClickHouse Keeper."""

        with By(f"sending kill -{signal} to ClickHouse Keeper process on {self.name}"):
            pid = self.keeper_pid()
            self.command(f"kill -{signal} {pid}", exitcode=0, steps=False)

        with And("checking pid does not exist"):
            for i, attempt in enumerate(retries(timeout=timeout, delay=5)):
                with attempt:
                    if i > 0 and i % 20 == 0:
                        self.command(f"kill -KILL {pid}", steps=False)

                    # The keeper image uses busybox ps, which can't check a specific pid
                    # instead, check that memory usage is 0
                    r = self.command(
                        f"cat /proc/{pid}/statm | grep '[1-9]'",
                        steps=False,
                        no_checks=True,
                    )

                    if r.exitcode == 0:
                        fail("pid still alive")

        with And("deleting ClickHouse Keeper pid file"):
            self.command("rm -rf /tmp/clickhouse-keeper.pid", exitcode=0, steps=False)

    def start_keeper(
        self,
        timeout=100,
        user=None,
        force_recovery=False,
        check_version=True,
        skip_if_running=False,
    ):
        """Start ClickHouse Keeper."""
        if check_version:
            r = self.command("/usr/bin/clickhouse-keeper --version", steps=False)
            current().context.keeper_version = filter_version(r.output.strip())

        pid = self.keeper_pid()
        if pid:
            if skip_if_running:
                return
            else:
                raise RuntimeError(f"ClickHouse Keeper already running with pid {pid}")

        start_cmd = (
            "/usr/bin/clickhouse-keeper --config-file=/etc/clickhouse-keeper/keeper_config.xml"
            " --log-file=/var/log/clickhouse-keeper/clickhouse-keeper.log"
            " --errorlog-file=/var/log/clickhouse-keeper/clickhouse-keeper.err.log"
            " --pidfile=/tmp/clickhouse-keeper.pid --daemon"
        )
        if force_recovery:
            start_cmd += " --force-recovery"
        if user is not None:
            start_cmd = f'su {user} -c "{start_cmd}"'

        with By("starting ClickHouse keeper process"):
            self.command(
                start_cmd,
                exitcode=0,
                steps=False,
            )

        with And("checking that ClickHouse keeper pid file was created"):
            for attempt in retries(timeout=timeout, delay=1):
                with attempt:
                    if self.command("ls /tmp/clickhouse-keeper.pid", steps=False, no_checks=True).exitcode != 0:
                        fail("no pid file yet")

    def restart_keeper(self, timeout=100, user=None):
        """Restart ClickHouse Keeper."""
        if self.keeper_pid():
            self.stop_keeper(timeout=timeout)

        self.start_keeper(timeout=timeout, user=user)

    def stop(self, timeout=100, retry_count=5):
        """Stop node."""
        if self.keeper_pid():
            self.stop_keeper(timeout=timeout)

        return super(ClickHouseKeeperNode, self).stop(timeout=timeout, retry_count=retry_count)

    def start(
        self,
        timeout=100,
        start_keeper=True,
        wait_healthy=True,
        retry_count=5,
        user=None,
    ):
        """Start node."""
        super(ClickHouseKeeperNode, self).start(timeout=timeout, retry_count=retry_count)

        if start_keeper:
            self.start_keeper(
                timeout=timeout,
                user=user,
            )

    def restart(
        self,
        timeout=100,
        safe=True,
        start_keeper=True,
        user=None,
    ):
        """Restart node."""
        if self.keeper_pid():
            self.stop_keeper(timeout=timeout, safe=safe)

        super(ClickHouseKeeperNode, self).restart(timeout=timeout)

        if start_keeper:
            self.start_keeper(timeout=timeout, user=user)


class PackageDownloader:
    """Download and unpack packages."""

    package_formats = (".deb", ".rpm", ".tgz")

    def extended_prefix_handler(self, path: str):
        """
        Interprets an extended set of package prefixes in order to simulate
        the older mode of operation where binaries were copied from packages
        instead of installing the package.

        Remove if nobody is using this in 2 months.
        """
        use_ripped_binary_by_default = False

        if "://" not in path:
            # No extended prefix, treat as a file path
            return path, use_ripped_binary_by_default

        if path.startswith("binary-"):
            use_ripped_binary_by_default = True
            path = path.split("-", 1)[1]

        elif path.startswith("package-"):
            use_ripped_binary_by_default = False
            path = path.split("-", 1)[1]

        if path.startswith("url://"):
            path = path.replace("url://", "https://", 1)

        if path.startswith("file://"):
            path = path.replace("file://", "", 1)

        return path, use_ripped_binary_by_default

    def __init__(self, source, program_name="clickhouse", binary_only=False):
        self.source = source
        self.binary_path = None
        self.docker_image = None
        self.program_name = program_name
        self.package_path = None
        self.package_version = None

        source, use_binary_instead = self.extended_prefix_handler(source)
        if use_binary_instead:
            binary_only = True

        if source.startswith("docker://"):
            self.get_binary_from_docker(source)

        elif source.startswith(("http://", "https://")):
            self.get_binary_from_url(source)

        elif source.endswith(self.package_formats):
            self.get_binary_from_package(source)
        else:
            self.binary_path = source

        if self.binary_path:
            self.binary_path = os.path.abspath(self.binary_path)
            with Shell() as bash:
                if os.path.relpath(self.binary_path, current_dir()).startswith("../.."):
                    # Binary is outside of the build context, move it to where docker can find it
                    binaries_dir = os.path.abspath(f"{current_dir()}/../binaries")
                    new_path = f"{binaries_dir}/{os.path.basename(self.binary_path)}"
                    bash(f"mkdir -p {binaries_dir}")
                    bash(f"cp {self.binary_path} {new_path}")
                    self.binary_path = os.path.relpath(new_path)

                bash(f"chmod +x {self.binary_path}")

                if not self.package_version:
                    if current_cpu() != "arm":
                        self.package_version = (
                            bash(f"{self.binary_path} server --version | grep -Po '(?<=version )[0-9.a-z]*'")
                            .output.split("\n")[-1]
                            .strip(".")
                        )
                    else:
                        # Mac: use Python regex since BSD grep doesn't support -P
                        version_output = bash(f"{self.binary_path} server --version 2>&1").output

                        matches = re.findall(r"(?<=version )[0-9.a-z]*", version_output)
                        if matches:
                            self.package_version = matches[-1].strip(".")

        if binary_only:
            # Hide the package path / image to force using binary
            # remove this block when removing extended_prefix_handler
            assert (
                self.binary_path
            ), "binary was not extracted, only docker, deb and tgz formats are supported in this mode"
            self.package_path = None
            self.docker_image = None

    def get_binary_from_docker(self, source):
        self.docker_image = source.split("docker://", 1)[1]

        self.package_version = parse_version_from_docker_path(self.docker_image)
        self.binary_path = get_binary_from_docker_container(
            docker_image=source,
            container_binary_path=f"/usr/bin/{self.program_name}",
        )

    def get_binary_from_url(self, source):
        path = download_http_binary(binary_source=source)
        if path.endswith(self.package_formats):
            self.get_binary_from_package(path)
        else:
            self.binary_path = path

    def get_binary_from_package(self, source):
        self.package_path = source
        if source.endswith(".deb"):
            self.get_binary_from_deb(source)
        elif source.endswith(".rpm"):
            pass
        elif source.endswith(".tgz"):
            self.binary_path = os.path.join(unpack_tgz(source), "usr/bin", self.program_name)

    def get_binary_from_deb(self, source):
        self.binary_path = unpack_deb(
            deb_binary_path=source,
            program_name=self.program_name,
        )


class Cluster(object):
    """Simple object around docker-compose cluster."""

    def __init__(
        self,
        local=False,
        clickhouse_path=None,
        as_binary=False,
        base_os=None,
        clickhouse_odbc_bridge_binary_path=None,
        configs_dir=None,
        nodes=None,
        docker_compose="docker-compose --log-level ERROR",
        docker_compose_project_dir=None,
        docker_compose_file="docker-compose.yml",
        environ=None,
        keeper_path=None,
        zookeeper_version=None,
        use_keeper=False,
        thread_fuzzer=False,
        collect_service_logs=False,
        use_zookeeper_nodes=False,
        frame=None,
        use_specific_version=False,
        rm_instances_files=True,
        reuse_env=False,
        cicd=False,
    ):
        self._bash = {}
        self._control_shell = None
        self.environ = {} if (environ is None) else environ
        self.clickhouse_path = clickhouse_path
        # Don't set base_os until we know if we have images or packages
        self.base_os = None
        self.keeper_base_os = None
        self.clickhouse_odbc_bridge_binary_path = clickhouse_odbc_bridge_binary_path
        self.keeper_path = keeper_path
        self.zookeeper_version = zookeeper_version
        self.use_keeper = use_keeper
        self.configs_dir = configs_dir
        self.local = local
        self.nodes: dict[str, list[str]] = nodes or {}
        self.docker_compose = docker_compose
        self.thread_fuzzer = thread_fuzzer
        self.running = False
        self.collect_service_logs = collect_service_logs
        self.use_zookeeper_nodes = use_zookeeper_nodes
        self.use_specific_version = use_specific_version
        self.reuse_env = reuse_env
        self.cicd = cicd
        if frame is None:
            frame = inspect.currentframe().f_back
        caller_dir = current_dir(frame=frame)
        self.clickhouse_docker_image_name = None
        self.keeper_docker_image_name = None

        # Check docker compose version >= MINIMUM_COMPOSE_VERSION
        with Shell() as bash:
            cmd = bash(f"{self.docker_compose} --version")
            version = cmd.output.split()[-1].strip("v").split(".")
            if version < MINIMUM_COMPOSE_VERSION.split("."):
                raise RuntimeError(f"docker-compose version must be >= {MINIMUM_COMPOSE_VERSION}")

        # auto set configs directory
        if self.configs_dir is None:
            caller_configs_dir = caller_dir
            if os.path.exists(caller_configs_dir):
                self.configs_dir = caller_configs_dir

        if not os.path.exists(self.configs_dir):
            raise TypeError(f"configs directory '{self.configs_dir}' does not exist")

        if docker_compose_project_dir is None:
            docker_compose_project_dir = os.path.join(self.configs_dir, os.path.basename(self.configs_dir) + "_env")

        if not docker_compose_project_dir:
            raise TypeError("docker compose project directory must be specified")

        if current_cpu() in ("aarch64", "arm"):
            if not docker_compose_project_dir.endswith("_arm64"):
                docker_compose_project_dir += f"_arm64"

        if not os.path.exists(docker_compose_project_dir):
            raise TypeError(f"docker compose project directory '{docker_compose_project_dir}' does not exist")

        docker_compose_file_path = os.path.join(docker_compose_project_dir, docker_compose_file)

        self.docker_compose_project_dir = docker_compose_project_dir

        if not os.path.exists(docker_compose_file_path):
            raise TypeError(f"docker compose file '{docker_compose_file_path}' does not exist")

        if rm_instances_files and not reuse_env:
            shutil.rmtree(
                os.path.join(docker_compose_project_dir, "..", "_instances"),
                ignore_errors=True,
            )

        if self.clickhouse_path:
            if self.use_specific_version:
                alternate_clickhouse_package = PackageDownloader(
                    self.use_specific_version,
                    program_name="clickhouse",
                    binary_only=True,
                )

                self.environ["CLICKHOUSE_SPECIFIC_BINARY"] = os.path.abspath(alternate_clickhouse_package.binary_path)

            clickhouse_package = PackageDownloader(
                self.clickhouse_path,
                program_name="clickhouse",
                binary_only=as_binary,
            )
            if getsattr(current().context, "clickhouse_version", None) is None and clickhouse_package.package_version:
                current().context.clickhouse_version = clickhouse_package.package_version

            self.clickhouse_path = clickhouse_package.binary_path

            if clickhouse_package.docker_image:
                self.clickhouse_docker_image_name = clickhouse_package.docker_image
            else:
                if base_os is None:
                    if clickhouse_package.package_path:
                        assert not clickhouse_package.package_path.endswith(".rpm"), error(
                            "base_os must be specified for rpm packages"
                        )
                    self.base_os = "altinityinfra/clickhouse-regression-multiarch:3.0"
                else:
                    self.base_os = base_os.split("docker://", 1)[-1]

                base_os_name = self.base_os.replace(":", "-")

                if clickhouse_package.package_path:
                    package_name = os.path.basename(clickhouse_package.package_path)
                    self.clickhouse_docker_image_name = f"{base_os_name}:{sanitize_docker_tag(package_name)}"
                    self.clickhouse_path = os.path.relpath(clickhouse_package.package_path)
                else:
                    self.clickhouse_docker_image_name = f"{base_os_name}:local-binary"
                    with Shell() as bash:
                        bash(  # Force rebuild
                            f"docker rmi --force clickhouse-regression/{self.clickhouse_docker_image_name}"
                        )

        if self.keeper_path:
            keeper_package = PackageDownloader(
                self.keeper_path,
                program_name=("clickhouse-keeper" if "keeper" in self.keeper_path else "clickhouse"),
                binary_only=as_binary,
            )
            if getsattr(current().context, "keeper_version", None) is None and keeper_package.package_version:
                current().context.keeper_version = keeper_package.package_version
            self.keeper_path = keeper_package.binary_path

            if keeper_package.docker_image:
                self.keeper_docker_image_name = keeper_package.docker_image
            else:
                if base_os is None:
                    if keeper_package.package_path:
                        assert not keeper_package.package_path.endswith(".rpm"), error(
                            "base_os must be specified for rpm packages"
                        )
                    self.keeper_base_os = "altinityinfra/clickhouse-regression-multiarch:2.0"
                else:
                    self.keeper_base_os = base_os.split("docker://", 1)[-1]

                base_os_name = self.keeper_base_os.replace(":", "-")

                if keeper_package.package_path:
                    package_name = os.path.basename(keeper_package.package_path)
                    self.keeper_docker_image_name = f"{base_os_name}:{sanitize_docker_tag(package_name)}"
                    self.keeper_path = os.path.relpath(keeper_package.package_path)
                else:
                    self.keeper_docker_image_name = f"{base_os_name}:local-binary"
                    with Shell() as bash:
                        bash(  # Force rebuild
                            f"docker rmi --force clickhouse-regression/{self.keeper_docker_image_name}"
                        )

        else:
            self.keeper_base_os = self.base_os
            self.keeper_docker_image_name = self.clickhouse_docker_image_name
            self.keeper_path = self.clickhouse_path

        self.docker_compose += (
            f' --ansi never --project-directory "{docker_compose_project_dir}" --file "{docker_compose_file_path}"'
        )
        self.lock = threading.Lock()

    @property
    def control_shell(self, timeout=300):
        """Must be called with self.lock.acquired."""
        if self._control_shell is not None:
            return self._control_shell

        time_start = time.time()
        i = -1
        while True:
            i += 1
            with By(f"attempt #{i}"):
                try:
                    shell = Shell()
                    shell.timeout = 30
                    shell("echo 1")
                    break
                except IOError:
                    raise
                except Exception as exc:
                    shell.__exit__(None, None, None)
                    if time.time() - time_start > timeout:
                        raise RuntimeError(f"failed to open control shell")
        self._control_shell = shell
        return self._control_shell

    def close_control_shell(self):
        """Must be called with self.lock.acquired."""
        if self._control_shell is None:
            return
        shell = self._control_shell
        self._control_shell = None
        shell.__exit__(None, None, None)

    def node_container_id(self, node, timeout=300):
        """Must be called with self.lock acquired."""
        container_id = None
        time_start = time.time()
        i = -1
        while True:
            i += 1
            with By(f"attempt #{i}"):
                try:
                    c = self.control_shell(f"{self.docker_compose} ps -q {node}", timeout=timeout)
                    container_id = c.output.strip()
                    if c.exitcode == 0 and len(container_id) > 1:
                        break
                except IOError:
                    raise
                except ExpectTimeoutError:
                    self.close_control_shell()
                timeout = timeout - (time.time() - time_start)
                if timeout <= 0:
                    raise RuntimeError(f"failed to get docker container id for the {node} service")
                time.sleep(1)
        return container_id

    def shell(self, node, timeout=300):
        """Returns unique shell terminal to be used."""
        container_id = None

        if node is not None:
            with self.lock:
                container_id = self.node_container_id(node=node, timeout=timeout)

        time_start = time.time()
        i = -1
        while True:
            i += 1
            with By(f"attempt #{i}"):
                try:
                    if node is None:
                        shell = Shell()
                    else:
                        shell = Shell(
                            command=[
                                "/bin/bash",
                                "--noediting",
                                "-c",
                                f"docker exec -it {container_id} bash --noediting",
                            ],
                            name=node,
                        )
                    shell.timeout = 30
                    shell("echo 1")
                    break
                except IOError:
                    raise
                except Exception as exc:
                    shell.__exit__(None, None, None)
                    if time.time() - time_start > timeout:
                        raise RuntimeError(f"failed to open bash to node {node}")

        shell.timeout = timeout
        return shell

    def bash(self, node, timeout=NONE, command="bash --noediting"):
        """Returns thread-local bash terminal
        to a specific node.
        :param node: name of the service
        """
        if timeout is NONE:
            timeout = 600 if self.cicd else 300

        test = current()

        current_thread = threading.current_thread()
        id = (current_thread.name, f"{node}")

        with self.lock:
            if self._bash.get(id) is None:
                if node is not None:
                    container_id = self.node_container_id(node=node, timeout=timeout)

                time_start = time.time()
                i = -1
                while True:
                    i += 1
                    with By(f"attempt #{i}"):
                        try:
                            if node is None:
                                self._bash[id] = Shell()
                            else:
                                self._bash[id] = Shell(
                                    command=[
                                        "/bin/bash",
                                        "--noediting",
                                        "-c",
                                        f"docker exec -it {container_id} {command}",
                                    ],
                                    name=node,
                                ).__enter__()
                            self._bash[id].timeout = 30
                            self._bash[id]("echo 1")
                            break
                        except IOError:
                            raise
                        except Exception as exc:
                            self._bash[id].__exit__(None, None, None)
                            if time.time() - time_start > timeout:
                                raise RuntimeError(f"failed to open bash to node {node}")

                if node is None:
                    for name, value in self.environ.items():
                        self._bash[id](f"export {name}={value}")

                self._bash[id].timeout = timeout

                # clean up any stale open shells for threads that have exited
                active_thread_names = {thread.name for thread in threading.enumerate()}

                for bash_id in list(self._bash.keys()):
                    thread_name, node_name = bash_id
                    if thread_name not in active_thread_names:
                        self._bash[bash_id].__exit__(None, None, None)
                        del self._bash[bash_id]

            return self._bash[id]

    def close_bash(self, node):
        current_thread = threading.current_thread()
        id = (current_thread.name, f"{node}")

        with self.lock:
            if self._bash.get(id) is None:
                return
            self._bash[id].__exit__(None, None, None)
            del self._bash[id]

    def __enter__(self):
        with Given("docker-compose cluster"):
            self.up()
        return self

    def __exit__(self, type, value, traceback):
        try:
            with Finally("I clean up"):
                if self.collect_service_logs:
                    with Finally("collect service logs"):
                        with Shell() as bash:
                            log_path = f"../_service_logs"
                            bash(f"cd {self.docker_compose_project_dir}", timeout=1000)
                            bash(f"mkdir -p {log_path}")
                            nodes = bash(f"{self.docker_compose} ps --services").output.split("\n")
                            debug(nodes)
                            for node in nodes:
                                snode = bash(
                                    f"{self.docker_compose} logs {node} " f"> {log_path}/{node}.log",
                                    timeout=1000,
                                )
                                if snode.exitcode != 0:
                                    xfail(f"failed to get service log - exitcode {snode.exitcode}")

                self.down()
        finally:
            with self.lock:
                for shell in self._bash.values():
                    shell.__exit__(type, value, traceback)

    def node(self, name):
        """Get object with node bound methods.
        :param name: name of service name
        """
        if name is not None:
            if self.use_zookeeper_nodes:
                if name.startswith("zookeeper"):
                    return ZooKeeperNode(self, name)
            if name.startswith("clickhouse"):
                return ClickHouseNode(self, name)
            elif name.startswith("keeper"):
                return ClickHouseKeeperNode(self, name)
        return Node(self, name)

    def down(self, timeout=300):
        """Bring cluster down by executing docker-compose down."""

        if self.reuse_env:
            return

        # add message to each clickhouse-server.log
        if settings.debug and self.running:
            for node in self.nodes["clickhouse"]:
                self.command(
                    node=node,
                    command=f'echo -e "\n-- sending stop to: {node} --\n" >> /var/log/clickhouse-server/clickhouse-server.log',
                )

        # Edit permissions on server files for external manipulation
        for node_type in ["clickhouse", "zookeeper", "keeper"]:
            for node in self.nodes.get(node_type, []):
                try:
                    self.open_instances_permissions(node=node)
                except:
                    pass

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
            cmd = self.command(
                None,
                f"{self.docker_compose} down -v --remove-orphans --timeout 60",
                bash=bash,
                timeout=timeout,
            )
            with self.lock:
                if self._control_shell:
                    self._control_shell.__exit__(None, None, None)
                    self._control_shell = None
            return cmd

    def open_instances_permissions(self, node):
        """
        Add open permissions on all files and folders in _instances.

        Will not do anything if cluster is already down.
        """
        with self.lock:
            try:
                with By(f"getting docker container id for {node}"):
                    container_id = self.node_container_id(node, timeout=1)
            except RuntimeError:
                return

        with By(f"querying mounted volumes for {node}"):
            with tempfile.NamedTemporaryFile() as tmp:
                self.command(
                    node=None,
                    command=f"docker inspect {container_id} > {tmp.name}",
                    exitcode=0,
                    steps=False,
                )
                mounts = json.load(tmp)[0]["Mounts"]

        docker_exposed_dirs = [m["Destination"] for m in mounts if "_instances" in m["Source"]]

        for exposed_dir in docker_exposed_dirs:
            with By(f"changing permissions in {exposed_dir}"):
                self.command(
                    node=node,
                    command=f"chmod a+rwX -R {exposed_dir}",
                    no_checks=True,
                    steps=False,
                )

    def temp_path(self):
        """Return temporary folder path."""
        p = f"{self.environ['CLICKHOUSE_TESTS_DIR']}/_temp"
        if not os.path.exists(p):
            os.mkdir(p)
        return p

    def temp_file(self, name):
        """Return absolute temporary file path."""
        return f"{os.path.join(self.temp_path(), name)}"

    def up(self, timeout=30 * 60):
        """Bring cluster up."""
        if self.local:
            with Given("I am running in local mode"):
                with Then(
                    "check --clickhouse-binary-path is specified",
                    description=self.clickhouse_path,
                ):
                    assert (
                        self.clickhouse_path
                    ), "when running in local mode then --clickhouse-binary-path must be specified"
                with And("path should exist"):
                    if self.base_os:  # check that we are not in docker mode
                        assert os.path.exists(self.clickhouse_path), self.clickhouse_path

            with And("I set all the necessary environment variables"):
                self.environ["COMPOSE_HTTP_TIMEOUT"] = "600"
                assert self.clickhouse_path
                self.environ["CLICKHOUSE_TESTS_SERVER_BIN_PATH"] = (
                    # To work with the dockerfiles, the path must be relative to the docker-compose directory
                    os.path.relpath(self.clickhouse_path, current_dir())
                )
                self.environ["CLICKHOUSE_TESTS_ODBC_BRIDGE_BIN_PATH"] = (
                    self.clickhouse_odbc_bridge_binary_path
                    or os.path.join(
                        os.path.dirname(self.clickhouse_path),
                        "clickhouse-odbc-bridge",
                    )
                )
                self.environ["CLICKHOUSE_TESTS_KEEPER_BIN_PATH"] = (
                    "" if not self.keeper_path else os.path.relpath(self.keeper_path, current_dir())
                )
                self.environ["CLICKHOUSE_TESTS_ZOOKEEPER_VERSION"] = self.zookeeper_version or ""
                self.environ["CLICKHOUSE_TESTS_COORDINATOR"] = "keeper" if self.use_keeper else "zookeeper"
                self.environ["CLICKHOUSE_TESTS_DIR"] = self.configs_dir
                self.environ["CLICKHOUSE_TESTS_DOCKER_IMAGE_NAME"] = self.clickhouse_docker_image_name
                self.environ["CLICKHOUSE_TESTS_BASE_OS"] = self.base_os
                self.environ["CLICKHOUSE_TESTS_BASE_OS_NAME"] = (
                    "clickhouse" if not self.base_os else self.base_os.split(":")[0].split("/")[-1]
                )
                self.environ["CLICKHOUSE_TESTS_KEEPER_DOCKER_IMAGE"] = self.keeper_docker_image_name
                self.environ["CLICKHOUSE_TESTS_KEEPER_BASE_OS"] = self.keeper_base_os
                self.environ["CLICKHOUSE_TESTS_KEEPER_BASE_OS_NAME"] = (
                    "clickhouse" if not self.keeper_base_os else self.keeper_base_os.split(":")[0].split("/")[-1]
                )

            with And("I list environment variables to show their values"):
                self.command(None, "env | grep CLICKHOUSE")

        def start_cluster(max_up_attempts=3):
            if not self.reuse_env:
                with By("pulling images for all the services"):
                    for pull_attempt in retries(count=5, delay=10):
                        with pull_attempt:
                            cmd = self.command(
                                None,
                                f"set -o pipefail && {self.docker_compose} pull 2>&1 | tee",
                                no_checks=True,
                                timeout=timeout,
                            )
                            if cmd.exitcode == 0:
                                break
                    else:
                        return False

                with And("checking if any containers are already running"):
                    self.command(None, f"set -o pipefail && {self.docker_compose} ps | tee")

                with And("executing docker-compose down just in case it is up"):
                    cmd = self.command(
                        None,
                        f"set -o pipefail && {self.docker_compose} down 2>&1 | tee",
                        no_checks=True,
                        timeout=timeout,
                    )
                    if cmd.exitcode != 0:
                        return False

                with And("checking if any containers are still left running"):
                    self.command(None, f"set -o pipefail && {self.docker_compose} ps | tee")

                with And("creating a unique builder just in case docker-compose needs to build images"):
                    self.command(
                        None,
                        f"docker buildx create --use --bootstrap --node clickhouse-regression-builder",
                        exitcode=0,
                    )

            with By("building the clickhouse image"):
                self.command(
                    None,
                    f"docker build "
                    f'--build-arg CLICKHOUSE_DOCKER_IMAGE_NAME="{self.environ["CLICKHOUSE_TESTS_DOCKER_IMAGE_NAME"]}" '
                    f'--build-arg CLICKHOUSE_PACKAGE="{self.environ["CLICKHOUSE_TESTS_SERVER_BIN_PATH"]}" '
                    f'--build-arg BASE_OS="{self.environ["CLICKHOUSE_TESTS_BASE_OS"]}" '
                    f'-t clickhouse-regression/{self.environ["CLICKHOUSE_TESTS_DOCKER_IMAGE_NAME"]} '
                    f'-f {current_dir()}/../docker-compose/base_os/{self.environ["CLICKHOUSE_TESTS_BASE_OS_NAME"] if self.environ["CLICKHOUSE_TESTS_BASE_OS_NAME"] else "clickhouse"}.Dockerfile '
                    f"{current_dir()}/../",
                    exitcode=0,
                )

            if self.clickhouse_docker_image_name != self.keeper_docker_image_name:
                with By("building the keeper image"):
                    self.command(
                        None,
                        f"docker build "
                        f'--build-arg CLICKHOUSE_DOCKER_IMAGE_NAME="{self.environ["CLICKHOUSE_TESTS_DOCKER_IMAGE_NAME"]}" '
                        f'--build-arg CLICKHOUSE_PACKAGE="{self.environ["CLICKHOUSE_TESTS_SERVER_BIN_PATH"]}" '
                        f'--build-arg BASE_OS="{self.environ["CLICKHOUSE_TESTS_BASE_OS"]}" '
                        f'-t clickhouse-regression/{self.environ["CLICKHOUSE_TESTS_KEEPER_DOCKER_IMAGE"]} '
                        f'-f {current_dir()}/../docker-compose/base_os/{self.environ["CLICKHOUSE_TESTS_KEEPER_BASE_OS_NAME"] if self.environ["CLICKHOUSE_TESTS_KEEPER_BASE_OS_NAME"] else "clickhouse"}.Dockerfile '
                        f"{current_dir()}/../",
                        exitcode=0,
                    )

            with By("executing docker-compose up"):
                up_args = "" if self.reuse_env else "--renew-anon-volumes --force-recreate"
                for attempt in retries(count=max_up_attempts):
                    with attempt:
                        cmd = self.command(
                            None,
                            f"set -o pipefail && {self.docker_compose} up {up_args} --timeout 600 -d 2>&1 | tee",
                            timeout=timeout,
                            no_checks=True,
                        )
                        if "port is already allocated" in cmd.output:
                            port = re.search(r"Bind for .+:([0-9]+) failed", cmd.output).group(1)

                            ps = self.command(None, f"docker ps | grep {port}", no_checks=True)
                            conflict_env = ps.output.split()[-1]
                            raise RuntimeError(f"Failed to allocate port {port}, already in use by {conflict_env}.")

                        assert cmd.exitcode == 0, error(cmd.output)
                        assert "ERROR:" not in cmd.output, error(cmd.output)
                        if "is unhealthy" not in cmd.output:
                            return True

            with Then("check there are no unhealthy containers"):
                ps_cmd = self.command(
                    None,
                    f'set -o pipefail && {self.docker_compose} ps | tee | grep -v "Exit 0"',
                )
                if "is unhealthy" in cmd.output or "Exit" in ps_cmd.output:
                    self.command(
                        None,
                        f"set -o pipefail && {self.docker_compose} logs | tee",
                    )
                    return False

            if cmd.exitcode == 0 and "is unhealthy" not in cmd.output and "Exit" not in ps_cmd.output:
                return True

            return False

        with Given("start the cluster"):
            all_running = False
            try:
                with When(f"starting the cluster"):
                    all_running = start_cluster(max_up_attempts=1)

            except:
                with When("making sure any running containers are stopped"):
                    self.command(
                        None,
                        f"set -o pipefail && {self.docker_compose} down 2>&1 | tee",
                    )

            if not all_running:
                fail("could not bring up docker-compose cluster")

        with Then("wait all nodes report healthy"):
            if self.use_zookeeper_nodes:
                for name in self.nodes["zookeeper"]:
                    self.node(name).wait_healthy()
                    if name.startswith("zookeeper"):
                        self.node(name).start_zookeeper(skip_if_running=self.reuse_env)

            for name in self.nodes["clickhouse"]:
                self.node(name).wait_healthy()
                if name == "clickhouse-different-versions":
                    self.node(name).start_clickhouse(
                        thread_fuzzer=self.thread_fuzzer,
                        check_version=False,
                        skip_if_running=self.reuse_env,
                    )
                elif name.startswith("clickhouse"):
                    self.node(name).start_clickhouse(thread_fuzzer=self.thread_fuzzer, skip_if_running=self.reuse_env)

            for name in self.nodes.get("keeper", []):
                if name.startswith("keeper"):
                    self.node(name).start_keeper(skip_if_running=self.reuse_env)

        self.running = True

    def command(
        self,
        node,
        command,
        message=None,
        messages=None,
        exitcode=0,
        steps=True,
        bash=None,
        no_checks=False,
        use_error=True,
        shell_command="bash --noediting",
        *args,
        **kwargs,
    ):
        """Execute and check command.
        :param node: name of the service
        :param command: command
        :param message: expected message that should be in the output, default: None
        :param messages: expected messages that should be in the output, default: None
        :param exitcode: expected exitcode, use no_checks or set to None to ignore, default: 0
        :param no_checks: skip exitcode and message checks, default: False
        :param steps: don't break command into steps, default: True
        """
        with By("executing command", description=command, format_description=False) if steps else NullStep():
            if bash is None:
                bash = self.bash(node, command=shell_command)
            try:
                r = bash(command, *args, **kwargs)
            except ExpectTimeoutError:
                self.close_bash(node)
                raise

        if no_checks:
            return r

        if exitcode is not None:
            with Then(f"exitcode should be {exitcode}", format_name=False) if steps else NullStep():
                if str(exitcode).startswith("!="):
                    exitcode = int(str(exitcode).split("!=", 1)[-1].strip())
                    assert r.exitcode != exitcode, error(r.output)
                else:
                    assert r.exitcode == exitcode, error(r.output)

        if messages is None:
            messages = []

        if message:
            messages = [message] + messages

        for i, message in enumerate(messages):
            with (
                Then(
                    f"output should contain message{' #' + str(i) if i > 0 else ''}",
                    description=message,
                    format_description=False,
                )
                if steps
                else NullStep()
            ):
                assert message in r.output, error(r.output)

        return r


@TestStep(Given)
def create_cluster(
    self,
    local=False,
    clickhouse_path=None,
    as_binary=False,
    base_os=None,
    clickhouse_odbc_bridge_binary_path=None,
    collect_service_logs=False,
    configs_dir=None,
    nodes=None,
    docker_compose="docker-compose --log-level ERROR",
    docker_compose_project_dir=None,
    docker_compose_file="docker-compose.yml",
    environ=None,
    keeper_path=None,
    zookeeper_version=None,
    use_keeper=False,
    thread_fuzzer=False,
    use_zookeeper_nodes=False,
    use_specific_version=False,
    reuse_env=False,
    cicd=False,
) -> Cluster:  # type: ignore
    """Create docker compose cluster."""
    with Cluster(
        local=local,
        clickhouse_path=clickhouse_path,
        as_binary=as_binary,
        base_os=base_os,
        clickhouse_odbc_bridge_binary_path=clickhouse_odbc_bridge_binary_path,
        collect_service_logs=collect_service_logs,
        configs_dir=configs_dir,
        nodes=nodes,
        docker_compose=docker_compose,
        docker_compose_project_dir=docker_compose_project_dir,
        docker_compose_file=docker_compose_file,
        environ=environ,
        keeper_path=keeper_path,
        zookeeper_version=zookeeper_version,
        use_keeper=use_keeper,
        thread_fuzzer=thread_fuzzer,
        use_zookeeper_nodes=use_zookeeper_nodes,
        use_specific_version=use_specific_version,
        reuse_env=reuse_env,
        cicd=cicd,
    ) as cluster:
        yield cluster
