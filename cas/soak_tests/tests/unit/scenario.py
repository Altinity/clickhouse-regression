from testflows.core import *
from testflows.asserts import error

from cas.soak_tests.oracle.events import cluster_events_delta, events_delta
from cas.soak_tests.oracle.scenario import select
from cas.soak_tests.oracle.verdict import (
    FAIL,
    INCONCLUSIVE,
    PASS,
    SKIPPED,
    ScenarioResult,
    Verdict,
    worst_status,
)
from cas.soak_tests.steps.card import assert_replicas_agree


@TestScenario
@Name("events delta drops zeros and reports resets")
def events_delta_drops_zeros_and_reports_resets(self):
    d = events_delta({"CASBlobPut": 10, "CASBlobHead": 5}, {"CASBlobPut": 17, "CASBlobHead": 5, "CASGCDelete": 3})
    assert d["CASBlobPut"] == 7, error()
    assert "CASBlobHead" not in d, error()
    assert d["CASGCDelete"] == 3, error()
    d2 = events_delta({"CASBlobPut": 100}, {"CASBlobPut": 4})
    assert d2["CASBlobPut"] == 4, error()


@TestScenario
@Name("cluster events delta totals")
def cluster_events_delta_totals(self):
    out = cluster_events_delta(
        {"ch1": {"CASBlobPut": 1}, "ch2": {"CASBlobPut": 2}},
        {"ch1": {"CASBlobPut": 5}, "ch2": {"CASBlobPut": 10}},
    )
    assert out["ch1"]["CASBlobPut"] == 4, error()
    assert out["ch2"]["CASBlobPut"] == 8, error()
    assert out["_total"]["CASBlobPut"] == 12, error()


@TestScenario
@Name("worst status ordering")
def worst_status_ordering(self):
    assert worst_status([]) == INCONCLUSIVE, error()
    assert worst_status([Verdict("a", "", "", PASS)]) == PASS, error()
    assert worst_status([Verdict("a", "", "", PASS), Verdict("b", "", "", SKIPPED)]) == SKIPPED, error()
    assert worst_status(
        [Verdict("a", "", "", PASS), Verdict("b", "", "", INCONCLUSIVE)]
    ) == INCONCLUSIVE, error()
    assert worst_status(
        [Verdict("a", "", "", INCONCLUSIVE), Verdict("b", "", "", FAIL)]
    ) == FAIL, error()


@TestScenario
@Name("verdict helpers")
def verdict_helpers(self):
    assert Verdict.check("x", "1", 1, True).status == PASS, error()
    assert Verdict.check("x", "1", 2, False).status == FAIL, error()
    assert Verdict.inconclusive("x", "1", "no data").status == INCONCLUSIVE, error()
    assert Verdict.skipped("x", "n/a").status == SKIPPED, error()
    reported = Verdict.reported("x", "n/a", 7, "non-gating")
    assert reported.status == PASS, error()
    assert reported.observed == "7", error()


@TestScenario
@Name("result finalize and markdown")
def result_finalize_and_markdown(self):
    r = ScenarioResult(scenario="S99", title="t", priority="P0", seed=1)
    r.add(Verdict.check("fsck dangling", "0", 0, True))
    r.add(Verdict.inconclusive("dryrun", "subset", "no detail"))
    r.finalize()
    assert r.status == INCONCLUSIVE, error()
    md = r.to_markdown()
    assert "S99" in md and "fsck dangling" in md and "Budget verdict" in md, error()


@TestScenario
@Name("select by priority and name")
def select_by_priority_and_name(self):
    import cas.soak_tests.cards  # noqa: F401

    p0 = select("P0")
    assert p0, error()
    assert all(c.priority == "P0" for c in p0), error()
    assert {c.name for c in p0} >= {
        "S01",
        "S02",
        "S03",
        "S04",
        "S05",
        "S06",
        "S07",
        "S08",
        "S09",
        "S10",
        "S11",
        "S12",
        "S13",
        "S14",
        "S38",
        "S40",
        "S42",
        "S43",
    }, error()
    assert select("S01") and select("S01")[0].name == "S01", error()
    assert select("S02") and select("S02")[0].name == "S02", error()
    assert select("S12") and select("S12")[0].compose_variant == "tenreplicas", error()
    assert select("S12")[0].needs_infra is None, error()
    assert select("all"), error()
    assert select("S99") == [], error()
    p0_names = [c.name for c in p0]
    assert p0_names[-1] == "S43", error()
    p1 = select("P1")
    assert p1, error()
    assert all(c.priority == "P1" for c in p1), error()
    assert {c.name for c in p1} >= {
        "S15",
        "S16",
        "S17",
        "S18",
        "S19",
        "S20",
        "S21",
        "S22",
        "S28",
        "S29",
        "S30",
        "S31",
        "S33",
        "S34",
        "S35",
        "S36",
        "S37",
        "S39",
        "S41",
        "S44",
        "S45",
    }, error()
    for name in ("S22", "S31", "S36", "S37", "S39", "S41"):
        assert select(name)[0].needs_infra is None, error()
        assert "run_inconclusive" not in select(name)[0].run.__code__.co_names, error()
    p1_names = [c.name for c in p1]
    assert p1_names[-1] == "S45", error()
    assert "S32" not in p1_names, error()
    p2 = select("P2")
    assert [c.name for c in p2] == ["S23", "S24", "S25", "S26", "S27", "S32"], error()
    assert all(c.priority == "P2" for c in p2), error()
    for name in ("S24", "S27"):
        assert select(name)[0].needs_infra is None, error()
        assert "run_inconclusive" not in select(name)[0].run.__code__.co_names, error()


@TestScenario
@Name("s01 params resolve per scale")
def s01_params_resolve_per_scale(self):
    from cas.soak_tests.cards.s01 import S01

    s = S01()
    assert s.resolve_params("dev")["blob_mib"] == 64, error()
    assert s.resolve_params("ci")["blob_mib"] == 512, error()
    assert s.resolve_params("full")["blob_mib"] == 102400, error()
    assert s.resolve_params("dev", {"blob_mib": "32"})["blob_mib"] == 32, error()


@TestScenario
@Name("s02 params resolve per scale")
def s02_params_resolve_per_scale(self):
    from cas.soak_tests.cards.s02 import S02, insert_plan

    s = S02()
    assert s.resolve_params("dev")["blob_mib"] == 64, error()
    assert s.resolve_params("ci")["blob_mib"] == 512, error()
    assert s.resolve_params("full")["blob_mib"] == 102400, error()
    plan = insert_plan(s.resolve_params("dev"))
    assert plan["per_row"] == 1_000_000, error()
    assert plan["rows"] == 67, error()
    assert plan["seed"] == 20260703, error()
    assert "generateRandom" in plan["gen"], error()
    assert plan["settings"]["max_threads"] == 1, error()
    ci = insert_plan(s.resolve_params("ci"))
    assert ci["per_row"] == 1_000_000, error()
    assert ci["rows"] == 536, error()


@TestScenario
@Name("p0 cards resolve params")
def p0_cards_resolve_params(self):
    from cas.soak_tests.cards.s03_s05 import S03, S05
    from cas.soak_tests.cards.s06_s08 import S06, S08
    from cas.soak_tests.cards.s09_s11 import S09
    from cas.soak_tests.cards.s12 import S12
    from cas.soak_tests.cards.s40 import S40

    assert S03().resolve_params("dev")["prefill_parts"] == 8, error()
    assert S05().resolve_params("dev")["tables"] == 200, error()
    assert S06().resolve_params("dev")["n_cols"] == 1000, error()
    assert S08().resolve_params("dev")["n_parts"] == 2000, error()
    assert S09().resolve_params("ci")["columns"] == 120, error()
    assert S12().compose_variant == "tenreplicas", error()
    assert S12().needs_infra is None, error()
    assert S12().resolve_params("ci")["replicas"] == 10, error()
    assert S40().resolve_params("dev")["pause_s"] == 105, error()
    from cas.soak_tests.steps.s3_inject import parse_ref_txn_id, render_ref_txn_id, HUGE_SEQ

    rendered = render_ref_txn_id(1, 2)
    assert rendered == "0000000000000001-0000000000000002", error()
    assert parse_ref_txn_id(rendered + ".zst") == (1, 2), error()
    assert parse_ref_txn_id("nope") is None, error()
    assert HUGE_SEQ == 0xFFFFFFFFFFFFFFFE, error()


@TestScenario
@Name("p1 cards resolve params")
def p1_cards_resolve_params(self):
    from cas.soak_tests.cards.s15_s18 import S15, S16
    from cas.soak_tests.cards.s19_s22 import S20, S22
    from cas.soak_tests.cards.s28_s33 import S28, S31
    from cas.soak_tests.cards.s36_s37 import S36, S37
    from cas.soak_tests.cards.s39 import S39
    from cas.soak_tests.cards.s41 import S41
    from cas.soak_tests.cards.s45 import S45

    assert S15().resolve_params("dev")["parts"] == 8, error()
    assert S16().resolve_params("dev")["cycles"] == 4, error()
    assert S20().resolve_params("dev")["parts"] == 3, error()
    assert S28().resolve_params("dev")["concurrency"] == 4, error()
    assert S45().resolve_params("dev")["victim_tables"] == 3, error()
    assert S22().compose_variant == "s3faultproxy", error()
    assert S31().compose_variant == "gc_shards2", error()
    assert S36().compose_variant == "multidisk", error()
    assert S37().compose_variant == "multidisk", error()
    assert S39().compose_variant == "s3faultproxy", error()
    assert S39().resolve_params("ci")["short_fault_s"] < 10, error()
    assert S41().compose_variant == "s41", error()
    assert S41().resolve_params("full")["rows"] == 10000000, error()
    for card in (S22(), S31(), S36(), S37(), S39(), S41()):
        assert card.needs_infra is None, error()


class _FakeNode:
    def __init__(self, container, values):
        self.container = container
        self._values = list(values)

    def query(self, _query):
        return self._values.pop(0) if len(self._values) > 1 else self._values[0]


class _FakeCluster:
    def __init__(self, *nodes):
        self._nodes = list(nodes)

    def nodes(self):
        return self._nodes


@TestScenario
@Name("replica agree waits for lag")
def replica_agree_waits_for_lag(self):
    r = ScenarioResult(scenario="S99", title="t", priority="P0", seed=1)
    cl = _FakeCluster(_FakeNode("ch1", ["50\thash"]), _FakeNode("ch2", ["0\t0", "50\thash"]))
    sleeps = []
    agree = assert_replicas_agree(r, cl, "q", sleep_fn=sleeps.append)
    assert agree is True, error()
    assert r.verdicts[-1].status == PASS, error()
    assert sleeps == [2.0], error()


@TestScenario
@Name("replica agree genuine divergence fails")
def replica_agree_genuine_divergence_fails(self):
    r = ScenarioResult(scenario="S99", title="t", priority="P0", seed=1)
    cl = _FakeCluster(_FakeNode("ch1", ["50\thash"]), _FakeNode("ch2", ["49\tother"]))
    sleeps = []
    agree = assert_replicas_agree(r, cl, "q", attempts=3, sleep_fn=sleeps.append)
    assert agree is False, error()
    assert r.verdicts[-1].status == FAIL, error()
    assert len(sleeps) == 2, error()


@TestScenario
@Name("replica agree error is not agreement")
def replica_agree_error_is_not_agreement(self):
    r = ScenarioResult(scenario="S99", title="t", priority="P0", seed=1)
    cl = _FakeCluster(
        _FakeNode("ch1", ["50\thash"]), _FakeNode("ch2", ["ERROR: readonly", "50\thash"])
    )
    agree = assert_replicas_agree(r, cl, "q", sleep_fn=lambda s: None)
    assert agree is True, error()
    r2 = ScenarioResult(scenario="S99", title="t", priority="P0", seed=1)
    cl2 = _FakeCluster(_FakeNode("ch1", ["ERROR: down"]), _FakeNode("ch2", ["ERROR: down"]))
    agree2 = assert_replicas_agree(r2, cl2, "q", attempts=2, sleep_fn=lambda s: None)
    assert agree2 is False, error()
    assert r2.verdicts[-1].status == INCONCLUSIVE, error()


@TestFeature
@Name("scenario")
def feature(self):
    for scenario in loads(current_module(), Scenario):
        Scenario(run=scenario)
