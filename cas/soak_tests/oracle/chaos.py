"""Deterministic chaos schedule. Pure: no docker."""

from dataclasses import dataclass
from enum import Enum

from .rng import splitmix64


class FaultTarget(str, Enum):
    CH1 = "ch1"
    CH2 = "ch2"
    BOTH = "both"
    RUSTFS = "rustfs"


class FaultAction(str, Enum):
    KILL = "kill"
    RESTART = "restart"
    PAUSE = "pause"
    FREEZE_LONG = "freeze_long"


@dataclass(frozen=True)
class Fault:
    t_offset: int
    target: FaultTarget
    action: FaultAction
    duration_s: int


_TARGETS = [FaultTarget.CH1, FaultTarget.CH2, FaultTarget.BOTH, FaultTarget.RUSTFS]
_ACTIONS = [FaultAction.KILL, FaultAction.RESTART, FaultAction.PAUSE]


def generate_chaos_schedule(seed: int, duration_s: int, mean_interval_s: int):
    """Poisson-ish inter-arrival via splitmix64. Never a long simultaneous KILL of BOTH.
    RustFS+KILL is remapped to RESTART (B145). FREEZE_LONG (~1/6) hits one CH replica for 60..90s.
    """
    faults = []
    t = 0
    i = 0
    while True:
        r = splitmix64(seed ^ (i * 0x9E3779B1))
        gap = (mean_interval_s * (30 + (r % 140))) // 100
        t += max(1, gap)
        if t >= duration_s:
            break
        r2 = splitmix64(r)
        target = _TARGETS[(r2 >> 3) % len(_TARGETS)]
        action = _ACTIONS[(r2 >> 7) % len(_ACTIONS)]
        dur = 5 + ((r2 >> 11) % 56)
        if target == FaultTarget.RUSTFS and action == FaultAction.KILL:
            action = FaultAction.RESTART
        if target == FaultTarget.BOTH and action == FaultAction.KILL:
            dur = min(dur, 60)
        if ((r2 >> 9) % 6) == 0:
            action = FaultAction.FREEZE_LONG
            target = FaultTarget.CH1 if ((r2 >> 13) & 1) == 0 else FaultTarget.CH2
            dur = 60 + ((r2 >> 17) % 31)
        faults.append(Fault(t_offset=t, target=target, action=action, duration_s=dur))
        i += 1
    return faults
