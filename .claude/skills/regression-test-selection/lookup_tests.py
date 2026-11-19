#!/usr/bin/env python3
"""List the regression tests for taxonomy ids.

The model chooses the ids. This script reads mapping.yaml beside itself and
prints the suites and scenarios for those ids. It does not decide whether a
change activates an id.

Usage:
    python3 lookup_tests.py functions.string.base58_encode functions.encryption.encrypt
"""

import json
import re
import sys
from pathlib import Path

import yaml

MAPPING = Path(__file__).with_name("mapping.yaml")
FLAG = re.compile(r"--[A-Za-z0-9-]+")


def load_suites() -> list[dict]:
    document = yaml.safe_load(MAPPING.read_text())
    return document["suites"]


def flag_tokens(description: str) -> list[str]:
    found = []
    for token in FLAG.findall(description or ""):
        if token not in found:
            found.append(token)
    return found


def fips_only(feature: dict) -> bool:
    text = feature.get("description") or ""
    return "FIPS" in text


def lookup(ids: list[str]) -> dict:
    wanted = list(dict.fromkeys(ids))
    wanted_set = set(wanted)
    seen_ids: set[str] = set()
    jobs = []
    manual = []
    needs_flag = []
    for suite in load_suites():
        suite_path = suite.get("path")
        if not suite_path or suite_path == ".":
            continue
        suite_manual = suite.get("ci") == "manual"
        scenarios: list[str] = []
        flags: list[str] = []
        hit_ids: list[str] = []
        for feature in suite.get("features") or []:
            feature_id = feature.get("id")
            if feature_id not in wanted_set:
                continue
            seen_ids.add(feature_id)
            entry_scenarios = list(feature.get("scenarios") or [])
            entry_flags = flag_tokens(feature.get("description") or "")
            if suite_manual or feature.get("ci") == "manual" or fips_only(feature):
                manual.append(
                    {
                        "suite_name": suite_path,
                        "id": feature_id,
                        "scenarios": entry_scenarios,
                        "flags": entry_flags,
                        "description": feature.get("description") or "",
                        "fips_only": fips_only(feature),
                    }
                )
                continue
            if not entry_scenarios and not entry_flags:
                needs_flag.append(
                    {
                        "suite_name": suite_path,
                        "id": feature_id,
                        "description": feature.get("description") or "",
                    }
                )
                continue
            if feature_id not in hit_ids:
                hit_ids.append(feature_id)
            for path in entry_scenarios:
                if path not in scenarios:
                    scenarios.append(path)
            for token in entry_flags:
                if token not in flags:
                    flags.append(token)
        if not hit_ids:
            continue
        only = ""
        if scenarios:
            only = "--only " + " ".join(f'"{path}"' for path in scenarios)
        regression_args = " ".join(flags + ([only] if only else [])).strip()
        jobs.append(
            {
                "suite_name": suite_path,
                "ids": hit_ids,
                "scenarios": scenarios,
                "flags": flags,
                "regression_args": regression_args,
            }
        )
    return {
        "ids": wanted,
        "jobs": jobs,
        "manual": manual,
        "needs_flag": needs_flag,
        "ids_with_no_suite": [feature_id for feature_id in wanted if feature_id not in seen_ids],
    }


def main() -> int:
    ids = [item for item in sys.argv[1:] if item]
    if not ids:
        print("usage: lookup_tests.py <taxonomy-id> [<taxonomy-id> ...]", file=sys.stderr)
        return 2
    json.dump(lookup(ids), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
