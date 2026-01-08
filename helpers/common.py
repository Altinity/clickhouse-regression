import os
import re
import uuid
import time
import duckdb
import platform
import xml.etree.ElementTree as xmltree
from collections import namedtuple
from threading import Event

import testflows.settings as settings
from testflows.core import *
from testflows.asserts import values, error, snapshot
from testflows.core.name import basename, parentname, unclean
from testflows._core.testtype import TestSubType


def current_cpu():
    """Return current cpu architecture."""
    arch = platform.processor()
    if arch not in ("x86_64", "aarch64", "arm"):
        raise TypeError(f"unsupported CPU architecture {arch}")
    return arch


def check_current_cpu(arch):
    """Check current cpu architecture."""

    def check(test):
        return current_cpu() == arch

    return check


def check_analyzer():
    """Check if analyzer is enabled."""

    def check(test):
        default_query_settings = getsattr(
            current().context, "default_query_settings", []
        )
        if (
            "allow_experimental_analyzer",
            1,
        ) in default_query_settings or (
            check_clickhouse_version(">=24.3")(test)
            and ("allow_experimental_analyzer", 0) not in default_query_settings
        ):
            return True
        else:
            return False

    return check


def check_with_ubsan(test):
    """Check if the build is with undefined behavior sanitizer (ubsan)."""
    if hasattr(test.context, "build_options"):
        if "ubsan" in test.context.build_options.values():
            return True

    return False


def check_with_tsan(test):
    """Check if the build is with thread sanitizer (tsan)."""
    if hasattr(test.context, "build_options"):
        if "tsan" in test.context.build_options.values():
            return True

    return False


def check_with_asan(test):
    """Check if the build is with address sanitizer (asan)."""
    if hasattr(test.context, "build_options"):
        if "asan" in test.context.build_options.values():
            return True

    return False


def check_with_msan(test):
    """Check if the build is with memory sanitizer (msan)."""
    if hasattr(test.context, "build_options"):
        if "msan" in test.context.build_options.values():
            return True

    return False


def check_tsan_in_binary_link(test):
    """Check if the build is with ThreadSanitizer (tsan)."""
    binary_path = getsattr(test.context.cluster, "clickhouse_path", "")
    note(f"binary path: {binary_path}")
    return "tsan" in binary_path


def check_asan_in_binary_link(test):
    """Check if the build is with AddressSanitizer (asan)."""
    binary_path = getsattr(test.context.cluster, "clickhouse_path", "")
    note(f"binary path: {binary_path}")
    return "asan" in binary_path


def check_ubsan_in_binary_link(test):
    """Check if the build is with UndefinedBehaviorSanitizer (ubsan)."""
    binary_path = getsattr(test.context.cluster, "clickhouse_path", "")
    note(f"binary path: {binary_path}")
    return "ubsan" in binary_path


def check_msan_in_binary_link(test):
    """Check if the build is with MemorySanitizer (msan)."""
    binary_path = getsattr(test.context.cluster, "clickhouse_path", "")
    note(f"binary path: {binary_path}")
    return "msan" in binary_path


def check_if_antalya_build(test=None):
    """True if build is Antalya build."""
    return "antalya" in current().context.full_clickhouse_version


def check_if_not_antalya_build(test=None):
    """True if build is not Antalya build."""
    return "antalya" not in current().context.full_clickhouse_version


def check_if_altinity_build(test=None):
    """True if build is Altinity build."""
    return "altinity" in current().context.full_clickhouse_version


def check_if_25_8_altinity_build(test=None):
    """True if build is 25.8 Altinity build."""
    return "25.8" in current().context.full_clickhouse_version and check_if_altinity_build()


def check_if_head(test):
    """True if build is head build."""
    binary_path = getsattr(test.context.cluster, "clickhouse_path", "")
    return "head" in binary_path


def check_with_any_sanitizer(test):
    """Check if the build is with any sanitizer (tsan, asan, ubsan, msan)."""
    sanitizers = ["tsan", "asan", "ubsan", "msan"]
    if hasattr(test.context, "build_options"):
        return any(
            sanitizer in test.context.build_options.values() for sanitizer in sanitizers
        )
    return False


def check_several_sanitizers_in_binary_link(
    sanitizers=["tsan", "asan", "ubsan", "msan"]
):
    """Check if the build is with specified list of sanitizers."""

    def check(test):
        if hasattr(test.context, "build_options"):
            return any(
                sanitizer in test.context.build_options.values()
                for sanitizer in sanitizers
            )
        return False

    return check


def check_clickhouse_version(version):
    """Compare ClickHouse version."""

    def check(test):
        if getattr(test.context, "clickhouse_version", None) is None:
            return False

        if callable(version):
            return version(test.context.clickhouse_version)

        if version.startswith("~~"):
            # full regex matching
            return bool(re.match("^" + version[2:], test.context.clickhouse_version))

        if version.startswith("~"):
            # simplified pattern matching
            if "\\*" in version:
                raise ValueError(
                    "literal '*' character is not allowed in simplified pattern matching. Use ~~ for full regex matching."
                )
            return bool(
                re.match(
                    "^" + version[1:].replace(".", "\\.").replace("*", ".*"),
                    test.context.clickhouse_version,
                )
            )

        version_list = version.translate({ord(i): None for i in "<>="}).split(".")
        clickhouse_version_list = test.context.clickhouse_version.split(".")
        for index, i in enumerate(clickhouse_version_list):
            if not i.isnumeric():
                break
            elif index == len(clickhouse_version_list) - 1:
                index += 1

        if index == 0:
            raise ValueError(f"failed to parse version {clickhouse_version_list}")

        version_list = [int(i) for i in version_list[0:index]]
        clickhouse_version_list = [int(i) for i in clickhouse_version_list[0:index]]

        if version.startswith("=="):
            return clickhouse_version_list == version_list
        elif version.startswith(">="):
            return clickhouse_version_list >= version_list
        elif version.startswith("<="):
            return clickhouse_version_list <= version_list
        elif version.startswith("="):
            return clickhouse_version_list == version_list
        elif version.startswith(">"):
            return clickhouse_version_list > version_list
        elif version.startswith("<"):
            return clickhouse_version_list < version_list
        else:
            return clickhouse_version_list == version_list

    return check


def check_is_altinity_build(node=None):
    """
    Check if the build is from Altinity.

    The check needs to be robust, it's possible that a test build
    will not have the version set correctly.
    """
    if node is None:
        node = current().context.node

    res = node.command(
        "grep -q -i -a altinity /usr/bin/clickhouse", no_checks=True, steps=False
    )
    return res.exitcode == 0


def getuid(with_test_name=False):
    if not with_test_name:
        return str(uuid.uuid1()).replace("-", "_")

    if current().subtype == TestSubType.Example:
        testname = (
            f"{basename(parentname(current().name)).replace(' ', '_').replace(',', '')}"
        )
    else:
        testname = f"{basename(current().name).replace(' ', '_').replace(',', '')}"

    return testname + "_" + str(uuid.uuid1()).replace("-", "_")


@TestStep(Given)
def instrument_clickhouse_server_log(
    self,
    node=None,
    test=None,
    clickhouse_server_log="/var/log/clickhouse-server/clickhouse-server.log",
    always_dump=False,
):
    """Instrument clickhouse-server.log for the current test (default)
    by adding start and end messages that include test name to log
    of the specified node. If we are in the debug mode and the test
    fails then dump the messages from the log for this test.

    :param always_dump: always dump clickhouse log after test, default: `False`
    """
    if test is None:
        test = current()

    if node is None:
        node = self.context.node

    with By("getting current log size"):
        cmd = node.command(f"stat -c %s {clickhouse_server_log}")
        if (
            cmd.output
            == f"stat: cannot stat '{clickhouse_server_log}': No such file or directory"
        ):
            start_logsize = 0
        else:
            start_logsize = cmd.output.split(" ")[0].strip()

    try:
        with And("adding test name start message to the clickhouse-server.log"):
            node.command(
                f'echo -e "\\n-- start: {test.name} --\\n" >> {clickhouse_server_log}'
            )
        yield

    finally:
        if test.terminating is True:
            return

        with Finally(
            "adding test name end message to the clickhouse-server.log", flags=TE
        ):
            node.command(
                f'echo -e "\\n-- end: {test.name} --\\n" >> {clickhouse_server_log}'
            )

        with And("getting current log size at the end of the test"):
            cmd = node.command(f"stat -c %s {clickhouse_server_log}")
            end_logsize = cmd.output.split(" ")[0].strip()

        dump_log = always_dump or (settings.debug and not self.parent.result)

        if dump_log:
            with Then("dumping clickhouse-server.log for this test"):
                node.command(
                    f"tail -c +{start_logsize} {clickhouse_server_log}"
                    f" | head -c {int(end_logsize) - int(start_logsize)}"
                )


xml_with_utf8 = '<?xml version="1.0" encoding="utf-8"?>\n'


def xml_indent(elem, level=0, by="  "):
    i = "\n" + level * by
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + by
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            xml_indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def xml_append(root, tag, text):
    element = xmltree.Element(tag)
    element.text = text
    root.append(element)
    return element


class Config:
    def __init__(self, content, path, name, uid, preprocessed_name):
        self.content = content
        self.path = path
        self.name = name
        self.uid = uid
        self.preprocessed_name = preprocessed_name


class KeyWithAttributes:
    def __init__(self, name, attributes):
        """XML key with attributes.

        :param name: key name
        :param attributes: dictionary of attributes {name: value, ...}
        """
        self.name = name
        self.attributes = dict(attributes)


def _create_xml_tree(entries, parent):
    """
    Helper function for create_xml_config_content_with_duplicate_tags.
    Recursive helper that understands:
      • dict            – one element per key
      • list | tuple    – either a) list of dicts/KeyWithAttributes
                          or b) list of scalars → duplicate tags
    """

    if isinstance(entries, (list, tuple)):
        for item in entries:
            _create_xml_tree(item, parent)
        return

    for k, v in entries.items():
        if isinstance(k, KeyWithAttributes):
            elem = xmltree.Element(k.name, **k.attributes)
            if isinstance(v, (dict, list, tuple)):
                _create_xml_tree(v, elem)
            else:
                elem.text = str(v)
            parent.append(elem)
            continue

        if isinstance(v, (list, tuple)):
            if all(
                not isinstance(i, (dict, KeyWithAttributes, list, tuple)) for i in v
            ):
                for scalar in v:
                    xml_append(parent, k, scalar)
            else:
                for item in v:
                    elem = xmltree.Element(k)
                    _create_xml_tree(item, elem)
                    parent.append(elem)
            continue

        if isinstance(v, dict):
            elem = xmltree.Element(k)
            _create_xml_tree(v, elem)
            parent.append(elem)
            continue

        xml_append(parent, k, v)


def create_xml_config_content_with_duplicate_tags(
    entries,
    config_file,
    config_d_dir="/etc/clickhouse-server/config.d",
    root_tag="clickhouse",
    preprocessed_name="config.xml",
):
    """Create XML configuration file from a dictionary. This function is used
    when we want to create a config file with duplicate tags. If you want normal
    behavior, use create_xml_config_content.

    :param entries: dictionary that defines xml
    :param config_file: name of the config file
    :param config_d_dir: config.d directory path, default: `/etc/clickhouse-server/config.d`
    """
    uid = getuid()
    path = os.path.join(config_d_dir, config_file)
    name = config_file

    root = xmltree.Element(root_tag)
    root.append(xmltree.Comment(text=f"config uid: {uid}"))

    _create_xml_tree(entries, root)
    xml_indent(root)

    content = xml_with_utf8 + xmltree.tostring(
        root, short_empty_elements=False, encoding="utf-8"
    ).decode("utf-8")
    return Config(content, path, name, uid, preprocessed_name)


def create_xml_config_content(
    entries,
    config_file,
    config_d_dir="/etc/clickhouse-server/config.d",
    root="clickhouse",
    preprocessed_name="config.xml",
):
    """Create XML configuration file from a dictionary.

    :param entries: dictionary that defines xml
    :param config_file: name of the config file
    :param config_d_dir: config.d directory path, default: `/etc/clickhouse-server/config.d`
    """
    uid = getuid()
    path = os.path.join(config_d_dir, config_file)
    name = config_file
    root = xmltree.Element(root)
    root.append(xmltree.Comment(text=f"config uid: {uid}"))

    def create_xml_tree(entries, root):
        for k, v in entries.items():
            if isinstance(k, KeyWithAttributes):
                xml_element = xmltree.Element(k.name)
                for attr_name, attr_value in k.attributes.items():
                    xml_element.set(attr_name, attr_value)
                if type(v) is dict:
                    create_xml_tree(v, xml_element)
                elif type(v) in (list, tuple):
                    for e in v:
                        create_xml_tree(e, xml_element)
                else:
                    xml_element.text = v
                root.append(xml_element)
            elif type(v) is dict:
                xml_element = xmltree.Element(k)
                create_xml_tree(v, xml_element)
                root.append(xml_element)
            elif type(v) in (list, tuple):
                xml_element = xmltree.Element(k)
                for e in v:
                    create_xml_tree(e, xml_element)
                root.append(xml_element)
            else:
                xml_append(root, k, v)

    create_xml_tree(entries, root)
    xml_indent(root)
    content = xml_with_utf8 + str(
        xmltree.tostring(root, short_empty_elements=False, encoding="utf-8"), "utf-8"
    )

    return Config(content, path, name, uid, preprocessed_name)


def add_invalid_config(
    config, message, recover_config=None, tail=300, timeout=300, restart=True, user=None
):
    """Check that ClickHouse errors when trying to load invalid configuration file."""
    cluster = current().context.cluster
    node = current().context.node

    try:
        with Given("I prepare the error log by writing empty lines into it"):
            node.command(
                'echo -e "%s" > /var/log/clickhouse-server/clickhouse-server.err.log'
                % ("-\\n" * tail)
            )

        with When("I add the config", description=config.path):
            command = f"cat <<HEREDOC > {config.path}\n{config.content}\nHEREDOC"
            node.command(command, steps=False, exitcode=0)

        with Then(
            f"{config.preprocessed_name} should be updated",
            description=f"timeout {timeout}",
        ):
            started = time.time()
            command = f"cat /var/lib/clickhouse/preprocessed_configs/{config.preprocessed_name} | grep {config.uid}{' > /dev/null' if not settings.debug else ''}"
            while time.time() - started < timeout:
                exitcode = node.command(command, steps=False, no_checks=True).exitcode
                if exitcode == 0:
                    break
                time.sleep(1)
            assert exitcode == 0, error()

        if restart:
            with When("I restart ClickHouse to apply the config changes"):
                node.restart_clickhouse(safe=False, wait_healthy=False, user=user)

    finally:
        if recover_config is None:
            with Finally(f"I remove {config.name}"):
                with By("removing invalid configuration file"):
                    system_config_path = os.path.join(
                        cluster.environ["CLICKHOUSE_TESTS_DIR"],
                        "configs",
                        node.name,
                        "config.d",
                        config.path.split("config.d/")[-1],
                    )
                    cluster.command(
                        None,
                        f"rm -rf {system_config_path}",
                        timeout=timeout,
                        exitcode=0,
                    )

                if restart:
                    with And("restarting ClickHouse"):
                        node.restart_clickhouse(safe=False, user=user)
                        node.restart_clickhouse(safe=False, user=user)
        else:
            with Finally(f"I change {config.name}"):
                with By("changing invalid configuration file"):
                    system_config_path = os.path.join(
                        cluster.environ["CLICKHOUSE_TESTS_DIR"],
                        "configs",
                        node.name,
                        "config.d",
                        config.path.split("config.d/")[-1],
                    )
                    cluster.command(
                        None,
                        f"rm -rf {system_config_path}",
                        timeout=timeout,
                        exitcode=0,
                    )
                    command = f"cat <<HEREDOC > {system_config_path}\n{recover_config.content}\nHEREDOC"
                    cluster.command(None, command, timeout=timeout, exitcode=0)

                if restart:
                    with And("restarting ClickHouse"):
                        node.restart_clickhouse(safe=False, user=user)

    with Then("error log should contain the expected error message"):
        started = time.time()
        command = f'tail -n {tail} /var/log/clickhouse-server/clickhouse-server.err.log | grep "{message}"'
        while time.time() - started < timeout:
            exitcode = node.command(command, steps=False, no_checks=True).exitcode
            if exitcode == 0:
                break
            time.sleep(1)
        assert exitcode == 0, error()


def add_config(
    config,
    timeout=300,
    restart=False,
    modify=False,
    node=None,
    user=None,
    wait_healthy=True,
    check_preprocessed=True,
    after_removal=True,
):
    """Add dynamic configuration file to ClickHouse.

    :param config: configuration file description
    :param timeout: timeout, default: 300 sec
    :param restart: restart server, default: False
    :param modify: only modify configuration file, default: False
    """
    if node is None:
        node = current().context.node
    cluster = current().context.cluster

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
                node.start_clickhouse(user=user, wait_healthy=wait_healthy)

            with Then("I tail the log file from using previous log size as the offset"):
                bash.prompt = bash.__class__.prompt
                bash.open()
                bash.send(
                    f"tail -c +{logsize} -f /var/log/clickhouse-server/clickhouse-server.log"
                )

        with Then("I wait for config reload message in the log file"):
            if restart:
                choice = bash.expect(
                    (
                        f"(ConfigReloader: Loaded config '/etc/clickhouse-server/config.xml', performed update on configuration)|"
                        f"(ConfigReloader: Error updating configuration from '/etc/clickhouse-server/config.xml')"
                    ),
                    timeout=timeout,
                )
            else:
                choice = bash.expect(
                    (
                        f"(ConfigReloader: Loaded config '/etc/clickhouse-server/{config.preprocessed_name}', performed update on configuration)|"
                        f"(ConfigReloader: Error updating configuration from '/etc/clickhouse-server/{config.preprocessed_name}')"
                    ),
                    timeout=timeout,
                )
            if choice.group(2):
                bash.expect(".+\n", timeout=5, expect_timeout=True)
                fail("ConfigReloader: Error updating configuration")

    try:
        with Given(f"{config.name}"):
            if settings.debug:
                with When("I output the content of the config"):
                    debug(config.content)

            with node.cluster.shell(node.name) as bash:
                if check_preprocessed:
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

        yield config

    finally:
        if not modify:
            with Finally(f"I remove {config.name} on {node.name}"):
                with node.cluster.shell(node.name) as bash:
                    if check_preprocessed:
                        bash.expect(bash.prompt)
                        bash.send(
                            "tail -v -n 0 -f /var/log/clickhouse-server/clickhouse-server.log"
                        )
                        # make sure tail process is launched and started to follow the file
                        bash.expect("<==")
                        bash.expect("\n")

                    with By("removing the config file", description=config.path):
                        node.command(f"rm -rf {config.path}", exitcode=0)

                    if check_preprocessed:
                        with Then(
                            f"{config.preprocessed_name} should be updated",
                            description=f"timeout {timeout}",
                        ):
                            check_preprocessed_config_is_updated(
                                after_removal=after_removal
                            )

                        with And("I wait for config to be reloaded"):
                            wait_for_config_to_be_loaded()


def remove_config(
    config,
    timeout=300,
    restart=False,
    modify=False,
    node=None,
    user=None,
    wait_healthy=True,
    check_preprocessed=True,
):
    """Remove configuration file from ClickHouse.

    :param config: configuration file description
    :param timeout: timeout, default: 300 sec
    :param restart: restart server, default: False
    :param modify: only modify configuration file, default: False
    """
    if node is None:
        node = current().context.node
    cluster = current().context.cluster

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
                node.start_clickhouse(user=user, wait_healthy=wait_healthy)

            with Then("I tail the log file from using previous log size as the offset"):
                bash.prompt = bash.__class__.prompt
                bash.open()
                bash.send(
                    f"tail -c +{logsize} -f /var/log/clickhouse-server/clickhouse-server.log"
                )

        with Then("I wait for config reload message in the log file"):
            if restart:
                choice = bash.expect(
                    (
                        f"(ConfigReloader: Loaded config '/etc/clickhouse-server/config.xml', performed update on configuration)|"
                        f"(ConfigReloader: Error updating configuration from '/etc/clickhouse-server/config.xml')"
                    ),
                    timeout=timeout,
                )
            else:
                choice = bash.expect(
                    (
                        f"(ConfigReloader: Loaded config '/etc/clickhouse-server/{config.preprocessed_name}', performed update on configuration)|"
                        f"(ConfigReloader: Error updating configuration from '/etc/clickhouse-server/{config.preprocessed_name}')"
                    ),
                    timeout=timeout,
                )
            if choice.group(2):
                bash.expect(".+\n", timeout=5, expect_timeout=True)
                fail("ConfigReloader: Error updating configuration")

    try:
        with Given(f"{config.name}"):
            if settings.debug:
                with When("I output the content of the config"):
                    debug(config.content)

            with node.cluster.shell(node.name) as bash:
                if check_preprocessed:
                    bash.expect(bash.prompt)
                    bash.send(
                        "tail -v -n 0 -f /var/log/clickhouse-server/clickhouse-server.log"
                    )
                    # make sure tail process is launched and started to follow the file
                    bash.expect("<==")
                    bash.expect("\n")

                with By("removing the config file", description=config.path):
                    node.command(f"rm -rf {config.path}", exitcode=0)

                if check_preprocessed:
                    with Then(
                        f"{config.preprocessed_name} should be updated",
                        description=f"timeout {timeout}",
                    ):
                        check_preprocessed_config_is_updated(after_removal=True)

                    with And("I wait for config to be reloaded"):
                        wait_for_config_to_be_loaded()

        yield

    finally:
        if not modify:
            with Finally(f"Restore {config.name} on {node.name}"):
                with node.cluster.shell(node.name) as bash:
                    if check_preprocessed:
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


@TestStep(Given)
def copy(
    self,
    dest_node,
    src_path,
    dest_path,
    bash=None,
    binary=False,
    eof="EOF",
    src_node=None,
):
    """Copy file from source to destination node."""
    if binary:
        raise NotImplementedError("not yet implemented; need to use base64 encoding")

    bash = self.context.cluster.bash(node=src_node)

    cmd = bash(f"cat {src_path}")

    assert cmd.exitcode == 0, error()
    contents = cmd.output
    try:
        dest_node.command(f"cat << {eof} > {dest_path}\n{contents}\n{eof}")
        yield dest_path
    finally:
        with Finally(f"I delete {dest_path}"):
            dest_node.command(f"rm -rf {dest_path}")


@TestStep(Given)
def add_user_to_group_on_node(
    self, node=None, group="clickhouse", username="clickhouse"
):
    """Add user {username} into group {group}."""
    if node is None:
        node = self.context.node

    node.command(f"usermode -g {group} {username}", exitcode=0)


@TestStep(Given)
def change_user_on_node(self, node=None, username="clickhouse"):
    """Change user on node."""
    if node is None:
        node = self.context.node
    try:
        node.command(f"su {username}", exitcode=0)
        yield
    finally:
        node.command("exit", exitcode=0)


@TestStep(Given)
def add_user_on_node(self, node=None, groupname=None, username="clickhouse"):
    """Create user on node with group specifying."""
    if node is None:
        node = self.context.node
    try:
        if groupname is None:
            node.command(f"useradd -s /bin/bash {username}", exitcode=0)
        else:
            node.command(f"useradd -g {groupname} -s /bin/bash {username}", exitcode=0)
        yield
    finally:
        node.command(f"userdel {username}", exitcode=0)


@TestStep(Given)
def add_group_on_node(self, node=None, groupname="clickhouse"):
    """Create group on node"""
    if node is None:
        node = self.context.node
    try:
        node.command(f"groupadd {groupname}", exitcode=0)
        yield
    finally:
        node.command(f"groupdel {groupname}", no_checks=True)


@TestStep(Given)
def create_file_on_node(self, path, content, node=None):
    """Create file on node.

    :param path: file path
    :param content: file content
    """
    if node is None:
        node = self.context.node
    try:
        with By(f"creating file {path}"):
            node.command(f"cat <<HEREDOC > {path}\n{content}\nHEREDOC", exitcode=0)
        yield path
    finally:
        with Finally(f"I remove {path}"):
            node.command(f"rm -rf {path}", exitcode=0)


@TestStep(Given)
def create_user(self, name=None, node=None):
    """Create a user."""
    if node is None:
        node = self.context.node

    if name is None:
        name = f"user_{getuid()}"

    try:
        node.query(f"CREATE USER OR REPLACE {name}")
        yield name
    finally:
        with Finally(f"drop the user {name}"):
            node.query(f"DROP USER IF EXISTS {name}")


@TestStep(Given)
def create_role(self, privilege=None, object=None, role_name=None, node=None):
    """Create role and grant privilege on object."""

    if node is None:
        node = self.context.node

    if role_name is None:
        role_name = f"role_{getuid()}"

    query = f"CREATE ROLE {role_name}; "

    if privilege is not None and object is not None:
        query += f"GRANT {privilege} ON {object} TO {role_name};"

    try:
        node.query(query)
        yield role_name

    finally:
        with Finally("drop the role"):
            node.query(f"DROP ROLE IF EXISTS {role_name}")


@TestStep(When)
def replace_partition(
    self,
    destination_table,
    source_table,
    partition=1,
    exitcode=None,
    user_name=None,
    message=None,
    node=None,
    additional_parameters=None,
):
    """Replace partition of the destination table from the source table. If message is not None, we expect that the
    usage of replace partition should output an error.
    """
    if node is None:
        node = self.context.node

    params = {}
    query = f"ALTER TABLE {destination_table} REPLACE PARTITION {partition} FROM {source_table}"

    if additional_parameters is not None:
        query += f" {additional_parameters}"

    with By("Executing the replace partition command"):
        if user_name is not None:
            params["settings"] = [("user", user_name)]
        if message is not None:
            params["message"] = message
        if exitcode is not None:
            params["exitcode"] = exitcode

        node.query(query, **params)


@TestStep(When)
def attach_partition(
    self,
    table,
    partition=1,
    exitcode=None,
    errorcode=None,
    user_name=None,
    message=None,
    node=None,
    additional_parameters=None,
):
    """Attaches a partition from the detached directory to the table."""
    if node is None:
        node = self.context.node

    params = {}
    query = f"ALTER TABLE {table} ATTACH PARTITION {partition}"

    if additional_parameters is not None:
        query += f" {additional_parameters}"

    with By("Executing the attach partition command"):
        if user_name is not None:
            params["settings"] = [("user", user_name)]
        if message is not None:
            params["message"] = message
        if exitcode is not None:
            params["exitcode"] = exitcode
        if errorcode is not None:
            params["errorcode"] = errorcode
        node.query(query, **params)


@TestStep(When)
def attach_part(
    self,
    table,
    part=None,
    exitcode=None,
    user_name=None,
    message=None,
    node=None,
    additional_parameters=None,
):
    """Attaches a partition from the detached directory to the table."""
    if node is None:
        node = self.context.node

    params = {}
    query = f"ALTER TABLE {table} ATTACH PART '{part}'"

    if additional_parameters is not None:
        query += f" {additional_parameters}"

    with By("Executing the attach partition command"):
        if user_name is not None:
            params["settings"] = [("user", user_name)]
        if message is not None:
            params["message"] = message
        if exitcode is not None:
            params["exitcode"] = exitcode

        node.query(query, **params)


@TestStep(When)
def attach_partition_from(
    self,
    destination_table,
    source_table,
    partition=1,
    exitcode=None,
    user_name=None,
    message=None,
    node=None,
    additional_parameters=None,
):
    """Attach partition to the destination table from the source table."""
    if node is None:
        node = self.context.node

    params = {}
    query = f"ALTER TABLE {destination_table} ATTACH PARTITION {partition} FROM {source_table}"

    if additional_parameters is not None:
        query += f" {additional_parameters}"

    with By("Executing the ATTACH PARTITION FROM command"):
        if user_name is not None:
            params["settings"] = [("user", user_name)]
        if message is not None:
            params["message"] = message
        if exitcode is not None:
            params["exitcode"] = exitcode

        node.query(query, **params)


@TestStep(When)
def detach_partition(
    self,
    table,
    partition=1,
    exitcode=None,
    errorcode=None,
    user_name=None,
    message=None,
    node=None,
    additional_parameters=None,
):
    """Moves a partition or part to the detached directory and forget it."""
    if node is None:
        node = self.context.node

    params = {}
    query = f"ALTER TABLE {table} DETACH PARTITION {partition}"

    if additional_parameters is not None:
        query += f" {additional_parameters}"

    with By("Executing the detach partition command"):
        if user_name is not None:
            params["settings"] = [("user", user_name)]
        if message is not None:
            params["message"] = message
        if exitcode is not None:
            params["exitcode"] = exitcode
        if errorcode is not None:
            params["errorcode"] = errorcode

        node.query(query, **params)


@TestStep(When)
def detach_part(
    self,
    table,
    part=None,
    exitcode=None,
    user_name=None,
    message=None,
    node=None,
    additional_parameters=None,
):
    """Moves a partition or part to the detached directory and forget it."""
    if node is None:
        node = self.context.node

    params = {}
    query = f"ALTER TABLE {table} DETACH PART '{part}'"

    if additional_parameters is not None:
        query += f" {additional_parameters}"

    with By("Executing the detach partition command"):
        if user_name is not None:
            params["settings"] = [("user", user_name)]
        if message is not None:
            params["message"] = message
        if exitcode is not None:
            params["exitcode"] = exitcode

        node.query(query, **params)


@TestStep(Given)
def set_envs_on_node(self, envs, node=None):
    """Set environment variables on node.

    :param envs: dictionary of env variables key=value
    """
    if node is None:
        node = self.context.node
    try:
        with By("setting envs"):
            for key, value in envs.items():
                node.command(f"export {key}={value}", exitcode=0)
        yield
    finally:
        with Finally(f"I unset envs"):
            for key in envs:
                node.command(f"unset {key}", exitcode=0)


def get_snapshot_id(snapshot_id=None, clickhouse_version=None):
    """Return snapshot id based on the current test's name
    and ClickHouse server version."""
    id_postfix = ""
    if clickhouse_version:
        if check_clickhouse_version(clickhouse_version)(current()):
            id_postfix = clickhouse_version

    if snapshot_id is None:
        return unclean(name.basename(current().name)) + id_postfix
    return snapshot_id


def get_settings_value(
    setting_name, node=None, table="system.settings", column="value"
):
    """Return value of the setting from some table."""
    if node is None:
        node = current().context.node

    return node.query(
        f"SELECT {column} FROM {table} WHERE name = '{setting_name}' FORMAT TabSeparated"
    ).output


def is_with_analyzer(node):
    """Return True if the `allow_experimental_analyzer` setting is enabled."""
    return (
        get_settings_value(node=node, setting_name="allow_experimental_analyzer") == "1"
    )


@TestStep(Given)
def experimental_analyzer(self, node, with_analyzer):
    """Enable or disable the experimental analyzer."""
    default_value = get_settings_value(
        node=node,
        setting_name="allow_experimental_analyzer",
    )
    default_query_settings = getsattr(self.context, "default_query_settings", [])
    if with_analyzer and default_value == "0":
        default_query_settings.append(("allow_experimental_analyzer", 1))
    elif not with_analyzer and default_value == "1":
        default_query_settings.append(("allow_experimental_analyzer", 0))


@TestStep(When)
def repeat_until_stop(self, stop_event: Event, func, delay=0.5):
    """
    Call the given function with no arguments until stop_event is set.
    Use with parallel=True.
    """
    while not stop_event.is_set():
        func()
        time.sleep(delay)


@TestStep(Given)
def allow_higher_cpu_wait_ratio(
    self, min_os_cpu_wait_time_ratio_to_throw=10, max_os_cpu_wait_time_ratio_to_throw=20
):
    """
    Temporarily increase the threshold for OS CPU wait time ratio
    to reduce the chance of query rejection due to system overload.

    This step updates the default query settings for the test context
    by increasing the min and max OS CPU wait-to-busy time ratios.

    Useful for tests that are expected to put high load on the system
    and may otherwise be rejected due to CPU pressure.

    Args:
        min_ratio (float): Minimum ratio at which query rejection starts (default=10).
        max_ratio (float): Maximum ratio at which rejection probability becomes 100% (default=20).
    """
    min_os_cpu_wait_time_ratio_to_throw_setting = (
        "min_os_cpu_wait_time_ratio_to_throw",
        min_os_cpu_wait_time_ratio_to_throw,
    )
    max_os_cpu_wait_time_ratio_to_throw_setting = (
        "max_os_cpu_wait_time_ratio_to_throw",
        max_os_cpu_wait_time_ratio_to_throw,
    )
    default_query_settings = None

    try:
        with By(
            "adding relaxed OS CPU wait ratio thresholds to default query settings"
        ):
            default_query_settings = getsattr(
                current().context, "default_query_settings", []
            )
            default_query_settings.append(min_os_cpu_wait_time_ratio_to_throw_setting)
            default_query_settings.append(max_os_cpu_wait_time_ratio_to_throw_setting)
        yield
    finally:
        with Finally(
            "removing the relaxed OS CPU wait ratio settings from default query settings"
        ):
            if default_query_settings:
                try:
                    default_query_settings.pop(
                        default_query_settings.index(
                            min_os_cpu_wait_time_ratio_to_throw_setting
                        )
                    )
                    default_query_settings.pop(
                        default_query_settings.index(
                            max_os_cpu_wait_time_ratio_to_throw_setting
                        )
                    )
                except ValueError:
                    pass


@TestStep(Given)
def run_duckdb(self):
    """Run DuckDB in a subprocess."""
    with By("running DuckDB"):
        connection = duckdb.connect()
        yield connection

    with Finally("closing the DuckDB connection"):
        connection.close()


@TestStep(When)
def run_duckdb_query(self, connection=None, query=None):
    """Run a query on the DuckDB connection."""
    if connection is None:
        connection = self.context.duckdb_connection

    with By(f"running the query {query}"):
        return connection.execute(query).fetchall()


@TestStep(Then)
def compare_with_expected(self, expected, output):
    """Compare the output with the expected."""
    for retry in retries(count=10, delay=1):
        with retry:
            assert output.output.strip() == expected.strip(), error()
