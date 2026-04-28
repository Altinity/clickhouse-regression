#!/usr/bin/env python3
"""Parse a ci_run_report.html and emit failures from the relevant sections as JSON.

Usage:
    parse_report.py <url_or_path>

Output JSON shape:
    {
      "checks_errors":    [ {"job_status","job_name","test_status","test_name"} , ... ],
      "checks_new_fails": [ ... same shape ... ],
      "regression_new_fails": [ {"arch","job_name","status","test_name"} , ... ]
    }

Uses only the Python stdlib (html.parser, urllib).
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from html.parser import HTMLParser

CHECK_SECTIONS = {"Checks Errors", "Checks New Fails"}
REGRESSION_SECTION = "Regression New Fails"
JOBS_SECTION = "CI Jobs Status"
CVE_SECTION = "Docker Images CVEs"
WANTED_SECTIONS = CHECK_SECTIONS | {REGRESSION_SECTION, JOBS_SECTION, CVE_SECTION}


def load(src: str) -> str:
    if src.startswith("http://") or src.startswith("https://"):
        with urllib.request.urlopen(src, timeout=60) as r:
            return r.read().decode("utf-8", errors="replace")
    with open(src) as f:
        return f.read()


def clean_title(title: str) -> str:
    return re.sub(r"\s*\(\d+.*?\)\s*$", "", title).strip()


class ReportParser(HTMLParser):
    """Stream HTML parser that captures rows from <table>s following h2/h3 headings.

    Strategy:
      - Track current heading text (latest h2/h3) when its content is a section we want.
      - When the section is set and we hit a <table>, consume its <tr>/<td> until
        the table closes; record cells as a row.
      - Reset section when we see another h2/h3 (regardless of whether wanted).
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.section: str | None = None  # current wanted section, if any
        self._capturing_heading: str | None = None  # 'h2' or 'h3' or None
        self._heading_buf: list[str] = []

        self._in_table_for: str | None = None  # section the current table belongs to
        self._in_row = False
        self._in_cell = False
        self._cell_buf: list[str] = []
        self._row_cells: list[str] = []

        self.tables: dict[str, list[list[str]]] = {}
        # Raw heading text for sections that carry useful summary info in the title
        # (e.g. "Docker Images CVEs (0 high/critical)").
        self.raw_titles: dict[str, str] = {}

    # -- headings --------------------------------------------------------
    def handle_starttag(self, tag: str, attrs):
        if tag in ("h2", "h3"):
            self._capturing_heading = tag
            self._heading_buf = []
            return
        if tag == "table":
            # The table that follows the most recent wanted heading belongs to it.
            if self.section is not None and self._in_table_for is None:
                self._in_table_for = self.section
                self.tables.setdefault(self.section, [])
            return
        if self._in_table_for is not None:
            if tag == "tr":
                self._in_row = True
                self._row_cells = []
            elif tag in ("td", "th") and self._in_row:
                self._in_cell = True
                self._cell_buf = []

    def handle_endtag(self, tag: str):
        if tag in ("h2", "h3") and self._capturing_heading == tag:
            raw_title = "".join(self._heading_buf).strip()
            title = clean_title(raw_title)
            self._capturing_heading = None
            self._heading_buf = []
            if title in WANTED_SECTIONS:
                self.section = title
                self.raw_titles[title] = raw_title
            else:
                # New section starts — stop assigning future tables to the old one.
                self.section = None
            return

        if self._in_table_for is not None:
            if tag in ("td", "th") and self._in_cell:
                self._row_cells.append("".join(self._cell_buf).strip())
                self._cell_buf = []
                self._in_cell = False
            elif tag == "tr" and self._in_row:
                if self._row_cells:
                    self.tables[self._in_table_for].append(self._row_cells)
                self._row_cells = []
                self._in_row = False
            elif tag == "table":
                # Close out the table; further tables (e.g. nested sections) need a
                # fresh wanted heading to be captured.
                self._in_table_for = None
                self.section = None

    def handle_data(self, data: str):
        if self._capturing_heading is not None:
            self._heading_buf.append(data)
        elif self._in_cell:
            self._cell_buf.append(data)


def _toc_summary(html: str, anchor: str) -> str:
    """Return the TOC suffix for an anchor, e.g. '(0 high/critical)'.

    The Table of Contents lists each section as
        <li><a href="#anchor">Title</a> (suffix)</li>
    The heading <h2> itself does not contain the suffix, so we recover it here.
    """
    m = re.search(
        rf'<a[^>]*href="#{re.escape(anchor)}"[^>]*>[^<]*</a>\s*([^<]*)<',
        html,
    )
    return (m.group(1).strip() if m else "")


def parse(html: str) -> dict:
    p = ReportParser()
    p.feed(html)

    cve_suffix = _toc_summary(html, "docker-images-cves")
    cve_title = p.raw_titles.get("Docker Images CVEs", "Docker Images CVEs")
    if cve_suffix:
        cve_title = f"{cve_title} {cve_suffix}".strip()

    out = {
        "checks_errors": [],
        "checks_new_fails": [],
        "regression_new_fails": [],
        "ci_jobs_failed": [],   # all jobs from "CI Jobs Status" with status error/failure
        "cve_section_title": cve_title,
        "cve_high_critical": [],  # rows where Severity is High or Critical
    }

    def rows_after_header(rows: list[list[str]]) -> list[list[str]]:
        # First row is the header in these tables; skip it.
        return rows[1:] if rows else []

    for cells in rows_after_header(p.tables.get("Checks Errors", [])):
        out["checks_errors"].append({
            "job_status": cells[0] if len(cells) > 0 else "",
            "job_name":   cells[1] if len(cells) > 1 else "",
            "test_status": cells[2] if len(cells) > 2 else "",
            "test_name":  cells[3] if len(cells) > 3 else "",
        })
    for cells in rows_after_header(p.tables.get("Checks New Fails", [])):
        out["checks_new_fails"].append({
            "job_status": cells[0] if len(cells) > 0 else "",
            "job_name":   cells[1] if len(cells) > 1 else "",
            "test_status": cells[2] if len(cells) > 2 else "",
            "test_name":  cells[3] if len(cells) > 3 else "",
        })
    for cells in rows_after_header(p.tables.get("Regression New Fails", [])):
        out["regression_new_fails"].append({
            "arch":      cells[0] if len(cells) > 0 else "",
            "job_name":  cells[1] if len(cells) > 1 else "",
            "status":    cells[2] if len(cells) > 2 else "",
            "test_name": cells[3] if len(cells) > 3 else "",
        })
    # CI Jobs Status: Job Name | Job Status | Message | Results Link
    for cells in rows_after_header(p.tables.get("CI Jobs Status", [])):
        if len(cells) < 2:
            continue
        status = cells[1].strip().lower()
        if status in ("error", "failure"):
            out["ci_jobs_failed"].append({
                "job_name":   cells[0],
                "job_status": cells[1],
                "message":    cells[2] if len(cells) > 2 else "",
            })
    # Docker Images CVEs: Docker Image | Severity | Identifier | Namespace
    for cells in rows_after_header(p.tables.get("Docker Images CVEs", [])):
        if len(cells) < 2:
            continue
        severity = cells[1].strip().lower()
        if severity in ("high", "critical"):
            out["cve_high_critical"].append({
                "image":      cells[0],
                "severity":   cells[1],
                "identifier": cells[2] if len(cells) > 2 else "",
                "namespace":  cells[3] if len(cells) > 3 else "",
            })

    return out


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: parse_report.py <url_or_path>", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(parse(load(sys.argv[1])), indent=2))


if __name__ == "__main__":
    main()
