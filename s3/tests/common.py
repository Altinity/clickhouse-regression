import os
import base64
import tempfile
from contextlib import contextmanager

from minio import Minio
from testflows.connect import Shell
from testflows.combinatorics import combinations

from helpers.common import *
from helpers.queries import sync_replica, get_row_count

Config = namedtuple("Config", "content path name uid preprocessed_name")


def add_config(
    config,
    timeout=60,
    restart=False,
    modify=False,
    nodes=None,
    user=None,
    wait_healthy=True,
    check_preprocessed=True,
):
    """Add dynamic configuration file to ClickHouse.

    :param node: node
    :param config: configuration file description
    :param timeout: timeout, default: 20 sec
    """
    cluster = current().context.cluster
    if nodes is None:
        nodes = [cluster.node(node) for node in cluster.nodes["clickhouse"]]

    def check_preprocessed_config_is_updated(after_removal=False):
        """Check that preprocessed config is updated."""
        started = time.time()
        command = f"cat /var/lib/clickhouse/preprocessed_configs/{config.preprocessed_name} | grep {config.uid}{' > /dev/null' if not settings.debug else ''}"

        while time.time() - started < timeout:
            exitcode = node.command(command, steps=False, no_checks=True).exitcode
            if after_removal:
                if exitcode == 1:
                    break
            else:
                if exitcode == 0:
                    break
            time.sleep(1)

        if settings.debug:
            node.command(
                f"cat /var/lib/clickhouse/preprocessed_configs/{config.preprocessed_name}"
            )

        if after_removal:
            assert exitcode == 1, error()
        else:
            assert exitcode == 0, error()

    def wait_for_config_to_be_loaded(user=None):
        """Wait for config to be loaded."""
        if restart:
            with When("I close terminal to the node to be restarted"):
                bash.close()

            with And("I stop ClickHouse to apply the config changes"):
                node.stop_clickhouse(safe=False)

            with And("I get the current log size"):
                cmd = node.cluster.command(
                    None,
                    f"stat -c %s {cluster.environ['CLICKHOUSE_TESTS_DIR']}/_instances/{node.name}/logs/clickhouse-server.log",
                )
                logsize = cmd.output.split(" ")[0].strip()

            with And("I start ClickHouse back up"):
                node.start_clickhouse(
                    user=user, wait_healthy=wait_healthy, timeout=timeout
                )

            with Then("I tail the log file from using previous log size as the offset"):
                bash.prompt = bash.__class__.prompt
                bash.open()
                bash.send(
                    f"tail -c +{logsize} -f /var/log/clickhouse-server/clickhouse-server.log"
                )

        with Then("I wait for config reload message in the log file"):
            if restart:
                bash.expect(
                    f"ConfigReloader: Loaded config '/etc/clickhouse-server/config.xml', performed update on configuration",
                    timeout=timeout,
                )
            else:
                bash.expect(
                    f"ConfigReloader: Loaded config '/etc/clickhouse-server/{config.preprocessed_name}', performed update on configuration",
                    timeout=timeout,
                )

    try:
        for node in nodes:
            with Given(f"{config.name}"):
                if settings.debug:
                    with When("I output the content of the config"):
                        debug(config.content)

                with node.cluster.shell(node.name) as bash:
                    bash.expect(bash.prompt)
                    bash.send(
                        "tail -v -n 0 -f /var/log/clickhouse-server/clickhouse-server.log"
                    )
                    # make sure tail process is launched and started to follow the file
                    bash.expect("<==")
                    bash.expect("\n")

                    with When("I add the config", description=config.path):
                        command = (
                            f"cat <<HEREDOC > {config.path}\n{config.content}\nHEREDOC"
                        )
                        node.command(command, steps=False, exitcode=0)

                    if check_preprocessed:
                        with Then(
                            f"{config.preprocessed_name} should be updated",
                            description=f"timeout {timeout}",
                        ):
                            check_preprocessed_config_is_updated()

                        with And("I wait for config to be reloaded"):
                            wait_for_config_to_be_loaded(user=user)
        yield

    finally:
        for node in nodes:
            if not modify:
                with Finally(f"I remove {config.name}"):
                    with node.cluster.shell(node.name) as bash:
                        bash.expect(bash.prompt)
                        bash.send(
                            "tail -v -n 0 -f /var/log/clickhouse-server/clickhouse-server.log"
                        )
                        # make sure tail process is launched and started to follow the file
                        bash.expect("<==")
                        bash.expect("\n")

                        with By("removing the config file", description=config.path):
                            node.command(f"rm -rf {config.path}", exitcode=0)

                        with Then(
                            f"{config.preprocessed_name} should be updated",
                            description=f"timeout {timeout}",
                        ):
                            check_preprocessed_config_is_updated(after_removal=True)

                        with And("I wait for config to be reloaded"):
                            wait_for_config_to_be_loaded()


def create_export_partition_config(
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="enable_experimental_export_merge_tree_partition.xml",
):
    """Create export partition config content.."""
    entries = {"enable_experimental_export_merge_tree_partition_feature": "1"}

    return create_xml_config_content(
        entries, config_file=config_file, config_d_dir=config_d_dir
    )


@TestStep(Given)
def enable_export_partition(
    self,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="enable_experimental_export_merge_tree_partition.xml",
    timeout=300,
    restart=True,
    config=None,
    nodes=None,
):
    """Add configuration which enables export partition."""
    if config is None:
        config = create_export_partition_config(config_d_dir, config_file)

    return add_config(config, restart=restart, nodes=nodes, timeout=timeout)


def create_s3_storage_config_content(
    disks,
    policies,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="storage.xml",
):
    """Create S3 storage configuration content."""
    entries = {"storage_configuration": {"disks": [disks], "policies": policies}}

    return create_xml_config_content(
        entries, config_file=config_file, config_d_dir=config_d_dir
    )


def create_s3_endpoint_config_content(
    endpoints,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="s3_endpoints.xml",
):
    """Create S3 endpoints configuration content."""
    entries = {"s3": endpoints}

    return create_xml_config_content(
        entries, config_file=config_file, config_d_dir=config_d_dir
    )


@TestStep(Given)
def s3_storage(
    self,
    disks=None,
    policies=None,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="storage.xml",
    timeout=300,
    restart=False,
    config=None,
    nodes=None,
):
    """Add S3 storage disk and policy configurations."""
    if disks is None:
        disks = {}
    if policies is None:
        policies = {}

    if config is None:
        config = create_s3_storage_config_content(
            disks, policies, config_d_dir, config_file
        )
    return add_config(config, restart=restart, nodes=nodes, timeout=timeout)


@TestStep(Given)
def named_s3_credentials(
    self, access_key_id, secret_access_key, restart=False, nodes=None, timeout=60
):
    """Add S3 connection configuration as a named collection."""
    config = create_xml_config_content(
        entries={
            "named_collections": {
                "s3_credentials": {
                    "access_key_id": access_key_id,
                    "secret_access_key": secret_access_key,
                }
            }
        },
        config_file="s3_credentials.xml",
    )
    return add_config(config, restart=restart, nodes=nodes, timeout=timeout)


@contextmanager
def s3_endpoints(
    endpoints,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="s3_endpoints.xml",
    timeout=60,
    restart=False,
    config=None,
    nodes=None,
):
    """Add S3 endpoints configuration."""
    if config is None:
        config = create_s3_endpoint_config_content(
            endpoints, config_d_dir=config_d_dir, config_file=config_file
        )
    return add_config(config, restart=restart, nodes=nodes)


def invalid_s3_storage_config(
    disks, policies, message=None, tail=30, timeout=30, config=None
):
    """Check that ClickHouse errors when trying to load invalid S3 storage configuration file."""
    cluster = current().context.cluster
    node = current().context.node

    if config is None:
        config = create_s3_storage_config_content(disks, policies)

    if message is None:
        message = f"Exception: Failed to merge config with '{config.path}'"

    try:
        with Given("I prepare the error log by writting empty lines into it"):
            node.command(
                'echo -e "%s" > /var/log/clickhouse-server/clickhouse-server.err.log'
                % ("-\\n" * tail)
            )

        with Then("Get the current log size"):
            cmd = node.command(
                f"stat -c %s /var/log/clickhouse-server/clickhouse-server.err.log"
            )
            start_logsize = cmd.output.split(" ")[0].strip()

        with When("I add the config", description=config.path):
            command = f"cat <<HEREDOC > {config.path}\n{config.content}\nHEREDOC"
            node.command(command, steps=False, exitcode=0)

        with Then(
            f"{config.preprocessed_name} should be updated",
            description=f"timeout {timeout}",
        ):
            started = time.time()
            command = f"cat /var/lib/clickhouse/preprocessed_configs/{config.preprocessed_name} | grep {config.uid}{' > /dev/null' if not settings.debug else ''}"
            for attempt in retries(timeout=timeout, delay=1):
                with attempt:
                    cmd = node.command(command, steps=False, exitcode=0)

        with When("I restart ClickHouse to apply the config changes"):
            node.restart_clickhouse(safe=False, wait_healthy=False)

        with And("Get the current log size at the end of the test"):
            cmd = node.command(
                f"stat -c %s /var/log/clickhouse-server/clickhouse-server.err.log"
            )
            end_logsize = cmd.output.split(" ")[0].strip()

        with Then("the error log should contain the expected error message"):
            command = f"tail -c +{start_logsize} /var/log/clickhouse-server/clickhouse-server.err.log | head -c {int(end_logsize) - int(start_logsize)}"
            for attempt in retries(timeout=timeout, delay=1):
                with attempt:
                    cmd = node.command(
                        command, steps=False, message=message, exitcode=0
                    )

    finally:
        with When(f"I remove {config.name}"):
            with By("removing invalid configuration file"):
                node.command(f"rm -rf {config.path}", timeout=timeout, exitcode=0)

            with And("restarting the node"):
                node.restart_clickhouse(safe=False)


def create_s3_credentials_config_content(
    endpoints, config_d_dir="/etc/clickhouse-server/config.d", config_file="s3.xml"
):
    """Create S3 server-level environment credentials configuration content."""
    uid = getuid()
    path = os.path.join(config_d_dir, config_file)
    name = config_file

    root = xmltree.fromstring("<yandex><s3></s3></yandex>")
    xml_s3 = root.find("s3")
    xml_s3.append(xmltree.Comment(text=f"S3 environment credentials {uid}"))

    for _name, endpoint in list(endpoints.items()):
        xml_endpoint = xmltree.Element(_name)
        for key, value in list(endpoint.items()):
            xml_append(xml_endpoint, key, value)
        xml_s3.append(xml_endpoint)

    xml_indent(root)
    content = str(
        xmltree.tostring(root, short_empty_elements=False, encoding="utf-8"), "utf-8"
    )

    return Config(content, path, name, uid, "config.xml")


@contextmanager
def s3_env_credentials(
    endpoints,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="s3.xml",
    timeout=60,
    restart=False,
    config=None,
    nodes=None,
):
    """Add S3 server-level environment credentials configuration."""
    if config is None:
        config = create_s3_credentials_config_content(
            endpoints, config_d_dir, config_file
        )
    return add_config(config, restart=restart, nodes=nodes)


def create_remote_host_filter_config_content(
    urls,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="remote_host_filter.xml",
    timeout=60,
    restart=False,
    config=None,
):
    """Create S3 remote host filter configuration content."""
    uid = getuid()
    path = os.path.join(config_d_dir, config_file)
    name = config_file

    root = xmltree.fromstring(
        "<yandex><remote_url_allow_hosts></remote_url_allow_hosts></yandex>"
    )
    xml_rhf = root.find("remote_url_allow_hosts")
    xml_rhf.append(xmltree.Comment(text=f"Remote Host Filter configuration {uid}"))

    for key, value in list(urls.items()):
        xml_append(xml_rhf, key, value)

    xml_indent(root)
    content = str(
        xmltree.tostring(root, short_empty_elements=False, encoding="utf-8"), "utf-8"
    )

    return Config(content, path, name, uid, "config.xml")


@contextmanager
def remote_host_filter_config(
    urls,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="remote_host_filter.xml",
    timeout=60,
    restart=False,
    config=None,
):
    """Add S3 remote host filter configuration."""
    if config is None:
        config = create_remote_host_filter_config_content(
            urls, config_d_dir, config_file
        )
    return add_config(config, restart=restart)


def create_s3_max_redirects_config_content(
    profiles,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="s3_max_redirects.xml",
    timeout=60,
    restart=False,
    config=None,
):
    """Create S3 max redirects configuration content."""
    uid = getuid()
    path = os.path.join(config_d_dir, config_file)
    name = config_file

    root = xmltree.fromstring("<yandex><profiles></profiles></yandex>")
    xml_s3_max = root.find("profiles")
    xml_s3_max.append(xmltree.Comment(text=f"S3 max redirects configuration {uid}"))

    for _name, profile in list(profiles.items()):
        xml_profile = xmltree.Element(_name)
        for key, value in list(profile.items()):
            xml_append(xml_profile, key, value)
        xml_s3_max.append(xml_profile)

    xml_indent(root)
    content = str(
        xmltree.tostring(root, short_empty_elements=False, encoding="utf-8"), "utf-8"
    )

    return Config(content, path, name, uid, "config.xml")


@contextmanager
def s3_max_redirects(
    profiles,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="s3_max_redirects.xml",
    timeout=60,
    restart=False,
    config=None,
    nodes=None,
):
    """Add S3 max redirects configuration."""
    if config is None:
        config = create_s3_max_redirects_config_content(
            profiles, config_d_dir, config_file
        )
    return add_config(config, restart=restart, nodes=nodes)


def create_mergetree_config_content(
    settings,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="merge_tree.xml",
    timeout=60,
    restart=False,
    config=None,
):
    """Create MergeTree configuration content."""
    uid = getuid()
    path = os.path.join(config_d_dir, config_file)
    name = config_file

    root = xmltree.fromstring("<yandex><merge_tree></merge_tree></yandex>")
    xml_merge_tree = root.find("merge_tree")
    xml_merge_tree.append(xmltree.Comment(text=f"MergeTree configuration {uid}"))

    for key, value in list(settings.items()):
        xml_append(xml_merge_tree, key, value)

    xml_indent(root)
    content = str(
        xmltree.tostring(root, short_empty_elements=False, encoding="utf-8"), "utf-8"
    )

    return Config(content, path, name, uid, "config.xml")


@TestStep(Given)
def mergetree_config(
    self,
    settings,
    config_d_dir="/etc/clickhouse-server/config.d",
    config_file="merge_tree.xml",
    timeout=60,
    restart=True,
    config=None,
    nodes=None,
):
    """Add MergeTree configuration."""
    if config is None:
        config = create_mergetree_config_content(settings, config_d_dir, config_file)
    return add_config(config, restart=restart, nodes=nodes)


@contextmanager
def subshell(bash, command, name, prompt=None):
    def spawn(command):
        bash.send(command)
        return bash.child

    def close():
        bash.send("exit")
        bash.expect(bash.prompt)
        bash("")

    child_close = bash.child.close
    child_timeout = bash.child.timeout
    child_eol = bash.child.eol

    try:
        bash.child.close = close

        with Shell(spawn=spawn, command=command, name=name, prompt=prompt) as sub_shell:
            yield sub_shell
    finally:
        bash.child.close = child_close
        bash.child.timeout = child_timeout
        bash.child.eol = child_eol


@TestStep(Given)
def ssh_terminal(
    self,
    host,
    username,
    password=None,
    command="{client} {username}@{host} {options}",
    client="ssh",
    options=None,
    port=None,
    prompt=r"[\$#] ",
    new_prompt="bash# ",
    rsa_password=None,
):
    """Open ssh terminal to a remote host."""
    node = current().context.node

    if options is None:
        options = []

    if port is not None:
        options.append(f"-p {port}")

    with node.cluster.shell(node.name) as bash:
        command = command.format(
            client=client,
            username=username,
            host=host,
            options=" ".join(options).strip(),
        )

        bash.send(command)

        while True:
            c = bash.expect(
                r"(Enter passphrase for key)|(Last login)|"
                r"(Could not resolve hostname)|(Connection refused)|"
                r"(Are you sure you want to continue connecting)"
            )

            if c.group() == "Enter passphrase for key":
                bash.send(rsa_password, delay=0.5)
                continue

            if c.group() == "Are you sure you want to continue connecting":
                bash.send("yes", delay=0.5)
                continue

            break

        if c.group() == "Last login":
            bash.expect(prompt)
        else:
            raise IOError(c.group())

        bash.send("\r")

        def spawn(command):
            bash.send(" ".join(command))
            return bash.child

        def close():
            bash.send("exit")

        child_close = bash.child.close
        child_timeout = bash.child.timeout
        child_eol = bash.child.eol

        try:
            bash.child.close = close

            with Shell(spawn=spawn, name=host, prompt=prompt, command=[""]) as ssh_bash:
                yield ssh_bash
        finally:
            bash.child.close = child_close
            bash.child.timeout = child_timeout
            bash.child.eol = child_eol


@contextmanager
def change_max_single_part_upload_size(node, size):
    setting_s3_max_single_part_upload_size = ("s3_max_single_part_upload_size", size)
    default_query_settings = None

    try:
        with Given(
            "I add s3_max_single_part_upload_size to the default query settings"
        ):
            default_query_settings = getsattr(
                current().context, "default_query_settings", []
            )
            default_query_settings.append(setting_s3_max_single_part_upload_size)

        yield
    finally:
        with Finally(
            "I remove s3_max_single_part_upload_size from the default query settings"
        ):
            if default_query_settings:
                try:
                    default_query_settings.pop(
                        default_query_settings.index(
                            setting_s3_max_single_part_upload_size
                        )
                    )
                except ValueError:
                    pass


def get_used_disks_for_table(node, name, step=When, steps=True):
    def get_used_disks():
        sql = f"select disk_name from system.parts where table == '{name}' and active=1 order by modification_time FORMAT TabSeparated"
        return node.query(sql).output.strip().split("\n")

    if not steps:
        return get_used_disks()
    else:
        with step(f"I get used disks for table '{name}'"):
            return get_used_disks()


def get_path_for_part_from_part_log(node, table, part_name, step=When):
    with step("I flush logs"):
        node.query("SYSTEM FLUSH LOGS")
    with And(f"get path_on_disk for part {part_name}"):
        path = node.query(
            f"SELECT path_on_disk FROM system.part_log WHERE table = '{table}' "
            f" AND part_name = '{part_name}' ORDER BY event_time DESC LIMIT 1 FORMAT TabSeparated"
        ).output
    return path.strip()


def get_paths_for_partition_from_part_log(node, table, partition_id, step=When):
    with step("I flush logs"):
        node.query("SYSTEM FLUSH LOGS")
    with And(f"get path_on_disk for partition id {partition_id}"):
        paths = node.query(
            f"SELECT path_on_disk FROM system.part_log WHERE table = '{table}'"
            f" AND partition_id = '{partition_id}' ORDER BY event_time DESC FORMAT TabSeparated"
        ).output
    return paths.strip().split("\n")


def get_random_string(cluster, length, steps=True, *args, **kwargs):
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8") as fd:
        cluster.command(
            None,
            rf"cat /dev/urandom | tr -dc 'A-Za-z0-9#$&()*+,-./:;<=>?@[\]^_~' | head -c {length} > {fd.name}",
            steps=steps,
            no_checks=True,
            *args,
            **kwargs,
        )
        fd.seek(0)
        random_string = fd.read()
        assert len(random_string) == length
        return random_string


@TestStep(When)
def insert_data(self, name, number_of_mb, start=0, node=None):
    if node is None:
        node = current().context.node

    values = ",".join(
        f"({x})"
        for x in range(start, int((1024 * 1024 * number_of_mb) / 8) + start + 1)
    )
    node.query(f"INSERT INTO {name} VALUES {values}")


@TestStep(Given)
def insert_random(
    self,
    node,
    table_name,
    columns: str,
    rows: int = 1000000,
    settings: str = None,
    **kwargs,
):
    """Insert random data to a table."""

    if settings:
        settings = "SETTINGS " + settings
    else:
        settings = ""

    return node.query(
        f"INSERT INTO {table_name} SELECT * FROM generateRandom('{columns}') LIMIT {rows} {settings}",
        exitcode=0,
        **kwargs,
    )


@TestStep(Then)
def check_query(self, num, query, expected):
    node = current().context.node

    with By(f"executing query {num}", description=query):
        r = node.query(query).output.strip()
        with Then(f"result should match the expected", description=expected):
            assert r == expected, error()


@TestStep(Then)
def check_query_node(self, node, num, query, expected):
    node = current().context.node

    with By(f"executing query {num}", description=query):
        r = node.query(query).output.strip()
        with Then(f"result should match the expected", description=expected):
            assert r == expected, error()


def get_s3_file_content(cluster, bucket, filename, decode=True):
    """Return content of a given s3 file as a string."""

    data = cluster.minio_client.get_object(bucket, filename)
    data_str = b""
    for chunk in data.stream():
        data_str += chunk
    if decode:
        return data_str.decode()

    return data_str


def run_query(instance, query, stdin=None, settings=None):
    """Run a query on the specified ClickHouse node."""

    if stdin:
        stdin_file = tempfile.TemporaryFile(mode="w+")
        stdin_file.write(stdin)
        stdin_file.seek(0)

        result = instance.command(
            f'echo -e "{stdin}" | clickhouse client --query="{query}"',
            steps=False,
            no_checks=True,
        )
    else:
        result = instance.query(
            query, steps=False, raise_on_exception=True
        ).output.strip()

    return result


@TestStep(Given)
def get_bucket_size(
    self, name=None, prefix=None, key_id=None, access_key=None, minio_enabled=None
):
    """Get the size of an blob storage bucket with the specified prefix."""

    if self.context.storage == "azure":
        account_name = self.context.azure_account_name
        container_name = self.context.azure_container_name
        with By(
            "querying with az cli",
            description=f"account: {account_name}, container: {container_name}",
        ):
            cmd = (
                f"AZURE_STORAGE_KEY={self.context.azure_account_key} "
                f'az storage blob list --container-name {container_name} --account-name {account_name} --num-results "*" --query "[].properties.contentLength" --output json '
                "| jq -M '. | add'"
            )
            result = self.context.cluster.command(
                "azure-client", cmd, steps=False, no_checks=True
            )

            return int(result.output)

    if name is None:
        name = self.context.bucket_name

    if prefix is None:
        prefix = self.context.bucket_path

    if key_id is None:
        key_id = self.context.access_key_id

    if access_key is None:
        access_key = self.context.secret_access_key

    if minio_enabled is None:
        minio_enabled = getattr(self.context, "storage", None) == "minio" or getattr(
            self.context, "minio_enabled", False
        )

    if minio_enabled:
        with By("querying with minio client"):
            minio_client = self.context.cluster.minio_client

            objects = minio_client.list_objects(
                bucket_name=name, prefix=prefix, recursive=True
            )
            return sum(obj._size for obj in objects)

    with By("querying with aws cli", description=f"bucket: {name}, prefix: {prefix}"):
        aws = "aws"

        if self.context.storage == "gcs":
            aws = f"AWS_ACCESS_KEY_ID={self.context.access_key_id} AWS_SECRET_ACCESS_KEY={self.context.secret_access_key} aws --endpoint-url=https://storage.googleapis.com/"

        cmd = (
            f"{aws} s3 ls s3://{name}/{prefix} --recursive --summarize | "
            "grep -Po --color=never '(?<=Total Size: )(.+)'"
        )
        result = self.context.cluster.command("aws", cmd, steps=False, no_checks=True)
        return int(result.output)


@TestStep(Then)
def check_bucket_size(
    self, expected_size, tolerance=0, name=None, prefix=None, minio_enabled=None
):
    current_size = get_bucket_size(
        name=name,
        prefix=prefix,
        minio_enabled=minio_enabled,
        access_key=self.context.secret_access_key,
        key_id=self.context.access_key_id,
    )
    assert abs(current_size - expected_size) <= tolerance, error()


@TestStep(When)
def get_stable_bucket_size(
    self,
    name=None,
    prefix=None,
    delay=15,
    timeout=300,
):
    """Get the size of an s3 bucket, waiting until the size hasn't changed for [delay] seconds."""

    with By("checking the current bucket size"):
        size_previous = get_bucket_size(
            name=name,
            prefix=prefix,
        )
    debug(size_previous)
    start_time = time.time()
    while True:
        with And(f"waiting {delay}s"):
            time.sleep(delay)
        with And("checking the current bucket size"):
            size = get_bucket_size(
                name=name,
                prefix=prefix,
            )
        with And(f"checking if current:{size} == previous:{size_previous}"):
            if size_previous == size:
                break
        size_previous = size

        with And("checking timeout"):
            assert time.time() - start_time <= timeout, error(
                f"Bucket size did not stabilize in {timeout}s"
            )
    debug(start_time)
    return size


@TestStep(Then)
def check_stable_bucket_size(
    self,
    expected_size,
    name=None,
    prefix=None,
    tolerance=0,
    delay=15,
):
    """Assert the size of an s3 bucket, waiting until the size hasn't changed for [delay] seconds."""

    current_size = get_stable_bucket_size(
        name=name,
        prefix=prefix,
        delay=delay,
    )
    assert abs(current_size - expected_size) <= tolerance, error()


@TestStep(Given)
def start_minio(
    self,
    uri="localhost:9001",
    access_key="minio",
    secret_key="minio123",
    timeout=30,
    secure=False,
    cleanup=True,
):
    minio_client = Minio(
        uri, access_key=access_key, secret_key=secret_key, secure=secure
    )
    start = time.time()
    while time.time() - start < timeout:
        try:
            if cleanup:
                buckets_to_delete = minio_client.list_buckets()

                for bucket in buckets_to_delete:
                    objects = minio_client.list_objects(bucket.name, recursive=True)
                    object_names = [o.object_name for o in objects]
                    for name in object_names:
                        minio_client.remove_object(bucket.name, name)

                buckets = ["root", "root2"]
                self.context.cluster.minio_bucket = "root"

                for bucket in buckets:
                    if minio_client.bucket_exists(bucket):
                        objects = minio_client.list_objects(bucket, recursive=True)
                        object_names = [o.object_name for o in objects]
                        for name in object_names:
                            minio_client.remove_object(bucket, name)
                        minio_client.remove_bucket(bucket)
                    minio_client.make_bucket(bucket)

                self.context.cluster.minio_client = minio_client
                return
            else:
                return
        except Exception as ex:
            time.sleep(1)

    raise Exception("Can't wait Minio to start")


@TestStep(Given)
def s3_table(self, table_name, policy, node=None):
    """Create s3 table using provided policy."""
    db_engine = "Ordinary" if check_clickhouse_version("<22.7")(self) else "Atomic"
    if node is None:
        node = self.context.node

    try:
        with When("I create an Ordinary engine database"):
            node.query(f"CREATE DATABASE IF NOT EXISTS s3 ENGINE = {db_engine}")

        with When(f"I create the table {table_name}"):
            node.query(
                f"""
                CREATE TABLE {table_name} (id UInt64, x UInt64)
                ENGINE = MergeTree()
                PARTITION BY id
                ORDER BY id
                SETTINGS storage_policy='{policy}'
                """
            )
        yield

    finally:
        with Finally(f"I remove the table {table_name}"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")

        with And("I drop the database"):
            node.query("DROP DATABASE IF EXISTS s3 SYNC")


@TestStep(Given)
def attach_table(self, table_name, policy, node=None):
    """Attach an s3 table using provided policy."""
    db_engine = "Ordinary" if check_clickhouse_version("<22.7")(self) else "Atomic"

    if node is None:
        node = self.context.node

    try:
        with When("I create an Ordinary engine database"):
            node.query(f"CREATE DATABASE IF NOT EXISTS s3 ENGINE = {db_engine}")

        with And(f"I attach the table {table_name}"):
            node.query(
                f"""
                ATTACH TABLE {table_name} (id UInt64, x UInt64)
                ENGINE = MergeTree()
                PARTITION BY id
                ORDER BY id
                SETTINGS storage_policy='{policy}'
                """
            )

        yield

    finally:
        with Finally(f"I remove the table {table_name}"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")

        with And("I drop the database"):
            node.query("DROP DATABASE IF EXISTS s3 SYNC")


@TestStep(When)
def drop_s3_metadata(self, disk, node=None):
    """Drop s3 metadata."""
    if node is None:
        node = self.context.node

    node.command(f"rm -rf /var/lib/clickhouse/disks/{disk}/*")


@TestStep(Then)
def create_restore_file(
    self, disk, revision=None, bucket=None, path=None, detached=None, node=None
):
    """Create a restore file."""
    if node is None:
        node = self.context.node

    node.command(f"mkdir -p /var/lib/clickhouse/disks/{disk}/")
    node.command(f"touch /var/lib/clickhouse/disks/{disk}/restore")

    add_restore_option = "echo -en '{}={}\n' >> /var/lib/clickhouse/disks/{}/restore"
    if revision is not None:
        node.command(add_restore_option.format("revision", revision, disk))
    if bucket is not None:
        node.command(add_restore_option.format("source_bucket", bucket, disk))
    if path is not None:
        node.command(add_restore_option.format("source_path", path, disk))
    if detached is not None:
        node.command(add_restore_option.format("detached", "true", disk))


@TestStep(When)
def remove_restore(self, disk, node=None):
    """Remove an existing restore file."""
    if node is None:
        node = self.context.node

    with When("I remove the restore file"):
        node.command(f"rm -rf /var/lib/clickhouse/disks/{disk}/restore")


@TestStep(When)
def get_revision_counter(self, table_name, backup_number, disk, node=None):
    """Return the revision counter."""
    if node is None:
        node = self.context.node

    with When("I create a backup"):
        node.query(f"ALTER TABLE {table_name} FREEZE")

    return int(
        node.command(
            f"cat /var/lib/clickhouse/disks/{disk}/shadow/{backup_number}/revision.txt"
        ).output
    )


@TestStep(Given)
def cleanup(self, storage="minio", disk="external", s3_path=None):
    """Clean up shadow directory, s3 metadata, and minio if necessary."""
    cluster = self.context.cluster

    for node in cluster.nodes["clickhouse"]:
        node = cluster.node(node)

        node.command(f"rm -rf /var/lib/clickhouse/disks/{disk}/*")
        node.command("rm -rf /var/lib/clickhouse/shadow/*")

    if storage == "minio":
        minio_client = self.context.cluster.minio_client
        for obj in list(
            minio_client.list_objects(cluster.minio_bucket, recursive=True)
        ):
            if str(obj.object_name).find(".SCHEMA_VERSION") != -1:
                continue
            minio_client.remove_object(cluster.minio_bucket, obj.object_name)

    if storage == "aws_s3" and s3_path is not None:
        current().context.cluster.command(
            "aws",
            f"aws s3 rm s3://{self.context.bucket_name}/data/{s3_path} --recursive",
        )


@TestStep(Given)
def aws_s3_setup_second_bucket(self, region, bucket):
    """Create a second bucket."""
    cluster = self.context.cluster

    try:
        with When("I create a new bucket"):
            cluster.command(
                "aws", f"aws s3api create-bucket --bucket {bucket}2 --region {region}"
            )

    finally:
        with Finally("I remove everything from the bucket", flags=TE):
            cluster.command("aws", f"aws s3 rm s3://{bucket} --recursive")

        with And("I remove the second bucket", flags=TE):
            cluster.command(
                "aws", f"aws s3api delete-bucket --bucket {bucket} --region {region}"
            )


@TestStep(Given)
def temporary_bucket_path(
    self,
    bucket_name=None,
    bucket_prefix=None,
    access_key_id=None,
    secret_access_key=None,
    storage=None,
    aws_region=None,
):
    """
    Return a temporary bucket sub-path which will be cleaned up.
    This is returned without the given prefix for compatibility with the
    uri defined in s3/regression.py, which already includes the prefix.

    Example:

        with Given("a temporary s3 path"):
            temp_s3_path = temporary_bucket_path(
                bucket_name=self.context.bucket_name,
                bucket_prefix=f"{bucket_prefix}/my_test_prefix",
            )

            temp_uri = f"{uri}my_test_prefix/{temp_s3_path}"

            temp_bucket_path = f"{bucket_prefix}/my_test_prefix/{temp_s3_path}"

    """
    if storage is None:
        storage = self.context.storage

    assert storage in [
        "minio",
        "aws_s3",
        "gcs",
    ], f"Unsupported storage: {storage}"

    if bucket_name is None:
        bucket_name = self.context.bucket_name

    if bucket_prefix is None:
        bucket_prefix = self.context.bucket_prefix

    if access_key_id is None:
        access_key_id = self.context.access_key_id
    if secret_access_key is None:
        secret_access_key = self.context.secret_access_key

    try:
        with When("I create a temporary bucket path"):
            temp_path = f"tmp_{getuid()}"
            yield temp_path

    finally:
        with Finally("remove the temporary bucket path"):
            if storage == "minio":
                minio_client = self.context.cluster.minio_client
                for obj in list(minio_client.list_objects(bucket_name, recursive=True)):
                    if str(obj.object_name).find(".SCHEMA_VERSION") != -1:
                        continue
                    if obj.object_name.startswith(f"{bucket_prefix}/{temp_path}"):
                        minio_client.remove_object(bucket_name, obj.object_name)

            elif storage == "aws_s3":
                cluster = current().context.cluster

                cmd = f"aws s3 rm s3://{bucket_name}/{bucket_prefix}/{temp_path} --recursive"
                if aws_region:
                    cmd += f" --region {aws_region}"
                if secret_access_key:
                    cmd = f"AWS_SECRET_ACCESS_KEY={secret_access_key} {cmd}"
                if access_key_id:
                    cmd = f"AWS_ACCESS_KEY_ID={access_key_id} {cmd}"

                cluster.command("aws", cmd)

            elif storage == "gcs":
                cluster = current().context.cluster
                cluster.command(
                    "aws",
                    (
                        f"AWS_ACCESS_KEY_ID={access_key_id} AWS_SECRET_ACCESS_KEY={secret_access_key}"
                        f" aws s3 rm s3://{bucket_name}/{bucket_prefix}/{temp_path} --recursive"
                        " --endpoint=https://storage.googleapis.com/"
                    ),
                )


@contextmanager
def allow_s3_truncate(node):
    """Enable S3 truncate on insert setting."""
    setting = ("s3_truncate_on_insert", 1)
    default_query_settings = None

    try:
        if check_clickhouse_version(">=22.3")(current()):
            with Given("I add s3_truncate_on_insert to the default query settings"):
                default_query_settings = getsattr(
                    current().context, "default_query_settings", []
                )
                default_query_settings.append(setting)
        yield
    finally:
        if check_clickhouse_version(">=22.3")(current()):
            with Finally(
                "I remove s3_truncate_on_insert from the default query settings"
            ):
                if default_query_settings:
                    try:
                        default_query_settings.pop(
                            default_query_settings.index(setting)
                        )
                    except ValueError:
                        pass


def s3_type_disk_parameters(uri, access_key_id, secret_access_key, disk_settings=None):
    """Return dict of disk parameters for an S3 disk."""

    disk_settings = disk_settings or {}
    return {
        "type": "s3",
        "endpoint": uri,
        "access_key_id": access_key_id,
        "secret_access_key": secret_access_key,
        **disk_settings,
    }


def azure_blob_type_disk_parameters(
    storage_account_url, container_name, account_name, account_key, disk_settings=None
):
    """Return dict of disk parameters for an Azure Blob Storage disk."""

    disk_settings = disk_settings or {}
    return {
        "type": "azure_blob_storage",
        "storage_account_url": storage_account_url,
        "container_name": container_name,
        "account_name": account_name,
        "account_key": account_key,
        **disk_settings,
    }


@TestStep(Given)
def default_s3_and_local_disk(
    self, restart=True, uri=None, policy_name="default_and_external", disk_settings=None
):
    """Default settings for s3 and local disks."""

    disk_settings = disk_settings or {}

    with Given("parameters for an external disk"):
        if self.context.storage == "azure":
            external_disk = azure_blob_type_disk_parameters(
                self.context.azure_storage_account_url,
                self.context.azure_container_name,
                self.context.azure_account_name,
                self.context.azure_account_key,
                disk_settings,
            )
        else:
            uri = uri or self.context.uri
            external_disk = s3_type_disk_parameters(
                uri,
                self.context.access_key_id,
                self.context.secret_access_key,
                disk_settings,
            )

    with And("disk configuration for a blob storage disk"):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "external": external_disk,
        }
        if check_clickhouse_version(">=22.8")(self):
            disks["s3_cache"] = {
                "type": "cache",
                "disk": "external",
                "path": "external_disk_cache/",
                "max_size": "22548578304",
                "cache_on_write_operations": "1",
                # "do_not_evict_index_and_mark_files": "1",
            }
        else:
            disks["s3_cache"] = disks["external"]

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            policy_name: {
                "volumes": [
                    {
                        "default_and_external": [
                            {"disk": "default"},
                            {
                                "disk": (
                                    "s3_cache"
                                    if check_clickhouse_version(">=22.8")(self)
                                    else "external"
                                )
                            },
                        ]
                    }
                ]
            },
        }

    return s3_storage(disks=disks, policies=policies, restart=restart)


@TestStep(Given)
def default_s3_and_local_volume(
    self, restart=True, uri=None, policy_name="default_and_external", disk_settings=None
):
    """Default settings for s3 and local volumes."""

    disk_settings = disk_settings or {}

    with Given("parameters for an external disk"):
        if self.context.storage == "azure":
            external_disk = azure_blob_type_disk_parameters(
                self.context.azure_storage_account_url,
                self.context.azure_container_name,
                self.context.azure_account_name,
                self.context.azure_account_key,
                disk_settings,
            )
        else:
            uri = uri or self.context.uri
            external_disk = s3_type_disk_parameters(
                uri,
                self.context.access_key_id,
                self.context.secret_access_key,
                disk_settings,
            )

    with And("disk configuration for a blob storage disk"):
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "external": external_disk,
        }
        if check_clickhouse_version(">=22.8")(self):
            disks["s3_cache"] = {
                "type": "cache",
                "disk": "external",
                "path": "external_disk_cache/",
                "max_size": "22548578304",
                "cache_on_write_operations": "1",
                # "do_not_evict_index_and_mark_files": "1",
            }
        else:
            disks["s3_cache"] = disks["external"]

    with And("I have a storage policy configured to use the S3 disk"):
        policies = {
            policy_name: {
                "volumes": {
                    "default": {"disk": "default"},
                    "external": {"disk": "s3_cache"},
                }
            },
        }

    return s3_storage(disks=disks, policies=policies, restart=restart)


@TestStep(Given)
def default_s3_disk_and_volume(
    self,
    uri=None,
    access_key_id=None,
    secret_access_key=None,
    settings={},
    disk_name="external",
    policy_name="external",
    restart=True,
):
    """Setup disk configuration and storage policy for s3 disk and volume with the given parameters."""
    if uri is None:
        uri = self.context.uri
    if settings is None:
        settings = {}

    if self.context.storage != "azure":
        if access_key_id is None:
            access_key_id = self.context.access_key_id
        if secret_access_key is None:
            secret_access_key = self.context.secret_access_key

    with Given("parameters for an external disk"):
        if self.context.storage == "azure":
            external_disk = azure_blob_type_disk_parameters(
                self.context.azure_storage_account_url,
                self.context.azure_container_name,
                self.context.azure_account_name,
                self.context.azure_account_key,
            )
        else:
            uri = uri or self.context.uri
            external_disk = s3_type_disk_parameters(
                uri,
                self.context.access_key_id,
                self.context.secret_access_key,
            )

    with And("disk configuration for a blob storage disk"):
        if check_clickhouse_version(">=22.8")(self):
            disks = {
                disk_name: external_disk,
                "s3_cache": {
                    "type": "cache",
                    "disk": disk_name,
                    "path": f"{disk_name}_cache/",
                    "max_size": "22548578304",
                    "cache_on_write_operations": "1",
                    # "do_not_evict_index_and_mark_files": "1",
                },
            }
        else:
            disks = {disk_name: external_disk}

        if hasattr(self.context, "s3_options"):
            disks[disk_name].update(self.context.s3_options)

        if settings:
            disks[disk_name].update(settings)

    with And("I have a storage policy configured to use the S3 disk"):
        if check_clickhouse_version(">=22.8")(self):
            policies = {
                "default": {"volumes": {"default": {"disk": "default"}}},
                f"{policy_name}_nocache": {
                    "volumes": {"external": {"disk": disk_name}}
                },
                policy_name: {"volumes": {"external": {"disk": "s3_cache"}}},
                "s3_cache": {"volumes": {"external": {"disk": "s3_cache"}}},
            }
        else:
            policies = {policy_name: {"volumes": {"external": {"disk": disk_name}}}}

    return s3_storage(disks=disks, policies=policies, restart=restart)


@TestStep(Given)
def simple_table(
    self, name, policy="external", node=None, columns="d UInt64", settings: str = ""
):
    """Create a simple MergeTree table for s3 tests."""
    node = node or self.context.node

    query = f"CREATE TABLE {name} ({columns}) ENGINE = MergeTree() ORDER BY {columns.split()[0]}"
    if policy:
        query += f" SETTINGS storage_policy='{policy}'"
    if settings:
        query += ", " + settings

    try:
        with Given(f"I have a table {name}"):
            node.query(query)

        yield

    finally:
        with Finally(f"I remove the table {name}"):
            node.query(f"DROP TABLE IF EXISTS {name} SYNC")


@TestStep(Given)
def replicated_table(
    self,
    table_name,
    policy="external",
    node=None,
    columns="d UInt64",
    path=None,
    settings: str = "",
):
    """Create a ReplicatedMergeTree table for s3 tests."""
    node = node or self.context.node
    path = path or f"/clickhouse/tables/{table_name}"
    query = f"""
        CREATE TABLE {table_name} ({columns})
        ENGINE = ReplicatedMergeTree('{path}', '{{replica}}')
        ORDER BY {columns.split()[0]}
        SETTINGS storage_policy='{policy}'"""

    if settings:
        query += ", " + settings

    try:
        with Given(f"I have a table {table_name}"):
            node.query(query)
        yield table_name

    finally:
        with Finally(f"I drop the table {table_name}"):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")


@TestStep(Given)
def delete_replica(self, node, table_name, timeout=30):
    """Delete the local copy of a replicated table."""
    r = node.query(
        f"DROP TABLE IF EXISTS {table_name} SYNC", exitcode=0, timeout=timeout
    )
    return r


@TestStep(Given)
def distributed_table_cluster(
    self,
    columns: str,
    table_name: str = None,
    cluster_name: str = "replicated_cluster",
    order_by: str = None,
    partition_by: str = None,
    primary_key: str = None,
    ttl: str = None,
    allow_zero_copy: bool = None,
    exitcode: int = 0,
    no_cleanup=False,
):
    """Create a distributed table with the ON CLUSTER clause."""

    node = current().context.node

    if table_name is None:
        table_name = "table_" + getuid()

    simple_table(
        node=self.context.cluster.node("clickhouse1"),
        name=table_name + "_local",
        policy="default",
        columns=columns,
    )
    simple_table(
        node=self.context.cluster.node("clickhouse2"),
        name=table_name + "_local",
        policy="default",
        columns=columns,
    )
    simple_table(
        node=self.context.cluster.node("clickhouse3"),
        name=table_name + "_local",
        policy="default",
        columns=columns,
    )

    if order_by is None:
        order_by = columns.split()[0]

    if allow_zero_copy is not None:
        settings.append(f"allow_remote_fs_zero_copy_replication={int(allow_zero_copy)}")

    if partition_by is not None:
        partition_by = f"PARTITION BY ({partition_by})"
    else:
        partition_by = ""

    if primary_key is not None:
        primary_key = f"PRIMARY KEY {primary_key}"
    else:
        primary_key = ""

    if ttl is not None:
        ttl = "TTL " + ttl
    else:
        ttl = ""

    try:
        with Given("I have a table"):
            r = node.query(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} as {table_name}_local
                ENGINE=Distributed({cluster_name}, default, {table_name}_local, rand())
                """,
                settings=[("distributed_ddl_task_timeout ", 360)],
                exitcode=exitcode,
            )

        yield r, table_name

    finally:
        if not no_cleanup:
            with Finally(f"I drop the table"):
                for attempt in retries(timeout=120, delay=5):
                    with attempt:
                        node.query(
                            f"DROP TABLE IF EXISTS {table_name} ON CLUSTER '{cluster_name}' SYNC",
                            timeout=60,
                        )


@TestStep(Given)
def replicated_table_cluster(
    self,
    columns: str,
    table_name: str = None,
    storage_policy: str = "external",
    cluster_name: str = "replicated_cluster",
    order_by: str = None,
    partition_by: str = None,
    primary_key: str = None,
    ttl: str = None,
    settings: str = None,
    allow_zero_copy: bool = None,
    exitcode: int = 0,
    no_cleanup=False,
):
    """Create a replicated table with the ON CLUSTER clause."""
    node = current().context.node

    if table_name is None:
        table_name = "table_" + getuid()

    if order_by is None:
        order_by = columns.split()[0]

    if settings is None:
        settings = []
    else:
        settings = [settings]

    settings.append(f"storage_policy='{storage_policy}'")

    if allow_zero_copy is not None:
        settings.append(f"allow_remote_fs_zero_copy_replication={int(allow_zero_copy)}")

    if partition_by is not None:
        partition_by = f"PARTITION BY ({partition_by})"
    else:
        partition_by = ""

    if primary_key is not None:
        primary_key = f"PRIMARY KEY {primary_key}"
    else:
        primary_key = ""

    if ttl is not None:
        ttl = "TTL " + ttl
    else:
        ttl = ""

    try:
        with Given("I have a table"):
            r = node.query(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} 
                ON CLUSTER '{cluster_name}' ({columns}) 
                ENGINE=ReplicatedMergeTree('/clickhouse/tables/{table_name}', '{{replica}}')
                ORDER BY {order_by} {partition_by} {primary_key} {ttl}
                SETTINGS {', '.join(settings)}
                """,
                settings=[("distributed_ddl_task_timeout ", 360)],
                exitcode=exitcode,
            )

        yield r, table_name

    finally:
        if not no_cleanup:
            with Finally(f"I drop the table"):
                for attempt in retries(timeout=120, delay=5):
                    with attempt:
                        node.query(
                            f"DROP TABLE IF EXISTS {table_name} ON CLUSTER '{cluster_name}' SYNC",
                            timeout=60,
                        )


@TestStep(When)
def standard_check(self):
    """Create a table on s3, insert data, check the data is correct."""
    name = "table_" + getuid()
    node = self.context.node

    with Given(f"I create table using S3 storage policy external"):
        simple_table(name=name)

    with When("I store simple data in the table"):
        node.query(f"INSERT INTO {name} VALUES (427)")

    with Then("I check that a simple SELECT * query returns matching data"):
        r = node.query(f"SELECT * FROM {name} FORMAT TabSeparated").output.strip()
        assert r == "427", error()


@TestStep(When)
def standard_inserts(self, node, table_name):
    """Standard inserts of a known amount of data."""

    with By("first inserting 1MB of data"):
        insert_data(node=node, number_of_mb=1, name=table_name)

    with And("another insert of 1MB of data"):
        insert_data(node=node, number_of_mb=1, start=1024 * 1024, name=table_name)

    with And("a large insert of 10Mb of data"):
        insert_data(node=node, number_of_mb=10, start=1024 * 1024 * 2, name=table_name)


@TestStep(Then)
def standard_selects(self, node, table_name):
    """Validate the data inserted by standard_inserts to an empty table."""
    check_query_node(
        node=node,
        num=0,
        query=f"SELECT COUNT() FROM {table_name} FORMAT TabSeparated",
        expected="1572867",
    )
    check_query_node(
        node=node,
        num=1,
        query=f"SELECT uniqExact(d) FROM {table_name} WHERE d < 10 FORMAT TabSeparated",
        expected="10",
    )
    check_query_node(
        node=node,
        num=2,
        query=f"SELECT d FROM {table_name} ORDER BY d DESC LIMIT 1 FORMAT TabSeparated",
        expected="3407872",
    )
    check_query_node(
        node=node,
        num=3,
        query=f"SELECT d FROM {table_name} ORDER BY d ASC LIMIT 1 FORMAT TabSeparated",
        expected="0",
    )
    check_query_node(
        node=node,
        num=4,
        query=f"SELECT * FROM {table_name} WHERE d == 0 OR d == 1048578 OR d == 2097154 ORDER BY d FORMAT TabSeparated",
        expected="0\n1048578\n2097154",
    )
    check_query_node(
        node=node,
        num=5,
        query=f"SELECT * FROM (SELECT d FROM {table_name} WHERE d == 1) FORMAT TabSeparated",
        expected="1",
    )


@TestStep(Then)
def assert_row_count(self, node, table_name: str, rows: int = 1000000):
    """Assert that the number of rows in a table is as expected."""
    if node is None:
        node = current().context.node

    actual_count = get_row_count(node=node, table_name=table_name)
    assert rows == actual_count, error()


@TestStep(Then)
def check_consistency(self, nodes, table_name, sync_timeout=10):
    """SYNC the given nodes and check that they agree about the given table"""

    for attempt in retries(timeout=100, delay=10):
        with attempt:
            with When("I make sure all nodes are synced"):
                for node in nodes:
                    sync_replica(
                        node=node,
                        table_name=table_name,
                        timeout=sync_timeout,
                        no_checks=True,
                    )

            with When("I query all nodes for their row counts"):
                row_counts = {}
                for node in nodes:
                    row_counts[node.name] = get_row_count(
                        node=node, table_name=table_name
                    )

            with Then("All replicas should have the same state"):
                for n1, n2 in combinations(nodes, 2):
                    assert row_counts[n1.name] == row_counts[n2.name], error()


@TestStep(Given)
def add_ssec_s3_option(self, ssec_key=None):
    """Add S3 SSE-C encryption option."""
    if not hasattr(self.context, "s3_options"):
        self.context.s3_options = {}

    if ssec_key is None:
        with By("generating 256 bit key encoded using base64"):
            ssec_key = base64.b64encode(os.urandom(16)).decode("utf-8")
    else:
        with By("using provided ssec key"):
            ssec_key = ssec_key

    try:
        with By(
            "adding 'server_side_encryption_customer_key_base64' S3 option",
            description=f"key={ssec_key}",
        ):
            self.context.s3_options["server_side_encryption_customer_key_base64"] = (
                ssec_key
            )
        yield

    finally:
        with Finally("I remove 'server_side_encryption_customer_key_base64' S3 option"):
            if hasattr(self.context, "s3_options"):
                self.context.s3_options.pop(
                    "server_side_encryption_customer_key_base64"
                )


@TestStep(Given)
def add_batch_delete_option(self, batch_delete="false"):
    """Add S3 batch delete option."""
    if not hasattr(self.context, "s3_options"):
        self.context.s3_options = {}

    try:
        with By(
            "adding 'support_batch_delete' S3 option",
            description=f"batch_delete={batch_delete}",
        ):
            self.context.s3_options["support_batch_delete"] = batch_delete
        yield

    finally:
        with Finally("I remove 'support_batch_delete' S3 option"):
            if hasattr(self.context, "s3_options"):
                self.context.s3_options.pop("support_batch_delete")


@TestStep(Given)
def insert_to_s3_function(
    self,
    filename,
    table_name,
    columns="d UInt64",
    compression=None,
    fmt=None,
    uri=None,
):
    """Write a table to a file in s3. File will be overwritten from an empty table during cleanup."""

    uri = uri or self.context.uri
    node = current().context.node

    try:
        query = f"INSERT INTO FUNCTION s3(s3_credentials, url='{uri}{filename}', format='CSVWithNames', structure='{columns}'"

        if compression:
            query += f", compression_method='{compression}'"

        query += f") SELECT * FROM {table_name}"

        if fmt:
            query += f" FORMAT {fmt}"

        node.query(query)

        yield

    finally:
        query = f"INSERT INTO FUNCTION s3(s3_credentials, url='{uri}{filename}', format='CSV', structure='{columns}'"
        query += f") SELECT * FROM null('{columns}')"

        node.query(query)


@TestStep(When)
def insert_from_s3_function(
    self,
    filename,
    table_name,
    columns="d UInt64",
    compression=None,
    fmt=None,
    uri=None,
    cluster_name=None,
    no_checks=False,
):
    """Import data from a file in s3 to a table."""
    uri = uri or self.context.uri
    node = current().context.node

    if cluster_name is None:
        query = f"INSERT INTO {table_name} SELECT * FROM s3(s3_credentials, url='{uri}{filename}', format='CSVWithNames', structure='{columns}'"
    else:
        column_names = [col.split()[0] for col in columns.split(',')]
        columns_list = ', '.join(column_names)
        query = f"INSERT INTO {table_name} SELECT {columns_list} FROM s3Cluster('{cluster_name}', s3_credentials, url='{uri}{filename}', format='CSVWithNames', structure='{columns}'"

    if compression:
        query += f", compression_method='{compression}'"

    query += ")"

    if fmt:
        query += f" FORMAT {fmt}"

    return node.query(query, no_checks=no_checks)


@TestStep(Given)
def measure_buckets_before_and_after(
    self,
    bucket_prefix=None,
    bucket_name=None,
    tolerance=5,
    delay=15,
    less_ok=False,
):
    """Return the current bucket size and assert that it is the same after cleanup."""

    with When("I get the size of the s3 bucket before adding data"):
        size_before = get_stable_bucket_size(
            prefix=bucket_prefix, name=bucket_name, delay=delay
        )

    yield size_before

    if less_ok:
        with Then("the size of the s3 bucket should not be more than the initial size"):
            for attempt in retries(count=3):
                with attempt:
                    size = get_stable_bucket_size(
                        prefix=bucket_prefix,
                        name=bucket_name,
                        delay=delay * (attempt.retry_number + 1),
                    )
                    assert size <= size_before + tolerance, error()
    else:
        with Then("the size of the s3 bucket should be very close to the initial size"):
            for attempt in retries(count=3):
                with attempt:
                    check_stable_bucket_size(
                        prefix=bucket_prefix,
                        name=bucket_name,
                        expected_size=size_before,
                        tolerance=tolerance,
                        delay=delay * (attempt.retry_number + 1),
                    )
