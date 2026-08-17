#!/usr/bin/env python3
"""CAS soak suite — separate entrypoint under cas/soak (not wired into cas/regression.py).

Port of ClickHouse utils/ca-soak onto helpers.cluster / soak_env.

Examples:
  python3 cas/soak/regression.py --clickhouse docker://… --local \\
      --suite unit,phase1 --seed 1

  python3 cas/soak/regression.py --clickhouse /path/to/clickhouse --as-binary \\
      --suite all --seed 1 --phase3-duration 15m --scenario-scale ci
"""

import os
import sys
from testflows.core import *

append_path(sys.path, "../..")
append_path(sys.path, ".")

from helpers.cluster import create_cluster
from helpers.argparser import (
    argparser_minio,
    CaptureClusterArgs,
    CaptureMinioArgs,
)
from helpers.common import experimental_analyzer

from cas.soak.bridge import bind_cluster, ensure_binary_env


xfails = {}
ffails = {}


def argparser(parser):
    """CAS soak suite arguments on top of the shared minio/cluster parser."""
    argparser_minio(parser)

    parser.add_argument(
        "--suite",
        type=str,
        default="unit,phase1",
        help=(
            "Comma-separated suites to run: unit, phase1, phase2, phase3, scenarios, all. "
            "Default: unit,phase1"
        ),
    )
    parser.add_argument("--seed", type=int, default=1, help="Deterministic soak/scenario seed")
    parser.add_argument(
        "--phase1-ops",
        type=int,
        default=200,
        help="Phase-1/2 ledger op count (default 200 for CI-smoke)",
    )
    parser.add_argument(
        "--phase1-checkpoint-every",
        type=int,
        default=50,
        help="Phase-1/2 checkpoint interval in ops",
    )
    parser.add_argument(
        "--phase3-duration",
        type=str,
        default="15m",
        help="Phase-3 wall duration (default 15m; use 24h for full soak)",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="all",
        help="Scenario filter for scenarios suite (name, all, P0, …)",
    )
    parser.add_argument(
        "--scenario-duration",
        type=str,
        default="15m",
        help="Per-scenario duration",
    )
    parser.add_argument(
        "--scenario-scale",
        type=str,
        default="ci",
        choices=("dev", "ci", "full"),
        help="Scenario scale profile",
    )
    parser.add_argument(
        "--skip-cluster",
        action="store_true",
        help="Skip helpers.cluster bring-up (unit tests only, or external cluster via CA_SOAK_*)",
    )


def _parse_suites(raw: str):
    parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
    if "all" in parts:
        return ["unit", "phase1", "phase2", "phase3", "scenarios"]
    return parts


@TestFeature
@Name("phases")
def feature_live_phases(
    self,
    suites,
    cluster_args,
    minio_root_user,
    minio_root_password,
    with_analyzer,
    skip_cluster,
    seed,
    phase1_ops,
    phase1_checkpoint_every,
    phase3_duration,
):
    """Run phase1-3 against soak_env.

    Cluster lifetime is this feature, not the module, so `--suite all` can tear
    soak_env down before scenarios bring up their own compose on 8123/8124.
    """
    if not skip_cluster:
        nodes = {"clickhouse": ("clickhouse1", "clickhouse2")}
        with Given("docker-compose cluster (soak_env)"):
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

        with And("bind CA_SOAK_* env to helpers.cluster nodes"):
            bind_cluster(cluster)

        with And("enable or disable experimental analyzer if needed"):
            for node in self.context.nodes:
                experimental_analyzer(node=node, with_analyzer=with_analyzer)
    else:
        note("skip-cluster set; expecting CA_SOAK_NODE* already configured")

    if "phase1" in suites:
        Feature(test=load("cas.soak.features", "feature_phase1"))(
            seed=seed,
            ops=phase1_ops,
            checkpoint_every=phase1_checkpoint_every,
        )

    if "phase2" in suites:
        Feature(test=load("cas.soak.features", "feature_phase2"))(
            seed=seed,
            ops=phase1_ops,
            checkpoint_every=phase1_checkpoint_every,
        )

    if "phase3" in suites:
        Feature(test=load("cas.soak.features", "feature_phase3"))(
            seed=seed,
            duration=phase3_duration,
        )


@TestModule
@Name("cas soak")
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
    suite="unit,phase1",
    seed=1,
    phase1_ops=200,
    phase1_checkpoint_every=50,
    phase3_duration="15m",
    scenario="all",
    scenario_duration="15m",
    scenario_scale="ci",
    skip_cluster=False,
):
    """Run the CAS soak harness as a separate suite under cas/soak."""
    suites = _parse_suites(suite)
    needs_cluster = any(s in suites for s in ("phase1", "phase2", "phase3"))
    # scenarios manage their own compose variants; still resolve binary for mounts
    needs_binary = any(s in suites for s in ("phase1", "phase2", "phase3", "scenarios"))

    self.context.clickhouse_version = clickhouse_version
    if stress is not None:
        self.context.stress = stress

    minio_root_user = minio_args["minio_root_user"].value
    minio_root_password = minio_args["minio_root_password"].value
    self.context.minio_root_user = minio_root_user
    self.context.minio_root_password = minio_root_password

    clickhouse_path = cluster_args.get("clickhouse_path")
    if needs_binary and clickhouse_path:
        with Given("resolve ClickHouse binary for compose variants"):
            ensure_binary_env(clickhouse_path)

    # Unit tests need no cluster — run them first so a missing pytest does not
    # pay for (and then tear down) a fresh soak_env.
    if "unit" in suites:
        Feature(run=load("cas.soak.features", "feature_unit"))

    if needs_cluster:
        Feature(test=feature_live_phases)(
            suites=suites,
            cluster_args=cluster_args,
            minio_root_user=minio_root_user,
            minio_root_password=minio_root_password,
            with_analyzer=with_analyzer,
            skip_cluster=skip_cluster,
            seed=seed,
            phase1_ops=phase1_ops,
            phase1_checkpoint_every=phase1_checkpoint_every,
            phase3_duration=phase3_duration,
        )

    if "scenarios" in suites:
        Feature(test=load("cas.soak.features", "feature_scenarios"))(
            scenario=scenario,
            seed=seed,
            duration=scenario_duration,
            scale=scenario_scale,
        )


if main():
    regression()
