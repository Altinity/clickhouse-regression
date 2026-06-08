# DateTime and Timezones in ClickHouse

Working with `DateTime` in ClickHouse can be confusing because the same value may be interpreted differently depending on:

- whether the column has an explicit timezone,
- whether the query uses a bare string literal or `toDateTime`,
- whether `session_timezone` is set,
- and what timezone the server uses.

The most important idea is this:

> `DateTime` stores a Unix timestamp.
> Timezones are used only when ClickHouse **parses** a string into that timestamp, or **formats** that timestamp back into text.

This article explains the tricky parts step by step, with one reproducible example.

---

## 1. The core idea: DateTime stores an instant, not a timezone

A `DateTime` value is stored internally as Unix seconds — the number of seconds since:

```
1970-01-01 00:00:00 UTC
```

The stored integer does **not** contain a timezone label.

For example, the Unix timestamp `1705320000` means:

```
2024-01-15 12:00:00 UTC
```

But the same instant is displayed differently in different timezones:

| Timezone           | Displayed value       |
| ------------------ | --------------------- |
| `UTC`              | `2024-01-15 12:00:00` |
| `Europe/Berlin`    | `2024-01-15 13:00:00` |
| `America/New_York` | `2024-01-15 07:00:00` |
| `Asia/Tokyo`       | `2024-01-15 21:00:00` |

The value is the same instant. Only the wall-clock representation changes.

---

## 2. Column timezone: plain DateTime vs DateTime('TZ')

ClickHouse supports both plain `DateTime` and `DateTime` with an explicit timezone:

```sql
DateTime
DateTime('UTC')
DateTime('Europe/Berlin')
```

They all store Unix seconds, but they use different rules for parsing and display.

| Column type               | Timezone in metadata? | Timezone used for strings and display                                       |
| ------------------------- | --------------------- | --------------------------------------------------------------------------- |
| `DateTime`                | No                    | Server timezone, or session timezone when `session_timezone` is set         |
| `DateTime('UTC')`         | Yes                   | `UTC`                                                                       |
| `DateTime('Europe/Berlin')` | Yes                 | `Europe/Berlin`                                                             |

So `DateTime('UTC')` does **not** store a different physical format. It still stores Unix seconds. The timezone only tells ClickHouse how to interpret strings and how to print the value.

---

## 3. Example table

The examples below assume the server timezone is `UTC`. You can check it with:

```sql
SELECT serverTimeZone(), timeZone();
```

Expected result:

```
┌─serverTimeZone()─┬─timeZone()─┐
│ UTC              │ UTC        │
└──────────────────┴────────────┘
```

Now create a demo table:

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
```

Insert one meaningful event. The event happened at `2024-01-15 12:00:00 UTC`. At that same instant:

| Timezone           | Local time            |
| ------------------ | --------------------- |
| `UTC`              | `2024-01-15 12:00:00` |
| `Europe/Berlin`    | `2024-01-15 13:00:00` |
| `America/New_York` | `2024-01-15 07:00:00` |
| `Asia/Tokyo`       | `2024-01-15 21:00:00` |

Insert the same instant into all columns:

```sql
INSERT INTO datetime_tz_demo
SELECT
    1,
    'Product launch',
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC'),
    toDateTime('2024-01-15 12:00:00', 'UTC');
```

Now select the data:

```sql
SELECT event_name, dt_plain, dt_utc, dt_berlin, dt_ny
FROM datetime_tz_demo;
```

Expected result when server timezone is `UTC`:

```
┌─event_name─────┬────────────dt_plain─┬──────────────dt_utc─┬───────────dt_berlin─┬───────────────dt_ny─┐
│ Product launch │ 2024-01-15 12:00:00 │ 2024-01-15 12:00:00 │ 2024-01-15 13:00:00 │ 2024-01-15 07:00:00 │
└────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘
```

All four columns store the same instant. They are displayed differently because their timezone rules are different.

---

## 4. The main trap: bare string literals and toDateTime() are not the same

This is the most important part. These two filters look similar:

```sql
WHERE dt_utc = '2024-01-15 12:00:00'
WHERE dt_utc = toDateTime('2024-01-15 12:00:00')
```

But they are **not** equivalent:

- A **bare string literal** compared to a `DateTime` column is interpreted using the **column timezone**.
- A **one-argument `toDateTime('...')`** is interpreted using the **server/session timezone**, not the column timezone.

---

## 5. Bare string literal in WHERE

A bare string literal uses the timezone of the column being compared.

```sql
SELECT
    countIf(dt_plain  = '2024-01-15 12:00:00') AS plain_match,
    countIf(dt_utc    = '2024-01-15 12:00:00') AS utc_match,
    countIf(dt_berlin = '2024-01-15 13:00:00') AS berlin_match,
    countIf(dt_ny     = '2024-01-15 07:00:00') AS ny_match,
    countIf(dt_berlin = '2024-01-15 12:00:00') AS berlin_wrong_wall_clock
FROM datetime_tz_demo;
```

Expected result:

```
┌─plain_match─┬─utc_match─┬─berlin_match─┬─ny_match─┬─berlin_wrong_wall_clock─┐
│           1 │         1 │            1 │        1 │                       0 │
└─────────────┴───────────┴──────────────┴──────────┴─────────────────────────┘
```

The stored instant is `2024-01-15 12:00:00 UTC`. For each column, the matching wall-clock string is different:

| Column                                  | Matching string                                       |
| --------------------------------------- | ----------------------------------------------------- |
| `dt_plain` `DateTime`                   | `2024-01-15 12:00:00` (server timezone is `UTC`)      |
| `dt_utc` `DateTime('UTC')`              | `2024-01-15 12:00:00`                                 |
| `dt_berlin` `DateTime('Europe/Berlin')` | `2024-01-15 13:00:00`                                 |
| `dt_ny` `DateTime('America/New_York')`  | `2024-01-15 07:00:00`                                 |

So this matches:

```sql
WHERE dt_berlin = '2024-01-15 13:00:00'
```

But this does not, because 12:00 in Berlin is a different instant from 12:00 UTC:

```sql
WHERE dt_berlin = '2024-01-15 12:00:00'
```

---

## 6. One-argument toDateTime('...')

Now compare with `toDateTime`:

```sql
SELECT
    countIf(dt_berlin = '2024-01-15 13:00:00')                                AS literal_berlin_match,
    countIf(dt_berlin = toDateTime('2024-01-15 13:00:00'))                    AS to_datetime_one_arg,
    countIf(dt_berlin = toDateTime('2024-01-15 13:00:00', 'Europe/Berlin'))   AS to_datetime_explicit_berlin,
    countIf(dt_berlin = toDateTime('2024-01-15 12:00:00', 'UTC'))             AS to_datetime_explicit_utc
FROM datetime_tz_demo;
```

Expected result when server timezone is `UTC`:

```
┌─literal_berlin_match─┬─to_datetime_one_arg─┬─to_datetime_explicit_berlin─┬─to_datetime_explicit_utc─┐
│                    1 │                   0 │                           1 │                        1 │
└──────────────────────┴─────────────────────┴─────────────────────────────┴──────────────────────────┘
```

Why?

- `dt_berlin = '2024-01-15 13:00:00'` parses the string as **Berlin** time, so it means `2024-01-15 12:00:00 UTC`. Matches.
- `dt_berlin = toDateTime('2024-01-15 13:00:00')` does **not** use the Berlin timezone. Because the server timezone is `UTC`, it means `2024-01-15 13:00:00 UTC` — one hour later than the stored event. Does not match.

The safe versions are:

```sql
toDateTime('2024-01-15 13:00:00', 'Europe/Berlin')
toDateTime('2024-01-15 12:00:00', 'UTC')
```

Both describe the same instant explicitly.

---

## 7. What changes when session_timezone is set

`session_timezone` changes the effective timezone for the session.

```sql
SELECT timeZone(), serverTimeZone()
SETTINGS session_timezone = 'Asia/Tokyo';
```

Expected result:

```
┌─timeZone()─┬─serverTimeZone()─┐
│ Asia/Tokyo │ UTC              │
└────────────┴──────────────────┘
```

The server timezone is still `UTC`, but the effective session timezone is now `Asia/Tokyo`.

---

## 8. Display with session_timezone

```sql
SELECT
    event_name,
    dt_plain,
    dt_utc,
    dt_berlin,
    dt_ny,
    timeZone() AS effective_timezone
FROM datetime_tz_demo
SETTINGS session_timezone = 'Asia/Tokyo';
```

Expected result on builds where `session_timezone` is respected for plain `DateTime` display:

```
┌─event_name─────┬────────────dt_plain─┬──────────────dt_utc─┬───────────dt_berlin─┬───────────────dt_ny─┬─effective_timezone─┐
│ Product launch │ 2024-01-15 21:00:00 │ 2024-01-15 12:00:00 │ 2024-01-15 13:00:00 │ 2024-01-15 07:00:00 │ Asia/Tokyo         │
└────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴────────────────────┘
```

Only the plain `DateTime` column changed display from `UTC` to Tokyo. The explicit timezone columns did not change:

| Column                                  | Display timezone            |
| --------------------------------------- | --------------------------- |
| `dt_plain` `DateTime`                   | Session timezone: `Asia/Tokyo` |
| `dt_utc` `DateTime('UTC')`              | `UTC`                       |
| `dt_berlin` `DateTime('Europe/Berlin')` | `Europe/Berlin`             |
| `dt_ny` `DateTime('America/New_York')`  | `America/New_York`          |

> **Important:** `timeZone` returns the effective session timezone. It does **not** mean every `DateTime('TZ')` column is displayed in that timezone.

---

## 9. WHERE with session_timezone

The stored event is still `2024-01-15 12:00:00 UTC`. In Tokyo, that same instant is `2024-01-15 21:00:00 Asia/Tokyo`.

```sql
SELECT
    countIf(dt_plain = '2024-01-15 21:00:00')                       AS plain_tokyo_literal,
    countIf(dt_plain = '2024-01-15 12:00:00')                       AS plain_utc_literal,
    countIf(dt_utc   = '2024-01-15 12:00:00')                       AS utc_literal,
    countIf(dt_utc   = toDateTime('2024-01-15 12:00:00'))           AS utc_to_datetime_one_arg,
    countIf(dt_utc   = toDateTime('2024-01-15 12:00:00', 'UTC'))    AS utc_to_datetime_explicit
FROM datetime_tz_demo
SETTINGS session_timezone = 'Asia/Tokyo';
```

Expected result:

```
┌─plain_tokyo_literal─┬─plain_utc_literal─┬─utc_literal─┬─utc_to_datetime_one_arg─┬─utc_to_datetime_explicit─┐
│                   1 │                 0 │           1 │                       0 │                        1 │
└─────────────────────┴───────────────────┴─────────────┴─────────────────────────┴──────────────────────────┘
```

### Plain DateTime

- `dt_plain = '2024-01-15 21:00:00'` — with `session_timezone = 'Asia/Tokyo'`, the string is parsed as Tokyo time, which equals `2024-01-15 12:00:00 UTC`. Matches.
- `dt_plain = '2024-01-15 12:00:00'` — parsed as `2024-01-15 12:00:00 Asia/Tokyo` = `2024-01-15 03:00:00 UTC`. Does not match.

### Explicit `DateTime('UTC')`

- `dt_utc = '2024-01-15 12:00:00'` still parses the string as `UTC`, because the column has an explicit timezone. Matches.
- `dt_utc = toDateTime('2024-01-15 12:00:00')` uses the session timezone. With `session_timezone = 'Asia/Tokyo'`, it means `2024-01-15 12:00:00 Asia/Tokyo` = `2024-01-15 03:00:00 UTC`. Does not match.

This is the key asymmetry — the following two expressions can return different results:

```sql
dt_utc = '2024-01-15 12:00:00'
dt_utc = toDateTime('2024-01-15 12:00:00')
```

---

## 10. Summary: which timezone parses the string?

| Expression                                            | `DateTime`        | `DateTime('UTC')`  | `DateTime('Europe/Berlin')` |
| ----------------------------------------------------- | ----------------- | ------------------ | --------------------------- |
| Bare string in `WHERE`, no `session_timezone`         | Server timezone   | `UTC`              | `Europe/Berlin`             |
| Bare string in `WHERE`, with `session_timezone`       | Session timezone  | `UTC`              | `Europe/Berlin`             |
| `toDateTime('...')`, no `session_timezone`            | Server timezone   | Server timezone    | Server timezone             |
| `toDateTime('...')`, with `session_timezone`          | Session timezone  | Session timezone   | Session timezone            |
| `toDateTime('...', 'TZ')`                             | Explicit TZ       | Explicit TZ        | Explicit TZ                 |

The safest rule:

> If the string represents a known timezone, pass that timezone explicitly.

For example:

```sql
WHERE dt_utc    = toDateTime('2024-01-15 12:00:00', 'UTC')
WHERE dt_berlin = toDateTime('2024-01-15 13:00:00', 'Europe/Berlin')
```

---

## 11. INSERT rules

The same parsing rules apply when inserting strings.

```sql
INSERT INTO datetime_tz_demo VALUES
(
    2,
    'Morning sync',
    '2024-01-15 12:00:00',
    '2024-01-15 12:00:00',
    '2024-01-15 13:00:00',
    '2024-01-15 07:00:00'
);
```

Assuming server timezone is `UTC`, all four datetime values describe the same instant `2024-01-15 12:00:00 UTC`:

| Target column                           | Inserted string         | Parsed as                                |
| --------------------------------------- | ----------------------- | ---------------------------------------- |
| `dt_plain` `DateTime`                   | `2024-01-15 12:00:00`   | 12:00 `UTC` (server timezone is `UTC`)   |
| `dt_utc` `DateTime('UTC')`              | `2024-01-15 12:00:00`   | 12:00 `UTC`                              |
| `dt_berlin` `DateTime('Europe/Berlin')` | `2024-01-15 13:00:00`   | 13:00 Berlin = 12:00 `UTC`               |
| `dt_ny` `DateTime('America/New_York')`  | `2024-01-15 07:00:00`   | 07:00 New York = 12:00 `UTC`             |

Check:

```sql
SELECT id, event_name, dt_plain, dt_utc, dt_berlin, dt_ny
FROM datetime_tz_demo
ORDER BY id;
```

Expected result when server timezone is `UTC`:

```
┌─id─┬─event_name─────┬────────────dt_plain─┬──────────────dt_utc─┬───────────dt_berlin─┬───────────────dt_ny─┐
│  1 │ Product launch │ 2024-01-15 12:00:00 │ 2024-01-15 12:00:00 │ 2024-01-15 13:00:00 │ 2024-01-15 07:00:00 │
│  2 │ Morning sync   │ 2024-01-15 12:00:00 │ 2024-01-15 12:00:00 │ 2024-01-15 13:00:00 │ 2024-01-15 07:00:00 │
└────┴────────────────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘
```

However, this insert depends on the server timezone for `dt_plain`. A more stable insert is:

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

This version is explicit and does not depend on the server timezone.

### INSERT with session_timezone

`INSERT` follows the same parsing rules as `WHERE`. `session_timezone` only affects columns and expressions that do **not** carry an explicit timezone:

| Inserted expression                       | Target `DateTime`                | Target `DateTime('UTC')`           |
| ----------------------------------------- | -------------------------------- | ---------------------------------- |
| Bare string `'2024-01-15 12:00:00'`       | Parsed in **session timezone**   | Parsed in **column timezone (`UTC`)** |
| `toDateTime('2024-01-15 12:00:00')`       | Parsed in **session timezone**   | Parsed in **session timezone**     |
| `toDateTime('2024-01-15 12:00:00', 'UTC')` | Explicit `UTC`                   | Explicit `UTC`                     |

Example — with `session_timezone = 'Asia/Tokyo'`, the same string is stored as different instants depending on how it is written:

```sql
TRUNCATE TABLE datetime_tz_demo;

INSERT INTO datetime_tz_demo
SELECT
    10,
    'Bare literal into plain',
    '2024-01-15 12:00:00',                          -- dt_plain  → parsed as Tokyo time
    '2024-01-15 12:00:00',                          -- dt_utc    → parsed as UTC (column TZ)
    toDateTime('2024-01-15 12:00:00'),              -- dt_berlin → parsed as Tokyo time, NOT Berlin
    toDateTime('2024-01-15 12:00:00', 'UTC')        -- dt_ny     → explicit UTC
SETTINGS session_timezone = 'Asia/Tokyo';

SELECT id, dt_plain, dt_utc, dt_berlin, dt_ny
FROM datetime_tz_demo
WHERE id = 10
SETTINGS session_timezone = 'UTC';
```

Expected result (displayed in `UTC` for clarity):

```
┌─id─┬────────────dt_plain─┬──────────────dt_utc─┬───────────dt_berlin─┬───────────────dt_ny─┐
│ 10 │ 2024-01-15 03:00:00 │ 2024-01-15 12:00:00 │ 2024-01-15 03:00:00 │ 2024-01-15 12:00:00 │
└────┴─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┘
```

Notice:

- `dt_plain` — bare literal parsed as Tokyo → `03:00 UTC`.
- `dt_utc` — bare literal parsed in the column's explicit timezone (`UTC`) → `12:00 UTC`. The session setting was **ignored** for parsing.
- `dt_berlin` — one-argument `toDateTime` ignored the column's `Europe/Berlin` timezone and used the session timezone (Tokyo) → `03:00 UTC`. This is almost certainly a bug in the query.
- `dt_ny` — explicit `'UTC'` argument wins → `12:00 UTC`, regardless of session or column timezone.

The takeaway is the same asymmetry as in `WHERE`:

> For a column with an explicit timezone, a bare string literal uses the **column** timezone, but one-argument `toDateTime` uses the **session/server** timezone. `session_timezone` can silently shift the meaning of `toDateTime('...')` inside an `INSERT`.

The safe pattern for `INSERT` is the same as for filters — always pass the timezone explicitly:

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

This produces the same stored instant regardless of server or session timezone.

---

## 12. Common mistake: comparing explicit timezone columns with one-argument toDateTime()

This is risky:

```sql
WHERE dt_utc = toDateTime('2024-01-15 12:00:00')
```

It only means `UTC` if the effective server/session timezone is `UTC`. If the session timezone is Tokyo, it means `2024-01-15 12:00:00 Asia/Tokyo`, not `2024-01-15 12:00:00 UTC`.

Use this instead:

```sql
WHERE dt_utc = toDateTime('2024-01-15 12:00:00', 'UTC')
```

For a Berlin column:

```sql
WHERE dt_berlin = toDateTime('2024-01-15 13:00:00', 'Europe/Berlin')
```

Or compare by UTC instant — both are correct if they describe the same instant:

```sql
WHERE dt_berlin = toDateTime('2024-01-15 12:00:00', 'UTC')
```

---

## 13. Practical rules

### Rule 1: Prefer explicit timezone columns for important timestamps

For event timestamps, logs, `created_at`, and `updated_at` fields, prefer:

```sql
DateTime('UTC')
DateTime64(3, 'UTC')
```

This makes the intended meaning clear.

### Rule 2: Avoid one-argument toDateTime() in filters

Avoid:

```sql
WHERE created_at = toDateTime('2024-01-15 12:00:00')
```

Prefer:

```sql
WHERE created_at = toDateTime('2024-01-15 12:00:00', 'UTC')
```

or the timezone that matches the meaning of the input string.

### Rule 3: Do not assume a bare string and toDateTime() behave the same

These can be different:

```sql
WHERE dt_utc = '2024-01-15 12:00:00'
WHERE dt_utc = toDateTime('2024-01-15 12:00:00')
```

The first uses the column timezone. The second uses server/session timezone.

### Rule 4: In tests, set session_timezone explicitly

Tests can fail when they run on a machine with a different server timezone. Use:

```sql
SET session_timezone = 'UTC';
```

or pass it per query:

```sql
SELECT ...
SETTINGS session_timezone = 'UTC';
```

Even better, use explicit timezone arguments in `toDateTime`.

### Rule 5: Be extra careful in distributed queries

If different shards have different server timezones, then this can be dangerous:

```sql
toDateTime('2024-01-15 12:00:00')
```

Different nodes may interpret the same string differently. Use:

```sql
toDateTime('2024-01-15 12:00:00', 'UTC')
```

---

## 14. DateTime64

`DateTime64` follows the same general idea as `DateTime`, but stores fractional seconds.

```sql
DateTime64(3)
DateTime64(3, 'UTC')
DateTime64(3, 'Europe/Berlin')
```

The timezone rules are similar:

- explicit timezone columns use their own timezone,
- plain `DateTime64` depends on server/session behavior,
- one-argument conversion functions can still depend on server/session timezone,
- explicit timezone arguments are safest.

For stable filters, prefer:

```sql
toDateTime64('2024-01-15 12:00:00.123', 3, 'UTC')
```

instead of relying on the server or session timezone.

---

## 15. DST and ambiguous local times

Some timezones have daylight saving time. That means a local wall-clock time may be:

- skipped,
- repeated,
- or interpreted differently depending on timezone database rules.

For example, in some regions `02:30` may not exist on the spring DST transition day. On the autumn transition day, the same local time may happen twice.

This is another reason to store important event timestamps as UTC:

```sql
DateTime('UTC')
```

and only convert to local time at the UI or reporting layer.

---

## 16. Troubleshooting

| Symptom                                                    | Likely cause                                                                | Fix                                                          |
| ---------------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `WHERE dt = '...'` returns no rows                         | The string was parsed in a different timezone than expected                 | Check `serverTimeZone` and `timeZone`                        |
| Bare literal works, but `toDateTime('...')` does not       | Bare literal uses column timezone; `toDateTime` uses server/session timezone | Use `toDateTime('...', 'TZ')`                                |
| Test passes locally but fails in CI                        | Different server/session timezone                                           | Set `session_timezone` explicitly or use explicit TZ args    |
| Query behaves differently after changing `session_timezone` | Plain `DateTime` depends on effective timezone                              | Use explicit timezone columns and explicit conversion functions |
| Distributed query gives inconsistent results               | Different shards may use different server timezones                         | Avoid one-argument `toDateTime`                              |

---

## 17. Final cheat sheet

```sql
-- Risky: depends on server/session timezone
toDateTime('2024-01-15 12:00:00')

-- Safe: explicit meaning
toDateTime('2024-01-15 12:00:00', 'UTC')
```

```sql
-- Uses column timezone
WHERE dt_utc = '2024-01-15 12:00:00'

-- Uses server/session timezone unless timezone is passed explicitly
WHERE dt_utc = toDateTime('2024-01-15 12:00:00')
```

So when reading or writing ClickHouse queries, always ask:

> **Which timezone parses this string?**

If the answer is not obvious from the SQL, make it explicit.
