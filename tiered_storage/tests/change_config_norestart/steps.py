#  Copyright 2020, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import os
import json
import xml.etree.ElementTree as xmltree

from testflows.core import *
from testflows.asserts import error
from tiered_storage.tests.common import get_used_disks_for_table

storage_config = "storage_configuration.xml"
base_config = """
<yandex>
    <storage_configuration>
        <disks></disks>
        <policies></policies>
    </storage_configuration>
</yandex>
"""


def xml_indent(elem, level=0):
    i = "\n" + level * (4 * " ")
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            xml_indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def check_disk_in_system_disks_by_name(node, name, is_present=True):
    """Checking disk name is either present or not present in the
    system.disks table."""
    with By("reading system.disks table"):
        r = node.query("SELECT name FROM system.disks FORMAT JSON").output.strip()

    with And("converting data to json"):
        disks = set([disk["name"] for disk in json.loads(r)["data"]])

    with Then(
        f"checking disk name is{' not' if not is_present else ''} present",
        description=name,
    ):
        if is_present:
            assert name in disks, error()
        else:
            assert name not in disks, error()


@TestStep
def checking_disk_is_present_in_system_disks_by_name(self, node, name):
    """Checking disk name is present in system.disks table."""
    check_disk_in_system_disks_by_name(node, name, is_present=True)


@TestStep
def checking_disk_is_not_present_in_system_disks_by_name(self, node, name):
    """Checking disk name is not present in system.disks table."""
    check_disk_in_system_disks_by_name(node, name, is_present=False)


def check_disks_in_volume_in_system_policies_by_name(
    node, policy, volume, disks, is_present=True
):
    with By("reading system.storage_policies"):
        result = node.query(
            f"SELECT * FROM system.storage_policies WHERE policy_name = '{policy}' AND volume_name = '{volume}' FORMAT JSON"
        ).output

    with And("convert result data to JSON"):
        volume_data = json.loads(result)["data"][0]

    with And("I extract disk names"):
        volume_disks = set(volume_data["disks"])

    with Then(
        f"checking disks name are{' not' if not is_present else ''} present",
        description=disks,
    ):
        for disk in disks:
            if is_present:
                assert disk in volume_disks, error()
            else:
                assert disk not in volume_disks, error()


@TestStep
def checking_disks_in_volume_is_present_in_system_policies_by_name(
    self, node, policy, volume, disks
):
    check_disks_in_volume_in_system_policies_by_name(node, policy, volume, disks)


@TestStep
def checking_disks_in_volume_is_not_present_in_system_policies_by_name(
    self, node, policy, volume, disks
):
    check_disks_in_volume_in_system_policies_by_name(
        node, policy, volume, disks, is_present=False
    )


def check_volume_in_system_policies_by_name(node, policy, name, is_present=True):
    with By("reading system.storage_policies"):
        result = node.query(
            f"SELECT * FROM system.storage_policies WHERE policy_name = '{policy}' FORMAT JSON"
        ).output

    with And("convert result data to JSON"):
        policy_data = json.loads(result)["data"]

    with And("I extract volume names"):
        volumes = set([entry["volume_name"] for entry in policy_data])

    with Then(
        f"checking volume name is{' not' if not is_present else ''} present",
        description=name,
    ):
        if is_present:
            assert name in volumes, error()
        else:
            assert name not in volumes, error()


@TestStep
def checking_volume_is_present_in_system_policies_by_name(self, node, policy, name):
    check_volume_in_system_policies_by_name(node, policy, name)


@TestStep
def checking_volume_is_not_present_in_system_policies_by_name(self, node, policy, name):
    check_volume_in_system_policies_by_name(node, policy, name, is_present=False)


def check_policy_in_system_policies_by_name(node, name, is_present=True):
    with By("reading system.storage_policies"):
        query = "SELECT policy_name FROM system.storage_policies FORMAT JSON"
        result = node.query(query).output

    with And("get set of policies"):
        policies = set(entry["policy_name"] for entry in json.loads(result)["data"])

    with Then(
        f"checking name is{' not' if not is_present else ''} present", description=name
    ):
        if is_present:
            assert name in policies, error()
        else:
            assert name not in policies, error()


@TestStep
def checking_policy_is_present_in_system_policies_by_name(self, node, name):
    check_policy_in_system_policies_by_name(node, name)


@TestStep
def checking_policy_is_not_present_in_system_policies_by_name(self, node, name):
    check_policy_in_system_policies_by_name(node, name, is_present=False)


@TestStep
def reloading_config(self, node, restart=False, config=storage_config):
    """Reloading configuration."""
    if not restart:
        with By("dumping current config"):
            node.command(f"cat /etc/clickhouse-server/config.d/{config}", steps=False)
        with By("executing sytem reload config"):
            node.query("SELECT name FROM system.disks")
            node.query("SELECT policy_name FROM system.storage_policies")
            node.query("SYSTEM RELOAD CONFIG")
    else:
        with By("restarting the server"):
            node.restart()


@TestStep
def adding_disks_to_volume(
    self, node, policy, volume, disks, inplace=True, config=storage_config
):
    """Add new disks to a volume."""
    if not inplace:
        with By("reading current disks from system.storage_policies"):
            query = (
                "SELECT * FROM system.storage_policies "
                f"WHERE policy_name = '{policy}' AND volume_name = '{volume}' FORMAT JSON"
            )

            result = node.query(query).output
            volume_data = json.loads(result)["data"][0]
            volume_disks = set(volume_data["disks"])

        with And("adding new disk to the list of disks"):
            volume_disks.union(set(disks))

        By(
            run=adding_volume_to_policy,
            args=args(
                node=node,
                policy=policy,
                name=volume,
                disks=volume_disks,
                inplace=inplace,
            ),
        )
    else:
        config_path = os.path.join(node.config_d_dir, config)
        root = xmltree.fromstring(
            node.command(f"cat {config_path}", steps=False).output.strip()
        )
        volume_element = (
            root.find("storage_configuration")
            .find("policies")
            .find(policy)
            .find("volumes")
            .find(volume)
        )
        for disk in disks:
            new_disk = xmltree.Element("disk")
            new_disk.text = disk
            volume_element.append(new_disk)
        xml_indent(root)
        new_config = str(xmltree.tostring(root), "utf-8")
        node.command(
            f"cat <<HEREDOC > {config_path}\n{new_config}\nHEREDOC", steps=False
        )


@TestStep
def adding_volume_to_policy(
    self, node, policy, name, disks, inplace=True, config=storage_config
):
    if not inplace:
        config_path = os.path.join(
            node.config_d_dir, f"policy_{policy}_volume_{name}.xml"
        )
        root = xmltree.ElementTree(xmltree.fromstring(base_config)).getroot()
        policy_element = xmltree.Element(policy)
        volumes_element = xmltree.Element("volumes")
        policy_element.append(volumes_element)
        root.find("storage_configuration").find("policies").append(policy_element)
    else:
        config_path = os.path.join(node.config_d_dir, config)
        root = xmltree.fromstring(
            node.command(f"cat {config_path}", steps=False).output.strip()
        )
    new_volume = xmltree.Element(name)
    for disk in disks:
        new_disk = xmltree.Element("disk")
        new_disk.text = disk
        new_volume.append(new_disk)
    root.find("storage_configuration").find("policies").find(policy).find(
        "volumes"
    ).append(new_volume)
    xml_indent(root)
    new_config = str(xmltree.tostring(root), "utf-8")
    node.command(f"cat <<HEREDOC > {config_path}\n{new_config}\nHEREDOC", steps=False)


@TestStep
def removing_disk(self, node, name, inplace=True, config=storage_config):
    """Removing disk from storage configuration."""
    if not inplace:
        By(run=removing_config_file, args=args(node=node, name=f"disk_{name}"))
    else:
        config_path = os.path.join(node.config_d_dir, config)
        root = xmltree.fromstring(
            node.command(f"cat {config_path}", steps=False).output.strip()
        )
        disks_element = root.find("storage_configuration").find("disks")
        disk_element = root.find("storage_configuration").find("disks").find(name)
        disks_element.remove(disk_element)
        xml_indent(root)
        new_config = str(xmltree.tostring(root), "utf-8")
        node.command(
            f"cat <<HEREDOC > {config_path}\n{new_config}\nHEREDOC", steps=False
        )


@TestStep
def removing_disks_from_volume(
    self, node, policy, volume, disks, inplace=True, config=storage_config
):
    if not inplace:
        By(
            run=removing_config_file,
            args=args(node=node, name=f"policy_{policy}_volume_{volume}"),
        )
    else:
        config_path = os.path.join(node.config_d_dir, config)
        root = xmltree.fromstring(
            node.command(f"cat {config_path}", steps=False).output.strip()
        )
        volume_element = (
            root.find("storage_configuration")
            .find("policies")
            .find(policy)
            .find("volumes")
            .find(volume)
        )
        for disk in volume_element:
            if disk.text in disks:
                volume_element.remove(disk)
        xml_indent(root)
        new_config = str(xmltree.tostring(root), "utf-8")
        node.command(
            f"cat <<HEREDOC > {config_path}\n{new_config}\nHEREDOC", steps=False
        )


@TestStep
def removing_volume(self, node, policy, name, inplace=True, config=storage_config):
    """Removing volume from the policy in the storage configuration."""
    if not inplace:
        By(
            run=removing_config_file,
            args=args(node=node, name=f"policy_{policy}_volume_{name}"),
        )
    else:
        config_path = os.path.join(node.config_d_dir, config)
        root = xmltree.fromstring(
            node.command(f"cat {config_path}", steps=False).output.strip()
        )
        volumes_element = (
            root.find("storage_configuration")
            .find("policies")
            .find(policy)
            .find("volumes")
        )
        volume_element = volumes_element.find(name)
        volumes_element.remove(volume_element)
        xml_indent(root)
        new_config = str(xmltree.tostring(root), "utf-8")
        node.command(
            f"cat <<HEREDOC > {config_path}\n{new_config}\nHEREDOC", steps=False
        )


@TestStep
def removing_policy(self, node, name, inplace=True, config=storage_config):
    """Removing a policy from the storage configuration."""
    if not inplace:
        By(run=removing_config_file, args=args(node=node, name=f"policy_{name}"))
    else:
        config_path = os.path.join(node.config_d_dir, config)
        root = xmltree.fromstring(
            node.command(f"cat {config_path}", steps=False).output.strip()
        )
        policies_element = root.find("storage_configuration").find("policies")
        policy_element = policies_element.find(name)
        policies_element.remove(policy_element)
        xml_indent(root)
        new_config = str(xmltree.tostring(root), "utf-8")
        node.command(
            f"cat <<HEREDOC > {config_path}\n{new_config}\nHEREDOC", steps=False
        )


@TestStep
def adding_disk(
    self,
    node,
    name,
    path,
    disk_space_bytes=None,
    keep_free_space_bytes=None,
    keep_free_space_ratio=None,
    inplace=False,
    config=storage_config,
):
    if not inplace:
        config_path = os.path.join(node.config_d_dir, f"disk_{name}.xml")
        root = xmltree.ElementTree(xmltree.fromstring(base_config)).getroot()
    else:
        config_path = os.path.join(node.config_d_dir, config)
        root = xmltree.fromstring(
            node.command(f"cat {config_path}", steps=False).output.strip()
        )

    new_disk = xmltree.Element(name)
    new_path = xmltree.Element("path")
    new_path.text = path
    new_disk.append(new_path)

    params = dict(
        disk_space_bytes=disk_space_bytes,
        keep_free_space_bytes=keep_free_space_bytes,
        keep_free_space_ratio=keep_free_space_ratio,
    )

    for param, value in params.items():
        if value is None:
            continue
        new_param = xmltree.Element(param)
        new_param.text = str(value)
        new_disk.append(new_param)

    root.find("storage_configuration").find("disks").append(new_disk)
    xml_indent(root)
    new_config = str(xmltree.tostring(root), "utf-8")
    node.command(f"cat <<HEREDOC > {config_path}\n{new_config}\nHEREDOC", steps=False)


@TestStep
def adding_policy(self, node, name, volumes, inplace=False, config=storage_config):
    if not inplace:
        config_path = os.path.join(node.config_d_dir, f"policy_{name}.xml")
        root = xmltree.ElementTree(xmltree.fromstring(base_config)).getroot()
    else:
        config_path = os.path.join(node.config_d_dir, config)
        root = xmltree.fromstring(
            node.command(f"cat {config_path}", steps=False).output.strip()
        )
    new_policy = xmltree.Element(name)
    new_volumes = xmltree.Element("volumes")
    for volume in volumes:
        new_volume = xmltree.Element(volume["name"])
        for disk in volume["disks"]:
            new_disk = xmltree.Element("disk")
            new_disk.text = disk
            new_volume.append(new_disk)
        new_volumes.append(new_volume)
    new_policy.append(new_volumes)
    root.find("storage_configuration").find("policies").append(new_policy)
    xml_indent(root)
    new_config = str(xmltree.tostring(root), "utf-8")
    node.command(f"cat <<HEREDOC > {config_path}\n{new_config}\nHEREDOC", steps=False)


@TestStep
def creating_config_file(self, node, name, contents):
    """Create new configuration file."""
    filename = f"/etc/clickhouse-server/config.d/{name}.xml"

    with By(
        f"creating file",
        description=f"{filename} with contents\n{contents}",
        format_description=False,
    ):
        node.command(f"cat <<HEREDOC > {filename}\n{contents}\nHEREDOC", steps=False)
        node.command(f"cat {filename}", steps=False)
        node.command("ls /etc/clickhouse-server/config.d", steps=False)


@TestStep
def removing_config_file(self, node, name):
    """Remove configuration file."""
    filename = f"/etc/clickhouse-server/config.d/{name}.xml"

    with By("removing file", description=filename, format_description=False):
        node.command(f"rm -f {filename}")


@TestStep
def change_table_policy(self, node, table, policy):
    """Change table policy."""
    node.query(f"ALTER TABLE {table} MODIFY SETTING storage_policy='{policy}'")


@TestStep
def attach_partition_from_table(self, node, table, from_table, partition):
    """Attach partition from another table with the same structure."""
    node.query(f"ALTER TABLE {table} ATTACH PARTITION '{partition}' FROM {from_table}")


@TestStep
def replace_partition_from_table(self, node, table, from_table, partition):
    """Replace partition from another table with the same structure."""
    node.query(f"ALTER TABLE {table} REPLACE PARTITION '{partition}' FROM {from_table}")


@TestStep
def moving_part_to_disk(self, node, table, part, disk, **kwargs):
    node.query(f"ALTER TABLE {table} MOVE PART {part} TO DISK {disk}", **kwargs)


@TestStep
def moving_partition_to_disk(self, node, table, partition, disk, **kwargs):
    node.query(
        f"ALTER TABLE {table} MOVE PARTITION {partition} TO DISK {disk}", **kwargs
    )


@TestStep
def moving_part_to_volume(self, node, table, part, volume, **kwargs):
    node.query(f"ALTER TABLE {table} MOVE PART {part} TO VOLUME {volume}", **kwargs)


@TestStep
def moving_partition_to_volume(self, node, table, partition, volume, **kwargs):
    node.query(
        f"ALTER TABLE {table} MOVE PARTITION {partition} TO VOLUME {volume}", **kwargs
    )


@TestStep
def moving_part_or_partition(self, node, **kwargs):
    """Move part or partition to disk or volume.

    :param node: node
    :param table: table name (kwargs)
    :param part: part to move (kwargs)
    :param partition: partition to move (kwargs)
    :param disk: disk to move to (kwargs)
    :param volume: volume to move to (kwargs)
    """
    if kwargs is None:
        return

    table = kwargs.pop("table")
    part = kwargs.pop("part", None)
    partition = kwargs.pop("partition", None)
    disk = kwargs.pop("disk", None)
    volume = kwargs.pop("volume", None)

    if part and disk:
        By(
            run=moving_part_to_disk,
            args=args(node=node, table=table, part=part, disk=disk),
        )
    elif part and volume:
        By(
            run=moving_part_to_volume,
            args=args(node=node, table=table, part=part, volume=volume),
        )
    elif partition and disk:
        By(
            run=moving_partition_to_disk,
            args=args(node=node, table=table, partition=partition, disk=disk),
        )
    elif partition and volume:
        By(
            run=moving_partition_to_volume,
            args=args(node=node, table=table, partition=partition, volume=volume),
        )
    else:
        raise ValueError(f"invalid arguments")

    By(run=moving_part_or_partition)


@TestStep
def dropping_table(self, node, name):
    node.query(
        f"""
        DROP TABLE IF EXISTS {name} SYNC
    """
    )


@TestStep
def creating_mergetree_table(self, node, name, policy, cleanup=True):
    try:
        node.query(
            f"""
            CREATE TABLE {name} (
                EventDate DateTime,
                number UInt64
            ) ENGINE = MergeTree
            ORDER BY tuple()
            PARTITION BY toYYYYMM(EventDate)
            SETTINGS storage_policy='{policy}'
        """
        )
    finally:
        if cleanup:

            def callback():
                By(run=dropping_table, args=args(node=node, name=name))

            self.context.cleanup(callback)


@TestStep
def creating_replicated_mergetree_table(
    self, node, name, replica, policy, cleanup=True
):
    try:
        node.query(
            f"""
            CREATE TABLE {name} (
                EventDate DateTime,
                number UInt64
            ) ENGINE = ReplicatedMergeTree('/clickhouse/{name}', '{replica}')
            ORDER BY tuple()
            PARTITION BY toYYYYMM(EventDate)
            SETTINGS storage_policy='{policy}', old_parts_lifetime=1, cleanup_delay_period=1, cleanup_delay_period_random_add=2
        """
        )
    finally:
        if cleanup:

            def callback():
                By(run=dropping_table, args=args(node=node, name=name))

            self.context.cleanup(callback)


@TestStep
def creating_table(self, node, cleanup=True, **kwargs):
    if not kwargs:
        return

    engine = kwargs.pop("engine")
    name = kwargs.pop("name")
    policy = kwargs.pop("policy")
    replica = kwargs.pop("replica", None)

    if engine == "MergeTree":
        By(
            run=creating_mergetree_table,
            args=args(node=node, name=name, policy=policy, cleanup=cleanup),
        )
    elif engine == "ReplicatedMergeTree":
        By(
            run=creating_replicated_mergetree_table,
            args=args(
                node=node, name=name, replica=replica, policy=policy, cleanup=cleanup
            ),
        )
    else:
        raise TypeError("invalid engine")

    By(run=creating_table, args=args(node=node))


@TestStep
def inserting_into_table(self, node, name, count):
    node.query(
        f"""
        INSERT INTO {name} (EventDate, number)
        WITH
            toDateTime(toDate('2020-01-01')) as start_time
        SELECT
            start_time + INTERVAL rand() % 86400 SECOND as EventDate,
            rand() % 1048576 as number
        FROM system.numbers
        LIMIT {count}
    """
    )


@TestStep
def selecting_from_table(self, node, name, count):
    with By("reading number of rows in the table"):
        r = node.query(f"SELECT count() FROM {name}").output.strip()
    with Then("checking against the expected value", description=f"{count}"):
        assert r == str(count), error()


@TestStep
def check_used_disks_for_table(self, node, name, disks):
    disks = set(disks)
    used_disks = set(get_used_disks_for_table(node, name))

    with Then("check disks should match"):
        assert disks == used_disks, error()
