"""Suite routing for the TestFlows CAS soak rewrite.

Isolation
---------
This package must not import ``cas.soak`` or subprocess the old harness.
``cas/soak`` stays the reference implementation until a stage is ported.

Port stages (do these in order; each stage is its own change)
-------------------------------------------------------------
0. Exoskeleton + cluster smoke          done
1. Oracle unit tests                    done (rng, ledger, cliff cap, rowgen, model)
2. Workload + checkpoint primitives     done (SQL, quiesce, replica compare,
                                        cas-fsck, GC dry-run subset)
3. Soak phase 1                         done (green-path ledger driver, no chaos)
4. Soak phase 2                         done (deterministic chaos on the same driver)
5. Soak phase 3                         done (wall-clock duration driver)
6. Scenario cards                       done (S01–S45; compose variants still need the harness)

``--suite`` names below match the old harness so we can compare runs later.
Unimplemented suites skip rather than fail.
"""

from testflows.core import *

IMPLEMENTED_SUITES = (
    "smoke",
    "unit",
    "primitives",
    "phase1",
    "phase2",
    "phase3",
    "scenarios",
)
LIVE_SUITES = ("smoke", "primitives", "phase1", "phase2", "phase3", "scenarios")


def _not_ported(name):
    skip(
        f"{name} is not ported yet; implemented suites: {', '.join(IMPLEMENTED_SUITES)}"
    )


@TestFeature
@Name("smoke")
def feature_smoke(self):
    """Prove the independent cluster comes up with a CAS disk. Not a soak."""
    Feature(run=load("cas.soak_tests.tests.smoke", "feature"))


@TestFeature
@Name("unit")
def feature_unit(self):
    """Oracle unit tests. No cluster."""
    Feature(run=load("cas.soak_tests.tests.unit.feature", "feature"))


@TestFeature
@Name("primitives")
def feature_primitives(self):
    """Workload SQL + checkpoint primitives on a live CAS cluster (stage 2)."""
    Feature(run=load("cas.soak_tests.tests.primitives", "feature"))


@TestFeature
@Name("phase1")
def feature_phase1(self, **_kwargs):
    """Green-path soak (stage 3). Seed/ops/checkpoint-every live on context."""
    Feature(run=load("cas.soak_tests.tests.phase1", "feature"))


@TestFeature
@Name("phase2")
def feature_phase2(self, **_kwargs):
    """Chaos soak (stage 4). Seed/ops/chaos-interval live on context."""
    Feature(run=load("cas.soak_tests.tests.phase2", "feature"))


@TestFeature
@Name("phase3")
def feature_phase3(self, **_kwargs):
    """Wall-clock soak (stage 5). Duration/chaos flags live on context."""
    Feature(run=load("cas.soak_tests.tests.phase3", "feature"))


@TestFeature
@Name("scenarios")
def feature_scenarios(self, **_kwargs):
    """Adversarial cards. --scenario / --scenario-scale live on context."""
    Feature(run=load("cas.soak_tests.tests.scenarios", "feature"))
