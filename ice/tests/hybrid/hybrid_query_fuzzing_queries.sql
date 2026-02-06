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
SELECT string_col, long_col, row_number() OVER (PARTITION BY string_col ORDER BY long_col) as rn FROM {hybrid_table} LIMIT 20;

SELECT string_col, long_col, rank() OVER (ORDER BY long_col DESC) as rank_val FROM {hybrid_table} LIMIT 15;

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

-- Hybrid partitioning queries (date_col based partitioning)
SELECT date_col, COUNT(*) as cnt FROM {hybrid_table} WHERE date_col IS NOT NULL GROUP BY date_col ORDER BY date_col;

SELECT date_col, string_col, COUNT(*) as cnt, AVG(long_col) as avg_long FROM {hybrid_table} WHERE date_col <= '2024-01-01' GROUP BY date_col, string_col ORDER BY date_col, cnt DESC;

SELECT date_col, string_col, COUNT(*) as cnt, AVG(long_col) as avg_long FROM {hybrid_table} WHERE date_col > '2024-01-01' GROUP BY date_col, string_col ORDER BY date_col, cnt DESC;

SELECT date_col, COUNT(*) as total_rows, SUM(long_col) as sum_long, AVG(double_col) as avg_double FROM {hybrid_table} WHERE date_col IS NOT NULL GROUP BY date_col;

-- Decimal operations
SELECT string_col, SUM(decimal_col) as sum_decimal, AVG(decimal_col) as avg_decimal, MIN(decimal_col) as min_decimal, MAX(decimal_col) as max_decimal FROM {hybrid_table} WHERE decimal_col IS NOT NULL GROUP BY string_col ORDER BY sum_decimal DESC;

SELECT string_col, decimal_col, long_col, (decimal_col * long_col) as decimal_long_product FROM {hybrid_table} WHERE decimal_col IS NOT NULL AND long_col IS NOT NULL LIMIT 20;

SELECT string_col, decimal_col, double_col, (decimal_col + double_col) as decimal_double_sum FROM {hybrid_table} WHERE decimal_col IS NOT NULL AND double_col IS NOT NULL LIMIT 20;

SELECT string_col, round(decimal_col, 1) as rounded_decimal, floor(decimal_col) as floored_decimal, ceil(decimal_col) as ceiled_decimal FROM {hybrid_table} WHERE decimal_col IS NOT NULL LIMIT 20;

-- Float operations
SELECT string_col, SUM(float_col) as sum_float, AVG(float_col) as avg_float FROM {hybrid_table} WHERE float_col IS NOT NULL GROUP BY string_col ORDER BY avg_float DESC;

SELECT string_col, float_col, double_col, (float_col + double_col) as float_double_sum, (float_col * double_col) as float_double_product FROM {hybrid_table} WHERE float_col IS NOT NULL AND double_col IS NOT NULL LIMIT 20;

SELECT string_col, round(float_col, 2) as rounded_float, floor(float_col) as floored_float FROM {hybrid_table} WHERE float_col IS NOT NULL LIMIT 20;

-- Timestamp and time operations
SELECT string_col, timestamp_col, toStartOfHour(timestamp_col) as hour_start, toStartOfDay(timestamp_col) as day_start FROM {hybrid_table} WHERE timestamp_col IS NOT NULL LIMIT 20;

SELECT string_col, timestamptz_col, toTimeZone(timestamptz_col, 'America/New_York') as ny_time FROM {hybrid_table} WHERE timestamptz_col IS NOT NULL LIMIT 20;

SELECT string_col, timestamp_col, timestamptz_col, dateDiff('second', timestamp_col, timestamptz_col) as time_diff_seconds FROM {hybrid_table} WHERE timestamp_col IS NOT NULL AND timestamptz_col IS NOT NULL LIMIT 20;

SELECT toStartOfDay(timestamp_col) as day, COUNT(*) as cnt, AVG(long_col) as avg_long FROM {hybrid_table} WHERE timestamp_col IS NOT NULL GROUP BY day ORDER BY day;

SELECT toHour(timestamp_col) as hour, COUNT(*) as cnt FROM {hybrid_table} WHERE timestamp_col IS NOT NULL GROUP BY hour ORDER BY hour;

SELECT string_col, time_col, toHour(toDateTime(time_col)) as hour_from_time FROM {hybrid_table} WHERE time_col IS NOT NULL LIMIT 20;

-- Date operations
SELECT date_col, toYear(date_col) as year, toMonth(date_col) as month, toDayOfMonth(date_col) as day, toDayOfWeek(date_col) as day_of_week FROM {hybrid_table} WHERE date_col IS NOT NULL LIMIT 20;

SELECT toYear(date_col) as year, toMonth(date_col) as month, COUNT(*) as cnt, SUM(long_col) as sum_long FROM {hybrid_table} WHERE date_col IS NOT NULL GROUP BY year, month ORDER BY year, month;

SELECT date_col, dateDiff('day', date_col, today()) as days_from_today FROM {hybrid_table} WHERE date_col IS NOT NULL LIMIT 20;

SELECT date_col, addDays(date_col, 30) as date_plus_30, addMonths(date_col, 1) as date_plus_month FROM {hybrid_table} WHERE date_col IS NOT NULL LIMIT 20;

-- Complex WHERE with multiple data types
SELECT * FROM {hybrid_table} WHERE boolean_col = true AND long_col > 5000 AND double_col < 5000 AND string_col IN ('Alice', 'Bob', 'Charlie') AND date_col IS NOT NULL LIMIT 20;

SELECT * FROM {hybrid_table} WHERE (long_col + integer_col) > 10000 AND (double_col + float_col) < 10000 AND decimal_col IS NOT NULL LIMIT 20;

SELECT * FROM {hybrid_table} WHERE long_col BETWEEN 2000 AND 8000 AND double_col BETWEEN 2000.0 AND 8000.0 AND integer_col BETWEEN 2000 AND 8000 LIMIT 20;

-- Complex aggregations with multiple columns
SELECT string_col, COUNT(*) as cnt, SUM(long_col) as sum_long, AVG(double_col) as avg_double, SUM(integer_col) as sum_int, AVG(float_col) as avg_float, SUM(decimal_col) as sum_decimal FROM {hybrid_table} GROUP BY string_col ORDER BY cnt DESC;

SELECT boolean_col, string_col, COUNT(*) as cnt, AVG(long_col) as avg_long, AVG(double_col) as avg_double, AVG(integer_col) as avg_int, AVG(float_col) as avg_float FROM {hybrid_table} GROUP BY boolean_col, string_col ORDER BY cnt DESC LIMIT 20;

SELECT string_col, countIf(boolean_col = true) as true_count, countIf(boolean_col = false) as false_count, sumIf(long_col, long_col > 5000) as sum_high_long, sumIf(long_col, long_col <= 5000) as sum_low_long FROM {hybrid_table} GROUP BY string_col ORDER BY string_col;

-- Percentile and statistical functions
SELECT string_col, quantile(0.1)(long_col) as p10, quantile(0.25)(long_col) as p25, quantile(0.5)(long_col) as p50, quantile(0.75)(long_col) as p75, quantile(0.9)(long_col) as p90, quantile(0.99)(long_col) as p99 FROM {hybrid_table} WHERE long_col IS NOT NULL GROUP BY string_col;

SELECT string_col, stddevPop(long_col) as stddev_long, stddevSamp(long_col) as stddev_samp_long, varPop(long_col) as var_pop_long, varSamp(long_col) as var_samp_long FROM {hybrid_table} WHERE long_col IS NOT NULL GROUP BY string_col;

SELECT string_col, quantile(0.5)(double_col) as median_double, quantile(0.5)(integer_col) as median_int, quantile(0.5)(float_col) as median_float FROM {hybrid_table} GROUP BY string_col;

-- Advanced window functions
SELECT string_col, long_col, double_col, row_number() OVER (PARTITION BY string_col ORDER BY long_col DESC) as rn_long, row_number() OVER (PARTITION BY string_col ORDER BY double_col DESC) as rn_double FROM {hybrid_table} LIMIT 30;

SELECT string_col, long_col, rank() OVER (PARTITION BY string_col ORDER BY long_col) as rank_val, dense_rank() OVER (PARTITION BY string_col ORDER BY long_col) as dense_rank_val FROM {hybrid_table} LIMIT 30;

SELECT string_col, long_col, lagInFrame(long_col, 1) OVER (PARTITION BY string_col ORDER BY long_col) as prev_long, leadInFrame(long_col, 1) OVER (PARTITION BY string_col ORDER BY long_col) as next_long FROM {hybrid_table} LIMIT 30;

SELECT string_col, long_col, SUM(long_col) OVER (PARTITION BY string_col ORDER BY long_col ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as running_sum FROM {hybrid_table} LIMIT 30;

SELECT string_col, long_col, AVG(long_col) OVER (PARTITION BY string_col ORDER BY long_col ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING) as moving_avg FROM {hybrid_table} LIMIT 30;

SELECT string_col, long_col, double_col, first_value(long_col) OVER (PARTITION BY string_col ORDER BY long_col) as first_long, last_value(long_col) OVER (PARTITION BY string_col ORDER BY long_col ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_long FROM {hybrid_table} LIMIT 30;

-- Complex CASE expressions with multiple conditions
SELECT string_col, long_col, double_col, integer_col, CASE WHEN long_col > 8000 AND double_col > 8000 THEN 'very_high' WHEN long_col > 5000 OR double_col > 5000 THEN 'high' WHEN long_col > 2000 AND double_col > 2000 THEN 'medium' ELSE 'low' END as category FROM {hybrid_table} LIMIT 30;

SELECT string_col, boolean_col, CASE WHEN boolean_col = true THEN SUM(long_col) ELSE 0 END as sum_true_long, CASE WHEN boolean_col = false THEN SUM(long_col) ELSE 0 END as sum_false_long FROM {hybrid_table} GROUP BY string_col, boolean_col ORDER BY string_col;

SELECT string_col, COUNT(*) as total, COUNT(CASE WHEN long_col > 5000 THEN 1 END) as high_long_count, COUNT(CASE WHEN double_col > 5000 THEN 1 END) as high_double_count, COUNT(CASE WHEN integer_col > 5000 THEN 1 END) as high_int_count FROM {hybrid_table} GROUP BY string_col ORDER BY string_col;

-- String operations
SELECT string_col, length(string_col) as str_len, upper(string_col) as upper_str, lower(string_col) as lower_str, reverse(string_col) as reversed_str FROM {hybrid_table} LIMIT 20;

SELECT string_col, substring(string_col, 1, 1) as first_char, substring(string_col, -1) as last_char, position(string_col, 'a') as pos_a FROM {hybrid_table} LIMIT 20;

SELECT string_col, concat(string_col, '_', toString(long_col), '_', toString(integer_col)) as combined_str FROM {hybrid_table} LIMIT 20;

SELECT string_col, replace(string_col, 'a', 'A') as replaced_str, replaceAll(string_col, 'e', 'E') as replaced_all FROM {hybrid_table} LIMIT 20;

SELECT string_col, startsWith(string_col, 'A') as starts_with_a, endsWith(string_col, 'e') as ends_with_e, (position(string_col, 'a') > 0) as contains_a FROM {hybrid_table} LIMIT 20;

-- Mathematical operations
SELECT string_col, long_col, integer_col, (long_col + integer_col) as sum_cols, (long_col - integer_col) as diff_cols, (long_col * integer_col) as product_cols, CASE WHEN integer_col != 0 THEN (long_col / integer_col) ELSE NULL END as div_cols FROM {hybrid_table} WHERE long_col IS NOT NULL AND integer_col IS NOT NULL LIMIT 20;

SELECT string_col, double_col, float_col, (double_col + float_col) as sum_float_cols, (double_col - float_col) as diff_float_cols, (double_col * float_col) as product_float_cols FROM {hybrid_table} WHERE double_col IS NOT NULL AND float_col IS NOT NULL LIMIT 20;

SELECT string_col, long_col, pow(long_col, 2) as squared, sqrt(CAST(long_col AS Float64)) as sqrt_long, log2(long_col + 1) as log2_long FROM {hybrid_table} WHERE long_col IS NOT NULL AND long_col >= 0 LIMIT 20;

SELECT string_col, double_col, round(double_col, 0) as rounded, floor(double_col) as floored, ceil(double_col) as ceiled, trunc(double_col) as truncated FROM {hybrid_table} WHERE double_col IS NOT NULL LIMIT 20;

SELECT string_col, long_col, integer_col, abs(long_col - integer_col) as abs_diff, greatest(long_col, integer_col) as max_val, least(long_col, integer_col) as min_val FROM {hybrid_table} WHERE long_col IS NOT NULL AND integer_col IS NOT NULL LIMIT 20;

-- NULL handling with multiple columns
SELECT COUNT(*) as total_rows, COUNT(boolean_col) as non_null_bool, COUNT(long_col) as non_null_long, COUNT(double_col) as non_null_double, COUNT(string_col) as non_null_string, COUNT(timestamp_col) as non_null_timestamp, COUNT(date_col) as non_null_date, COUNT(integer_col) as non_null_int, COUNT(float_col) as non_null_float, COUNT(decimal_col) as non_null_decimal FROM {hybrid_table};

SELECT string_col, countIf(boolean_col IS NULL) as null_bool, countIf(long_col IS NULL) as null_long, countIf(double_col IS NULL) as null_double, countIf(integer_col IS NULL) as null_int FROM {hybrid_table} GROUP BY string_col ORDER BY string_col;

SELECT * FROM {hybrid_table} WHERE boolean_col IS NULL OR long_col IS NULL OR double_col IS NULL OR integer_col IS NULL LIMIT 20;

SELECT string_col, coalesce(long_col, 0) as long_with_default, coalesce(double_col, 0.0) as double_with_default, coalesce(integer_col, 0) as int_with_default FROM {hybrid_table} LIMIT 20;

SELECT string_col, ifNull(long_col, 0) as long_if_null, ifNull(double_col, 0.0) as double_if_null, nullIf(long_col, 5000) as long_null_if_5000 FROM {hybrid_table} LIMIT 20;

-- Complex JOINs with multiple conditions
SELECT h.string_col, h.long_col as hybrid_long, m.long_col as mt_long, h.double_col as hybrid_double, m.double_col as mt_double, abs(h.long_col - m.long_col) as long_diff, abs(h.double_col - m.double_col) as double_diff FROM {hybrid_table} h INNER JOIN {merge_tree_table} m ON h.string_col = m.string_col AND h.boolean_col = m.boolean_col WHERE h.long_col IS NOT NULL AND m.long_col IS NOT NULL LIMIT 20 {join_settings};

SELECT h.string_col, h.date_col, h.long_col as hybrid_long, i.long_col as iceberg_long, h.double_col as hybrid_double, i.double_col as iceberg_double FROM {hybrid_table} h LEFT JOIN {clickhouse_iceberg_table_name} i ON h.string_col = i.string_col AND h.date_col = i.date_col WHERE h.date_col IS NOT NULL LIMIT 20 {join_settings};

SELECT h.string_col, h.boolean_col, COUNT(*) as join_count, AVG(h.long_col) as avg_hybrid_long, AVG(m.long_col) as avg_mt_long, AVG(i.long_col) as avg_iceberg_long FROM {hybrid_table} h LEFT JOIN {merge_tree_table} m ON h.string_col = m.string_col LEFT JOIN {clickhouse_iceberg_table_name} i ON h.string_col = i.string_col WHERE h.boolean_col = true GROUP BY h.string_col, h.boolean_col ORDER BY join_count DESC LIMIT 20 {join_settings};

-- Complex CTEs with multiple levels
WITH base_stats AS (SELECT string_col, COUNT(*) as cnt, AVG(long_col) as avg_long, AVG(double_col) as avg_double FROM {hybrid_table} GROUP BY string_col), filtered_stats AS (SELECT * FROM base_stats WHERE cnt > 1 AND avg_long > 1000) SELECT fs.string_col, fs.cnt, fs.avg_long, fs.avg_double, h.long_col, h.double_col FROM filtered_stats fs JOIN {hybrid_table} h ON fs.string_col = h.string_col WHERE h.long_col > fs.avg_long ORDER BY h.long_col DESC LIMIT 20;

WITH hybrid_agg AS (SELECT string_col, boolean_col, SUM(long_col) as sum_long, AVG(double_col) as avg_double FROM {hybrid_table} GROUP BY string_col, boolean_col), mt_agg AS (SELECT string_col, boolean_col, SUM(long_col) as sum_long, AVG(double_col) as avg_double FROM {merge_tree_table} GROUP BY string_col, boolean_col) SELECT COALESCE(h.string_col, m.string_col) as string_col, COALESCE(h.boolean_col, m.boolean_col) as boolean_col, COALESCE(h.sum_long, 0) as hybrid_sum_long, COALESCE(m.sum_long, 0) as mt_sum_long, COALESCE(h.avg_double, 0) as hybrid_avg_double, COALESCE(m.avg_double, 0) as mt_avg_double, (COALESCE(h.sum_long, 0) + COALESCE(m.sum_long, 0)) as total_sum_long FROM hybrid_agg h FULL OUTER JOIN mt_agg m ON h.string_col = m.string_col AND h.boolean_col = m.boolean_col ORDER BY total_sum_long DESC LIMIT 20 {join_settings};

WITH date_partition_stats AS (SELECT date_col, COUNT(*) as cnt, SUM(long_col) as sum_long FROM {hybrid_table} WHERE date_col IS NOT NULL GROUP BY date_col), string_stats AS (SELECT string_col, COUNT(*) as cnt, AVG(double_col) as avg_double FROM {hybrid_table} GROUP BY string_col) SELECT h.string_col, h.date_col, h.long_col, h.double_col, dps.cnt as date_count, dps.sum_long as date_sum_long, ss.cnt as string_count, ss.avg_double as string_avg_double FROM {hybrid_table} h LEFT JOIN date_partition_stats dps ON h.date_col = dps.date_col LEFT JOIN string_stats ss ON h.string_col = ss.string_col WHERE h.date_col IS NOT NULL ORDER BY h.long_col DESC LIMIT 20;

-- Array aggregations with filtering
SELECT string_col, groupArray(long_col) as long_array, arrayFilter(x -> x > 5000, groupArray(long_col)) as filtered_long_array FROM {hybrid_table} GROUP BY string_col;

SELECT string_col, groupArray(double_col) as double_array, arraySort(groupArray(double_col)) as sorted_double_array, arrayReverse(arraySort(groupArray(double_col))) as reverse_sorted_double_array FROM {hybrid_table} GROUP BY string_col;

SELECT string_col, groupArray(long_col) as long_array, arraySum(groupArray(long_col)) as array_sum, arrayAvg(groupArray(long_col)) as array_avg, arrayMax(groupArray(long_col)) as array_max, arrayMin(groupArray(long_col)) as array_min FROM {hybrid_table} GROUP BY string_col;

SELECT string_col, groupArray(string_col) as string_array, arrayUniq(groupArray(string_col)) as unique_string_array, length(groupArray(string_col)) as array_length FROM {hybrid_table} GROUP BY string_col;

SELECT string_col, long_array, arrayElement(long_array, 1) as first_element, arrayElement(long_array, length(long_array)) as last_element FROM (SELECT string_col, groupArray(long_col) as long_array FROM {hybrid_table} GROUP BY string_col);

-- Multi-table analytics and comparisons
SELECT 'hybrid' as source, string_col, COUNT(*) as cnt, SUM(long_col) as sum_long, AVG(double_col) as avg_double FROM {hybrid_table} GROUP BY string_col UNION ALL SELECT 'mergetree' as source, string_col, COUNT(*) as cnt, SUM(long_col) as sum_long, AVG(double_col) as avg_double FROM {merge_tree_table} GROUP BY string_col UNION ALL SELECT 'iceberg' as source, string_col, COUNT(*) as cnt, SUM(long_col) as sum_long, AVG(double_col) as avg_double FROM {clickhouse_iceberg_table_name} GROUP BY string_col ORDER BY source, string_col;

WITH hybrid_totals AS (SELECT SUM(long_col) as total_long, SUM(double_col) as total_double, COUNT(*) as total_rows FROM {hybrid_table}), mt_totals AS (SELECT SUM(long_col) as total_long, SUM(double_col) as total_double, COUNT(*) as total_rows FROM {merge_tree_table}), iceberg_totals AS (SELECT SUM(long_col) as total_long, SUM(double_col) as total_double, COUNT(*) as total_rows FROM {clickhouse_iceberg_table_name}) SELECT 'hybrid' as table_name, h.total_long, h.total_double, h.total_rows FROM hybrid_totals h UNION ALL SELECT 'mergetree' as table_name, m.total_long, m.total_double, m.total_rows FROM mt_totals m UNION ALL SELECT 'iceberg' as table_name, i.total_long, i.total_double, i.total_rows FROM iceberg_totals i;

SELECT h.string_col, h.boolean_col, h.long_col as hybrid_long, m.long_col as mt_long, i.long_col as iceberg_long, CASE WHEN h.long_col = m.long_col AND h.long_col = i.long_col THEN 'all_match' WHEN h.long_col = m.long_col THEN 'hybrid_mt_match' WHEN h.long_col = i.long_col THEN 'hybrid_iceberg_match' WHEN m.long_col = i.long_col THEN 'mt_iceberg_match' ELSE 'no_match' END as match_status FROM {hybrid_table} h FULL OUTER JOIN {merge_tree_table} m ON h.string_col = m.string_col AND h.boolean_col = m.boolean_col FULL OUTER JOIN {clickhouse_iceberg_table_name} i ON COALESCE(h.string_col, m.string_col) = i.string_col AND COALESCE(h.boolean_col, m.boolean_col) = i.boolean_col WHERE h.long_col IS NOT NULL OR m.long_col IS NOT NULL OR i.long_col IS NOT NULL LIMIT 30 {join_settings};

-- EXISTS and correlated subqueries
SELECT h1.string_col, h1.long_col, h1.double_col FROM {hybrid_table} h1 WHERE EXISTS (SELECT 1 FROM {merge_tree_table} m WHERE m.string_col = h1.string_col AND m.long_col > h1.long_col) ORDER BY h1.long_col DESC LIMIT 20;

SELECT h.string_col, h.long_col FROM {hybrid_table} h WHERE h.long_col > (SELECT AVG(m.long_col) FROM {merge_tree_table} m WHERE m.string_col = h.string_col) ORDER BY h.long_col DESC LIMIT 20;

SELECT h.string_col, h.long_col, h.double_col FROM {hybrid_table} h WHERE h.string_col IN (SELECT DISTINCT m.string_col FROM {merge_tree_table} m WHERE m.long_col > 5000) AND h.long_col > 5000 ORDER BY h.long_col DESC LIMIT 20;

SELECT h.string_col, h.long_col FROM {hybrid_table} h WHERE h.long_col = (SELECT MAX(m.long_col) FROM {merge_tree_table} m WHERE m.string_col = h.string_col) ORDER BY h.string_col LIMIT 20;

-- Top N per group queries
SELECT string_col, long_col, double_col FROM (SELECT string_col, long_col, double_col, row_number() OVER (PARTITION BY string_col ORDER BY long_col DESC) as rn FROM {hybrid_table}) WHERE rn <= 3 ORDER BY string_col, long_col DESC;

SELECT string_col, boolean_col, long_col, double_col FROM (SELECT string_col, boolean_col, long_col, double_col, rank() OVER (PARTITION BY string_col, boolean_col ORDER BY double_col DESC) as rnk FROM {hybrid_table}) WHERE rnk <= 2 ORDER BY string_col, boolean_col, double_col DESC;

-- Complex filtering with subqueries
SELECT string_col, long_col, double_col, integer_col FROM {hybrid_table} WHERE (long_col, double_col) IN (SELECT long_col, double_col FROM {merge_tree_table} WHERE long_col > 5000) ORDER BY long_col DESC LIMIT 20;

SELECT string_col, COUNT(*) as cnt FROM {hybrid_table} WHERE string_col IN (SELECT string_col FROM {merge_tree_table} GROUP BY string_col HAVING COUNT(*) > 1) GROUP BY string_col ORDER BY cnt DESC;

-- Time-based analytics
SELECT toStartOfDay(timestamp_col) as day, toHour(timestamp_col) as hour, COUNT(*) as cnt, AVG(long_col) as avg_long FROM {hybrid_table} WHERE timestamp_col IS NOT NULL GROUP BY day, hour ORDER BY day, hour;

SELECT date_col, string_col, COUNT(*) as cnt, SUM(long_col) as sum_long, AVG(double_col) as avg_double FROM {hybrid_table} WHERE date_col IS NOT NULL GROUP BY date_col, string_col ORDER BY date_col, cnt DESC;

-- Conditional aggregations with multiple conditions
SELECT string_col, sumIf(long_col, boolean_col = true AND long_col > 5000) as sum_high_true, sumIf(long_col, boolean_col = false AND long_col > 5000) as sum_high_false, sumIf(long_col, boolean_col = true AND long_col <= 5000) as sum_low_true, sumIf(long_col, boolean_col = false AND long_col <= 5000) as sum_low_false FROM {hybrid_table} GROUP BY string_col ORDER BY string_col;

SELECT string_col, avgIf(double_col, double_col > 4000 AND double_col < 6000) as avg_mid_range, avgIf(double_col, double_col <= 4000) as avg_low_range, avgIf(double_col, double_col >= 6000) as avg_high_range FROM {hybrid_table} GROUP BY string_col ORDER BY string_col;

-- Complex HAVING clauses
SELECT string_col, boolean_col, COUNT(*) as cnt, AVG(long_col) as avg_long, SUM(double_col) as sum_double, AVG(integer_col) as avg_int FROM {hybrid_table} GROUP BY string_col, boolean_col HAVING cnt > 1 AND avg_long > 2000 AND sum_double > 5000 AND avg_int > 2000 ORDER BY cnt DESC LIMIT 20;

SELECT string_col, COUNT(*) as cnt, SUM(long_col) as sum_long, AVG(double_col) as avg_double FROM {hybrid_table} WHERE long_col IS NOT NULL AND double_col IS NOT NULL GROUP BY string_col HAVING cnt >= 2 AND sum_long > (SELECT AVG(sum_long) FROM (SELECT string_col, SUM(long_col) as sum_long FROM {hybrid_table} GROUP BY string_col)) ORDER BY sum_long DESC LIMIT 10;

-- Multi-column ordering and pagination
SELECT string_col, long_col, double_col, integer_col FROM {hybrid_table} ORDER BY string_col ASC, long_col DESC, double_col ASC, integer_col DESC LIMIT 30;

SELECT string_col, boolean_col, long_col, double_col FROM {hybrid_table} ORDER BY boolean_col DESC, string_col ASC, long_col DESC LIMIT 30 OFFSET 10;

-- Complex UNION with different column selections
SELECT string_col, long_col, double_col, 'hybrid' as source FROM {hybrid_table} WHERE long_col > 5000 UNION ALL SELECT string_col, long_col, double_col, 'mergetree' as source FROM {merge_tree_table} WHERE long_col > 5000 UNION ALL SELECT string_col, long_col, double_col, 'iceberg' as source FROM {clickhouse_iceberg_table_name} WHERE long_col > 5000 ORDER BY source, long_col DESC LIMIT 30;

-- Data quality and validation queries
SELECT string_col, COUNT(*) as total, countIf(long_col IS NOT NULL) as non_null_long, countIf(double_col IS NOT NULL) as non_null_double, countIf(boolean_col IS NOT NULL) as non_null_bool, countIf(date_col IS NOT NULL) as non_null_date FROM {hybrid_table} GROUP BY string_col ORDER BY string_col;

SELECT string_col, min(long_col) as min_long, max(long_col) as max_long, avg(long_col) as avg_long, (max(long_col) - min(long_col)) as range_long FROM {hybrid_table} WHERE long_col IS NOT NULL GROUP BY string_col ORDER BY range_long DESC;

-- Cross-table data consistency checks
SELECT h.string_col, h.long_col as hybrid_long, m.long_col as mt_long, i.long_col as iceberg_long, CASE WHEN h.long_col = m.long_col AND h.long_col = i.long_col THEN 'consistent' WHEN h.long_col = m.long_col OR h.long_col = i.long_col OR m.long_col = i.long_col THEN 'partial_match' ELSE 'mismatch' END as consistency FROM {hybrid_table} h FULL OUTER JOIN {merge_tree_table} m ON h.string_col = m.string_col FULL OUTER JOIN {clickhouse_iceberg_table_name} i ON COALESCE(h.string_col, m.string_col) = i.string_col WHERE h.long_col IS NOT NULL OR m.long_col IS NOT NULL OR i.long_col IS NOT NULL LIMIT 30 {join_settings};

-- Advanced analytical queries with multiple aggregations
SELECT string_col, COUNT(*) as total_count, COUNT(DISTINCT boolean_col) as distinct_bool, COUNT(DISTINCT date_col) as distinct_dates, SUM(long_col) as total_long, AVG(double_col) as avg_double, stddevPop(double_col) as stddev_double, MIN(integer_col) as min_int, MAX(integer_col) as max_int FROM {hybrid_table} GROUP BY string_col ORDER BY total_count DESC;

SELECT boolean_col, date_col, COUNT(*) as cnt, AVG(long_col) as avg_long, quantile(0.5)(long_col) as median_long FROM {hybrid_table} WHERE long_col IS NOT NULL GROUP BY boolean_col, date_col ORDER BY boolean_col, date_col;

-- Complex nested subqueries
SELECT string_col, long_col, double_col FROM {hybrid_table} h1 WHERE long_col > (SELECT AVG(long_col) FROM {hybrid_table} h2 WHERE h2.string_col = h1.string_col) AND double_col < (SELECT AVG(double_col) FROM {hybrid_table} h3 WHERE h3.string_col = h1.string_col) ORDER BY long_col DESC LIMIT 20;

SELECT string_col, long_col FROM {hybrid_table} WHERE (string_col, long_col) IN (SELECT string_col, MAX(long_col) FROM {hybrid_table} GROUP BY string_col) ORDER BY string_col;

-- Multi-level aggregations
SELECT string_col, boolean_col, COUNT(*) as cnt, AVG(long_col) as avg_long, (SELECT AVG(long_col) FROM {hybrid_table} h2 WHERE h2.string_col = h1.string_col) as overall_avg_long FROM {hybrid_table} h1 GROUP BY string_col, boolean_col HAVING avg_long > (SELECT AVG(long_col) FROM {hybrid_table}) ORDER BY cnt DESC LIMIT 20;

-- Advanced string pattern matching
SELECT string_col, long_col FROM {hybrid_table} WHERE string_col LIKE '%a%' AND string_col LIKE '%e%' ORDER BY string_col LIMIT 20;

SELECT string_col, COUNT(*) as cnt FROM {hybrid_table} WHERE string_col REGEXP '^[A-Z][a-z]+$' GROUP BY string_col ORDER BY cnt DESC;

SELECT string_col, multiIf(startsWith(string_col, 'A'), 'A_group', startsWith(string_col, 'B'), 'B_group', startsWith(string_col, 'C'), 'C_group', 'other') as name_group, COUNT(*) as cnt FROM {hybrid_table} GROUP BY string_col, name_group ORDER BY name_group, cnt DESC;

-- Complex date and timestamp calculations
SELECT string_col, date_col, timestamp_col, dateDiff('day', date_col, toDate(timestamp_col)) as days_between, dateDiff('hour', timestamp_col, timestamptz_col) as hours_between FROM {hybrid_table} WHERE date_col IS NOT NULL AND timestamp_col IS NOT NULL AND timestamptz_col IS NOT NULL LIMIT 20;

SELECT toYear(date_col) as year, toQuarter(date_col) as quarter, COUNT(*) as cnt, SUM(long_col) as sum_long FROM {hybrid_table} WHERE date_col IS NOT NULL GROUP BY year, quarter ORDER BY year, quarter;

SELECT toStartOfWeek(date_col) as week_start, COUNT(*) as cnt, AVG(long_col) as avg_long FROM {hybrid_table} WHERE date_col IS NOT NULL GROUP BY week_start ORDER BY week_start;

SELECT toStartOfMonth(date_col) as month_start, COUNT(*) as cnt, SUM(double_col) as sum_double FROM {hybrid_table} WHERE date_col IS NOT NULL GROUP BY month_start ORDER BY month_start;

-- Advanced window functions with multiple partitions
SELECT string_col, boolean_col, long_col, row_number() OVER (PARTITION BY string_col, boolean_col ORDER BY long_col DESC) as rn, rank() OVER (PARTITION BY string_col ORDER BY long_col DESC) as rank_all FROM {hybrid_table} LIMIT 30;

SELECT string_col, long_col, double_col, percent_rank() OVER (PARTITION BY string_col ORDER BY long_col) as pct_rank FROM {hybrid_table} LIMIT 30;

SELECT string_col, long_col, row_number() OVER (PARTITION BY string_col ORDER BY long_col) as row_num, count() OVER (PARTITION BY string_col) as partition_count FROM {hybrid_table} LIMIT 30;

-- Complex JOINs with aggregations
SELECT h.string_col, COUNT(DISTINCT h.boolean_col) as hybrid_bool_count, COUNT(DISTINCT m.boolean_col) as mt_bool_count, AVG(h.long_col) as avg_hybrid_long, AVG(m.long_col) as avg_mt_long, corr(h.long_col, m.long_col) as correlation FROM {hybrid_table} h INNER JOIN {merge_tree_table} m ON h.string_col = m.string_col WHERE h.long_col IS NOT NULL AND m.long_col IS NOT NULL GROUP BY h.string_col ORDER BY h.string_col {join_settings};

SELECT h.string_col, h.date_col, COUNT(*) as join_count, SUM(h.long_col + COALESCE(i.long_col, 0)) as combined_sum, AVG(ABS(h.double_col - COALESCE(i.double_col, 0))) as avg_diff FROM {hybrid_table} h LEFT JOIN {clickhouse_iceberg_table_name} i ON h.string_col = i.string_col AND h.date_col = i.date_col WHERE h.date_col IS NOT NULL GROUP BY h.string_col, h.date_col ORDER BY combined_sum DESC LIMIT 20 {join_settings};

-- Recursive CTE-like patterns with multiple CTEs
WITH ranked_data AS (SELECT string_col, long_col, double_col, row_number() OVER (PARTITION BY string_col ORDER BY long_col DESC) as rn FROM {hybrid_table}), top_per_group AS (SELECT * FROM ranked_data WHERE rn <= 3), aggregated AS (SELECT string_col, AVG(long_col) as avg_long, AVG(double_col) as avg_double FROM top_per_group GROUP BY string_col) SELECT a.string_col, a.avg_long, a.avg_double, t.long_col, t.double_col FROM aggregated a JOIN top_per_group t ON a.string_col = t.string_col ORDER BY a.string_col, t.long_col DESC;

WITH hybrid_summary AS (SELECT string_col, COUNT(*) as cnt, SUM(long_col) as sum_long, AVG(double_col) as avg_double FROM {hybrid_table} GROUP BY string_col), mt_summary AS (SELECT string_col, COUNT(*) as cnt, SUM(long_col) as sum_long, AVG(double_col) as avg_double FROM {merge_tree_table} GROUP BY string_col), comparison AS (SELECT COALESCE(h.string_col, m.string_col) as string_col, COALESCE(h.cnt, 0) as hybrid_cnt, COALESCE(m.cnt, 0) as mt_cnt, COALESCE(h.sum_long, 0) as hybrid_sum, COALESCE(m.sum_long, 0) as mt_sum, ABS(COALESCE(h.sum_long, 0) - COALESCE(m.sum_long, 0)) as diff FROM hybrid_summary h FULL OUTER JOIN mt_summary m ON h.string_col = m.string_col) SELECT * FROM comparison WHERE diff > 0 ORDER BY diff DESC LIMIT 20 {join_settings};

-- Advanced array operations
SELECT string_col, long_array, arrayReduce('max', long_array) as array_max, arrayReduce('min', long_array) as array_min, arrayReduce('avg', long_array) as array_avg FROM (SELECT string_col, groupArray(long_col) as long_array FROM {hybrid_table} GROUP BY string_col);

SELECT string_col, groupArray(long_col) as long_array, arrayEnumerate(long_array) as indices, arrayMap((x, i) -> x * i, long_array, indices) as multiplied_array FROM (SELECT string_col, groupArray(long_col) as long_array FROM {hybrid_table} WHERE long_col IS NOT NULL GROUP BY string_col) WHERE length(long_array) > 0;

SELECT string_col, groupArray(long_col) as long_array, arrayFilter(x -> x > 5000, long_array) as filtered, arraySort(filtered) as sorted_filtered FROM (SELECT string_col, groupArray(long_col) as long_array FROM {hybrid_table} GROUP BY string_col);

-- Complex mathematical and statistical operations
SELECT string_col, long_col, integer_col, double_col, (long_col * integer_col + double_col) as complex_calc, sqrt(ABS(long_col - integer_col)) as sqrt_diff FROM {hybrid_table} WHERE long_col IS NOT NULL AND integer_col IS NOT NULL AND double_col IS NOT NULL LIMIT 20;

SELECT string_col, corr(long_col, double_col) as corr_long_double, corr(long_col, integer_col) as corr_long_int, corr(double_col, float_col) as corr_double_float FROM {hybrid_table} WHERE long_col IS NOT NULL AND double_col IS NOT NULL AND integer_col IS NOT NULL AND float_col IS NOT NULL GROUP BY string_col;

SELECT string_col, covarPop(long_col, double_col) as covar_pop, covarSamp(long_col, double_col) as covar_samp FROM {hybrid_table} WHERE long_col IS NOT NULL AND double_col IS NOT NULL GROUP BY string_col;

-- Advanced NULL handling and data quality
SELECT string_col, COUNT(*) as total, countIf(boolean_col IS NULL) as null_bool, countIf(long_col IS NULL) as null_long, countIf(double_col IS NULL) as null_double, countIf(integer_col IS NULL) as null_int, countIf(float_col IS NULL) as null_float, countIf(decimal_col IS NULL) as null_decimal, countIf(date_col IS NULL) as null_date, countIf(timestamp_col IS NULL) as null_timestamp FROM {hybrid_table} GROUP BY string_col ORDER BY total DESC;

SELECT string_col, COUNT(*) as total_rows, COUNT(long_col) as non_null_long, (COUNT(*) - COUNT(long_col)) as null_long_count, (COUNT(long_col) * 100.0 / COUNT(*)) as non_null_percentage FROM {hybrid_table} GROUP BY string_col ORDER BY non_null_percentage DESC;

-- Complex filtering with multiple OR/AND conditions
SELECT * FROM {hybrid_table} WHERE (long_col > 7000 AND double_col > 7000) OR (integer_col > 7000 AND float_col > 7000) OR (long_col + integer_col > 12000) ORDER BY long_col DESC LIMIT 20;

SELECT string_col, long_col, double_col, integer_col FROM {hybrid_table} WHERE (string_col IN ('Alice', 'Bob', 'Charlie') AND long_col > 5000) OR (string_col IN ('David', 'Eve', 'Frank') AND double_col > 5000) ORDER BY string_col, long_col DESC LIMIT 20;

-- Performance and optimization test queries
SELECT string_col, COUNT(*) as cnt FROM {hybrid_table} WHERE long_col BETWEEN 2000 AND 8000 AND double_col BETWEEN 2000.0 AND 8000.0 AND integer_col BETWEEN 2000 AND 8000 GROUP BY string_col HAVING cnt > 1 ORDER BY cnt DESC;

SELECT h.string_col, COUNT(*) as join_rows, SUM(h.long_col) as hybrid_sum, SUM(COALESCE(m.long_col, 0)) as mt_sum, SUM(COALESCE(i.long_col, 0)) as iceberg_sum FROM {hybrid_table} h LEFT JOIN {merge_tree_table} m ON h.string_col = m.string_col LEFT JOIN {clickhouse_iceberg_table_name} i ON h.string_col = i.string_col WHERE h.long_col IS NOT NULL GROUP BY h.string_col HAVING COUNT(*) > 1 ORDER BY hybrid_sum DESC LIMIT 20 {join_settings};

-- Advanced grouping and rollup patterns
SELECT string_col, boolean_col, COUNT(*) as cnt, SUM(long_col) as sum_long FROM {hybrid_table} GROUP BY string_col, boolean_col WITH ROLLUP ORDER BY string_col, boolean_col;

SELECT string_col, toYear(date_col) as year, COUNT(*) as cnt, AVG(double_col) as avg_double FROM {hybrid_table} WHERE date_col IS NOT NULL GROUP BY string_col, year WITH CUBE ORDER BY string_col, year;

-- Complex UNION with different filters and aggregations
SELECT 'hybrid_high' as category, string_col, COUNT(*) as cnt, AVG(long_col) as avg_long FROM {hybrid_table} WHERE long_col > 7000 GROUP BY string_col UNION ALL SELECT 'hybrid_mid' as category, string_col, COUNT(*) as cnt, AVG(long_col) as avg_long FROM {hybrid_table} WHERE long_col BETWEEN 3000 AND 7000 GROUP BY string_col UNION ALL SELECT 'hybrid_low' as category, string_col, COUNT(*) as cnt, AVG(long_col) as avg_long FROM {hybrid_table} WHERE long_col < 3000 GROUP BY string_col ORDER BY category, string_col;

-- Real-world analytical scenarios
SELECT string_col, date_col, COUNT(*) as daily_count, SUM(long_col) as daily_sum, AVG(double_col) as daily_avg, MIN(integer_col) as daily_min, MAX(integer_col) as daily_max FROM {hybrid_table} WHERE date_col IS NOT NULL GROUP BY string_col, date_col ORDER BY date_col, daily_sum DESC;

SELECT boolean_col, string_col, COUNT(*) as records, SUM(long_col) as total_value, AVG(double_col) as avg_metric, quantile(0.5)(long_col) as median_value FROM {hybrid_table} WHERE long_col IS NOT NULL GROUP BY boolean_col, string_col HAVING COUNT(*) >= 2 AND SUM(long_col) > 5000 ORDER BY SUM(long_col) DESC LIMIT 20;

-- Cross-table statistical comparisons
WITH hybrid_stats AS (SELECT string_col, AVG(long_col) as avg_long, stddevPop(long_col) as stddev_long, COUNT(*) as cnt FROM {hybrid_table} WHERE long_col IS NOT NULL GROUP BY string_col), mt_stats AS (SELECT string_col, AVG(long_col) as avg_long, stddevPop(long_col) as stddev_long, COUNT(*) as cnt FROM {merge_tree_table} WHERE long_col IS NOT NULL GROUP BY string_col) SELECT COALESCE(h.string_col, m.string_col) as string_col, h.avg_long as hybrid_avg, m.avg_long as mt_avg, ABS(h.avg_long - m.avg_long) as avg_diff, h.stddev_long as hybrid_stddev, m.stddev_long as mt_stddev FROM hybrid_stats h FULL OUTER JOIN mt_stats m ON h.string_col = m.string_col WHERE h.cnt > 1 OR m.cnt > 1 ORDER BY avg_diff DESC LIMIT 20 {join_settings};

