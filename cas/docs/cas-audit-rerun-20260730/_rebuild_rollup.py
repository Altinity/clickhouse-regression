#!/usr/bin/env python3
"""Rebuild RECONCILIATION.md + ISSUE-2031-DRAFT.md with zero not-reviewed."""
import re
import collections
import pathlib

root = pathlib.Path(__file__).resolve().parent

# --- parse original catalog ---
text = (root / "original-audit-gist.md").read_text()
end = text.find("## cas-ad1")
summary = text[:end]

tiers = {}
info = {}  # cas -> (title, class)
current = "?"
for line in summary.splitlines():
    if re.match(r"##\s*1\.", line):
        current = "High"
    elif re.match(r"##\s*2\.", line):
        current = "Medium"
    elif re.match(r"##\s*3\.", line):
        current = "Low"
    elif re.match(r"##\s*4\.", line):
        current = "Info"
    m = re.match(r"\|\s*(CAS-\d+)\s*\|\s*(.*?)\s*\|\s*([^|]*?)\s*\|", line)
    if m and m.group(1) not in info:
        title = re.sub(r"\*\*", "", m.group(2)).strip()
        info[m.group(1)] = (title, m.group(3).strip())
        tiers[m.group(1)] = current

# Issue historically lists CAS-009 as High; prefer High if present in High table already.
# Keep catalog tier as parsed.

# --- parse verdicts.tsv ---
rows = []
for line in (root / "verdicts.tsv").read_text().splitlines()[1:]:
    parts = line.split("\t")
    if len(parts) < 5:
        continue
    cas, sev, status, anchor, audit = parts[0], parts[1], parts[2], parts[3], parts[4]
    rows.append((cas, sev, status, anchor, audit))

by_cas = collections.defaultdict(list)
for r in rows:
    by_cas[r[0]].append(r)


def normalize(status: str) -> str:
    s = status.strip()
    sl = s.lower()
    if "not-reviewed" in sl or "❔" in s:
        return "❔ not-reviewed"
    if "still-present" in sl or "🔴" in s:
        return "🔴 still-present"
    if "will-fix" in sl or "🛠" in s:
        return "🛠 will-fix"
    if "partial" in sl or "mitigated" in sl or "🟡" in s:
        return "🟡 partial/mitigated"
    if "split-out" in sl or "↗" in s:
        return "↗ split-out"
    if "wontfix" in sl or "❌" in s:
        return "❌ wontfix"
    if "not-a-bug" in sl or "🚫" in s:
        return "🚫 not-a-bug"
    if "by-design" in sl or "📐" in s:
        return "📐 by-design"
    if "fixed" in sl or "verified" in sl or "✅" in s:
        return "✅ fixed"
    if "info" in sl or "⚪" in s:
        return "⚪ info"
    return s


RANK = {
    "🔴 still-present": 0,
    "🟡 partial/mitigated": 1,
    "🛠 will-fix": 2,
    "↗ split-out": 3,
    "❌ wontfix": 4,
    "🚫 not-a-bug": 5,
    "📐 by-design": 6,
    "✅ fixed": 7,
    "⚪ info": 8,
    "❔ not-reviewed": 9,
}

consolidated = {}
disagreements = []
for cas, items in by_cas.items():
    norms = [(normalize(st), st, anc, aud) for _, _, st, anc, aud in items]
    chosen = min(norms, key=lambda x: RANK.get(x[0], 50))
    unique_norms = sorted({n[0] for n in norms}, key=lambda x: RANK.get(x, 50))
    if len(unique_norms) > 1:
        disagreements.append((cas, [(n[3], n[0]) for n in norms], chosen[0]))
    anchor = chosen[2]
    if not anchor or anchor == "—":
        for n in norms:
            if n[2] and n[2] != "—":
                anchor = n[2]
                break
    sources = sorted({n[3] for n in norms})
    consolidated[cas] = {
        "status": chosen[0],
        "anchor": (anchor or "—")[:160],
        "sources": sources,
    }

missing = set(info) - set(consolidated)
if missing:
    raise SystemExit(f"Missing verdicts for: {sorted(missing)}")
if any(v["status"] == "❔ not-reviewed" for v in consolidated.values()):
    raise SystemExit("not-reviewed still present")

counts = collections.Counter(v["status"] for v in consolidated.values())
high_still = [
    cas
    for cas in sorted(info, key=lambda x: int(x[4:]))
    if tiers.get(cas) == "High" and consolidated[cas]["status"] == "🔴 still-present"
]
fixed = [c for c, v in consolidated.items() if v["status"] == "✅ fixed"]


def short_title(t: str) -> str:
    t = re.sub(r"\s+", " ", t)
    if len(t) > 140:
        return t[:137] + "…"
    return t


# --- RECONCILIATION.md ---
out = []
out.append("# CAS audit re-run — reconciliation vs current PR #2073 code\n")
out.append(
    "Date: 2026-07-30. Scope: static audit of Content-Addressed Storage backend, only CAS code paths.\n"
)
out.append("## Executive summary\n")
out.append(
    "- **131 / 131** original `CAS-###` ids re-verified (38 thematic audits + 1 backfill). **Zero `❔ not-reviewed`.**"
)
out.append(
    f"- **{counts['🔴 still-present']} still-present**, "
    f"**{counts['✅ fixed']} fixed**, "
    f"**{counts.get('🟡 partial/mitigated', 0)} partial/mitigated**, "
    f"**{counts.get('🛠 will-fix', 0)} will-fix**, "
    f"**{counts.get('📐 by-design', 0)} by-design**, "
    f"**{counts.get('⚪ info', 0)} info**, "
    f"**{counts.get('↗ split-out', 0)} split-out**."
)
out.append(f"- **High still-present**: {', '.join(high_still)}.")
fixed_s = ", ".join(sorted(fixed, key=lambda x: int(x[4:])))
out.append(f"- **Key wins (✅ fixed)**: {fixed_s}.")
out.append(
    "- Per-audit reports live under `reports/`; this file is the single triage table for issue #2031."
)
out.append("")
out.append("## Verdict counts\n")
out.append("| Verdict | Count |")
out.append("|---|---|")
for k in [
    "🔴 still-present",
    "✅ fixed",
    "🟡 partial/mitigated",
    "🛠 will-fix",
    "📐 by-design",
    "↗ split-out",
    "🚫 not-a-bug",
    "❌ wontfix",
    "⚪ info",
]:
    if counts.get(k):
        out.append(f"| {k} | {counts[k]} |")
out.append(f"| **Total** | **{sum(counts.values())}** |")
out.append("")
out.append("## Reconciliation table\n")

for tier_name in ["High", "Medium", "Low", "Info"]:
    out.append(f"### {tier_name} severity\n")
    out.append(
        "| CAS-id | Title | Class | Old sev | New status | Anchor | Sources |"
    )
    out.append("|---|---|---|---|---|---|---|")
    for cas in sorted(
        (c for c in info if tiers.get(c) == tier_name), key=lambda x: int(x[4:])
    ):
        title, cls = info[cas]
        v = consolidated[cas]
        src = ", ".join(v["sources"])
        out.append(
            f"| {cas} | {short_title(title)} | {cls} | {tier_name} | {v['status']} | `{v['anchor']}` | {src} |"
        )
    out.append("")

out.append("## Disagreements between audits\n")
if not disagreements:
    out.append("None.\n")
else:
    out.append("| CAS-id | Verdicts by audit | Chosen |")
    out.append("|---|---|---|")
    for cas, vs, chosen in sorted(disagreements, key=lambda x: int(x[0][4:])):
        vs_s = "; ".join(f"{a}:{s}" for a, s in vs)
        out.append(f"| {cas} | {vs_s} | {chosen} |")
    out.append("")

out.append("## Coverage\n")
out.append(
    f"All **{len(info)}** catalog ids have a verdict. "
    "No `❔ not-reviewed` rows remain after `reports/backfill-not-reviewed.md`.\n"
)

(root / "RECONCILIATION.md").write_text("\n".join(out))

# --- ISSUE-2031-DRAFT.md ---
CHECKED = {
    "✅ fixed",
    "🚫 not-a-bug",
    "📐 by-design",
    "⚪ info",
    "↗ split-out",
}

issue = []
issue.append(
    "**DRAFT — DO NOT POST until reviewed. Proposed replacement body for "
    "https://github.com/Altinity/ClickHouse/issues/2031.**\n"
)
issue.append(
    "# CAS (`metadata_type = content_addressed` MergeTree backend) — consolidated audit tracking\n"
)
issue.append(
    "This is a **tracking issue** for a static-analysis audit of the Content-Addressed Storage (CAS) MergeTree"
)
issue.append(
    "disk backend. It consolidates audit reports into a single deduplicated checklist of **131 distinct"
)
issue.append("findings**, each with a unique `CAS-###` id.\n")
issue.append("> [!IMPORTANT]")
issue.append(
    "> This is a static/logical review. **Many items are expected to be by-design, not-a-bug, latent, or"
)
issue.append(
    "> already-handled.** The checklist is meant to be triaged item-by-item — please dismiss or resolve freely.\n"
)
issue.append("### 📎 Audit reports")
issue.append(
    "- **Original (2026-07-09)**: https://gist.github.com/vzakaznikov/8b0506a495187ce3d634385544beebea"
)
issue.append(
    "- **Re-run vs PR #2073 (2026-07-30)**: *«GIST_URL_PLACEHOLDER»* — all per-audit reports + `RECONCILIATION.md` + New Findings."
)
issue.append(
    "- **PR under review**: https://github.com/Altinity/ClickHouse/pull/2073\n"
)
issue.append("### How to triage")
issue.append("For each item, when reviewed:")
issue.append(
    "1. **Check the box** once it is triaged (resolved, dismissed, or filed as its own issue)."
)
issue.append("2. Replace `resolution:` inline with a verdict, e.g.")
issue.append(
    "   `✅ fixed (#PR)` · `🛠 will-fix` · `❌ wontfix` · `🚫 not-a-bug` · `📐 by-design` · `🟡 needs-repro` · `↗ split-out (#NNN)` · `🔴 still-present`."
)
issue.append(
    "3. Add reasoning as a **comment** referencing the `CAS-###` id.\n"
)
issue.append("Severity is the highest assigned by any source audit. Class tags:")
issue.append(
    "`DATA-LOSS · LEAK · LIVENESS · CONCURRENCY · INTEGRITY · SECURITY · DECODE/DoS · COMPAT · FEATURE-GAP ·"
)
issue.append(
    "PERF/SCALE · OBSERV/DAY2 · COMPLIANCE · CONFIG · TEST-GAP · CORRECTNESS`.\n"
)
issue.append("---\n")

tier_headers = {
    "High": "## 🔴 High\n",
    "Medium": "## 🟠 Medium\n",
    "Low": "## 🟡 Low / hardening\n",
    "Info": "## ⚪ Info / by-design / verified-safe (non-actionable — for the record)\n",
}
for tier_name in ["High", "Medium", "Low", "Info"]:
    issue.append(tier_headers[tier_name])
    for cas in sorted(
        (c for c in info if tiers.get(c) == tier_name), key=lambda x: int(x[4:])
    ):
        title, cls = info[cas]
        v = consolidated[cas]
        box = "x" if v["status"] in CHECKED else " "
        t = short_title(title)
        issue.append(
            f'- [{box}] **{cas}** {t} · `{cls}` — resolution: {v["status"]} — `{v["anchor"]}`'
        )
    issue.append("")

issue.append("---\n")
issue.append("## 🆕 New findings from the 2026-07-30 re-run\n")
issue.append(
    "These are **new** issues surfaced against PR #2073 code that were **not** in the original 131-id catalog."
)
issue.append(
    "Full write-ups live in the re-run gist (`NEW-FINDINGS.md` and the per-audit `reports/*.md` \"New findings\" sections)."
)
issue.append(
    "Triage separately — do not reuse `CAS-###` ids from the original list.\n"
)
issue.append("«NEW_FINDINGS_SECTION_PLACEHOLDER»\n")
issue.append("---\n")
issue.append("<details>")
issue.append(
    "<summary>Genuine data-loss / correctness paths (the short list to look at first)</summary>\n"
)
issue.append(
    "`CAS-001` (reader pin), `CAS-002` (writer_epoch fencing — single highest-leverage fix), `CAS-015`"
)
issue.append(
    "(GC REBUILD mount-lease interlock), `CAS-016`/`CAS-017` (lifecycle expiration / Object Lock —"
)
issue.append(
    "config-triggered), and the integrity delegation `CAS-005`+`CAS-003`."
)
issue.append(
    "Everything else biases to a reclaimable **leak**, a **liveness/operability** cliff, or an **unverified edge**.\n"
)
issue.append("</details>\n")

(root / "ISSUE-2031-DRAFT.md").write_text("\n".join(issue))
print("Wrote RECONCILIATION.md + ISSUE-2031-DRAFT.md")
print("counts:", dict(counts))
print("disagreements:", len(disagreements))
print("OK: zero not-reviewed")
