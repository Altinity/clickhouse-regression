import tempfile
import textwrap
from testflows.core import *
from testflows.asserts import error
from helpers.common import (
    add_config,
    add_invalid_config,
    create_xml_config_content,
    getuid,
)
from xml.sax.saxutils import escape as xml_escape
import copy

entries = {
    "storage_configuration": {
        "disks": [
            {"local": {"path": "$disk_local$/"}},
            {
                "encrypted_local": {
                    "type": "encrypted",
                    "disk": "local",
                    "path": "encrypted/",
                    "$key_parameter_name$": "$key_value$",
                }
            },
        ],
        "policies": {
            "local_encrypted": {
                "volumes": {"encrypted_disk": {"disk": "encrypted_local"}}
            }
        },
    }
}


@TestStep(Given)
def add_encrypted_disk_configuration(
    self, entries, xml_symbols=True, modify=False, restart=True, format=None, user=None
):
    """Create encrypted disk configuration file and add it to the server."""
    with By("converting config file content to xml"):
        config = create_xml_config_content(entries, "encrypted_disk.xml")
        if format is not None:
            for key, value in format.items():
                if xml_symbols:
                    config.content = config.content.replace(key, xml_escape(value))
                else:
                    config.content = config.content.replace(key, value)
    with And("adding xml config file to the server"):
        return add_config(config, restart=restart, modify=modify, user=user)


@TestStep(Given)
def add_invalid_encrypted_disk_configuration(
    self,
    entries,
    message,
    recover_entries=None,
    xml_symbols=True,
    tail=30,
    timeout=300,
    restart=True,
    format=None,
):
    """Create invalid encrypted disk configuration file and add it to the server."""
    with By("converting config file content to xml"):
        config = create_xml_config_content(entries, "encrypted_disk.xml")
        if format is not None:
            for key, value in format.items():
                if xml_symbols:
                    config.content = config.content.replace(key, xml_escape(value))
                else:
                    config.content = config.content.replace(key, value)
    if recover_entries is None:
        recover_config = None
    else:
        with By("converting recover config file content to xml"):
            recover_config = create_xml_config_content(
                recover_entries, "encrypted_disk.xml"
            )
            if format is not None:
                for key, value in format.items():
                    if xml_symbols:
                        recover_config.content = recover_config.content.replace(
                            key, xml_escape(value)
                        )
                    else:
                        recover_config.content = recover_config.content.replace(
                            key, value
                        )

    with And("adding invalid xml config file to the server"):
        return add_invalid_config(
            config,
            recover_config=recover_config,
            message=message,
            tail=tail,
            timeout=timeout,
            restart=restart,
        )


@TestStep(Given)
def create_table(
    self,
    policy=None,
    ttl=False,
    ttl_timeout=None,
    partition_by_id=False,
    cluster=None,
    name=None,
    node=None,
    engine="MergeTree()",
    min_bytes_for_wide_part=None,
    without_order_by=False,
):
    """Create a MergeTree table that uses a given storage policy."""
    if name is None:
        name = getuid()

    if node is None:
        node = self.context.node

    try:
        node.query(
            textwrap.dedent(
                f"""
                CREATE TABLE {name} """
                + (f"""ON CLUSTER {cluster}""" if not (cluster is None) else "")
                + """
                (
                    Id Int32,"""
                + (
                    """
                    Date DateTime,
                """
                    if ttl
                    else ""
                )
                + f"""    Value String
                )
                ENGINE = {engine}"""
                + (
                    """
                PARTITION BY Id
                """
                    if partition_by_id
                    else ""
                )
                + (
                    ""
                    if without_order_by
                    else f"""
                ORDER BY Id"""
                )
                + (
                    """
                TTL Date TO VOLUME 'volume0',
                    Date + INTERVAL 1 HOUR TO VOLUME 'volume1',
                    Date + INTERVAL 2 HOUR DELETE
                    """
                    if ttl
                    else ""
                )
                + (
                    f"""
                SETTINGS storage_policy = '{policy}'"""
                    if not (policy is None)
                    else ""
                )
                + (
                    f""",merge_with_ttl_timeout = {ttl_timeout}
                """
                    if ttl_timeout is not None
                    else ""
                )
                + (
                    f""",min_bytes_for_wide_part={min_bytes_for_wide_part}
                """
                    if min_bytes_for_wide_part is not None
                    else ""
                )
            )
        )
        yield name

    finally:
        with Finally("I drop the table if exists"):
            if cluster is None:
                node.query(f"DROP TABLE IF EXISTS {name} SYNC")
            else:
                node.query(f"DROP TABLE IF EXISTS {name} ON CLUSTER {cluster} SYNC")


@TestStep(When)
def insert_into_table(self, name, values, settings=None, node=None):
    """Insert data into a table."""
    if node is None:
        node = self.context.node
    if settings is None:
        return node.query(f"INSERT INTO {name} VALUES {values}")
    else:
        return node.query(f"INSERT INTO {name} VALUES {values}", settings=settings)


@TestStep(When)
def multiple_insert_into_table(self, name, values, node=None):
    """Insert multiple data into a table."""
    if node is None:
        node = self.context.node
    query = "; ".join([f"INSERT INTO {name} VALUES {data}" for data in values])
    return node.query(query)


@TestStep(Given)
def create_directory(self, path, node=None):
    """Creating directory on node"""
    if node is None:
        node = self.context.node
    try:
        node.command(f"mkdir '{path}'", exitcode=0)
        yield path
    finally:
        with Finally("delete directory", description=f"{path}"):
            node.command(f"rm -rf '{path}'", exitcode=0)


@TestStep(Then)
def check_if_all_files_are_encrypted(
    self, disk_path, node=None, encrypted_header="ENC"
):
    """Check that all files inside the encrypted disk
    are encrypted by looking for encrypted header.
    """
    node = self.context.node if node is None else node

    flag = True

    with By("finding all files inside the encrypted disk"):
        r = node.command(
            f"for file in `find {disk_path} -type f`\ndo\nhead -1 $file | cut -c 1,2,3\ndone"
        )

    with Then("checking that they all have encrypted header"):
        headers = set(r.output.splitlines())
        assert headers == {"ENC"}, error()


@TestStep(Given)
def create_policy_with_local_encrypted_disk(
    self, key_parameter_name="key", key_value="firstfirstfirstf"
):
    """Modify server configuration to provide
    a policy that uses a local encrypted disk.
    """
    with Given("I create local disk folder on the server"):
        disk_local = "/disk_local"
        create_directory(path=disk_local)

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(
            entries=entries,
            format={
                "$disk_local$": disk_local,
                "$key_parameter_name$": key_parameter_name,
                "$key_value$": key_value,
            },
        )

    self.context.disk_path = disk_local
    self.context.policy = "local_encrypted"


@TestStep(Given)
def create_policy_with_local_encrypted_disk_and_local_disk(
    self, key_parameter_name="key", key_value="firstfirstfirstf"
):
    """Modify server configuration to provide a policy
    that uses a local encrypted disk and local disk.
    """
    with Given("I create local disk folders on the server"):
        create_directory(path="/disk_local0")
        create_directory(path="/disk_local1")

    entries = {
        "storage_configuration": {
            "disks": [
                {"local0": {"path": "/disk_local0/"}},
                {"local1": {"path": "/disk_local1/"}},
                {
                    "encrypted_local": {
                        "type": "encrypted",
                        "disk": "local0",
                        "path": "encrypted/",
                        "$key_parameter_name$": "$key_value$",
                    }
                },
            ],
            "policies": [
                {
                    "local_encrypted": {
                        "volumes": {"encrypted_disk": {"disk": "encrypted_local"}}
                    }
                },
                {"local": {"volumes": {"local_disk": {"disk": "local1"}}}},
            ],
        }
    }

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(
            entries=entries,
            format={
                "$key_parameter_name$": key_parameter_name,
                "$key_value$": key_value,
            },
        )

    self.context.policy = "local_encrypted"


@TestStep(Given)
def create_directories_multi_disk_volume(self, number_of_disks):
    with Given("I create local disk folders on the server"):
        for i in range(number_of_disks):
            create_directory(path=f"disk_local{i}/")


@TestStep(Given)
def add_config_multi_disk_volume(self, number_of_disks, disks_types, keys):
    entries = {
        "storage_configuration": {
            "disks": [],
            "policies": {"local_encrypted": {"volumes": {"volume1": []}}},
        }
    }

    with Given("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        for i in range(number_of_disks):
            if disks_types[i] == "local":
                entries_in_this_test["storage_configuration"]["disks"].append(
                    {f"local{i}": {"path": f"/disk_local{i}/"}}
                )
            elif disks_types[i] == "encrypted":
                entries_in_this_test["storage_configuration"]["disks"].append(
                    {f"local{i}": {"path": f"/disk_local{i}/"}}
                )
                entries_in_this_test["storage_configuration"]["disks"].append(
                    {
                        f"encrypted_local{i}": {
                            "type": "encrypted",
                            "disk": f"local{i}",
                            "path": "encrypted/",
                            "key": f"{keys[i]}",
                        }
                    }
                )
            if disks_types[i] == "local":
                entries_in_this_test["storage_configuration"]["policies"][
                    "local_encrypted"
                ]["volumes"]["volume1"].append({"disk": f"local{i}"})
            elif disks_types[i] == "encrypted":
                entries_in_this_test["storage_configuration"]["policies"][
                    "local_encrypted"
                ]["volumes"]["volume1"].append({"disk": f"encrypted_local{i}"})

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)


@TestStep
def create_directories_multi_volume_policy(self, number_of_volumes, numbers_of_disks):
    with Given("I create local disk folders on the server"):
        for j in range(number_of_volumes):
            for i in range(numbers_of_disks[j]):
                create_directory(path=f"/disk_local{j}{i}/")


@TestStep
def add_config_multi_volume_policy(
    self, number_of_volumes, numbers_of_disks, disks_types, keys, move_factor=False
):
    entries = {
        "storage_configuration": {
            "disks": [],
            "policies": {"local_encrypted": {"volumes": {}}},
        }
    }
    with Given("I set up parameters"):
        entries_in_this_test = copy.deepcopy(entries)
        for j in range(number_of_volumes):
            for i in range(numbers_of_disks[j]):
                if disks_types[j][i] == "local":
                    entries_in_this_test["storage_configuration"]["disks"].append(
                        {f"local{j}{i}": {"path": f"/disk_local{j}{i}/"}}
                    )
                elif disks_types[j][i] == "encrypted":
                    entries_in_this_test["storage_configuration"]["disks"].append(
                        {f"local{j}{i}": {"path": f"/disk_local{j}{i}/"}}
                    )
                    entries_in_this_test["storage_configuration"]["disks"].append(
                        {
                            f"encrypted_local{j}{i}": {
                                "type": "encrypted",
                                "disk": f"local{j}{i}",
                                "path": "encrypted/",
                                "key": f"{keys[j][i]}",
                            }
                        }
                    )

        for j in range(number_of_volumes):
            entries_in_this_test["storage_configuration"]["policies"][
                "local_encrypted"
            ]["volumes"][f"volume{j}"] = []

        for j in range(number_of_volumes):
            for i in range(numbers_of_disks[j]):
                if disks_types[j][i] == "local":
                    entries_in_this_test["storage_configuration"]["policies"][
                        "local_encrypted"
                    ]["volumes"][f"volume{j}"].append({"disk": f"local{j}{i}"})
                elif disks_types[j][i] == "encrypted":
                    entries_in_this_test["storage_configuration"]["policies"][
                        "local_encrypted"
                    ]["volumes"][f"volume{j}"].append(
                        {"disk": f"encrypted_local{j}{i}"}
                    )
        if move_factor:
            entries_in_this_test["storage_configuration"]["policies"][
                "local_encrypted"
            ]["move_factor"] = "0.99"

    with And("I add storage configuration that uses encrypted disk"):
        add_encrypted_disk_configuration(entries=entries_in_this_test, restart=True)


@TestStep
def get_random_string(self, length, cluster=None, steps=True, *args, **kwargs):
    cluster = self.context.cluster if cluster is None else cluster
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8") as fd:
        cluster.command(
            None,
            f"cat /dev/urandom | tr -dc 'A-Za-z0-9#$&()*+,-./:;<=>?@[\]^_~' | head -c {length} > {fd.name}",
            steps=steps,
            *args,
            **kwargs,
        )
        fd.seek(0)
        return fd.read()


@TestStep(Given)
def start_clickhouse_process(self, node=None, manual_cleanup=False, user=None):
    """Start ClickHouse server services."""
    node = self.context.node if node is None else node
    try:
        node.start_clickhouse(user=user)
        yield
    finally:
        if not manual_cleanup:
            node.stop_clickhouse()
            node.user = None
