# CAS — Jepsen report, 2026-08-11

**Verdict: 8 of 8 scenarios passed. No acknowledged write was lost, no unexpected
value appeared, no server crashed.**

| | |
|---|---|
| Artifact | `cas-jepsen-artifacts-x86-31475969456.zip` (GitHub Actions run `31475969456`, x86) |
| Build under test | `26.6.2.20000.altinityantalya` |
| Run window | 2026-08-11, 09:06 → 17:18 GMT (~8 h wall clock) |
| Result | **8 successes, 0 failures, 0 unknown, 0 crashed** |

---

## 1. What was tested

Jepsen runs a real 3-node ClickHouse cluster, injects faults while clients write,
heals the faults, and then checks the surviving data against what clients were
told. It is the strongest safety evidence we have for CAS, because it tests the
system under partial failure rather than in a quiet room.

**Topology.** Three ClickHouse nodes (`172.18.0.4`, `.5`, `.6`) plus one Keeper
(`172.18.0.3`), all in Docker. Object storage is RustFS, reachable on the same
network, and every node's data sits on a content-addressed disk
(`metadata_type = cas`, storage policy `cas`). This is a **single shared CAS
pool** across the three replicas, which is the configuration CAS is designed for.

**Workload — `set`.** Clients insert unique integers into a
`ReplicatedMergeTree` table on the CAS policy. Inserts use `insert_quorum = 2`
with `async_insert = 0`. After the fault phase ends and the cluster heals,
Jepsen issues `SYSTEM SYNC REPLICA` and does one final `SELECT`, then checks two
things:

- **No lost writes** — every insert the client was told succeeded must be present.
- **No unexpected values** — nothing may appear that was never written.

**Parameters.** 3600 s per scenario, concurrency 12, target rate 10 ops/s,
8 scenarios (`--test-count 8`), one per nemesis.

**The 8 nemeses.** Four process faults and four network faults:

| Nemesis | Fault injected |
|---|---|
| `random-node-killer` | Kill ClickHouse on one random node, restart it |
| `all-nodes-killer` | Kill ClickHouse on *all* nodes at once, then restart |
| `random-node-hammer-time` | `SIGSTOP` one node (freeze), then `SIGCONT` |
| `all-nodes-hammer-time` | `SIGSTOP` all nodes, then `SIGCONT` |
| `simple-partitioner` | Split the cluster into two random halves |
| `bridge-partitioner` | Two nodes can't see each other; both see a third bridge node |
| `blind-node-partitioner` | One victim can't send to the others; they can still send to it |
| `blind-others-partitioner` | The reverse asymmetry |

---

## 2. Results

| Nemesis | Attempted | Acknowledged | Recovered | **Lost** | **Unexpected** | Valid? |
|---|---:|---:|---:|---:|---:|:--:|
| random-node-hammer-time | 35,925 | 19,150 | 1 | **0** | **0** | yes |
| bridge-partitioner | 35,879 | 18,696 | 0 | **0** | **0** | yes |
| all-nodes-hammer-time | 35,646 | 13,850 | 0 | **0** | **0** | yes |
| random-node-killer | 35,842 | 12,110 | 7 | **0** | **0** | yes |
| blind-node-partitioner | 35,829 | 6,941 | 0 | **0** | **0** | yes |
| simple-partitioner | 35,902 | 5,866 | 1 | **0** | **0** | yes |
| blind-others-partitioner | 35,886 | 5,400 | 0 | **0** | **0** | yes |
| all-nodes-killer | 35,612 | 2,378 | 12 | **0** | **0** | yes |
| **Total** | **286,521** | **84,391** | **21** | **0** | **0** | **8/8** |

Reading the columns:

- **Attempted** — insert operations the clients tried. Most fail during a fault; that is the point of the exercise, not a defect.
- **Acknowledged** — inserts the client was told had succeeded. These are the ones that carry a durability promise.
- **Recovered** — inserts whose outcome was indeterminate (the client got an error or a timeout) but which turned out to be present in the final read. Permitted and expected; an indeterminate write is allowed to land.
- **Lost** — acknowledged but missing from the final read. **This is the number that matters, and it is zero everywhere.**
- **Unexpected** — present but never written. Also zero everywhere.

Roughly 29% of attempted inserts were acknowledged across the run. That is a
function of how aggressive the faults are, not a throughput measurement: with
`insert_quorum = 2` on a 3-node cluster, any nemesis that removes two nodes makes
writes correctly unavailable. `all-nodes-killer` is the extreme case at 6.7%
acknowledged — expected, since it kills every node simultaneously — and it is
also the scenario with the most recovered writes (12), which is exactly the
in-flight-at-kill-time population.

Nemesis activity confirms the faults actually fired: 1,420–1,436 nemesis
operations in each partition scenario, 262–266 in the kill scenarios (kills are
slower, with sleeps between), 1,302 in `all-nodes-hammer-time`.

---

## 3. Server-log observations

Logs from the harshest scenario (`all-nodes-killer`, node `172.18.0.4`, 1 h):

**No crash of any kind.** No `Fatal`, no logical errors, no sanitizer reports, no
segfaults, no `std::terminate`. Across an hour of repeatedly killing every node
in the cluster, the server always came back and always converged.

**The error mix is entirely quorum-related, which is correct behavior:**

| Count | Error |
|---:|---|
| 843 | `Quorum for previous write has not been satisfied yet` (Code 286) |
| 363 | `Another quorum insert has been already started` (Code 286) |
| 174 | `Number of alive replicas (1) is less than requested quorum (2/3)` (TOO_FEW_LIVE_REPLICAS) |

These are the correct refusals to acknowledge a write that cannot meet its
durability contract. They are why the lost-write count is zero.

**One CAS-specific observation worth acting on.** 89 log records mention the
relink protocol, all of them the same abandonment:

```
Code: 210. DB::Exception: Source n3 did not prove it still holds the manifest it
offered for part all_0_126_19 by relink; the relink is abandoned and the fetch
will be retried later. (NETWORK_ERROR)
```

Functionally this is exactly right: the receiving replica refuses to adopt a
manifest the sender can no longer prove it holds, gives up on the metadata-only
fast path, and retries the fetch. Fail-closed, self-healing, no data lost — the
protocol behaving as designed while its peer is being killed.

The problem is that **all 89 are logged at `Error` severity**, and two of them
additionally surface as `MergeTreeBackgroundExecutor: Exception while executing
background task` complete with a stack trace. A benign, expected, self-correcting
retry should not look like an incident. On a cluster with real monitoring this
will page someone. Recommend demoting the abandonment path to `Warning` or
`Information`, or logging it once per part rather than per attempt.

---

## 4. What this does and does not prove

**Proven by this run:**

- ReplicatedMergeTree on a shared CAS pool does not lose acknowledged writes under node kills, process freezes, and four distinct network partition shapes, including asymmetric ones.
- It does not fabricate data.
- Replicas converge after healing.
- The server survives repeated hard kills on CAS storage without crashing.
- Quorum semantics are honored on CAS exactly as they would be on an ordinary disk.
- The replica-to-replica relink handshake is exercised and fails closed correctly when its precondition breaks.

**Not covered — do not read this report as evidence for any of it:**

- **Garbage collection and pool integrity.** Nothing here runs `ca-fsck` or checks for orphaned blobs, dangling refs, or leaked objects after the faults. A run can be Jepsen-clean and still have left the pool littered.
- **Relink efficiency.** The check is safety-only. Whether same-pool fetches actually avoid byte transfer is not measured. The 89 abandonments confirm the handshake runs but say nothing about the success rate in a quiet cluster — successes are not logged at this level. This remains an open question tracked in the CAS status report.
- **One workload only.** `set` is insert-plus-final-read. There is no read workload under fault, no partition DDL, no mutation, no `OPTIMIZE`, no schema change.
- **Single pool, single disk.** No cross-pool or cross-disk scenario, which is where our current known defects live.
- **No S3-level fault injection.** RustFS stayed healthy throughout. Object-store slowness, 5xx storms, throttling, and partial-write behavior are untested here.
- **x86 only**, one run per nemesis. No repetition, so this speaks to the absence of frequent bugs, not rare ones.

---

## 5. Recommendations

1. **Add a post-run pool check.** After each scenario heals, run `ca-fsck` and assert a clean pool, and record blob/ref counts. This is the single highest-value addition: it turns Jepsen from a data-safety check into a data-safety *and* storage-integrity check, and it directly covers the GC findings that the static audit rates highest.
2. **Demote the relink-abandonment log severity.** Benign retries logged as `Error` with stack traces will generate false alarms in production.
3. **Add S3-level faults.** A fault proxy in front of RustFS (the soak suite already has one) would exercise the object-store failure modes that CAS uniquely depends on.
4. **Run it more than once.** A single hour per nemesis on one architecture is a good gate but a weak search. Periodic longer runs would be worth the machine time.

---

## Appendix — how to reproduce

```bash
python3 cas/jepsen/run.py \
  --package docker://<clickhouse-image-or-url> \
  --minutes 60 \
  --test-count 8
```

Underlying invocation per the artifact:

```
lein run test-all --nodes-file .../nodes.txt --keeper 172.18.0.3 \
  --username root --ssh-private-key .../id_rsa \
  --time-limit 3600 --concurrency 12 -r 10.0 \
  --clickhouse-source http://172.18.0.1:8765/clickhouse \
  --reuse-binary --test-count 8
```

Pass criteria: every scenario `:valid? true`, `passed == --test-count`, and Lein
exit 0. Per-scenario evidence lives in
`jepsen.clickhouse/store/<scenario>/<timestamp>/` — `results.edn` for the verdict,
`history.txt` for the operation history, and `<node-ip>/logs.tar.gz` for server
logs. Setup: `cas/jepsen/README.md`.
