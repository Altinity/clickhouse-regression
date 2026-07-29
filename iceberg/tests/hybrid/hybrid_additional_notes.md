All hybrid tests are currently under clickhouse-regression/iceberg/tests/hybrid.
Suite lives under iceberg/tests/hybrid (moved from ice/tests/hybrid).

Important when testing Hybrid / Distributed

  The engine can run subqueries locally or send them to a remote server — those are entirely different code paths. If you set prefer_localhost_replica=0, the local portion is executed as if it were remote. Some issues show up specifically when merging the result of the local plan with what was executed on the shard.

  When a query is sent to a remote server, ClickHouse usually builds an SQL subquery (you can see it in the logs). There is also a relatively new option: instead of a subquery, it can send a prepared fragment of the query execution plan to the remote server — a graph of steps serialized as JSON — via serialize_query_plan=1. That setting is off by default, but it will likely be enabled by default in the future.

  When queries are sent to shards as SQL, the shard-side subquery may run in one of four modes, depending on the query shape:

  • complete
  • with_mergeable_state
  • with_mergeable_state_after_aggregation
  • with_mergeable_state_after_aggregation_and_limit

  During query analysis, enable_analyzer may be on or off; for Hybrid, only enable_analyzer=1 is supported.

  On top of that, there is a distributed-over-distributed scenario — which CISCO will apparently use.

  To test this properly, there are quite a few important branches to cover.

Read this to understand Hybrid table basics: https://altinity.com/blog/introducing-hybrid-tables-transparent-query-on-clickhouse-mergetree-and-iceberg-data

Read this to understand the way Hybrid tables will link MergeTree and Iceberg, end to end: https://gist.github.com/filimonov/a2bf4f2758de421c569ba8af898b656e

Consider creating a test suite similar to hybrid_query_fuzzing, but where the queries are based on the ones being used in stateless/stateful/integration tests upstream.