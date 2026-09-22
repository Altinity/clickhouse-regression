"""Pure phase-3 helpers: duration parsing, throttle, mutation thinning, op gating."""

from .chaos import Fault, FaultAction, FaultTarget, generate_chaos_schedule
from .ledger import CLIFF_TYPES, Op, OpType
from .schedule import StageKind, chaos_window

METRICS_INTERVAL_S = 60
GB = 1024 ** 3
_THROTTLE_MAX = 1.0


def parse_duration(s) -> int:
    """Parse a wall-clock duration to seconds. Bare int, or suffixed n{s,m,h,d}."""
    if isinstance(s, int):
        return s
    s = str(s).strip().lower()
    if not s:
        raise ValueError("empty duration")
    if s[-1] in "smhd":
        n = float(s[:-1])
        mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}[s[-1]]
        return int(n * mult)
    return int(s)


def metrics_interval_for(duration_s: int, base_interval_s: int = METRICS_INTERVAL_S) -> int:
    """Scale the 60s production cadence down for short runs (floor 5s)."""
    target_samples = 30
    return max(5, min(base_interval_s, duration_s // target_samples))


def compute_throttle(pool_bytes, max_pool_bytes, *, current_sleep_s):
    """Resource-bounding policy. Unknown pool + budget set -> fail closed (B204)."""
    if max_pool_bytes is None or max_pool_bytes <= 0:
        return current_sleep_s
    if pool_bytes is None:
        return _THROTTLE_MAX
    frac = pool_bytes / max_pool_bytes
    if frac < 0.75:
        return 0.0
    if frac < 0.90:
        return 0.05
    if frac < 1.00:
        return 0.25
    return _THROTTLE_MAX


def demote_dense_mutations(ledger, min_ops_between_mutations: int):
    """Demote UPDATE/DELETE to OPTIMIZE unless spaced by min_ops_between_mutations."""
    if min_ops_between_mutations <= 0:
        return list(ledger)
    out = []
    last_mut_op = None
    for op in ledger:
        if op.type in (OpType.UPDATE, OpType.DELETE):
            far_enough = (
                last_mut_op is None
                or (op.op_id - last_mut_op) >= min_ops_between_mutations
            )
            if far_enough:
                last_mut_op = op.op_id
                out.append(op)
            else:
                out.append(
                    Op(
                        op_id=op.op_id,
                        type=OpType.OPTIMIZE,
                        target=op.target,
                        param=op.param,
                    )
                )
        else:
            out.append(op)
    return out


def phase3_op_permitted(op, stage) -> bool:
    """True iff op's class may fire in stage."""
    if op.type == OpType.INSERT:
        return stage.allow_inserts
    if op.type == OpType.OPTIMIZE:
        return stage.allow_optimize
    if op.type in (OpType.UPDATE, OpType.DELETE):
        return stage.allow_mutations
    if op.type in CLIFF_TYPES:
        return stage.allow_cliffs
    return False


def phase3_chaos_schedule(chaos_seed, plan, chaos_interval_s):
    """Faults only in the chaos-armed window, plus a converge both-replica restart."""
    win_start, win_end = chaos_window(plan)
    raw = generate_chaos_schedule(chaos_seed, win_end, chaos_interval_s)
    faults = [f for f in raw if f.t_offset >= win_start]
    converge = next((s for s in plan if s.kind == StageKind.CONVERGE), None)
    if converge is not None and converge.t_end - converge.t_start > 5:
        faults.append(
            Fault(
                t_offset=converge.t_start + 1,
                target=FaultTarget.BOTH,
                action=FaultAction.RESTART,
                duration_s=3,
            )
        )
    return faults
