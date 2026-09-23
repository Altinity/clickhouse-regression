"""Select the cluster shape a scenario card asks for.

The regression runner always boots the 2-node soak_tests_env. Cards that need
something else say so with ``compose_variant``. This module applies that shape
before the card runs and puts the 2-node config back afterwards.

``multidisk`` and ``s41`` are not switched here. Their disks and policies live
in storage.xml all the time.
"""

import os
import subprocess
import time
import urllib.request

from testflows.core import note

from cas.soak_tests.steps.card import ClusterView, cluster_from_context
from cas.soak_tests.steps.http import HttpNode

_SUITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORAGE = os.path.join(_SUITE, "configs", "clickhouse", "config.d", "storage.xml")
_REMOTE = os.path.join(_SUITE, "configs", "clickhouse", "config.d", "remote.xml")
_RUSTFS = "cas_soak_tests_rustfs"

_MODE = {
    "s3faultproxy": "proxy",
    "s3listproxy": "proxy",
    "smalldedupcache": "dedup",
    "gc_shards2": "gc2",
    "tenreplicas": "ten",
}

# Original file bytes, taken the first time a card changes them.
_original = {"storage": None, "remote": None}
_mode = None


def mode_for(variant):
    return _MODE.get(variant)


def ten_nodes():
    return ClusterView([HttpNode("localhost", 8122 + i, name=f"clickhouse{i}") for i in range(1, 11)])


def activate(context, variant):
    """Make ``variant`` the active shape. A no-op when it already is."""
    global _mode
    want = mode_for(variant)
    if want == _mode:
        return
    if _mode is not None:
        _leave(context)
    if want is not None:
        # Record the mode before the work so a failed switch is undone by the next card.
        _mode = want
        note(f"cluster variant: {want}")
        _enter(context, want)


def restore(context):
    """Return to the 2-node minio endpoint. Safe when nothing was switched."""
    activate(context, None)


def _remember():
    if _original["storage"] is None:
        with open(_STORAGE, "rb") as f:
            _original["storage"] = f.read()
    if _original["remote"] is None:
        with open(_REMOTE, "rb") as f:
            _original["remote"] = f.read()


def _write(path, data):
    with open(path, "wb") as f:
        f.write(data)


def _restore_files():
    if _original["storage"] is not None:
        _write(_STORAGE, _original["storage"])
    if _original["remote"] is not None:
        _write(_REMOTE, _original["remote"])


def _patch_storage(edit):
    _remember()
    with open(_STORAGE, "r", encoding="utf-8") as f:
        text = f.read()
    updated = edit(text)
    if updated == text:
        raise RuntimeError(f"storage.xml patch did not match ({_STORAGE})")
    with open(_STORAGE, "w", encoding="utf-8") as f:
        f.write(updated)


def _restart_pair(context):
    context.node.restart_clickhouse(timeout=180)
    context.node2.restart_clickhouse(timeout=180)


def _stop_pair(context):
    context.node.stop_clickhouse(timeout=180)
    context.node2.stop_clickhouse(timeout=180)


def _start_pair(context):
    context.node.start_clickhouse(timeout=180)
    context.node2.start_clickhouse(timeout=180)


def _compose(context, args):
    env = os.environ.copy()
    env.update({k: str(v) for k, v in context.cluster.environ.items()})
    cmd = f"{context.cluster.docker_compose} {args}"
    proc = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-2000:]
        raise RuntimeError(f"docker compose {args} failed: {tail}")
    return proc.stdout


def _container(index):
    out = subprocess.check_output(["docker", "ps", "-a", "--format", "{{.Names}}"], text=True)
    suffix = f"-clickhouse{index}-1"
    for name in out.splitlines():
        if name.endswith(suffix):
            return name
    raise RuntimeError(f"no container matching *{suffix}")


def _wait_ping(port, timeout=180):
    deadline = time.monotonic() + timeout
    url = f"http://127.0.0.1:{port}/ping"
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:
                if resp.status == 200:
                    return
        except Exception:
            time.sleep(2)
    raise RuntimeError(f"clickhouse on port {port} did not answer /ping")


def _drop_user_tables(context):
    cluster = cluster_from_context(context)
    sql = (
        "SELECT database, name FROM system.tables "
        "WHERE database NOT IN ('system', 'INFORMATION_SCHEMA', 'information_schema') "
        "FORMAT TabSeparated"
    )
    for node in cluster.nodes():
        rows = node.query(sql)
        for line in rows.splitlines():
            if "\t" not in line:
                continue
            db, name = line.split("\t", 1)
            node.command(f"DROP TABLE IF EXISTS `{db}`.`{name}` SYNC")


def _wipe_pools():
    subprocess.run(
        [
            "docker", "exec", _RUSTFS, "rm", "-rf",
            "/data/warehouse/soak_pool", "/data/warehouse/s3plain_pool",
        ],
        check=True,
    )


def _proxy_edit(text):
    old = "<endpoint>http://minio:9000/warehouse/soak_pool/</endpoint>"
    new = "<endpoint>http://s3proxy:9000/warehouse/soak_pool/</endpoint>"
    return text.replace(old, new, 1)


def _dedup_edit(text):
    old = "                <expect_continue_min_bytes>65536</expect_continue_min_bytes>\n            </ca>"
    new = (
        "                <expect_continue_min_bytes>65536</expect_continue_min_bytes>\n"
        "                <deduplication_cache_bytes>1048576</deduplication_cache_bytes>\n"
        "            </ca>"
    )
    return text.replace(old, new, 1)


def _gc_edit(text):
    old = "                <gc_interval_sec>10</gc_interval_sec>\n"
    new = old + "                <gc_shards>2</gc_shards>\n"
    return text.replace(old, new, 1)


def _write_ten_remote():
    _remember()
    replicas = []
    for i in range(1, 11):
        replicas.append(
            "                <replica>\n"
            f"                    <host>clickhouse{i}</host>\n"
            "                    <port>9000</port>\n"
            "                </replica>"
        )
    body = (
        "<clickhouse>\n"
        "    <remote_servers>\n"
        "        <replicated_cluster>\n"
        "            <shard>\n"
        + "\n".join(replicas)
        + "\n            </shard>\n"
        "        </replicated_cluster>\n"
        "    </remote_servers>\n"
        "</clickhouse>\n"
    )
    with open(_REMOTE, "w", encoding="utf-8") as f:
        f.write(body)


def _prepare_instance_dirs(context):
    root = os.path.join(context.cluster.environ["CLICKHOUSE_TESTS_DIR"], "_instances")
    script = (
        "for i in 3 4 5 6 7 8 9 10; do "
        "mkdir -p /data/clickhouse$i/database /data/clickhouse$i/logs && "
        "chmod 777 /data/clickhouse$i /data/clickhouse$i/database /data/clickhouse$i/logs; "
        "done"
    )
    subprocess.run(
        ["docker", "run", "--rm", "-v", f"{root}:/data", "alpine", "sh", "-c", script],
        check=True,
    )


def _start_extra_servers():
    # Do not pgrep for "clickhouse server": that pattern matches this shell's own
    # command line, the check succeeds, and the server never starts.
    # compose stop leaves the pid file on the container filesystem.
    cmd = (
        "rm -f /tmp/clickhouse-server.pid; "
        "clickhouse server --config-file=/etc/clickhouse-server/config.xml "
        "--log-file=/var/log/clickhouse-server/clickhouse-server.log "
        "--errorlog-file=/var/log/clickhouse-server/clickhouse-server.err.log "
        "--pidfile=/tmp/clickhouse-server.pid --daemon"
    )
    for i in range(3, 11):
        subprocess.run(["docker", "exec", _container(i), "bash", "-lc", cmd], check=True)


def _enter(context, want):
    if want == "proxy":
        _patch_storage(_proxy_edit)
        _restart_pair(context)
        _wait_ping(8123)
        _wait_ping(8124)
    elif want == "dedup":
        _patch_storage(_dedup_edit)
        _restart_pair(context)
        _wait_ping(8123)
        _wait_ping(8124)
    elif want == "gc2":
        _drop_user_tables(context)
        _stop_pair(context)
        _wipe_pools()
        _patch_storage(_gc_edit)
        _start_pair(context)
        _wait_ping(8123)
        _wait_ping(8124)
    elif want == "ten":
        _write_ten_remote()
        _prepare_instance_dirs(context)
        names = " ".join(f"clickhouse{i}" for i in range(3, 11))
        # --no-recreate keeps containers from the previous compose network, which
        # `down` has already deleted. Recreate only the extra replicas.
        _compose(context, f"--profile tenreplicas up -d --force-recreate --no-deps {names}")
        _start_extra_servers()
        _restart_pair(context)
        for i in range(1, 11):
            _wait_ping(8122 + i)
    else:
        raise RuntimeError(f"unknown cluster variant {want}")


def _leave(context):
    global _mode
    leaving = _mode
    _mode = None
    if leaving == "gc2":
        try:
            _drop_user_tables(context)
        except Exception as e:
            note(f"drop before leaving gc_shards2: {e}")
        _stop_pair(context)
        _restore_files()
        _wipe_pools()
        _start_pair(context)
    elif leaving == "ten":
        names = " ".join(f"clickhouse{i}" for i in range(3, 11))
        _compose(context, f"stop {names}")
        _restore_files()
        _restart_pair(context)
    elif leaving in ("proxy", "dedup"):
        _restore_files()
        _restart_pair(context)
    else:
        _restore_files()
    _wait_ping(8123)
    _wait_ping(8124)
