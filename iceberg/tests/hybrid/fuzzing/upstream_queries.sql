-- Upstream-derived Hybrid fuzz shapes (hand-ported from ClickHouse 0_stateless
-- patterns). Placeholders: {hybrid_table}, {merge_tree_table}, {join_settings}
-- Keep this additive to hybrid_query_fuzzing_queries.sql — do not duplicate
-- basic SELECT/COUNT coverage already covered there.

-- LIMIT BY (stateless-style)
SELECT string_col, long_col FROM {hybrid_table} ORDER BY long_col DESC LIMIT 1 BY string_col;

-- OFFSET
SELECT * FROM {hybrid_table} ORDER BY long_col LIMIT 5 OFFSET 3;

-- Window functions
SELECT string_col, long_col, row_number() OVER (PARTITION BY string_col ORDER BY long_col) AS rn FROM {hybrid_table} LIMIT 50;

SELECT string_col, long_col, sum(long_col) OVER (PARTITION BY string_col) AS part_sum FROM {hybrid_table} LIMIT 50;

SELECT string_col, long_col, lag(long_col) OVER (PARTITION BY string_col ORDER BY long_col) AS prev_long FROM {hybrid_table} LIMIT 50;

-- UNION DISTINCT
SELECT string_col FROM {hybrid_table} UNION DISTINCT SELECT string_col FROM {merge_tree_table};

-- EXCEPT / INTERSECT shapes via WHERE NOT IN / IN (portable)
SELECT string_col FROM {hybrid_table} WHERE string_col GLOBAL NOT IN (SELECT string_col FROM {merge_tree_table} WHERE long_col < 0);

-- Subquery in FROM
SELECT t.string_col, t.cnt FROM (SELECT string_col, count() AS cnt FROM {hybrid_table} GROUP BY string_col) AS t ORDER BY t.cnt DESC LIMIT 10;

-- Scalar subquery
SELECT * FROM {hybrid_table} WHERE long_col > (SELECT avg(long_col) FROM {hybrid_table}) LIMIT 20;

-- WITH FILL (Date gaps) — only when date_col present
SELECT date_col, count() AS cnt FROM {hybrid_table} WHERE date_col = date_col GROUP BY date_col ORDER BY date_col WITH FILL LIMIT 20;

-- GROUP BY WITH TOTALS
SELECT string_col, count() AS cnt FROM {hybrid_table} GROUP BY string_col WITH TOTALS ORDER BY string_col;

-- SAMPLE-like filter via cityHash64 (deterministic subset)
SELECT count() FROM {hybrid_table} WHERE cityHash64(string_col, long_col) % 10 = 0;

-- ORDER BY expression
SELECT string_col, long_col FROM {hybrid_table} ORDER BY length(string_col), long_col DESC LIMIT 20;

-- Multi-arg aggregate + FILTER-style countIf (avoid Nullable null-map on Hybrid)
SELECT string_col, countIf(long_col > 1000), avg(ifNull(double_col, 0)) FROM {hybrid_table} GROUP BY string_col;

-- JOIN against MergeTree with local join mode
SELECT h.string_col, h.long_col, m.long_col AS mt_long FROM {hybrid_table} AS h INNER JOIN {merge_tree_table} AS m ON h.string_col = m.string_col LIMIT 20 {join_settings};

-- GLOBAL IN
SELECT * FROM {hybrid_table} WHERE string_col GLOBAL IN (SELECT string_col FROM {merge_tree_table} LIMIT 5) LIMIT 20;
