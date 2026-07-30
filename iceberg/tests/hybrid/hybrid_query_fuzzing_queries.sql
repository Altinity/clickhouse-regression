-- Hybrid Query Fuzzing SQL Queries
-- Placeholders: {hybrid_table}, {merge_tree_table}, {clickhouse_iceberg_table_name}, {join_settings}
-- Each query is separated by a blank line

-- Basic SELECT queries
SELECT * FROM {hybrid_table} LIMIT 10;

SELECT * FROM {hybrid_table} ORDER BY long_col LIMIT 100;

SELECT * FROM {hybrid_table} WHERE long_col > 1000 LIMIT 50;

SELECT * FROM {hybrid_table} WHERE string_col = 'Alice' ORDER BY integer_col;

SELECT * FROM {hybrid_table} WHERE boolean_col = true AND double_col > 400.0;

SELECT * FROM {hybrid_table} WHERE boolean_col = true AND double_col <= 400.0;

-- Aggregate functions - COUNT
SELECT COUNT(*) FROM {hybrid_table};

SELECT COUNT(*) as total_rows FROM {hybrid_table} WHERE long_col IS NOT NULL;

SELECT COUNT(DISTINCT string_col) as unique_strings FROM {hybrid_table};

SELECT COUNT(long_col), COUNT(double_col), COUNT(integer_col) FROM {hybrid_table};

-- Aggregate functions - SUM
SELECT SUM(long_col) as sum_long FROM {hybrid_table};

SELECT SUM(long_col) as sum_long, SUM(integer_col) as sum_int FROM {hybrid_table} WHERE long_col > 400;

SELECT SUM(double_col) as sum_double FROM {hybrid_table} WHERE double_col IS NOT NULL;

SELECT SUM(long_col + integer_col) as sum_combined FROM {hybrid_table};

-- Aggregate functions - AVG
SELECT AVG(long_col) as avg_long FROM {hybrid_table};

SELECT AVG(double_col) as avg_double FROM {hybrid_table} WHERE double_col IS NOT NULL;

SELECT AVG(long_col) as avg_long, AVG(integer_col) as avg_int FROM {hybrid_table};

SELECT AVG(long_col), AVG(double_col), AVG(integer_col) FROM {hybrid_table} WHERE boolean_col = true;

-- Aggregate functions - MIN/MAX
SELECT MIN(long_col) as min_long, MAX(long_col) as max_long FROM {hybrid_table};

SELECT MIN(double_col) as min_double, MAX(double_col) as max_double FROM {hybrid_table};

SELECT MIN(integer_col) as min_int, MAX(integer_col) as max_int FROM {hybrid_table};

SELECT MIN(string_col) as min_string, MAX(string_col) as max_string FROM {hybrid_table};

SELECT MIN(long_col), MAX(long_col), MIN(double_col), MAX(double_col) FROM {hybrid_table};

-- Aggregate functions - GROUP BY
SELECT string_col, COUNT(*) as cnt FROM {hybrid_table} GROUP BY string_col ORDER BY cnt DESC;

SELECT string_col, SUM(long_col) as sum_long FROM {hybrid_table} GROUP BY string_col;

SELECT string_col, AVG(double_col) as avg_double FROM {hybrid_table} GROUP BY string_col ORDER BY string_col;

SELECT boolean_col, COUNT(*) as cnt, AVG(long_col) as avg_long FROM {hybrid_table} GROUP BY boolean_col;

SELECT string_col, boolean_col, COUNT(*) as cnt FROM {hybrid_table} GROUP BY string_col, boolean_col ORDER BY cnt DESC;

SELECT string_col, MIN(long_col) as min_long, MAX(long_col) as max_long, AVG(long_col) as avg_long FROM {hybrid_table} GROUP BY string_col;

-- Aggregate functions - HAVING
SELECT string_col, COUNT(*) as cnt FROM {hybrid_table} GROUP BY string_col HAVING cnt > 2;

SELECT string_col, SUM(long_col) as sum_long FROM {hybrid_table} GROUP BY string_col HAVING sum_long > 2000;

SELECT boolean_col, AVG(double_col) as avg_double FROM {hybrid_table} GROUP BY boolean_col HAVING avg_double > 400.0;

SELECT string_col, COUNT(*) as cnt, AVG(long_col) as avg_long FROM {hybrid_table} GROUP BY string_col HAVING cnt >= 2 AND avg_long > 1000;

-- Aggregate functions - Advanced
SELECT groupBitXor(cityHash64(*)) as hash FROM {hybrid_table};

SELECT groupBitXor(cityHash64(*)) as hash FROM (SELECT * FROM {hybrid_table} ORDER BY tuple(*));

SELECT uniq(string_col) as unique_strings FROM {hybrid_table};

SELECT uniqExact(string_col) as exact_unique_strings FROM {hybrid_table};

SELECT quantile(0.5)(long_col) as median_long FROM {hybrid_table};

SELECT quantile(0.25)(long_col) as q25, quantile(0.5)(long_col) as q50, quantile(0.75)(long_col) as q75 FROM {hybrid_table};

SELECT argMin(string_col, long_col) as min_string, argMax(string_col, long_col) as max_string FROM {hybrid_table};

SELECT any(string_col) as any_string, anyLast(string_col) as any_last_string FROM {hybrid_table};

SELECT topK(3)(string_col) as top_strings FROM {hybrid_table};

SELECT groupArray(string_col) as string_array FROM {hybrid_table} GROUP BY boolean_col;

SELECT groupUniqArray(string_col) as unique_string_array FROM {hybrid_table} GROUP BY boolean_col;

-- WHERE clauses with different conditions
SELECT * FROM {hybrid_table} WHERE long_col BETWEEN 1000 AND 2000;

SELECT * FROM {hybrid_table} WHERE string_col IN ('Alice', 'Bob');

SELECT * FROM {hybrid_table} WHERE long_col IS NOT NULL AND double_col IS NOT NULL;

SELECT * FROM {hybrid_table} WHERE long_col > integer_col;

SELECT * FROM {hybrid_table} WHERE double_col >= 400.0 AND double_col <= 500.0;

SELECT * FROM {hybrid_table} WHERE string_col LIKE 'A%';

SELECT * FROM {hybrid_table} WHERE string_col LIKE '%e';

SELECT * FROM {hybrid_table} WHERE (long_col > 1500 OR integer_col > 1500) AND boolean_col = true;

SELECT * FROM {hybrid_table} WHERE NOT boolean_col;

-- ORDER BY
SELECT * FROM {hybrid_table} ORDER BY long_col ASC LIMIT 10;

SELECT * FROM {hybrid_table} ORDER BY long_col DESC LIMIT 10;

SELECT * FROM {hybrid_table} ORDER BY string_col, long_col LIMIT 20;

SELECT * FROM {hybrid_table} ORDER BY double_col DESC, integer_col ASC LIMIT 15;

SELECT string_col, COUNT(*) as cnt FROM {hybrid_table} GROUP BY string_col ORDER BY cnt DESC LIMIT 5;

-- LIMIT and OFFSET
SELECT * FROM {hybrid_table} LIMIT 5;

SELECT * FROM {hybrid_table} LIMIT 10 OFFSET 5;

SELECT * FROM {hybrid_table} ORDER BY long_col LIMIT 3 OFFSET 2;

-- DISTINCT
SELECT DISTINCT string_col FROM {hybrid_table};

SELECT DISTINCT boolean_col, string_col FROM {hybrid_table};

SELECT DISTINCT string_col FROM {hybrid_table} ORDER BY string_col;

-- Subqueries
SELECT * FROM {hybrid_table} WHERE long_col > (SELECT AVG(long_col) FROM {hybrid_table});

SELECT * FROM {hybrid_table} WHERE string_col IN (SELECT DISTINCT string_col FROM {hybrid_table} WHERE long_col > 1500);

SELECT string_col, long_col FROM {hybrid_table} WHERE long_col = (SELECT MAX(long_col) FROM {hybrid_table});

SELECT * FROM (SELECT string_col, AVG(long_col) as avg_long FROM {hybrid_table} GROUP BY string_col) WHERE avg_long > 1500;

-- JOINs with MergeTree table
SELECT h.*, m.* FROM {hybrid_table} h INNER JOIN {merge_tree_table} m ON h.string_col = m.string_col LIMIT 10 {join_settings};

SELECT h.string_col, h.long_col, m.double_col FROM {hybrid_table} h LEFT JOIN {merge_tree_table} m ON h.string_col = m.string_col {join_settings};

SELECT h.string_col, COUNT(*) as cnt FROM {hybrid_table} h JOIN {merge_tree_table} m ON h.string_col = m.string_col GROUP BY h.string_col {join_settings};

SELECT h.string_col, h.long_col, m.long_col as mt_long FROM {hybrid_table} h RIGHT JOIN {merge_tree_table} m ON h.string_col = m.string_col WHERE h.long_col IS NOT NULL {join_settings};

SELECT h.*, m.* FROM {hybrid_table} h FULL OUTER JOIN {merge_tree_table} m ON h.string_col = m.string_col LIMIT 10 {join_settings};

-- JOINs with Iceberg table
SELECT h.*, i.* FROM {hybrid_table} h INNER JOIN {clickhouse_iceberg_table_name} i ON h.string_col = i.string_col LIMIT 10 {join_settings};

SELECT h.string_col, h.long_col, i.double_col FROM {hybrid_table} h LEFT JOIN {clickhouse_iceberg_table_name} i ON h.string_col = i.string_col {join_settings};

SELECT h.string_col, AVG(h.long_col) as avg_hybrid, AVG(i.long_col) as avg_iceberg FROM {hybrid_table} h JOIN {clickhouse_iceberg_table_name} i ON h.string_col = i.string_col GROUP BY h.string_col {join_settings};

-- UNION queries
SELECT * FROM {hybrid_table} UNION ALL SELECT * FROM {merge_tree_table} LIMIT 20;

SELECT string_col, long_col FROM {hybrid_table} UNION ALL SELECT string_col, long_col FROM {merge_tree_table} ORDER BY string_col LIMIT 15;

SELECT string_col, COUNT(*) as cnt FROM {hybrid_table} GROUP BY string_col UNION ALL SELECT string_col, COUNT(*) as cnt FROM {merge_tree_table} GROUP BY string_col ORDER BY string_col;

SELECT string_col, long_col FROM {hybrid_table} UNION DISTINCT SELECT string_col, long_col FROM {merge_tree_table} ORDER BY string_col LIMIT 10;

SELECT * FROM {hybrid_table} UNION ALL SELECT * FROM {merge_tree_table} UNION ALL SELECT * FROM {clickhouse_iceberg_table_name} LIMIT 30;

-- UNION with aggregates
SELECT 'hybrid' as source, string_col, SUM(long_col) as sum_long FROM {hybrid_table} GROUP BY string_col UNION ALL SELECT 'mergetree' as source, string_col, SUM(long_col) as sum_long FROM {merge_tree_table} GROUP BY string_col ORDER BY string_col;

SELECT 'hybrid' as source, COUNT(*) as cnt FROM {hybrid_table} UNION ALL SELECT 'mergetree' as source, COUNT(*) as cnt FROM {merge_tree_table} UNION ALL SELECT 'iceberg' as source, COUNT(*) as cnt FROM {clickhouse_iceberg_table_name};

-- Complex queries with multiple clauses
SELECT string_col, COUNT(*) as cnt, AVG(long_col) as avg_long, SUM(double_col) as sum_double FROM {hybrid_table} WHERE long_col > 1000 GROUP BY string_col HAVING cnt > 1 ORDER BY avg_long DESC LIMIT 5;

SELECT h.string_col, h.long_col, m.double_col FROM {hybrid_table} h JOIN {merge_tree_table} m ON h.string_col = m.string_col WHERE h.long_col > 1500 ORDER BY h.long_col DESC LIMIT 10 {join_settings};

SELECT string_col, AVG(long_col) as avg_long FROM {hybrid_table} WHERE boolean_col = true GROUP BY string_col HAVING avg_long > (SELECT AVG(long_col) FROM {hybrid_table}) ORDER BY avg_long DESC;

-- Window functions (if supported)
SELECT string_col, long_col, ROW_NUMBER() OVER (PARTITION BY string_col ORDER BY long_col) as rn FROM {hybrid_table} LIMIT 20;

SELECT string_col, long_col, RANK() OVER (ORDER BY long_col DESC) as rank_val FROM {hybrid_table} LIMIT 15;

SELECT string_col, long_col, SUM(long_col) OVER (PARTITION BY string_col) as sum_partition FROM {hybrid_table} LIMIT 20;

SELECT string_col, long_col, AVG(long_col) OVER (PARTITION BY string_col ORDER BY long_col) as avg_running FROM {hybrid_table} LIMIT 20;

-- CASE expressions
SELECT string_col, CASE WHEN long_col > 1500 THEN 'high' WHEN long_col > 1000 THEN 'medium' ELSE 'low' END as category FROM {hybrid_table};

SELECT string_col, SUM(CASE WHEN boolean_col = true THEN long_col ELSE 0 END) as sum_true, SUM(CASE WHEN boolean_col = false THEN long_col ELSE 0 END) as sum_false FROM {hybrid_table} GROUP BY string_col;

-- Date functions
SELECT string_col, date_col, toYear(date_col) as year FROM {hybrid_table} WHERE date_col IS NOT NULL LIMIT 10;

SELECT string_col, timestamp_col, toDate(timestamp_col) as date_part FROM {hybrid_table} WHERE timestamp_col IS NOT NULL LIMIT 10;

SELECT toYear(date_col) as year, COUNT(*) as cnt FROM {hybrid_table} WHERE date_col IS NOT NULL GROUP BY year ORDER BY year;

-- String functions
SELECT string_col, length(string_col) as str_len, upper(string_col) as upper_str FROM {hybrid_table} LIMIT 10;

SELECT string_col, substring(string_col, 1, 3) as substr FROM {hybrid_table} LIMIT 10;

SELECT string_col, concat(string_col, '_', toString(long_col)) as combined FROM {hybrid_table} LIMIT 10;

-- Mathematical functions
SELECT long_col, integer_col, long_col + integer_col as sum_cols, long_col * 2 as doubled FROM {hybrid_table} LIMIT 10;

SELECT double_col, round(double_col, 2) as rounded, floor(double_col) as floored FROM {hybrid_table} WHERE double_col IS NOT NULL LIMIT 10;

SELECT long_col, abs(long_col - 1500) as diff_from_1500 FROM {hybrid_table} LIMIT 10;

-- NULL handling
SELECT COUNT(*) as total, COUNT(long_col) as non_null_long, COUNT(*) - COUNT(long_col) as null_long FROM {hybrid_table};

SELECT string_col, countIf(long_col IS NULL) as null_count, countIf(long_col IS NOT NULL) as non_null_count FROM {hybrid_table} GROUP BY string_col;

SELECT * FROM {hybrid_table} WHERE long_col IS NULL OR double_col IS NULL LIMIT 10;

SELECT coalesce(long_col, 0) as long_with_default FROM {hybrid_table} LIMIT 10;

-- Multiple table comparisons
SELECT 'hybrid' as table_name, COUNT(*) as row_count FROM {hybrid_table} UNION ALL SELECT 'mergetree' as table_name, COUNT(*) as row_count FROM {merge_tree_table} UNION ALL SELECT 'iceberg' as table_name, COUNT(*) as row_count FROM {clickhouse_iceberg_table_name};

SELECT COALESCE(hm.string_col, i.string_col) as string_col, hm.hybrid_long, hm.mt_long, i.long_col as iceberg_long FROM (SELECT COALESCE(h.string_col, m.string_col) as string_col, h.long_col as hybrid_long, m.long_col as mt_long FROM {hybrid_table} h FULL OUTER JOIN {merge_tree_table} m ON h.string_col = m.string_col {join_settings}) hm FULL OUTER JOIN {clickhouse_iceberg_table_name} i ON hm.string_col = i.string_col LIMIT 10 {join_settings};

-- EXISTS and IN subqueries
SELECT * FROM {hybrid_table} h WHERE EXISTS (SELECT 1 FROM {merge_tree_table} m WHERE m.string_col = h.string_col);

SELECT * FROM {hybrid_table} WHERE string_col IN (SELECT DISTINCT string_col FROM {merge_tree_table} WHERE long_col > 1500);

SELECT * FROM {hybrid_table} WHERE string_col NOT IN (SELECT DISTINCT string_col FROM {merge_tree_table} WHERE long_col < 1000);

-- CTE (Common Table Expressions)
WITH hybrid_stats AS (SELECT string_col, AVG(long_col) as avg_long FROM {hybrid_table} GROUP BY string_col) SELECT * FROM hybrid_stats WHERE avg_long > 1500 ORDER BY avg_long DESC;

WITH mt_stats AS (SELECT string_col, COUNT(*) as cnt FROM {merge_tree_table} GROUP BY string_col), hybrid_stats AS (SELECT string_col, COUNT(*) as cnt FROM {hybrid_table} GROUP BY string_col) SELECT COALESCE(mt_stats.string_col, hybrid_stats.string_col) as string_col, COALESCE(mt_stats.cnt, 0) as mt_cnt, COALESCE(hybrid_stats.cnt, 0) as hybrid_cnt FROM mt_stats FULL OUTER JOIN hybrid_stats ON mt_stats.string_col = hybrid_stats.string_col {join_settings};

-- Array and map functions
SELECT string_col, groupArray(long_col) as long_array FROM {hybrid_table} GROUP BY string_col;

SELECT string_col, groupArrayDistinct(long_col) as unique_long_array FROM {hybrid_table} GROUP BY string_col;

SELECT string_col, arraySort(groupArray(long_col)) as sorted_array FROM {hybrid_table} GROUP BY string_col;

-- Conditional aggregates
SELECT string_col, countIf(boolean_col = true) as true_count, countIf(boolean_col = false) as false_count FROM {hybrid_table} GROUP BY string_col;

SELECT string_col, sumIf(long_col, long_col > 1500) as sum_high, sumIf(long_col, long_col <= 1500) as sum_low FROM {hybrid_table} GROUP BY string_col;

SELECT string_col, avgIf(double_col, double_col > 400.0) as avg_high_double FROM {hybrid_table} GROUP BY string_col;

-- Comparison queries
SELECT h.string_col, h.long_col as hybrid_long, m.long_col as mt_long, (h.long_col = m.long_col) as matches FROM {hybrid_table} h JOIN {merge_tree_table} m ON h.string_col = m.string_col LIMIT 10 {join_settings};

SELECT h.string_col, h.long_col as hybrid_long, i.long_col as iceberg_long, abs(h.long_col - i.long_col) as diff FROM {hybrid_table} h JOIN {clickhouse_iceberg_table_name} i ON h.string_col = i.string_col LIMIT 10 {join_settings};

