"""Table schema variants shared by the datatypes and parquet-variety
features.

Every column derives deterministically from ``id`` so expected values and
aggregates can be computed in Python. The wide schema carries a column for
every Iceberg type the Spark writer supports; the nullable schema makes
NULL-dense columns the norm rather than the exception.
"""

NARROW_COLUMNS = "id BIGINT, data STRING"

NARROW_INSERT = (
    "INSERT INTO {{table}} SELECT /*+ COALESCE(1) */ id, "
    "concat('row-', CAST(id AS STRING)) FROM range({rows})"
)

WIDE_COLUMNS = """
    id BIGINT,
    flag BOOLEAN,
    i32 INT,
    i64 BIGINT,
    f32 FLOAT,
    f64 DOUBLE,
    dec DECIMAL(18,2),
    d DATE,
    ts TIMESTAMP,
    ts_ntz TIMESTAMP_NTZ,
    s STRING,
    bin BINARY,
    arr ARRAY<STRING>,
    m MAP<STRING, INT>,
    st STRUCT<a: INT, tags: ARRAY<STRING>>,
    nested MAP<STRING, ARRAY<INT>>,
    nl INT
""".strip()

WIDE_INSERT = """
INSERT INTO {{table}} SELECT /*+ COALESCE(1) */
    id,
    id % 2 = 0,
    CAST(id * 2 AS INT),
    id * 1000000,
    CAST(id * 0.5 AS FLOAT),
    CAST(id * 0.25 AS DOUBLE),
    CAST(id AS DECIMAL(18,2)) + 0.25,
    date_add(DATE'2024-01-01', CAST(id AS INT)),
    timestampadd(SECOND, CAST(id AS INT), TIMESTAMP'2024-01-01 00:00:00'),
    timestampadd(SECOND, CAST(id AS INT), TIMESTAMP_NTZ'2024-01-01 00:00:00'),
    concat('s-', CAST(id AS STRING)),
    CAST(concat('b-', CAST(id AS STRING)) AS BINARY),
    array(concat('a-', CAST(id AS STRING)), 'x'),
    map('k', CAST(id AS INT)),
    named_struct('a', CAST(id AS INT), 'tags', array(concat('t-', CAST(id AS STRING)))),
    map('k', array(CAST(id AS INT))),
    IF(id % 3 = 0, NULL, CAST(id AS INT))
FROM range({rows})
""".strip()

NULLABLE_COLUMNS = (
    "id BIGINT, n_int INT, n_str STRING, n_float DOUBLE, n_arr ARRAY<INT>"
)

NULLABLE_INSERT = (
    "INSERT INTO {{table}} SELECT /*+ COALESCE(1) */ id, "
    "IF(id % 2 = 0, NULL, CAST(id AS INT)), "
    "IF(id % 3 = 0, NULL, concat('n-', CAST(id AS STRING))), "
    "IF(id % 5 = 0, NULL, id * 0.5), "
    "IF(id % 7 = 0, NULL, array(CAST(id AS INT))) "
    "FROM range({rows})"
)

# schema name → (columns DDL, INSERT statement template with a {{table}}
# placeholder surviving one .format(rows=...) call)
SCHEMAS = {
    "narrow": (NARROW_COLUMNS, NARROW_INSERT),
    "wide": (WIDE_COLUMNS, WIDE_INSERT),
    "nullable": (NULLABLE_COLUMNS, NULLABLE_INSERT),
}


def columns_and_insert(schema, rows):
    """(columns DDL, ready INSERT statement with a {table} placeholder) for
    one schema variant and row count."""
    columns, insert = SCHEMAS[schema]
    return columns, insert.format(rows=rows)
