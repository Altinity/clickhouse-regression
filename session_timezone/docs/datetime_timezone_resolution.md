# DateTime Timezone Resolution in ClickHouse

> **Sources:**
> - `src/Core/Settings.cpp` — official `session_timezone` setting description and examples
> - `src/DataTypes/DataTypeDateTime.h` — column type comments
> - ClickHouse docs: [DateTime](https://clickhouse.com/docs/sql-reference/data-types/datetime),
>   [DateTime64](https://clickhouse.com/docs/sql-reference/data-types/datetime64)
> - [ClickHouse PR #100647](https://github.com/ClickHouse/ClickHouse/pull/100647) — fixes `session_timezone` for server-side `DateTime` / `DateTime64` parsing (backported to 26.2.x / 26.3.x; user-visible jump often **26.2.3 → 26.2.4** on the 26.2 branch)

**Contents:** [Storage](#how-datetime-values-are-stored) · [Column types](#column-timezone-what-gets-stored-at-create-table) · [Cases 1–7](#detailed-examples-same-instant-three-column-types) · [No session_timezone](#behavior-without-session_timezone-beta) · [With session_timezone](#behavior-with-session_timezone-beta) · [Summary table](#summary-timezone-used-for-parsing) · [timezone()](#the-timezone-function) · [DateTime64](#datetime64-short) · [DST](#dst-and-ambiguous-local-times) · [JOINs / distributed](#joins-subqueries-and-distributed) · [Clients](#clients-and-default-settings) · [Troubleshooting](#troubleshooting) · [Version history](#version-history) · [Appendix tz_proof](#appendix--reproducible-tz_proof-table-recheck)

> **Scope:** This note describes **observed / documented** rules for interactive SQL and
> common client paths. Upstream may refine edge cases (mutations, mixed `ALTER`, specific
> format parsers). When in doubt, run the [appendix](#appendix--reproducible-tz_proof-table-recheck)
> on your exact build (`SELECT version()`).

---

## How DateTime Values Are Stored

`DateTime` values are stored internally as **Unix timestamps** — seconds since
`1970-01-01 00:00:00 UTC`. The stored integer has **no timezone label**. A timezone
only matters when converting between that integer and a human-readable string:

- **Parsing:** `'2000-01-01 06:00:00'` → Unix timestamp (depends on *which* timezone interprets the string)
- **Display:** Unix timestamp → string (depends on *which* timezone formats the output)

The same Unix timestamp displays differently in different timezones:

```sql
-- Unix timestamp 946706400:
-- In UTC:                  2000-01-01 06:00:00
-- In Asia/Novosibirsk:     2000-01-01 12:00:00  (UTC+6 in year 2000)
```

---

## Column Timezone: What Gets Stored at CREATE TABLE

### `DateTime` — no explicit timezone

```sql
CREATE TABLE t (d DateTime) ENGINE = MergeTree ...
```

**No timezone name is stored in the column metadata.** The persisted type string is
just `DateTime` (no argument), and `has_explicit_time_zone` is `false` in the type
descriptor. However, the `DataTypeDateTime` object **always carries an associated
timezone** — a `DateLUTImpl` reference from `DateLUT::instance()` at the time the
type is bound to the query.

How that timezone is resolved depends on **build** and **code path** (interactive
`WHERE`, sync insert, async insert, HTTP). See **[Version history](#version-history)** for
the **PR #100647** split (server-side serialization vs `session_timezone`). In broad
terms: plain `DateTime` uses **server** timezone when `session_timezone` is unset, and
**session** timezone when it is set — on versions where the setting is wired through for
that path.

### `DateTime('TZ')` — explicit timezone

```sql
CREATE TABLE t (d DateTime('Asia/Novosibirsk')) ENGINE = MergeTree ...
```

The name `Asia/Novosibirsk` **is stored** in metadata. That timezone is used for parsing
and display of **this column**, regardless of server timezone or `session_timezone`
(for string literals tied to the column and for display rules described below).

---

## Detailed examples: same instant, three column types

Fix one row in your head: **Unix `946706400`** = `2000-01-01 06:00:00` **UTC**.

| Column type | Meaning for that cell |
|-------------|------------------------|
| `DateTime` (no tz) | Still **946706400**; *which* clock reads `'…'` strings / formats output follows **effective** tz (server or session, by version and setting). |
| `DateTime('UTC')` | Still **946706400**; literals for this column use **UTC**; display in UTC unless output rules say otherwise. |
| `DateTime('Europe/Berlin')` | Still **946706400**; in January 2000 (CET, UTC+1) wall-clock in Berlin is **`2000-01-01 07:00:00`** for that same instant. |

### Case 1 — String literal in `WHERE`, no `session_timezone`

The string is interpreted in the **column’s** parsing timezone:

- **`DateTime`:** **server** timezone when `session_timezone` is unset; **session** when set (on builds where that path respects the setting; see [Version history](#version-history)).
- **`DateTime('UTC')`:** **UTC** (always).
- **`DateTime('Europe/Berlin')`:** **Europe/Berlin** (always).

Example pattern (exact counts depend on server tz; see appendix for a full script):

```sql
-- If server timezone is UTC:
--   d_server = '2000-01-01 06:00:00'  → parsed as 06:00 UTC → matches 946706400 → matched = 1

-- If server timezone were Europe/Berlin:
--   '2000-01-01 07:00:00' on d_berlin  → parsed as 07:00 Berlin = 946706400 → matched = 1
```

### Case 2 — `toDateTime('…')` without second argument

The string is interpreted in the **server** timezone (not the column’s explicit tz),
unless `session_timezone` is set (then see Case 4).

So **`DateTime('UTC')`** vs **`toDateTime('2000-01-01 00:00:00')`** can disagree even when
you “mean” UTC: the literal uses the column, the function uses the server/session clock.

### Case 3 — `toDateTime('…', 'TZ')` with explicit timezone

Always uses the given timezone. Prefer this when you want a stable meaning:

```sql
WHERE d_utc = toDateTime('2000-01-01 06:00:00', 'UTC')   -- unambiguous
```

### Case 4 — `session_timezone` set (Beta)

For **`DateTime` without explicit tz**, `session_timezone` replaces the server timezone
for **both** parsing of literals tied to that column and **default** display (see
official docs for edge cases).

For **`DateTime('UTC')`** (or any explicit column tz), **string literals in `WHERE`**
still use the **column** timezone. **`toDateTime('…')` without a tz argument** still
follows **session** (or server), which is the documented **asymmetry**:

```sql
-- Stored: 2000-01-01 00:00:00 UTC  (example)
SELECT * FROM t
WHERE d = '2000-01-01 00:00:00'
SETTINGS session_timezone = 'Asia/Novosibirsk';   -- literal uses column UTC → can match

SELECT * FROM t
WHERE d = toDateTime('2000-01-01 00:00:00')
SETTINGS session_timezone = 'Asia/Novosibirsk';   -- function uses session → often no match
```

> To avoid surprises, use **`toDateTime('…', 'UTC')`** (or the column’s tz) whenever you
> compare against `DateTime('UTC')` columns.

### Case 5 — `SELECT` display

- **`DateTime`:** formatted using **server** tz, or **session** tz if set (when the build
  wires `session_timezone` through for display of plain `DateTime`).
- **`DateTime('UTC')`:** display follows the **column** tz (UTC), while `timeZone()` can
  still show the session — do not confuse the two.
- **`DateTime('Europe/Berlin')`:** display in **Berlin** for that column’s values.

### Case 6 — `INSERT` from string literals

Strings in `INSERT … VALUES ('2000-01-01 06:00:00')` are coerced to the **destination
column’s** parsing rules — same idea as `WHERE`:

| Target column | String `'2000-01-01 06:00:00'` is read as |
|----------------|-------------------------------------------|
| `DateTime` | **Server** tz, or **session** when `session_timezone` is set and respected on that insert path (post-#100647). |
| `DateTime('UTC')` | **06:00 UTC** |
| `DateTime('Europe/Berlin')` | **06:00 Berlin** wall time (not “06:00 UTC” unless it coincides). |

Prefer **`INSERT … SELECT toDateTime('…', 'TZ')`** when the source string is authored in
a known zone (ETL configs, CSV fields) so the insert does not depend on where the server
runs.

### Case 7 — Comparing columns or mixing with `toDateTime`

Comparisons use the **same instant** (Unix seconds) after both sides are evaluated.
Pitfalls happen when **each side** was built with a different parsing clock:

```sql
-- RHS uses server/session; LHS uses column tz if it is a bare literal on that column
WHERE d_utc = toDateTime('2000-01-01 06:00:00');          -- risky if server ≠ UTC
WHERE d_utc = toDateTime('2000-01-01 06:00:00', 'UTC');   -- stable
```

Casting `d_server` ↔ `d_utc` does **not** rewrite the stored integer; it may only change
how future string I/O treats the value. For storage that is always “UTC semantics”, use
`DateTime('UTC')` (or store UTC epoch in `UInt32` / document server tz).

---

## Behavior Without session_timezone (Beta)

The **server timezone** governs parsing for `toDateTime('…')` without tz and governs
effective timezone for plain `DateTime` columns (subject to the version notes above).

### String literals → column’s effective timezone

```sql
-- Plain DateTime: string parsed in server timezone (e.g. Europe/Berlin)
WHERE d = '2000-01-01 06:00:00'

-- DateTime('UTC'): string parsed in UTC
WHERE d = '2000-01-01 06:00:00'
```

### `toDateTime()` without explicit timezone → server timezone

```sql
WHERE d = toDateTime('2000-01-01 06:00:00')
-- Interpreted in server timezone, regardless of column type
```

### `toDateTime()` with explicit timezone → always that timezone

```sql
WHERE d = toDateTime('2000-01-01 06:00:00', 'UTC')
```

### SELECT display (illustration)

```sql
-- Stored: Unix timestamp 946706400

SELECT d FROM t;
-- DateTime (no tz), server = Europe/Berlin:      2000-01-01 07:00:00
-- DateTime('UTC'):                                2000-01-01 06:00:00
-- DateTime('Asia/Novosibirsk') (UTC+6 in 2000):  2000-01-01 12:00:00
```

---

## Behavior With session_timezone (Beta)

> `session_timezone` is a **Beta** setting. Not every DateTime-related function follows
> it; prefer explicit `toDateTime(..., 'TZ')` in comparisons.

```sql
SET session_timezone = 'Asia/Novosibirsk';
-- or per query:
SELECT ... SETTINGS session_timezone = 'Asia/Novosibirsk';
```

### Plain `DateTime`: session replaces server for that column’s literal parsing and display

```sql
-- Table stores UTC midnight as Unix 946684800
SELECT d, timezone() FROM t
SETTINGS session_timezone = 'Asia/Novosibirsk';
-- d shown in Novosibirsk; timezone() reports session

SELECT * FROM t WHERE d = '2000-01-01 06:00:00'
SETTINGS session_timezone = 'Asia/Novosibirsk';
-- Literal parsed in session tz → matches if that wall time equals stored instant

SELECT * FROM t WHERE d = '2000-01-01 00:00:00'
SETTINGS session_timezone = 'Asia/Novosibirsk';
-- Often no match if stored instant is not midnight in that zone
```

### `DateTime('UTC')`: column wins for literals; `toDateTime('…')` one-arg still uses session/server

See **Case 4** above — same SQL pattern, documented asymmetry between literals and
`toDateTime()` without a timezone argument.

---

## Summary: Timezone Used for Parsing

| Expression | `DateTime` (no tz) | `DateTime('UTC')` | `DateTime('Europe/Berlin')` |
|---|---|---|---|
| `'…'` in `WHERE`, no `session_timezone` | Server | UTC | Europe/Berlin |
| `'…'` in `WHERE`, `session_timezone` set | **Session** (plain `DateTime`, post-#100647) | UTC | Europe/Berlin |
| `toDateTime('…')` one-arg, no session | Server | Server | Server |
| `toDateTime('…')` one-arg, session set | **Session** | **Session** | **Session** |
| `toDateTime('…', 'TZ')` | `'TZ'` | `'TZ'` | `'TZ'` |
| `SELECT` display, no session | Server | UTC | Europe/Berlin |
| `SELECT` display, session set | **Session** (plain `DateTime`) | UTC | Europe/Berlin |

---

## The `timezone()` Function

`timezone()` / `timeZone()` returns the **effective session timezone**: `session_timezone`
if set, otherwise the server timezone. It does **not** switch per column; explicit
`DateTime('TZ')` columns still parse/display in their own tz.

```sql
SELECT timeZone(), serverTimeZone() FORMAT CSV;

SELECT timeZone(), serverTimeZone()
SETTINGS session_timezone = 'Asia/Novosibirsk' FORMAT CSV;
-- "Asia/Novosibirsk","Europe/Berlin"   -- example if server is Berlin
```

---

## `DateTime64` (short)

`DateTime64(precision, 'TZ')` stores **sub-second** values with a fixed scale; the
optional `'TZ'` behaves like `DateTime('TZ')` for that column’s parsing and display.
Rules for **which** clock parses a bare string still follow the same split: **column
explicit tz** vs **server/session** for functions such as one-argument `toDateTime64`.
When you need cross-version stability, keep the same habit: **pass the timezone
explicitly** in the constructor you use in `INSERT`/`WHERE`.

---

## DST and ambiguous local times

Zones with daylight saving time have two practical footguns for `DateTime` (second
precision, no offset in the string):

1. **Non-existent local time** (spring “gap”): e.g. a clock jumps from `02:59` to
   `04:00`. A string like `02:30` on that date may be invalid or be adjusted by rules
   in the IANA zone and ClickHouse — **do not rely** on wall-clock strings across DST
   transitions without checking.

2. **Repeated local time** (autumn “fold”): the same wall-clock hour happens twice with
   different UTC offsets. Parsing `'YYYY-MM-DD HH:MM:SS'` without an offset can map to
   **either** occurrence depending on rules and version.

**Practical mitigations**

- Store **UTC** in `DateTime('UTC')` (or epoch in `UInt32` / `Int64`) and convert only at
  the UI layer.
- If you must store local civil time, use **`DateTime64`** with explicit zone and/or
  supply **offset-aware** input formats where your pipeline allows.
- In tests and ETL, prefer **`toDateTime('…', 'UTC')`** (or **`toDateTime64`** with an
  explicit zone) over bare strings; for free-form text, use a parser that accepts an
  explicit timezone where your ClickHouse version supports it.

---

## JOINs, subqueries, and distributed

- **Single query, one session:** `SETTINGS session_timezone = '…'` applies to the whole
  statement, including subqueries and both sides of a `JOIN`, for settings that are
  propagated that way. Plain `DateTime` literals still follow **session/server**;
  `DateTime('TZ')` columns still follow **their** column tz.

- **`GLOBAL` / distributed plans:** remote stages execute with the **remote** server’s
  default session unless you set session-level options in a way the initiator forwards.
  If a shard’s `timezone` in `config.xml` differs from the initiator, **one-arg**
  `toDateTime('…')` can disagree across nodes. Mitigation: explicit **`'TZ'`** in
  constructors, or align shard configs.

- **Comparing `DateTime` to `DateTime('UTC')`:** comparison is on **Unix seconds** after
  evaluation; mismatches usually mean the **two expressions were parsed with different
  clocks**, not that `DateTime` “lost” a timezone bit.

---

## Clients and default settings

| Client | What to watch |
|--------|----------------|
| `clickhouse-client` | Uses server defaults unless you `SET session_timezone = …` or pass `session_timezone` in the query. |
| HTTP / `play` | Query string or JSON body can carry `session_timezone`; otherwise server default. |
| JDBC / ODBC / drivers | Often expose server timezone or allow per-connection session settings — **verify** your pool does not pin an old default after a server upgrade. |
| `clickhouse-local` | Inherits host/OS context; not identical to production `config.xml` `timezone`. |

For regression tests, set **`session_timezone` explicitly** in the query (or in the
test harness) when asserting on plain `DateTime` string parsing, so results do not depend
on the runner’s server tz alone.

---

## Troubleshooting

| Symptom | Likely cause | What to try |
|--------|----------------|-------------|
| `WHERE d = '…'` returns 0 rows | Literal parsed in **server** (or **session**) tz for plain `DateTime`, not what you assumed | `SELECT serverTimeZone(), timeZone();` then match the string to that zone, or use `toDateTime('…', 'TZ')`. |
| Literal works but `toDateTime('…')` does not | **Asymmetry** on `DateTime('UTC')`: literal uses column, one-arg `toDateTime` uses server/session | `toDateTime('…', 'UTC')` (or column tz). |
| CI passes locally fails | Different **server** `timezone` in `config.xml` / image | Pin comparisons with explicit `'TZ'` or align test container tz. |
| After minor upgrade, plain `DateTime` / inserts changed | **`session_timezone`** wired for server-side parsing ([PR #100647](https://github.com/ClickHouse/ClickHouse/pull/100647)) | Re-read **Case 1** / appendix **Query C**; pin `session_timezone` in tests. |

---

## Version History

| Version | Behavior |
|---|---|
| **Before** [PR #100647](https://github.com/ClickHouse/ClickHouse/pull/100647) on your branch | Plain `DateTime` could use timezone **baked into serialization from table metadata** (`CREATE TABLE` time), so **`session_timezone` was ignored** for several **server-side** parse paths (notably **async insert over TCP** and **inserts over HTTP**), as described in [issue #100614](https://github.com/ClickHouse/ClickHouse/issues/100614). |
| **From** the first release that contains that fix (e.g. **26.2.4+** on 26.2 after backport) | Plain `DateTime`: effective tz resolved via `DateLUT::instance()` in serialization setup so **`session_timezone` is honored** for those paths. |

Older **26.1** branches did not ship this regression/fix pair; treat the table above as
“**buggy era vs fixed era**” on a given release line, not a strict semver inequality on
`26.1` alone.

---

## See Also

- [`session_timezone` setting](https://clickhouse.com/docs/operations/settings/settings#session_timezone)
- [`DateTime` data type](https://clickhouse.com/docs/sql-reference/data-types/datetime)
- [`DateTime64` data type](https://clickhouse.com/docs/sql-reference/data-types/datetime64)
- [`date_time_input_format` setting](https://clickhouse.com/docs/operations/settings/settings-formats#date_time_input_format)
- [ClickHouse issue #100614](https://github.com/ClickHouse/ClickHouse/issues/100614)
- [ClickHouse PR #100647](https://github.com/ClickHouse/ClickHouse/pull/100647)

---

## Appendix — Reproducible `tz_proof` table (recheck)

Use this block when you want to **verify** behavior on your own server. Comments below
assume you know `SELECT serverTimeZone(), timeZone();` output.

### Schema and fixed row

All three `DateTime*` columns store the **same Unix timestamp** `946706400`
(`2000-01-01 06:00:00` UTC). Only type metadata (and thus parsing/display rules) differ.

```sql
CREATE TABLE tz_proof
(
    id UInt8,
    d_server DateTime,                     -- effective tz: server (and session when wired, post-#100647)
    d_utc    DateTime('UTC'),              -- explicit UTC
    d_berlin DateTime('Europe/Berlin')     -- explicit Europe/Berlin
)
ENGINE = Memory;

INSERT INTO tz_proof VALUES
(
    1,
    946706400,
    946706400,
    946706400
);
```

### Query A — plain `DateTime` vs string literal

```sql
SELECT count() AS matched
FROM tz_proof
WHERE d_server = '2000-01-01 06:00:00';
```

- If **server timezone is `UTC`**: the literal is `06:00` UTC → matches `946706400` → **`matched = 1`**.
- If **server is `Europe/Berlin`**: `06:00` Berlin ≠ that UTC instant → **`matched = 0`**  
  (use `'2000-01-01 07:00:00'` on the literal for CET in early 2000, or compare with
  `toDateTime(..., 'UTC')`).

### Query B — explicit Berlin column vs `toDateTime` one-arg

```sql
SELECT count() AS matched
FROM tz_proof
WHERE d_berlin = toDateTime('2000-01-01 07:00:00');
```

- **`toDateTime` uses the server timezone**, not `Europe/Berlin`, when the second
  argument is omitted.
- So **`matched = 1` only if** the server timezone is **`Europe/Berlin`** (then
  `07:00` local = `946706400`).
- If the server is **`UTC`**, the RHS is `07:00` UTC → different instant → **`matched = 0`**.

Unambiguous alternatives:

```sql
-- Same instant, explicit zones on both sides
SELECT count() FROM tz_proof
WHERE d_berlin = toDateTime('2000-01-01 07:00:00', 'Europe/Berlin');

SELECT count() FROM tz_proof
WHERE d_berlin = toDateTime('2000-01-01 06:00:00', 'UTC');
```

### Quick display check

```sql
SELECT
    id,
    d_server,
    d_utc,
    d_berlin,
    serverTimeZone() AS srv,
    timeZone() AS eff
FROM tz_proof;
```

Re-run the `SELECT` with and without `SETTINGS session_timezone = '…'`. You should see
**plain `d_server`** formatting (and literal matches for Case C) track the session on
fixed builds, while **`d_utc` / `d_berlin`** keep **UTC** / **Berlin** wall-clock labels
for display; `timeZone()` still reports the session.

### Query C — `session_timezone` affects **plain** `d_server` (post-#100647 builds)

Assume **server UTC** and `946706400` stored in `d_server`. Novosibirsk is UTC+6 in
2000, so the same instant prints as **`2000-01-01 12:00:00`** in `Asia/Novosibirsk`.

```sql
SELECT d_server, timeZone() FROM tz_proof
SETTINGS session_timezone = 'Asia/Novosibirsk';
-- d_server shown in Novosibirsk; timeZone() = Asia/Novosibirsk

-- Literal is parsed in session tz: 12:00 Novosibirsk = 946706400 → match
SELECT count() FROM tz_proof
WHERE d_server = '2000-01-01 12:00:00'
SETTINGS session_timezone = 'Asia/Novosibirsk';
```

`d_utc` / `d_berlin` **string** comparisons still use **UTC** / **Berlin** for the literal;
only their **text formatting** in `SELECT` stays column-bound. Check with:

```sql
SELECT d_utc, d_berlin, timeZone()
FROM tz_proof
SETTINGS session_timezone = 'Asia/Novosibirsk';
```

### Query D — explicit `UTC` column vs one-arg `toDateTime` under `session_timezone`

```sql
SELECT count() AS matched
FROM tz_proof
WHERE d_utc = toDateTime('2000-01-01 06:00:00')
SETTINGS session_timezone = 'Asia/Novosibirsk';
```

- **`d_utc = '2000-01-01 06:00:00'`** with session set: literal still **UTC** → can match.
- **`toDateTime('2000-01-01 06:00:00')`** with session set: RHS is **06:00 Novosibirsk**
  → different instant → **`matched = 0`** (illustrates **Case 4**).

Fix:

```sql
SELECT count() FROM tz_proof
WHERE d_utc = toDateTime('2000-01-01 06:00:00', 'UTC');
```

### Query E — `INSERT` string into each column (optional)

After `DROP TABLE IF EXISTS tz_proof` and recreating empty `tz_proof`, try (with
**server `UTC`** so the first two fields line up cleanly):

```sql
INSERT INTO tz_proof VALUES
(2, '2000-01-01 06:00:00', '2000-01-01 06:00:00', '2000-01-01 07:00:00');
-- Row 2: all three store Unix 946706400 — 06:00 UTC, 06:00 UTC, 07:00 Berlin (CET) for the same instant.
```

Re-run `SELECT id, d_server, d_utc, d_berlin FROM tz_proof WHERE id = 2` with different
`SETTINGS session_timezone = '…'`: on **post-#100647** builds the **plain `d_server`** string formatting
in `SELECT` follows the session (stored seconds unchanged); `d_utc` / `d_berlin` outputs
stay in **UTC** / **Europe/Berlin** for those columns.
