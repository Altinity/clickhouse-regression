# Understanding DateTime and Timezones in ClickHouse

Working with `DateTime` in ClickHouse looks straightforward until the same query starts returning different results on a different server, a different session, or even a different shard of the same cluster. The value did not change. The timezone that ClickHouse used to read or print it did. Among the main things that affect this behavior are whether the column carries an explicit timezone, whether the query uses a bare string literal or a `toDateTime` call, whether `session_timezone` is set, and what the server timezone happens to be. There are more knobs than these, but those four are the ones that catch people off guard most often.

The single idea that makes everything else click is also the easiest one to forget: a `DateTime` column stores a Unix timestamp, not a timezone. Timezones come into play only when ClickHouse parses a string into that timestamp, or formats that timestamp back into text. This article walks through what that means in practice, with reproducible queries you can paste into any ClickHouse instance.

## DateTime Stores an Instant, Not a Timezone

Internally, a `DateTime` value is just the number of seconds since `1970-01-01 00:00:00 UTC`. The stored integer carries no timezone label at all. The Unix timestamp `1705320000`, for example, refers to the instant `2024-01-15 12:00:00 UTC`. That same instant is `13:00` in Berlin, `07:00` in New York, and `21:00` in Tokyo. The value on disk does not change between those views, only the wall-clock representation does.

ClickHouse exposes that distinction through the column type. You can declare `DateTime`, `DateTime('UTC')`, `DateTime('Europe/Berlin')`, and so on. They all store Unix seconds, but they differ in which timezone is used when ClickHouse turns a string into a timestamp on insert, or turns a timestamp back into a string on select. A plain `DateTime` column falls back to the server timezone (or the session timezone, when `session_timezone` is set), while a `DateTime('UTC')` column always treats strings as UTC and always prints in UTC. The qualifier does not change how the data is stored, only how it is interpreted at the boundary between strings and integers.

## DateTime64 Follows the Same Rules

Everything below applies equally to `DateTime64`. The only difference is that `DateTime64` keeps fractional seconds, so the underlying value is a 64-bit decimal rather than a 32-bit integer. The type still accepts an optional timezone — `DateTime64(3)`, `DateTime64(3, 'UTC')`, `DateTime64(3, 'Europe/Berlin')` — and the rules for parsing strings, displaying values, and reacting to `session_timezone` are identical. When the examples below show `toDateTime('2024-01-15 12:00:00', 'UTC')`, the equivalent for sub-second precision is `toDateTime64('2024-01-15 12:00:00.123', 3, 'UTC')`. Whatever you learn about `DateTime` carries straight over.

## A Demo Table to Work Against

All examples in this article were run against ClickHouse 26.5. The behavior described here is stable across recent versions, but the exact output formatting and a few edge cases around `session_timezone` have evolved over time, so if you are on an older build you may see small differences.

The rest of the article assumes the server is running in UTC. You can confirm that with `SELECT serverTimeZone(), timeZone();`, which on a clean install returns `UTC` for both. From there, create a table that stores the same instant four different ways:

```sql
DROP TABLE IF EXISTS datetime_tz_demo;

CREATE TABLE datetime_tz_demo
(
    id         UInt8,
    event_name String,
    dt_plain   DateTime,
    dt_utc     DateTime('UTC'),
    dt_berlin  DateTime('Europe/Berlin'),
    dt_ny      DateTime('America/New_York')
)
ENGINE = Memory;

INSERT INTO datetime_tz_demo
SELECT
    1,
    'Product launch',
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC');
```

A simple `SELECT event_name, dt_plain, dt_utc, dt_berlin, dt_ny FROM datetime_tz_demo` then prints:

```
┌─event_name─────┬────────────dt_plain─┬──────────────dt_utc─┬───────────dt_berlin─┬───────────────dt_ny─┐
│ Product launch │ 2024-01-15 12:00:00 │ 2024-01-15 12:00:00 │ 2024-01-15 13:00:00 │ 2024-01-15 07:00:00 │
└────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘
```

All four columns hold exactly the same Unix timestamp. They are displayed differently because each column carries its own rule for how to format that timestamp back into a string.

## The Trap: Bare Literals and toDateTime Are Not the Same

The single most common surprise in ClickHouse timezone handling lives in the difference between these two filters:

```sql
WHERE dt_berlin = '2024-01-15 13:00:00'
WHERE dt_berlin = toDateTime('2024-01-15 13:00:00')
```

They look interchangeable, and they are not. A bare string literal compared against a `DateTime` column is parsed in the **column's** timezone — Berlin in this case. A one-argument `toDateTime('...')` call is parsed in the **server or session** timezone instead, and ignores whatever timezone the column was declared with. With the server in UTC, the first line is read as `13:00 Berlin` (which equals `12:00 UTC` — the instant we stored) and the second is read as `13:00 UTC`, an hour later. One matches the row, the other does not.

The following query makes that visible against the demo table by running both forms side by side, and adds the two explicit-timezone variants for comparison:

```sql
SELECT
    countIf(dt_berlin = '2024-01-15 13:00:00')                              AS literal_berlin_match,
    countIf(dt_berlin = toDateTime('2024-01-15 13:00:00'))                  AS to_datetime_one_arg,
    countIf(dt_berlin = toDateTime('2024-01-15 13:00:00', 'Europe/Berlin')) AS to_datetime_explicit_berlin,
    countIf(dt_berlin = toDateTime('2024-01-15 12:00:00', 'UTC'))           AS to_datetime_explicit_utc
FROM datetime_tz_demo;
```

```
┌─literal_berlin_match─┬─to_datetime_one_arg─┬─to_datetime_explicit_berlin─┬─to_datetime_explicit_utc─┐
│                    1 │                   0 │                           1 │                        1 │
└──────────────────────┴─────────────────────┴─────────────────────────────┴──────────────────────────┘
```

Three of the four expressions match the stored row, and one does not. The bare literal `'2024-01-15 13:00:00'` matched because it was parsed in Berlin time, the column's own timezone. The one-argument `toDateTime('2024-01-15 13:00:00')` did not match, because the server timezone is UTC and ClickHouse therefore parsed the string as `2024-01-15 13:00:00 UTC` — an instant one hour later than the row we stored. Passing the timezone explicitly, either as `Europe/Berlin` or as the equivalent UTC time, restores the match. The two SQL expressions that disagree differ only in whether `toDateTime` is wrapped around the string, and yet they hit different rows.

## What session_timezone Actually Changes

`session_timezone` adjusts the effective timezone for the current session without touching the server timezone. Anywhere ClickHouse would have consulted the server timezone — when displaying or parsing a plain `DateTime` column, and when evaluating a one-argument `toDateTime('...')` call — it now consults the session timezone instead. That second part is the easy one to miss: the same `toDateTime('2024-01-15 12:00:00')` that meant `12:00 UTC` on a UTC server starts meaning `12:00 Tokyo` the moment the session is switched to Tokyo, even though nothing in the SQL changed. You can see the split with:

```sql
SELECT timeZone(), serverTimeZone()
SETTINGS session_timezone = 'Asia/Tokyo';
```

```
┌─timeZone()─┬─serverTimeZone()─┐
│ Asia/Tokyo │ UTC              │
└────────────┴──────────────────┘
```

The setting reaches the places where a plain `DateTime` (or a one-argument `toDateTime`) would otherwise consult the server timezone. It does not reach into columns that already declare their own timezone. Selecting the demo row under Tokyo makes that very concrete:

```sql
SELECT event_name, dt_plain, dt_utc, dt_berlin, dt_ny, timeZone() AS effective_timezone
FROM datetime_tz_demo
SETTINGS session_timezone = 'Asia/Tokyo';
```

```
┌─event_name─────┬────────────dt_plain─┬──────────────dt_utc─┬───────────dt_berlin─┬───────────────dt_ny─┬─effective_timezone─┐
│ Product launch │ 2024-01-15 21:00:00 │ 2024-01-15 12:00:00 │ 2024-01-15 13:00:00 │ 2024-01-15 07:00:00 │ Asia/Tokyo         │
└────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴────────────────────┘
```

Only `dt_plain` shifted. The three explicit-timezone columns kept printing in their own timezones, regardless of what `timeZone()` reports for the session. It is worth stating this out loud, because `timeZone()` is often misread as "the timezone in which all DateTime values are displayed", when in fact it only describes the fallback timezone for columns and expressions that do not carry one of their own.

The asymmetry between bare literals and `toDateTime` becomes sharper under a non-UTC session. The stored event is still `2024-01-15 12:00:00 UTC`, which is `2024-01-15 21:00:00` in Tokyo. With `session_timezone = 'Asia/Tokyo'`:

```sql
SELECT
    countIf(dt_plain = '2024-01-15 21:00:00')                    AS plain_tokyo_literal,
    countIf(dt_plain = '2024-01-15 12:00:00')                    AS plain_utc_literal,
    countIf(dt_utc   = '2024-01-15 12:00:00')                    AS utc_literal,
    countIf(dt_utc   = toDateTime('2024-01-15 12:00:00'))        AS utc_to_datetime_one_arg,
    countIf(dt_utc   = toDateTime('2024-01-15 12:00:00', 'UTC')) AS utc_to_datetime_explicit
FROM datetime_tz_demo
SETTINGS session_timezone = 'Asia/Tokyo';
```

```
┌─plain_tokyo_literal─┬─plain_utc_literal─┬─utc_literal─┬─utc_to_datetime_one_arg─┬─utc_to_datetime_explicit─┐
│                   1 │                 0 │           1 │                       0 │                        1 │
└─────────────────────┴───────────────────┴─────────────┴─────────────────────────┴──────────────────────────┘
```

For `dt_plain`, the Tokyo string matches and the UTC-looking string does not, because under Tokyo session the plain column treats every bare literal as Tokyo time. For `dt_utc`, the bare literal still matches `12:00` because the column's own UTC timezone wins over the session — but `toDateTime('2024-01-15 12:00:00')` no longer matches the same row, because that call is now parsed as `12:00 Tokyo`, which is `03:00 UTC`. Two expressions that look semantically identical return different results.

## INSERT Has Its Own Rules

Most of the parsing rules above carry over from `WHERE` to `INSERT`, but not all of them. The one place they diverge is the very place that matters most — the plain `DateTime` column under a non-default `session_timezone`. We will get to that asymmetry in a moment. The straightforward cases first:

```sql
INSERT INTO datetime_tz_demo VALUES
(2, 'Morning sync',
 '2024-01-15 12:00:00',
 '2024-01-15 12:00:00',
 '2024-01-15 13:00:00',
 '2024-01-15 07:00:00');
```

Every column stores the same instant, `2024-01-15 12:00:00 UTC`, but only because the server timezone happens to be UTC and the bare literal on `dt_plain` is read in the server timezone. Each of the three explicit-TZ columns parses its own literal in its own timezone, which is why the input strings have to be different to land on the same instant. A version that does not depend on the server timezone at all looks like this:

```sql
INSERT INTO datetime_tz_demo
SELECT
    3,
    'Stable insert',
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC');
```

Reading either of those two rows back confirms that all four columns hold the same Unix timestamp:

```
┌─id─┬─event_name─────┬────────────dt_plain─┬──────────────dt_utc─┬───────────dt_berlin─┬───────────────dt_ny─┐
│  1 │ Product launch │ 2024-01-15 12:00:00 │ 2024-01-15 12:00:00 │ 2024-01-15 13:00:00 │ 2024-01-15 07:00:00 │
│  2 │ Morning sync   │ 2024-01-15 12:00:00 │ 2024-01-15 12:00:00 │ 2024-01-15 13:00:00 │ 2024-01-15 07:00:00 │
│  3 │ Stable insert  │ 2024-01-15 12:00:00 │ 2024-01-15 12:00:00 │ 2024-01-15 13:00:00 │ 2024-01-15 07:00:00 │
└────┴────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘
```

Now the interesting case. Repeat the mixed insert under `session_timezone = 'Asia/Tokyo'`, where the four columns are fed the same `'2024-01-15 12:00:00'` string through four different syntactic forms:

```sql
TRUNCATE TABLE datetime_tz_demo;

INSERT INTO datetime_tz_demo
SELECT
    10,
    'Bare literal into plain',
    '2024-01-15 12:00:00',                       -- dt_plain  (bare literal)
    '2024-01-15 12:00:00',                       -- dt_utc    (bare literal)
    toDateTime('2024-01-15 12:00:00'),           -- dt_berlin (one-arg toDateTime)
    toDateTime('2024-01-15 12:00:00', 'UTC')     -- dt_ny     (explicit UTC)
SETTINGS session_timezone = 'Asia/Tokyo';

SELECT id, dt_plain, dt_utc, dt_berlin, dt_ny
FROM datetime_tz_demo
WHERE id = 10
SETTINGS session_timezone = 'UTC';
```

```
┌─id─┬────────────dt_plain─┬──────────────dt_utc─┬───────────dt_berlin─┬───────────────dt_ny─┐
│ 10 │ 2024-01-15 12:00:00 │ 2024-01-15 12:00:00 │ 2024-01-15 04:00:00 │ 2024-01-15 07:00:00 │
└────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘
```

The trailing `SETTINGS session_timezone = 'UTC'` only changes the display of `dt_plain` — explicit-TZ columns ignore the session and always print in their own timezone — so the four values shown are not directly comparable until you translate each back through its column's timezone. Doing that gives the actually stored Unix instants: `dt_plain → 12:00 UTC`, `dt_utc → 12:00 UTC`, `dt_berlin → 04:00 Berlin == 03:00 UTC`, `dt_ny → 07:00 New York == 12:00 UTC`.

Three behaviors fall out of that. `dt_utc` and `dt_ny` are unsurprising: the bare literal hits the column's own timezone, and the explicit `'UTC'` argument hits exactly what it says. `dt_berlin` is the trap from the `WHERE` section showing up again — the one-argument `toDateTime('...')` ignored the column's Berlin timezone and parsed the string in the session timezone (`12:00 Tokyo == 03:00 UTC`), so the column now holds an instant nobody asked for. The new wrinkle is `dt_plain`: its bare literal `'2024-01-15 12:00:00'` did **not** follow `session_timezone = 'Asia/Tokyo'`. It was parsed in the **server** timezone (UTC) and stored as `12:00 UTC`. If the session had won, the value would have been `03:00 UTC`, and it is not.

That makes `INSERT` quietly asymmetric with `WHERE` for plain `DateTime`. On the read side, a bare literal compared against `dt_plain` does honor `session_timezone` — the `plain_tokyo_literal = 1, plain_utc_literal = 0` result earlier in this article confirms it. On the write side, the same syntactic construct ignores `session_timezone` and falls back to the server timezone instead. A one-argument `toDateTime('...')`, by contrast, follows `session_timezone` consistently in both contexts, which is exactly what makes the `dt_berlin` row in this experiment go wrong.

The conclusion is the same in both directions: the safest pattern for `INSERT` is the same as for filters. Pass the timezone explicitly and the result no longer depends on the server, the session, or which side of an `=` you are standing on.

```sql
INSERT INTO datetime_tz_demo
SELECT
    11,
    'Always safe',
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC')
SETTINGS session_timezone = 'Asia/Tokyo';
```

## DST Is Not Hypothetical

Once timezones with daylight saving time enter the picture, the same kind of mismatch shows up in places that have nothing to do with `session_timezone`. Some local wall-clock times do not exist at all, and others occur twice. Both situations can be reproduced in ClickHouse.

In `Europe/Berlin`, on `2024-03-31` the clocks jump from `02:00 CET` directly to `03:00 CEST`. The local time `02:30` does not exist. ClickHouse will still accept the string, but the gap is visible if you bracket it on either side and compare the underlying Unix timestamps:

```sql
SELECT
    toDateTime('2024-03-31 01:30:00', 'Europe/Berlin') AS before_jump,
    toDateTime('2024-03-31 03:30:00', 'Europe/Berlin') AS after_jump,
    toUnixTimestamp(toDateTime('2024-03-31 03:30:00', 'Europe/Berlin'))
  - toUnixTimestamp(toDateTime('2024-03-31 01:30:00', 'Europe/Berlin')) AS seconds_between;
```

```
┌─────────before_jump─┬──────────after_jump─┬─seconds_between─┐
│ 2024-03-31 01:30:00 │ 2024-03-31 03:30:00 │            3600 │
└─────────────────────┴─────────────────────┴─────────────────┘
```

Two wall-clock readings two hours apart in appearance, but only one hour apart on the timeline. The missing hour is the DST jump.

The autumn transition is the opposite problem. On `2024-10-27`, `Europe/Berlin` falls back from `03:00 CEST` to `02:00 CET`, and the wall-clock time `02:30` happens twice — first at `00:30 UTC` and again at `01:30 UTC`. Two distinct instants share one local string:

```sql
SELECT
    toDateTime('2024-10-27 00:30:00', 'UTC') ::DateTime('Europe/Berlin') AS first_0230_local,
    toDateTime('2024-10-27 01:30:00', 'UTC') ::DateTime('Europe/Berlin') AS second_0230_local,
    toUnixTimestamp(toDateTime('2024-10-27 01:30:00', 'UTC'))
  - toUnixTimestamp(toDateTime('2024-10-27 00:30:00', 'UTC')) AS seconds_between;
```

```
┌────first_0230_local─┬───second_0230_local─┬─seconds_between─┐
│ 2024-10-27 02:30:00 │ 2024-10-27 02:30:00 │            3600 │
└─────────────────────┴─────────────────────┴─────────────────┘
```

Both instants print as `2024-10-27 02:30:00` in Berlin, yet they are an hour apart. A bare literal `'2024-10-27 02:30:00'` against `DateTime('Europe/Berlin')` can only resolve to one of them, and which one depends on the timezone database and on the rules ClickHouse uses to break ambiguity. This is the deepest reason to store event timestamps in UTC and only convert at the presentation layer — UTC has no DST, no gaps, and no repeats.

## Which Timezone Parses the String

Boiling everything down to one table, this is which timezone ClickHouse actually uses to turn a string into a Unix timestamp. Rows are the expression and the situation it appears in; columns are the target column type the expression is being matched against or written into. Each cell tells you which timezone is used to parse the string in that combination.

| Expression \ Column type                          | `DateTime`                | `DateTime('UTC')`  | `DateTime('Europe/Berlin')` |
| ------------------------------------------------- | ------------------------- | ------------------ | --------------------------- |
| Bare string in `WHERE`, no `session_timezone`     | Server timezone           | `UTC`              | `Europe/Berlin`             |
| Bare string in `WHERE`, with `session_timezone`   | **Session** timezone      | `UTC`              | `Europe/Berlin`             |
| Bare string in `INSERT`, no `session_timezone`    | Server timezone           | `UTC`              | `Europe/Berlin`             |
| Bare string in `INSERT`, with `session_timezone`  | **Server** timezone       | `UTC`              | `Europe/Berlin`             |
| `toDateTime('...')`, no `session_timezone`        | Server timezone           | Server timezone    | Server timezone             |
| `toDateTime('...')`, with `session_timezone`      | Session timezone          | Session timezone   | Session timezone            |
| `toDateTime('...', 'TZ')`                         | Explicit TZ               | Explicit TZ        | Explicit TZ                 |

Two rows are worth staring at. The plain `DateTime` column under `session_timezone` resolves bare literals differently in `WHERE` (session) and in `INSERT` (server) — that asymmetry is the one this article keeps coming back to. And the only row in the entire table that does not depend on context is the last one. Everything above it can shift under your feet when the server is reconfigured, the session changes, or a shard with a different timezone enters the picture. If the string represents a known timezone, pass that timezone explicitly:

```sql
WHERE dt_utc    = toDateTime('2024-01-15 12:00:00', 'UTC')
WHERE dt_berlin = toDateTime('2024-01-15 13:00:00', 'Europe/Berlin')
```

## A Mental Model That Survives Edge Cases

Pulling all of that together, the question that solves almost every timezone bug in ClickHouse is the same one, asked early: *which timezone parses this string?* For a bare literal against a column with an explicit timezone, the answer is the column's timezone, in both `WHERE` and `INSERT`. For a bare literal against a plain `DateTime`, the answer depends on which side of the query you are on — `WHERE` follows the session timezone (and falls back to the server's), while `INSERT` follows the server timezone and ignores `session_timezone` entirely. For a one-argument `toDateTime` (or `toDateTime64`), the answer is always the session or server timezone, regardless of the column and regardless of context. For an explicit two-argument call, the answer is the timezone you passed. Only the last form has no hidden dependency.

The practical guidance follows from that directly. Use explicit-timezone columns for anything that matters — `DateTime('UTC')` and `DateTime64(3, 'UTC')` are the conservative defaults for event timestamps, audit logs, `created_at`, and `updated_at`. Avoid one-argument `toDateTime` in filters and inserts; pass the timezone every time. Do not assume a bare string literal and a `toDateTime` call behave the same — they often do not. In tests, set `session_timezone` explicitly, or, better, write the timezone into every `toDateTime` so the test stops depending on the host machine's clock at all. In distributed queries, that discipline matters even more, because different shards can be configured with different server timezones, and a one-argument `toDateTime` is the easiest way to silently get inconsistent results across nodes.

When a query "returns no rows" and you cannot see why, the first thing to check is rarely the data. It is `serverTimeZone()`, `timeZone()`, and whether the literal in the `WHERE` clause was ever in the timezone you assumed. Once that becomes a reflex, ClickHouse's timezone handling stops feeling like a series of traps and starts feeling like what it actually is: a small set of consistent rules applied at the boundary between strings and Unix seconds.
