import os
import json

from pathlib import Path
from testflows.core import *
from importlib.machinery import SourceFileLoader


def snapshot_path(version: str) -> Path:
    """Get the path to the snapshot file for the given version."""
    snapshot_path = os.path.join(
        current_dir(),
        "snapshots",
        f"default_values.py.default values>={version}.snapshot",
    )
    if not os.path.exists(snapshot_path):
        raise FileNotFoundError(snapshot_path)
    return snapshot_path


def load_defaults(version: str) -> dict[str, str]:
    """Return default values of settings for the given version."""
    path = snapshot_path(version)
    mod = SourceFileLoader(version, str(path)).load_module()

    settings: dict[str, str] = {}
    for name, raw in vars(mod).items():
        if name.startswith("__") or not isinstance(raw, str):
            continue

        # raw ==  "'{\"value\":\"\\'auto(12)\\'\",\"changed\":0}'"
        # drop the outer single-quotes added by the snapshot generator
        json_str = raw.strip("'")

        # make the JSON valid:  \"\'abc\'\"  →  "\"abc\""
        json_str = json_str.replace(r"\'", "'")

        try:
            parsed = json.loads(json_str)
            # Handle both old format with "value" and new format with "default"
            if "value" in parsed:
                settings[name] = parsed["value"]
            elif "default" in parsed:
                settings[name] = parsed["default"]
            else:
                print(f"couldn't find 'value' or 'default' key for {name} in {path}")
        except (json.JSONDecodeError, KeyError):
            print(f"couldn't parse {name} in {path}")
    return settings


def diff(old: str, new: str) -> None:
    a, b = load_defaults(old), load_defaults(new)

    a_keys = set(a.keys())
    b_keys = set(b.keys())

    changed = sorted(k for k in a_keys & b_keys if a[k] != b[k])
    added = sorted(b_keys - a_keys)
    removed = sorted(a_keys - b_keys)

    print(f"### {old}  →  {new}")
    if not (changed or added or removed):
        print("No differences.\n")
        return

    if changed:
        print("*Changed*")
        for k in changed:
            print(f" • {k}: {a[k]!r} → {b[k]!r}")
    if added:
        print("\n*Added*")
        for k in added:
            print(f" • {k} (default {b[k]!r})")
    if removed:
        print("\n*Removed*")
        for k in removed:
            print(f" • {k}")
    print()


if __name__ == "__main__":
    version_1 = "25.3_antalya"
    version_2 = "25.6_antalya"

    diff(version_1, version_2)
