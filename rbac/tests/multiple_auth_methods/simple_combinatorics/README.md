# Simple example of combinatorial test with behavior model

## How to run

1. Uncomment this piece of code in the end of `/rbac/tests/multiple_auth_methods/feature.py`.

```python
Feature(
    run=load(
        "rbac.tests.multiple_auth_methods.simple_combinatorics.simple_combinatorics",
        "feature",
    ),
    parallel=True,
    executor=pool,
)
```

2. Go to clickhouse-regression/rbac and run `./regression.py --local --clickhouse-binary-path docker://clickhouse/clickhouse-server:24.12 --with-analyzer --only '/rbac/multiple authentication methods/simple combinatorics/*'`

