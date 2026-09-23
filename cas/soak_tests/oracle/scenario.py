"""Scenario card registry. Pure: no cluster I/O, no imports from cas.soak."""

from .verdict import INCONCLUSIVE, ScenarioResult, Verdict

_REGISTRY: dict = {}

SCALES = ("dev", "ci", "full")


def register(cls):
    key = cls.name.upper()
    if key in _REGISTRY:
        raise ValueError(f"duplicate scenario name {cls.name}")
    _REGISTRY[key] = cls
    return cls


def get(name: str):
    return _REGISTRY.get(name.upper())


def all_scenarios() -> dict:
    return dict(_REGISTRY)


def select(spec: str) -> list:
    """Resolve 'all' | P0/P1/P2 | comma-separated names | one name into registered classes."""
    items = sorted(_REGISTRY.values(), key=lambda c: c.name)
    s = spec.strip()
    if not s:
        return []
    if s.lower() == "all":
        return items
    if s.upper() in ("P0", "P1", "P2"):
        return [c for c in items if c.priority.upper() == s.upper()]
    names = [x.strip().upper() for x in s.split(",") if x.strip()]
    out = []
    for n in names:
        c = _REGISTRY.get(n)
        if c is not None:
            out.append(c)
    return out


def _coerce(default, raw: str):
    if isinstance(default, bool):
        return raw.lower() in ("1", "true", "yes", "on")
    if isinstance(default, int):
        return int(raw)
    if isinstance(default, float):
        return float(raw)
    return raw


class Scenario:
    name: str = "S00"
    title: str = "base"
    priority: str = "P0"
    abandons: bool = False
    expect_exception: bool = False
    needs_infra: str | None = None
    compose_variant: str | None = None
    param_table: dict = {"dev": {}, "ci": {}, "full": {}}

    def resolve_params(self, scale: str, overrides: dict | None = None) -> dict:
        base = dict(self.param_table.get("dev", {}))
        if scale != "dev":
            base.update(self.param_table.get(scale, {}))
        if overrides:
            for k, v in overrides.items():
                if k in base:
                    base[k] = _coerce(base[k], v) if isinstance(v, str) else v
                else:
                    base[k] = v
        return base

    def run(self, ctx, result: ScenarioResult) -> None:
        raise NotImplementedError

    def run_inconclusive(self, ctx, result: ScenarioResult) -> None:
        reason = self.needs_infra or "infrastructure unavailable"
        result.add(Verdict.inconclusive(self.name, "runnable", reason))
        result.note_anomaly(f"NOT RUN — {reason}")
        result.finalize(INCONCLUSIVE)
