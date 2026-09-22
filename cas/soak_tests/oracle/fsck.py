"""cas-fsck / cas-gc-dryrun parsers. Pure: no docker, no cluster."""

import re

PARTIAL_MARGIN_S = 20

# clickhouse disks writes cursor-control and color even when stdout is a file.
_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

KNOWN_DETAIL_CLASSES = (
    "reachable",
    "dangling",
    "unreachable",
    "pending-gc",
    "awaiting-gc",
    "unaccounted",
    "stale-edge",
    "corrupted-run",
)


class FsckTimeout(RuntimeError):
    """The fsck/dryrun scan exceeded its timeout."""


def parse_fsck_summary(line: str) -> dict:
    """Parse the single summary line from ``clickhouse disks cas-fsck``.

    On a ``--partial`` scan the line ends with ``reason='...'`` which can contain
    spaces; that field is trimmed off and parsed separately.
    """
    marker = " reason='"
    reason = None
    idx = line.find(marker)
    if idx != -1 and line.rstrip().endswith("'"):
        reason = line.rstrip()[idx + len(marker) : -1]
        line = line[:idx]

    out: dict = {}
    for tok in line.strip().split():
        if "=" in tok:
            kk, vv = tok.split("=", 1)
            out[kk] = float(vv) if "." in vv else int(vv)
    if reason is not None:
        out["reason"] = reason
    return out


def parse_fsck_detail(stdout: str) -> tuple[list[dict], list[str]]:
    """Parse TSV detail rows. Returns (rows, unknown_class_names)."""
    detail_rows: list[dict] = []
    unknown_classes: set[str] = set()
    for ln in stdout.splitlines():
        parts = ln.split("\t")
        if (
            len(parts) >= 3
            and parts[0] not in KNOWN_DETAIL_CLASSES
            and parts[0].islower()
            and " " not in parts[0]
            and parts[2].isdigit()
        ):
            unknown_classes.add(parts[0])
        if len(parts) >= 3 and parts[0] in KNOWN_DETAIL_CLASSES:
            detail_rows.append(
                {"class": parts[0], "key": parts[1], "size": int(parts[2])}
            )
    return detail_rows, sorted(unknown_classes)


def _plain_fsck_line(line: str) -> str:
    return _ANSI.sub("", line).strip()


def parse_fsck_stdout(stdout: str, *, exit_code: int, detail: bool) -> dict:
    """Build the fsck result dict the checkpoint asserts on."""
    summary_line = next(
        (plain for ln in stdout.splitlines() if (plain := _plain_fsck_line(ln)).startswith("reachable=")),
        "",
    )
    res = parse_fsck_summary(summary_line) if summary_line else {}
    res["exit_code"] = exit_code
    res["stdout"] = stdout
    if detail:
        rows, unknown = parse_fsck_detail(stdout)
        res["detail"] = rows
        if unknown:
            res["unknown_detail_classes"] = unknown
    return res


def stale_edge_verdict(fsck_result: dict, *, detail: bool) -> tuple:
    """Decide whether an fsck result proves the stale-edge class is empty.

    Verdict is one of ``absent``, ``found``, ``clean``, ``unchecked``.
    A missing ``stale_edge`` key fails closed (binary predates the class).
    """
    if "stale_edge" not in fsck_result:
        return (
            "absent",
            "fsck result carries no `stale_edge` field. `cas-fsck` prints it on every "
            "summary line, so this binary predates the StaleEdge class and the "
            "checkpoint cannot prove the class is empty. Failing CLOSED — a missing "
            "key is not zero.",
        )
    value = fsck_result["stale_edge"]
    if detail and value != 0:
        return (
            "found",
            f"fsck stale_edge = {value}: blob(s) whose every source edge names a "
            "manifest that no longer exists.",
        )
    if fsck_result.get("partial"):
        return (
            "unchecked",
            f"stale_edge was NOT checked: the scan is PARTIAL (reason: "
            f"{fsck_result.get('reason', 'unstated')}), so its counts are a lower bound.",
        )
    if detail:
        if value != 0:
            return (
                "found",
                f"fsck stale_edge = {value}: blob(s) whose every source edge names a "
                "manifest that no longer exists.",
            )
        return ("clean", "stale_edge == 0 on a --detail scan (cross-check ran)")
    if fsck_result.get("unreachable") == 0:
        return (
            "clean",
            "stale_edge == 0 implied: the summary counted zero unreferenced blobs",
        )
    return (
        "unchecked",
        f"stale_edge was NOT checked: this was a summary scan and "
        f"unreachable={fsck_result.get('unreachable')} > 0, so the printed "
        f"stale_edge={value} is structural rather than evidence",
    )


def parse_dryrun(text: str) -> dict:
    """Parse stdout of ``clickhouse disks cas-gc-dryrun``."""
    count = 0
    entries: list[dict] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("preview_deletes="):
            count = int(line.split("=", 1)[1])
        else:
            parts = line.split("\t")
            if len(parts) >= 3:
                entries.append(
                    {"reason": parts[0], "key": parts[1], "size": int(parts[2])}
                )
    return {"count": count, "entries": entries}
