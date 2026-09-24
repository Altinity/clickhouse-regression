#!/usr/bin/env python3
"""CAS soak rewrite — TestFlows suite, separate from cas/soak.

Do not import cas.soak. Do not wrap python -m soak.run.

Examples:
  python3 cas/soak_tests/regression.py --clickhouse <deb-or-binary> --local --suite smoke
  python3 cas/soak_tests/regression.py --local --suite unit
  python3 cas/soak_tests/regression.py --clickhouse <deb-or-binary> --local --suite primitives
  python3 cas/soak_tests/regression.py --clickhouse <deb-or-binary> --local --suite phase1
  python3 cas/soak_tests/regression.py --clickhouse <deb-or-binary> --local --suite phase2
  python3 cas/soak_tests/regression.py --clickhouse <deb-or-binary> --local --suite scenarios --scenario S01
  python3 cas/soak_tests/regression.py --clickhouse <deb-or-binary> --local --suite scenarios --scenario P0 --scenario-scale dev
"""

import sys
from testflows.core import *

append_path(sys.path, "../..")

from helpers.cluster import create_cluster
from helpers.argparser import (
    argparser_minio,
    CaptureClusterArgs,
    CaptureMinioArgs,
)
from helpers.common import experimental_analyzer

from cas.soak_tests.features import IMPLEMENTED_SUITES, LIVE_SUITES


xfails = {}
ffails = {}


def argparser(parser):
    argparser_minio(parser)
    parser.add_argument(
        "--suite",
        type=str,
        default="smoke",
        help=(
            "Comma-separated suites: smoke, unit, primitives, phase1, phase2, "
            "phase3, scenarios, all. Default: smoke. Unimplemented suites skip."
        ),
    )
    parser.add_argument("--seed", type=int, default=1, help="Deterministic soak seed")
    parser.add_argument(
        "--phase1-ops",
        type=int,
        default=200,
        dest="phase1_ops",
        help="Phase 1 ledger length (default 200)",
    )
    parser.add_argument(
        "--phase1-checkpoint-every",
        type=int,
        default=50,
        dest="phase1_checkpoint_every",
        help="Phase 1 checkpoint interval in ops (default 50)",
    )
    parser.add_argument(
        "--phase1-workers",
        type=int,
        default=6,
        dest="phase1_workers",
        help="Phase 1 concurrent INSERT/OPTIMIZE workers (default 6)",
    )
    parser.add_argument(
        "--chaos-seed",
        type=int,
        default=None,
        dest="chaos_seed",
        help="Phase 2 chaos schedule seed (default: same as --seed)",
    )
    parser.add_argument(
        "--chaos-interval",
        type=int,
        default=90,
        dest="chaos_interval",
        help="Phase 2/3 mean inter-fault interval in seconds (default 90)",
    )
    parser.add_argument(
        "--phase3-duration",
        type=str,
        default="15m",
        dest="phase3_duration",
        help="Phase 3 wall-clock duration (default 15m; use 24h for full soak)",
    )
    parser.add_argument(
        "--min-ops-between-mutations",
        type=int,
        default=80,
        dest="min_ops_between_mutations",
        help="Phase 3 mutation thinning gap (default 80; 0 disables)",
    )
    parser.add_argument(
        "--no-chaos",
        action="store_true",
        dest="no_chaos",
        help="Phase 3: empty chaos schedule, including the converge restart",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="S01",
        help="Scenario filter: name, P0/P1/P2, comma list, or all (default S01)",
    )
    parser.add_argument(
        "--scenario-scale",
        type=str,
        default="dev",
        dest="scenario_scale",
        choices=("dev", "ci", "full"),
        help="Scenario scale profile (default dev)",
    )


def _parse_suites(raw: str):
    parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
    if "all" in parts:
        return ["smoke", "unit", "primitives", "phase1", "phase2", "phase3", "scenarios"]
    return parts


def _needs_cluster(suites):
    return any(s in suites for s in LIVE_SUITES)


@TestModule
@Name("cas soak tests")
@FFails(ffails)
@XFails(xfails)
@ArgumentParser(argparser)
@CaptureClusterArgs
@CaptureMinioArgs
def regression(
    self,
    cluster_args,
    clickhouse_version,
    stress=None,
    with_analyzer=False,
    minio_args=None,
    suite="smoke",
    seed=1,
    phase1_ops=200,
    phase1_checkpoint_every=50,
    phase1_workers=6,
    chaos_seed=None,
    chaos_interval=90,
    phase3_duration="15m",
    min_ops_between_mutations=80,
    no_chaos=False,
    scenario="S01",
    scenario_scale="dev",
):
    """Independent TestFlows rewrite of CAS soak. See features.py for port stages."""
    suites = _parse_suites(suite)

    self.context.clickhouse_version = clickhouse_version
    self.context.soak_seed = seed
    self.context.phase1_ops = phase1_ops
    self.context.phase1_checkpoint_every = phase1_checkpoint_every
    self.context.phase1_workers = phase1_workers
    self.context.chaos_seed = seed if chaos_seed is None else chaos_seed
    self.context.chaos_interval = chaos_interval
    self.context.phase3_duration = phase3_duration
    self.context.min_ops_between_mutations = min_ops_between_mutations
    self.context.no_chaos = no_chaos
    self.context.scenario = scenario
    self.context.scenario_scale = scenario_scale
    if stress is not None:
        self.context.stress = stress

    minio_root_user = minio_args["minio_root_user"].value
    minio_root_password = minio_args["minio_root_password"].value
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password

    if _needs_cluster(suites):
        nodes = {"clickhouse": ("clickhouse1", "clickhouse2")}
        with Given("docker-compose cluster (soak_tests_env)"):
            cluster = create_cluster(
                **cluster_args,
                nodes=nodes,
                configs_dir=current_dir(),
                environ={
                    "MINIO_ROOT_USER": minio_root_user,
                    "MINIO_ROOT_PASSWORD": minio_root_password,
                },
            )
            self.context.cluster = cluster

        self.context.node = cluster.node("clickhouse1")
        self.context.node2 = cluster.node("clickhouse2")
        self.context.nodes = [self.context.node, self.context.node2]

        with And("enable or disable experimental analyzer if needed"):
            for node in self.context.nodes:
                experimental_analyzer(node=node, with_analyzer=with_analyzer)

    dispatch = {
        "smoke": "feature_smoke",
        "unit": "feature_unit",
        "primitives": "feature_primitives",
        "phase1": "feature_phase1",
        "phase2": "feature_phase2",
        "phase3": "feature_phase3",
        "scenarios": "feature_scenarios",
    }
    for name in suites:
        feature = dispatch.get(name)
        if feature is None:
            fail(f"unknown suite {name!r}; expected one of {', '.join(dispatch)}")
        Feature(run=load("cas.soak_tests.features", feature))

    note(f"implemented suites: {', '.join(IMPLEMENTED_SUITES)}")


if main():
    regression()
