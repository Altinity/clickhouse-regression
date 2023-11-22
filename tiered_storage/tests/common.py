#  Copyright 2019, Altinity LTD. All Rights Reserved.
#
#  All information contained herein is, and remains the property
#  of Altinity LTD. Any dissemination of this information or
#  reproduction of this material is strictly forbidden unless
#  prior written permission is obtained from Altinity LTD.
#
import random
import tempfile

from testflows.core import When, And
from helpers.cluster import QueryRuntimeException
from s3.tests.common import add_config
from helpers.common import create_xml_config_content
from contextlib import contextmanager


def get_random_string(cluster, length, steps=True, *args, **kwargs):
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


def get_used_disks_for_table(node, name, step=When, steps=True):
    def get_used_disks():
        sql = f"select disk_name from system.parts where table == '{name}' and active=1 order by modification_time"
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
            f" AND part_name = '{part_name}' ORDER BY event_time DESC LIMIT 1"
        ).output
    return path.strip()


def get_paths_for_partition_from_part_log(node, table, partition_id, step=When):
    with step("I flush logs"):
        node.query("SYSTEM FLUSH LOGS")
    with And(f"get path_on_disk for partition id {partition_id}"):
        paths = node.query(
            f"SELECT path_on_disk FROM system.part_log WHERE table = '{table}'"
            f" AND partition_id = '{partition_id}' ORDER BY event_time DESC"
        ).output
    return paths.strip().split("\n")


def produce_alter_move(node, name, steps=True, random_seed=None, *args, **kwargs):
    myrandom = random.Random(random_seed)
    move_type = myrandom.choice(["PART", "PARTITION"])

    if move_type == "PART":
        for _ in range(10):
            try:
                parts = (
                    node.query(
                        f"SELECT name from system.parts where table = '{name}' and active = 1",
                        steps=steps,
                        *args,
                        **kwargs,
                    )
                    .output.strip()
                    .split("\n")
                )
                if parts != [""]:
                    break
            except QueryRuntimeException:
                pass
        else:
            raise Exception("Cannot select from system.parts")

        assert "" not in parts, str(parts)

        move_part = myrandom.choice(["'" + part + "'" for part in parts])
    else:
        move_part = myrandom.choice([201903, 201904])

    move_disk = random.choice(["DISK", "VOLUME"])
    if move_disk == "DISK":
        move_volume = myrandom.choice(["'external'", "'jbod1'", "'jbod2'"])
    else:
        move_volume = myrandom.choice(["'main'", "'external'"])
    try:
        node.query(
            f"ALTER TABLE {name} MOVE {move_type} {move_part} TO {move_disk} {move_volume}",
            steps=steps,
            *args,
            **kwargs,
        )
    except QueryRuntimeException:
        pass


@contextmanager
def add_storage_config(
    with_minio=False, with_aws_s3=False, with_gcs_s3=False, environ=None
):
    """Add the minio storage config to storage_configuration.xml."""
    if with_minio:
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "jbod1": {"path": "/jbod1/"},
            "jbod2": {"path": "/jbod2/", "keep_free_space_bytes": "10485760"},
            "jbod3": {"path": "/jbod3/", "keep_free_space_ratio": "0.5"},
            "external": {
                "type": "s3",
                "endpoint": "http://minio:9001/root/data/",
                "access_key_id": "minio",
                "secret_access_key": "minio123",
            },
        }
    elif with_aws_s3:
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "jbod1": {"path": "/jbod1/"},
            "jbod2": {"path": "/jbod2/", "keep_free_space_bytes": "10485760"},
            "jbod3": {"path": "/jbod3/", "keep_free_space_ratio": "0.5"},
            "external": {
                "type": "s3",
                "endpoint": f"{environ['S3_AMAZON_URI']}",
                "access_key_id": f"{environ['S3_AMAZON_KEY_ID']}",
                "secret_access_key": f"{environ['S3_AMAZON_ACCESS_KEY']}",
            },
        }

    elif with_gcs_s3:
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "jbod1": {"path": "/jbod1/"},
            "jbod2": {"path": "/jbod2/", "keep_free_space_bytes": "10485760"},
            "jbod3": {"path": "/jbod3/", "keep_free_space_ratio": "0.5"},
            "external": {
                "type": "s3",
                "endpoint": f"{environ['GCS_URI']}",
                "access_key_id": f"{environ['GCS_KEY_ID']}",
                "secret_access_key": f"{environ['GCS_KEY_SECRET']}",
            },
        }

    else:
        disks = {
            "default": {"keep_free_space_bytes": "1024"},
            "jbod1": {"path": "/jbod1/"},
            "jbod2": {"path": "/jbod2/", "keep_free_space_bytes": "10485760"},
            "jbod3": {"path": "/jbod3/", "keep_free_space_ratio": "0.5"},
            "external": {"path": "/external/"},
        }

    policies = {
        "one_small_disk": {"volumes": {"main": {"disk": "jbod1"}}},
        "small_jbod_with_external": {
            "volumes": {"main": {"disk": "jbod1"}, "external": {"disk": "external"}}
        },
        "jbods": {
            "volumes": {
                "main": [{"disk": "jbod1"}, {"disk": "jbod2"}],
            }
        },
        "jbods_with_external": {
            "volumes": {
                "main": [
                    {"disk": "jbod1"},
                    {"disk": "jbod2"},
                    {"max_data_part_size_bytes": "10485760"},
                ],
                "external": {"disk": "external"},
            }
        },
        "moving_jbod_with_external": {
            "volumes": {
                "main": {"disk": "jbod1"},
                "external": {"disk": "external"},
            },
            "move_factor": "0.7",
        },
        "jbods_with_external_ratio": {
            "volumes": {
                "main": [
                    {"disk": "jbod1"},
                    {"disk": "jbod2"},
                    {"max_data_part_size_ratio": "0.25"},
                ],
                "external": {"disk": "external"},
            }
        },
        "moving_max_jbod_with_external": {
            "volumes": {
                "main": {"disk": "jbod1"},
                "external": {"disk": "external"},
            },
            "move_factor": "1",
        },
        "moving_min_jbod_with_external": {
            "volumes": {
                "main": {"disk": "jbod1"},
                "external": {"disk": "external"},
            },
            "move_factor": "0",
        },
        "default_disk_with_external": {
            "volumes": {
                "small": [{"disk": "default"}, {"max_data_part_size_bytes": "2097152"}],
                "big": [{"disk": "external"}, {"max_data_part_size_bytes": "20971520"}],
            }
        },
        "jbod1_with_jbod2": {
            "volumes": {
                "main": {"disk": "jbod1"},
                "external": {"disk": "jbod2"},
            },
        },
        "fast_med_and_slow": {
            "volumes": {
                "fast": {"disk": "jbod1"},
                "medium": {"disk": "jbod2"},
                "slow": {"disk": "external"},
            },
        },
        "only_jbod1": {"volumes": {"main": {"disk": "jbod1"}}},
        "only_jbod2": {"volumes": {"main": {"disk": "jbod2"}}},
        "only_jbod3": {"volumes": {"main": {"disk": "jbod3"}}},
        "special_warning_zero_volume": {
            "volumes": {
                "special_warning_zero_volume": [
                    {"disk": "default"},
                    {"max_data_part_size_bytes": "0"},
                ],
                "special_warning_default_volume": {"disk": "external"},
                "special_warning_small_volume": [
                    {"disk": "jbod1"},
                    {"max_data_part_size_bytes": "1024"},
                ],
                "special_warning_big_volume": [
                    {"disk": "jbod2"},
                    {"max_data_part_size_bytes": "1024000000"},
                ],
            }
        },
    }
    entries = {"storage_configuration": {"disks": [disks], "policies": policies}}
    config = create_xml_config_content(entries, "storage_configuration.xml")
    return add_config(config, restart=True)
