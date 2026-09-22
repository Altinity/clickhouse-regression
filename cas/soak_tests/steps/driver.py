"""Green-path / chaos ledger driver.

INSERT and OPTIMIZE run concurrently. UPDATE/DELETE/TRUNCATE/DROP_PARTITION are
barriers. Phase 1 does not retry transport failures; phase 2 reroutes.
"""

import threading
from concurrent.futures import FIRST_EXCEPTION, ThreadPoolExecutor, wait

from cas.soak_tests.oracle import BARRIER_TYPES, OpType
from cas.soak_tests.oracle.workload import (
    delete_sql,
    insert_values_sql,
    truncate_sql,
    update_sql,
)
from cas.soak_tests.steps.http import (
    QueryError,
    is_timeout,
    is_transport_error,
    retry_on_aborted,
    retry_on_transport,
)

INSERT_SETTINGS = "SETTINGS async_insert=0"
OPTIMIZE_TIMEOUT_S = 45
TRANSPORT_ATTEMPTS = 40


class Driver:
    def __init__(
        self,
        http_nodes,
        table,
        model,
        seed,
        base_time,
        workers=6,
        insert_settings=INSERT_SETTINGS,
        transport_resilient=False,
        transport_attempts=TRANSPORT_ATTEMPTS,
    ):
        self.http_nodes = list(http_nodes)
        self.table = table
        self.model = model
        self.seed = seed
        self.base_time = base_time
        self.workers = workers
        self.insert_settings = insert_settings
        self.transport_resilient = transport_resilient
        self.transport_attempts = transport_attempts
        self.model_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=workers)
        self.inflight = []
        self.last_op = None
        self.aborted_retries = 0
        self.transport_retries = 0
        self._aborted_lock = threading.Lock()
        self._transport_lock = threading.Lock()
        self._optimize_gate = threading.BoundedSemaphore(1)

    def node_for(self, target):
        return self.http_nodes[target]

    def _nodes_starting_at(self, target):
        primary = self.node_for(target)
        other = self.node_for(1 - target)
        return [primary, other]

    def _with_transport_retry(self, op_kind, op_id, one_attempt):
        if not self.transport_resilient:
            one_attempt(0)
            return
        counter = {"i": 0}

        def attempt():
            i = counter["i"]
            counter["i"] += 1
            return one_attempt(i)

        def on_retry(attempt_no, err):
            with self._transport_lock:
                self.transport_retries += 1

        retry_on_transport(
            attempt, attempts=self.transport_attempts, on_retry=on_retry
        )

    def _submit_insert(self, op):
        n = 1 + (op.param % self.model.insert_block)
        with self.model_lock:
            self.model.apply(op)
        sql = insert_values_sql(
            self.seed,
            op.op_id,
            n,
            self.table,
            self.base_time,
            settings=self.insert_settings,
        )
        fut = self.executor.submit(self._insert_with_retry, op.target, sql, op.op_id)
        self.inflight.append(fut)

    def _insert_with_retry(self, target, sql, op_id):
        def aborted_on_retry(attempt, err):
            with self._aborted_lock:
                self.aborted_retries += 1

        order = self._nodes_starting_at(target)

        def one_attempt(attempt_idx):
            node = order[attempt_idx % len(order)]
            retry_on_aborted(lambda: node.command(sql), on_retry=aborted_on_retry)

        self._with_transport_retry("INSERT", op_id, one_attempt)

    def _submit_optimize(self, op):
        fut = self.executor.submit(self._optimize_once, op.target, op.op_id)
        self.inflight.append(fut)

    def _optimize_once(self, target, op_id):
        if not self._optimize_gate.acquire(blocking=False):
            return
        try:
            order = self._nodes_starting_at(target)

            def one_attempt(attempt_idx):
                node = order[attempt_idx % len(order)]
                try:
                    node.command(
                        f"OPTIMIZE TABLE {self.table}", timeout=OPTIMIZE_TIMEOUT_S
                    )
                except QueryError as e:
                    if self.transport_resilient and (
                        e.is_node_down
                        or e.is_readonly
                        or e.is_mount_fenced
                        or e.is_keeper_transient
                        or e.is_s3_transient
                    ):
                        return
                    raise
                except Exception as e:
                    if is_timeout(e) or (
                        self.transport_resilient and is_transport_error(e)
                    ):
                        return
                    raise

            self._with_transport_retry("OPTIMIZE", op_id, one_attempt)
        finally:
            self._optimize_gate.release()

    def drain(self):
        if not self.inflight:
            return
        wait(self.inflight, return_when=FIRST_EXCEPTION)
        futures, self.inflight = self.inflight, []
        for fut in futures:
            fut.result()

    def harvest(self):
        if not self.inflight:
            return
        still = []
        for fut in self.inflight:
            if fut.done():
                fut.result()
            else:
                still.append(fut)
        self.inflight = still

    def inflight_count(self):
        return len(self.inflight)

    def apply_barrier(self, op):
        self.drain()
        if op.type == OpType.UPDATE:
            sql = update_sql(self.table, self.model._pred_bucket(op.param))
        elif op.type == OpType.DELETE:
            sql = delete_sql(self.table, self.model._pred_bucket(op.param))
        elif op.type == OpType.TRUNCATE:
            sql = truncate_sql(self.table)
        elif op.type == OpType.DROP_PARTITION:
            sql = truncate_sql(self.table)
        else:
            raise AssertionError(f"apply_barrier on non-barrier op {op.type}")
        order = self._nodes_starting_at(op.target)

        def one_attempt(attempt_idx):
            order[attempt_idx % len(order)].command(sql)

        self._with_transport_retry(f"BARRIER:{op.type.name}", op.op_id, one_attempt)
        with self.model_lock:
            self.model.apply(op)

    def execute(self, op):
        if op.type == OpType.INSERT:
            self._submit_insert(op)
        elif op.type == OpType.OPTIMIZE:
            self._submit_optimize(op)
        elif op.type in BARRIER_TYPES:
            self.apply_barrier(op)
        else:
            raise AssertionError(f"unknown op type {op.type}")
        self.last_op = op

    def close(self):
        try:
            self.drain()
        finally:
            self.executor.shutdown(wait=True)
