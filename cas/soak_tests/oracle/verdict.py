"""Scenario verdict model. Pure: no cluster I/O, no imports from cas.soak."""

from dataclasses import asdict, dataclass, field

PASS = "pass"
FAIL = "fail"
INCONCLUSIVE = "inconclusive"
SKIPPED = "skipped"

_RANK = {PASS: 0, SKIPPED: 1, INCONCLUSIVE: 2, FAIL: 3}


@dataclass
class Verdict:
    name: str
    expected: str
    observed: str
    status: str
    note: str = ""

    @staticmethod
    def check(name: str, expected: str, observed, ok: bool, note: str = "") -> "Verdict":
        return Verdict(name, expected, str(observed), PASS if ok else FAIL, note)

    @staticmethod
    def inconclusive(name: str, expected: str, reason: str) -> "Verdict":
        return Verdict(name, expected, "unavailable", INCONCLUSIVE, reason)

    @staticmethod
    def skipped(name: str, reason: str) -> "Verdict":
        return Verdict(name, "(not run)", "skipped", SKIPPED, reason)

    @staticmethod
    def reported(name: str, expected: str, observed, note: str = "") -> "Verdict":
        """Recorded observation that never gates the run (status is pass)."""
        return Verdict(name, expected, str(observed), PASS, note)


def worst_status(verdicts) -> str:
    if not verdicts:
        return INCONCLUSIVE
    return max((v.status for v in verdicts), key=lambda s: _RANK.get(s, 0))


@dataclass
class ScenarioResult:
    scenario: str
    title: str
    priority: str
    seed: int
    params: dict = field(default_factory=dict)
    verdicts: list = field(default_factory=list)
    observations: dict = field(default_factory=dict)
    anomalies: list = field(default_factory=list)
    timings: dict = field(default_factory=dict)
    status: str = INCONCLUSIVE
    error: str = ""

    def add(self, v: Verdict) -> Verdict:
        self.verdicts.append(v)
        return v

    def note_anomaly(self, text: str) -> None:
        self.anomalies.append(text)

    def finalize(self, explicit_status: str | None = None) -> None:
        self.status = explicit_status or worst_status(self.verdicts)

    def to_json(self) -> dict:
        return asdict(self)

    def to_markdown(self) -> str:
        import json

        lines = [
            f"# {self.scenario}: {self.title}",
            "",
            f"- **Priority:** {self.priority}",
            f"- **Status:** `{self.status.upper()}`",
            f"- **Seed:** {self.seed}",
            "",
            "## Parameters",
            "",
            "```json",
            json.dumps(self.params, indent=2, default=str),
            "```",
            "",
            "## Budget verdict",
            "",
            "| metric | expected | observed | verdict |",
            "|---|---|---|---|",
        ]
        for v in self.verdicts:
            note = f" — {v.note}" if v.note else ""
            lines.append(
                f"| {v.name} | {v.expected} | {v.observed} | {v.status}{note} |"
            )
        lines.append("")
        if self.timings:
            lines.append("## Timings")
            lines.append("")
            for k, val in self.timings.items():
                lines.append(f"- {k}: {val}")
            lines.append("")
        if self.observations:
            lines.append("## Observations")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(self.observations, indent=2, default=str))
            lines.append("```")
            lines.append("")
        if self.anomalies:
            lines.append("## Anomalies")
            lines.append("")
            for a in self.anomalies:
                lines.append(f"- {a}")
            lines.append("")
        return "\n".join(lines)
