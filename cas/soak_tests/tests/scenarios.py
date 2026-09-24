"""TestFlows runner for registered scenario cards."""

import os
import time

from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.cards import select
from cas.soak_tests.oracle.verdict import ScenarioResult, Verdict
from cas.soak_tests.steps.card import (
    apply_card_result,
    cluster_from_context,
    drop_table_both,
    drop_tables_like,
)
from cas.soak_tests.steps.variants import activate, restore, ten_nodes


def _log(msg):
    print(msg, flush=True)


class _Ctx:
    def __init__(self, cluster, params, seed, scale, log):
        self.cluster = cluster
        self.params = params
        self.seed = seed
        self.scale = scale
        self.log = log
        self.extra = {}
        self.timestamp = int(time.time() * 1000)

    def write_json(self, name, obj):
        pass


_CLEANUP_LIKE = (
    "s01_%",
    "s02_%",
    "s03_%",
    "s04_%",
    "s05_%",
    "s06_%",
    "s07_%",
    "s08_%",
    "s09_%",
    "s10_%",
    "s11_%",
    "s12_%",
    "s13_%",
    "s14_%",
    "s15_%",
    "s16_%",
    "s17_%",
    "s18_%",
    "s19_%",
    "s20_%",
    "s21_%",
    "s22_%",
    "s23_%",
    "s24_%",
    "s25_%",
    "s26_%",
    "s27_%",
    "s28_%",
    "s29_%",
    "s30_%",
    "s31_%",
    "s32_%",
    "s33_%",
    "s34_%",
    "s35_%",
    "s36_%",
    "s37_%",
    "s38_%",
    "s39_%",
    "s40_%",
    "s41_%",
    "s42_%",
    "s43_%",
    "s44_%",
    "s45_%",
    "w3_%",
)


@TestScenario
def run_card(self, card_cls):
    seed = int(getattr(self.context, "soak_seed", 1))
    scale = str(getattr(self.context, "scenario_scale", "dev"))
    card = card_cls()
    params = card.resolve_params(scale)
    result = ScenarioResult(
        scenario=card.name,
        title=card.title,
        priority=card.priority,
        seed=seed,
        params=params,
    )
    cluster = cluster_from_context(self.context)
    ctx = _Ctx(cluster, params, seed, scale, _log)
    user = getattr(self.context, "minio_root_user", None)
    password = getattr(self.context, "minio_root_password", None)
    if user:
        os.environ["CA_SOAK_TESTS_S3_ACCESS_KEY"] = str(user)
    if password:
        os.environ["CA_SOAK_TESTS_S3_SECRET_KEY"] = str(password)
    try:
        ctx.extra["since_event_time"] = cluster.node1.scalar("SELECT toString(now())")
        result.observations["since_event_time"] = ctx.extra["since_event_time"]
    except Exception:
        ctx.extra["since_event_time"] = None
    note(f"{card.name}: {card.title} scale={scale} params={params}")
    try:
        activate(self.context, card.compose_variant)
        if card.compose_variant == "tenreplicas":
            cluster = ten_nodes()
        else:
            cluster = cluster_from_context(self.context)
        ctx.cluster = cluster
        for like in _CLEANUP_LIKE:
            drop_tables_like(cluster, like)
        try:
            if card.needs_infra:
                card.run_inconclusive(ctx, result)
            else:
                card.run(ctx, result)
        except Exception as e:
            note(f"{card.name} raised {type(e).__name__}: {e}")
            result.note_anomaly(f"raised {type(e).__name__}: {e}")
            result.add(
                Verdict(
                    "card completed",
                    "no uncaught exception",
                    f"{type(e).__name__}: {e}"[:500],
                    "fail",
                )
            )
        apply_card_result(result)
    except Exception as e:
        note(f"{card.name} variant switch raised {type(e).__name__}: {e}")
        result.note_anomaly(f"variant switch raised {type(e).__name__}: {e}")
        result.add(
            Verdict(
                "cluster variant",
                card.compose_variant or "default",
                f"{type(e).__name__}: {e}"[:500],
                "fail",
            )
        )
        apply_card_result(result)
    finally:
        for name in list(result.observations.get("tables", []) or []):
            drop_table_both(cluster, name)
        for like in _CLEANUP_LIKE:
            drop_tables_like(cluster, like)


@TestFeature
@Name("scenarios")
def feature(self):
    """Registered cards, one at a time. Unregistered names are skipped."""
    spec = str(getattr(self.context, "scenario", "S01"))
    cards = select(spec)
    if not cards:
        skip(
            f"no implemented scenario cards match {spec!r}; "
            "registered: " + ", ".join(c.name for c in select("all") or ["(none)"])
        )
    try:
        for card_cls in cards:
            Scenario(test=run_card, name=f"{card_cls.name} {card_cls.title}", flags=TE)(
                card_cls=card_cls
            )
    finally:
        restore(self.context)
