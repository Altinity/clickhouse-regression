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

from testflows._core.cli.arg.common import description

import testflows.settings as settings

from testflows.core import *
from testflows.asserts import error
from testflows.connect import Shell as ShellBase
from testflows.uexpect import ExpectTimeoutError
from testflows._core.testtype import TestSubType
from helpers.common import check_clickhouse_version, current_cpu

MESSAGES_TO_RETRY = [
    "DB::Exception: ZooKeeper session has been expired",
    "DB::Exception: Connection loss",
    "Coordination::Exception: Session expired",
    "Coordination::Exception: Connection loss",
    "Coordination::Exception: Coordination error: Connection loss.",
    "Coordination::Exception: Operation timeout",
    "DB::Exception: Operation timeout",
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
    file_name = f"{short_hash(binary_source)}-{binary_source.rsplit('/', 1)[-1]}"
    file_dir = f"{current_dir()}/../binaries/"
    os.makedirs(file_dir, exist_ok=True)
    file_path = file_dir + file_name
    if not os.path.exists(file_path):
        with Shell() as bash:
            bash.timeout = 300
            try:
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
    deb_binary_dir = deb_binary_path.rsplit(".deb", 1)[0]
    os.makedirs(deb_binary_dir, exist_ok=True)
    with Shell() as bash:
        bash.timeout = 300
        if not os.path.exists(f"{deb_binary_dir}/{program_name}"):
            bash(f'ar x "{deb_binary_path}" --output "{deb_binary_dir}"')
            bash(
                f'tar -vxzf "{deb_binary_dir}/data.tar.gz" ./usr/bin/{program_name}" -O > "{deb_binary_dir}/{program_name}""'
            )
            bash(f'chmod +x "{deb_binary_dir}/{program_name}"')

    return f"{deb_binary_dir}/{program_name}"


def unpack_tar_gz(tar_path):
    """Unpack tar.gz file and return path to the result."""
    tar_dest_dir = tar_path.rsplit(".tar.gz", 1)[0]
    os.makedirs(tar_dest_dir, exist_ok=True)
    with Shell() as bash:
        bash.timeout = 300
        bash(f'tar -xzf "{tar_path}" -C "{tar_dest_dir}" --strip-components=1')
        bash(f'chmod +x "{tar_dest_dir}/bin/*"')

    return f"{tar_dest_dir}"


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

    class QueryHandler:
        def __init__(self, command_context, prompt="\[clickhouse1\] :\) "):
            self.command_context = command_context
            self.prompt = prompt

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
            match = re.search(r"Code:\s*(\d+)", message)
            if match:
                return int(match.group(1))
            else:
                return 0

        def query(self, query_string, match=None, exitcode=None, message=None):
            self.command_context.app.send(query_string)
            self.command_context.app.expect(query_string, escape=True)

            if match is not None:
                self.command_context.app.expect(match, escape=True)

            self.command_context.app.expect(self.prompt)

            query_result = self.command_context.app.child.before

            raise_exception = True

            if exitcode is not None:
                with Then(f"exitcode should be {exitcode}", format_name=False):
                    assert exitcode == self._parse_error_code(
                        str(query_result)
                    ), error()

                raise_exception = False
            if message is not None:
                with Then(f"message should be {message}", format_name=False):
                    assert message in query_result, error()

                raise_exception = False

            elif raise_exception and not query_result.strip().startswith("Output:"):
                raise Exception(query_result)

            return query_result

    def client(self, client="clickhouse-client-tty", name="clickhouse-client-tty"):
        command_context = self.command(
            client, asynchronous=True, no_checks=True, name=name
        )

        return self.QueryHandler(command_context)


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
            self.command(
                f"kill -{signal} {pid}", exitcode=0, steps=False, timeout=timeout
            )

        with And("checking pid does not exist"):
            retry(self.command, timeout=timeout, delay=3)(
                f"ps {pid}", steps=False, exitcode=1
            )

    def stop_zookeeper(self, timeout=300):
        """Stop ZooKeeper server."""

        with By(f"stopping {self.name}"):
            self.zk_server_command("stop")

    def start_zookeeper(self, timeout=300, check_version=True):
        """Start ZooKeeper server."""
        if check_version:
            r = self.zk_server_command("version")
            version = self.version_regex.search(r.output).group(1)
            current().context.zookeeper_version = version

        with By(f"starting {self.name}"):
            self.zk_server_command("start", exitcode=0)

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

            self.command(
                "export THREAD_FUZZER_pthread_mutex_lock_BEFORE_MIGRATE_PROBABILITY=1"
            )
            self.command(
                "export THREAD_FUZZER_pthread_mutex_lock_AFTER_MIGRATE_PROBABILITY=1"
            )
            self.command(
                "export THREAD_FUZZER_pthread_mutex_unlock_BEFORE_MIGRATE_PROBABILITY=1"
            )
            self.command(
                "export THREAD_FUZZER_pthread_mutex_unlock_AFTER_MIGRATE_PROBABILITY=1"
            )

            self.command(
                "export THREAD_FUZZER_pthread_mutex_lock_BEFORE_SLEEP_PROBABILITY=0.001"
            )
            self.command(
                "export THREAD_FUZZER_pthread_mutex_lock_AFTER_SLEEP_PROBABILITY=0.001"
            )
            self.command(
                "export THREAD_FUZZER_pthread_mutex_unlock_BEFORE_SLEEP_PROBABILITY=0.001"
            )
            self.command(
                "export THREAD_FUZZER_pthread_mutex_unlock_AFTER_SLEEP_PROBABILITY=0.001"
            )
            self.command(
                "export THREAD_FUZZER_pthread_mutex_lock_BEFORE_SLEEP_TIME_US=10000"
            )
            self.command(
                "export THREAD_FUZZER_pthread_mutex_lock_AFTER_SLEEP_TIME_US=10000"
            )
            self.command(
                "export THREAD_FUZZER_pthread_mutex_unlock_BEFORE_SLEEP_TIME_US=10000"
            )
            self.command(
                "export THREAD_FUZZER_pthread_mutex_unlock_AFTER_SLEEP_TIME_US=10000"
            )

    def wait_clickhouse_healthy(self, timeout=300, check_version=True):
        with By(f"waiting until ClickHouse server on {self.name} is healthy"):
            for attempt in retries(timeout=timeout, delay=1):
                with attempt:
                    if (
                        self.query(
                            "SELECT version() FORMAT CSV", no_checks=1, steps=False
                        ).exitcode
                        != 0
                    ):
                        fail("ClickHouse server is not healthy")

            if check_version:
                node_version = self.query(
                    "SELECT version() FORMAT CSV", no_checks=1, steps=False
                ).output.replace('"', "")
                if current().context.clickhouse_version is None:
                    current().context.clickhouse_version = node_version
                else:
                    assert check_clickhouse_version(f"={node_version}")(
                        current()
                    ), error()

    def clickhouse_pid(self):
        """Return ClickHouse server pid if present
        otherwise return None.
        """
        if self.command("ls /tmp/clickhouse-server.pid", no_checks=True).exitcode == 0:
            return self.command("cat /tmp/clickhouse-server.pid").output.strip()
        return None

    def stop_clickhouse(self, timeout=300, safe=True, signal="TERM"):
        """Stop ClickHouse server."""
        if safe:
            self.query("SYSTEM STOP MOVES")
            self.query("SYSTEM STOP MERGES")
            self.query("SYSTEM FLUSH LOGS")
            with By("waiting for 5 sec for moves and merges to stop"):
                time.sleep(5)
            with And("forcing to sync everything to disk"):
                self.command("sync", timeout=300, exitcode=0)

        with By(f"sending kill -{signal} to ClickHouse server process on {self.name}"):
            pid = self.clickhouse_pid()
            self.command(f"kill -{signal} {pid}", exitcode=0, steps=False)

        with And("checking pid does not exist"):
            for i, attempt in enumerate(retries(timeout=100, delay=3)):
                with attempt:
                    if i > 0 and i % 20 == 0:
                        self.command(f"kill -KILL {pid}", steps=False)
                    if (
                        self.command(f"ps {pid}", steps=False, no_checks=True).exitcode
                        != 1
                    ):
                        fail("pid still alive")

        with And("deleting ClickHouse server pid file"):
            self.command("rm -rf /tmp/clickhouse-server.pid", exitcode=0, steps=False)

    def start_clickhouse(
        self,
        timeout=300,
        wait_healthy=True,
        retry_count=5,
        user=None,
        thread_fuzzer=False,
        check_version=True,
        log_dir="/var/log/clickhouse-server",
    ):
        """Start ClickHouse server."""
        pid = self.clickhouse_pid()
        if pid:
            raise RuntimeError(f"ClickHouse server already running with pid {pid}")

        if thread_fuzzer:
            self.enable_thread_fuzzer()

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
            for attempt in retries(timeout=timeout, delay=1):
                with attempt:
                    if (
                        self.command(
                            "ls /tmp/clickhouse-server.pid", steps=False, no_checks=True
                        ).exitcode
                        != 0
                    ):
                        fail("no pid file yet")

        if wait_healthy:
            self.wait_clickhouse_healthy(timeout=timeout, check_version=check_version)

    def restart_clickhouse(
        self, timeout=300, safe=True, wait_healthy=True, retry_count=5, user=None
    ):
        """Restart ClickHouse server."""
        if self.clickhouse_pid():
            self.stop_clickhouse(timeout=timeout, safe=safe)

        self.start_clickhouse(timeout=timeout, wait_healthy=wait_healthy, user=user)

    def stop(self, timeout=300, safe=True, retry_count=5):
        """Stop node."""
        if self.clickhouse_pid():
            self.stop_clickhouse(timeout=timeout, safe=safe)

        return super(ClickHouseNode, self).stop(
            timeout=timeout, retry_count=retry_count
        )

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
            client += (
                " -s" if check_clickhouse_version("<24.1")(current()) else " --secure"
            )

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
            command = (
                f'set -o pipefail && {pipe_cmd} "{sql}" | {client} | {hash_utility}'
            )
            for setting in query_settings:
                name, value = setting
                client += f' --{name} "{value}"'
            with (
                step("executing command", description=command, format_description=False)
                if steps
                else NullStep()
            ):
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
            client += (
                " -s" if check_clickhouse_version("<24.1")(current()) else " --secure"
            )

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
            with (
                step("executing command", description=command, format_description=False)
                if steps
                else NullStep()
            ):
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
        """
        r = None
        retry_count = max(0, int(retry_count))
        retry_delay = max(0, float(retry_delay))
        settings = list(settings or [])
        query_settings = list(settings)

        if raise_on_exception:
            steps = False

        if messages_to_retry is None:
            messages_to_retry = MESSAGES_TO_RETRY

        if hasattr(current().context, "default_query_settings"):
            query_settings += current().context.default_query_settings

        if query_id is not None:
            query_settings += [("query_id", f"{query_id}")]

        client = "clickhouse client -n"
        if secure:
            client += (
                " -s" if check_clickhouse_version("<24.1")(current()) else " --secure"
            )

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

            with (
                step("executing command", description=command, format_description=False)
                if steps
                else NullStep()
            ):
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
            with (
                Then(f"output should contain message", description=message)
                if steps
                else NullStep()
            ):
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
        user="clickhouse",
        force_recovery=False,
        check_version=True,
    ):
        """Start ClickHouse Keeper."""
        if check_version:
            r = self.command("/usr/bin/clickhouse-keeper --version", steps=False)
            current().context.keeper_version = filter_version(r.output.strip())

        pid = self.keeper_pid()
        if pid:
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
                    if (
                        self.command(
                            "ls /tmp/clickhouse-keeper.pid", steps=False, no_checks=True
                        ).exitcode
                        != 0
                    ):
                        fail("no pid file yet")

    def restart_keeper(self, timeout=100, user="clickhouse"):
        """Restart ClickHouse Keeper."""
        if self.keeper_pid():
            self.stop_keeper(timeout=timeout)

        self.start_keeper(timeout=timeout, user=user)

    def stop(self, timeout=100, retry_count=5):
        """Stop node."""
        if self.keeper_pid():
            self.stop_keeper(timeout=timeout)

        return super(ClickHouseKeeperNode, self).stop(
            timeout=timeout, retry_count=retry_count
        )

    def start(
        self,
        timeout=100,
        start_keeper=True,
        wait_healthy=True,
        retry_count=5,
        user="clickhouse",
    ):
        """Start node."""
        super(ClickHouseKeeperNode, self).start(
            timeout=timeout, retry_count=retry_count
        )

        if start_keeper:
            self.start_keeper(
                timeout=timeout,
                wait_healthy=wait_healthy,
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


class Cluster(object):
    """Simple object around docker-compose cluster."""

    def __init__(
        self,
        local=False,
        clickhouse_binary_path=None,
        clickhouse_odbc_bridge_binary_path=None,
        configs_dir=None,
        nodes=None,
        docker_compose="docker-compose --log-level ERROR",
        docker_compose_project_dir=None,
        docker_compose_file="docker-compose.yml",
        environ=None,
        keeper_binary_path=None,
        zookeeper_version=None,
        use_keeper=False,
        thread_fuzzer=False,
        collect_service_logs=False,
        use_zookeeper_nodes=False,
        frame=None,
        use_specific_version=False,
        rm_instances_files=True,
    ):
        self._bash = {}
        self._control_shell = None
        self.environ = {} if (environ is None) else environ
        self.clickhouse_binary_path = clickhouse_binary_path
        self.clickhouse_odbc_bridge_binary_path = clickhouse_odbc_bridge_binary_path
        self.keeper_binary_path = keeper_binary_path
        self.zookeeper_version = zookeeper_version
        self.use_keeper = use_keeper
        self.configs_dir = configs_dir
        self.local = local
        self.nodes = nodes or {}
        self.docker_compose = docker_compose
        self.thread_fuzzer = thread_fuzzer
        self.running = False
        self.collect_service_logs = collect_service_logs
        self.use_zookeeper_nodes = use_zookeeper_nodes
        self.use_specific_version = use_specific_version
        if frame is None:
            frame = inspect.currentframe().f_back
        caller_dir = current_dir(frame=frame)

        # auto set configs directory
        if self.configs_dir is None:
            caller_configs_dir = caller_dir
            if os.path.exists(caller_configs_dir):
                self.configs_dir = caller_configs_dir

        if not os.path.exists(self.configs_dir):
            raise TypeError(f"configs directory '{self.configs_dir}' does not exist")

        if docker_compose_project_dir is None:
            docker_compose_project_dir = os.path.join(
                self.configs_dir, os.path.basename(self.configs_dir) + "_env"
            )

        if not docker_compose_project_dir:
            raise TypeError("docker compose project directory must be specified")

        if current_cpu() == "aarch64":
            if not docker_compose_project_dir.endswith("_arm64"):
                docker_compose_project_dir += f"_arm64"

        if not os.path.exists(docker_compose_project_dir):
            raise TypeError(
                f"docker compose project directory '{docker_compose_project_dir}' does not exist"
            )

        docker_compose_file_path = os.path.join(
            docker_compose_project_dir, docker_compose_file
        )

        self.docker_compose_project_dir = docker_compose_project_dir

        if not os.path.exists(docker_compose_file_path):
            raise TypeError(
                f"docker compose file '{docker_compose_file_path}' does not exist"
            )

        if rm_instances_files:
            shutil.rmtree(
                os.path.join(docker_compose_project_dir, "..", "_instances"),
                ignore_errors=True,
            )

        if self.clickhouse_binary_path:
            if self.use_specific_version:
                (
                    self.specific_clickhouse_binary_path,
                    self.clickhouse_specific_odbc_binary,
                ) = self.get_clickhouse_binary_from_docker_container(
                    self.use_specific_version
                )

                self.environ[
                    "CLICKHOUSE_SPECIFIC_BINARY"
                ] = self.specific_clickhouse_binary_path

                self.environ[
                    "CLICKHOUSE_SPECIFIC_ODBC_BINARY"
                ] = self.clickhouse_specific_odbc_binary

            if self.clickhouse_binary_path.startswith(("http://", "https://")):
                with Given(
                    "I download ClickHouse server binary",
                    description=f"{self.clickhouse_binary_path}",
                ):
                    self.clickhouse_binary_path = download_http_binary(
                        binary_source=self.clickhouse_binary_path
                    )

            elif self.clickhouse_binary_path.startswith("docker://"):
                if current().context.clickhouse_version is None:
                    parsed_version = parse_version_from_docker_path(
                        self.clickhouse_binary_path
                    )
                    if parsed_version:
                        if not (  # What case are we trying to catch here?
                            parsed_version.startswith(".")
                            or parsed_version.endswith(".")
                        ):
                            current().context.clickhouse_version = parsed_version

                (
                    self.clickhouse_binary_path,
                    self.clickhouse_odbc_bridge_binary_path,
                ) = self.get_clickhouse_binary_from_docker_container(
                    self.clickhouse_binary_path
                )

            if self.clickhouse_binary_path.endswith(".deb"):
                with Given(
                    "unpack deb package", description=f"{self.clickhouse_binary_path}"
                ):
                    self.clickhouse_binary_path = unpack_deb(
                        deb_binary_path=self.clickhouse_binary_path,
                        program_name="clickhouse",
                    )
                    unpack_deb(
                        deb_binary_path=self.clickhouse_binary_path,
                        program_name="clickhouse-odbc-bridge",
                    )

            self.clickhouse_binary_path = os.path.abspath(self.clickhouse_binary_path)

            with Shell() as bash:
                bash.timeout = 300
                bash(f"chmod +x {self.clickhouse_binary_path}")

        if self.keeper_binary_path:
            if self.keeper_binary_path.startswith(("http://", "https://")):
                with Given(
                    "I download ClickHouse Keeper server binary",
                    description=f"{self.keeper_binary_path}",
                ):
                    self.keeper_binary_path = download_http_binary(
                        binary_source=self.keeper_binary_path
                    )

            elif self.keeper_binary_path.startswith("docker://"):
                if getsattr(current().context, "keeper_version", None) is None:
                    parsed_version = parse_version_from_docker_path(
                        self.keeper_binary_path
                    )
                    if parsed_version:
                        if not (
                            parsed_version.startswith(".")
                            or parsed_version.endswith(".")
                        ):
                            current().context.keeper_version = parsed_version

                self.keeper_binary_path = self.get_binary_from_docker_container(
                    docker_image=self.keeper_binary_path,
                    container_binary_path="/usr/bin/clickhouse-keeper",
                )

            if self.keeper_binary_path.endswith(".deb"):
                with Given(
                    "unpack deb package", description=f"{self.keeper_binary_path}"
                ):
                    self.keeper_binary_path = unpack_deb(
                        deb_binary_path=self.keeper_binary_path,
                        program_name="clickhouse-keeper",
                    )

            self.keeper_binary_path = os.path.abspath(self.keeper_binary_path)

            with Shell() as bash:
                bash.timeout = 300
                bash(f"chmod +x {self.keeper_binary_path}")

        self.docker_compose += f' --ansi never --project-directory "{docker_compose_project_dir}" --file "{docker_compose_file_path}"'
        self.lock = threading.Lock()

    def get_clickhouse_binary_from_docker_container(
        self,
        docker_image,
        container_clickhouse_binary_path="/usr/bin/clickhouse",
        container_clickhouse_odbc_bridge_binary_path="/usr/bin/clickhouse-odbc-bridge",
        host_clickhouse_binary_path=None,
        host_clickhouse_odbc_bridge_binary_path=None,
    ):
        """Get clickhouse-server and clickhouse-odbc-bridge binaries
        from some Docker container.
        """
        docker_image = docker_image.split("docker://", 1)[-1]
        docker_container_name = str(uuid.uuid1())

        if host_clickhouse_binary_path is None:
            host_clickhouse_binary_path = os.path.join(
                tempfile.gettempdir(),
                f"{docker_image.rsplit('/', 1)[-1].replace(':', '_')}",
            )

        if host_clickhouse_odbc_bridge_binary_path is None:
            host_clickhouse_odbc_bridge_binary_path = (
                host_clickhouse_binary_path + "_odbc_bridge"
            )

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
                    f'docker cp "{docker_container_name}:{container_clickhouse_binary_path}" "{host_clickhouse_binary_path}"'
                )
                bash(
                    f'docker cp "{docker_container_name}:{container_clickhouse_odbc_bridge_binary_path}" "{host_clickhouse_odbc_bridge_binary_path}"'
                )
                bash(f'docker stop "{docker_container_name}"')

        with And("debug"):
            with Shell() as bash:
                bash.timeout = 300
                bash(f"ls -la {host_clickhouse_binary_path}")

        return host_clickhouse_binary_path, host_clickhouse_odbc_bridge_binary_path

    def get_binary_from_docker_container(
        self,
        docker_image,
        container_binary_path="/usr/bin/clickhouse",
        host_binary_path=None,
    ):
        """
        Get clickhouse-keeper binary from some Docker container.

        Args:
            docker_image: docker image name
            container_binary_path: path to link the binary in the container
            host_binary_path: path to store the binary on the host
        """

        docker_image = docker_image.split("docker://", 1)[-1]
        docker_container_name = str(uuid.uuid1())

        if host_binary_path is None:
            host_binary_path = os.path.join(
                tempfile.gettempdir(),
                f"{docker_image.rsplit('/', 1)[-1].replace(':', '_')}",
            )

        with Given(
            "I get ClickHouse Keeper binary from docker container",
            description=f"{docker_image}",
        ):
            with Shell() as bash:
                bash.timeout = 300
                bash(
                    f'set -o pipefail && docker run -d --name "{docker_container_name}" {docker_image} | tee'
                )
                bash(
                    f'docker cp "{docker_container_name}:{container_binary_path}" "{host_binary_path}"'
                )
                bash(f'docker stop "{docker_container_name}"')

        with And("debug"):
            with Shell() as bash:
                bash.timeout = 300
                bash(f"ls -la {host_binary_path}")

        return host_binary_path

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
                    c = self.control_shell(
                        f"{self.docker_compose} ps -q {node}", timeout=timeout
                    )
                    container_id = c.output.strip()
                    if c.exitcode == 0 and len(container_id) > 1:
                        break
                except IOError:
                    raise
                except ExpectTimeoutError:
                    self.close_control_shell()
                timeout = timeout - (time.time() - time_start)
                if timeout <= 0:
                    raise RuntimeError(
                        f"failed to get docker container id for the {node} service"
                    )
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

    def bash(self, node, timeout=300, command="bash --noediting"):
        """Returns thread-local bash terminal
        to a specific node.
        :param node: name of the service
        """
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
                                raise RuntimeError(
                                    f"failed to open bash to node {node}"
                                )

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
                            bash(f"cd {self.docker_compose_project_dir}", timeout=1000)
                            nodes = bash(
                                f"{self.docker_compose} ps --services"
                            ).output.split("\n")
                            debug(nodes)
                            for node in nodes:
                                with By(f"getting log for {node}"):
                                    log_path = f"../_instances"
                                    snode = bash(
                                        f"{self.docker_compose} logs {node} "
                                        f"> {log_path}/{node}.log",
                                        timeout=1000,
                                    )
                                    if snode.exitcode != 0:
                                        xfail(
                                            f"failed to get service log - exitcode {snode.exitcode}"
                                        )

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
                container_id = self.node_container_id(node, timeout=1)
            except RuntimeError:
                return

        r = self.command(
            node=None, command=f"docker inspect {container_id}", exitcode=0
        )
        mounts = json.loads(r.output)[0]["Mounts"]
        docker_exposed_dirs = [
            m["Destination"] for m in mounts if "_instances" in m["Source"]
        ]

        for exposed_dir in docker_exposed_dirs:
            self.command(
                node=node, command=f"chmod a+rwX -R {exposed_dir}", no_checks=True
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
                with Then("check --clickhouse-binary-path is specified"):
                    assert (
                        self.clickhouse_binary_path
                    ), "when running in local mode then --clickhouse-binary-path must be specified"
                with And("path should exist"):
                    assert os.path.exists(self.clickhouse_binary_path)

            with And("I set all the necessary environment variables"):
                self.environ["COMPOSE_HTTP_TIMEOUT"] = "600"
                self.environ[
                    "CLICKHOUSE_TESTS_SERVER_BIN_PATH"
                ] = self.clickhouse_binary_path
                self.environ[
                    "CLICKHOUSE_TESTS_ODBC_BRIDGE_BIN_PATH"
                ] = self.clickhouse_odbc_bridge_binary_path or os.path.join(
                    os.path.dirname(self.clickhouse_binary_path),
                    "clickhouse-odbc-bridge",
                )
                self.environ["CLICKHOUSE_TESTS_KEEPER_BIN_PATH"] = (
                    self.keeper_binary_path or ""
                )
                self.environ["CLICKHOUSE_TESTS_ZOOKEEPER_VERSION"] = (
                    self.zookeeper_version or ""
                )
                self.environ["CLICKHOUSE_TESTS_COORDINATOR"] = "keeper" if self.use_keeper else "zookeeper"
                self.environ["CLICKHOUSE_TESTS_DIR"] = self.configs_dir

            with And("I list environment variables to show their values"):
                self.command(None, "env | grep CLICKHOUSE")

        with Given("docker-compose"):
            max_attempts = 5
            max_up_attempts = 3

            for attempt in range(max_attempts):
                with When(f"attempt {attempt}/{max_attempts}"):
                    with By("pulling images for all the services"):
                        cmd = self.command(
                            None,
                            f"set -o pipefail && {self.docker_compose} pull 2>&1 | tee",
                            no_checks=True,
                            timeout=timeout,
                        )
                        if cmd.exitcode != 0:
                            continue

                    with And("checking if any containers are already running"):
                        self.command(
                            None, f"set -o pipefail && {self.docker_compose} ps | tee"
                        )

                    with And("executing docker-compose down just in case it is up"):
                        cmd = self.command(
                            None,
                            f"set -o pipefail && {self.docker_compose} down 2>&1 | tee",
                            no_checks=True,
                            timeout=timeout,
                        )
                        if cmd.exitcode != 0:
                            continue

                    with And("checking if any containers are still left running"):
                        self.command(
                            None, f"set -o pipefail && {self.docker_compose} ps | tee"
                        )

                    with And("executing docker-compose up"):
                        with By(
                            "creating a unique builder just in case docker-compose needs to build images"
                        ):
                            self.command(
                                None,
                                f"docker buildx create --use --bootstrap --node clickhouse-regression-builder",
                                exitcode=0,
                            )

                        for attempt in retries(count=max_up_attempts):
                            with attempt:
                                cmd = self.command(
                                    None,
                                    f"set -o pipefail && {self.docker_compose} up --renew-anon-volumes --force-recreate --build --timeout 600 -d 2>&1 | tee",
                                    timeout=timeout,
                                    exitcode=0,
                                )
                                assert "ERROR:" not in cmd.output, error(cmd.output)
                                if "is unhealthy" not in cmd.output:
                                    break

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
                            continue

                    if (
                        cmd.exitcode == 0
                        and "is unhealthy" not in cmd.output
                        and "Exit" not in ps_cmd.output
                    ):
                        break

            if (
                cmd.exitcode != 0
                or "is unhealthy" in cmd.output
                or "Exit" in ps_cmd.output
            ):
                fail("could not bring up docker-compose cluster")

        with Then("wait all nodes report healthy"):
            if self.use_zookeeper_nodes:
                for name in self.nodes["zookeeper"]:
                    self.node(name).wait_healthy()
                    if name.startswith("zookeeper"):
                        self.node(name).start_zookeeper()

            for name in self.nodes["clickhouse"]:
                self.node(name).wait_healthy()
                if name == "clickhouse-different-versions":
                    self.node(name).start_clickhouse(
                        thread_fuzzer=self.thread_fuzzer, check_version=False
                    )
                elif name.startswith("clickhouse"):
                    self.node(name).start_clickhouse(thread_fuzzer=self.thread_fuzzer)

            for name in self.nodes.get("keeper", []):
                if name.startswith("keeper"):
                    self.node(name).start_keeper()

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
        with (
            By("executing command", description=command, format_description=False)
            if steps
            else NullStep()
        ):
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
            with (
                Then(f"exitcode should be {exitcode}", format_name=False)
                if steps
                else NullStep()
            ):
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
    clickhouse_binary_path=None,
    clickhouse_odbc_bridge_binary_path=None,
    collect_service_logs=False,
    configs_dir=None,
    nodes=None,
    docker_compose="docker-compose --log-level ERROR",
    docker_compose_project_dir=None,
    docker_compose_file="docker-compose.yml",
    environ=None,
    keeper_binary_path=None,
    zookeeper_version=None,
    use_keeper=False,
    thread_fuzzer=False,
    use_zookeeper_nodes=False,
    use_specific_version=False,
):
    """Create docker compose cluster."""
    with Cluster(
        local=local,
        clickhouse_binary_path=clickhouse_binary_path,
        clickhouse_odbc_bridge_binary_path=clickhouse_odbc_bridge_binary_path,
        collect_service_logs=collect_service_logs,
        configs_dir=configs_dir,
        nodes=nodes,
        docker_compose=docker_compose,
        docker_compose_project_dir=docker_compose_project_dir,
        docker_compose_file=docker_compose_file,
        environ=environ,
        keeper_binary_path=keeper_binary_path,
        zookeeper_version=zookeeper_version,
        use_keeper=use_keeper,
        thread_fuzzer=thread_fuzzer,
        use_zookeeper_nodes=use_zookeeper_nodes,
        use_specific_version=use_specific_version,
    ) as cluster:
        yield cluster
