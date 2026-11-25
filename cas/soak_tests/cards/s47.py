"""S47: a merge of text-index parts must commit past the 16 MiB inline cap.

A column ``.bin`` is stored as a blob, so column bytes never count toward the
inline cap. A skip-index file of 1 MiB or less is stored in the part manifest.
The total of those files cannot pass 16 MiB, or stageManifest throws
LIMIT_EXCEEDED. The customer's otel_logs merges fail that way: Wide parts
with several text indexes.

ClickHouse allows one text index per column. Each source part's tokens are
disjoint, so the merge unions the dictionaries. Files over 1 MiB spill to
blobs and leave the cap, so each index stays under 1 MiB and the number of
indexes carries the total past 16 MiB.
"""

import threading
import time

from cas.soak_tests.cards._p1 import scale_verdict
from cas.soak_tests.oracle.scenario import Scenario, register
from cas.soak_tests.oracle.verdict import Verdict
from cas.soak_tests.steps import card as C

_INDEX_SETTINGS = {"allow_experimental_full_text_index": "1"}


def _columns(n_text):
    """One text index per string column. ClickHouse rejects a second index on the same column."""
    cols = ["id UInt64", "body String"]
    cols += [f"t{i} String" for i in range(n_text)]
    indexes = [
        f"INDEX tx{i} t{i} TYPE text(tokenizer = splitByNonAlpha) GRANULARITY 1"
        for i in range(n_text)
    ]
    return ", ".join(cols + indexes)


def _word_expr(index_expr):
    """Eight letters from a mixed integer, so the dictionary does not collapse under LZ4.

    ``splitByNonAlpha`` drops digits, and ``w1 w2 w3`` compresses to almost nothing.
    The on-disk index is what the inline cap measures.
    """
    mixed = f"bitXor(multiply({index_expr}, 2654435761), 2246822519)"
    piece = mixed
    parts = []
    for _ in range(8):
        parts.append(f"substring('abcdefghijklmnopqrstuvwxyz', ({piece}) % 26 + 1, 1)")
        piece = f"intDiv({piece}, 26)"
    return "concat(" + ", ".join(parts) + ")"


def _insert_sql(op_id, n_text, tokens):
    """Disjoint tokens per part, so a merge unions the dictionaries."""
    start = op_id * tokens
    words = (
        f"arrayStringConcat(arrayMap(i -> {_word_expr(f'(i + {start})')}, "
        f"range({tokens})), ' ')"
    )
    cols = [f"{op_id} AS id", f"{words} AS body"]
    cols += [f"{words} AS t{i}" for i in range(n_text)]
    return "SELECT " + ", ".join(cols)


def _index_bytes(node, table):
    return node.query(
        "SELECT name, rows, secondary_indices_uncompressed_bytes, "
        "secondary_indices_compressed_bytes "
        f"FROM system.parts WHERE database = currentDatabase() AND table = '{table}' AND active "
        "ORDER BY name FORMAT TabSeparated"
    ).strip()


def _cap_exception(node, table):
    """The merge error, if stageManifest already rejected the part.

    OPTIMIZE FINAL on a replicated table retries a failed merge until the
    client gives up, so the LIMIT_EXCEEDED text shows up in part_log and the
    replication queue rather than as the OPTIMIZE response.
    """
    queries = (
        "SELECT exception FROM system.part_log "
        f"WHERE database = currentDatabase() AND table = '{table}' "
        "AND exception LIKE '%total inline%' "
        "ORDER BY event_time DESC LIMIT 1 FORMAT TabSeparated",
        "SELECT last_exception FROM system.replication_queue "
        f"WHERE database = currentDatabase() AND table = '{table}' "
        "AND last_exception LIKE '%total inline%' "
        "LIMIT 1 FORMAT TabSeparated",
    )
    for sql in queries:
        try:
            txt = node.query(sql, timeout=30).strip()
        except Exception:
            continue
        if txt:
            line = txt.splitlines()[0]
            stack = line.find("Stack trace")
            if stack != -1:
                line = line[:stack].rstrip(" ,")
            return line[:500]
    return ""


def _merge_diagnostics(node, table):
    try:
        return node.query(
            "SELECT event_type, error, substring(exception, 1, 240) FROM system.part_log "
            f"WHERE database = currentDatabase() AND table = '{table}' "
            "ORDER BY event_time DESC LIMIT 6 FORMAT TabSeparated",
            timeout=30,
        ).strip()
    except Exception as e:
        return str(e)[:300]


@register
class S47(Scenario):
    name = "S47"
    title = "text-index merge must commit past the 16 MiB inline cap"
    priority = "P1"
    param_table = {
        # 36 indexes * 50k disjoint letter-tokens. Measured on 26.8.34:
        # each source part's compressed text indexes are ~12.4 MiB (insert
        # commits, under 16 MiB) and the merge inlines 28,649,320 bytes.
        # The cap is a byte threshold, so dev, ci, and full use the same shape.
        "dev": {"text_indexes": 36, "tokens": 50000, "parts": 2, "merge_timeout_s": 600},
        "ci": {"text_indexes": 36, "tokens": 50000, "parts": 2, "merge_timeout_s": 1200},
        "full": {"text_indexes": 36, "tokens": 50000, "parts": 2, "merge_timeout_s": 1800},
    }

    def run(self, ctx, result):
        cl = ctx.cluster
        p = ctx.params
        n_text = int(p["text_indexes"])
        tokens = int(p["tokens"])
        n_parts = int(p["parts"])
        merge_timeout_s = int(p["merge_timeout_s"])
        table = "s47_text_cap"
        result.observations["tables"] = [table]
        scale_verdict(
            result,
            "text-index parts whose merged inline files can pass 16 MiB",
            f"{n_text} text indexes, {tokens} disjoint tokens per part, {n_parts} parts",
            "each source part stays under the cap; the merge is what crosses it",
        )

        C.create_ca_table(
            cl.node1,
            table,
            columns=_columns(n_text),
            order_by="id",
            client_settings=_INDEX_SETTINGS,
        )
        insert_error = None
        try:
            for i in range(n_parts):
                C.insert_values(
                    cl.node1,
                    table,
                    _insert_sql(i, n_text, tokens),
                    timeout=merge_timeout_s,
                    settings=_INDEX_SETTINGS,
                )
        except Exception as e:
            insert_error = str(e)[:500]
        cap_on_insert = bool(insert_error) and "total inline" in insert_error and "exceeds cap" in insert_error
        result.add(Verdict.check(
            "source parts commit",
            "each insert returns",
            insert_error or f"{n_parts} parts",
            insert_error is None,
            "the cap fired on insert, before the merge" if cap_on_insert else (insert_error or ""),
        ))
        if insert_error:
            C.standard_end(cluster=cl, result=result, tables=[table], expect_exception=True)
            return

        before = _index_bytes(cl.node1, table)
        result.observations["index_bytes_before_merge"] = before
        ctx.log(f"S47 index bytes before merge:\n{before}")

        holder = {"error": None, "done": False}

        def _optimize():
            try:
                cl.node1.command(
                    f"OPTIMIZE TABLE {table} FINAL",
                    timeout=merge_timeout_s,
                    settings=_INDEX_SETTINGS,
                )
            except Exception as e:
                holder["error"] = str(e)[:800]
            finally:
                holder["done"] = True

        # OPTIMIZE FINAL retries a merge that stageManifest rejects, so the
        # client would sit until merge_timeout_s. Watch the logs and stop.
        thread = threading.Thread(target=_optimize, daemon=True)
        thread.start()
        merge_error = None
        cap = ""
        t0 = time.monotonic()
        while time.monotonic() - t0 < merge_timeout_s:
            cap = _cap_exception(cl.node1, table) or _cap_exception(cl.node2, table)
            if cap:
                merge_error = cap
                break
            if holder["done"]:
                merge_error = holder["error"]
                break
            time.sleep(1)
        else:
            merge_error = holder["error"] or "timed out"
        if cap or not holder["done"]:
            try:
                cl.node1.query(
                    f"KILL QUERY WHERE query LIKE 'OPTIMIZE TABLE {table}%' SYNC",
                    timeout=30,
                )
            except Exception:
                pass
        thread.join(timeout=30)
        result.timings["merge_s"] = round(time.monotonic() - t0, 1)
        if merge_error and "total inline" not in merge_error:
            result.observations["merge_part_log"] = _merge_diagnostics(cl.node1, table)
        if merge_error is None:
            after = _index_bytes(cl.node1, table)
            result.observations["index_bytes_after_merge"] = after
            ctx.log(f"S47 index bytes after merge:\n{after}")
        cap_hit = bool(merge_error) and "total inline" in merge_error and "exceeds cap" in merge_error
        result.add(Verdict.check(
            "merge of text-index parts commits",
            "OPTIMIZE FINAL returns",
            merge_error or "committed",
            merge_error is None,
            "stageManifest rejected the part after the merge wrote it: "
            "total inline exceeds 16 MiB"
            if cap_hit else (merge_error or ""),
        ))
        if merge_error is None:
            count = cl.node1.query(f"SELECT count() FROM {table} FORMAT TabSeparated").strip()
            result.add(Verdict.check(
                "merged part keeps its rows",
                str(n_parts),
                count,
                count == str(n_parts),
            ))
            C.assert_replicas_agree(
                result, cl, C.table_checksum_query(table), name="S47 replica agreement"
            )
        C.standard_end(
            cluster=cl,
            result=result,
            tables=[table],
            expect_exception=merge_error is not None,
        )
