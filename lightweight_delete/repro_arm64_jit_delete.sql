-- Repro for the aarch64 JIT abort in job 107850295922
-- (Scheduled Altinity 26.3, lightweight_delete, 26.3.33.10001.altinitystable).
--
-- clickhouse1 aborted (signal 6) at 2026-09-24 23:38:57 UTC while compiling
-- this predicate for mutation bdd4bbbb-...::7_8_8_1_17:
--   LLVM ERROR: Cannot select: v8i8 = bitcast ...
--   AArch64DAGToDAGISel / CHJIT::compileModule / MutateTask
--
-- The expression is the OR of the last two DELETEs that were in flight.
-- Rerunning the TestFlows scenario misses it: the row groups are unseeded.
--
-- Run on aarch64. The process aborts with the same LLVM error:
--   docker run --rm -i --platform linux/arm64 \
--     altinity/clickhouse-server:26.3.33.10001.altinitystable \
--     clickhouse-local --multiquery < lightweight_delete/repro_arm64_jit_delete.sql

SET allow_experimental_lightweight_delete = 1;
SET allow_experimental_analyzer = 1;
SET compile_expressions = 1;
SET min_count_to_compile_expression = 1;

DROP TABLE IF EXISTS repro_jit SYNC;

CREATE TABLE repro_jit
(
    id Int64,
    x Int64
)
ENGINE = AggregatingMergeTree
PARTITION BY id
ORDER BY id;

-- Same rows as the test: id 0..9, x 0..99, one part per partition.
INSERT INTO repro_jit
SELECT intDiv(number, 100), number % 100
FROM numbers(1000)
SETTINGS max_block_size = 100;

-- One statement, so the filter is the same OR the mutation checker built
-- from the two concurrent DELETEs. Parentheses keep the two chains apart.
DELETE FROM repro_jit
WHERE
    ((id = 0 AND x = 45) OR (id = 9 AND x = 8) OR (id = 5 AND x = 14) OR (id = 8 AND x = 62) OR (id = 8 AND x = 67) OR (id = 2 AND x = 8) OR (id = 3 AND x = 95) OR (id = 5 AND x = 64) OR (id = 4 AND x = 35) OR (id = 7 AND x = 96) OR (id = 8 AND x = 53) OR (id = 9 AND x = 59) OR (id = 9 AND x = 30) OR (id = 3 AND x = 85) OR (id = 8 AND x = 55) OR (id = 8 AND x = 91) OR (id = 5 AND x = 79) OR (id = 5 AND x = 12) OR (id = 1 AND x = 83) OR (id = 0 AND x = 12) OR (id = 5 AND x = 34) OR (id = 9 AND x = 69) OR (id = 9 AND x = 60) OR (id = 7 AND x = 40) OR (id = 0 AND x = 88) OR (id = 4 AND x = 33) OR (id = 6 AND x = 88) OR (id = 1 AND x = 39) OR (id = 6 AND x = 36) OR (id = 4 AND x = 56) OR (id = 4 AND x = 3) OR (id = 2 AND x = 77) OR (id = 8 AND x = 9) OR (id = 1 AND x = 21) OR (id = 9 AND x = 11) OR (id = 6 AND x = 24) OR (id = 2 AND x = 81) OR (id = 7 AND x = 78) OR (id = 4 AND x = 31) OR (id = 0 AND x = 90) OR (id = 9 AND x = 14) OR (id = 3 AND x = 65) OR (id = 6 AND x = 50) OR (id = 0 AND x = 60) OR (id = 2 AND x = 5) OR (id = 1 AND x = 7) OR (id = 9 AND x = 62))
    OR
    ((id = 2 AND x = 39) OR (id = 3 AND x = 80) OR (id = 6 AND x = 30) OR (id = 3 AND x = 77) OR (id = 4 AND x = 26) OR (id = 9 AND x = 10) OR (id = 6 AND x = 47) OR (id = 5 AND x = 26) OR (id = 8 AND x = 90) OR (id = 4 AND x = 62) OR (id = 5 AND x = 54) OR (id = 7 AND x = 9) OR (id = 7 AND x = 15) OR (id = 4 AND x = 47) OR (id = 6 AND x = 99) OR (id = 2 AND x = 48) OR (id = 7 AND x = 91) OR (id = 0 AND x = 52) OR (id = 5 AND x = 38) OR (id = 6 AND x = 2) OR (id = 2 AND x = 47) OR (id = 9 AND x = 81) OR (id = 9 AND x = 16) OR (id = 3 AND x = 93) OR (id = 3 AND x = 13) OR (id = 8 AND x = 87) OR (id = 6 AND x = 54) OR (id = 1 AND x = 8) OR (id = 5 AND x = 73) OR (id = 2 AND x = 41) OR (id = 7 AND x = 29) OR (id = 9 AND x = 78) OR (id = 2 AND x = 53) OR (id = 4 AND x = 85) OR (id = 7 AND x = 8))
SETTINGS
    mutations_sync = 2,
    compile_expressions = 1,
    min_count_to_compile_expression = 1;

SELECT count() FROM repro_jit;
