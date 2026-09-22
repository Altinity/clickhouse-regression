from testflows.core import *

from cas.soak_tests.oracle import Model, build_effective_ledger, generate_ledger
from cas.soak_tests.steps.checkpoint import green_checkpoint
from cas.soak_tests.steps.driver import Driver
from cas.soak_tests.steps.http import http_nodes_from_context
from cas.soak_tests.steps.table import soak_table


@TestScenario
@Name("green-path ledger matches model")
def green_path_ledger_matches_model(self):
    seed = int(getattr(self.context, "soak_seed", 1))
    ops = int(getattr(self.context, "phase1_ops", 200))
    checkpoint_every = int(getattr(self.context, "phase1_checkpoint_every", 50))
    workers = int(getattr(self.context, "phase1_workers", 6))
    max_cliffs = 2
    min_gap = max(1, ops // 4)

    with Given("a soak table and wall-clock base_time"):
        table = soak_table()
        base_time = (
            int(
                self.context.node.query(
                    "SELECT toUnixTimestamp(now()) FORMAT TabSeparated"
                ).output.strip()
            )
            - 60
        )
        note(f"base_time={base_time} seed={seed} ops={ops} checkpoint_every={checkpoint_every}")
        model = Model(seed=seed, base_time=base_time)
        driver = Driver(
            http_nodes=http_nodes_from_context(self.context.nodes),
            table=table,
            model=model,
            seed=seed,
            base_time=base_time,
            workers=workers,
        )

    ledger = generate_ledger(seed, ops)
    effective = build_effective_ledger(ledger, max_cliffs, min_gap)
    note(f"effective ledger: {len(effective)} ops, min_gap={min_gap}")

    try:
        with When(f"I execute {len(effective)} ops, checkpoint every {checkpoint_every}"):
            executed = 0
            for op in effective:
                driver.execute(op)
                executed += 1
                if executed % checkpoint_every == 0:
                    green_checkpoint(
                        driver=driver,
                        table=table,
                        model=model,
                        label=f"checkpoint {executed}",
                    )
            if executed == 0 or executed % checkpoint_every != 0:
                green_checkpoint(
                    driver=driver,
                    table=table,
                    model=model,
                    label="final checkpoint",
                )
        note(f"ABORTED-retried INSERT attempts: {driver.aborted_retries}")
    finally:
        driver.close()


@TestFeature
@Name("phase1")
def feature(self):
    """Green-path soak: seeded ledger, concurrent INSERT/OPTIMIZE, no chaos."""
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
