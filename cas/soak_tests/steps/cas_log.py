"""Dump system.cas_log from the soak replicas before the cluster is removed.

The table lives on the data volume. Cluster cleanup drops that volume, and the
CI upload step runs after cleanup. The artifact globs keep ``*_instances/**/*.log``,
so the dump is written there, while the servers are still up.
"""

import os
import time
import urllib.error
import urllib.request

# Host ports from soak_tests_env/docker-compose.yml. clickhouse1 is 8123.
DEFAULT_NODES = {"clickhouse1": 8123, "clickhouse2": 8124}
_FLUSH = "SYSTEM FLUSH LOGS"
_QUERY = "SELECT * FROM system.cas_log FORMAT TSVWithNames"


def _post(port, sql, timeout, dest=None):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/",
        data=sql.encode("utf-8"),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if dest is None:
                resp.read()
                return
            with open(dest, "wb") as out:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code}: {body[:2000]}") from e


def dump_cas_logs(dest_dir, nodes=None, post=None, attempts=5, pause_s=5):
    """Write one TSV-with-names file per replica.

    A replica that never answers gets ``<name>.cas_log.err.log`` and no final
    table dump. Returns a status string per node. Does not raise.
    """
    nodes = DEFAULT_NODES if nodes is None else nodes
    post = _post if post is None else post
    os.makedirs(dest_dir, exist_ok=True)
    statuses = []
    for name, port in nodes.items():
        dest = os.path.join(dest_dir, f"{name}.cas_log.log")
        tmp = dest + ".tmp"
        err_path = os.path.join(dest_dir, f"{name}.cas_log.err.log")
        last = None
        for attempt in range(attempts):
            try:
                post(port, _FLUSH, 60, None)
                post(port, _QUERY, 900, tmp)
                os.replace(tmp, dest)
                last = None
                break
            except Exception as e:
                last = e
                if os.path.exists(tmp):
                    os.remove(tmp)
                if attempt + 1 < attempts and pause_s:
                    time.sleep(pause_s)
        if last is None:
            if os.path.exists(err_path):
                os.remove(err_path)
            statuses.append((name, f"ok {os.path.getsize(dest)} bytes"))
        else:
            with open(err_path, "w", encoding="utf-8") as err:
                err.write(f"{last}\n")
            statuses.append((name, f"failed: {last}"))
    return statuses
