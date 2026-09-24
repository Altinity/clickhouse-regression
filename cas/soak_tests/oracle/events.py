"""ProfileEvents snapshot deltas. Pure: no cluster I/O."""


def events_delta(before: dict, after: dict) -> dict:
    """after - before for keys in after. Zero deltas dropped. Negative (reset) -> after value."""
    out = {}
    for k, v in after.items():
        d = v - before.get(k, 0)
        if d > 0:
            out[k] = d
        elif d < 0:
            out[k] = v
    return out


def cluster_events_delta(before: dict, after: dict) -> dict:
    """Per-node delta plus `_total` summing matched keys."""
    per_node = {}
    total = {}
    for cont, aft in after.items():
        d = events_delta(before.get(cont, {}), aft)
        per_node[cont] = d
        for k, v in d.items():
            total[k] = total.get(k, 0) + v
    per_node["_total"] = total
    return per_node
