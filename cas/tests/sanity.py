import re
import time

from testflows.core import *
from testflows.asserts import error
from helpers.common import getuid


def rustfs_objects(self, pool_prefix):
    """Return the RustFS listing after removing leaked terminal responses."""
    objects = self.context.cluster.command(
        "mc",
        f"mc --no-color find minio/warehouse/{pool_prefix} --print '{{}}'",
    )
    clean_output = re.sub(
        r"\x1b\](?:10|11|12);rgb:[0-9a-fA-F/]+(?:\x07|\x1b\\)",
        "",
        objects.output,
    )
    clean_output = re.sub(r"\x1b\[\d+;\d+R", "", clean_output)
    pool_path = f"minio/warehouse/{pool_prefix}/"
    keys = [
        line.strip().split(pool_path, 1)[1]
        for line in clean_output.splitlines()
        if pool_path in line
    ]

    return clean_output, keys


@TestScenario
def replicated_merge_tree_on_content_addressed_storage(self):
    """Create a replicated MergeTree on a shared CAS pool and show its objects."""
    nodes = self.context.nodes
    table_name = "cas_sanity"
    run_id = getuid()
    pool_prefix = f"cas_sanity_pool_{run_id}"
    replication_path = f"/clickhouse/tables/{table_name}_{run_id}"

    with Given("a ReplicatedMergeTree on three nodes sharing one CAS pool"):
        for replica_number, node in enumerate(nodes, start=1):
            node.query(f"DROP TABLE IF EXISTS {table_name} SYNC")
            node.query(
                f"""
                CREATE TABLE {table_name}
                (
                    id UInt64,
                    value String
                )
                ENGINE = ReplicatedMergeTree(
                    '{replication_path}',
                    'replica{replica_number}'
                )
                ORDER BY id
                SETTINGS disk = disk(
                    type = object_storage,
                    object_storage_type = s3,
                    metadata_type = content_addressed,
                    server_root_id = 'cas-sanity-{run_id}-node{replica_number}',
                    endpoint = 'http://minio:9000/warehouse/{pool_prefix}/',
                    access_key_id = '{self.context.minio_root_user}',
                    secret_access_key = '{self.context.minio_root_password}'
                )
                """
            )

    with When("I write two parts on the first replica and merge them"):
        nodes[0].query(
            f"INSERT INTO {table_name} SELECT number, toString(number % 10) "
            "FROM numbers(5)"
        )
        nodes[0].query(
            f"INSERT INTO {table_name} SELECT number + 5, toString((number + 5) % 10) "
            "FROM numbers(5)"
        )
        nodes[0].query(f"OPTIMIZE TABLE {table_name} FINAL")

    with Then("all three replicas read the same data"):
        for replica_number, node in enumerate(nodes, start=1):
            node.query(f"SYSTEM SYNC REPLICA {table_name}")
            result = node.query(
                f"SELECT count(), sum(id), uniqExact(value) FROM {table_name}"
            )
            assert result.output.strip() == "10\t45\t10", error(
                f"replica{replica_number}: {result.output}"
            )
            pause()

    with And("I display the physical CAS layout stored in RustFS"):
        clean_output, keys = rustfs_objects(self, pool_prefix)
        note(f"RustFS objects under {pool_prefix}/:\n{clean_output}")

        blob_keys = [key for key in keys if key.startswith("blobs/")]
        manifest_keys = [key for key in keys if key.startswith("cas/manifests/")]
        ref_keys = [key for key in keys if key.startswith("cas/refs/")]

        assert blob_keys, error(f"no blobs found:\n{clean_output}")
        assert manifest_keys, error(f"no manifests found:\n{clean_output}")
        assert ref_keys, error(f"no refs found:\n{clean_output}")

        blob_data_keys = [key for key in blob_keys if not key.endswith(".meta")]
        blob_meta_keys = [key for key in blob_keys if key.endswith(".meta")]
        assert blob_data_keys, error("no content blobs found")
        assert blob_meta_keys, error("no blob .meta sidecars found")

        for key in blob_data_keys:
            match = re.fullmatch(r"blobs/ch128/([0-9a-f]{2})/([0-9a-f]{32})", key)
            assert match is not None, error(f"invalid blob key: {key}")
            assert match.group(1) == match.group(2)[:2], error(
                f"blob shard does not match its hash: {key}"
            )

        for key in blob_meta_keys:
            assert re.fullmatch(
                r"blobs/ch128/([0-9a-f]{2})/([0-9a-f]{32})\.meta", key
            ), error(f"invalid blob metadata key: {key}")

        assert {f"{key}.meta" for key in blob_data_keys} == set(blob_meta_keys), error(
            "every content blob must have exactly one .meta sidecar"
        )

        for key in manifest_keys:
            assert re.fullmatch(
                r"cas/manifests/.+/[0-9a-f]{16}-[0-9a-f]{16}/\d{6}\.zst",
                key,
            ), error(f"part manifest must use the expected .zst path: {key}")

        for key in ref_keys:
            is_ref_shard = re.fullmatch(r"cas/refs/.+/\d+", key)
            is_ref_log = re.fullmatch(
                r"cas/refs/.+/_log/[0-9a-f]{16}-[0-9a-f]{16}\.zst", key
            )
            assert is_ref_shard or is_ref_log, error(
                f"ref must be an extensionless numeric shard or a .zst log: {key!r}"
            )

        assert any(key.endswith(".zst") for key in ref_keys), error(
            f"no compressed ref journal entries found:\n{clean_output}"
        )
        assert not any(key.endswith(".parquet") for key in keys), error(
            f"CAS MergeTree objects must not be Parquet files:\n{clean_output}"
        )


@TestFeature
@Name("sanity")
def feature(self):
    """Basic content-addressed MergeTree checks."""
    Scenario(test=replicated_merge_tree_on_content_addressed_storage)()
