"""Physical CA-pool path classifier. Pure: no docker, no cas.soak."""

POOL_PREFIXES = ("blobs", "_manifests", "refs", "roots", "_files", "gc", "_pool_meta")


def classify_pool_path(key: str) -> str:
    """Bucket a pool object key by the per-server-tree layout.

    Manifests live under cas/manifests/; refs under cas/refs/. Leading soak_pool/ or ./ is skipped.
    """
    segs = [s for s in key.split("/") if s not in ("", ".")]
    for i, s in enumerate(segs):
        if s in ("blobs", "roots", "gc") or s.startswith("_pool_meta"):
            segs = segs[i:]
            break
        if s == "cas" and i + 1 < len(segs) and segs[i + 1] in ("manifests", "refs"):
            segs = segs[i:]
            break
    if not segs:
        return "other"
    if "_files" in segs:
        return "_files"
    head = segs[0]
    if head == "blobs":
        return "blobs"
    if head == "cas":
        if len(segs) > 1 and segs[1] in ("manifests", "refs"):
            return "_manifests" if segs[1] == "manifests" else "refs"
        return "other"
    if head == "roots":
        return "roots"
    if head == "gc":
        return "gc"
    if head.startswith("_pool_meta"):
        return "_pool_meta"
    return "other"


def parse_pool_find(text: str) -> dict:
    """Turn `stat -c '%s\\t%n'` lines into a prefix-bucketed shape dict with `_total` and `_ok`."""
    shape = {p: {"objects": 0, "bytes": 0} for p in POOL_PREFIXES}
    shape["other"] = {"objects": 0, "bytes": 0}
    total_obj = 0
    total_bytes = 0
    for line in text.splitlines():
        if "\t" not in line:
            continue
        size_s, path = line.split("\t", 1)
        try:
            size = int(size_s)
        except ValueError:
            continue
        rel = path[2:] if path.startswith("./") else path
        bucket = classify_pool_path(rel)
        if bucket not in shape:
            bucket = "other"
        shape[bucket]["objects"] += 1
        shape[bucket]["bytes"] += size
        total_obj += 1
        total_bytes += size
    shape["_total"] = {"objects": total_obj, "bytes": total_bytes}
    shape["_ok"] = True
    return shape
