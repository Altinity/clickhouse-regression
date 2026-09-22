import time

from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle.checker import (
    AGGREGATE_SQL,
    CheckpointFailure,
    compare_aggregates,
    dryrun_subset_check,
    gc_fixpoint_reached,
    is_genuine_hang,
    parse_aggregates,
    require_clean_stale_edge,
    wait_for_pool_consistent,
)
from cas.soak_tests.oracle.fsck import parse_dryrun, parse_fsck_stdout

FSCK_CONFIG = "/etc/clickhouse-server/fsck-only.xml"
FSCK_DISK = "ca_ro"


def refresh_cluster_shells(self):
    """Drop dead docker-exec bash sessions after a node kill/restart."""
    cluster = getattr(self.context, "cluster", None)
    if cluster is None:
        return
    for name in ("clickhouse1", "clickhouse2"):
        try:
            cluster.close_bash(name)
        except Exception:
            pass


def _node_command_retry(self, node, cmd, timeout):
    last = None
    for attempt in range(1, 4):
        try:
            return node.command(cmd, timeout=timeout, no_checks=True)
        except Exception as e:
            last = e
            note(
                f"{node.name} command {type(e).__name__} ({e}); "
                f"refresh shell retry {attempt}/3"
            )
            refresh_cluster_shells(self)
            time.sleep(2)
    raise last


def _nodes(self):
    return list(self.context.nodes)


def _table_filter(table):
    if "." in table:
        database, name = table.split(".", 1)
    else:
        database, name = "ca_soak", table
    return f"database='{database}' AND table='{name}'"


@TestStep(When)
def query_aggregates(self, table, node=None):
    if node is None:
        node = self.context.node
    sql = AGGREGATE_SQL.format(table=table)
    tsv = node.query(sql).output.strip()
    return parse_aggregates(tsv)


@TestStep(Then)
def replicas_match_model(self, table, model, now):
    expected = model.aggregates(now)
    n1 = query_aggregates(table=table, node=self.context.node)
    n2 = query_aggregates(table=table, node=self.context.node2)
    try:
        compare_aggregates(expected, n1, n2)
    except CheckpointFailure as e:
        assert False, error(str(e))
    return expected, n1, n2


def _backlog(self, table):
    where = _table_filter(table)
    total = 0
    for node in _nodes(self):
        total += int(
            node.query(
                f"SELECT count() FROM system.replication_queue WHERE {where} "
                "FORMAT TabSeparated"
            ).output.strip()
            or "0"
        )
        total += int(
            node.query(
                f"SELECT count() FROM system.mutations WHERE {where} AND NOT is_done "
                "FORMAT TabSeparated"
            ).output.strip()
            or "0"
        )
        total += int(
            node.query(
                f"SELECT count() FROM system.merges WHERE {where} FORMAT TabSeparated"
            ).output.strip()
            or "0"
        )
    return total


def _merge_activity(self, table):
    where = _table_filter(table)
    active = 0
    for node in _nodes(self):
        active += int(
            node.query(
                f"SELECT count() FROM system.merges WHERE {where} FORMAT TabSeparated"
            ).output.strip()
            or "0"
        )
    return active


def _errored_queue(self, table):
    where = _table_filter(table)
    total = 0
    for node in _nodes(self):
        total += int(
            node.query(
                f"SELECT count() FROM system.replication_queue "
                f"WHERE {where} AND last_exception != '' FORMAT TabSeparated"
            ).output.strip()
            or "0"
        )
    return total


def _drain(self, table, stage_label, timeout_s, no_progress_grace_s, absolute_cap_s):
    deadline = time.time() + timeout_s
    absolute_deadline = time.time() + absolute_cap_s
    last_backlog = None
    last_progress_t = time.time()
    while True:
        b = _backlog(self, table)
        if b == 0:
            return
        now = time.time()
        backlog_flat = True
        if last_backlog is None or b < last_backlog:
            last_backlog = b
            last_progress_t = now
            backlog_flat = False
        hang, reason = is_genuine_hang(
            backlog_flat=backlog_flat,
            active_merges=_merge_activity(self, table),
            errored_queue=_errored_queue(self, table),
            grace_exceeded=(now - last_progress_t) > no_progress_grace_s,
            budget_exceeded=now > deadline,
            absolute_cap_exceeded=now > absolute_deadline,
        )
        if hang:
            raise CheckpointFailure(
                f"quiescence {stage_label}: backlog={b} reason={reason}"
            )
        time.sleep(1)


@TestStep(When)
def quiesce(
    self,
    table,
    timeout_s=300,
    no_progress_grace_s=120.0,
    absolute_cap_s=1800.0,
    materialize_ttl=True,
):
    """Drain replication/mutations/merges, OPTIMIZE FINAL, optional MATERIALIZE TTL, re-drain.

    Returns server ``toUnixTimestamp(now())`` after convergence.
    """
    for node in _nodes(self):
        node.query(f"SYSTEM SYNC REPLICA {table}", timeout=timeout_s)
    _drain(self, table, "initial drain", timeout_s, no_progress_grace_s, absolute_cap_s)
    for node in _nodes(self):
        node.query(f"OPTIMIZE TABLE {table} FINAL", timeout=timeout_s)
        if materialize_ttl:
            node.query(f"ALTER TABLE {table} MATERIALIZE TTL", timeout=timeout_s)
    _drain(
        self,
        table,
        "after OPTIMIZE/MATERIALIZE TTL" if materialize_ttl else "after OPTIMIZE",
        timeout_s,
        no_progress_grace_s,
        absolute_cap_s,
    )
    return int(
        self.context.node.query(
            "SELECT toUnixTimestamp(now()) FORMAT TabSeparated"
        ).output.strip()
    )


def cas_fsck(*, node=None, disk=FSCK_DISK, detail=True, timeout=600):
    """Plain fsck helper. Progress is redirected to a file so TestFlows does not log every object."""
    self = current()
    if node is None:
        node = self.context.node
    query = "cas-fsck --detail" if detail else "cas-fsck"
    remote = "/tmp/cas-fsck.out"
    r = _node_command_retry(
        self,
        node,
        f'clickhouse disks --config-file {FSCK_CONFIG} --disk {disk} --query "{query}" '
        f'> {remote} 2>&1; echo __FSCK_EXIT__:$?',
        timeout,
    )
    exit_code = r.exitcode
    for line in (r.output or "").splitlines():
        if line.startswith("__FSCK_EXIT__:"):
            try:
                exit_code = int(line.split(":", 1)[1])
            except ValueError:
                pass
    # The summary line is first. A --detail scan then prints one row per object, so
    # `tail` drops `reachable=...` and the checkpoint sees dangling=None on a clean pool.
    # Keep the summary, then a short sample of everything that is not progress chatter.
    # Color and cursor codes sit in front of `reachable=`, so a start-of-line
    # match misses the summary and the checkpoint sees dangling as missing.
    dumped = _node_command_retry(
        self,
        node,
        f"grep -a -E 'reachable=' {remote} | head -n 5; "
        f"grep -a -Ev 'walking refs|listing blobs|listing manifests|reachable=' {remote} | head -n 40",
        timeout,
    )
    output = dumped.output or ""
    result = parse_fsck_stdout(output, exit_code=exit_code, detail=detail)
    result["stderr"] = output
    return result


@TestStep(When)
def run_cas_fsck(self, node=None, disk=FSCK_DISK, detail=True, timeout=600):
    return cas_fsck(node=node, disk=disk, detail=detail, timeout=timeout)


def cas_gc_dryrun(*, node=None, disk=FSCK_DISK, timeout=600):
    self = current()
    if node is None:
        node = self.context.node
    r = _node_command_retry(
        self,
        node,
        f'clickhouse disks --config-file {FSCK_CONFIG} --disk {disk} --query "cas-gc-dryrun"',
        timeout,
    )
    result = parse_dryrun(r.output)
    result["exit_code"] = r.exitcode
    result["stdout"] = r.output
    return result


@TestStep(When)
def run_cas_gc_dryrun(self, node=None, disk=FSCK_DISK, timeout=600):
    return cas_gc_dryrun(node=node, disk=disk, timeout=timeout)


AMBIGUOUS_BAND_EPS = 10
AMBIGUOUS_BAND_MAX_ATTEMPTS = 6


def wait_for_healthy(http_nodes, table, *, timeout_s=600.0, settle_s=2.0):
    """Both replicas answer /ping and can read ``table``. Raises CheckpointFailure on timeout."""
    deadline = time.time() + timeout_s

    def tables_loaded(node):
        try:
            node.query(f"SELECT count() >= 0 FROM {table}", timeout=5.0)
            return True
        except Exception:
            return False

    while True:
        if all(n.ping() for n in http_nodes) and all(tables_loaded(n) for n in http_nodes):
            time.sleep(settle_s)
            if all(n.ping() for n in http_nodes) and all(
                tables_loaded(n) for n in http_nodes
            ):
                return
        if time.time() > deadline:
            states = {repr(n): (n.ping(), tables_loaded(n)) for n in http_nodes}
            raise CheckpointFailure(
                f"node(s) never returned healthy-with-tables-loaded within {timeout_s:.0f}s: {states}"
            )
        time.sleep(1.0)


def gc_until_stable(*, polls=6, interval_s=2.0):
    """Poll summary fsck until unreachable settles. Residual is tracked, not failed."""
    history = []
    last = None
    for i in range(polls):
        last = cas_fsck(detail=False)
        u = int(last.get("unreachable") or 0)
        history.append(u)
        note(f"gc poll {i + 1}: unreachable={u}")
        if u == 0 or gc_fixpoint_reached(history, stable=2):
            break
        time.sleep(interval_s)
    residual = history[-1] if history else 0
    if residual:
        note(f"gc residual unreachable={residual} (B140 M-F debris; tracked, not failed)")
    return last, residual


@TestStep(When)
def drive_gc_until_stable(self, polls=6, interval_s=2.0):
    """Poll summary fsck until unreachable settles. Residual is tracked, not failed."""
    return gc_until_stable(polls=polls, interval_s=interval_s)


@TestStep(Then)
def green_checkpoint(self, driver, table, model, label="checkpoint", phase=1):
    """Checkpoint: drain, quiesce, model==replicas, prune TTL, GC poll, clean pool.

    Phase 2/3 wait for HTTP-healthy replicas and a coherent fsck cut before asserting.
    """
    note(f"{label}: drain")
    driver.drain()
    if phase >= 2:
        note(f"{label}: wait_for_healthy")
        try:
            wait_for_healthy(driver.http_nodes, table)
        except CheckpointFailure as e:
            assert False, error(str(e))
        refresh_cluster_shells(self)
        try:
            wait_for_pool_consistent(
                lambda: run_cas_fsck(detail=False),
                log_fn=note,
            )
        except CheckpointFailure as e:
            assert False, error(str(e))

    now = quiesce(table=table)

    ttl_band_ambiguous = False
    for band_attempt in range(AMBIGUOUS_BAND_MAX_ATTEMPTS):
        if not model.ambiguous_band_nonempty(now, eps=AMBIGUOUS_BAND_EPS):
            break
        wait_s = AMBIGUOUS_BAND_EPS + 1
        note(
            f"{label}: ambiguous TTL band at now={now}; waiting {wait_s}s "
            f"(attempt {band_attempt + 1}/{AMBIGUOUS_BAND_MAX_ATTEMPTS})"
        )
        time.sleep(wait_s)
        now = quiesce(table=table)
    else:
        if model.ambiguous_band_nonempty(now, eps=AMBIGUOUS_BAND_EPS):
            note(
                f"{label}: TTL band still nonempty after {AMBIGUOUS_BAND_MAX_ATTEMPTS} waits; "
                "degrading to count-range"
            )
            ttl_band_ambiguous = True

    if not ttl_band_ambiguous:
        replicas_match_model(table=table, model=model, now=now)
    else:
        count_low = model.aggregates(now + AMBIGUOUS_BAND_EPS)["count"]
        count_high = model.aggregates(now - AMBIGUOUS_BAND_EPS)["count"]
        n1 = query_aggregates(table=table, node=self.context.node)
        n2 = query_aggregates(table=table, node=self.context.node2)
        for name, na in (("node1", n1), ("node2", n2)):
            assert count_low <= na["count"] <= count_high, error(
                f"TTL-band {name} count {na['count']} outside [{count_low}, {count_high}]"
            )

    pruned = model.prune_expired(now)
    if pruned:
        note(f"{label}: prune_expired reclaimed {pruned} rows")

    _, residual = drive_gc_until_stable()
    note(f"{label}: gc residual unreachable={residual}")

    fsck = run_cas_fsck(detail=True)
    if phase >= 2 and fsck.get("dangling") not in (0, None):
        try:
            fsck = wait_for_pool_consistent(
                lambda: run_cas_fsck(detail=True),
                log_fn=note,
            )
        except CheckpointFailure as e:
            assert False, error(str(e))
    dryrun = run_cas_gc_dryrun()
    pool_is_clean(fsck_result=fsck, dryrun_result=dryrun, detail=True)
    return now


def assert_pool_is_clean(fsck_result, dryrun_result, *, detail=True):
    dangling = fsck_result.get("dangling", None)
    assert dangling == 0, error(f"fsck dangling={dangling} (INV-NO-LOSS)")
    try:
        require_clean_stale_edge(fsck_result, detail=detail)
        if detail:
            dryrun_subset_check(
                fsck_result.get("detail") or [],
                dryrun_result.get("entries") or [],
                log_fn=note,
            )
    except CheckpointFailure as e:
        assert False, error(str(e))
    return fsck_result, dryrun_result


@TestStep(Then)
def pool_is_clean(self, fsck_result, dryrun_result, *, detail=True):
    return assert_pool_is_clean(fsck_result, dryrun_result, detail=detail)
