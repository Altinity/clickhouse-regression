"""Phase-3 time-driven stage schedule.

Phase 1/2 are op-count driven. Phase 3 maps fractions of a wall-clock duration to a
fixed sequence of stages. Pure: no I/O, no clock reads.
"""

from dataclasses import dataclass
from enum import Enum


class StageKind(str, Enum):
    WARMUP = "warmup"
    STEADY = "steady"
    MUTATIONS = "mutations"
    TTL_PRESSURE = "ttl_pressure"
    GC_CHECKPOINT = "gc_checkpoint"
    CHAOS = "chaos"
    CLIFF = "cliff"
    CONVERGE = "converge"


_STAGE_FRACTIONS = [
    (StageKind.WARMUP, 0.05),
    (StageKind.STEADY, 0.10),
    (StageKind.MUTATIONS, 0.10),
    (StageKind.TTL_PRESSURE, 0.10),
    (StageKind.GC_CHECKPOINT, 0.05),
    (StageKind.CHAOS, 0.45),
    (StageKind.CLIFF, 0.05),
    (StageKind.CONVERGE, 0.10),
]


@dataclass(frozen=True)
class Stage:
    kind: StageKind
    t_start: int
    t_end: int
    allow_inserts: bool
    allow_optimize: bool
    allow_mutations: bool
    allow_cliffs: bool
    chaos_armed: bool

    def contains(self, t: float) -> bool:
        return self.t_start <= t < self.t_end


_CAPS = {
    #                         inserts optimize mutations cliffs  chaos
    StageKind.WARMUP:        (True,   False,   False,    False,  False),
    StageKind.STEADY:        (True,   True,    False,    False,  False),
    StageKind.MUTATIONS:     (True,   True,    True,     False,  False),
    StageKind.TTL_PRESSURE:  (True,   True,    True,     False,  False),
    StageKind.GC_CHECKPOINT: (False,  False,   False,    False,  False),
    StageKind.CHAOS:         (True,   True,    True,     False,  True),
    StageKind.CLIFF:         (True,   True,    True,     True,   True),
    StageKind.CONVERGE:      (True,   True,    True,     False,  False),
}


def stage_plan(duration_s: int) -> list:
    """Map duration_s to ordered Stage windows tiling [0, duration_s)."""
    if duration_s <= 0:
        raise ValueError(f"duration_s must be positive, got {duration_s}")
    stages = []
    t = 0
    n = len(_STAGE_FRACTIONS)
    for i, (kind, frac) in enumerate(_STAGE_FRACTIONS):
        if i == n - 1:
            t_end = duration_s
        else:
            t_end = t + int(round(frac * duration_s))
            t_end = max(t, min(t_end, duration_s))
        caps = _CAPS[kind]
        stages.append(
            Stage(
                kind=kind,
                t_start=t,
                t_end=t_end,
                allow_inserts=caps[0],
                allow_optimize=caps[1],
                allow_mutations=caps[2],
                allow_cliffs=caps[3],
                chaos_armed=caps[4],
            )
        )
        t = t_end
    return stages


def stage_at(plan: list, t: float):
    """Resolve wall-clock offset t to its active Stage. Past the end: last stage."""
    for s in plan:
        if s.contains(t):
            return s
    return plan[-1]


def chaos_window(plan: list) -> tuple:
    """Union of chaos-armed stages (CHAOS + CLIFF). (0, 0) if none."""
    armed = [s for s in plan if s.chaos_armed]
    if not armed:
        return (0, 0)
    return (armed[0].t_start, armed[-1].t_end)
