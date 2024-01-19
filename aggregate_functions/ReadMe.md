### Aggregate functions

How to run tests for:
- -Merge combinator (for exmaple, `sum` aggregate function): **./regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:23.8.5.16-alpine --only "/aggregate functions/merge/sumMerge/*"**

- finalizeAggregation function (for exmaple, `sum` aggregate function): **./regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:23.8.5.16-alpine --only "/aggregate functions/finalizeAggregation/sum_finalizeAggregation_Merge/*"**





