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


# --- Reporting fact-table schema (customer evaluation_reports.19pitest) ------
#
# A ~438-column, entirely-nullable, decimal-heavy flat analytics table matching
# a customer's Iceberg table. A synthetic non-null ``id`` key is prepended for
# row-order verification (the customer table has no key; deletion vectors
# address physical row positions). Every non-id column is NULL on the rows
# where ``id % 10 == 5`` so the all-nullable layout exercises Parquet
# definition levels with real nulls, while every other value derives
# deterministically from ``id`` so expected values are computed in Python.
#
# The point of this schema is physical-layout variety, not SQL semantics: a
# very high column count, high-precision decimals stored as fixed-length byte
# arrays (precision > 18), and pervasive definition levels are decode paths the
# narrow/wide/nullable schemas above do not exercise.

REPORTING_NULL_MODULUS = 10
REPORTING_NULL_REMAINDER = 5
REPORTING_BASE_DATE = "2024-01-01"

# decimal Spark type -> fractional-part digits appended after ``str(id)`` (the
# exact value a surviving row carries, rendered by ClickHouse at that scale)
REPORTING_DECIMAL_FRACTIONS = {
    "DECIMAL(38,15)": "000000000000123",
    "DECIMAL(28,6)": "000123",
    "DECIMAL(28,9)": "000000123",
    "DECIMAL(28,2)": "25",
}


def _reporting_column_types():
    """Ordered ``[(name, spark_type)]`` faithfully reproducing the customer
    schema, without the synthetic ``id`` key."""
    columns = [
        ("ReportDate", "DATE"),
        ("PartnerId", "STRING"),
        ("AdvertiserId", "STRING"),
        ("CampaignId", "STRING"),
        ("AdGroupId", "STRING"),
        ("Country", "STRING"),
        ("Region", "STRING"),
        ("City", "STRING"),
        ("Metro", "BIGINT"),
        ("TenantId", "BIGINT"),
        ("DataDomainId", "BIGINT"),
        ("ReportHourUtc", "TIMESTAMP"),
        ("LateDataProviderId", "BIGINT"),
        ("DataReceivedHourUtc", "TIMESTAMP"),
        ("ldp_key", "BIGINT"),
        ("report_date", "DATE"),
        ("BatchId", "STRING"),
        ("InsertTimestamp", "TIMESTAMP"),
        ("BidCount", "BIGINT"),
        ("ImpressionCount", "BIGINT"),
        ("AdvertiserCostInUSD", "DECIMAL(38,15)"),
        ("AdvertiserCostInAdvertiserCurrency", "DECIMAL(38,15)"),
        ("AdvertiserCostInPartnerCurrency", "DECIMAL(38,15)"),
        ("PartnerCostInUSD", "DECIMAL(38,15)"),
        ("PartnerCostInAdvertiserCurrency", "DECIMAL(38,15)"),
        ("PartnerCostInPartnerCurrency", "DECIMAL(38,15)"),
        ("CreativeIsTrackableCount", "BIGINT"),
        ("CreativeWasViewableCount", "BIGINT"),
        ("ClickCount", "BIGINT"),
        ("CustomCPACount", "DECIMAL(28,6)"),
        ("VideoEventStartCount", "BIGINT"),
        ("VideoEventCompleteCount", "BIGINT"),
        ("CustomRevenue", "DECIMAL(28,6)"),
        ("QualityReachIndex", "DECIMAL(28,9)"),
        ("QualityReachMeasuredImpressionCount", "BIGINT"),
        ("QualityScore", "DECIMAL(28,6)"),
        ("AudienceImpressionCount", "DECIMAL(28,2)"),
    ]
    for prefix in ("LastClick", "LastView", "Touch"):
        for index in range(1, 51):
            columns.append((f"{prefix}{index}Count", "BIGINT"))
            columns.append((f"{prefix}{index}Revenue", "DECIMAL(28,6)"))
    for index in range(1, 51):
        columns.append((f"Decay{index}Count", "DECIMAL(28,6)"))
        columns.append((f"Decay{index}Revenue", "DECIMAL(28,6)"))
    columns.append(("QualityScoreMeasuredImpressionCount", "BIGINT"))
    return columns


def _reporting_base_expr(spark_type):
    """Spark expression over ``id`` for the non-null value of one column."""
    if spark_type == "DATE":
        return f"date_add(DATE'{REPORTING_BASE_DATE}', CAST(id AS INT))"
    if spark_type == "TIMESTAMP":
        return (
            "timestampadd(SECOND, CAST(id AS INT), "
            f"TIMESTAMP'{REPORTING_BASE_DATE} 00:00:00')"
        )
    if spark_type == "STRING":
        return "CONCAT('s-', CAST(id AS STRING))"
    if spark_type == "BIGINT":
        return "id"
    if spark_type in REPORTING_DECIMAL_FRACTIONS:
        fraction = REPORTING_DECIMAL_FRACTIONS[spark_type]
        # build the literal from the id string so the stored value is exact at
        # the declared scale (no floating-point arithmetic in the writer)
        return f"CAST(CONCAT(CAST(id AS STRING), '.{fraction}') AS {spark_type})"
    raise ValueError(f"unhandled reporting column type {spark_type!r}")


def _reporting_value_expr(spark_type):
    """Full Spark expression including the all-nullable NULL band."""
    base = _reporting_base_expr(spark_type)
    return (
        f"IF(id % {REPORTING_NULL_MODULUS} = {REPORTING_NULL_REMAINDER}, "
        f"CAST(NULL AS {spark_type}), {base})"
    )


def reporting_columns_and_insert(rows):
    """(columns DDL, ready INSERT with a ``{table}`` placeholder) for the
    full-width reporting schema over ``id`` in ``0..rows-1``.

    ``COALESCE(1)`` keeps the whole INSERT in one write task so it produces a
    single data file whose physical row order the crafted-vector scenarios
    depend on."""
    types = _reporting_column_types()
    columns_ddl = "id BIGINT, " + ", ".join(
        f"{name} {spark_type}" for name, spark_type in types
    )
    value_exprs = ", ".join(
        _reporting_value_expr(spark_type) for _, spark_type in types
    )
    insert = (
        "INSERT INTO {table} SELECT /*+ COALESCE(1) */ id, "
        + value_exprs
        + f" FROM range({rows})"
    )
    return columns_ddl, insert


def reporting_is_null(row_id):
    """True for rows who's every non-id column is NULL (the all-nullable
    band)."""
    return row_id % REPORTING_NULL_MODULUS == REPORTING_NULL_REMAINDER


def reporting_decimal_str(row_id, spark_type):
    """Exact ClickHouse-rendered value of a reporting decimal column for a
    non-null row (``str(id)`` followed by the type's fixed fractional part)."""
    return f"{row_id}.{REPORTING_DECIMAL_FRACTIONS[spark_type]}"
