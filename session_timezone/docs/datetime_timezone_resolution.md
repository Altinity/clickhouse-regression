# DateTime Timezone Resolution in ClickHouse

> **Sources:**
> - `src/Core/Settings.cpp` — official `session_timezone` setting description and examples
> - `src/DataTypes/DataTypeDateTime.h` — column type comments
> - ClickHouse docs: [DateTime](https://clickhouse.com/docs/sql-reference/data-types/datetime),
>   [DateTime64](https://clickhouse.com/docs/sql-reference/data-types/datetime64)
> - [ClickHouse PR #100647](https://github.com/ClickHouse/ClickHouse/pull/100647) — behavior change in 26.2.4

---

## How DateTime Values Are Stored

`DateTime` values are stored internally as **Unix timestamps** — seconds since
`1970-01-01 00:00:00 UTC`. The internal representation has **no timezone**. A timezone
only matters when converting between that integer and a human-readable string:

- **Parsing:** converting a string like `'2000-01-01 06:00:00'` → Unix timestamp
- **Display:** converting a Unix timestamp → string for SELECT output

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

**No timezone is stored in the column metadata.** The column name in metadata is just
`DateTime`. The effective timezone is resolved **at query time**:

- If `session_timezone` is set → uses session timezone
- Otherwise → uses server timezone (configured in `config.xml` or inherited from OS)

> **Important:** The column does not "remember" the server timezone at the time of
> `CREATE TABLE`. Any later change to the server timezone (or setting `session_timezone`
> in a query) immediately affects how values in this column are parsed and displayed.

### `DateTime('TZ')` — explicit timezone

```sql
CREATE TABLE t (d DateTime('Asia/Novosibirsk')) ENGINE = MergeTree ...
```

The timezone name `Asia/Novosibirsk` **is stored** in the column metadata. This timezone
is always used for parsing and display of this column, regardless of server timezone or
`session_timezone`.

---

## Behavior Without `session_timezone`

The **server timezone** governs all DateTime parsing and display. It is set in
`config.xml` via the `timezone` parameter, or inherited from the OS at server startup.

### String literals → use the column's effective timezone

```sql
-- Column d has no explicit timezone → uses server timezone (e.g. Europe/Berlin)
WHERE d = '2000-01-01 06:00:00'
-- → parsed as 2000-01-01 06:00:00 Europe/Berlin

-- Column d has explicit timezone DateTime('UTC')
WHERE d = '2000-01-01 06:00:00'
-- → parsed as 2000-01-01 06:00:00 UTC
```

### `toDateTime()` without explicit timezone → uses server timezone

```sql
WHERE d = toDateTime('2000-01-01 06:00:00')
-- → parsed as 2000-01-01 06:00:00 in server timezone, regardless of column type
```

### `toDateTime()` with explicit timezone → always uses that timezone

```sql
WHERE d = toDateTime('2000-01-01 06:00:00', 'UTC')
-- → parsed as 2000-01-01 06:00:00 UTC, always
```

### SELECT display

```sql
-- Stored: Unix timestamp 946706400

SELECT d FROM t;
-- DateTime (no tz), server = Europe/Berlin:      2000-01-01 07:00:00
-- DateTime('UTC'):                                2000-01-01 06:00:00
-- DateTime('Asia/Novosibirsk') (UTC+6 in 2000):  2000-01-01 12:00:00
```

---

## Behavior With `session_timezone` (Beta)

> `session_timezone` is a **Beta** setting. Not all DateTime parsing functions respect it.
> See the warning section below.

`session_timezone` overrides the server timezone **for the current session or query**.
You can set it per-query with `SETTINGS` or for the whole session with `SET`:

```sql
SET session_timezone = 'Asia/Novosibirsk';
-- or per query:
SELECT ... SETTINGS session_timezone = 'Asia/Novosibirsk';
```

### Effect on `DateTime` column (no explicit timezone)

`session_timezone` fully replaces the server timezone for this column. Both parsing
and display use the session timezone:

```sql
CREATE TABLE t (d DateTime) ENGINE = Memory AS
SELECT toDateTime('2000-01-01 00:00:00', 'UTC');
-- Stored: Unix timestamp 946684800 (= 2000-01-01 00:00:00 UTC)

SELECT d, timezone() FROM t
SETTINGS session_timezone = 'Asia/Novosibirsk';
-- Display: 2000-01-01 06:00:00   Asia/Novosibirsk
-- (the UTC value shown in Novosibirsk time = UTC+6 in year 2000)

SELECT * FROM t WHERE d = '2000-01-01 06:00:00'
SETTINGS session_timezone = 'Asia/Novosibirsk';
-- String parsed as 2000-01-01 06:00:00 Novosibirsk = 2000-01-01 00:00:00 UTC → MATCHES → 1 row

SELECT * FROM t WHERE d = '2000-01-01 00:00:00'
SETTINGS session_timezone = 'Asia/Novosibirsk';
-- String parsed as 2000-01-01 00:00:00 Novosibirsk = 1999-12-31 18:00:00 UTC → no match → 0 rows
```

### Effect on `DateTime('UTC')` column (explicit timezone)

For string literals in WHERE, the **column's explicit timezone wins** over
`session_timezone`. For `toDateTime()` without an explicit timezone argument,
`session_timezone` still applies. This is an **inconsistency** in the current behavior
(documented in the official setting description):

```sql
CREATE TABLE t (d DateTime('UTC')) ENGINE = Memory AS
SELECT toDateTime('2000-01-01 00:00:00', 'UTC');
-- Stored: 2000-01-01 00:00:00 UTC

-- String literal: inherits the column's UTC timezone → matches the stored value
SELECT *, timezone() FROM t
WHERE d = '2000-01-01 00:00:00'
SETTINGS session_timezone = 'Asia/Novosibirsk';
-- → 1 row: 2000-01-01 00:00:00   Asia/Novosibirsk
-- (matched because string was parsed as UTC, displayed in session timezone)

-- toDateTime() without tz: uses session_timezone → parsed as Novosibirsk → no match
SELECT *, timezone() FROM t
WHERE d = toDateTime('2000-01-01 00:00:00')
SETTINGS session_timezone = 'Asia/Novosibirsk';
-- → 0 rows
-- (toDateTime parsed as 2000-01-01 00:00:00 Novosibirsk = 1999-12-31 18:00:00 UTC ≠ stored value)
```

> This difference between string literals and `toDateTime()` is officially documented as
> a known subtlety. To avoid ambiguity, always pass the timezone explicitly:
> `toDateTime('...', 'UTC')`.

---

## Summary: Timezone Used for Parsing

| Expression | `DateTime` (no tz) | `DateTime('UTC')` |
|---|---|---|
| `'2000-01-01 00:00:00'` in WHERE, no session_tz | server timezone | UTC |
| `'2000-01-01 00:00:00'` in WHERE, session_tz set | **session timezone** | UTC (column tz wins) |
| `toDateTime('2000-01-01 00:00:00')`, no session_tz | server timezone | server timezone |
| `toDateTime('2000-01-01 00:00:00')`, session_tz set | **session timezone** | **session timezone** |
| `toDateTime('2000-01-01 00:00:00', 'UTC')` | UTC (explicit wins) | UTC (explicit wins) |
| SELECT display, no session_tz | server timezone | UTC |
| SELECT display, session_tz set | **session timezone** | UTC (column tz wins) |

---

## The `timezone()` Function

`timezone()` returns the **effective session timezone**: `session_timezone` if set,
otherwise the server timezone. It always reflects the current session context, not any
specific column's timezone.

```sql
SELECT timeZone(), serverTimeZone() FORMAT CSV;
-- "Europe/Berlin","Europe/Berlin"

SELECT timeZone(), serverTimeZone() SETTINGS session_timezone = 'Asia/Novosibirsk' FORMAT CSV;
-- "Asia/Novosibirsk","Europe/Berlin"
```

---

## Version History

| Version | Behavior |
|---|---|
| ≤ 26.1 | `DateTime` (no tz): timezone baked in at server/table-load time, `session_timezone` ignored for string parsing in `WHERE` and `INSERT` |
| ≥ 26.2.4 | `DateTime` (no tz): `session_timezone` correctly applied at query time for all parsing paths (INSERT, WHERE, literals) |

The behavior change was introduced by [PR #100647](https://github.com/ClickHouse/ClickHouse/pull/100647),
fixing [issue #100614](https://github.com/ClickHouse/ClickHouse/issues/100614).

---

## See Also

- [`session_timezone` setting](https://clickhouse.com/docs/operations/settings/settings#session_timezone)
- [`DateTime` data type](https://clickhouse.com/docs/sql-reference/data-types/datetime)
- [`DateTime64` data type](https://clickhouse.com/docs/sql-reference/data-types/datetime64)
- [`date_time_input_format` setting](https://clickhouse.com/docs/operations/settings/settings-formats#date_time_input_format)
- [ClickHouse issue #100614](https://github.com/ClickHouse/ClickHouse/issues/100614)
- [ClickHouse PR #100647](https://github.com/ClickHouse/ClickHouse/pull/100647)
