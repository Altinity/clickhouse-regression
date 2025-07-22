# Running clickhouse-jdbc tests locally

## New info:

Clone clickhouse-jdbc repository:
```bash
git clone --recursive "https://github.com/ClickHouse/clickhouse-jdbc"
```

Go to `clickhouse-jdbc/clickhouse-client/src/test/java/com/clickhouse/client/ClickHouseServerForTest.java` and change 
`clickhouse/clickhouse-server` to the image that you want to use for testing, for example:
```
altinityinfra/clickhouse-server:0-25.3.6.10318.altinitytest
```

Then run:
```
sudo ./run_without_docker_jdbc_only.sh > test.log
``` 

Upolad `test.log` to the bucket of lts release you are testing.



## Old info:

clickhouse-jdbc: `https://github.com/ClickHouse/clickhouse-jdbc`

To run clickhouse-jdbc tests manually you need `clickhouse-common-static.deb` and the `clickhouse-client.deb` in your machine.

Then execute command
```bash
docker run --rm -v $(pwd)/PACKAGES:/clickhouse -e RELEASE=v0.3.2 registry.gitlab.com/altinity-public/container-images/test/clickhouse-jdbc-runner:v1.0
```

Where `$(pwd)/PACKAGES` is the folder to the clickhouse*.deb packages and `RELEASE=v0.3.2` is the clickhouse-jdbc version you want to test.
Test log you need is $(pwd)/PACKAGES/test.log

Make sure you have access to gitlab registry, if you don't then build the image manually with file in `https://gitlab.com/altinity-public/container-images/-/tree/main/test/clickhouse-jdbc-runner` and change the previous command with
```bash
docker run --rm -v $(pwd)/PACKAGES:/clickhouse -e RELEASE=v0.3.2 clickhouse-jdbc
```
Where `clickhouse-jdbc` is the name of created docker image.

Starting clickhouse-jdbc v0.4.0 running in docker not supported becouse of using docker inside the test.
to test version after or equal v0.4.0 use runner_without_docker.sh:

1. Specify clickhouse-jdbc version in runner_without_docker.sh
2. Specify clickhouse version runner_without_docker.sh
3. Run runner_without_docker.sh (sudo ./runner_without_docker.sh)

