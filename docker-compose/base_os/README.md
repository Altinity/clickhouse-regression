# Base OS Setup

These files install ClickHouse and test dependencies.

`clickhouse.Dockerfile` is special, it is used with docker releases of ClickHouse server and keeper, and thus only installs test dependencies.

Adding support for a new distribution is simple, make a copy of the most closely related Dockerfile, name it accordingly, and adjust it as necessary.

You can get the correct name with the following python snippet:

```python
>>> "docker://redhat/ubi9:9.4".split("//")[-1].split(":")[0].split("/")[-1] + ".Dockerfile"
'ubi9.Dockerfile'
```
